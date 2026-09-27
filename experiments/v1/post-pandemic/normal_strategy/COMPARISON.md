# Model Comparison: Post-Pandemic Scenario (Normal Strategy)

**Log File**: `data/post-pandemic/normal_strategy-mark-post_pandemic_financial_recovery-2026-09-20T18-06-09.json`  
**Player**: Mark  
**Evaluation Standard**: [EVALUATION_CRITERIA_v2.md](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/docs/EVALUATION_CRITERIA_v2.md)  
**Scoring Script**: [batch_score.py](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/scripts/batch_score.py) / [score_outputs.py](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/scripts/score_outputs.py)

---

## 1. Executive Scorecard: Relative Winner vs. Absolute Viability

| # | Criterion | Evaluation Type | Target Scale | Llama 3.2 (3B) | Phi-3.5-mini (3.8B) | Qwen 2.5 (3B) | Relative Winner | Absolute Production Threshold Status |
|---|---|---|---|---|---|---|---|---|
| 1 | **Groundedness** | Automatic (Script) | 0.0 – 1.0 | 0.00 *(0.00 exact)* | 0.00 *(0.00 exact)* | 0.00 *(0.00 exact)* | **Tie (0.00)** | ❌ **FAIL (All models)** — 0.00 is completely unusable |
| 2 | **Coverage** | Automatic (Script) | 0.0 – 1.0 (4 axes) | 0.75 (3/4 axes) | **1.00** (4/4 axes) | 0.50 (2/4 axes) | **Phi-3.5** | ⚠️ Only Phi-3.5 meets the 1.00 requirement |
| 3 | **Conciseness (Desc)**| Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (3 sents) | 0.00 (14 sents\*) | **1.00** (4 sents) | **Llama / Qwen** | ⚠️ Phi severely bloated by prompt echoing |
| 3 | **Conciseness (Eval)**| Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (4 sents) | **1.00** (5 sents) | **1.00** (5 sents) | **Tie (1.00)** | ✅ All models meet target |
| 4 | **Speed** | Automatic (Logged) | Wall-clock seconds | **33.6s** | 88.6s | 46.0s | **Llama 3.2** | ✅ All within acceptable range (<90s) |
| 5 | **Consistency** | Automatic | 0.0 – 1.0 (repeat runs)| *N/A (Single run)* | *N/A (Single run)* | *N/A (Single run)* | *N/A* | Requires repeat runs |
| 6 | **Factual Accuracy** | Semi-auto + Spot Check| 0.0 – 1.0 | 0.50 *(Severe Confabulation)* | **0.80** *(True Dollar Figure)* | 0.82 *(Day Misattribution)* | **Phi-3.5** | ❌ Llama disqualified; Qwen misattributes |
| 7 | **Tone (Evaluative)**| Semi-auto (Script) | 0.0 – 1.0 | 0.80 | **1.00** | **1.00** | **Phi / Qwen** | ✅ Highly encouraging across candidates |
| 8 | **Two-Part Separation**| Manual Checklist | Issue count (0 is best) | **0 issues** | 2 issues (Prompt leak) | **0 issues** | **Llama / Qwen** | ⚠️ Phi echoed Task 3 prompt inside Task 2 |
| 9 | **Fluency** | Manual Checklist | Issue count (0 is best) | **0 issues** | 1 issue (Structure leak) | **0 issues** | **Llama / Qwen** | Llama & Qwen write clean English |

*\*Note: Phi-3.5 echoed the Task 3 instruction inside the descriptive section, causing sentence count to expand to 14.*

---

## 2. Ground Truth Reference (Session Data)

- **Scenario**: Post-Pandemic Financial Recovery (30 Days completed)
- **Player**: Mark (Normal Strategy)
- **Clinical & Operational Outcome**:
  - Patients Treated: **530 total** (**400** successful, **130** unsuccessful, **75.5%** success rate)
  - Staff Resignations: **0** (Staff count: 14 maintained)
  - Financial Result: Initial funds **$1,679,502.26** → Final funds **$1,776,739.04** (**+$97,236.78 profit**)
- **AIM Performance Trajectory**:
  - **Staff Wellbeing**: 77.50 → 68.96 (*-8.54 pts*)
  - **Patient Health**: 75.00 → 60.56 (*-14.44 pts*)
  - **Patient Experience**: 75.00 → 69.28 (*-5.72 pts*)
  - **Cost Reduction**: 38.62 → 75.49 (*+36.87 pts*)
  - Overall Score: **68.57**
- **Key Events & Decisions**:
  - Day 13: *Talent War: Competitors Offering Sign-On Bonuses* → Chose **Retention Bonuses**
  - Day 21: *Operational Efficiency Audit Results* → Chose **Do Nothing**
  - Day 27: *Strategic Direction: Expand or Consolidate?* → Chose **Consolidation** (Locked Funds: **$62,500**)

---

## 3. Comparative Analysis & Production Viability

### 3.1 Groundedness Crisis: All Models Score 0.00
In this run, **every single model scored 0.00 on Groundedness**:
- None of the models cited the formal event titles (*"Talent War"*, *"Operational Efficiency Audit"*, *"Strategic Direction"*).
- None cited the significant change days (Days 4, 6, 8).
- **Absolute Usability Verdict**: **UNUSABLE AS-IS**. If an AI summary fails to reference any of the specific crisis events or operational inflection points, the player has no evidence that the report is personalized to their 30-day session.

### 3.2 Factual Accuracy & Hallucination Breakdown
- **Llama 3.2 (3B)**: **Severe Confabulation**.
  - Invented a financial loss of `-$50,000` (Mark actually made **+$97,236** profit, ending with **$1.78M**).
  - Invented 1,200 patients treated with an 85% success rate (actual: 530 treated, 75.5%).
  - Invented 2 staff resignations (actual: 0).
  - Invented a fictitious event called *"recovery expansion decision"* on Day 25.
  - *Verdict*: **Disqualified**. The model generates compelling narrative fiction.
- **Phi-3.5-mini (3.8B)**: **Highest Real Factual Anchor**.
  - Accurately identified the Day 27 decision to choose **consolidation**.
  - Accurately cited the exact locked funds: **$62,500** (a real number from the JSON).
  - Correctly tracked AIM dynamics (Cost Reduction rose to 75.49, Patient Health dropped to 60.56).
  - *Failure*: Echoed the prompt text for Task 3 inside Task 2.
- **Qwen 2.5 (3B)**: **Cautious but Distorted**.
  - Misattributed the consolidation decision to Day 21 instead of Day 27.
  - Covered only 2 of the 4 AIM axes (Patient Health and Cost Reduction).

---

## 4. Final Verdict & Log Recommendation

- **Relative Winner**: **Phi-3.5-mini-instruct** (for retaining real facts like Day 27 consolidation and $62,500 locked funds, and 100% axis coverage).
- **Production Usability Status**: **REJECT ALL WITHOUT SCAFFOLDING**. Phi-3.5 requires prompt guardrails against echoing system prompts, and all models require a deterministic pre-extraction card to raise Groundedness from 0.00 to acceptable production standards ($\ge 0.75$).

