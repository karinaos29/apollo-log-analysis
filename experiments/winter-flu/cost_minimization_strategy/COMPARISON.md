# Model Comparison: Winter Flu Crisis Scenario (Cost-Minimization Strategy)

**Log File**: `data/winter-flu/cost_minimization_strategy-winter_flu_crisis-2026-09-20T22-07-16.json`  
**Player**: Patrick (Cost-Minimization Strategy)  
**Evaluation Standard**: [EVALUATION_CRITERIA_v2.md](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/docs/EVALUATION_CRITERIA_v2.md)  
**Scoring Script**: [batch_score.py](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/scripts/batch_score.py) / [score_outputs.py](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/scripts/score_outputs.py)

---

## 1. Executive Scorecard: Relative Winner vs. Absolute Viability

| # | Criterion | Evaluation Type | Target Scale | Llama 3.2 (3B) | Phi-3.5-mini (3.8B) | Qwen 2.5 (3B) | Relative Winner | Absolute Production Threshold Status |
|---|---|---|---|---|---|---|---|---|
| 1 | **Groundedness** | Automatic (Script) | 0.0 – 1.0 | 0.00 *(0.00 exact)* | 0.00 *(0.00 exact)* | 0.00 *(0.00 exact)* | **Tie (0.00)** | ❌ **FAIL (All models)** — 0.00 is completely unusable |
| 2 | **Coverage** | Automatic (Script) | 0.0 – 1.0 (4 axes) | **1.00** (4/4 axes) | **1.00** (4/4 axes) | 0.75 (3/4 axes) | **Llama / Phi** | ⚠️ Only Llama & Phi hit 1.00 |
| 3 | **Conciseness (Desc)**| Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (5 sents) | **1.00** (5 sents) | 0.80 (2 sents) | **Llama / Phi** | ⚠️ Qwen too brief (2 sentences) |
| 3 | **Conciseness (Eval)**| Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (4 sents) | **1.00** (5 sents) | 0.80 (2 sents) | **Llama / Phi** | ⚠️ Qwen too brief (2 sentences) |
| 4 | **Speed** | Automatic (Logged) | Wall-clock seconds | 44.2s | 78.5s | **38.6s** | **Qwen 2.5** | ✅ All under 80s |
| 5 | **Consistency** | Automatic | 0.0 – 1.0 (repeat runs)| *N/A (Single run)* | *N/A (Single run)* | *N/A (Single run)* | *N/A* | Requires repeat runs |
| 6 | **Factual Accuracy** | Semi-auto + Spot Check| 0.0 – 1.0 | 1.00 *(Factual Inversion)* | **0.67** *(True Inaction Hit)* | 1.00 *(Vague / Thin)* | **Phi-3.5** | ❌ Llama asserts opposite decision; Qwen thin |
| 7 | **Tone (Evaluative)**| Semi-auto (Script) | 0.0 – 1.0 | **1.00** | 0.86 | 0.67 | **Llama / Phi** | ✅ Encouraging tone maintained |
| 8 | **Two-Part Separation**| Manual Checklist | Issue count (0 is best) | **0 issues** | **0 issues** | **0 issues** | **Tie (0)** | ✅ Clean separation across all |
| 9 | **Fluency** | Manual Checklist | Issue count (0 is best) | **0 issues** | **0 issues** | **0 issues** | **Tie (0)** | Fluent, well-structured English |

---

## 2. Ground Truth Reference (Session Data)

- **Scenario**: Winter Flu Crisis (60 Days completed)
- **Player**: Patrick (Cost-Minimization Strategy)
- **Clinical & Operational Outcome**:
  - Patients Treated: **1,177 total** (**869** successful, **308** unsuccessful, **73.8%** success rate — *21 fewer patients than Jane*)
  - Staff Resignations: **0** (Staff count: 14 maintained)
  - Financial Result: Initial funds **$3,335,791.56** → Final funds **$5,471,282.24** (**+$2,135,490.68 profit — $223,676 higher surplus than Jane**)
- **AIM Performance Trajectory**:
  - **Staff Wellbeing**: 77.50 → 57.66 (*-19.84 pts — lower than Jane's 59.14*)
  - **Patient Health**: 75.00 → 53.88 (*-21.12 pts — clinical collapse due to refusing vaccines*)
  - **Patient Experience**: 75.00 → 66.63 (*-8.37 pts*)
  - **Cost Reduction**: 39.02 → 82.17 (*+43.15 pts — highest priority*)
  - Overall Performance Score: **65.09**
- **Key Crisis Events & Decisions (Aggressive Cost-Cutting)**:
  - Day 6: *Emergency Flu Vaccine Shipment Available* → Chose **Decline Vaccines** (Saved cash; let outbreak spread)
  - Day 13: *Staff Exhaustion Reaches Critical Levels* → Chose **Minimal Response** (Refused overtime bonuses)
  - Day 21: *Staff Recovery: How Fast Should They Return?* → Chose **Accelerated Return** (Forced staff back early)
  - Day 31: *Midpoint Review: Operational Lessons Learned* → Chose **Skip Improvements** (Refused to invest in clinical upgrades)
  - Day 43: *Build a Crisis Reserve Fund?* → Chose **Do Nothing**
  - Day 53: *Final Strategic Direction* → Chose **Do Nothing**

---

## 3. Comparative Analysis & Production Viability

### 3.1 Failure to Capture the Core Strategy Trade-Off
The defining pedagogical feature of Patrick's run is that his aggressive cost-cutting generated an extra **$224,000 in cash reserves** while causing **Patient Health to crater to 53.88** (the worst clinical performance across all test runs).
- **None of the models identified this trade-off**: All three models completely missed Patrick's decisions on Day 6 (declining vaccines) and Day 13 (refusing overtime bonuses).
- **Absolute Usability Verdict**: **UNUSABLE FOR LEARNING FEEDBACK**. If an assessment report fails to identify why patient health collapsed (refusing vaccines to save money), the simulation cannot teach players the consequences of unconstrained cost-minimization in healthcare.

### 3.2 Factual Accuracy and Inversion
- **Llama 3.2**: **Hallucinated Opposite Action**.
  - Asserted: *"on Day 43, the hospital invested in flu preparedness, which led to an increase in patient health scores."*
  - **Reality**: Patrick chose `do_nothing` on Day 43 and never invested in flu preparedness.
  - Fabricated $100,000 in profit (actual: $2.14 million).
- **Phi-3.5**: **Recognized Strategic Inaction**.
  - Uniquely and correctly recognized that on Day 43, Patrick chose the `"do_nothing"` option for the crisis reserve fund, accurately describing it as *"strategic inaction"*.
  - Weakness: Confused 8 simulation weeks with "eight days".
- **Qwen 2.5**: **Overly Terse & Factually Wrong**.
  - Produced only 2 sentences per section, scoring 0.80 on conciseness.
  - Claimed a Crisis Reserve Fund was established on Day 5 (neither the day nor the action was true).

---

## 4. Final Verdict & Log Recommendation

- **Relative Winner**: **Phi-3.5-mini-instruct** (for 100% axis coverage, balanced 5-sentence length, and accurately recognizing Patrick's `do_nothing` choice on Day 43).
- **Production Usability Status**: **REJECT ALL WITHOUT TARGETED MILESTONE EXTRACTION**. All models suffer from recency bias on long logs, ignoring the epidemic peak in Weeks 1–4 where the player made their most decisive cost-cutting choices.

