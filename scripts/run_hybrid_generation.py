"""
Pipeline v4: deterministic draft + constrained model edits.

  descriptive : Python writes the factual text. Optionally (--rewrite-descriptive) the
                model may rewrite it into smoother prose; the rewrite is accepted only if
                every number and quoted title is unchanged (validate_rewrite). With
                Phi-3.5 this never passed (0 of 5), so it is off by default.
  evaluative  : the model writes freely but may use no digits and must cite a
                decision by its exact quoted event title (validate_evaluative).

Each part gets one retry with the specific problems listed; if it still fails,
the deterministic text is used and the log says so (mode "draft"/"template").

Requires Ollama running locally with the model pulled.

Usage:
    python run_hybrid_generation.py path/to/log.json phi3.5 [output_dir] [--rewrite-descriptive]
"""
import sys
import time
from pathlib import Path

import requests

from context_card import clean_generation, compute_facts
from report_draft import (build_phrases, draft_descriptive, draft_evaluative,
                          strengths_and_weak_spots, trim_sentences, validate_evaluative, validate_rewrite)
from run_card_generation import OLLAMA_URL, OPTIONS, RETRY_TEMPLATE, chat

SYSTEM_PROMPT = """You help write the end-of-session report for the APOLLO2028 Business Game, a \
hospital-management simulation. The report has two parts: a DESCRIPTION of what happened and an \
EVALUATION of what it meant. Players are scored on four axes: patient experience, patient health, \
cost reduction and staff wellbeing. Write in plain prose, no bullet points, no headings. Never invent facts."""

TASK_REWRITE = """Below is a factual DRAFT of the descriptive part of the report, written by a program.

DRAFT:
{draft}

Rewrite it as smooth, natural, neutral prose. Rules:
- Keep EVERY number, dollar amount, day and every quoted event title or option name exactly as in the draft, \
character for character.
- Do not add, remove or change any fact. Do not add opinions, praise or criticism, and do not say that one \
thing caused another.
- Write 3-5 sentences (you may merge sentences, but never drop a fact).
Output only the rewritten text."""

TASK_EVALUATIVE = """Write the EVALUATIVE part of the end-of-session report: 3-5 encouraging, constructive \
sentences about what the results mean for the player.

FACTS (all you may rely on):
- Scenario: {scenario}
- {money_line}
- Scores that rose: {rose}
- Scores that fell: {fell}
- Staff resignations: {resign}
- Decisions the player made (event title -> what the player chose):
{decisions}
- Strategic actions that were never used (examples): {unused}

Rules:
- Write NO digits at all: describe scores by name and direction only (rose, fell).
- Cite at least one decision by copying its exact event title in double quotes.
- Mention one score that fell or one action that was never used, framed as an opportunity for next time.
- You may suggest that a decision affected a score only with hedged wording ("may have", "could", "might"); never state it as fact. Do not introduce any facts beyond the list above.
- One paragraph; do not mention the name of the game or restate these instructions.
- End with one forward-looking, encouraging sentence.
Output only the evaluation."""


def evaluative_prompt(f: dict, p: dict) -> str:
    up, down = strengths_and_weak_spots(f)
    money_line = ("The hospital ended with more money than it started with." if f["end_balance"] > f["start_balance"]
                  else "The hospital ended with less money than it started with.")
    lines = []
    for d in f["decisions"]:
        choice = "chose to take no action" if d["chosen"] == "Take no action" else f'chose "{d["chosen"]}"'
        lines.append(f'  - "{d["title"]}" -> {choice}')
    unused = ", ".join(p[k] for k in ("UNUSED_1", "UNUSED_2") if k in p) or "none"
    return TASK_EVALUATIVE.format(
        scenario=f["scenario"], money_line=money_line, rose=", ".join(up) or "none", fell=", ".join(down) or "none",
        resign="none" if f["resignations"] == 0 else "some", decisions="\n".join(lines) or "  - none", unused=unused)


