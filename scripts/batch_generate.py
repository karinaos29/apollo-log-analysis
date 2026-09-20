"""
Batch generator for APOLLO2028 scenarios and strategies.
Iterates through each scenario/strategy log, invokes Ollama candidate models,
measures speed, and saves outputs into:
    experiments/<scenario>/<strategy>/output_<model>.md
"""
import json
import os
import sys
import time
from pathlib import Path
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = """You are assisting with the APOLLO2028 Business Game, a hospital-management \
simulation. Players are scored on four axes: Patient Experience, Patient \
Health, Cost Reduction, and Staff Wellbeing. After each session, players \
receive a report with two parts: a DESCRIPTION of what happened, and an \
EVALUATION of what it meant. You will be given the full simulation log in \
JSON. Work through this in three steps as instructed, one at a time."""

TASK1_TEMPLATE = """Here is the full simulation log in JSON:

{json_log}

TASK 1 - Analyze this log internally before writing anything player-facing. \
Identify:
- the overall trend of each of the four scores (staff_wellbeing, \
patient_health, patient_experience, cost_reduction) across the run
- any sharp increases or decreases, and the day they occurred
- whether any sharp change coincides with an entry in event_history, and if \
so, which event and what solution was chosen
- any notable absences: actions that were available but never taken, \
especially if a related score was declining
- overall outcome: days completed, patients treated and success rate, \
staff resignations, final financial result

List these findings as short bullet points."""

TASK2 = """TASK 2 - Using only the findings above, write the DESCRIPTIVE part \
of the report: 3-5 sentences, factual and neutral in tone, written from the \
system's point of view. Include the overall outcome AND at least one \
specific moment (a day, an event, or a sharp change). Do not include \
judgment or evaluation here."""

TASK3 = """TASK 3 - Now write the EVALUATIVE part: 3-5 sentences giving a \
high-level assessment of what these results mean for the player. Reference \
at least one specific, concrete detail from the findings. The tone must \
remain encouraging and constructive throughout, even where results were \
weak or mixed."""

MODELS = ["llama3.2", "phi3.5", "qwen2.5:3b"]

RUNS = [
    {
        "scenario": "post-pandemic",
        "strategy": "normal_strategy",
        "log": "data/post-pandemic/normal_strategy-mark-post_pandemic_financial_recovery-2026-09-20T18-06-09.json",
        "out_dir": "experiments/post-pandemic/normal_strategy",
    },
    {
        "scenario": "post-pandemic",
        "strategy": "cost_minimization_strategy",
        "log": "data/post-pandemic/cost_minimization_strategy_catherine-post_pandemic_financial_recovery-2026-09-20T18-25-52.json",
        "out_dir": "experiments/post-pandemic/cost_minimization_strategy",
    },
    {
        "scenario": "winter-flu",
        "strategy": "normal_strategy",
        "log": "data/winter-flu/normal_strategy-winter_flu_crisis-2026-09-20T22-07-06.json",
        "out_dir": "experiments/winter-flu/normal_strategy",
    },
    {
        "scenario": "winter-flu",
        "strategy": "cost_minimization_strategy",
        "log": "data/winter-flu/cost_minimization_strategy-winter_flu_crisis-2026-09-20T22-07-16.json",
        "out_dir": "experiments/winter-flu/cost_minimization_strategy",
    },
]


def chat(messages: list, model: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={"model": model, "messages": messages, "stream": False},
        timeout=900,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def run_single(json_path: str, model: str, out_dir: str, overwrite: bool = False):
    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)
    out_path = out_dir_path / f"output_{model.replace(':', '_')}.md"

    if out_path.exists() and not overwrite:
        print(f"[SKIP] Output already exists: {out_path}")
        return True

    print(f"\n==========================================")
    print(f"Running: model={model}")
    print(f"Log:     {json_path}")
    print(f"Output:  {out_path}")
    print(f"==========================================")

    log_text = Path(json_path).read_text()
    json.loads(log_text)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    t0 = time.time()
    try:
        # TASK 1
        print("-> Running TASK 1 (Analysis)...")
        messages.append({"role": "user", "content": TASK1_TEMPLATE.format(json_log=log_text)})
        analysis = chat(messages, model)
        messages.append({"role": "assistant", "content": analysis})

        # TASK 2
        print("-> Running TASK 2 (Descriptive)...")
        messages.append({"role": "user", "content": TASK2})
        descriptive = chat(messages, model)
        messages.append({"role": "assistant", "content": descriptive})

        # TASK 3
        print("-> Running TASK 3 (Evaluative)...")
        messages.append({"role": "user", "content": TASK3})
        evaluative = chat(messages, model)

        elapsed = time.time() - t0
        print(f"[DONE] Finished {model} in {elapsed:.1f}s")

        out_path.write_text(
            f"# Output — {model}\n\n"
            f"*(Generation time: {elapsed:.1f}s)*\n\n"
            f"## Analysis (internal)\n{analysis}\n\n"
            f"## Descriptive part\n{descriptive}\n\n"
            f"## Evaluative part\n{evaluative}\n"
        )
        print(f"Saved: {out_path}")
        
        # Unload model from memory to keep RAM free on 8GB Mac
        try:
            requests.post(OLLAMA_URL, json={"model": model, "keep_alive": 0})
        except Exception:
            pass

        return True
    except Exception as e:
        print(f"[ERROR] Failed {model} on {json_path}: {e}")
        try:
            requests.post(OLLAMA_URL, json={"model": model, "keep_alive": 0})
        except Exception:
            pass
        return False


def main():
    target_scenario = sys.argv[1] if len(sys.argv) > 1 else None
    target_strategy = sys.argv[2] if len(sys.argv) > 2 else None
    target_model = sys.argv[3] if len(sys.argv) > 3 else None

    for r in RUNS:
        if target_scenario and r["scenario"] != target_scenario:
            continue
        if target_strategy and r["strategy"] != target_strategy:
            continue

        for m in MODELS:
            if target_model and m != target_model:
                continue
            run_single(r["log"], m, r["out_dir"])


if __name__ == "__main__":
    main()

