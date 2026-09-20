"""
Automatic/semi-automatic scoring for generated APOLLO2028 assessment text,
per EVALUATION_CRITERIA_v2.md.

Usage:
    python score_outputs.py <log.json> <output_model.md> [<output_model.md> ...]

Each output .md file is expected to be in the format produced by
run_generation.py (## Descriptive part / ## Evaluative part headers).
Pass multiple output files from repeated runs of the SAME model+input to
also get a consistency score.
"""
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

POSITIVE_WORDS = {
    "good", "great", "strong", "excellent", "well", "success", "successful",
    "improve", "improved", "improvement", "positive", "solid", "effective",
    "impressive", "encouraging", "opportunity", "opportunities", "resilient",
    "steady", "recovered", "recovery", "gain", "achievement", "commendable",
}
NEGATIVE_WORDS = {
    "poor", "bad", "weak", "failure", "failed", "decline", "declined",
    "negative", "struggl", "concerning", "worsen", "worsened", "loss",
    "crisis", "disappointing", "unacceptable", "problem", "problematic",
}
JUDGMENT_WORDS = {
    "excellent", "impressive", "poor", "disappointing", "great", "terrible",
    "outstanding", "commendable", "unacceptable", "remarkable",
}
AXIS_KEYWORDS = {
    "staff_wellbeing": ["wellbeing", "well-being", "staff morale", "burnout", "exhaustion"],
    "patient_health": ["patient health"],
    "patient_experience": ["patient experience", "patient satisfaction"],
    "cost_reduction": ["cost reduction", "cost", "financ", "budget", "profit", "revenue"],
}


