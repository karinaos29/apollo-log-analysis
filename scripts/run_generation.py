"""
Run the 3-step (analysis -> descriptive -> evaluative) prompt against a
local Ollama model, using a real APOLLO2028 simulation JSON log.

Requires Ollama running locally (`ollama serve`) with the target model
already pulled (see MODEL_SHORTLIST.md).

Usage:
    python run_generation.py path/to/log.json phi3.5
    python run_generation.py path/to/log.json qwen2.5:3b
"""
import json
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


def chat(messages: list, model: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={"model": model, "messages": messages, "stream": False},
        timeout=600,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def run(json_path: str, model: str, output_dir: str = None):
    log_text = Path(json_path).read_text()
    # sanity check it's valid JSON before spending tokens on it
    json.loads(log_text)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"=== Model: {model} ===\n")

    t0 = time.time()
    messages.append({"role": "user", "content": TASK1_TEMPLATE.format(json_log=log_text)})
    analysis = chat(messages, model)
    messages.append({"role": "assistant", "content": analysis})
    print("--- TASK 1: Analysis ---")
    print(analysis, "\n")

    messages.append({"role": "user", "content": TASK2})
    descriptive = chat(messages, model)
    messages.append({"role": "assistant", "content": descriptive})
    print("--- TASK 2: Descriptive part ---")
    print(descriptive, "\n")

    messages.append({"role": "user", "content": TASK3})
    evaluative = chat(messages, model)
    print("--- TASK 3: Evaluative part ---")
    print(evaluative, "\n")

    elapsed = time.time() - t0
    print(f"(total time: {elapsed:.1f}s)")

    out_dir = Path(output_dir) if output_dir else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"output_{model.replace(':', '_')}.md"
    out_path.write_text(
        f"# Output — {model}\n\n"
        f"*(Generation time: {elapsed:.1f}s)*\n\n"
        f"## Analysis (internal)\n{analysis}\n\n"
        f"## Descriptive part\n{descriptive}\n\n"
        f"## Evaluative part\n{evaluative}\n"
    )
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_generation.py <log.json> <model_name> [output_dir]")
        sys.exit(1)
    out_dir = sys.argv[3] if len(sys.argv) > 3 else None
    run(sys.argv[1], sys.argv[2], out_dir)
