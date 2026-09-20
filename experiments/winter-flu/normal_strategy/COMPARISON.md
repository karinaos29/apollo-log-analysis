# Model Comparison: Winter Flu Crisis Scenario (Normal Strategy)

**Log File**: `data/winter-flu/normal_strategy-winter_flu_crisis-2026-09-20T22-07-06.json`  
**Player**: Jane (Normal Strategy)  
**Evaluation Standard**: [EVALUATION_CRITERIA_v2.md](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/docs/EVALUATION_CRITERIA_v2.md)  
**Scoring Script**: [batch_score.py](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/scripts/batch_score.py) / [score_outputs.py](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/scripts/score_outputs.py)

---

## 1. Executive Scorecard: Relative Winner vs. Absolute Viability

| # | Criterion | Evaluation Type | Target Scale | Llama 3.2 (3B) | Phi-3.5-mini (3.8B) | Qwen 2.5 (3B) | Relative Winner | Absolute Production Threshold Status |
|---|---|---|---|---|---|---|---|---|
| 1 | **Groundedness** | Automatic (Script) | 0.0 – 1.0 | 0.00 *(0.00 exact)* | 0.00 *(0.00 exact)* | 0.00 *(0.00 exact)* | **Tie (0.00)** | ❌ **FAIL (All models)** — 0.00 is completely unusable |
| 2 | **Coverage** | Automatic (Script) | 0.0 – 1.0 (4 axes) | **0.75** (3/4 axes) | **0.75** (3/4 axes) | **0.75** (3/4 axes) | **Tie (0.75)** | ⚠️ All models missed at least 1 axis |
| 3 | **Conciseness (Desc)**| Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (3 sents) | 0.60 (7 sents) | **1.00** (4 sents) | **Llama / Qwen** | ⚠️ Phi exceeded target length |
| 3 | **Conciseness (Eval)**| Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (4 sents) | 0.60 (7 sents) | **1.00** (4 sents) | **Llama / Qwen** | ⚠️ Phi exceeded target length |
| 4 | **Speed** | Automatic (Logged) | Wall-clock seconds | 54.0s | 77.8s | **36.0s** | **Qwen 2.5** | ✅ All under 80s on 60-day log |
| 5 | **Consistency** | Automatic | 0.0 – 1.0 (repeat runs)| *N/A (Single run)* | *N/A (Single run)* | *N/A (Single run)* | *N/A* | Requires repeat runs |
| 6 | **Factual Accuracy** | Semi-auto + Spot Check| 0.0 – 1.0 | 0.86 *(Gross Contradiction)*| **0.90** *(Exact Score Match)*| 0.60 | **Phi-3.5** | ❌ Llama asserts 8-day run with Day 50 event |
| 7 | **Tone (Evaluative)**| Semi-auto (Script) | 0.0 – 1.0 | 0.83 | **1.00** | 0.75 | **Phi-3.5** | ✅ Positive tone across candidates |
| 8 | **Two-Part Separation**| Manual Checklist | Issue count (0 is best) | **0 issues** | **0 issues** | **0 issues** | **Tie (0)** | ✅ Clean separation maintained |
| 9 | **Fluency** | Manual Checklist | Issue count (0 is best) | **0 issues** | **0 issues** | **0 issues** | **Tie (0)** | Fluent, well-structured English |

---

## 2. Ground Truth Reference (Session Data)

- **Scenario**: Winter Flu Crisis (60 Days completed)
- **Player**: Jane (Normal Strategy)
- **Clinical & Operational Outcome**:
  - Patients Treated: **1,198 total** (**885** successful, **313** unsuccessful, **73.9%** success rate)
  - Staff Resignations: **0** (Staff count: 14 maintained)
  - Financial Result: Initial funds **$3,351,684.57** → Final funds **$5,263,498.62** (**+$1,911,814.05 major profit**)
- **AIM Performance Trajectory**:
  - **Staff Wellbeing**: 77.50 → 59.14 (*-18.36 pts*)
  - **Patient Health**: 75.00 → 60.17 (*-14.83 pts — well-defended against flu outbreak*)
  - **Patient Experience**: 75.00 → 60.19 (*-14.81 pts*)
  - **Cost Reduction**: 39.02 → 81.44 (*+42.42 pts*)
  - Overall Performance Score: **65.24**
- **Key Crisis Events & Decisions**:
  - Day 6: *Emergency Flu Vaccine Shipment Available* → Chose **Buy Partial Vaccine Supply**
  - Day 13: *Staff Exhaustion Reaches Critical Levels* → Chose **Overtime Bonuses**
  - Day 21: *Staff Recovery: How Fast Should They Return?* → Chose **Conservative Return**
  - Day 31: *Midpoint Review: Operational Lessons Learned* → Chose **Basic Improvements**

---

## 3. Comparative Analysis & Production Viability

### 3.1 Groundedness Complete Breakdown (0.00 Across All Models)
In a 60-day crisis simulation with 14 decision events, **all three models scored 0.00 on Groundedness**:
- Not a single model cited the critical early-game interventions: Day 6 (buying vaccines), Day 13 (overtime bonuses), or Day 21 (staff recovery).
- By completely ignoring Days 1–40, the models missed the entire active flu epidemic.
- **Production Threshold Verdict**: **CRITICAL DEFICIENCY**. An end-of-game summary for a flu crisis scenario that fails to mention whether the hospital bought vaccines or handled staff exhaustion is useless to the player.

### 3.2 Llama 3.2: Severe Temporal Incoherence
- Llama 3.2 wrote: *"Over the course of 8 days, the hospital experienced a steady improvement in patient health, with a notable increase on Day 50..."*
- **Logical Impossibility**: Claiming that an event on Day 50 occurred during an "8-day" simulation proves that Llama 3.2 loses temporal context over longer 60-day JSON inputs.
- Fabricated $100,000 in savings (actual surplus: +$1.91 million).
- *Verdict*: **Disqualified**.

### 3.3 Phi-3.5 vs. Qwen 2.5
- **Phi-3.5** accurately retrieved the overall simulation score: **65.24** (an exact match with the JSON performance metric). It noted 57 simulation days and the Day 53/54 late-game decisions, but bloated to 7 sentences per section.
- **Qwen 2.5** maintained concise 4-sentence structures and was fast (36.0s), but like Phi, focused only on late-game days (Day 53) while omitting the actual epidemic outbreak in Weeks 1–4.

---

## 4. Final Verdict & Log Recommendation

- **Relative Winner**: **Phi-3.5-mini-instruct** (for exact score extraction `65.24` and true event awareness, despite slight over-length).
- **Production Usability Status**: **REJECT ALL WITHOUT CONTEXT COMPACTION**. Feeding raw 60-day JSON (180 KB) causes all 3B models to lose early-run context and focus solely on the tail end of the log. A sliding-window or milestone extractor is mandatory for long scenarios.

