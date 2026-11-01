# v4 Output Review: Repeat Runs Read by Hand

**What was done.** Every log was run four times with the v4 pipeline: the canonical run (seed 42, in
`experiments/v4/<scenario>/<strategy>/`) and three repeats (seeds 1, 2, 3, in
[`repeats/`](repeats/)). All 20 reports were **read in full by hand**; no scorer or automatic pattern
counter was used for this review. Counts below are from reading. The descriptive part is
deterministic and was identical in all four runs of each log; only the evaluative part varies.

**Model text accepted:** 19 of 20 evaluations (7 on the first try, 12 after one rewrite); 1 fell back
to the template (winter flu normal, seed 1).

Legend for the final reports: 🔴 needs revision before anyone sees it · 🟠 should be checked · 🟢 minor

## 1. Final reports that need the supervisor's revision

These are the canonical (seed 42) reports, i.e. the ones the pipeline would hand to the platform.

| Report | Flag | Main reason |
|---|---|---|
| [Post-pandemic normal](post-pandemic/normal_strategy/output_phi3.5.md) | 🔴 | garbled word; credits a $337,500 spend for cost reduction |
| [Winter flu normal](winter-flu/normal_strategy/output_phi3.5.md) | 🔴 | states a cause as fact; no closing sentence; unstable across runs |
| [Tutorial](tutorial/normal_strategy/output_phi3.5.md) | 🟠 | credits a $25,000 repair for the financial gain; unsupported praise |
| [Post-pandemic cost-min](post-pandemic/cost_minimization_strategy/output_phi3.5.md) | 🟠 | refusing bonuses framed generously; tone decision needed |
| [Winter flu cost-min](winter-flu/cost_minimization_strategy/output_phi3.5.md) | 🟢 | best of the five; "players" (plural) and some praise wording |
| All five descriptive parts | 🟢 | facts checked; wording and content choices for the supervisor (§3) |

### 🔴 Post-pandemic normal (Mark)
> "…may have contributed positively to cost reduction, a critical aspect of the **game'thy** financial health."
- **Garbled word** ("game'thy").
- **Unsupported credit.** The retention bonuses cost **$337,500** and are credited with improving cost reduction. In the log, cost reduction was already 77.8 on Day 12, the day before the decision, and ended at 75.5. All four runs for this log make the same claim.
- Opens with the stock sentence "The end of the session reveals a nuanced understanding of the complexities…" (identical in three of the five final reports).

### 🔴 Winter flu normal (Jane)
> "The significant rise in cost reduction scores **can be partly attributed to** the strategic decision to purchase flu vaccines for high-risk staff…"
- **A cause stated as fact** (not hedged). The check misses "attributed to". In the log, cost reduction was already 80.6 on Day 5, before the Day 6 vaccine decision, and the vaccines cost $20,000.
- **No forward-looking closing sentence**: the text ends on "…could have indirectly influenced the patient experience positively".
- **Least stable log.** The model needed a rewrite in every run, and seed 1 fell back to the template. Another run (seed 2) explains that overtime bonuses hurt patients "by not addressing immediate patient needs", which is invented reasoning.

### 🟠 Tutorial (Karina)
> "The decision to implement an "Emergency Maintenance Program"… **likely contributed to the hospital's financial improvement**."
- **Unsupported credit.** The repair cost $25,000, and cost reduction was already 82.8 on Day 14, before the Day 15 decision. All four runs give the same credit.
- **Unsupported praise:** "a strong foundation of professional dedication", inferred only from zero resignations.
- Same stock opening sentence as above.

### 🟠 Post-pandemic cost-minimization (Catherine)
> "The decision to "Hope for the Best"… demonstrates a **cautious optimism**… a **strategic restraint** that may have contributed to maintaining the hospital's financial stability."
- Refusing retention bonuses is described kindly. This run also had the largest drops in patient health and staff wellbeing. The declines are mentioned, but the supervisor should decide whether "encouraging" may go this far.
- In a repeat run (seed 2) the refusal is credited with keeping staff ("may have contributed to maintaining staff retention, as no resignations were recorded"). That reverses the meaning of the choice.

### 🟢 Winter flu cost-minimization (Patrick)
- Content is accurate and specific: the declined vaccines, the pizza-party response and the accelerated return are all discussed, with plausible hedged links to falling patient health and wellbeing.
- Wording: "**the players** demonstrated" (it is one player); "commendable financial acumen".

## 2. Patterns in the model-written evaluations (19 texts)

