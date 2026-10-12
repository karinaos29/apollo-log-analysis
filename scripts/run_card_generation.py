"""
Pipeline v3: context card instead of the daily table.

Python builds the fact sheet (context_card.py); the model only writes the two
report parts (descriptive -> evaluative). Each part is checked against the
card and rewritten once if it breaks a rule (missing balance, wrong day for a
decision, number that is not on the card, wrong sentence count).

Requires Ollama running locally with the model pulled.

Usage:
    python run_card_generation.py path/to/log.json phi3.5 [output_dir]
"""
import sys
import time
from pathlib import Path

import requests

from context_card import build_context_card, clean_generation, validate_part

OLLAMA_URL = "http://localhost:11434/api/chat"

# Fixed decoding settings: low temperature + seed make repeat runs comparable
# and reduce the token glitches seen in v2. num_ctx is set explicitly so the
# prompt is never silently truncated; the runner warns when it gets close.
OPTIONS = {"temperature": 0.3, "top_p": 0.9, "seed": 42, "num_ctx": 4096, "num_predict": 600}

SYSTEM_PROMPT = """You write the end-of-session report for the APOLLO2028 Business Game, a \
hospital-management simulation. Players are scored on four axes: patient experience, \
patient health, cost reduction and staff wellbeing. The report has two parts: a \
DESCRIPTION of what happened and an EVALUATION of what it meant.

You are given a FACT CARD computed exactly from the player's session log. Rules:
- Use only facts from the card. Never invent a number, day, event or decision.
- Copy figures exactly as written on the card (dollar amounts in full, e.g. $1,234,567).
- A decision belongs to the day written next to it on the card. Do not move it.
- Score changes listed after a decision happened afterwards; do not say the decision caused them.
- Write in plain prose, no bullet points, no headings."""

TASK2_TEMPLATE = """FACT CARD:
{card}

TASK 1 - Write the DESCRIPTIVE part of the report: 3-5 sentences, factual and neutral, \
from the system's point of view. It must contain:
- the starting and the ending balance, copied exactly from the card
- the number of patients treated
- all four scores (staff wellbeing, patient health, patient experience, cost reduction), \
saying whether each went up or down
- at least {n_decisions} of the player's decisions, each with its exact event title in quotes \
and its day{spread}
Use no praise or criticism words here (no "excellent", "poor", "impressive", "strong", "effective").
Write ONLY this description. Do not write an evaluation yet.

Style example from a DIFFERENT session (copy the style, never its facts or numbers):
The hospital started with $2,000,000 and finished with $2,400,000, a change of +$400,000 over 30 days. \
It treated 500 patients, 400 of them successfully (80.0%). Staff wellbeing fell from 77.5 to 70.0, \
patient health fell from 75.0 to 68.0, patient experience rose from 75.0 to 77.0 and cost reduction \
rose from 40.0 to 70.0. On Day 8, at the event "Supply Shortage", the player chose "Order Emergency Stock", \
and on Day 20, at the event "Staff Review", the player chose "Take no action"; patient health \
was 3.0 points lower a week later. No staff resignations were recorded."""

TASK3 = """TASK 2 - Now write the EVALUATIVE part: 3-5 sentences giving a high-level assessment \
of what these results mean for the player. Refer to at least one specific decision by its \
event title and day, and to one score that fell or one strategic action that was never used. \
Introduce no new facts beyond the card. The tone must stay encouraging and constructive; \
frame weaknesses as opportunities for next time."""

RETRY_TEMPLATE = """That draft breaks these rules:
{problems}
Rewrite the whole {part} part so it follows all of them. Output only the rewritten text."""


def chat(messages: list, model: str):
    resp = requests.post(
        OLLAMA_URL,
        json={"model": model, "messages": messages, "stream": False, "options": OPTIONS},
        timeout=900,
    )
    resp.raise_for_status()
    body = resp.json()
    return body["message"]["content"].strip(), body.get("prompt_eval_count", 0), body.get("done_reason") == "length"


