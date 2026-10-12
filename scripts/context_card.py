"""
Builds a "context card" from a raw APOLLO2028 simulation JSON log: a short,
deterministic fact sheet (start/end balances, patient counts, per-axis changes,
notable score swings, the player's decisions) that goes into the prompt in
place of the full daily table.

Every number is computed here, so the model only has to turn facts into
sentences. The module also validates a generated report against the same facts
(wrong day for a decision, numbers that are not on the card, missing axes).

Usage:
    python context_card.py path/to/log.json
"""
import json
import re
import sys
from pathlib import Path

AXES = [
    ("staff_wellbeing", "staff wellbeing"),
    ("patient_health", "patient health"),
    ("patient_experience", "patient experience"),
    ("cost_reduction", "cost reduction"),
]

EPISODE_THRESHOLD = 8   # cumulative one-direction move that counts as a notable swing
TOP_EPISODES = 3
SKIP_STARTUP_DAYS = 2   # first days reflect simulation calibration, not player actions
FOLLOW_UP_DAYS = 7
NON_STRATEGIC_ACTION_PREFIXES = ("unlock_",)
OPINION_WORDS = ("excellent", "impressive", "poor", "disappointing", "great", "strong", "effective", "effectively",
                 "commendable", "robust", "remarkable", "outstanding", "praiseworthy", "success of")
CAUSAL_PHRASES = ("led to", "resulted in", "caused", "because of", "due to", "thanks to", "triggered", "as a result")


def _money(v) -> str:
    return f"${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}"


def _signed_money(v) -> str:
    return ("+" if v >= 0 else "-") + f"${abs(v):,.0f}"


def _readable(solution_id: str) -> str:
    return solution_id.replace("_", " ")


def _swing_episodes(series: list) -> list:
    """Monotone runs whose cumulative move is >= EPISODE_THRESHOLD.

    Returns (magnitude, start_day, end_day). Same definition the scorer uses,
    so the days on the card are the days a reader would call notable.
    """
    out = []
    i = max(1, SKIP_STARTUP_DAYS)
    while i < len(series):
        direction = 1 if series[i] > series[i - 1] else -1 if series[i] < series[i - 1] else 0
        if direction == 0:
            i += 1
            continue
        start = i - 1
        j = i
        while j < len(series) - 1:
            nxt = 1 if series[j + 1] > series[j] else -1 if series[j + 1] < series[j] else 0
            if nxt != direction:
                break
            j += 1
        if abs(series[j] - series[start]) >= EPISODE_THRESHOLD:
            out.append((abs(series[j] - series[start]), start, j))
        i = j + 1
    return out


def compute_facts(json_path: str) -> dict:
    data = json.loads(Path(json_path).read_text())
    daily = data["daily_metrics"]
    final = data.get("final_metrics", {})
    meta = data.get("simulation_metadata", {})
    last_day = daily[-1]["day"]

    start_balance = daily[0]["finance_remaining"]
    end_balance = final.get("final_finance", daily[-1]["finance_remaining"])

    treated = final.get("total_patients_treated", 0)
    ok = final.get("patients_treated_successfully", 0)

    axes = {}
    for key, label in AXES:
        series = [row[key] for row in daily]
        lo = min(range(len(series)), key=lambda d: series[d])
        hi = max(range(len(series)), key=lambda d: series[d])
        axes[key] = {
            "label": label, "start": series[0], "end": series[-1],
            "lowest": (series[lo], daily[lo]["day"]), "highest": (series[hi], daily[hi]["day"]),
            "series": series,
        }

    episodes = []
    for key, label in AXES:
        for mag, s, e in _swing_episodes(axes[key]["series"]):
            episodes.append({
                "axis": label, "magnitude": mag,
                "start_day": daily[s]["day"], "end_day": daily[e]["day"],
                "from": axes[key]["series"][s], "to": axes[key]["series"][e],
            })
    episodes.sort(key=lambda x: -x["magnitude"])
    episodes = sorted(episodes[:TOP_EPISODES], key=lambda x: x["end_day"])

    decisions = []
    for ev in data.get("events", {}).get("event_history", []):
        choice_id = ev.get("choosed_solution_id")
        if not choice_id:
            continue  # weekly summaries etc.: no player decision
        title = ev.get("title") or ev.get("result", {}).get("event_title") or ev.get("event_id")
        options = {(s.get("id") or s.get("solution_id")): (s.get("title") or s.get("name"))
                   for s in ev.get("solutions", [])}
        if choice_id in options:
            chosen = options[choice_id]
        elif choice_id == "do_nothing":
            chosen = "Take no action"
        else:
            chosen = _readable(choice_id)
        others = [t for sid, t in options.items() if sid != choice_id]
        cost = ev.get("result", {}).get("total_cost_locked") or 0
        day = ev.get("triggered_day")
        end_idx = min(day + FOLLOW_UP_DAYS, last_day)
        follow = {}
        if day is not None and day < len(daily):
            for key, label in AXES:
                follow[label] = axes[key]["series"][end_idx] - axes[key]["series"][day]
        decisions.append({
            "day": day, "title": title, "chosen": chosen, "cost": cost,
            "not_chosen": others, "follow_end_day": end_idx, "follow": follow,
        })
    decisions.sort(key=lambda d: d["day"])

    used, unused = [], []
    for name, occ in final.get("actions_taken", {}).items():
        if name.startswith(NON_STRATEGIC_ACTION_PREFIXES):
            continue
        if occ:
            days = [str(o.get("purchase_day")) for o in occ if isinstance(o, dict) and o.get("purchase_day") is not None]
            used.append(f"{_readable(name)} (day {', '.join(days)})" if days else _readable(name))
        else:
            unused.append(_readable(name))

    return {
        "scenario": data.get("player_metadata", {}).get("scenario", {}).get("scenario_name", "unknown"),
        "last_day": last_day, "completed": meta.get("is_completed"),
        "start_balance": start_balance, "end_balance": end_balance,
        "treated": treated, "ok": ok, "failed": final.get("patients_treated_unsuccessfully", 0),
        "success_pct": round(100 * ok / treated, 1) if treated else None,
        "resignations": final.get("staff_resignations", 0),
        "overall_score": data.get("performance", {}).get("score"),
        "axes": axes, "episodes": episodes, "decisions": decisions,
        "actions_used": used, "actions_unused": unused,
    }