1. **Stock opening.** 12 of 19 start with a variant of "The end of the session / The end-of-session report / The session's conclusion … reveals a **nuanced** / **complex** …". Three of the five final reports open with the *same* sentence: "The end of the session reveal(s/ed) a nuanced understanding of the complexities…". Another 3 start with "In navigating the …".
2. **Fixed skeleton.** [abstract opening] → [a quoted decision with a hedged effect] → [a second decision as a "missed opportunity" or something that "may not have fully" helped] → ["scores fell, highlighting areas for growth"] → [closing].
3. **Stock closing.** 9 of 19 close with "Looking ahead, …". Several more use "…serves as a (valuable) foundation / learning experience…". 3 texts have no forward-looking closing at all (post-pandemic normal seed 1, winter flu normal seed 42, winter flu cost-min seed 3).
4. **Stock vocabulary:** nuanced, complex interplay, holistic, foundation, valuable insights, areas for growth, financial acumen, commendable, testament to, inadvertently.
5. **Credit goes to whichever decision is quoted.** The money or cost-reduction gain is attributed to the cited decision even when that decision *cost* money and the gain came earlier:
   - the maintenance repair, in 4 of 4 tutorial runs;
   - the retention bonuses, in 4 of 4 post-pandemic normal runs;
   - the vaccine purchase, in 2 of 3 winter-flu normal model texts.

   This is the most important content problem. It is usually hedged ("may have", "likely"), so the checks allow it.
6. **Invented or inverted reasoning:**
   - refusing bonuses credited with zero resignations (post-pandemic cost-min seed 2);
   - declining staff vaccines described as "a commitment to patient autonomy" (winter flu cost-min seed 2);
   - zero resignations used as evidence that the pizza parties failed (winter flu cost-min seed 3);
   - the player's motive inferred ("the player's focus on immediate financial concerns", tutorial seed 3).
7. **An event title used as if it were the choice:**
   - '"Critical Equipment Failure" response' (tutorial seed 2);
   - 'the decision "Talent War: …"' (post-pandemic normal seed 3);
   - 'the choice to "Build a Crisis Reserve Fund?" by taking no action' (winter flu cost-min seed 1).
8. **Garbled words in 3 of 19:** "game'thy", "underscs", "the hospital' extrinsic and intrinsic aspects".
9. **Length.**
   - One text has 6 sentences: tutorial seed 3, where the sentence counter misses a full stop inside a closing quote (`…Program."`), so it was never trimmed.
   - One ends in a ~70-word run-on sentence (winter flu cost-min seed 3).
   - One is thin: 3 sentences about a single decision (post-pandemic cost-min seed 3).
10. **Log-specific quality.** Winter flu cost-min is consistently the best (the clearest decisions to talk about). Winter flu normal and post-pandemic normal are the weakest.

## 3. Patterns in the deterministic (Python) text

1. **One frame for every player.** Every description is the same five sentences: money → patients and resignations → four scores (rises, then falls) → two largest swings → key decisions. Four of the five logs get the same phrasing variant, so the descriptions read alike apart from the numbers.
2. **The swing sentence can read as noise:**
   - tutorial lists a fall and an immediate recovery of the same score (patient experience, Days 3–5 and 5–7);
   - winter flu normal lists two drops of the same score;
   - swings are not linked to any decision.
3. **Option names without context.** "Hope for the Best" (Catherine's refusal to pay retention bonuses) cannot be understood without the alternatives.
4. **Decision selection.** At most three decisions are shown, picked by an impact rule. For example, Jane's Day 21 "Conservative Return" and the Day 43 and Day 53 inactions are left out.
5. **Fallback evaluation template** (used once, winter flu normal seed 1). It always has the same five-sentence structure ("A clear strength of this run is that…", "The best opportunity for next time is that…"). It repeats the score numbers from the description, and it starts with a judgment phrase. Its grammar error was fixed in this round ("Trying wellness program and counseling services was not part of this run" now reads "Options that were not used in this run, such as "wellness program" and "counseling services", could be useful next steps").

## 4. Decisions for the supervisor
1. **Is hedged speculation about effects acceptable at all** in a learning tool? If not, the evaluation should be limited to what the player chose and which scores rose or fell, with no "may have contributed".
2. **How encouraging is encouraging?** Is "cautious optimism" an acceptable way to describe a cost-cutting choice that hurt patients and staff?
3. **What belongs in the description:** keep the swing sentence? List all decisions or the top three? Explain opaque option names?
4. **Variety vs. predictability:** one fixed frame is safe and checkable, but every player gets the same-looking text.

## 5. Suggested fixes (not applied, so this review describes exactly what was produced)
- Extend the cause check ("attributed to", "testament to", "effectiveness of", "have led to" even when the sentence also contains a hedge word), and reject crediting a gain to a decision made after the gain.
- Ban the stock opening phrases and require a forward-looking closing sentence.
- Count a sentence end inside closing quotes (`."`) so trimming works.
- Simple check for garbled words.
- Ask the supervisor to rewrite 3–5 evaluations by hand. Those would make better examples in the prompt than rules.
