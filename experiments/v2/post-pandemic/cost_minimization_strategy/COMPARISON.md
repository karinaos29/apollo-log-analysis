# v2 vs v1: Post-Pandemic Financial Recovery (Cost-Minimization, Catherine)

**Log:** `data/post-pandemic/cost_minimization_strategy_catherine-post_pandemic_financial_recovery-2026-09-20T18-25-52.json` (30 days, 7 events)
**Model:** Phi-3.5-mini only | **Outputs:** [v1](../../../v1/post-pandemic/cost_minimization_strategy/output_phi3.5.md) · [v2](output_phi3.5.md)
**Master summary:** [experiments/v2/COMPARISON.md](../../COMPARISON.md)

## What changed vs v1
- Input: raw JSON (94 KB) → compact table (3.4 KB).
- Prompt: day-thirds review in TASK 1; TASK 2 requires start/end balance and one moment from each half.

## Scores (Phi-3.5)

| Criterion | v1 | v2 | Change |
|---|---|---|---|
| Groundedness | 0.33 | 0.50 | better |
| Coverage (4 axes) | 0.50 | 1.00 | better |
| Conciseness (desc / eval) | 0.80 / 0.60 | 0.00 / 0.60 | desc worse (over-long) |
| Tone (eval) | 1.00 | 0.83 | lower |
| Factual accuracy (approx.) | 0.50 | 1.00 | better |
| Generation time | 82.9 s | 101.7 s | slower (timing noisy) |

## Ground truth
Day 13 Talent War → Do Nothing (no retention bonuses); Day 21 Audit → Minor Changes; Day 27 Strategic Direction → Maintain Scope. Finance $1,631,198 → ≈$2.13M. 476 patients treated (73.1% success), 0 resignations. Staff wellbeing −14.9, patient health −18.0, patient experience −14.1, cost reduction +41.3.

## Observations
- **Better:** both balances, the patient count and the resignation count are correct; the Day 21 and Day 27 decisions are both cited correctly (v1 only had one event mention); all four axes are covered; no inverted decisions.
- **Missed:** the Day 13 refusal of retention bonuses, which is the defining choice of this cost-minimization run.
- **Chronology error:** the descriptive part ties a Day 8 dip to the Day 21 audit, and credits a cost-reduction increase "by Day 20" to that later audit.
- The descriptive part is too long (conciseness 0.00) and frames the run as "strong operational performance", which is evaluation inside the descriptive section. It also does not mention the large drops in patient health (−18.0) and staff wellbeing (−14.9) that this strategy produced.
