"""
Pipeline v4 helpers: deterministic drafts + strict acceptance checks.

Python writes a factual draft of the descriptive part straight from the
session facts, so every number, dollar amount, day and event title is correct
by construction. The model's job is limited to jobs a 3.8B model does reliably:

  * descriptive: rewrite the draft into smoother prose. The rewrite is accepted
    only if it keeps every number and quoted title exactly, adds none, and stays
    neutral (validate_rewrite). Otherwise the draft itself is used.
  * evaluative: write freely, but with NO digits at all, citing decisions by
    their exact quoted event title (validate_evaluative). Otherwise a
    deterministic encouraging text is used.

A first attempt at v4 asked the model to write around {PLACEHOLDERS}; Phi-3.5
could not hold that format (see experiments/v4/COMPARISON.md), hence this design.
"""
import re

from context_card import (AXES, CAUSAL_PHRASES, _money, _sentences, _signed_money, validate_part)

MAX_DECISIONS = 6
# Unused actions worth suggesting first (staff-support actions), in order of preference.
SUGGESTION_ORDER = ["wellness program", "counseling services", "peer support", "burnout training",
                    "protected admin time", "hire nurse", "hire doctor"]
TOKEN_RE = re.compile(r"\{([A-Za-z0-9_]+)\}")
QUOTE_RE = re.compile(r'"([^"]+)"')
HEDGES = ("may ", "might", "could", "possibly", "perhaps", "potentially", "likely", "seems", "appears", "suggests", "hint")


# ------------------------------------------------------------------ phrases

def _score_phrase(a: dict) -> str:
    delta = a["end"] - a["start"]
    if abs(delta) < 0.05:
        return f"{a['label']} stayed at {a['start']:.1f}"
    verb = "rose" if delta > 0 else "fell"
    return f"{a['label']} {verb} from {a['start']:.1f} to {a['end']:.1f}"


def build_phrases(f: dict) -> dict:
    """Ordered dict: name -> ready-made, fully factual phrase."""
    s = {}
    s["MONEY"] = (f"the hospital started with {_money(f['start_balance'])} and ended with "
                  f"{_money(f['end_balance'])} ({_signed_money(f['end_balance'] - f['start_balance'])})")
    s["PATIENTS"] = f"{f['treated']:,} patients were treated, {f['ok']:,} of them successfully ({f['success_pct']}%)"
    r = f["resignations"]
    s["RESIGNATIONS"] = "no staff members resigned" if r == 0 else f"{r} staff member{'s' if r != 1 else ''} resigned"
    for key, _ in AXES:
        s["SCORE_" + key.upper()] = _score_phrase(f["axes"][key])
    for i, e in enumerate(f["episodes"], 1):
        word = "rose" if e["to"] > e["from"] else "fell"
        s[f"SWING{i}"] = (f"{e['axis']} {word} from {e['from']:.1f} to {e['to']:.1f} "
                          f"between Day {e['start_day']} and Day {e['end_day']}")
    for i, d in enumerate(f["decisions"][:MAX_DECISIONS], 1):
        if d["chosen"] == "Take no action":
            choice = "the player took no action"
        else:
            cost = f" (cost {_money(d['cost'])})" if d["cost"] else ""
            choice = f'the player chose "{d["chosen"]}"{cost}'
        s[f"DEC{i}"] = f'on Day {d["day"]}, at the event "{d["title"]}", {choice}'
        s[f"DEC{i}_REF"] = f'the Day {d["day"]} decision at "{d["title"]}"'
    unused = list(f["actions_unused"])
    ordered = [a for a in SUGGESTION_ORDER if a in unused] + [a for a in unused if a not in SUGGESTION_ORDER]
    for i, a in enumerate(ordered[:2], 1):
        s[f"UNUSED_{i}"] = a
    return s


def strengths_and_weak_spots(f: dict):
    up = [f["axes"][k]["label"] for k, _ in AXES if f["axes"][k]["end"] - f["axes"][k]["start"] >= 0.05]
    down = [f["axes"][k]["label"] for k, _ in AXES if f["axes"][k]["end"] - f["axes"][k]["start"] <= -0.05]
    return up, down


def _capitalize_sentences(text: str) -> str:
    def up(m):
        return m.group(1) + m.group(2).upper()
    text = re.sub(r"(^\s*)([a-z])", up, text)
    return re.sub(r"([.!?]\s+)([a-z])", up, text)


def fill(text: str, phrases: dict) -> str:
    return _capitalize_sentences(TOKEN_RE.sub(lambda m: phrases.get(m.group(1).upper(), m.group(0)), text))


def _join_and(items: list) -> str:
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


# ------------------------------------------------------------------- drafts

