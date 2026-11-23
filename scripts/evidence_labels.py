"""
Before/after evidence labels for player decisions and actions.

For every event decision and action use, compare how each Quadruple Aim score
moved in the window BEFORE it with the window AFTER it, and turn the pair into
a label:

    no unusual change after                          the move afterwards is within this game's normal noise
    already rising before / already falling before   unusual move, but the score was moving that way anyway
    rebounded after a fall / after a rise            unusual move that undoes an unusual move just before
    rose after / fell after                          an unusual, new movement starting at the decision
    ... shared with: <other decisions/actions>       the same window holds other decisions, so no single one
                                                     can be credited

"Unusual" is judged per player and per score: the change over the window must be
at least 3 times the typical (median) window change of that score in the same
game, and at least 4 points. The median is used because a few large real swings
would inflate a percentile or a standard deviation. Endpoints are 3-day means,
so one noisy day cannot create a label.

A feedback text may link a decision to a score change only when the label is
"rose after" or "fell after" in the same direction and not shared. Everything
else is noise, a trend already under way, a rebound, or a coincidence of timing.

Even then the label is only evidence of TIMING, not of cause: it says the
decision is the only recorded decision or action in front of an unusual change.

Works on both export shapes: a single player (our 21-60-day logs) and a host
export with players_data (the platform's 364-day sessions). The warm-up length
and the week numbering are taken from the platform's own code
(healthcare-wargame-main/backend/ai_feedback), loaded read-only.

Usage:
    python scripts/evidence_labels.py <export.json> [--player N] [--unusual]
"""
import importlib.util
import json
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLATFORM_FEEDBACK = ROOT / "healthcare-wargame-main" / "backend" / "ai_feedback"

AIMS = ("staff_wellbeing", "patient_health", "patient_experience", "cost_reduction")
LABELS = {"staff_wellbeing": "staff wellbeing", "patient_health": "patient health",
          "patient_experience": "patient experience", "cost_reduction": "cost reduction"}
VISIBLE = 4.0       # points; minimum, the platform calls a 4-point change "slightly"
NOISE_MULTIPLE = 3.0  # a change must be at least 3x the typical (median) window change of that score
ALREADY = 0.5       # "already moving" = the before-window moved at least half the threshold the same way


