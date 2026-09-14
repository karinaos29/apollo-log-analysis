# Prompt Design

Per the professor's guidance: no external Python preprocessing of the JSON.
The "find the key shifts and changes" step happens **inside the prompt**, as
the model's first task, using the model's own reasoning over the raw JSON.
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

---

### System prompt

```
You are assisting with the APOLLO2028 Business Game, a hospital-management
simulation. Players are scored on four axes: Patient Experience, Patient
Health, Cost Reduction, and Staff Wellbeing. After each session, players
receive a report with two parts: a DESCRIPTION of what happened, and an
EVALUATION of what it meant. You will be given the full simulation log in
JSON. Work through this in three steps as instructed, one at a time.
```

### Turn 1 — Analysis (no output shown to player)

```
Here is the full simulation log in JSON:

<PASTE FULL JSON HERE>

TASK 1 — Analyze this log internally before writing anything player-facing.
Identify:
- the overall trend of each of the four scores (staff_wellbeing,
  patient_health, patient_experience, cost_reduction) across the run
- any sharp increases or decreases, and the day they occurred
- whether any sharp change coincides with an entry in event_history, and if
  so, which event and what solution was chosen
- any notable absences: actions that were available but never taken,
  especially if a related score was declining (e.g. wellbeing dropping with
  no wellness/support actions used)
- overall outcome: days completed, patients treated and success rate,
  staff resignations, final financial result

List these findings as short bullet points.
```

### Turn 2 — Descriptive part

```
TASK 2 — Using only the findings above, write the DESCRIPTIVE part of the
report: 3-5 sentences, factual and neutral in tone, written from the
system's point of view. This should read like an objective reconstruction
of what happened over the run — including the overall outcome AND at least
one specific moment (a day, an event, or a sharp change) — so the player can
see how their in-the-moment decisions added up, even if they didn't notice
it while playing. Do not include judgment or evaluation here — save that for
the next step.
```

### Turn 3 — Evaluative part

```
TASK 3 — Now write the EVALUATIVE part: 3-5 sentences giving a high-level
assessment of what these results mean for the player. Reference at least one
specific, concrete detail from the findings (not generic praise). The tone
must remain encouraging and constructive throughout, even where results were
weak or mixed — frame weaknesses as opportunities rather than failures.
```

---

## Notes / things to test

- Whether the model reliably keeps Task 2 purely descriptive vs. sneaking in
  judgment (a common failure mode) — worth checking explicitly per model
- Whether it's better to run Tasks 1–3 as one multi-turn chat (context
  carries over) or as separate calls where you manually paste Task 1's
  output into Task 3's prompt — multi-turn is simpler to start with
- French output: once the English version works, test asking for both
  languages in one pass vs. a separate translation call
