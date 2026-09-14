# Evaluation Criteria v2 — Definitions, Scale, and Scoring Method

Each criterion below specifies: what it measures, its scale, and exactly how
the score is produced — automatic (script only, no human judgment),
semi-automatic (script produces a first-pass score using a defined but
approximate method), or manual-but-structured (a human answers a fixed
checklist of yes/no items — not a holistic gut rating).

## Automatic (script computes the score, no human judgment)

### 1. Groundedness
**Definition:** the fraction of "referenceable facts" available in the JSON
(event names, specific days, sharp score changes) that actually appear in
the generated text.
**Scale:** 0.0–1.0 (ratio).
**Method:** the script extracts a fixed list of referenceable facts from the
JSON — every entry in `event_history` (by name), every day number where a
score changes by more than a threshold (e.g. 5 points) between consecutive
days, and the final outcome numbers (days completed, patients treated,
success rate, net financial result). It then checks, per fact, whether it
appears in the generated text (string/number match, allowing for reasonable
formatting variation). Score = (facts mentioned) / (facts available).
Implemented in `score_outputs.py::groundedness_score()`.

### 2. Coverage
**Definition:** whether all four AIM axes (staff wellbeing, patient health,
patient experience, cost reduction) are referenced in the text.
**Scale:** 0.0–1.0 (fraction of the 4 axes mentioned, via keyword match).
**Method:** keyword search per axis (e.g. "wellbeing", "patient health",
"patient experience", "cost"/"financ"/"budget"). Implemented in
`score_outputs.py::coverage_score()`.

### 3. Conciseness
**Definition:** whether each part (descriptive, evaluative) falls within the
target length (3–5 sentences, per the prompt design).
**Scale:** 0.0–1.0 per part (1.0 if within range, linear penalty outside it,
e.g. 6 sentences = 0.8, 8+ sentences = 0.0).
**Method:** sentence count via simple splitting. Implemented in
`score_outputs.py::conciseness_score()`.

### 4. Speed
**Definition:** wall-clock time for the full 3-step generation.
**Scale:** seconds (raw number, not normalized — compare directly across
models).
**Method:** already timed and printed by `run_generation.py`.

### 5. Consistency
**Definition:** how stable the model's output is on repeated runs of the
*same* input.
**Scale:** 0.0–1.0 (similarity score across N repeated runs).
**Method:** run the same model on the same JSON N times (suggest N=3),
extract the same "referenceable facts" as in Groundedness from each output,
and compute the average pairwise overlap (Jaccard similarity of the fact
sets) across runs. Implemented in `score_outputs.py::consistency_score()` —
requires multiple output files as input.

## Semi-automatic (script gives a first-pass number, method is approximate — flagged as such)

### 6. Factual accuracy
**Definition:** whether numeric claims in the text match numbers actually in
the JSON.
**Scale:** 0.0–1.0 (fraction of extracted numeric claims found in the JSON,
within a small tolerance for rounding).
**Method:** regex-extract standalone numbers from the text, compare each
against the full set of numeric values in the JSON (allowing ±1% tolerance
for rounding/formatting). **Caveat:** this will have false positives
(coincidental number matches) and false negatives (correct claims phrased
in a way the JSON doesn't literally contain, e.g. a computed percentage) —
treat this score as a flag for which outputs need a manual spot-check, not
a final verdict. Implemented in `score_outputs.py::factual_accuracy_score()`.

### 7. Tone (evaluative part only)
**Definition:** how positive/encouraging the evaluative part reads.
**Scale:** 0.0–1.0 (positive-word count / total sentiment-word count, using
a fixed small positive/negative word list).
**Method:** lexicon-based sentiment scoring — simple and transparent, but
crude (no negation handling, no sarcasm detection). Implemented in
`score_outputs.py::tone_score()`. **This is the criterion most worth
double-checking manually** — a text can score well lexically while still
reading oddly in context.

## Manual, but structured as a checklist (not a holistic rating)

These two are hard to fully automate without another model-as-judge (which
introduces its own subjectivity/cost), so instead of a 1–5 gut score, use a
fixed yes/no checklist — this bounds the human's judgment to specific,
repeatable questions rather than an overall impression.

### 8. Two-part separation
Checklist (score = number of "No" answers, i.e. lower is better):
- [ ] Does the descriptive part contain any judgment/opinion word (e.g.
      "excellent," "poor," "impressive," "disappointing," "great")?
- [ ] Does the evaluative part introduce new facts not present in the
      descriptive part or the JSON?

### 9. Fluency
Checklist (score = number of "No" answers, lower is better):
- [ ] Any grammatical errors?
- [ ] Any awkward/unnatural phrasing a native speaker wouldn't use?
- [ ] Any repeated words/phrases within the same part?

## Summary table

| # | Criterion | Type | Scale |
|---|---|---|---|
| 1 | Groundedness | Automatic | 0–1 |
| 2 | Coverage | Automatic | 0–1 |
| 3 | Conciseness | Automatic | 0–1 per part |
| 4 | Speed | Automatic | seconds |
| 5 | Consistency | Automatic (needs N repeat runs) | 0–1 |
| 6 | Factual accuracy | Semi-automatic | 0–1 (flag for spot-check) |
| 7 | Tone | Semi-automatic | 0–1 (flag for spot-check) |
| 8 | Two-part separation | Manual checklist | count of issues |
| 9 | Fluency | Manual checklist | count of issues |