def _load_platform_module(name: str):
    """Load one module from the platform's ai_feedback folder without importing its package
    (which needs Redis, httpx and PyYAML) and without writing bytecode into that folder."""
    sys.dont_write_bytecode = True
    if "yaml" not in sys.modules:
        try:
            import yaml  # noqa: F401
        except ImportError:  # digest.py imports yaml only to read action button labels; it falls back to ids
            stub = types.ModuleType("yaml")
            stub.safe_load = lambda *_a, **_k: {}
            sys.modules["yaml"] = stub
    spec = importlib.util.spec_from_file_location(f"platform_ai_feedback_{name}", PLATFORM_FEEDBACK / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_digest = _load_platform_module("digest")
_trends = _load_platform_module("trends")
warmup_days = _digest.warmup_days
week = _trends.week


def window_days(days_planned: int) -> int:
    """7 days for short games, 14 for a year (the platform's swing window for long games)."""
    return max(7, min(14, days_planned // 10))


def players(path: Path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data = data.get("data", data)
    return data.get("players_data") or [data]


def _series(player: dict) -> dict:
    return {aim: {r["day"]: r[aim] for r in player["daily_metrics"] if r.get(aim) is not None} for aim in AIMS}


def _smooth(values: dict, day: int):
    """3-day mean around a day (fewer days at the edges)."""
    pts = [values[d] for d in (day - 1, day, day + 1) if d in values]
    return sum(pts) / len(pts) if pts else None


def thresholds(series: dict, window: int, warmup: int) -> dict:
    """Per score: NOISE_MULTIPLE x the median window change after warm-up (floor VISIBLE)."""
    out = {}
    for aim, values in series.items():
        days = [d for d in sorted(values) if d > warmup and d + window in values]
        changes = sorted(abs(_smooth(values, d + window) - _smooth(values, d)) for d in days)
        typical = changes[len(changes) // 2] if changes else 0.0
        out[aim] = max(VISIBLE, NOISE_MULTIPLE * typical)
    return out


def label(before, after, threshold: float, warmup_overlap: bool, shared: list) -> str:
    if after is None:
        return "no data after"
    if abs(after) < threshold:
        return "no unusual change after"
    direction = "rising" if after > 0 else "falling"
    if before is not None and abs(before) >= ALREADY * threshold and (before > 0) == (after > 0):
        return f"already {direction} before"
    if before is not None and abs(before) >= threshold and (before > 0) != (after > 0):
        return f"rebounded after a {'fall' if before < 0 else 'rise'}"
    moved = "rose" if after > 0 else "fell"
    text = f"{moved} after" + (" (before-window in warm-up)" if warmup_overlap else "")
    return text + (f" - shared with: {', '.join(shared)}" if shared else "")


def evidence_for_day(series: dict, day: int, window: int, warmup: int, last_day: int,
                     limits: dict, shared: list) -> dict:
    out = {}
    for aim, values in series.items():
        v, b0 = _smooth(values, day), _smooth(values, day - window)
        a1 = _smooth(values, min(day + window, last_day))
        before = None if (v is None or b0 is None) else v - b0
        after = None if (v is None or a1 is None or day >= last_day) else a1 - v
        out[aim] = {"before": before, "after": after, "threshold": limits[aim],
                    "label": label(before, after, limits[aim], (day - window) <= warmup, shared)}
    return out


def moments(player: dict) -> list:
    """Event decisions and action uses (unlocks excluded), with their day."""
    rows = []
    for e in (player.get("events") or {}).get("event_history", []):
        if e.get("choosed_solution_id") and e.get("triggered_day") is not None:
            rows.append({"day": e["triggered_day"], "kind": "decision",
                         "what": e.get("title") or e.get("event_id"), "choice": e["choosed_solution_id"]})
    for action, uses in ((player.get("final_metrics") or {}).get("actions_taken") or {}).items():
        if action.startswith("unlock_"):
            continue
        for u in uses or []:
            if isinstance(u, dict) and u.get("purchase_day") is not None:
                rows.append({"day": u["purchase_day"], "kind": "action", "what": action})
    unique = {(r["day"], r["kind"], r["what"], r.get("choice")): r for r in rows}  # same action twice a day = one moment
    return sorted(unique.values(), key=lambda r: r["day"])


def evidence(player: dict) -> dict:
    meta = player.get("simulation_metadata") or {}
    planned = int(meta.get("simulation_days") or meta.get("current_day") or 0)
    last_day = max(r["day"] for r in player["daily_metrics"])
    warmup, window = warmup_days(planned), window_days(planned)
    series = _series(player)
    limits = thresholds(series, window, warmup)
    all_moments = moments(player)
    rows = []
    for m in all_moments:
        if m["day"] <= warmup:
            rows.append({**m, "note": "inside warm-up: no evidence either way"})
            continue
        others = sorted({o["what"] for o in all_moments
                         if o is not m and m["day"] - 1 <= o["day"] <= m["day"] + window and o["what"] != m["what"]})
        rows.append({**m, "week": week(m["day"]), "shared_with": others,
                     "scores": evidence_for_day(series, m["day"], window, warmup, last_day, limits, others)})
    return {"warmup_days": warmup, "window_days": window, "last_day": last_day,
            "thresholds": limits, "moments": rows}


def _fmt(x):
    return "  n/a" if x is None else f"{x:+5.1f}"


def print_report(player: dict, only_unusual: bool = False):
    ev = evidence(player)
    lim = ", ".join(f"{LABELS[a]} {t:.1f}" for a, t in ev["thresholds"].items())
    print(f"== {player.get('player_name')} | warm-up {ev['warmup_days']} days, window {ev['window_days']} days")
    print(f"   unusual-change thresholds (points): {lim}")
    for m in ev["moments"]:
        head = f"day {m['day']:>3} (week {week(m['day']):>2}) {m['kind']:<8} {m['what']}" + (f" -> {m['choice']}" if m.get("choice") else "")
        if "scores" not in m:
            print(f"  {head}   [{m['note']}]")
            continue
        lines = [f"      {LABELS[a]:<19} before {_fmt(s['before'])}  after {_fmt(s['after'])}  -> {s['label']}"
                 for a, s in m["scores"].items() if not (only_unusual and s["label"].startswith("no "))]
        if lines or not only_unusual:
            print(f"  {head}")
            print("\n".join(lines) if lines else "      (no unusual change in any score)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = Path(sys.argv[1])
    only = int(sys.argv[sys.argv.index("--player") + 1]) if "--player" in sys.argv else None
    for i, p in enumerate(players(path)):
        if only is None or i == only:
            print_report(p, only_unusual="--unusual" in sys.argv)
