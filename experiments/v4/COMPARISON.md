# v4 Master Comparison: Deterministic Facts + Constrained Model Text

**Model:** Phi-3.5-mini only. **Runs:** one fresh run per scenario (no repeats, so small differences are within noise).
**Earlier rounds:** [v1](../v1/COMPARISON.md) · [v2](../v2/COMPARISON.md) · [v3](../v3/COMPARISON.md)
**Scoring:** current `scripts/score_outputs.py` applied to **all four versions**, so every number in this document comes from the same scorer. The figures inside the v1–v3 documents were computed with earlier scorer versions and differ slightly (see §3).
**Outputs:** `experiments/v4/<scenario>/<strategy>/output_phi3.5.md` (each file holds the Python draft, the validation log, the model's raw text and the final report).
**Repeat runs:** `experiments/v4/repeats/<scenario>/<strategy>/output_phi3.5_seed{1,2,3}.md`. **Hand review:** [REVIEW.md](REVIEW.md).

## 1. What v4 does

| Part | Who writes it | Rule for accepting it |
|---|---|---|
| Descriptive | **Python** ([report_draft.py](../../scripts/report_draft.py)): balances, patients, resignations, the four score changes, the two largest score swings, up to three decisions (chosen by an impact score, listed by day) with exact event title, chosen option and cost; one of three neutral phrasing variants, picked from the session data so the same log always gives the same text | correct by construction |
| Evaluative | **The model**, given only a digit-free fact list (scores that rose/fell, decisions as "event title → choice", unused actions) | no digits; quoted names must match an event title (or a 2+-word part of it), an option or an action, exactly or closely (≥2 words and ≥12 characters for partial matches); ≥1 decision cited; a fallen score or unused action mentioned; an effect of a decision may only be *suggested* ("may have", "could"); 3–5 sentences (longer text is trimmed, keeping the closing sentence) |

Each model text gets one targeted rewrite request if it fails; if it still fails, a deterministic template is used and the run log says so. Runner: [run_hybrid_generation.py](../../scripts/run_hybrid_generation.py). An optional `--rewrite-descriptive` flag lets a model polish the descriptive text (accepted only if every number and quoted title is unchanged); it is **off by default** because Phi-3.5 never passed it.

## 2. How we got here (what did not work)

1. **Placeholders** (model writes prose around `{MONEY}`, `{DEC1}`, …; Python fills them in). Two attempts on the winter-flu normal log: both parts failed validation both times. The model typed numbers it could see in the table, used one placeholder three times, invented placeholders from the masking markers (`{AMOUNT}`, `{DAY}`), and corrupted a name (`{SCOREUBE_…}`). Not retained.
2. **Letting the model rewrite the Python draft** ([outputs kept](first_attempt_rewrite_enabled/)). 0 of 5 descriptive rewrites passed: the model dropped facts (ending balance, decisions), moved events to other days, and wrote "the specific end amount was not provided in the draft". The factual text is therefore left to Python.
3. **Evaluative acceptance depends heavily on the validation rules**, which were tuned on the same five logs (so treat acceptance rates as a description of the rules, not as independent evidence):

| Rule for effects of decisions | Model text accepted (of 5) |
|---|---|
| ban only "led to" / "resulted in" | 5 |
| also ban "contributed to", "played a role", "paid off", "impacted" | 1 |
| allow those words only when hedged ("may", "could", "likely", …) | 4 |
| same, plus close matching of quoted event names (current) | **5** |

   The first setting accepted sentences such as "this decision … contributed to a decline in staff wellbeing" although wellbeing fell steadily across the whole run; the second rejected almost everything; the hedging rule keeps interpretation but not unsupported certainty.

## 3. Results (Phi-3.5, fresh run)

| Scenario | Groundedness v3 → **v4** | Factual acc. v3 → **v4** | Tone v3 → **v4** | Time (s) | Evaluative source |
|---|---|---|---|---|---|
| Tutorial | 0.25 → **0.75** | 1.00 → **1.00** | 0.70 → 0.67 | 20.1 | model (1st try) |
| Post-pandemic normal | 0.50 → **0.83** | 0.96 → **1.00** | 1.00 → 1.00 | 17.0 | model (1st try) |
| Post-pandemic cost-min | 0.83 → **0.83** | 0.79 → **1.00** | 0.90 → 1.00 | 18.8 | model (1st try) |
| Winter flu normal | 0.00 → **0.56** | 0.95 → 0.97 | 0.57 → 0.00 | 42.9 | model (after rewrite) |
| Winter flu cost-min | 0.11 → **0.56** | 1.00 → 1.00 | 0.62 → 0.50 | 37.6 | model (after rewrite) |

Means over the five scenarios (all versions scored with the current scorer):

| | v1 | v2 | v3 | **v4** |
|---|---|---|---|---|
| Groundedness | 0.14 | 0.15 | 0.34 | **0.71** |
| Four-axis coverage | 0.85 | 0.90 | 1.00 | **1.00** |
| Factual accuracy (approx.) | 0.77 | 0.93 | 0.94 | **0.99** |
| Conciseness descriptive / evaluative | 0.72 / 0.88 | 1.00 / 0.64 | 0.84 / 1.00 | **1.00 / 1.00** |
| Tone (lexicon score) | 0.90 | 0.82 | 0.76 | 0.63 |
| Model calls per report | 3 | 3 | 2 (+retries) | **1 (+retry)** |
| Mean generation time (s) | ~82 | ~107 | 71 | **27** |

Model evaluation accepted in **5 of 5** runs: 3 on the first try, 2 after one rewrite; no template fallback. 4 of the 5 accepted texts were trimmed to 5 sentences. Timings come from different sessions on a shared 8 GB machine and are indicative only.

Scorer note: the scorer now ignores score swings in Days 0–2 (start-up calibration) when it picks the "significant days". This lowers some earlier groundedness figures (e.g. v3 tutorial 0.50 → 0.25) compared with the v1–v3 documents.

**Repeat runs (seeds 1, 2, 3; read by hand in [REVIEW.md](REVIEW.md)).** Across all 20 runs (5 logs × 4 seeds) the
model evaluation was accepted 19 times (7 first try, 12 after one rewrite) and the template was used once. The
descriptive part was identical in every run of a log. The review lists the recurring wording patterns and flags
which final reports need the supervisor's revision.

## 4. How to read these numbers

- **The descriptive part is written by Python, not the model.** Its numbers, days and titles are correct by construction. This is why groundedness, coverage and factual accuracy are high; they show that the facts are reliable, not that the model can write them.
- **Groundedness is now partly circular.** The description generator and the scorer use the same definition of a "notable score swing", so the description prints the days the scorer counts. For v4 this metric mainly confirms the template; it is not independent evidence of quality.
- **The model's contribution is the evaluative part** (5 of 5 runs here). The checks guarantee no figures, real decision names and hedged causality. They do **not** measure whether the interpretation is sensible, specific or encouraging; that needs human review.

## 5. Known weaknesses

1. **Generic evaluations.** Three of five evaluations open with nearly the same sentence ("The end of the session reveals a nuanced understanding of the complexities…") for different players. The fixed seed and low temperature make this worse.
2. **Unhedged causal claims still pass** when they use wording outside the check's list, e.g. "can be partly attributed to the strategic decision…" (winter flu normal) and "leading to an increase in the hospital's funds" (winter flu cost-min).
3. **Token glitches are not detected**, e.g. "game'thy" (post-pandemic normal, this run) and "underscs" (earlier rounds).
4. **Sentence trimming** can remove middle sentences of an over-long text (4 of 5 accepted texts were trimmed).
5. **Limited description variety.** The phrasing variant is chosen from the session data; on these five logs four get the same variant, so variety only shows across many logs.
6. **Tone score** is a lexicon count and drops to 0.00 on a constructive text that discusses declines (winter flu normal); it is not a reliable tone measure.
7. **Single run per log; five logs.** Run-to-run variation and behaviour on other kinds of sessions are unmeasured.

## 6. Changes in this revision
- Phrasing variant chosen with a stable checksum of the session data instead of Python's `hash()`, which changed between runs (the same log produced different text).
- Description wording made neutral and grammatical: removed "positive financial territory", "held to zero", "pivotal", "achieving", the incorrect "mid-session" for early swings, and "strategic actions" (a term used for the unused-actions list).
- Quoted-name matching tightened: a single generic word (e.g. "Strategic") no longer counts as citing a decision; titles are split only at real separators.
- All five logs re-run with the model. An earlier version of this document reported "5 of 5" from **re-validating stored model text** with the relaxed rules (old timings, rewritten logs); those results are superseded by this fresh run.
- All four versions rescored with the same, current scorer.

## 7. Next steps
1. **Human review** of the evaluations with a short fixed checklist (accurate? specific to this player? constructive?), since the automatic scores cannot judge this.
2. **Repeat runs (N ≥ 3) per log and more logs** (debt, resignations, early-ending sessions); re-measure acceptance and fallback rate.
3. **Reduce generic openings:** vary the seed per session, raise temperature slightly, or ban stock opening phrases in the check.
4. **Extend the checks:** more causal patterns ("attributed to", "leading to"), a simple word-list check for glitched words.
5. **Independent metric:** score groundedness against facts chosen separately from the generator (e.g. all decisions, human-marked key moments), so v4 is not graded by its own definition.
6. **Try other models** on the evaluative part only (Qwen 2.5, Llama 3.2, a larger model if the server allows), and `--rewrite-descriptive` with a stronger model.
7. **French**, then **deployment basics** (service wrapper, logging of the fallback rate, timeouts, log-schema check).