def _badness(text: str, problems: list) -> int:
    """Lower is better. A draft with fewer than 3 sentences (e.g. cut off) is penalised heavily."""
    n = len([x for x in text.replace("\n", " ").split(". ") if x.strip()])
    return len(problems) + (10 if n < 3 else 0)


def generate_part(messages: list, model: str, check, part: str, log: list) -> str:
    """One call, then at most one rewrite if `check(text)` reports problems.

    Keeps whichever draft has fewer problems (a rewrite is not always better).
    """
    text, tokens, cut = chat(messages, model)
    text, note = clean_generation(text, cut)
    if note:
        log.append(f"{part}: {note}")
    if tokens > OPTIONS["num_ctx"] * 0.9:
        log.append(f"WARNING: {part} prompt used {tokens} of {OPTIONS['num_ctx']} tokens (truncation risk)")
    problems = check(text)
    if not problems:
        log.append(f"{part}: passed validation first try")
        return text
    log.append(f"{part}: first draft failed -> " + "; ".join(problems))
    retry = messages + [
        {"role": "assistant", "content": text},
        {"role": "user", "content": RETRY_TEMPLATE.format(problems="\n".join(f"- {p}" for p in problems), part=part)},
    ]
    text2, _, cut2 = chat(retry, model)
    text2, note2 = clean_generation(text2, cut2)
    if note2:
        log.append(f"{part} rewrite: {note2}")
    problems2 = check(text2)
    if not problems2:
        log.append(f"{part}: rewrite passed validation")
        return text2
    if _badness(text2, problems2) <= _badness(text, problems):
        log.append(f"{part}: kept rewrite (still failing) -> " + "; ".join(problems2))
        return text2
    log.append(f"{part}: kept first draft; rewrite was worse -> " + "; ".join(problems2))
    return text


def run(json_path: str, model: str, output_dir: str = None):
    card, facts = build_context_card(json_path)
    log = []

    n_dec = min(2, len(facts["decisions"]))
    spread = " (one from each half of the run if possible)" if len(facts["decisions"]) >= 2 else ""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": TASK2_TEMPLATE.format(card=card, n_decisions=n_dec, spread=spread)},
    ]

    print(f"=== Model: {model} | card ~{len(card) // 4} tokens ===\n")
    t0 = time.time()

    descriptive = generate_part(
        messages, model, lambda t: validate_part(facts, card, t, "descriptive"), "descriptive", log)
    print("--- Descriptive part ---\n" + descriptive + "\n")

    messages += [{"role": "assistant", "content": descriptive}, {"role": "user", "content": TASK3}]
    evaluative = generate_part(
        messages, model, lambda t: validate_part(facts, card, t, "evaluative"), "evaluative", log)
    print("--- Evaluative part ---\n" + evaluative + "\n")

    elapsed = time.time() - t0
    print(f"(total time: {elapsed:.1f}s)")
    for line in log:
        print("  " + line)

    out_dir = Path(output_dir) if output_dir else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"output_{model.replace(':', '_')}.md"
    # The scorer reads only the Descriptive/Evaluative sections, so the card and
    # validation log go first and the Evaluative section stays last.
    out_path.write_text(
        f"# Output — {model} (pipeline v3: context card)\n\n"
        f"*(Generation time: {elapsed:.1f}s)*\n\n"
        f"## Context card\n```\n{card}\n```\n\n"
        f"## Validation log\n" + "\n".join(f"- {l}" for l in log) + "\n\n"
        f"## Descriptive part\n{descriptive}\n\n"
        f"## Evaluative part\n{evaluative}\n"
    )
    print(f"Saved to {out_path}")
    requests.post(OLLAMA_URL, json={"model": model, "keep_alive": 0})  # free RAM on 8 GB Mac


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_card_generation.py <log.json> <model_name> [output_dir]")
        sys.exit(1)
    run(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