def draft_descriptive(p: dict, f: dict) -> str:
    """Neutral, factual description (4-5 sentences) built only from computed phrases."""
    scores = _join_and(["{SCORE_%s}" % k.upper() for k, _ in AXES])
    parts = ["{MONEY}.", "In total, {PATIENTS}, and {RESIGNATIONS}.", f"Over the run, {scores}."]
    swings = ["{%s}" % k for k in p if k.startswith("SWING")]
    if swings:
        parts.append("Notable score movements were that " + _join_and(swings[:2]) + ".")
    decs = ["{%s}" % k for k in p if re.fullmatch(r"DEC\d+", k)]
    if decs:
        pick = [decs[0]] if len(decs) == 1 else [decs[0], decs[-1]] if len(decs) < 4 else [decs[0], decs[len(decs) // 2], decs[-1]]
        parts.append("Key decisions were: " + "; ".join(pick) + ".")
    return fill(" ".join(parts), p)


def draft_evaluative(p: dict, f: dict) -> str:
    """Encouraging evaluation built only from computed phrases (fallback for the model's text)."""
    up, down = strengths_and_weak_spots(f)
    ups = ["{SCORE_%s}" % k.upper() for k, _ in AXES if f["axes"][k]["label"] in up]
    downs = ["{SCORE_%s}" % k.upper() for k, _ in AXES if f["axes"][k]["label"] in down]
    parts = []
    if ups:
        parts.append(f"A clear strength of this run is that {_join_and(ups)}.")
    if downs:
        parts.append(f"The best opportunity for next time is that {_join_and(downs)}, which leaves room to improve.")
    unused = ["{%s}" % k for k in ("UNUSED_1", "UNUSED_2") if k in p]
    if unused:
        parts.append(f"Trying {_join_and(unused)} was not part of this run and could be a useful next step.")
    if "DEC1_REF" in p:
        parts.append("Looking back at {DEC1_REF} is a good starting point for planning a different approach.")
    parts.append("With these insights, the next session is a good chance to build on what worked.")
    return fill(" ".join(parts), p)


# -------------------------------------------------------------- acceptance

def _numbers(text: str) -> set:
    text = re.sub(r"APOLLO\s?2028", "APOLLO", text, flags=re.IGNORECASE)  # the game's name is not a fact
    return {re.sub(r"\D", "", m) for m in re.findall(r"\d[\d,]*(?:\.\d+)?", text)}


def trim_sentences(text: str, max_n: int = 5):
    """Shorten to max_n sentences, keeping the first max_n-1 and the closing one. Returns (text, note_or_None)."""
    sents = _sentences(text)
    if len(sents) <= max_n:
        return text, None
    return " ".join(sents[:max_n - 1] + [sents[-1]]), f"trimmed from {len(sents)} to {max_n} sentences (kept the closing sentence)"


def _quotes(text: str) -> set:
    return set(QUOTE_RE.findall(text.replace("“", '"').replace("”", '"')))


def validate_rewrite(draft: str, text: str, facts: dict) -> list:
    """The rewrite may change the wording but not the facts."""
    problems = []
    want, got = _numbers(draft), _numbers(text)
    got_extra = {n for n in got - want if n != str(facts["last_day"])}
    if want - got:
        problems.append("keep every number from the draft exactly; missing: " + ", ".join(sorted(want - got)[:5]))
    if got_extra:
        problems.append("remove numbers that are not in the draft: " + ", ".join(sorted(got_extra)[:5]))
    qw, qg = _quotes(draft), _quotes(text)
    if qw - qg:
        problems.append('keep every quoted title/option exactly as in the draft; missing: ' + "; ".join(sorted(qw - qg)[:3]))
    if qg - qw:
        problems.append("do not add or change quoted titles: " + "; ".join(sorted(qg - qw)[:3]))
    # neutrality, wrong-day, sentence count and score/balance coverage reuse the v3 checks
    for p in validate_part(facts, draft, text, "descriptive"):
        duplicate = "not on the fact card" in p or p.startswith("name at least")
        if p not in problems and not duplicate:
            problems.append(p)
    return problems


def validate_evaluative(text: str, facts: dict, phrases: dict) -> list:
    problems = []
    low = text.lower()
    digits = re.findall(r"\d+", re.sub(r"APOLLO\s?2028", "APOLLO", text, flags=re.IGNORECASE))
    if digits:
        problems.append("write no digits at all (found: " + ", ".join(digits[:4]) + "); refer to scores by name and direction")
    titles = {d["title"] for d in facts["decisions"]}
    options = {d["chosen"] for d in facts["decisions"]} | {o for d in facts["decisions"] for o in d["not_chosen"]}
    q = _quotes(text)
    bad = [x for x in q if x not in titles and x not in options]
    if bad:
        problems.append("these quoted names are not exact event titles or options: " + "; ".join(bad[:3]))
    chosen = {d["chosen"] for d in facts["decisions"]}
    if titles and not any(t in q for t in titles | chosen):
        problems.append("cite at least one decision by copying its exact event title (or the option the player chose) in double quotes")
    unused = [phrases[k].lower() for k in ("UNUSED_1", "UNUSED_2") if k in phrases]
    weak = list(strengths_and_weak_spots(facts)[1])
    if not (any(w in low for w in weak) or any(u in low for u in unused)):
        problems.append("mention a score that fell or an action that was never used")
    # Interpretation is allowed, but a cause may only be suggested, never stated as fact.
    asserted = []
    for sent in _sentences(text):
        sl = sent.lower()
        hit = [w for w in CAUSAL_PHRASES if w in sl]
        if hit and not any(h in sl for h in HEDGES):
            asserted += hit
    if asserted:
        problems.append("a decision's effect may only be suggested (use 'may have', 'could', 'might'), not stated as fact: "
                        + ", ".join(sorted(set(asserted))))
    n = len(_sentences(text))
    if not 3 <= n <= 5:
        problems.append(f"write 3-5 sentences, not {n}")
    return problems