def render_card(f: dict) -> str:
    lines = [
        f"Scenario: {f['scenario']} | Length: {f['last_day']} days | Completed: {'yes' if f['completed'] else 'no'}",
        f"Money: started with {_money(f['start_balance'])}, ended with {_money(f['end_balance'])} "
        f"(change {_signed_money(f['end_balance'] - f['start_balance'])})",
        f"Patients: {f['treated']:,} treated, {f['ok']:,} successful ({f['success_pct']}%), {f['failed']:,} unsuccessful",
        f"Staff resignations: {f['resignations']}",
    ]
    if f["overall_score"] is not None:
        lines.append(f"Overall score: {f['overall_score']}")
    lines.append("Scores (start -> end, 0-100):")
    for key, _ in AXES:
        a = f["axes"][key]
        delta = a["end"] - a["start"]
        word = "up" if delta > 0 else "down" if delta < 0 else "unchanged"
        lines.append(
            f"- {a['label']}: {a['start']:.1f} -> {a['end']:.1f} ({word} {abs(delta):.1f}); "
            f"lowest {a['lowest'][0]:.1f} on Day {a['lowest'][1]}, highest {a['highest'][0]:.1f} on Day {a['highest'][1]}"
        )
    if f["episodes"]:
        lines.append("Notable score swings:")
        for e in f["episodes"]:
            word = "rose" if e["to"] > e["from"] else "fell"
            lines.append(f"- {e['axis']} {word} from {e['from']:.1f} to {e['to']:.1f} between Day {e['start_day']} and Day {e['end_day']}")
    lines.append("Player decisions (in order):")
    if not f["decisions"]:
        lines.append("- none")
    for i, d in enumerate(f["decisions"], 1):
        cost = f", cost {_money(d['cost'])}" if d["cost"] else ""
        lines.append(f'{i}. Day {d["day"]}, event "{d["title"]}": chose "{d["chosen"]}"{cost}')
        if d["not_chosen"]:
            lines.append("   not chosen: " + "; ".join(d["not_chosen"]))
        moves = ", ".join(f"{k} {v:+.1f}" for k, v in d["follow"].items())
        lines.append(f"   scores Day {d['day']} -> Day {d['follow_end_day']} (observed, not necessarily caused by the decision): {moves}")
    lines.append("Strategic actions used: " + (", ".join(f["actions_used"]) if f["actions_used"] else "none"))
    lines.append("Strategic actions never used: " + (", ".join(f["actions_unused"]) if f["actions_unused"] else "none"))
    return "\n".join(lines)


def build_context_card(json_path: str):
    """Returns (card_text, facts_dict)."""
    facts = compute_facts(json_path)
    return render_card(facts), facts


# ---------------------------------------------------------------- validation

def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def _money_mentioned(text: str, value: float) -> bool:
    want = _digits(f"{value:,.0f}")
    for m in re.finditer(r"\$?\d[\d,]*(?:\.\d+)?", text):
        if _digits(m.group(0).split(".")[0]) == want:
            return True
    # "5.26 million" style
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:million|m\b)", text, re.IGNORECASE):
        if abs(float(m.group(1)) * 1_000_000 - value) / max(value, 1) < 0.005:
            return True
    return False


