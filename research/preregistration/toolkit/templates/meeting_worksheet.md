# Research working meeting: decision worksheet

Study ID:  
Date and timezone:  
Facilitator / recorder:  
Participants:  
Transcript or notes location / version:  
Relevant prior pilots, data, results, and who has seen them:

## Claim and evidence chain

Plain-language claim:  
Why this task can discriminate between explanations:  
Alternative explanation / shortcut solution:  
Primary hypothesis ID and directional prediction:  
Manipulated mechanism and comparator:  
Primary condition / test population:  
Primary observable, units, and exact scoring formula:  
Independent unit of replication:  
Estimator and uncertainty procedure:  
Meaningful-effect threshold and justification:  
Evidence supporting / challenging / leaving the hypothesis unresolved:  
Scope of conclusion:

Directly encoded effect, or a prediction that could discriminate mechanisms?  
Alternative/control/result entries for `claim_measure_map`:  
Components included now, future components excluded, and implementation/evidence status:  
Offline calibration / within-run state dynamics / online parameter updates:  
For each active learning phase: parameters, rule, objective, teaching signal, timing, evaluation policy:

## Generator, models, and execution

Generator equations and parameter distributions:  
Factors, levels, constants, and factorial combinations:  
Observation / action / reward interfaces, if applicable:  
Train / validation / confirmatory split rule and leakage checks:  
Architectures, baselines, ablations, and tuning budgets:  
Checkpoint / early stopping rule:  
Independent repetitions and count justification:  
Episodes per condition and aggregation:  
Pilot / confirmatory seed namespaces:  
Compute budget and completion/interruption rule:  
Crashes, retries, nonconvergence, exclusions, and missing outcomes:  
Code, environment, and scenario manifest versions:

## Artifact and results-access handoff

Captured/requested/unavailable/inapplicable status for code, config, environment, scenario manifest, input traces, equations, slides, and chat:  
Artifact locations and hashes/immutable versions:  
Handoff confirmation owner/date:  
Previous results/demonstrations, who saw them and when, conditions, and influence on design:  
Reserved unobserved runs/conditions and access controls:  
Registration scope: new simulation runs / analysis of existing uninspected outputs:  
Actual results-access declaration owner/date:

## Expected figures and interpretation

Predicted figure axes / series / uncertainty bars:  
Expected ordering and interaction:  
Negligible-effect region, if using equivalence:  
Multiplicity or testing order:  
Secondary outcomes:  
Exploratory questions:  
Sanity checks and measurement-invalidity criteria:

## Decision ledger

Use `decided`, `proposed`, `deferred`, or `rejected`. Agreement requires explicit evidence. Preserve disagreement instead of selecting the most fluent statement.

| ID | Protocol field | Decision or proposal | Status | Speaker + timestamp or note line | Owner | Resolution method / due date |
| --- | --- | --- | --- | --- | --- | --- |
| D001 | | | | | | |

Transfer current decisions into `provenance` using field paths. Capture origin, source ID and locator, original speaker attribution, actual decision owner/record, and the current value digest. Keep unknown speakers unresolved. Do not mark an analyst proposal decided without explicit adoption evidence.

## Readback before closing

- Primary hypothesis, outcome, contrast, and independent unit read aloud:
- Unresolved scientific and numerical decisions assigned:
- Pilot work and already-seen results disclosed:
- Implementation, analysis, and review responsibilities assigned:
- Draft OSF title, contributors, and public/embargoed preference captured:

The meeting need not produce a submit-ready registration. Its output must make the remaining decisions explicit and actionable.

Use `templates/protocol_close.md` for the final ten-minute readback and artifact handoff.


## V3 test-contract handoff

Record whether the candidate is a mechanism benchmark or a theory-discrimination study. Identify the strongest account alternative, the same-estimand quantitative predictions if actually decided, all six outcome interpretations, bridge assumptions, and the owner of the results-blind review in [severe_test_review.md](severe_test_review.md). Keep numerical decisions, sensitivity evidence, and perspective approvals unresolved when absent from the meeting.
