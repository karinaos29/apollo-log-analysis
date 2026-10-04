# v2 vs v1: Winter Flu Crisis (Normal Strategy, Jane): 60-day test

**Log:** `data/winter-flu/normal_strategy-winter_flu_crisis-2026-09-20T22-07-06.json` (60 days, 14 events: 6 decisions + 8 weekly summaries)
**Model:** Phi-3.5-mini only | **Outputs:** [v1](../../../v1/winter-flu/normal_strategy/output_phi3.5.md) · [v2](output_phi3.5.md)
**Master summary:** [experiments/v2/COMPARISON.md](../../COMPARISON.md)

## What changed vs v1
- Input: raw JSON (184 KB) → compact table (5.7 KB, about 2,050 tokens).
- Prompt: day-thirds review in TASK 1; TASK 2 requires start/end balance and one moment from each half.

## Scores (Phi-3.5)

| Criterion | v1 | v2 | Change |
|---|---|---|---|
| Groundedness | 0.00 | 0.00 | = |
| Coverage (4 axes) | 0.75 | 1.00 | better |
| Conciseness (desc / eval) | 0.60 / 0.60 | 1.00 / 0.60 | desc better |
| Tone (eval) | 1.00 | 0.78 | lower |
| Factual accuracy (approx.) | 0.90 | 0.75 | worse |
| Generation time | 77.8 s | 70.2 s | faster |

## Ground truth
Day 6 buy partial vaccines; Day 13 overtime bonuses ($40,000); Day 21 conservative return; Day 31 basic improvements; Day 43 and Day 53 do nothing. Finance $3,351,685 → $5,263,446 (about +$1.9M). 1,198 patients treated (73.9% success), 0 resignations.

## Observations
- **The critical requirement failed:** no number appears anywhere in the report. TASK 2 asked for start and end balances; the output says "an initial financial balance" and "a lower than projected ending financial balance". The table contained both figures, and the claim of a lower ending balance contradicts a gain of about $1.9M.
- **Wrong date:** the vaccine purchase (Day 6) is placed on Day 50 in both parts ("sharp decrease on Day 50 following the vaccine decision").
- **Questionable claim:** a "significant improvement in staff wellbeing" on Day 21. Staff wellbeing fell steadily across the run (77.5 → 59.1).
- **Better than v1:** the model cites days from the early, middle and late parts of the run (21, 50) and a real decision label, so the raw "forgets the first 40 days" pattern is reduced, but Days 6, 13 and 31 are still missing.
- Why groundedness stays 0.00: the scorer matches event names (e.g. "Staff Recovery: How Fast Should They Return?"), while the model quotes the chosen solution's title ("Conservative Return: Full Recovery Required"). See the scorer note in the master doc.
- Token glitch: "underscs".
