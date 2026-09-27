"""
Run the 3-step (analysis -> descriptive -> evaluative) prompt against a
local Ollama model, using a real APOLLO2028 simulation JSON log.

The raw JSON log is first converted into a compact table (see
table_converter.py) before being handed to the model - this cuts token
count by ~95% on long runs and reduces the recency bias small models show
on 60-day logs (see experiments/COMPARISON.md).

Requires Ollama running locally (`ollama serve`) with the target model
already pulled (see MODEL_SHORTLIST.md).

Usage:
    python run_generation.py path/to/log.json phi3.5
    python run_generation.py path/to/log.json qwen2.5:3b
"""
import sys
import time
from pathlib import Path

import requests

from table_converter import build_context_table, get_total_days

OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = """You are assisting with the APOLLO2028 Business Game, a hospital-management \
simulation. Players are scored on four axes: Patient Experience, Patient \
Health, Cost Reduction, and Staff Wellbeing. Simulations can run up to 60 \
days, and every day matters equally - do not let the most recent days \
dominate your analysis; a player's early and mid-game decisions are just \
as important as how they finished. After each session, players receive a \
report with two parts: a DESCRIPTION of what happened, and an EVALUATION \
of what it meant. You will be given the simulation log as a compact table \
(a final outcome summary, a daily metrics table, an event log, and an \
actions-used summary). Work through this in three steps as instructed, \
one at a time."""

TASK1_TEMPLATE = """Here is the simulation log, converted into a compact table:

{table}

TASK 1 - Analyze this log internally before writing anything player-facing. \
The daily metrics table covers all {total_days} days of the run, from Day 0 \
to Day {total_days}. Review the FULL table - early days ({early_range}), \
middle days ({mid_range}), and late days ({late_range}) all matter equally. \
Do not let the final rows dominate your analysis just because they come \
last. Identify:
- the overall trend of each of the four scores (staff_wellbeing, \
patient_health, patient_experience, cost_reduction) across the run
- any sharp increases or decreases, and the day they occurred - scan the \
whole table, including {early_range}
- whether any sharp change coincides with an entry in the event log, and if \
so, which event and what choice was made
- any notable absences: actions listed as "never used" in the actions \
summary, especially if a related score was declining
- overall outcome: days completed, patients treated and success rate, \
staff resignations, final financial result

List these findings as short bullet points. Include at least one bullet \
about something from {early_range} and one about {mid_range} - not only \
the ending."""

TASK2 = """TASK 2 - Using only the findings above, write the DESCRIPTIVE part \
of the report: 3-5 sentences, factual and neutral in tone, written from the \
system's point of view. You must include:
- the starting financial balance (Day 0) and the ending financial balance
- the overall outcome
- at least one specific moment from the first half of the run AND one from \
the second half (a day, an event, or a sharp change) - do not describe only \
the ending
Do not include judgment or evaluation here."""

TASK3 = """TASK 3 - Now write the EVALUATIVE part: 3-5 sentences giving a \
high-level assessment of what these results mean for the player. Reference \
at least one specific, concrete detail from the findings - it does not have \
to be from the ending, pick whichever moment is most meaningful. The tone \
must remain encouraging and constructive throughout, even where results \
were weak or mixed."""


def day_thirds(total_days: int) -> dict:
    third = max(1, total_days // 3)
    return {
        "total_days": total_days,
        "early_range": f"Day 0-{third}",
        "mid_range": f"Day {third + 1}-{2 * third}",
        "late_range": f"Day {2 * third + 1}-{total_days}",
    }


def chat(messages: list, model: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={"model": model, "messages": messages, "stream": False},
        timeout=900,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def run(json_path: str, model: str, output_dir: str = None):
    table = build_context_table(json_path)
    thirds = day_thirds(get_total_days(json_path))

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"=== Model: {model} ===\n")

    t0 = time.time()
    messages.append({"role": "user", "content": TASK1_TEMPLATE.format(table=table, **thirds)})
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
