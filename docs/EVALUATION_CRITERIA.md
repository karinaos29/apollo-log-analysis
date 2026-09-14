# Evaluation Criteria for Model Comparison

Score each generated report (descriptive + evaluative parts) on these axes,
1–5. Run the same JSON log through each candidate model and compare scores
side by side.

| Criterion | What it checks | 1 (poor) | 5 (excellent) |
|---|---|---|---|
| **Groundedness** | Does it cite real, specific facts from this run (days, event names, numbers) rather than generic phrasing? | Generic score-bucket language, could apply to any run | Cites specific days/events/numbers unique to this run |
| **Factual accuracy** | Are the cited facts actually correct per the JSON? | Contains fabricated or wrong numbers/events | Everything checked against the JSON is correct |
| **Two-part separation** | Does the descriptive part stay neutral/factual, and the evaluative part carry the judgment — without either bleeding into the other? | Judgment appears in the descriptive part, or vice versa | Clean separation, each part does its job |
| **Tone (evaluative part only)** | Is it encouraging/constructive even when results are mixed or weak? | Neutral, harsh, or fails to acknowledge weak results at all | Positive framing that still honestly engages with weak spots |
| **Coverage** | Does it touch on all four AIM axes, not just 1–2? | Only discusses 1–2 axes | All four represented, appropriately weighted by what mattered |
| **Conciseness** | Is it the right length (3–5 sentences per part), or does it ramble/pad? | Too long, repetitive, or too thin to be useful | Tight, every sentence earns its place |
| **Consistency** | Running the same log through the same model twice — does the output stay reasonably stable in content (not necessarily wording)? | Wildly different facts/conclusions each run | Same key facts and conclusions each run |
| **Fluency** | Natural, well-written English (and French, once tested)? | Awkward, robotic, or broken phrasing | Reads naturally |
| **Speed** | Wall-clock time for the 3-step generation on your hardware | Unusably slow for practical use | Fast enough for real-time end-of-session use |

