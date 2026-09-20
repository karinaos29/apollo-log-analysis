# Model Comparison: Post-Pandemic Scenario (Cost-Minimization Strategy)

**Log File**: `data/post-pandemic/cost_minimization_strategy_catherine-post_pandemic_financial_recovery-2026-09-20T18-25-52.json`  
**Player**: Catherine  
**Evaluation Standard**: [EVALUATION_CRITERIA_v2.md](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/docs/EVALUATION_CRITERIA_v2.md)  
**Scoring Script**: [batch_score.py](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/scripts/batch_score.py) / [score_outputs.py](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/scripts/score_outputs.py)

---

## 1. Executive Scorecard: Relative Winner vs. Absolute Viability

| # | Criterion | Evaluation Type | Target Scale | Llama 3.2 (3B) | Phi-3.5-mini (3.8B) | Qwen 2.5 (3B) | Relative Winner | Absolute Production Threshold Status |
|---|---|---|---|---|---|---|---|---|
| 1 | **Groundedness** | Automatic (Script) | 0.0 – 1.0 | 0.17 *(0.17 exact)* | **0.33** *(0.33 exact)* | 0.00 *(0.00 exact)* | **Phi-3.5** | ❌ **FAIL (All models)** — 0.33 is critically inadequate |
| 2 | **Coverage** | Automatic (Script) | 0.0 – 1.0 (4 axes) | **1.00** (4/4 axes) | 0.50 (2/4 axes) | 0.75 (3/4 axes) | **Llama 3.2** | ⚠️ Only Llama meets 1.00 (but hallucinates content) |
| 3 | **Conciseness (Desc)**| Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (4 sents) | 0.80 (6 sents) | 0.80 (6 sents) | **Llama 3.2** | ⚠️ Phi & Qwen slightly exceed limit |
| 3 | **Conciseness (Eval)**| Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (4 sents) | 0.60 (7 sents) | 0.80 (6 sents) | **Llama 3.2** | ⚠️ Phi & Qwen slightly exceed limit |
| 4 | **Speed** | Automatic (Logged) | Wall-clock seconds | 56.2s | 82.9s | **48.2s** | **Qwen 2.5** | ✅ All within operational bounds (<90s) |
| 5 | **Consistency** | Automatic | 0.0 – 1.0 (repeat runs)| *N/A (Single run)* | *N/A (Single run)* | *N/A (Single run)* | *N/A* | Requires repeat runs |
| 6 | **Factual Accuracy** | Semi-auto + Spot Check| 0.0 – 1.0 | 1.00 *(Catastrophic Inversion)* | 0.50 | **0.75** | **Qwen 2.5** | ❌ Llama asserts opposite strategy; Phi/Qwen partial |
| 7 | **Tone (Evaluative)**| Semi-auto (Script) | 0.0 – 1.0 | **1.00** | **1.00** | **1.00** | **Tie (1.00)** | ✅ Encouraging tone across all |
| 8 | **Two-Part Separation**| Manual Checklist | Issue count (0 is best) | **0 issues** | **0 issues** | **0 issues** | **Tie (0)** | ✅ Clean separation maintained |
| 9 | **Fluency** | Manual Checklist | Issue count (0 is best) | **0 issues** | **0 issues** | **0 issues** | **Tie (0)** | Fluent English across all models |

---

## 2. Ground Truth Reference (Session Data)

- **Scenario**: Post-Pandemic Financial Recovery (30 Days completed)
- **Player**: Catherine (Cost-Minimization Strategy)
- **Clinical & Operational Outcome**:
  - Patients Treated: **476 total** (**348** successful, **128** unsuccessful, **73.1%** success rate — *54 fewer patients than Mark's normal strategy*)
  - Staff Resignations: **0** (Staff count: 14 maintained)
  - Financial Result: Initial funds **$1,631,198.38** → Final funds **$2,129,999.53** (**+$498,801.15 massive surplus**)
- **AIM Performance Trajectory**:
  - **Staff Wellbeing**: 77.50 → 62.63 (*-14.87 pts — heavily sacrificed*)
  - **Patient Health**: 75.00 → 57.00 (*-18.00 pts — heavily sacrificed*)
  - **Patient Experience**: 75.00 → 60.95 (*-14.05 pts — heavily sacrificed*)
  - **Cost Reduction**: 39.02 → 80.30 (*+41.28 pts — primary focus*)
  - Overall Score: **65.22** (lower than Mark's 68.57 due to clinical score erosion)
- **Key Events & Decisions**:
  - Day 13: *Talent War: Competitors Offering Sign-On Bonuses* → Chose **Do Nothing (No Retention Bonuses)**
  - Day 21: *Operational Efficiency Audit Results* → Chose **Minor Changes**
  - Day 27: *Strategic Direction: Expand or Consolidate?* → Chose **Maintain Current Scope**

---

## 3. Comparative Analysis & Production Viability

### 3.1 The Catastrophic Strategy Inversion in Llama 3.2
Llama 3.2 scored 1.00 on automated factual accuracy purely because numbers like `20`, `25`, and `850000` existed somewhere in metadata. However, qualitative spot-checking reveals a **fatal decision reversal**:
- Llama reported: *"notable increase on day 20, coinciding with the implementation of competitive retention bonuses in response to the Talent War event... highlighting the value of investing in staff retention."*
- **The Reality**: Catherine adopted a strict **cost-minimization strategy** and explicitly chose `do_nothing_retention` (she refused to pay bonuses, saving money at the cost of staff morale).
- **Usability Impact**: Praising a player for an action they deliberately chose *not* to take invalidates the pedagogical utility of the simulation. Llama cannot be deployed in this role.

### 3.2 Groundedness Threshold Failure (0.33 Maximum)
Phi-3.5 captured Day 20 and an event mention, yielding **0.33**. However, it omitted:
- Catherine's massive financial milestone (**$2.13M ending balance**, **+$498k surplus**).
- The total patient throughput (476 treated).
- The severe decline in clinical metrics (Patient Health falling to 57.00).
- **Threshold Assessment**: Missing two-thirds of the key simulation facts means the report fails to provide the player with meaningful, actionable feedback on their aggressive cost-cutting.

### 3.3 Qwen 2.5 (3B): Stable but Shallow
Qwen accurately captured final Cost Reduction at 80.30 and Patient Health at 57.00, avoiding Llama's hallucination. However, it achieved **0.00 Groundedness** on specific events and failed to explicitly mention Staff Wellbeing in the summary text.

---

## 4. Final Verdict & Log Recommendation

- **Relative Winner**: **Phi-3.5-mini-instruct** (highest groundedness at 0.33 and accurately avoids fabricating false bonuses).
- **Production Usability Status**: **UNUSABLE WITHOUT PRE-EXTRACTED ANCHORS**. Llama completely inverts the player's core strategy, while Phi and Qwen capture too few facts to reflect the aggressive financial vs. clinical trade-offs of the session.

