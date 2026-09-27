"""
Converts a raw APOLLO2028 simulation JSON log into a compact table format
before it's handed to the model, to cut token count and reduce recency bias
on long (60-day) runs.

This is a format conversion only: it flattens/restates fields that already
exist in the JSON (per-day metrics, event log, final totals). It does not
compute trends, detect sharp changes, or correlate events with score
shifts — that reasoning still happens inside the prompt (TASK 1), over this
table, as the model's own first step.

Usage:
    python table_converter.py path/to/log.json
"""
import json
import sys
from pathlib import Path

DAILY_COLUMNS = [
    ("day", "day"),
    ("staff_wellbeing", "staff_wellbeing"),
    ("patient_health", "patient_health"),
    ("patient_experience", "patient_experience"),
    ("cost_reduction", "cost_reduction"),
    ("finance_remaining", "finance"),
    ("patients_treated_successfully_total", "patients_ok"),
    ("patients_treated_unsuccessfully_total", "patients_fail"),
    ("staff_resignations", "resignations"),
]

# UI/dashboard unlocks aren't hospital-management decisions - excluded so
# the "never used" list only surfaces actions that actually affect the sim.
NON_STRATEGIC_ACTION_PREFIXES = ("unlock_",)


def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.1f}"
    if v is None:
        return ""
    return str(v)


def _fmt_finance(v) -> str:
    # comma-separated, whole dollars - large undelimited numbers (e.g.
    # 3351684.6) are a known misread source for small models (a digit gets
    # dropped or the decimal point gets mistaken for a thousands separator).
    if isinstance(v, (int, float)):
        return f"{v:,.0f}"
    return _fmt(v)


def build_daily_table(daily_metrics: list) -> str:
    # pipe-delimited, not comma-delimited: finance values use "," as a
    # thousands separator (e.g. "3,351,684") so a comma can't double as the
    # column delimiter without corrupting column alignment.
    header = " | ".join(label for _, label in DAILY_COLUMNS)
    lines = [header]
    for row in daily_metrics:
        cells = []
        for key, _ in DAILY_COLUMNS:
            if key == "finance_remaining":
                cells.append(_fmt_finance(row.get(key)))
            else:
                cells.append(_fmt(row.get(key)))
        lines.append(" | ".join(cells))
    return "\n".join(lines)


def build_event_list(event_history: list) -> str:
    lines = []
    for e in event_history:
        day = e.get("triggered_day")
        title = e.get("title") or e.get("result", {}).get("event_title") or e.get("event_id")
        choice_id = e.get("choosed_solution_id")
        if choice_id:
            solutions = {
                (s.get("id") or s.get("solution_id")): (s.get("title") or s.get("name"))
                for s in e.get("solutions", [])
            }
            choice_label = solutions.get(choice_id, choice_id)
            cost = e.get("result", {}).get("total_cost_locked")
            cost_str = f", cost ${cost:,.0f}" if isinstance(cost, (int, float)) and cost else ""
            lines.append(f'Day {day} - {title}: chose "{choice_label}"{cost_str}')
        else:
            lines.append(f"Day {day} - {title} (informational, no decision)")
    return "\n".join(lines) if lines else "(no events recorded)"


def build_actions_summary(actions_taken: dict) -> str:
    used, unused = [], []
    for action, occurrences in actions_taken.items():
        if action.startswith(NON_STRATEGIC_ACTION_PREFIXES):
            continue
        if occurrences:
            days = ", ".join(
                str(o.get("purchase_day")) for o in occurrences
                if isinstance(o, dict) and o.get("purchase_day") is not None
            )
            note = f" (day(s) {days})" if days else ""
            used.append(f"{action} x{len(occurrences)}{note}")
        else:
            unused.append(action)
    lines = ["Actions used: " + (", ".join(used) if used else "none")]
    lines.append("Actions never used: " + (", ".join(unused) if unused else "none"))
    return "\n".join(lines)


def build_final_summary(data: dict) -> str:
    meta = data.get("simulation_metadata", {})
    final = data.get("final_metrics", {})
    perf = data.get("performance", {})
    aim = perf.get("aim_scores", {})
    scenario = data.get("player_metadata", {}).get("scenario", {}).get("scenario_name", "unknown")

    def axis(name):
        v = aim.get(name)
        return f"{v:.1f}" if isinstance(v, (int, float)) else "n/a"

    return "\n".join([
        f"Scenario: {scenario}",
        f"Simulation length: {meta.get('simulation_days')} days "
        f"(completed: {meta.get('is_completed')}, end reason: {meta.get('end_reason')})",
        f"Final financial result: ${final.get('final_finance', 0):,.0f}",
        f"Total patients treated: {final.get('total_patients_treated')} "
        f"({final.get('patients_treated_successfully')} successful, "
        f"{final.get('patients_treated_unsuccessfully')} unsuccessful)",
        f"Staff resignations: {final.get('staff_resignations')}",
        f"Final AIM scores - staff_wellbeing: {axis('staff_wellbeing')}, "
        f"patient_health: {axis('patient_health')}, "
        f"patient_experience: {axis('patient_experience')}, "
        f"cost_reduction: {axis('cost_reduction')}",
        f"Overall score: {perf.get('score')}",
    ])


def get_total_days(json_path: str) -> int:
    data = json.loads(Path(json_path).read_text())
    days = data.get("simulation_metadata", {}).get("simulation_days")
    if days is not None:
        return days
    return len(data.get("daily_metrics", [])) - 1


def build_context_table(json_path: str) -> str:
    data = json.loads(Path(json_path).read_text())
    daily_metrics = data.get("daily_metrics", [])

    final_summary = build_final_summary(data)
    daily_table = build_daily_table(daily_metrics)
    events = build_event_list(data.get("events", {}).get("event_history", []))
    actions = build_actions_summary(data.get("final_metrics", {}).get("actions_taken", {}))

    return (
        f"=== FINAL OUTCOME SUMMARY ===\n{final_summary}\n\n"
        f"=== DAILY METRICS TABLE (one row per day, {len(daily_metrics)} days total) ===\n"
        f"{daily_table}\n\n"
        f"=== EVENT LOG (chronological) ===\n{events}\n\n"
        f"=== ACTIONS TAKEN VS NEVER TAKEN ===\n{actions}\n"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python table_converter.py <log.json>")
        sys.exit(1)
    table = build_context_table(sys.argv[1])
    print(table)
    print(f"\n--- {len(table)} chars (vs {len(Path(sys.argv[1]).read_text())} raw JSON chars) ---", file=sys.stderr)
