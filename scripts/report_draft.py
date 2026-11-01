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
from difflib import SequenceMatcher
import re
import zlib

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
    # Prioritize pivotal decisions by impact score, preserved in chronological order
    ranked_decs = sorted(f["decisions"], key=lambda d: -d.get("impact_score", 0))
    top_decs = sorted(ranked_decs[:MAX_DECISIONS], key=lambda d: d["day"])
    for i, d in enumerate(top_decs, 1):
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

def _style_index(f: dict, n: int) -> int:
    """Pick a phrasing variant from the session itself, so the same log always gives the same text.

    (Python's built-in hash() of a string changes between runs, so it is not used here.)
    """
    key = f"{f.get('scenario', '')}|{f.get('start_balance', 0):.0f}|{f.get('end_balance', 0):.0f}|{f.get('last_day', 0)}"
    return zlib.crc32(key.encode("utf-8")) % n


def draft_descriptive(p: dict, f: dict, style_idx: int = None) -> str:
    """Neutral, factual description (4-5 sentences), phrased in one of three variants.

    Wording rule: report what happened, never how good it was (no "positive",
    "pivotal", "achieving", "held to"), and no time words the facts do not support.
    """
    if style_idx is None:
        style_idx = _style_index(f, 3)
    pick = lambda opts: opts[style_idx % len(opts)]

    days, start, end = f["last_day"], f["start_balance"], f["end_balance"]
    money = f"{_money(start)} to {_money(end)} ({_signed_money(end - start)})"
    parts = [pick([
        f"Over the {days}-day session, the hospital's balance went from {money}.",
        f"The hospital's balance moved from {money} during the {days}-day simulation.",
        f"Across the {days}-day run, the hospital's funds changed from {money}.",
    ])]

    r = f["resignations"]
    res = ("no staff members resigned" if r == 0 else
           "1 staff member resigned" if r == 1 else f"{r} staff members resigned")
    pct = f"{f['success_pct']}%" if f.get("success_pct") is not None else "an unknown share"
    parts.append(pick([
        f"In total, {f['treated']:,} patients were treated, {f['ok']:,} of them successfully ({pct}), and {res}.",
        f"Of the {f['treated']:,} patients treated, {f['ok']:,} were treated successfully ({pct}), and {res}.",
        f"The hospital treated {f['treated']:,} patients with a success rate of {pct} ({f['ok']:,} successful), and {res}.",
    ]))

    rose, fell, flat = [], [], []
    for k, label in AXES:
        a = f["axes"][k]
        d = a["end"] - a["start"]
        if abs(d) < 0.05:
            flat.append(f"{label} stayed at {a['start']:.1f}")
        elif d > 0:
            rose.append(f"{label} rose from {a['start']:.1f} to {a['end']:.1f}")
        else:
            fell.append(f"{label} fell from {a['start']:.1f} to {a['end']:.1f}")
    if rose and fell:
        s3 = pick([
            f"By the end of the run, {_join_and(rose)}, while {_join_and(fell)}.",
            f"Across the four scores, {_join_and(rose)}, whereas {_join_and(fell)}.",
            f"Of the four scores, {_join_and(rose)}, and {_join_and(fell)}.",
        ])
    elif rose:
        s3 = f"All scores that changed went up: {_join_and(rose)}."
    elif fell:
        s3 = f"All scores that changed went down: {_join_and(fell)}."
    else:
        s3 = ""
    if flat:
        s3 = (s3 + " " if s3 else "") + f"Unchanged: {_join_and(flat)}."
    parts.append(s3)

    swings = []
    for e in f["episodes"][:2]:
        noun = "rise" if e["to"] > e["from"] else "fall"
        swings.append(f"a {noun} in {e['axis']} from {e['from']:.1f} to {e['to']:.1f} "
                      f"between Day {e['start_day']} and Day {e['end_day']}")
    if swings:
        parts.append(pick([
            f"The largest score swings were {_join_and(swings)}.",
            f"Notable score swings included {_join_and(swings)}.",
            f"Among the largest score movements were {_join_and(swings)}.",
        ]))

    # up to three decisions, chosen by impact_score (cost, action taken, size of the following week's
    # score change), listed in chronological order
    ranked = sorted(f["decisions"], key=lambda d: -d.get("impact_score", 0))
    top = sorted(ranked[:3], key=lambda d: d["day"])
    decs = []
    for d in top:
        if d["chosen"] == "Take no action":
            choice = "the player took no action"
        else:
            cost = f" (cost {_money(d['cost'])})" if d["cost"] else ""
            choice = f'the player chose "{d["chosen"]}"{cost}'
        decs.append(f'on Day {d["day"]}, at the event "{d["title"]}", {choice}')
    if decs:
        parts.append(pick([
            "Key decisions were: " + "; ".join(decs) + ".",
            "The player's decisions included: " + "; ".join(decs) + ".",
            "Decisions at key events included: " + "; ".join(decs) + ".",
        ]))
    return " ".join(x for x in parts if x)


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
        # unused-action names are raw labels ("wellness program", "hire nurse"), so quote them instead of
        # building a sentence that needs articles and verb agreement
        names = _join_and(['"' + p[k] + '"' for k in ("UNUSED_1", "UNUSED_2") if k in p])
        parts.append(f"Options that were not used in this run, such as {names}, could be useful next steps.")
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


