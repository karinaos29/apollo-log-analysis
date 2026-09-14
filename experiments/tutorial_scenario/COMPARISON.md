# Model Comparison: Tutorial Scenario Log Evaluation

This document presents a structured evaluation and comparison of the three candidate foundation models on the **Tutorial Scenario** (`data/apollo_player-Karina-2026-08-30T20-38-57.json`), evaluated in accordance with [EVALUATION_CRITERIA_v2.md](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/docs/EVALUATION_CRITERIA_v2.md) and scored via [score_outputs.py](file:///Users/KarinaOsipova/Desktop/apollo28/apollo-log-analysis/scripts/score_outputs.py).

---

## 1. Executive Summary & Scorecard

| # | Criterion | Evaluation Type | Target / Scale | Llama 3.2 (3B) | Phi-3.5-mini (3.8B) | Qwen 2.5 (3B) | Winner |
|---|---|---|---|---|---|---|---|
| 1 | **Groundedness** | Automatic (Script) | 0.0 – 1.0 | 0.18 *(0.00 exact)* | **0.27** *(0.18 exact)* | 0.18 *(0.09 exact)* | **Phi-3.5** |
| 2 | **Coverage** | Automatic (Script) | 0.0 – 1.0 (4 axes) | 0.75 (3/4 axes) | **1.00** (4/4 axes) | 0.25 (1/4 axes) | **Phi-3.5** |
| 3 | **Conciseness (Desc)** | Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (4 sents) | **1.00** (4 sents) | 0.80 (2 sents) | **Llama / Phi** |
| 3 | **Conciseness (Eval)** | Automatic (Script) | 0.0 – 1.0 (3–5 sents) | **1.00** (5 sents) | **1.00** (5 sents) | **1.00** (4 sents) | **Tie** |
| 4 | **Speed** | Automatic | seconds | *N/A (Not logged)* | *N/A (Not logged)* | *N/A (Not logged)* | *N/A* |
| 5 | **Consistency** | Automatic | 0.0 – 1.0 (repeat runs)| *N/A (Single run)* | *N/A (Single run)* | *N/A (Single run)* | *N/A* |
| 6 | **Factual Accuracy** | Semi-auto + Spot Check | 0.0 – 1.0 | 0.67 *(Severe Hallucinations)* | **1.00** *(Minor Inversion)* | 1.00 *(Generalized Misclaim)* | **Phi-3.5** |
| 7 | **Tone (Evaluative)** | Semi-auto (Script) | 0.0 – 1.0 | 0.70 | 0.62 | **1.00** | **Qwen 2.5** (Lexical) / **Phi-3.5** (Grounded) |
| 8 | **Two-Part Separation**| Manual Checklist | Count of issues (lower is better) | 1 issue | 1 issue | **0 issues** | **Qwen 2.5** |
| 9 | **Fluency** | Manual Checklist | Count of issues (lower is better) | **0 issues** | 1–2 issues | 0–1 issues | **Llama 3.2** |

---

## 2. Ground Truth Reference (Session Data)

- **Source Log**: `data/apollo_player-Karina-2026-08-30T20-38-57.json`
- **Scenario**: Tutorial Scenario (Player: Karina)
- **Duration**: **21 days** (Day 0 to Day 21)
- **Events (1 total)**: Day 15 — **"Critical Equipment Failure"** (`equipment_failure_crisis`), Solution: **"Emergency Maintenance Program"** (`emergency_maintenance`), locked funds: **$25,000**.
- **Outcome Metrics**:
  - Staff Resignations: **0**
  - Patients Treated: **302** successful, **75** unsuccessful (Total 377, **80.1%** success rate)
  - Remaining Finance: **$1,612,332.23**
  - AIM Trajectory:
    - **Staff Wellbeing**: 77.50 → 66.50 (*Decreased -11.00 pts*)
    - **Patient Health**: 75.00 → 60.10 (*Decreased -14.90 pts*)
    - **Patient Experience**: 75.00 → 66.29 (*Decreased -8.71 pts*)
    - **Cost Reduction**: 37.59 → 79.94 (*Increased +42.35 pts*)
    - Overall Score: **68.21**

---

## 3. Detailed Model Analysis

### 1. Llama 3.2 (3B-instruct)
- **Output File**: `experiments/tutorial_scenario/output_llama3.2.md`
- **Strengths**:
  - **Superb Fluency and Style**: Highest prose quality, natural sentence variety, and professional cadence.
  - **Perfect Structural Length**: 4 sentences in the descriptive part, 5 sentences in the evaluative part (1.00 on both conciseness metrics).
  - **Constructive Evaluative Tone**: Balances encouragement with constructive areas for improvement.
- **Weaknesses & Critical Failures**:
  - **Catastrophic Hallucinations**: Confabulated nearly every key numerical and historical fact:
    - Hallucinated that the simulation lasted **30 days** (actual: 21 days).
    - Hallucinated that the equipment crisis happened on **Day 18** (actual: Day 15).
    - Hallucinated **two staff members resigning** (actual: 0 resignations).
    - Hallucinated a final financial result of **$250,000** (actual: $1,612,332).
    - Hallucinated **100 patients treated** in Task 1 analysis (actual: 377).
    - Invented a fictitious **"missed opportunity for cost reduction on Day 20"**.
  - **Groundedness**: Received a script score of 0.18 only because `Day 1` and `Day 2` falsely substring-matched `Day 18` and `Day 20`. Exact groundedness on real report facts is **0.00**.
- **Verdict**: Unsuitable for deployment without severe guardrails / strict RAG, as it invents believable but completely incorrect hospital metrics.

---

### 2. Phi-3.5-mini-instruct (3.8B)
- **Output File**: `experiments/tutorial_scenario/output_phi3.5.md`
- **Strengths**:
  - **Comprehensive AIM Coverage (1.00)**: The only model to explicitly mention all four AIM dimensions (*Cost Reduction, Patient Health, Patient Experience, Staff Wellbeing*).
  - **Strong Factual Grounding**:
    - Correctly identified the exact event title: **"Critical Equipment Failure"**.
    - Correctly placed the event on **Day 15**.
    - Accurately observed the metric dynamics: steady increase in Cost Reduction while Patient Health, Experience, and Wellbeing faced declines leading up to Day 15.
  - **Clean Structure**: 4 descriptive sentences, 5 evaluative sentences (1.00 conciseness).
- **Weaknesses**:
  - **Scratchpad Generation Glitch**: In the internal analysis (Task 1), suffered a token looping crash: `"emergency_mainten0000000000000000000000000000000"`. Fortunately, it recovered cleanly in Tasks 2 and 3.
  - **Descriptive Leakage**: Descriptive closing ventures into subjective/interpretive analysis (*"suggesting an effective intervention"*, *"underscore the interconnectedness..."*).
  - **Calendar Artifact**: Framed the run as a *"Tuesday to Friday period"*, which is an artificial mapping onto the 21-day timeline.
- **Verdict**: **Best overall performer**. It genuinely understood and represented the multi-axis hospital dynamics and remained anchored to the log facts.

---

### 3. Qwen 2.5 (3B-instruct)
- **Output File**: `experiments/tutorial_scenario/output_qwen2.5_3b.md`
- **Strengths**:
  - **Clean Two-Part Separation**: Kept descriptive factual and evaluative focused, with zero checklist issues.
  - **Accurate Event Identification**: Correctly matched Day 15, equipment failure, and the chosen solution (*"Emergency Maintenance"*).
  - **Positive Tone (1.00)**: Highly encouraging and supportive tone throughout the evaluative part.
- **Weaknesses**:
  - **Excessive Brevity**: The descriptive section is only 2 sentences (below the 3–5 sentence requirement, scoring 0.80).
  - **Poor Explicit Axis Coverage (0.25)**: Explicitly named only *Patient Experience*. Grouped the others into a vague *"across all four axes"* statement.
  - **Qualitative Factual Distortion**: Claimed *"modest improvement across all four axes"*, when in fact 3 out of 4 axes significantly deteriorated (only Cost Reduction improved).
  - **Analysis Discrepancy**: Stated *"15 days completed"* in Task 1 analysis instead of 21 days.
- **Verdict**: Solid baseline that avoids blatant number hallucinations, but overly terse and glosses over critical negative score trends.

---

## 4. Methodological Findings & Script Audit

During this evaluation, an audit of `scripts/score_outputs.py` revealed an important nuance:
- **Substring Collision in Groundedness**:
  `score_outputs.py` uses `f"day {d}" in text.lower()`. Because single-digit days (e.g. `d = 1`, `d = 2`) are tested without word boundaries, `"Day 18"` registers as a hit for Day 1, and `"Day 20"` registers as a hit for Day 2.
  - *Recommendation*: Update `score_outputs.py` to use regex word boundaries: `re.search(rf"\bday\s*{d}\b", text, re.IGNORECASE)`.
- **Consistency Score Context**:
  The script's `0.06` consistency score was calculated across three **different** models. Per `EVALUATION_CRITERIA_v2.md`, consistency measures the stability of the **same model** across $N \ge 3$ repeated runs of identical input.

---

## 5. Final Recommendation

1. **Top Candidate: Phi-3.5-mini-instruct**
   Phi-3.5 is the top choice for APOLLO2028 report generation. It is the only model that grasped the multi-dimensional nature of the simulation, faithfully captured all four axes, and accurately situated the Day 15 equipment failure.
2. **Mitigations for Phi-3.5**:
   - Add a temperature / repetition penalty constraint to prevent the scratchpad zero-looping (`emergency_mainten000...`).
   - Reinforce the system prompt boundary: descriptive section must strictly state *what occurred*, deferring *why/effectiveness* to the evaluative part.