def attempt(messages, model, check, kind, fallback_text, mode_fallback, log, post=None):
    """One call, one targeted retry, then the deterministic fallback. Returns (text, raw_model_text, mode)."""
    def one(msgs):
        raw, tokens, cut = chat(msgs, model)
        raw, note = clean_generation(raw, cut)
        if post:
            raw, note_post = post(raw)
            note = "; ".join(n for n in (note, note_post) if n) or None
        if note:
            log.append(f"{kind}: {note}")
        if tokens > OPTIONS["num_ctx"] * 0.9:
            log.append(f"WARNING: {kind} prompt used {tokens} of {OPTIONS['num_ctx']} tokens")
        return raw

    raw = one(messages)
    problems = check(raw)
    if not problems:
        log.append(f"{kind}: passed validation first try")
        return raw, raw, "llm"
    log.append(f"{kind}: first draft failed -> " + "; ".join(problems))
    retry = messages + [
        {"role": "assistant", "content": raw},
        {"role": "user", "content": RETRY_TEMPLATE.format(problems="\n".join(f"- {x}" for x in problems), part=kind)},
    ]
    raw2 = one(retry)
    problems2 = check(raw2)
    if not problems2:
        log.append(f"{kind}: rewrite passed validation")
        return raw2, raw2, "llm"
    log.append(f"{kind}: rewrite still failing -> " + "; ".join(problems2) + f" => USING {mode_fallback.upper()} TEXT")
    return fallback_text, raw2, mode_fallback


def run(json_path: str, model: str, output_dir: str = None, rewrite_descriptive: bool = False):
    facts = compute_facts(json_path)
    phrases = build_phrases(facts)
    draft_d = draft_descriptive(phrases, facts)
    log = []

    print(f"=== Model: {model} ===\n")
    t0 = time.time()

    if rewrite_descriptive:
        descriptive, raw_d, mode_d = attempt(
            [{"role": "system", "content": SYSTEM_PROMPT},
             {"role": "user", "content": TASK_REWRITE.format(draft=draft_d)}],
            model, lambda t: validate_rewrite(draft_d, t, facts), "descriptive", draft_d, "draft", log)
    else:
        descriptive, raw_d, mode_d = draft_d, "(not requested: descriptive part is the deterministic draft)", "draft"
        log.append("descriptive: deterministic draft (model rewrite disabled; enable with --rewrite-descriptive)")
    print("--- Descriptive part ---\n" + descriptive + "\n")

    eval_template = draft_evaluative(phrases, facts)
    evaluative, raw_e, mode_e = attempt(
        [{"role": "system", "content": SYSTEM_PROMPT},
         {"role": "user", "content": evaluative_prompt(facts, phrases)}],
        model, lambda t: validate_evaluative(t, facts, phrases), "evaluative", eval_template, "template", log,
        post=lambda t: trim_sentences(t, 5))
    print("--- Evaluative part ---\n" + evaluative + "\n")

    elapsed = time.time() - t0
    print(f"(total time: {elapsed:.1f}s | descriptive: {mode_d}, evaluative: {mode_e})")
    for line in log:
        print("  " + line)

    out_dir = Path(output_dir) if output_dir else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"output_{model.replace(':', '_')}.md"
    # The scorer reads only the Descriptive/Evaluative sections, so everything else
    # goes first and the Evaluative section stays last.
    out_path.write_text(
        f"# Output — {model} (pipeline v4: deterministic draft + constrained edits)\n\n"
        f"*(Generation time: {elapsed:.1f}s)*\n\n"
        f"*(Source — descriptive: {mode_d}, evaluative: {mode_e})*\n\n"
        f"## Python draft of the descriptive part\n{draft_d}\n\n"
        f"## Validation log\n" + "\n".join(f"- {l}" for l in log) + "\n\n"
        f"## Raw model output (last attempt)\n### Raw descriptive\n{raw_d}\n\n### Raw evaluative\n{raw_e}\n\n"
        f"## Descriptive part\n{descriptive}\n\n"
        f"## Evaluative part\n{evaluative}\n"
    )
    print(f"Saved to {out_path}")
    requests.post(OLLAMA_URL, json={"model": model, "keep_alive": 0})  # free RAM on 8 GB Mac


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        print("Usage: python run_hybrid_generation.py <log.json> <model_name> [output_dir] [--rewrite-descriptive]")
        sys.exit(1)
    run(args[0], args[1], args[2] if len(args) > 2 else None, "--rewrite-descriptive" in sys.argv)
