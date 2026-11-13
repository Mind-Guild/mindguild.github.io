# Ten-minute protocol close

Study ID:  
Meeting/date/timezone:  
Recorder and source version:  
Decision owner(s):

## Readback

| Minutes | Prompt | Capture in v3 |
| --- | --- | --- |
| 0–2 | Which one claim are we testing first? What is outside this study? | Hypothesis ID; construct, operational definition, and conclusion limits in `claim_measure_map`. |
| 2–4 | What manipulation and control distinguish the mechanism from our strongest alternative? Is the result directly encoded by our design? | Component IDs, comparator, rival/control/result rows, encoded-effect interpretation. |
| 4–6 | What number will we plot? What results support, challenge, or leave the claim unresolved? | Common estimand, both accounts' quantitative regions, and target-only/rival-only/both/neither/inconclusive/invalid interpretations; leave unsupplied thresholds open. |
| 6–8 | What is built, demonstrated, or planned? What learns? What have we already seen? | `components`, `learning`, and `results_access`. Keep offline calibration, runtime state changes, and parameter updates separate. |
| 8–10 | What is agreed, proposed, or unresolved? Who supplies missing artifacts and numerical choices? | Per-field `provenance`, open-decision owners, artifact handoff, and critical-review responsibilities. Schedule the results-blind contract review. |

## Artifact handoff

Record a disposition for code, config, environment, scenario manifest, input traces, equations, slides, and chat. Core code/config/environment/scenario artifacts need captured locations and pins. Document unavailable or inapplicable supporting artifacts with reasons. Retain the exact input schedule used for any demonstration when available.

## Results-access declaration

What results or demonstrations exist?  
Who has seen them, and when?  
Which conditions/runs did they involve?  
How did they influence design or tuning?  
What exact runs/conditions remain unobserved?  
Who confirms this disclosure, and when?

## Current decision record

| Field path | Status | Evidence and locator | Original speaker attribution | Actual decision owner / written decision record | Next step |
| --- | --- | --- | --- | --- | --- |
| | decided / proposed / deferred / rejected / not_recorded | | identified / unresolved / not_applicable | | |

Unresolved speaker attribution is preserved. A named owner can subsequently accept a decision in a written follow-up without retroactively identifying the original speaker. Analyst proposals require explicit adoption evidence. Numerical decisions can be completed after the meeting by named owners before review and registration.

## Follow-up before freeze

Use [severe_test_review.md](severe_test_review.md) to examine the level of claim, bridge assumptions, competing predictions, sensitivity evidence, conflicts and actual perspective acceptance, analysis masking, replication, and reporting. The meeting close assigns this work; it does not certify a severe test or invent agreement.
