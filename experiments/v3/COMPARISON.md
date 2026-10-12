# v3 Master Comparison: Context-Card Pipeline vs v2 (table) vs v1 (raw JSON)

**Model:** Phi-3.5-mini only. **Runs:** one per scenario (no repeats, so small differences are within noise).
**Earlier rounds:** [v1](../v1/COMPARISON.md) · [v2](../v2/COMPARISON.md)
**Scoring:** current `scripts/score_outputs.py` for all three versions (see "Scorer fix" below).
**Outputs:** `experiments/v3/<scenario>/<strategy>/output_phi3.5.md` (each file also contains the card the model saw and a validation log).

## 1. What changed between v2 and v3

| Area | v2 | v3 |
|---|---|---|
| What the model reads | Daily table (60 rows) + event log; it finds the facts itself | A ~950-token **context card** computed in Python ([context_card.py](../../scripts/context_card.py)): start/end balance, patients, per-score change with lowest/highest day, notable swings, every player decision (event title, chosen option, cost, options not chosen, score change over the following week), strategic actions used/never used |
| LLM chain | 3 calls (analysis → descriptive → evaluative) | **2 calls** (descriptive → evaluative); the analysis step is done by Python |
| Mandatory facts | requested in the prompt, ignored on 60-day logs | requested in the prompt **and checked**: both balances, all four scores, ≥2 decisions by exact title |
| Validation | none | per-part checks ([validate_part](../../scripts/context_card.py)): balances, scores named, decision titles, numbers not on the card, a decision placed on the wrong day, causal wording, opinion words, evaluation leaking into the description, 3–5 sentences |
| Retry | none | one rewrite per part with the specific problems listed; the better of the two drafts is kept |
| Output hygiene | none | removes degenerate zero-runs and half-finished last sentences, keeps the first paragraph only (drops meta-notes like "(Note: the rewritten…)") |
| Decoding | defaults | temperature 0.3, top_p 0.9, seed 42, `num_ctx` 4096, `num_predict` 600 |
| Prompt | rules only | rules + one-shot style example from a made-up session |

Runner: [run_card_generation.py](../../scripts/run_card_generation.py). The v2 pipeline is unchanged and still runnable.

## 2. Results (Phi-3.5, scores from the fixed scorer)

| Scenario | Groundedness v1 / v2 / **v3** | Coverage v1 / v2 / **v3** | Factual acc. v1 / v2 / **v3** | Conc. desc v1 / v2 / **v3** | Conc. eval v1 / v2 / **v3** | Tone v1 / v2 / **v3** |
|---|---|---|---|---|---|---|
| Tutorial | 0.25 / 0.25 / **0.50** | 1.00 / 0.50 / **1.00** | 1.00 / 1.00 / **1.00** | 1.00 / 1.00 / **1.00** | 1.00 / 0.80 / **1.00** | 0.62 / 0.77 / **0.70** |
| Post-pandemic normal | 0.00 / 0.17 / **0.50** | 1.00 / 1.00 / **1.00** | 0.80 / 1.00 / **0.96** | 0.00 / 1.00 / **0.60** | 1.00 / 0.60 / **1.00** | 1.00 / 0.82 / **1.00** |
| Post-pandemic cost-min | 0.33 / 0.50 / **0.83** | 0.50 / 1.00 / **1.00** | 0.50 / 1.00 / **0.79** | 0.80 / 1.00 / **0.60** | 0.60 / 0.60 / **1.00** | 1.00 / 0.83 / **0.90** |
| Winter flu normal | 0.00 / 0.00 / **0.00** | 0.75 / 1.00 / **1.00** | 0.90 / 0.75 / **0.95** | 0.80 / 1.00 / **1.00** | 0.80 / 0.60 / **1.00** | 1.00 / 0.78 / **0.57** |
| Winter flu cost-min | 0.00 / 0.00 / **0.11** | 1.00 / 1.00 / **1.00** | 0.67 / 0.90 / **1.00** | 1.00 / 1.00 / **1.00** | 1.00 / 0.60 / **1.00** | 0.86 / 0.89 / **0.62** |
| **Mean** | 0.12 / 0.18 / **0.39** | 0.85 / 0.90 / **1.00** | 0.77 / 0.93 / **0.94** | 0.72 / 1.00 / **0.84** | 0.88 / 0.64 / **1.00** | 0.90 / 0.82 / **0.76** |

