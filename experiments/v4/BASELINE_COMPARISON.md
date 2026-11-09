# Our Reports vs the Platform's Current Summaries

Side-by-side comparison for the 5 test sessions. The platform's texts are copied from each log (`final_metrics.game_story_text` and `text_summary`); ours are the final v4 reports (seed 42). The notes are a first reading, checked against the logs. **This is not yet a rating by independent readers**, and 5 sessions is a small sample.

## 1. Main observations

| | Platform (current) | Our pipeline (v4) |
|---|---|---|
| **Specific to this player's game** | No days, events or decisions | Days, event names, choices and costs |
| **Trends over the session** | No | Start and end of all four scores |
| **Reflects the strategy played** | No: nothing marks the two cost-minimization sessions as cost-cutting | Yes, through the listed decisions |
| **Agreement with the data** | Praise often ignores falling scores; day count off by one in 4 of 5 | Figures come from the log; some evaluation claims aren't supported by it |
| **Risk of invented claims** | None seen beyond the template's fixed wording | Yes: unsupported credit, garbled words, odd reasoning (see [REVIEW.md](REVIEW.md)) |
| **Readability** | Short, plain, addresses the player as "you" | About 2.7 times longer, more formal, says "the player" |
| **Repeated wording** | Fixed sentences reused across players | Same structure, and a stock opening in the evaluation |
| **French** | Already in the logs | Not built yet |

**Overall:** our description adds what the platform's summary lacks, which is what actually happened in this player's game. The evaluation is more mixed: it's more specific, but it can make claims the data doesn't support, while the platform's text is safe but generic and often too positive. Readers should decide which they prefer.

**Reused sentences in the platform's text (found by reading):**
- "The patient experience you provide is exemplary…" appears for Karina and Mark.
- "Health outcomes are respectable though unremarkable…" appears for Karina and Mark.
- "The patient experience meets basic expectations…" appears for Catherine and Jane.
- "You've achieved remarkable cost efficiency…" appears for Mark and Patrick.
- All five stories follow one template, including "0 staff members resigned, which is an impressive feat".

**Length in words (both parts together):**

| Player | Platform | Ours |
|---|---|---|
| Karina | 111 | 240 |
| Mark | 111 | 302 |
| Catherine | 112 | 311 |
| Jane | 113 | 299 |
| Patrick | 114 | 351 |
| **Average** | **112** | **301** |

**Something our reports miss:** actions players took outside the events don't appear, such as the nurse hire Karina started on Day 8 and the wellness program Mark bought on Day 13. Our description lists only event decisions. This should be fixed.

## 2. Financial figures: a question for the platform team

The platform and our reports don't always show the same numbers, because the log holds more than one version of them:

| Player | Balance change (end minus start) | Platform's "net gain" (`net_profit_loss`) | Gap |
|---|---|---|---|
| Karina | +$510,209 | §510k | 0 |
| Mark | +$97,237 | §97k | 0 |
| Catherine | +$498,801 | §498k | 0 |
| Jane | +$1,911,814 | §1843k ($1,843,814) | **$68,000** |
| Patrick | +$2,135,491 | §2134k ($2,134,491) | **$1,000** |