def clean_generation(text: str, truncated: bool = False):
    """Cut a degenerate tail (runs of zeros) or a half-finished last sentence.

    Returns (clean_text, note_or_None).
    """
    note = None
    paragraphs = [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    if len(paragraphs) > 1:
        text, note = paragraphs[0], "kept only the first paragraph (dropped extra text / meta-notes)"
    m = re.search(r"\S*0{5,}", text)
    if m:
        text, note = text[:m.start()], (note + "; " if note else "") + "removed degenerate zero-run at the end"
        truncated = True
    if truncated:
        # last real sentence end: . ! ? followed by whitespace or the end (not a decimal point)
        ends = [m.end() for m in re.finditer(r"[.!?](?=\s|$)", text)]
        if ends:
            text = text[: ends[-1]]
        note = (note + "; " if note else "") + "cut back to the last complete sentence"
    return text.strip(), note


def _sentences(text: str) -> list:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def validate_part(facts: dict, card: str, text: str, kind: str) -> list:
    """Check one report part against the facts. kind: 'descriptive' or 'evaluative'.

    The descriptive part carries the mandatory facts (balances, all four scores,
    decisions); the evaluative part only needs to stay consistent with the card.
    Returns a list of problem descriptions (empty list = passed).
    """
    problems = []
    low = text.lower()

    if kind == "descriptive":
        if not _money_mentioned(text, facts["start_balance"]):
            problems.append(f"state the starting balance exactly: {_money(facts['start_balance'])}")
        if not _money_mentioned(text, facts["end_balance"]):
            problems.append(f"state the ending balance exactly: {_money(facts['end_balance'])}")
        missing = [label for _, label in AXES if label not in low]
        if missing:
            problems.append("name these scores and say whether each went up or down: " + ", ".join(missing))

    wanted = min(2, len(facts["decisions"])) if kind == "descriptive" else min(1, len(facts["decisions"]))
    named = sum(1 for d in facts["decisions"] if d["title"].lower() in low or d["chosen"].lower() in low)
    if named < wanted:
        examples = "; ".join(f'Day {d["day"]} "{d["title"]}"' for d in facts["decisions"][:: max(1, len(facts["decisions"]) // 2)][:2])
        problems.append(f"name at least {wanted} player decision(s) by copying the exact event title in quotes, e.g. {examples}")

    if kind == "descriptive":
        if "evaluat" in low:
            problems.append("write only the description; leave the evaluation for the next step")
        opinion = [w for w in OPINION_WORDS if re.search(rf"\b{w}", low)]
        if opinion:
            problems.append("remove opinion words (" + ", ".join(opinion) + "); stay neutral")
        causal = [w for w in CAUSAL_PHRASES if w in low]
        if causal:
            problems.append("do not claim causes (" + ", ".join(causal) + "); say what the scores did afterwards")

    # numbers that are not on the card (small integers are sentence counts / day numbers)
    card_numbers = {_digits(n) for n in re.findall(r"\d[\d,]*(?:\.\d+)?", card)}
    card_numbers |= {_digits(n.split(".")[0]) for n in re.findall(r"\d[\d,]*\.\d+", card)}
    for m in re.finditer(r"(?<![\w.])\$?\d[\d,]*(?:\.\d+)?%?", text):
        raw = m.group(0)
        num = raw.strip("$%")
        if re.fullmatch(r"\d{1,2}", num):
            continue
        if _digits(num) in card_numbers or _digits(num.split(".")[0]) in card_numbers:
            continue
        problems.append(f"remove {raw}: it is not on the fact card")

    # a decision must be tied to its own day
    for sent in _sentences(text):
        days = {int(x) for x in re.findall(r"\bDay\s+(\d+)", sent, re.IGNORECASE)}
        if not days:
            continue
        for d in facts["decisions"]:
            if (d["title"].lower() in sent.lower() or d["chosen"].lower() in sent.lower()) and d["day"] not in days:
                problems.append(f'"{d["title"]}" happened on Day {d["day"]}, not Day {sorted(days)[0]}')
                break

    n = len(_sentences(text))
    if not 3 <= n <= 5:
        hint = " by merging related facts into one sentence" if n > 5 else ""
        problems.append(f"write 3-5 sentences, not {n}{hint}")
    return problems


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python context_card.py <log.json>")
        sys.exit(1)
    card, _ = build_context_card(sys.argv[1])
    print(card)
    print(f"\n--- {len(card)} chars (~{len(card) // 4} tokens) ---", file=sys.stderr)
