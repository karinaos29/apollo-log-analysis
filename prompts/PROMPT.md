# Prompt Design

The raw JSON log is first converted to a compact table by
`scripts/table_converter.py` (format conversion only: no trends, shifts or
correlations are computed). The "find the key shifts and changes" step still
happens **inside the prompt**, as the model's first task, using the model's own
reasoning over the table.
The output then has two distinct parts, matching what the current PDF
already does structurally:

- **Descriptive part** — what happened, factually, from the system's point of
  view (matches `game_story_text`'s role, but should also reference the
  trajectory/events, not just static end totals)
- **Evaluative part** — a higher-level assessment of what it meant, tone
  always encouraging/positive even when results were mixed (matches
  `text_summary`'s role)

This is a 3-turn conversation with the model (same chat session, so later
turns can refer to the earlier analysis).

The prompts below are the version in `scripts/run_generation.py` (pipeline v2).
The v1 prompts, which received the full raw JSON, are described in
`experiments/v1/`.

---

### Table input

The log is flattened into four blocks (about 2.5–5.7 KB instead of 64–184 KB):

1. **Final outcome summary** — scenario, length, final financial result,
   patients treated (successful/unsuccessful), resignations, final axis scores
2. **Daily metrics table** — one row per day: the four axis scores, finance,
   cumulative patients treated successfully/unsuccessfully, resignations
   (`|`-delimited, finance with thousands separators, human-readable column
   names such as `patient health`)
3. **Event log** — day, event title, the solution the player chose and its
   cost, or "informational" for weekly summaries
4. **Actions taken vs never taken** — strategic actions only (dashboard
   `unlock_*` actions are excluded)

### System prompt

```
You are assisting with the APOLLO2028 Business Game, a hospital-management
simulation. Players are scored on four axes: Patient Experience, Patient
Health, Cost Reduction, and Staff Wellbeing. Simulations can run up to 60
days, and every day matters equally - do not let the most recent days
dominate your analysis; a player's early and mid-game decisions are just
as important as how they finished. After each session, players receive a
report with two parts: a DESCRIPTION of what happened, and an EVALUATION
of what it meant. You will be given the simulation log as a compact table
(a final outcome summary, a daily metrics table, an event log, and an
actions-used summary). Work through this in three steps as instructed,
one at a time.
```

### Turn 1 — Analysis (no output shown to player)

`{early_range}`, `{mid_range}`, `{late_range}` are the run split into thirds
(e.g. Day 0-20, Day 21-40, Day 41-60 for a 60-day run).

```
Here is the simulation log, converted into a compact table:

<TABLE>

TASK 1 - Analyze this log internally before writing anything player-facing.
The daily metrics table covers all {total_days} days of the run, from Day 0
to Day {total_days}. Review the FULL table - early days ({early_range}),
middle days ({mid_range}), and late days ({late_range}) all matter equally.
Do not let the final rows dominate your analysis just because they come
last. Identify:
- the overall trend of each of the four scores (staff wellbeing,
  patient health, patient experience, cost reduction) across the run
- any sharp increases or decreases, and the day they occurred - scan the
  whole table, including {early_range}
- whether any sharp change coincides with an entry in the event log, and if
  so, which event and what choice was made
- any notable absences: actions listed as "never used" in the actions
  summary, especially if a related score was declining
- overall outcome: days completed, patients treated and success rate,
  staff resignations, final financial result

List these findings as short bullet points. Include at least one bullet
about something from {early_range} and one about {mid_range} - not only
the ending.
```

### Turn 2 — Descriptive part

```
TASK 2 - Using only the findings above, write the DESCRIPTIVE part of the
report: 3-5 sentences, factual and neutral in tone, written from the
system's point of view. You must include:
- the starting financial balance (Day 0) and the ending financial balance
- the overall outcome
- at least one specific moment from the first half of the run AND one from
  the second half (a day, an event, or a sharp change) - do not describe only
  the ending
Do not include judgment or evaluation here.
```

### Turn 3 — Evaluative part

```
TASK 3 - Now write the EVALUATIVE part: 3-5 sentences giving a high-level
assessment of what these results mean for the player. Reference at least one
specific, concrete detail from the findings - it does not have to be from the
ending, pick whichever moment is most meaningful. The tone must remain
encouraging and constructive throughout, even where results were weak or
mixed.
```

---

## Pipeline v3 (current): context card

`scripts/context_card.py` computes a fact card from the log (balances, patients,
per-score change with lowest/highest day, notable swings, every player decision
with its event title, chosen option, cost and the score change over the next week,
strategic actions used/never used). The model no longer analyses the log: the
chain is two turns, and each output is validated against the card (one rewrite
if it fails). The prompts live in `scripts/run_card_generation.py`; their content:

- **System prompt:** write the end-of-session report from a FACT CARD; use only
  card facts, copy figures exactly, keep each decision on its own day, say that
  score changes after a decision happened *afterwards* (never that it caused them),
  plain prose.
- **Turn 1 (descriptive):** 3-5 neutral sentences containing the exact starting and
  ending balance, patients treated, all four scores with direction, and at least
  two decisions by exact event title and day; no praise/criticism words; description
  only. A one-shot style example from a different, made-up session is included.
- **Turn 2 (evaluative):** 3-5 encouraging sentences referring to at least one
  decision by event title and day, plus one score that fell or one unused strategic
  action; no new facts; weaknesses framed as opportunities.
- **Rewrite request (only when validation fails):** lists the specific problems and
  asks for the whole part to be rewritten.

Decoding: temperature 0.3, top_p 0.9, seed 42, num_ctx 4096, num_predict 600.
Results and known defects: `experiments/v3/COMPARISON.md`.

---

## Open questions

- Whether the model reliably keeps Task 2 purely descriptive vs. sneaking in
  judgment (a common failure mode) — in v2 it still leaks evaluation
- Whether the model carries mandatory facts (financial balances, all four
  axes) into the report on 60-day logs — in v2 it did not; in v3 it does, but it
  can still attach numbers to the wrong score (see `experiments/v3/COMPARISON.md`)
- Whether it's better to run Tasks 1–3 as one multi-turn chat (context
  carries over) or as separate calls where you manually paste Task 1's
  output into Task 3's prompt — multi-turn is simpler to start with
- Whether the numbers should be filled in by code (placeholders or fixed
  sentences) instead of written by the model
- French output: once the English version works, test asking for both
  languages in one pass vs. a separate translation call
