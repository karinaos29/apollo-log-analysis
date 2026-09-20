"""
Batch evaluation script per EVALUATION_CRITERIA_v2.md.
Evaluates all models in an experiment subfolder against its ground-truth JSON log,
producing full metric summaries including comparative and threshold analysis.
"""
import json
import re
import sys
from pathlib import Path
from score_outputs import (
    parse_output_md,
    extract_events_and_days,
    load_json_numbers,
    groundedness_score,
    coverage_score,
    conciseness_score,
    tone_score,
    factual_accuracy_score,
    judgment_leakage_count,
    AXIS_KEYWORDS,
    POSITIVE_WORDS,
    NEGATIVE_WORDS,
    JUDGMENT_WORDS,
)

def evaluate_log_experiment(json_path: str, exp_dir: str):
    print(f"\n=======================================================")
    print(f"EVALUATING: {exp_dir}")
    print(f"JSON LOG:   {json_path}")
    print(f"=======================================================")

    facts = extract_events_and_days(json_path)
    print(f"Referenceable facts: Events={facts['events']}, SigDays={facts['sig_days']}")
    total_facts = len(facts["events"]) + len(facts["sig_days"])
    print(f"Total referenceable facts: {total_facts}")

    md_files = sorted(Path(exp_dir).glob("output_*.md"))
    if not md_files:
        print(f"No output_*.md files found in {exp_dir}")
        return

    results = []
    for md_file in md_files:
        model_name = md_file.stem.replace("output_", "").replace("_", ":")
        text = md_file.read_text()
        
        # Extract generation time if present
        time_match = re.search(r"\(Generation time:\s*([\d\.]+)s\)", text)
        gen_time = f"{float(time_match.group(1)):.1f}s" if time_match else "N/A"

        parts = parse_output_md(str(md_file))
        desc = parts.get("descriptive", "")
        eval_part = parts.get("evaluative", "")
        full_text = f"{desc}\n{eval_part}"

        # 1. Groundedness
        g_raw = groundedness_score(json_path, full_text)
        
        # Exact word-bounded day hits
        e_hits = [e for e in facts["events"] if e.lower() in full_text.lower()]
        d_hits = [d for d in facts["sig_days"] if re.search(rf"\bday\s*{d}\b", full_text, re.IGNORECASE)]
        g_exact = round((len(e_hits) + len(d_hits)) / max(total_facts, 1), 2)

        # 2. Coverage
        cov = coverage_score(full_text)
        axes_hit = [axis for axis, kws in AXIS_KEYWORDS.items() if any(k in full_text.lower() for k in kws)]

        # 3. Conciseness
        desc_sents = len([s for s in re.split(r"[.!?]+", desc) if s.strip()])
        eval_sents = len([s for s in re.split(r"[.!?]+", eval_part) if s.strip()])
        c_desc = conciseness_score(desc)
        c_eval = conciseness_score(eval_part)

        # 6. Factual Accuracy
        claimed = [float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*\.?\d*", full_text)]
        jn = load_json_numbers(json_path)
        matched = [c for c in claimed if any(abs(c - x) / max(abs(x), 1) < 0.01 for x in jn)]
        fact_acc = round(len(matched) / max(len(claimed), 1), 2) if claimed else None

        # 7. Tone
        words = re.findall(r"[a-z]+", eval_part.lower())
        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
        t_score = tone_score(eval_part)

        # 8. Two-Part Separation
        leakage = judgment_leakage_count(desc)

        results.append({
            "model": model_name,
            "speed": gen_time,
            "groundedness_raw": g_raw,
            "groundedness_exact": g_exact,
            "event_hits": e_hits,
            "day_hits": d_hits,
            "coverage": cov,
            "axes_hit": axes_hit,
            "desc_sents": desc_sents,
            "desc_concise": c_desc,
            "eval_sents": eval_sents,
            "eval_concise": c_eval,
            "fact_acc": fact_acc,
            "claimed_nums": claimed,
            "matched_nums": matched,
            "tone": t_score,
            "pos_words": pos_count,
            "neg_words": neg_count,
            "separation_leakage": leakage,
        })

    # Print summary table
    print(f"\n{'Model':<15} | {'Speed':<8} | {'Grounded (Raw/Ex)':<18} | {'Coverage':<10} | {'Desc Sents':<10} | {'Eval Sents':<10} | {'Fact Acc':<9} | {'Tone':<6} | {'Leakage':<7}")
    print("-" * 105)
    for r in results:
        g_str = f"{r['groundedness_raw']} / {r['groundedness_exact']}"
        print(f"{r['model']:<15} | {r['speed']:<8} | {g_str:<18} | {r['coverage']:<10.2f} | {r['desc_sents']} ({r['desc_concise']})    | {r['eval_sents']} ({r['eval_concise']})    | {str(r['fact_acc']):<9} | {str(r['tone']):<6} | {r['separation_leakage']:<7}")

    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_score.py <log.json> <experiment_dir>")
        sys.exit(1)
    evaluate_log_experiment(sys.argv[1], sys.argv[2])

