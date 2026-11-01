"""
Run the v4 pipeline (run_hybrid_generation.py) on every session log, optionally
several times with different seeds.

Usage (paths are resolved from the repository root, so any working directory works):
    python scripts/batch_hybrid.py                         # canonical run, seed 42 -> experiments/v4/
    python scripts/batch_hybrid.py --seeds 1 2 3 --out experiments/v4/repeats
    python scripts/batch_hybrid.py --only winter-flu       # subset by scenario folder name

The descriptive part is deterministic, so only the evaluative part changes
between seeds.
"""
import argparse
import sys
import time
from pathlib import Path

from run_hybrid_generation import run

ROOT = Path(__file__).resolve().parent.parent  # paths below are relative to the repository root

LOGS = [
    ("tutorial/normal_strategy", "data/tutorial/apollo_player-Karina-2026-08-30T20-38-57.json"),
    ("post-pandemic/normal_strategy", "data/post-pandemic/normal_strategy-mark-post_pandemic_financial_recovery-2026-09-20T18-06-09.json"),
    ("post-pandemic/cost_minimization_strategy", "data/post-pandemic/cost_minimization_strategy_catherine-post_pandemic_financial_recovery-2026-09-20T18-25-52.json"),
    ("winter-flu/normal_strategy", "data/winter-flu/normal_strategy-winter_flu_crisis-2026-09-20T22-07-06.json"),
    ("winter-flu/cost_minimization_strategy", "data/winter-flu/cost_minimization_strategy-winter_flu_crisis-2026-09-20T22-07-16.json"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="phi3.5")
    ap.add_argument("--seeds", type=int, nargs="+", default=[42])
    ap.add_argument("--out", default="experiments/v4", help="root folder; each log gets <out>/<scenario>/<strategy>/")
    ap.add_argument("--only", default=None, help="run only logs whose folder contains this text")
    a = ap.parse_args()

    failures = []
    for folder, log in LOGS:
        if a.only and a.only not in folder:
            continue
        for seed in a.seeds:
            t0 = time.time()
            out_root = Path(a.out) if Path(a.out).is_absolute() else ROOT / a.out
            try:
                run(str(ROOT / log), a.model, str(out_root / folder), seed=seed)
                print(f"[ok]   {folder} seed={seed} ({time.time() - t0:.0f}s)\n")
            except Exception as e:  # keep going: one failed log should not stop the batch
                failures.append((folder, seed, repr(e)))
                print(f"[FAIL] {folder} seed={seed}: {e!r}\n")
    if failures:
        print(f"{len(failures)} run(s) failed:")
        for f in failures:
            print("  ", *f)
        sys.exit(1)


if __name__ == "__main__":
    main()
