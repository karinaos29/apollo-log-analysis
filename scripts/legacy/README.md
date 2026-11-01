# Legacy pipelines

Kept so the v2 and v3 experiments can be reproduced. They are not maintained;
use `scripts/run_hybrid_generation.py` (v4) for new work.

| Script | Pipeline | Experiments |
|---|---|---|
| `table_converter.py`, `run_generation.py` | v2: JSON log -> compact table -> 3 model calls (analysis, descriptive, evaluative) | `experiments/v2/` |
| `batch_generate.py` | v1/v2 batch over the original log list with three models | `experiments/v1/`, `experiments/v2/` (its output paths predate the `v1/`/`v2/` folders) |
| `run_card_generation.py` | v3: context card -> 2 model calls, validation and one rewrite | `experiments/v3/` |

Run from the repository root, e.g.
`./venv/bin/python3 scripts/legacy/run_card_generation.py data/tutorial/<log>.json phi3.5 /tmp/out`
