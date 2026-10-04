# v2 Master Comparison: Table-Input Pipeline vs v1 Raw-JSON Pipeline

**Model:** Phi-3.5-mini only (the v1 winner in all five scenarios). Llama 3.2 and Qwen 2.5 were not rerun.
**Baseline:** [experiments/v1/COMPARISON.md](../v1/COMPARISON.md)
**Scoring:** current `scripts/score_outputs.py` applied to both versions, so numbers are comparable with each other (they may differ slightly from the figures in the v1 write-ups).

## 1. What changed between v1 and v2

| Area | v1 | v2 |
|---|---|---|
| Model input | Full raw JSON log (64–184 KB) | Compact table from [table_converter.py](../../scripts/table_converter.py): outcome summary, daily metrics, event log, actions used/unused (2.5–5.7 KB, about 97% smaller) |
| Number format | raw values | thousands separators on finance, `\|`-delimited table, human-readable column names |
| TASK 1 prompt | generic trend/shift analysis | same, plus a required review of early/middle/late thirds with at least one finding from the first two |
| TASK 2 prompt | outcome + one specific moment | outcome + start and end financial balance + a moment from each half of the run |
| System prompt | no mention of day coverage | states that all days matter equally and recent days must not dominate |
| Scripts | duplicated prompts in two files | `batch_generate.py` imports prompts/helpers from `run_generation.py` |

Two bugs found and fixed while producing v2: (a) undelimited large numbers (`3351684.6`) were misread, and (b) snake_case column names (`patient_health`) were echoed into the prose, which defeats the scorer's `"patient health"` keyword match.

## 2. Results (Phi-3.5, 5 scenarios)

| Scenario | Groundedness v1 → v2 | Coverage v1 → v2 | Factual acc. v1 → v2 | Conciseness desc v1 → v2 | Tone v1 → v2 |
|---|---|---|---|---|---|
| [Tutorial](tutorial/normal_strategy/COMPARISON.md) | 0.25 → 0.25 | 1.00 → **0.50** | 1.00 → 1.00 | 1.00 → 0.80 | 0.62 → 0.77 |
| [Post-pandemic normal](post-pandemic/normal_strategy/COMPARISON.md) | 0.00 → **0.17** | 1.00 → 1.00 | 0.80 → **1.00** | 0.00 → **0.80** | 1.00 → 0.82 |
| [Post-pandemic cost-min](post-pandemic/cost_minimization_strategy/COMPARISON.md) | 0.33 → **0.50** | 0.50 → **1.00** | 0.50 → **1.00** | 0.80 → **0.00** | 1.00 → 0.83 |
| [Winter flu normal](winter-flu/normal_strategy/COMPARISON.md) | 0.00 → 0.00 | 0.75 → **1.00** | 0.90 → **0.75** | 0.60 → **1.00** | 1.00 → 0.78 |
| [Winter flu cost-min](winter-flu/cost_minimization_strategy/COMPARISON.md) | 0.00 → 0.00 | 1.00 → 1.00 | 0.67 → **0.90** | 1.00 → 1.00 | 0.86 → 0.89 |
| **Mean** | **0.12 → 0.18** | **0.85 → 0.90** | **0.77 → 0.93** | **0.68 → 0.72** | **0.90 → 0.82** |

Evaluative-part conciseness fell on average (0.84 → 0.64); it is 0.60 (6–7 sentences) in four of five v2 runs.
Generation time (v1 → v2, s): 88.6 → 151.3, 82.9 → 101.7, 77.8 → 70.2, 78.5 → 89.1 (tutorial: not recorded in v1). These timings are noisy (other jobs were running on the same 8 GB machine) and should not be read as a speed result.

## 3. Conclusions

**What improved**
- The approximate factual-accuracy score rose in 4 of 5 scenarios (mean 0.77 → 0.93). Start and end balances, patient counts and resignation counts are mostly correct on the 21- and 30-day logs.
- Groundedness rose on both 30-day logs and coverage rose on the post-pandemic cost-min log; the v1 prompt-echo failure and the 14-sentence descriptive part did not recur.
- Prompt size dropped from tens of thousands of tokens to about 2,000, comfortably inside Ollama's default 4,096-token window (measured for the 60-day prompt: 2,050 tokens). The v1 raw logs are far larger than that window, so they were probably truncated silently before the model saw them. This was not verified for the v1 runs and may be part of the v1 recency-bias symptom.

**What did not improve**
- **60-day logs still fail the key requirement.** Neither winter-flu run states a single financial figure, although TASK 2 requires start and end balances and the table contains them. Both runs miss the early decisions that define the scenario (the Day 6 vaccine choice and the Day 13 morale response), and one misdates the vaccine purchase to Day 50.
- Groundedness is still far below the 0.75 production threshold in every scenario (best 0.50).
- Tutorial coverage regressed: the internal analysis listed all four axes but the player-facing text used two.
- Evaluation leaks into the descriptive part ("effective management", "strong operational performance") even though the judgment-word counter reads 0.
- Small token glitches appear in several outputs ("underscs", "achdemonstrating").

**Interpretation.** Changing the input format fixes the input-side problem (no more 180 KB logs) but not the instruction-following problem: a 3.8B model reads the table yet does not reliably carry its mandatory facts into the report, and the effect is strongest on the longest logs. That points to the long-term plan in the project notes: compute the mandatory anchors (final financial result, patient counts, per-axis deltas, the decision list) in Python and place them in the prompt as a context card, so the model narrates facts instead of retrieving them.

## 4. Scorer notes (not changed in this round)
- Groundedness matches event *names* ("Staff Recovery: How Fast Should They Return?"). The model usually quotes the chosen *solution title*, so it scores 0 even when the decision is described correctly. Consider also accepting solution titles.
- The "significant days" part of groundedness uses score swings that may not be the moments a player would call key.
- The consistency score compares raw file text and is meaningless across v1/v2 (different input and prompt), so it is not reported.
- Factual accuracy only checks that a number exists somewhere in the JSON, so a wrong-but-present value (e.g. the 60.6% success rate in post-pandemic normal) scores as accurate.

## 5. Open items for v3
1. Add a Python-computed context card (or, at minimum, mandatory anchor slots in TASK 2) and rerun the two 60-day logs first.
2. Require all four axes by name in both parts to fix the tutorial coverage dropout.
3. Update the scorer (solution-title matching; check key numbers against the JSON by field).
4. Run repeated runs (N ≥ 3) to separate real changes from sampling noise; v2 is a single run per scenario.
5. Consider setting `num_ctx` explicitly in the Ollama call if prompts grow, keeping the 8 GB memory limit in mind.