def _clean_quote(q: str) -> str:
    return re.sub(r"^[\s\"'.,:;!?-]+|[\s\"'.,:;!?-]+$", "", q)


def _normalize(s: str) -> str:
    return re.sub(r"[^\w\s]", "", s.lower()).strip()


def validate_evaluative(text: str, facts: dict, phrases: dict) -> list:
    problems = []
    low = text.lower()
    digits = re.findall(r"\d+", re.sub(r"APOLLO\s?2028", "APOLLO", text, flags=re.IGNORECASE))
    if digits:
        problems.append("write no digits at all (found: " + ", ".join(digits[:4]) + "); refer to scores by name and direction")

    decision_targets = set()
    all_valid_targets = set()

    for d in facts["decisions"]:
        decision_targets.add(d["title"])
        all_valid_targets.add(d["title"])
        # Add subtitles or split parts (e.g. "Talent War: Competitors Offering Sign-On Bonuses" -> "Competitors Offering Sign-On Bonuses")
        # a title's sub-parts ("Talent War: Competitors Offering Sign-On Bonuses" -> "Competitors Offering
        # Sign-On Bonuses") count, but only at real separators and only if they are 2+ words
        for part in re.split(r":|—| - ", d["title"]):
            p_strip = part.strip()
            if len(p_strip.split()) >= 2:
                decision_targets.add(p_strip)
                all_valid_targets.add(p_strip)
        decision_targets.add(d["chosen"])
        all_valid_targets.add(d["chosen"])
        for o in d["not_chosen"]:
            all_valid_targets.add(o)

    for a in facts.get("actions_used", []) + facts.get("actions_unused", []):
        all_valid_targets.add(a)
    for k in ("UNUSED_1", "UNUSED_2"):
        if k in phrases:
            all_valid_targets.add(phrases[k])

    raw_quotes = _quotes(text)
    cleaned_quotes = {_clean_quote(q) for q in raw_quotes}
    cleaned_quotes = {q for q in cleaned_quotes if q}

    def matches_target(q_str: str, target_pool: set) -> bool:
        nq = _normalize(q_str)
        if not nq:
            return False
        for target in target_pool:
            nt = _normalize(target)
            if nq == nt:
                return True
            # partial or near matches only for specific quotes: a single generic word such as
            # "Strategic" must not count as naming a decision
            if len(nq) < 12 or len(nq.split()) < 2:
                continue
            if nq in nt or nt in nq:
                return True
            if SequenceMatcher(None, nq, nt).ratio() >= 0.82:
                return True
        return False

    bad = []
    for q in cleaned_quotes:
        if not matches_target(q, all_valid_targets):
            bad.append(q)
    if bad:
        problems.append("these quoted names are not recognized event titles or options: " + "; ".join(bad[:3]))

    if facts["decisions"]:
        has_decision = any(matches_target(q, decision_targets) for q in cleaned_quotes)
        if not has_decision:
            problems.append("cite at least one decision by copying its event title (or chosen option) in double quotes")

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