def load_json_numbers(json_path: str) -> set:
    """Flatten all numeric leaf values in the JSON into a set of rounded numbers."""
    data = json.loads(Path(json_path).read_text())
    numbers = set()

    def walk(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            numbers.add(round(obj))
            numbers.add(round(obj, 1))

    walk(data)
    return numbers


def extract_events_and_days(json_path: str) -> dict:
    """Extract event names and 'significant change' days as referenceable facts."""
    data = json.loads(Path(json_path).read_text())
    facts = {"events": [], "sig_days": []}

    # adjust this path if the real schema nests players_data differently
    def find_key(obj, key):
        if isinstance(obj, dict):
            if key in obj:
                yield obj[key]
            for v in obj.values():
                yield from find_key(v, key)
        elif isinstance(obj, list):
            for v in obj:
                yield from find_key(v, key)

    for eh in find_key(data, "event_history"):
        if isinstance(eh, list):
            for e in eh:
                name = e.get("event_name") or e.get("name") or e.get("title")
                if name:
                    facts["events"].append(str(name))

    EPISODE_THRESHOLD = 8   # minimum cumulative move to even be a candidate episode
    TOP_N_EPISODES = 3      # only the most salient moments count as "must-cite" facts

    candidate_episodes = []  # (magnitude, day, axis)

    for hist_key in ["staff_wellbeing_history", "patient_health_history",
                      "patient_experience_history", "cost_reduction_history"]:
        for series in find_key(data, hist_key):
            if not isinstance(series, list) or len(series) < 2:
                continue
            SKIP_STARTUP_DAYS = 2  # first days often reflect sim calibration, not real events
            i = max(1, SKIP_STARTUP_DAYS)
            while i < len(series):
                direction = 1 if series[i] > series[i - 1] else -1 if series[i] < series[i - 1] else 0
                if direction == 0:
                    i += 1
                    continue
                start = i - 1
                j = i
                while j < len(series) - 1:
                    next_dir = 1 if series[j + 1] > series[j] else -1 if series[j + 1] < series[j] else 0
                    if next_dir != direction:
                        break
                    j += 1
                cumulative = abs(series[j] - series[start])
                if cumulative >= EPISODE_THRESHOLD:
                    candidate_episodes.append((cumulative, j, hist_key))
                i = j + 1

    # keep only the top-N most salient episodes overall (across all axes)
    candidate_episodes.sort(key=lambda x: -x[0])
    facts["sig_days"] = sorted({day for _, day, _ in candidate_episodes[:TOP_N_EPISODES]})
    return facts


def parse_output_md(md_path: str) -> dict:
    text = Path(md_path).read_text()
    parts = {}
    for name, header in [("descriptive", "## Descriptive part"),
                          ("evaluative", "## Evaluative part")]:
        if header in text:
            chunk = text.split(header, 1)[1]
            for other in ["## Analysis (internal)", "## Descriptive part", "## Evaluative part"]:
                if other != header and other in chunk:
                    chunk = chunk.split(other, 1)[0]
            parts[name] = chunk.strip()
    return parts


def sentence_count(text: str) -> int:
    return len([s for s in re.split(r"[.!?]+", text) if s.strip()])


def groundedness_score(json_path: str, full_text: str) -> float:
    facts = extract_events_and_days(json_path)
    total = len(facts["events"]) + len(facts["sig_days"])
    if total == 0:
        return None
    hits = sum(1 for e in facts["events"] if e.lower() in full_text.lower())
    hits += sum(1 for d in facts["sig_days"] if re.search(rf"\bday\s*{d}\b", full_text, re.IGNORECASE))
    return round(hits / total, 2)


def coverage_score(full_text: str) -> float:
    text_low = full_text.lower()
    hit = 0
    for axis, keywords in AXIS_KEYWORDS.items():
        if any(k in text_low for k in keywords):
            hit += 1
    return round(hit / len(AXIS_KEYWORDS), 2)


def conciseness_score(part_text: str, target_range=(3, 5)) -> float:
    n = sentence_count(part_text)
    lo, hi = target_range
    if lo <= n <= hi:
        return 1.0
    over = max(n - hi, lo - n)
    return max(0.0, round(1.0 - over * 0.2, 2))


def tone_score(evaluative_text: str) -> float:
    words = re.findall(r"[a-z]+", evaluative_text.lower())
    pos = sum(1 for w in words if w in POSITIVE_WORDS)
    neg = sum(1 for w in words if w in NEGATIVE_WORDS)
    if pos + neg == 0:
        return None
    return round(pos / (pos + neg), 2)


def factual_accuracy_score(json_path: str, full_text: str) -> float:
    json_numbers = load_json_numbers(json_path)
    claimed = [float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*\.?\d*", full_text)]
    if not claimed:
        return None
    matched = 0
    for c in claimed:
        if any(abs(c - jn) / max(abs(jn), 1) < 0.01 for jn in json_numbers):
            matched += 1
    return round(matched / len(claimed), 2)


def judgment_leakage_count(descriptive_text: str) -> int:
    words = re.findall(r"[a-z]+", descriptive_text.lower())
    return sum(1 for w in words if w in JUDGMENT_WORDS)


def consistency_score(md_paths: list) -> float:
    if len(md_paths) < 2:
        return None
    texts = [Path(p).read_text() for p in md_paths]
    sims = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sims.append(SequenceMatcher(None, texts[i], texts[j]).ratio())
    return round(sum(sims) / len(sims), 2)


def score_file(json_path: str, md_path: str):
    parts = parse_output_md(md_path)
    full_text = "\n".join(parts.values())
    print(f"\n=== {md_path} ===")
    print(f"Groundedness:      {groundedness_score(json_path, full_text)}")
    print(f"Coverage:          {coverage_score(full_text)}")
    if "descriptive" in parts:
        print(f"Conciseness (desc):{conciseness_score(parts['descriptive'])}")
        print(f"Judgment leakage in descriptive part (should be 0): {judgment_leakage_count(parts['descriptive'])}")
    if "evaluative" in parts:
        print(f"Conciseness (eval):{conciseness_score(parts['evaluative'])}")
        print(f"Tone (evaluative): {tone_score(parts['evaluative'])}")
    print(f"Factual accuracy:  {factual_accuracy_score(json_path, full_text)} (approximate - spot check)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python score_outputs.py <log.json> <output.md> [<output.md> ...]")
        sys.exit(1)
    json_path = sys.argv[1]
    md_paths = sys.argv[2:]
    for p in md_paths:
        score_file(json_path, p)
    if len(md_paths) > 1:
        print(f"\nConsistency across {len(md_paths)} runs: {consistency_score(md_paths)}")