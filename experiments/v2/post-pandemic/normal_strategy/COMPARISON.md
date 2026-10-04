# v2 vs v1: Post-Pandemic Financial Recovery (Normal Strategy, Mark)

**Log:** `data/post-pandemic/normal_strategy-mark-post_pandemic_financial_recovery-2026-09-20T18-06-09.json` (30 days, 7 events)
**Model:** Phi-3.5-mini only | **Outputs:** [v1](../../../v1/post-pandemic/normal_strategy/output_phi3.5.md) · [v2](output_phi3.5.md)
**Master summary:** [experiments/v2/COMPARISON.md](../../COMPARISON.md)

## What changed vs v1
- Input: raw JSON (99 KB) → compact table (3.5 KB).
- Prompt: day-thirds review in TASK 1; TASK 2 requires start/end balance and one moment from each half.
- v1 had echoed the TASK 3 instruction inside the descriptive part (14 sentences). That did not recur in v2.

## Scores (Phi-3.5)

| Criterion | v1 | v2 | Change |
|---|---|---|---|
| Groundedness | 0.00 | 0.17 | better |
| Coverage (4 axes) | 1.00 | 1.00 | = |
| Conciseness (desc / eval) | 0.00 / 1.00 | 0.80 / 0.60 | desc better, eval worse |
| Tone (eval) | 1.00 | 0.82 | lower |
| Factual accuracy (approx.) | 0.80 | 1.00 | better |
| Generation time | 88.6 s | 151.3 s | slower (timing noisy, see master doc) |

## Ground truth
Day 13 Talent War → Retention Bonuses; Day 21 Efficiency Audit → Do Nothing; Day 27 Expand/Consolidate → Consolidation ($62,500). Finance $1,679,502 → $1,785,655 (final_finance field). 531 patients treated, 400 successful (75.5%). 0 resignations.

## Observations
- **Better:** start/end balances and the patient count are correct; the Day 27 consolidation and the Day 13 retention bonuses are both cited (v1 only had Day 27); the prompt echo is gone.
- **Wrong:** "success rate stood at 60.6%" is incorrect (actual 75.5%; 60.6 is the final Patient Health score, so two columns were confused). "Sharp increase in patient experience on Day 4 following the Talent War event" misdates the event (it was Day 13).
- **Missed:** the Day 21 audit decision.
- Token glitch: "underscs".
- Note: the log's `final_finance` ($1,785,655) differs from the Day-30 `finance_remaining` ($1,776,739). The model used the former; the v1 write-up used the latter.