(Balance change here uses the last daily row, as the platform's story does.)

1. **The gain and the balance disagree for Jane and Patrick.** Each gap equals the locked cost of the event decisions whose policies were later deactivated:
   - Jane: $20,000 + $40,000 + $8,000 = $68,000 (her $25,000 decision has no deactivation record and isn't in the gap);
   - Patrick: $1,000;
   - the other three players have no deactivated policies and no gap.

   So those costs seem to count in `net_profit_loss` but not in the final balance. This fits all five logs, but the simulator code hasn't been checked, so it could be intended or a bug.
2. **Two sources for the end-of-run figures.** The platform's story uses the last daily row; our text uses `final_finance`, recorded slightly later. The difference is about $50 for four players. For Mark it is larger: $1,776,739 and 530 patients in the daily row, $1,785,655 and 531 patients in `final_metrics`. If both versions reached a player, the numbers would disagree.
3. **Currency symbol.** The platform's story uses §; event messages in the logs use $, and so do our reports.

**Questions:** Which balance and gain should players see? Is the day count (29 and 59 for 30- and 60-day sessions; Karina's older 21-day log shows 21) intended? Which currency symbol is right?

## 3. Session by session

### Karina: Tutorial (21 days)

| | Platform (current) | Our pipeline (v4, seed 42) |
|---|---|---|
| **What happened** | You completed the simulation in 21 days. Congratulations on successfully managing the hospital! Throughout the simulation, 0 staff members resigned, which is an impressive feat. You treated a total of 377 patients, with 302 (80.11%) treated successfully. By the end of the simulation, your hospital's finances stood at §1612k, which means a net gain of §510k. | Over the 21-day session, the hospital's balance went from $1,102,123 to $1,612,280 (+$510,157). In total, 377 patients were treated, 302 of them successfully (80.1%), and no staff members resigned. By the end of the run, cost reduction rose from 37.6 to 79.9, while staff wellbeing fell from 77.5 to 66.5, patient health fell from 75.0 to 60.1 and patient experience fell from 75.0 to 66.3. The largest score swings were a fall in patient experience from 83.0 to 69.0 between Day 3 and Day 5 and a rise in patient experience from 69.0 to 82.0 between Day 5 and Day 7. Key decisions were: on Day 15, at the event "Critical Equipment Failure", the player chose "Emergency Maintenance Program" (cost $25,000). |
| **What it means** | Your staff thrives at work, feeling valued, secure, and genuinely passionate about their roles. Health outcomes are respectable though unremarkable, showing competence without demonstrating clinical excellence. The patient experience you provide is exemplary, with individuals feeling genuinely cared for and valued. Financial stewardship is outstanding, with lean operations and smart investments creating lasting economic health. | The end of the session revealed a nuanced understanding of the complexities within hospital management, particularly in balancing financial health with patient care and staff wellbeing. The decision to implement an "Emergency Maintenance Program" in response to a "Critical Equipment Failure" demonstrates strategic thinking, which likely contributed to the hospital's financial improvement. However, this focus on immediate crisis management may have inadvertently impacted staff wellbeing, patient health, and patient experience, as these scores fell during the session. The absence of staff resignations suggests that the team remained committed despite these challenges, indicating a strong foundation of professional dedication. Looking ahead, these insights can be invaluable for continuous learning and improvement, fostering a resilient and patient-centered approach in hospital management. |

**Platform:**
- The figures match the log.
- "Your staff thrives at work, feeling valued, secure, and genuinely passionate", but staff wellbeing fell from 77.5 to 66.5.
- "The patient experience you provide is exemplary", but patient experience fell from 75.0 to 66.3.
- No mention of the Day 15 equipment failure.

**Ours:**
- Names the Day 15 event, the choice and its cost, and gives the direction of all four scores.
- The evaluation credits the $25,000 repair for the financial gain. Cost reduction was already 82.8 on Day 14, so the data doesn't support this.
- Leaves out the nurse hire Karina started on Day 8 (the log shows no activation day for it).

**Reviewer notes:** _(to fill in)_

### Mark: Post-pandemic, normal strategy (30 days)

| | Platform (current) | Our pipeline (v4, seed 42) |
|---|---|---|
| **What happened** | You completed the simulation in 29 days. Congratulations on successfully managing the hospital! Throughout the simulation, 0 staff members resigned, which is an impressive feat. You treated a total of 530 patients, with 400 (75.47%) treated successfully. By the end of the simulation, your hospital's finances stood at §1776k, which means a net gain of §97k. | Over the 30-day session, the hospital's balance went from $1,679,502 to $1,785,655 (+$106,153). In total, 531 patients were treated, 401 of them successfully (75.5%), and no staff members resigned. By the end of the run, cost reduction rose from 38.6 to 75.5, while staff wellbeing fell from 77.5 to 69.0, patient health fell from 75.0 to 60.6 and patient experience fell from 75.0 to 69.3. The largest score swings were a rise in cost reduction from 47.7 to 75.2 between Day 4 and Day 6 and a fall in patient experience from 95.6 to 72.1 between Day 4 and Day 8. Key decisions were: on Day 13, at the event "Talent War: Competitors Offering Sign-On Bonuses", the player chose "Competitive Retention Bonuses" (cost $337,500); on Day 21, at the event "Operational Efficiency Audit Results", the player took no action; on Day 27, at the event "Strategic Direction: Expand or Consolidate?", the player chose "Strategic Consolidation" (cost $62,500). |
| **What it means** | Your team demonstrates exceptional morale and engagement, creating a positive environment that attracts talent. Health outcomes are respectable though unremarkable, showing competence without demonstrating clinical excellence. The patient experience you provide is exemplary, with individuals feeling genuinely cared for and valued. You've achieved remarkable cost efficiency, turning tight budgets into opportunities for innovation and growth. | The end of the session reveals a nuanced understanding of the complexities involved in post-pandemic financial recovery within a hospital setting. The strategic choice to implement competitive retention bonuses, as indicated by the decision made during "Talent War: Competitors Offering Sign-On Bonuses," may have contributed positively to cost reduction, a critical aspect of the game'thy financial health. However, the lack of action in response to the "Operational Efficiency Audit Results" and the unused strategies such as counseling services and peer support present areas for potential growth and improvement. Notably, the decision to pursue "Strategic Consolidation" was made, which could have implications for the hospital's long-term sustainability and capacity to serve patients effectively. Looking ahead, the commitment to refining strategies and enhancing staff and patient support mechanisms promises a path to not only recover financially but also to foster a more robust and resilient healthcare environment. |

**Platform:**
- Says 29 days; the log records 30 completed.
- "exceptional morale and engagement", but staff wellbeing fell from 77.5 to 69.0 (no one resigned).
- "The patient experience you provide is exemplary", but patient experience fell from 75.0 to 69.3.
- No mention of the Talent War, the $337,500 bonuses or the consolidation.

**Ours:**
- Names all three event decisions with days and costs.
- The evaluation contains a garbled word ("game'thy") and credits the $337,500 bonuses for cost reduction, which had already reached 77.8 by Day 12.
- Leaves out the wellness program Mark bought on Day 13.

**Reviewer notes:** _(to fill in)_

### Catherine: Post-pandemic, cost-minimization (30 days)

| | Platform (current) | Our pipeline (v4, seed 42) |
|---|---|---|
| **What happened** | You completed the simulation in 29 days. Congratulations on successfully managing the hospital! Throughout the simulation, 0 staff members resigned, which is an impressive feat. You treated a total of 476 patients, with 348 (73.11%) treated successfully. By the end of the simulation, your hospital's finances stood at §2129k, which means a net gain of §498k. | Over the 30-day session, the hospital's balance went from $1,631,198 to $2,129,947 (+$498,749). In total, 476 patients were treated, 348 of them successfully (73.1%), and no staff members resigned. By the end of the run, cost reduction rose from 39.0 to 80.3, while staff wellbeing fell from 77.5 to 62.6, patient health fell from 75.0 to 57.0 and patient experience fell from 75.0 to 60.9. The largest score swings were a rise in patient health from 52.9 to 66.3 between Day 18 and Day 20 and a fall in patient experience from 74.0 to 48.5 between Day 20 and Day 22. Key decisions were: on Day 13, at the event "Talent War: Competitors Offering Sign-On Bonuses", the player chose "Hope for the Best"; on Day 21, at the event "Operational Efficiency Audit Results", the player chose "Minor Process Tweaks"; on Day 27, at the event "Strategic Direction: Expand or Consolidate?", the player chose "Maintain Current Scope". |
| **What it means** | Your workforce flourishes in a supportive atmosphere, exhibiting loyalty and enthusiasm that inspires excellence. Clinical outcomes are generally satisfactory, with occasional lapses in quality that could be addressed. The patient experience meets basic expectations but falls short of creating truly memorable positive interactions. Operations run efficiently with excellent resource utilization, minimal waste, and strong financial sustainability. | The end of the session reveals a nuanced understanding of the complexities involved in post-pandemic financial recovery within a hospital setting. The decision to "Hope for the Best" in the face of competitors offering sign-on bonuses demonstrates a cautious optimism, which, while not directly influencing the financial outcome, underscores a strategic restraint that may have contributed to maintaining the hospital's financial stability. The choice to implement only "Minor Process Tweaks" in response to the Operational Efficiency Audit Results suggests a focus on incremental improvements, which could be a stepping stone for more significant advancements in the future. Notably, the scores on staff wellbeing, patient health, and patient experience all fell, highlighting areas that require attention and possibly more innovative approaches. Looking ahead, these insights present a valuable foundation for developing more comprehensive strategies that not only bolster financial health but also elevate the quality of care provided to patients and the work environment for staff. |

**Platform:**
- Says 29 days; the log records 30 completed.
- "Your workforce flourishes in a supportive atmosphere, exhibiting loyalty and enthusiasm", but staff wellbeing fell from 77.5 to 62.6, and she declined the retention bonuses.
- "Operations run efficiently" fits her cost reduction score (39.0 to 80.3).
- Nothing shows that this was a cost-cutting strategy.

**Ours:**
- Names her three choices, so the strategy is visible.
- "Hope for the Best" is hard to understand without knowing it means refusing retention bonuses.
- The evaluation is generous about the refusal ("cautious optimism", "strategic restraint").

**Reviewer notes:** _(to fill in)_

### Jane: Winter flu, normal strategy (60 days)

| | Platform (current) | Our pipeline (v4, seed 42) |
|---|---|---|
| **What happened** | You completed the simulation in 59 days. Congratulations on successfully managing the hospital! Throughout the simulation, 0 staff members resigned, which is an impressive feat. You treated a total of 1198 patients, with 885 (73.87%) treated successfully. By the end of the simulation, your hospital's finances stood at §5263k, which means a net gain of §1843k. | Over the 60-day session, the hospital's balance went from $3,351,685 to $5,263,446 (+$1,911,762). In total, 1,198 patients were treated, 885 of them successfully (73.9%), and no staff members resigned. By the end of the run, cost reduction rose from 39.0 to 81.4, while staff wellbeing fell from 77.5 to 59.1, patient health fell from 75.0 to 60.2 and patient experience fell from 75.0 to 60.2. The largest score swings were a fall in patient experience from 69.3 to 59.7 between Day 15 and Day 18 and a fall in patient experience from 69.5 to 56.0 between Day 49 and Day 51. Key decisions were: on Day 6, at the event "Emergency Flu Vaccine Shipment Available", the player chose "Purchase Vaccines for High-Risk Staff Only" (cost $20,000); on Day 13, at the event "Breaking Point: Staff Exhaustion Reaches Critical Levels", the player chose "Overtime Bonuses + Extended Breaks" (cost $40,000); on Day 31, at the event "Midpoint Review: Operational Lessons Learned", the player chose "Basic Process Improvements" (cost $25,000). |
| **What it means** | Your team copes with daily pressures reasonably well, though they'd benefit from additional support and recognition. Most patients receive acceptable care, though some experience delays or suboptimal treatment quality. The patient experience meets basic expectations but falls short of creating truly memorable positive interactions. Your facility demonstrates exemplary cost management, maximizing value while maintaining high-quality service delivery. | The end-of-session report underscores a period of financial acumen and strategic decision-making amidst the Winter Flu Crisis, with the hospital concluding the scenario with an increased budget. The significant rise in cost reduction scores can be partly attributed to the strategic decision to purchase flu vaccines for high-risk staff, as noted when the player chose "Purchase Vaccines for High-Risk Staff Only." This choice, while potentially enhancing the hospital's financial position, may have had complex implications for staff wellbeing, patient health, and patient experience, with the latter two scores experiencing a downturn. Despite the critical exhaustion levels faced by staff, the decision to offer overtime bonuses and extended breaks, as chosen when confronted with "Staff Exhaustion Reaches Critical Levels," likely provided some relief and could have indirectly influenced the patient experience positively. |

**Platform:**
- Says 59 days; the log records 60 completed.
- Says a gain of §1843k, while the balance in the log rose by about 1,912k (see section 2).
- The most honest of the five summaries: "copes with daily pressures reasonably well, though they'd benefit from additional support".
- No mention of the flu, the vaccines or the staff exhaustion event.

**Ours:**
- Names three flu decisions with days and costs.
- The evaluation states as fact that the cost reduction rise "can be partly attributed to" the vaccine purchase. Cost reduction was already 80.6 on Day 5, before the decision.
- The evaluation has no forward-looking closing sentence.

**Reviewer notes:** _(to fill in)_

### Patrick: Winter flu, cost-minimization (60 days)

| | Platform (current) | Our pipeline (v4, seed 42) |
|---|---|---|
| **What happened** | You completed the simulation in 59 days. Congratulations on successfully managing the hospital! Throughout the simulation, 0 staff members resigned, which is an impressive feat. You treated a total of 1177 patients, with 869 (73.83%) treated successfully. By the end of the simulation, your hospital's finances stood at §5471k, which means a net gain of §2134k. | The hospital's balance moved from $3,335,792 to $5,471,230 (+$2,135,438) during the 60-day simulation. Of the 1,177 patients treated, 869 were treated successfully (73.8%), and no staff members resigned. Across the four scores, cost reduction rose from 39.0 to 82.2, whereas staff wellbeing fell from 77.5 to 57.7, patient health fell from 75.0 to 53.9 and patient experience fell from 75.0 to 66.6. Notable score swings included a fall in patient health from 69.9 to 54.1 between Day 3 and Day 9 and a rise in cost reduction from 65.9 to 79.6 between Day 8 and Day 12. The player's decisions included: on Day 6, at the event "Emergency Flu Vaccine Shipment Available", the player chose "Decline - Hope Natural Immunity Builds"; on Day 13, at the event "Breaking Point: Staff Exhaustion Reaches Critical Levels", the player chose "Provide Pizza Parties + Recognition Only"; on Day 21, at the event "Staff Recovery: How Fast Should They Return?", the player chose "Accelerated Return: Get Everyone Back ASAP" (cost $1,000). |
| **What it means** | Staff wellbeing hovers at an acceptable level, with room for enhancement through targeted interventions. Treatment quality is adequate for routine cases but struggles with complex situations requiring advanced care. Patients consistently praise the exceptional attention to their needs, comfort, and dignity throughout their care. You've achieved remarkable cost efficiency, turning tight budgets into opportunities for innovation and growth. | In the concluding analysis of the Winter Flu Crisis scenario, the players demonstrated a commendable financial acumen, leading to an increase in the hospital's funds by the end of the simulation. The decision to "Decline - Hope Natural Immunity Builds" regarding the Emergency Flu Vaccine Shipment Available may have inadvertently contributed to a decline in patient health scores, presenting a learning opportunity for more proactive health measures in future engagements. The choice to "Provide Pizza Parties + Recognition Only" in response to "Breaking Point: Staff Exhaustion Reaches Critical Levels" might not have fully rejuvenated staff wellbeing, suggesting that future strategies could benefit from a more holistic approach to staff morale. Opting for an "Accelerated Return: Get Everyone Back ASAP" when contemplating "Staff Recovery: How Fast Should They Return?" underscores the players' focus on operational continuity, yet it may have overlooked the nuanced needs of staff recuperation, offering a valuable insight for subsequent scenarios. Looking ahead, the players are encouraged to integrate these experiences into their future simulations, aiming to enhance patient health, staff wellbeing, and financial stability while maintaining a high level of care. |

**Platform:**
- Says 59 days; the log records 60 completed.
- "Patients consistently praise the exceptional attention to their needs, comfort, and dignity", but patient experience fell from 75.0 to 66.6, and patient health fell to 53.9, the lowest of the five.
- Nothing shows that he declined the vaccines or answered staff exhaustion with pizza parties.

**Ours:**
- The clearest gain over the platform: it names the declined vaccines, the pizza parties and the accelerated return.
- The evaluation links the declined vaccines to falling patient health, using hedged wording.
- Wording issue: "the players" for one player.

**Reviewer notes:** _(to fill in)_
