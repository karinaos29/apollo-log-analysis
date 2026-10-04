# v2 vs v1: Winter Flu Crisis (Cost-Minimization, Patrick): 60-day test

**Log:** `data/winter-flu/cost_minimization_strategy-winter_flu_crisis-2026-09-20T22-07-16.json` (60 days, 14 events)
**Model:** Phi-3.5-mini only | **Outputs:** [v1](../../../v1/winter-flu/cost_minimization_strategy/output_phi3.5.md) · [v2](output_phi3.5.md)
**Master summary:** [experiments/v2/COMPARISON.md](../../COMPARISON.md)

## What changed vs v1
- Input: raw JSON (180 KB) → compact table (5.7 KB).
- Prompt: day-thirds review in TASK 1; TASK 2 requires start/end balance and one moment from each half.

## Scores (Phi-3.5)

| Criterion | v1 | v2 | Change |
|---|---|---|---|
| Groundedness | 0.00 | 0.00 | = |
| Coverage (4 axes) | 1.00 | 1.00 | = |
| Conciseness (desc / eval) | 1.00 / 1.00 | 1.00 / 0.60 | eval worse |
| Tone (eval) | 0.86 | 0.89 | slightly better |
| Factual accuracy (approx.) | 0.67 | 0.90 | better |
| Generation time | 78.5 s | 89.1 s | slower (timing noisy) |

## Ground truth
Day 6 decline vaccines; Day 13 pizza parties + recognition only (no bonuses); Day 21 accelerated return ($1,000); Day 31 skip improvements; Day 43 and Day 53 do nothing. Finance $3,335,792 → ≈$5.47M (about +$2.1M). 1,177 patients treated, 0 resignations. Patient health fell to 53.9.

## Observations
- **Correct:** the Day 21 accelerated return decision and its $1,000 cost; the Day 57 reference is the only late-run detail.
- **The central failure persists:** the report never mentions the Day 6 vaccine refusal or the Day 13 morale decision, which are the cost-minimization story and the likely cause of the patient-health drop.
- **Financial anchor ignored:** "the final financial balance not explicitly stated" and "ambiguous final financial result", although the table states $5,471,230 and the start balance. The start balance is described only as "stable", with no number.
- The "Day 57 peak in patient health" claim was not checked against the log.
- The evaluative part is mostly generic ("commendable engagement", "valuable insights").