Judgment-word leakage in the description: 0 in every v3 run. Generation time (s): 54.5, 94.8, 87.5, 63.5, 56.4 (mean 71) for two LLM calls. Timings from different rounds are not a clean benchmark (machine load differed), so treat them as indicative only.

Validation outcome: 6 of the 10 report parts needed a rewrite. Final status: evaluative part passed all checks in 5 of 5 runs; descriptive part in 3 of 5 (the other two stay at 6–7 sentences, one also with causal wording).

## 3. What the review of the actual reports shows

**Fixed relative to v2**
- Every start/end balance, patient count, resignation count and per-score change is correct in all five reports. In v2 the two 60-day reports contained no financial figure at all.
- The 60-day reports now name the early decisions: the Day 6 vaccine choice (correctly dated) and, in the cost-minimization run, the Day 13 "pizza parties" choice, the Day 31 skipped improvements, and the Day 43/53 inaction.
- All four scores are named in every run (tutorial coverage 0.50 → 1.00).
- Groundedness is the best so far (mean 0.18 → 0.39, best run 0.83), but still below the 0.75 target in 3 of 5 runs.

**Still wrong or weak (the scorer does not see most of these)**
1. **Invented fact, winter flu normal:** "two strategic actions, ordering emergency vaccine stock and implementing basic process improvements, were identified as used". The card says no strategic actions were used.
2. **Scrambled numbers, post-pandemic cost-min:** the Day 13 follow-up changes are listed as "2.5, 13.4, 13.4, and 3.8" against patient health/experience/cost, but the card has staff wellbeing −2.5, patient health +12.6, patient experience +13.4, cost reduction +3.8. Each number exists on the card, so the "number not on the card" check passes. This is why factual accuracy there is 0.79.
3. **Garbled title, winter flu cost-min:** "Decline Emergency Flu Vaccine Shipment Available" mixes an option title with an event title.
4. **Causal drift and opinion creep:** "decisions … influenced these outcomes", "led to", "effective financial management" still appear despite the instructions; the check only retries once. The "following week" score changes on the card invite these claims even though they are labelled as observed, not caused.
5. **Event names vs option titles:** the model usually quotes the chosen option's title. The scorer's groundedness counts event *names*, so winter-flu normal scores 0.00 although its Day 6 and Day 31 decisions are correct and correctly dated.
6. **Description length:** two descriptions are 6–7 sentences, because the card requires so many facts to be mentioned.
7. **Tone score:** drops on the winter-flu runs (0.57, 0.62) because the lexicon scorer reacts to words like "decline"; the text itself stays constructive. Not a real regression on its own.

## 4. Scorer fix made in this round
`score_outputs.py` counted sentences by splitting on every `.`, so a score like "77.5" added a sentence. A 4-sentence v3 description was scored as 17 sentences. `sentence_count` now splits only where `.`/`!`/`?` is followed by whitespace. All three versions were rescored with the fixed script; the v2 documents were corrected where their conciseness figures changed (mean conciseness v1 → v2: descriptive 0.72 → 1.00, evaluative 0.88 → 0.64).

## 5. Where this leaves the pipeline
- **Verdict:** a clear improvement in factual reliability (the figures are now trustworthy) and the first version that reports financial results and early decisions on 60-day logs. Still not deployable: it has an invented-fact failure, scrambled per-decision numbers, only one run per scenario, and groundedness under the 0.75 target in 3 of 5 runs.
- **Why the remaining errors happen:** the model is still asked to *assemble* numbers into sentences. Whenever it combines several figures in one sentence (four score changes after a decision), it can attach them to the wrong score.

## 6. Proposed next steps (v4)
1. **Fill numbers with code, not the model.** Have the model write prose containing placeholders (`{end_balance}`, `{d1.patient_health_change}`) and substitute the values in Python, or generate the fixed "facts" sentences (balances, patients, score list, decision lines) deterministically and let the model write only the evaluative part and one linking sentence. This removes errors 2 and 3 completely.
2. **Drop or shrink the "following week" score changes** on the card, or move them into the deterministic sentences, to stop the causal claims and scrambled numbers (errors 2 and 4).
3. **Add checks** for claims about strategic actions used/never used (error 1) and for each number being attached to the right score.
4. **Update the scorer:** accept option titles for groundedness, check numbers by field rather than "appears anywhere", and report real sentence counts.
5. **Repeat runs (N ≥ 3) per scenario** and add more logs before drawing conclusions from differences of a few hundredths.
6. **Try a second model** (Qwen 2.5, or a larger one if the server allows) on the same card, since the card makes the task easier for every model.
