# v4 Master Comparison: Deterministic Facts + Constrained Model Text

**Model:** Phi-3.5-mini only. **Runs:** one per scenario (no repeats, so small differences are within noise).
**Earlier rounds:** [v1](../v1/COMPARISON.md) · [v2](../v2/COMPARISON.md) · [v3](../v3/COMPARISON.md)
**Scoring:** current `scripts/score_outputs.py` for all versions (sentence-count fix described in the v3 document).
**Outputs:** `experiments/v4/<scenario>/<strategy>/output_phi3.5.md` (each file also holds the Python draft, the validation log and the model's raw text).

## 1. What v4 does

| Part | Who writes it | Rule for accepting it |
|---|---|---|
| Descriptive | **Python** ([report_draft.py](../../scripts/report_draft.py)): balances, patients, resignations, the four score changes, the two largest score swings, up to three key decisions with day, exact event title, chosen option and cost | correct by construction |
| Evaluative | **The model**, given only a digit-free fact list (scores that rose/fell, decisions as "event title → choice", unused actions) | no digits, quoted names must be exact event titles/options, ≥1 decision cited, a fallen score or unused action mentioned, an effect of a decision may only be *suggested* ("may have", "could"), 3–5 sentences (longer text is trimmed, keeping the closing sentence) |

Each model text gets one targeted rewrite request if it fails; if it still fails, a deterministic template is used and the run log says so. Runner: [run_hybrid_generation.py](../../scripts/run_hybrid_generation.py). An optional `--rewrite-descriptive` flag lets a model polish the descriptive text (accepted only if every number and quoted title is unchanged); it is **off by default** because Phi-3.5 never passed it.

## 2. How we got here (what did not work)

1. **Placeholders** (model writes prose around `{MONEY}`, `{DEC1}`, …; Python fills them in). Two attempts on the winter-flu normal log: both parts failed validation both times. The model typed numbers it could see in the table, used one placeholder three times, invented placeholders from the masking markers (`{AMOUNT}`, `{DAY}`), and corrupted a name (`{SCOREUBE_…}`). Not retained.
2. **Letting the model rewrite the Python draft** ([outputs kept](first_attempt_rewrite_enabled/)). 0 of 5 descriptive rewrites passed: the model dropped facts (ending balance, decisions), moved events to other days, and wrote "the specific end amount was not provided in the draft". The factual text is therefore left to Python.
3. **Evaluative acceptance depends heavily on the causality rule**, which we tuned in three steps on the same five logs (so treat the numbers as a description of the rule, not as independent evidence):

| Rule for effects of decisions | Model text accepted (of 5) |
|---|---|
| ban only "led to" / "resulted in" | 5 |
| also ban "contributed to", "played a role", "paid off", "impacted" | 1 |
| allow those words only when hedged ("may", "could", "likely", …) | **4** (final) |

   The first setting accepted sentences such as "this decision … contributed to a decline in staff wellbeing" although wellbeing fell steadily across the whole run; the second rejected almost everything; the third keeps interpretation but not unsupported certainty.

## 3. Results (Phi-3.5)

| Scenario | Groundedness v3 → **v4** | Factual acc. v3 → **v4** | Tone v3 → **v4** | Time (s) v3 → **v4** | Evaluative source |
|---|---|---|---|---|---|
| Tutorial | 0.50 → **0.75** | 1.00 → **1.00** | 0.70 → 0.67 | 54.5 → **14.9** | model (1st try) |
| Post-pandemic normal | 0.50 → **0.67** | 0.96 → **1.00** | 1.00 → 1.00 | 94.8 → **31.7** | template |
| Post-pandemic cost-min | 0.83 → 0.83 | 0.79 → **1.00** | 0.90 → 1.00 | 87.5 → **17.6** | model (1st try) |
| Winter flu normal | 0.00 → **0.56** | 0.95 → 0.96 | 0.57 → 0.33 | 63.5 → **55.3** | model (after rewrite) |
| Winter flu cost-min | 0.11 → **0.78** | 1.00 → 1.00 | 0.62 → 0.62 | 56.4 → **53.4** | model (after rewrite) |

Means over the five scenarios:

| | v1 | v2 | v3 | **v4** |
|---|---|---|---|---|
| Groundedness | 0.12 | 0.18 | 0.39 | **0.72** |
| Four-axis coverage | 0.85 | 0.90 | 1.00 | **1.00** |
| Factual accuracy (approx.) | 0.77 | 0.93 | 0.94 | **0.99** |
| Conciseness descriptive / evaluative | 0.72 / 0.88 | 1.00 / 0.64 | 0.84 / 1.00 | **1.00 / 1.00** |
| Tone (lexicon score) | 0.90 | 0.82 | 0.76 | 0.72 |
| Model calls per report | 3 | 3 | 2 (+retries) | **1 (+retry)** |
| Mean generation time (s) | ~82 | ~107 | 71 | **35** |

Judgment-word leakage in the description: 0 in every run (it is Python text). Timings come from different sessions on a shared 8 GB machine and are indicative only.

## 4. How to read these numbers

- **The descriptive part is not model-generated.** The high groundedness, coverage and factual-accuracy scores are largely a property of the Python text, which is exactly what "all numbers, days and titles correct by construction" means. They show that the facts can be made reliable; they do not show that the model can write them.
- **The model's contribution is the evaluative part** (4 of 5 runs), where it adds interpretation and tone that a template cannot. In the accepted texts every quoted name is exact, no figure appears, and effects of decisions are phrased as possibilities.
- Groundedness 0.72 is just under the 0.75 target; the five-log sample, a single run per log, and a rule tuned on those same logs mean it should be confirmed on new logs before it is relied on.

## 5. Known weaknesses

1. **Template-like description.** Every report has the same structure and wording; there is no variety between players beyond the facts.
2. **Early-run swings.** The "notable score movements" can be start-up effects (e.g. patient health falling between Day 1 and Day 2); they are factual but may not be what a player would call a key moment.
3. **Evaluative content is only partly checked.** The validator controls facts, titles and causal certainty, not whether the interpretation is sensible. Some accepted sentences are generic ("a nuanced understanding of the complexities…") or mildly speculative ("a strategic restraint that may have contributed…").
4. **Sentence trimming** can remove middle sentences of an over-long text (3 of the 4 accepted texts were trimmed).
5. **A shortened event title fails the check** (post-pandemic normal: "Competitors Offering Sign-On Bonuses" instead of the full title), which sends a good-quality text to the template.
6. **Token glitches** (e.g. "underscs" seen in earlier rounds) are not detected.
7. **Tone score** is a lexicon count and drops on texts that discuss declines, even when they are constructive.
8. **Single run per log; five logs.** Nothing here measures run-to-run variation.

## 6. Next steps
1. **Repeat runs (N ≥ 3) per log and add more logs** (including debt, resignations and early-ending sessions), then re-measure evaluative acceptance and fallback rate.
2. **Human review** of the evaluations with a short fixed checklist (accurate? constructive? generic?) to complement the automatic scores.
3. **Try a stronger model** (Qwen 2.5 7B or larger, if the platform server can host one) with `--rewrite-descriptive`; if it keeps the facts intact, descriptive variety can come back without losing correctness.
4. **Improve the Python description:** vary the sentence patterns, drop start-up swings, choose the most informative decisions rather than first/middle/last.
5. **French:** the deterministic text only needs translated templates; the model prompt needs a French version and a French set of checks.
6. **Update the scorer** to accept option titles for groundedness and to check numbers by field.
7. **Deployment basics:** wrap the pipeline as a service with logging of the validation outcome (fallback rate is the key health metric), timeouts, and a schema check for the log format.
