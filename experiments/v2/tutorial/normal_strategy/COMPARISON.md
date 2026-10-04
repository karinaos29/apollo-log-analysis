# v2 vs v1: Tutorial Scenario (Normal Strategy)

**Log:** `data/tutorial/apollo_player-Karina-2026-08-30T20-38-57.json` (21 days, 1 event)
**Model:** Phi-3.5-mini only (the v1 winner) | **Outputs:** [v1](../../../v1/tutorial/normal_strategy/output_phi3.5.md) · [v2](output_phi3.5.md)
**Master summary:** [experiments/v2/COMPARISON.md](../../COMPARISON.md)

## What changed vs v1
- Input: raw JSON (64 KB) replaced by a compact table (2.5 KB) built by [table_converter.py](../../../../scripts/table_converter.py).
- Prompt: day-thirds review instruction in TASK 1; TASK 2 requires start/end financial balance plus a moment from each half of the run.
- Scores below are recomputed with the current `score_outputs.py` for both versions (v1 figures can differ slightly from the v1 write-up).

## Scores (Phi-3.5)

| Criterion | v1 | v2 | Change |
|---|---|---|---|
| Groundedness | 0.25 | 0.25 | = |
| Coverage (4 axes) | 1.00 | 0.50 | worse |
| Conciseness (desc / eval) | 1.00 / 1.00 | 0.80 / 0.80 | worse (6 sentences each) |
| Tone (eval) | 0.62 | 0.77 | better |
| Factual accuracy (approx.) | 1.00 | 1.00 | = |
| Generation time | n/a (not recorded in v1) | 123.2 s | n/a |

## Ground truth
Day 15 "Critical Equipment Failure" → Emergency Maintenance ($25,000 locked). Finance $1,102,123 → $1,612,280. 377 patients treated (302 successful), 0 resignations. Staff wellbeing −11.0, patient health −14.9, patient experience −8.7, cost reduction +42.4.

## Observations
- **Better:** start and end balances are stated and correct; the Day 15 event and the emergency maintenance response are named; zero resignations is correct.
- **Worse:** the player-facing text names only 2 of 4 axes (patient health and staff wellbeing are missing), so the three declining scores are never mentioned and the run is framed as "positive overall". The model's internal analysis did list all four axes, so the information was available but not carried into the report.
- The descriptive part contains evaluation ("effective management and budgeting skills"), which breaks the two-part separation even though the judgment-word counter reads 0.
- One token glitch: "achdemonstrating".
- Not mentioned: the $25,000 cost of the maintenance program.
