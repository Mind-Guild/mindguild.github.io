# Persistent object representations and identity-location binding through occlusion

**Local review packet. This document is not an OSF registration.**

Study ID: MG-OCC-001  
Mechanical readiness: BLOCKED  
Review digest: `f26a0df206dbb8b668b2e9930ad7ccc4609102cc1c8d65b9696286c2be544abb`

## Metadata

```json
{
  "description": "Proposed simulation comparing object-centric and global recurrent predictive models on target localization through occlusion, including held-out color-motion combinations. All numerical and implementation commitments require review before registration.",
  "contributors": [
    {
      "name": "Kevin Schmidt",
      "profile_url": "https://osf.io/user/zryq5"
    }
  ],
  "license": null,
  "subjects": [],
  "tags": [
    "Mind Guild",
    "simulation",
    "object binding",
    "occlusion",
    "compositional generalization"
  ],
  "public_or_embargoed": null,
  "embargo_end_date": null
}
```

## Prior work and outcome access

**MISSING — decision required**

**MISSING — decision required**

## Aims — research questions and hypotheses

Estimate whether persistent object-centric representations improve identity-conditioned localization after occlusion, and whether any advantage extends to held-out color-motion combinations. This is a bounded functional test; it does not establish subjective experience.

### Explicit hypothesis records

```json
[
  {
    "id": "H1",
    "classification": "primary",
    "status": "proposed",
    "statement": "A persistent object-centric predictive model has higher identity-conditioned localization accuracy than a comparable global recurrent model in the occluded, held-out condition.",
    "contrast": "M1 minus M2; occluded visibility and held-out color-motion combinations.",
    "outcome": "Identity-conditioned localization accuracy, aggregated first within each independent training/evaluation block.",
    "analysis": null,
    "interpretation_rule": null,
    "source_record_ids": [
      "S1",
      "S2",
      "S3"
    ]
  }
]
```

## Data-generating mechanism — parameters

PROPOSED: a controlled 2D generator with two differently colored balls. Cue the target color before occlusion. At a fixed registered query time, each model predicts the target's 2D position from permitted observations. UNRESOLVED: physics, numeric parameter distributions, timestep, rendering, query time, occluder geometry, target/distractor separation rules, and observation schema.

## Data-generating mechanism — varied factors

PROPOSED: visibility (occluded / continuously visible) and combination split (seen / held-out color-motion combinations). Models are comparison methods, not additional generator factors. UNRESOLVED: exact factor levels and whether motions include more than bouncing.

## Data-generating mechanism — values and constants

UNRESOLVED: enumerate colors, speeds, trajectories, bounce physics, episode lengths, occlusion durations, object sizes, nuisance variables, and numeric constants.

## Data-generating mechanism — combinations and condition count

PROPOSED: 2 visibility levels x 2 combination-split levels = 4 evaluation conditions per method. The primary contrast uses the occluded, held-out condition. Three candidate methods would yield 12 method-condition cells, not 12 independent model fits per block. UNRESOLVED: accept/revise methods and exact scenario manifest.

## Estimands and targets

PROPOSED primary estimand: expected full-minus-global-baseline localization-accuracy difference in the occluded, held-out condition, over the registered independent training/evaluation blocks. Secondary descriptive targets: visible-control accuracy, identity swap frequency, and performance loss under the binding ablation.

## Included methods and extracted quantities

PROPOSED: (M1) persistent object-centric recurrent predictive model, (M2) global recurrent predictive model, and (M3) ablation that disrupts persistent object binding. Supply the same permitted observations and comparable data/training/tuning budgets. Extract per-episode predicted target position, ground truth for scoring only, and per-run success/failure. UNRESOLVED: exact models, trainable capacity, forward model, use of SF, hyperparameters, and checkpoint rule.

## Performance measures

PROPOSED: per-episode identity-conditioned localization success = 1 if the Euclidean target-position error is within a fixed tolerance and the prediction is strictly closer to the target than to the distractor; else 0. Average episodes within condition and block, then take the registered across-block estimator. UNRESOLVED: tolerance, missing predictions, ties, ambiguous configurations, and exact secondary scoring.

## Handling Monte Carlo uncertainty

PROPOSED: paired analysis over independently generated training/evaluation blocks, with an evaluation panel shared across methods within each block and independently generated across blocks. UNRESOLVED: validate the pairing and specify the confidence interval algorithm, confidence level, any resample count, and analysis RNG seed.

## Number of simulation repetitions — rationale

UNRESOLVED: choose independent repetition count using disclosed pilot variability, target interval precision or power, and compute budget. Fix evaluation episodes separately. Do not count frames or episodes from one model as independent model replications.

## Missing values and nonconvergence

UNRESOLVED: distinguish infrastructure crashes, generator/scoring bugs, numerical nonconvergence, and valid low-performing models. Set retry cap, resume policy, failure outcome treatment, missing-pair handling, and interruption rule before confirmatory execution.

## Interpretation and analysis of performance measures

PROPOSED: estimate H1's full-minus-baseline difference with a prespecified interval. Define the minimum meaningful benefit before registration. Treat visible-control and binding-ablation comparisons as descriptive/exploratory unless explicitly promoted and given a multiplicity plan. UNRESOLVED: numerical threshold and exact support/challenge/inconclusive rules.

## Statistical software and packages

UNRESOLVED: selected framework, exact versions, dependency lockfile, generator, training, and analysis packages.

## Planned computational environment

UNRESOLVED: CPU/GPU, OS, accelerator libraries, precision/determinism settings, memory, and expected compute.

## Reproducibility measures

PROPOSED: archive frozen code/config/splits with hashes, all run statuses, scoring outputs, analysis outputs, and deviation logs; link the resulting research outputs to the OSF registration. UNRESOLVED: repository and artifact release plan.

## Additional notes for preregistration

No meeting transcript was supplied for this example. Every design choice here is a proposal for review. Confirm actual pilot/outcome exposure before registration. Keep novel dynamics composition and reward transfer as separately specified follow-on claims.

## Structured scientific records (schema v2)

These records supplement the OSF form. Mechanical validation checks declared decisions and consistency; scientific adequacy and actual agreement remain human responsibilities.

### Claim-to-measure map: H1

| Decision | Specification |
| --- | --- |
| construct | Persistent identity-location binding through occlusion |
| operational definition | Predict the cued object location after occlusion while distinguishing the distractor. |
| metric definition | UNRESOLVED: choose the localization tolerance, query time, ties, invalid-output treatment, and episode scoring. |
| estimand | Proposed full-minus-global-baseline mean accuracy difference in the occluded held-out condition across independent blocks. |
| mechanism | Persistent object-specific recurrent representations for target identity and motion. |
| manipulation | Proposed comparison of full, global recurrent, and disrupted-binding models under matched observations. |
| comparator | UNRESOLVED: match training, tuning, and capacity budgets and specify remaining model differences. |
| conclusion scope | A functional binding/generalization claim under the declared generator. |
| inference limits | An advantage alone would not establish phenomenal experience or novel-dynamics composition. |
| component IDs | ["M1", "M2", "M3"] |
| directly encoded effect | Missing |
| interpretation of encoded effect | Missing |

| Rival explanation | Discriminating control | Distinguishing result |
| --- | --- | --- |
| Additional capacity or tuning rather than persistent binding. | Match capacity and tuning budgets and include the binding ablation. | A binding-specific advantage must survive the matched comparison; exact decision rule remains to be chosen. |

Expected result patterns: {"support": "UNRESOLVED: select the meaningful-effect threshold and interval criterion.", "challenge": "A precise reversed or practically negligible effect under prespecified criteria would challenge the prediction.", "inconclusive": "Uncertainty spanning meaningful benefit and negligible/adverse outcomes."}

### Component status

| ID / component | Implementation | Evidence | Included? | Artifacts / sources |
| --- | --- | --- | --- | --- |
| M1 / Persistent object-centric predictive model | analyst_proposed | not_demonstrated | True | {"artifacts": [], "sources": ["S4"]} |
| M2 / Global recurrent predictive comparator | analyst_proposed | not_demonstrated | True | {"artifacts": [], "sources": ["S4"]} |
| M3 / Persistent-binding ablation | analyst_proposed | not_demonstrated | True | {"artifacts": [], "sources": ["S4"]} |

### Calibration, state dynamics, and learning

| Phase | Declaration |
| --- | --- |
| offline calibration | {"enabled": true, "parameters": ["encoder parameters", "predictive model parameters"], "method": "UNRESOLVED: specify training rule and objective.", "data_and_selection": "UNRESOLVED: training/validation manifests and tuning selection.", "freeze_point": "UNRESOLVED: choose the checkpoint before confirmatory evaluation."} |
| within run state | {"enabled": true, "state_variables": ["object slots or global recurrent state"], "update_rule": "UNRESOLVED: exact model-specific state transition equations.", "memory_role": "Proposed preservation of identity and predicted position across occlusion."} |
| online updates | {"enabled": false, "parameters": [], "rule": null, "signal_type": null, "signal_definition": null, "objective": null, "schedule": null, "evaluation_update_policy": null} |

### Artifact handoff

| ID / kind | Status | Location | Pin | Owner / reason |
| --- | --- | --- | --- | --- |
| A_code / code | requested | Missing | Missing | {"owner": null, "reason": null} |
| A_config / config | requested | Missing | Missing | {"owner": null, "reason": null} |
| A_environment / environment | requested | Missing | Missing | {"owner": null, "reason": null} |
| A_scenario_manifest / scenario_manifest | requested | Missing | Missing | {"owner": null, "reason": null} |
| A_input_traces / input_traces | requested | Missing | Missing | {"owner": null, "reason": null} |
| A_equations / equations | requested | Missing | Missing | {"owner": null, "reason": null} |
| A_slides / slides | requested | Missing | Missing | {"owner": null, "reason": null} |
| A_chat / chat | requested | Missing | Missing | {"owner": null, "reason": null} |

Handoff confirmation: {"confirmed_by": null, "confirmed_at_utc": null}

### Prior results and prospective boundary

| Declaration | Value |
| --- | --- |
| declaration status | incomplete |
| declared by | Missing |
| declared at utc | Missing |
| registration scope | new_simulation_runs |
| confirmatory status | Missing |
| prospective scope | PROPOSED: new model/scenario runs reserved after registration. |
| reserved runs or conditions | Missing |
| access controls | Missing |

No-prior-results explanation: Missing

### Per-field provenance

The full decision ledger includes current value digests in `decision_ledger.csv`. Unknown speakers remain unresolved; proposals require explicit adoption.

| Field | Decision / origin | Source / locator | Speaker attribution | Decision owner |
| --- | --- | --- | --- | --- |
| /prior_work_disclosure | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /outcome_access_before_registration | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /sections/aims | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/data_generating_parameters | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/varied_factors | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/factor_values_and_constants | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/factor_combinations_and_condition_count | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/estimands_and_targets | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/methods_and_extracted_quantities | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/performance_measures | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/monte_carlo_uncertainty | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/repetition_count_rationale | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/missingness_and_nonconvergence | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /sections/interpretation_and_analysis | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /execution/independent_unit | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /execution/n_independent_repetitions | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/evaluation_episodes_per_condition | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/pilot_seed_blocks | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/confirmatory_seed_blocks | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/rng_stream_derivation | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/training_budget | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/hyperparameter_selection | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/checkpoint_selection | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/stopping_rule | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/failure_rule | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /execution/test_access_rule | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /hypotheses/0/statement | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /hypotheses/0/contrast | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /hypotheses/0/outcome | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /hypotheses/0/analysis | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /hypotheses/0/interpretation_rule | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /claim_measure_map/0/construct | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/operational_definition | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/metric_definition | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/estimand | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/mechanism | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/manipulation | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/comparator | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/conclusion_scope | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/inference_limits | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/component_ids | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/rival_explanations | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/expected_result_patterns | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /claim_measure_map/0/directly_encoded_effect | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /components/0/mechanism | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/0/implementation_status | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/0/evidence_status | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/0/included_in_study | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/0/artifact_ids | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /components/1/mechanism | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/1/implementation_status | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/1/evidence_status | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/1/included_in_study | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/1/artifact_ids | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /components/2/mechanism | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/2/implementation_status | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/2/evidence_status | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/2/included_in_study | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /components/2/artifact_ids | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /learning/offline_calibration/enabled | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /learning/offline_calibration/parameters | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /learning/offline_calibration/method | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /learning/offline_calibration/data_and_selection | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /learning/offline_calibration/freeze_point | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /learning/within_run_state/enabled | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /learning/within_run_state/state_variables | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /learning/within_run_state/update_rule | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /learning/within_run_state/memory_role | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /learning/online_updates/enabled | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /artifact_handoff/items | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /results_access/prior_results | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /results_access/registration_scope | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /results_access/confirmatory_status | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /results_access/prospective_scope | proposed / analyst_proposal | ["S4"] / v2 worked-example proposal; no adoption recorded | not_applicable / None | Missing |
| /results_access/reserved_runs_or_conditions | not_recorded / not_recorded | [] / None | unresolved / None | Missing |
| /results_access/access_controls | not_recorded / not_recorded | [] / None | unresolved / None | Missing |


## Execution plan

```json
{
  "independent_unit": "PROPOSED: one independently generated block containing a training run per method and an independent evaluation panel shared only within that block.",
  "n_independent_repetitions": null,
  "evaluation_episodes_per_condition": null,
  "pilot_seed_blocks": [],
  "confirmatory_seed_blocks": [],
  "rng_stream_derivation": null,
  "training_budget": null,
  "hyperparameter_selection": null,
  "checkpoint_selection": null,
  "stopping_rule": null,
  "failure_rule": null,
  "test_access_rule": "PROPOSED: use only disclosed pilots and validation for selection; freeze and register before confirmatory training/evaluation; keep confirmatory combinations out of training, validation, tuning, and probe fitting.",
  "run_command": null,
  "analysis_command": null
}
```

## Pinned artifacts

```json
{
  "code_repository_url": null,
  "code_commit_sha": null,
  "scenario_manifest_sha256": null,
  "environment_lock_sha256": null
}
```

## Implementation evidence

```json
{
  "generator_properties": null,
  "split_leakage_check": null,
  "metric_synthetic_cases": null,
  "full_dry_run": null
}
```

## Source records

```json
[
  {
    "id": "S1",
    "location": "paper outline 20261106.docx; sections on object-centric encapsulation, task, and metrics",
    "what_it_supports": "Motivation for stable object features, transferable operators, successor features, and observable representations. Does not settle the concrete design."
  },
  {
    "id": "S2",
    "location": "Draft Position Paper 20261104.docx; opening sections through the central claim",
    "what_it_supports": "Theoretical motivation and scope; broad decompositionality and qualia claims. Does not finalize sample size or analysis."
  },
  {
    "id": "S3",
    "location": "Kevin's recent direction: object-occlusion bouncing-ball color/object/location binding task",
    "what_it_supports": "Starting task family; specific implementation below is a proposal."
  },
  {
    "id": "S4",
    "location": "Schema v2 worked example, 12 November 2026; analyst-authored design proposals",
    "what_it_supports": "The structured additions below illustrate capture. They are not meeting agreements or implementation evidence."
  }
]
```

## Review attestations

```json
{
  "science": {
    "reviewer_name": null,
    "approved": false,
    "reviewed_at_utc": null,
    "review_digest": null,
    "notes": null
  },
  "implementation": {
    "reviewer_name": null,
    "approved": false,
    "reviewed_at_utc": null,
    "review_digest": null,
    "notes": null
  },
  "analysis": {
    "reviewer_name": null,
    "approved": false,
    "reviewed_at_utc": null,
    "review_digest": null,
    "notes": null
  }
}
```

## Open decisions

```json
[
  {
    "id": "D1",
    "decision": "Approve the narrow hypothesis and choose primary outcome/condition/meaningful-effect threshold.",
    "owner": null
  },
  {
    "id": "D2",
    "decision": "Finalize numeric generator, allowed observations, scoring, and split manifest.",
    "owner": null
  },
  {
    "id": "D3",
    "decision": "Select exact predictive architectures, forward model, ablation, training/tuning budgets, and checkpoint rule.",
    "owner": null
  },
  {
    "id": "D4",
    "decision": "Disclose all prior work/results, run feasibility pilots, choose independent repetitions and inference.",
    "owner": null
  },
  {
    "id": "D5",
    "decision": "Specify failures, stopping, random streams, exact commands, and reproducibility artifacts.",
    "owner": null
  },
  {
    "id": "D6",
    "decision": "Confirm title, coauthors/order, license, subjects, public or embargoed status, and reviews.",
    "owner": null
  },
  {
    "id": "V2_CAPTURE",
    "decision": "Complete the v2 structured records and renew the three reviews.",
    "owner": null
  }
]
```

## Mechanical blockers

- status: use approved_for_freeze only after resolving and reviewing the plan
- metadata.license: supply a nonempty, specific value
- prior_work_disclosure: supply a nonempty, specific value
- outcome_access_before_registration: supply a nonempty, specific value
- metadata.subjects: supply a nonempty list
- metadata.public_or_embargoed: choose public or embargoed
- sections.data_generating_parameters: resolve proposed or placeholder content
- sections.varied_factors: resolve proposed or placeholder content
- sections.factor_values_and_constants: resolve proposed or placeholder content
- sections.factor_combinations_and_condition_count: resolve proposed or placeholder content
- sections.methods_and_extracted_quantities: resolve proposed or placeholder content
- sections.performance_measures: resolve proposed or placeholder content
- sections.monte_carlo_uncertainty: resolve proposed or placeholder content
- sections.repetition_count_rationale: resolve proposed or placeholder content
- sections.missingness_and_nonconvergence: resolve proposed or placeholder content
- sections.interpretation_and_analysis: resolve proposed or placeholder content
- sections.software_and_packages: resolve proposed or placeholder content
- sections.computational_environment: resolve proposed or placeholder content
- sections.reproducibility_measures: resolve proposed or placeholder content
- hypotheses[0]: statement has not been marked decided
- hypotheses[0].analysis: supply resolved, specific text
- hypotheses[0].interpretation_rule: supply resolved, specific text
- execution.independent_unit: resolve proposed or placeholder content
- execution.rng_stream_derivation: supply a nonempty, specific value
- execution.training_budget: supply a nonempty, specific value
- execution.hyperparameter_selection: supply a nonempty, specific value
- execution.checkpoint_selection: supply a nonempty, specific value
- execution.stopping_rule: supply a nonempty, specific value
- execution.failure_rule: supply a nonempty, specific value
- execution.test_access_rule: resolve proposed or placeholder content
- execution.run_command: supply a nonempty, specific value
- execution.analysis_command: supply a nonempty, specific value
- execution.n_independent_repetitions: supply an integer of at least 2, justified by the analysis
- execution.evaluation_episodes_per_condition: supply a positive integer
- execution.confirmatory_seed_blocks: length must equal the independent repetition count
- artifacts.code_repository_url: supply a nonempty, specific value
- artifacts.code_commit_sha: supply a full 40- or 64-hex commit ID
- artifacts.scenario_manifest_sha256: supply a 64-hex SHA-256 digest
- artifacts.environment_lock_sha256: supply a 64-hex SHA-256 digest
- quality_evidence.generator_properties: supply a nonempty, specific value
- quality_evidence.split_leakage_check: supply a nonempty, specific value
- quality_evidence.metric_synthetic_cases: supply a nonempty, specific value
- quality_evidence.full_dry_run: supply a nonempty, specific value
- open_decisions: resolve the list before freeze
- artifact_handoff.items[0].reason: supply resolved, specific text
- artifact_handoff.items[0].owner: supply resolved, specific text
- artifact_handoff.items[0]: requested capture is still open
- artifact_handoff.items[1].reason: supply resolved, specific text
- artifact_handoff.items[1].owner: supply resolved, specific text
- artifact_handoff.items[1]: requested capture is still open
- artifact_handoff.items[2].reason: supply resolved, specific text
- artifact_handoff.items[2].owner: supply resolved, specific text
- artifact_handoff.items[2]: requested capture is still open
- artifact_handoff.items[3].reason: supply resolved, specific text
- artifact_handoff.items[3].owner: supply resolved, specific text
- artifact_handoff.items[3]: requested capture is still open
- artifact_handoff.items[4].reason: supply resolved, specific text
- artifact_handoff.items[4].owner: supply resolved, specific text
- artifact_handoff.items[4]: requested capture is still open
- artifact_handoff.items[5].reason: supply resolved, specific text
- artifact_handoff.items[5].owner: supply resolved, specific text
- artifact_handoff.items[5]: requested capture is still open
- artifact_handoff.items[6].reason: supply resolved, specific text
- artifact_handoff.items[6].owner: supply resolved, specific text
- artifact_handoff.items[6]: requested capture is still open
- artifact_handoff.items[7].reason: supply resolved, specific text
- artifact_handoff.items[7].owner: supply resolved, specific text
- artifact_handoff.items[7]: requested capture is still open
- artifact_handoff: capture the core code artifact
- artifact_handoff: capture the core config artifact
- artifact_handoff: capture the core environment artifact
- artifact_handoff: capture the core scenario_manifest artifact
- artifact_handoff.confirmed_by: supply resolved, specific text
- artifact_handoff.confirmed_at_utc: supply a timezone-aware confirmation time
- components[0]: a confirmatory component must be implemented before freeze
- components[0].artifact_ids: supply a nonempty list
- components[1]: a confirmatory component must be implemented before freeze
- components[1].artifact_ids: supply a nonempty list
- components[2]: a confirmatory component must be implemented before freeze
- components[2].artifact_ids: supply a nonempty list
- claim_measure_map[0].metric_definition: supply resolved, specific text
- claim_measure_map[0].comparator: supply resolved, specific text
- claim_measure_map[0].expected_result_patterns.support: supply resolved, specific text
- claim_measure_map[0].directly_encoded_effect: explicitly choose true or false
- learning.offline_calibration.method: supply resolved, specific text
- learning.offline_calibration.data_and_selection: supply resolved, specific text
- learning.offline_calibration.freeze_point: supply resolved, specific text
- learning.within_run_state.update_rule: supply resolved, specific text
- results_access.declaration_status: a complete disclosure is required
- results_access.declared_by: supply resolved, specific text
- results_access.declared_at_utc: supply a timezone-aware declaration time
- results_access.no_prior_results_reason: supply resolved, specific text
- results_access.confirmatory_status: choose already_inspected, generated_uninspected, not_generated, not_recorded
- results_access: registration scope requires not_generated; disclose observed outputs as prior work and reserve a genuinely unobserved target
- results_access.prospective_scope: supply resolved, specific text
- results_access.reserved_runs_or_conditions: supply resolved, specific text
- results_access.access_controls: supply resolved, specific text
- provenance: /prior_work_disclosure needs an explicit decided record
- provenance: /outcome_access_before_registration needs an explicit decided record
- provenance: /sections/aims needs an explicit decided record
- provenance: /sections/data_generating_parameters needs an explicit decided record
- provenance: /sections/varied_factors needs an explicit decided record
- provenance: /sections/factor_values_and_constants needs an explicit decided record
- provenance: /sections/factor_combinations_and_condition_count needs an explicit decided record
- provenance: /sections/estimands_and_targets needs an explicit decided record
- provenance: /sections/methods_and_extracted_quantities needs an explicit decided record
- provenance: /sections/performance_measures needs an explicit decided record
- provenance: /sections/monte_carlo_uncertainty needs an explicit decided record
- provenance: /sections/repetition_count_rationale needs an explicit decided record
- provenance: /sections/missingness_and_nonconvergence needs an explicit decided record
- provenance: /sections/interpretation_and_analysis needs an explicit decided record
- provenance: /execution/independent_unit needs an explicit decided record
- provenance: /execution/n_independent_repetitions needs an explicit decided record
- provenance: /execution/evaluation_episodes_per_condition needs an explicit decided record
- provenance: /execution/pilot_seed_blocks needs an explicit decided record
- provenance: /execution/confirmatory_seed_blocks needs an explicit decided record
- provenance: /execution/rng_stream_derivation needs an explicit decided record
- provenance: /execution/training_budget needs an explicit decided record
- provenance: /execution/hyperparameter_selection needs an explicit decided record
- provenance: /execution/checkpoint_selection needs an explicit decided record
- provenance: /execution/stopping_rule needs an explicit decided record
- provenance: /execution/failure_rule needs an explicit decided record
- provenance: /execution/test_access_rule needs an explicit decided record
- provenance: /hypotheses/0/statement needs an explicit decided record
- provenance: /hypotheses/0/contrast needs an explicit decided record
- provenance: /hypotheses/0/outcome needs an explicit decided record
- provenance: /hypotheses/0/analysis needs an explicit decided record
- provenance: /hypotheses/0/interpretation_rule needs an explicit decided record
- provenance: /claim_measure_map/0/construct needs an explicit decided record
- provenance: /claim_measure_map/0/operational_definition needs an explicit decided record
- provenance: /claim_measure_map/0/metric_definition needs an explicit decided record
- provenance: /claim_measure_map/0/estimand needs an explicit decided record
- provenance: /claim_measure_map/0/mechanism needs an explicit decided record
- provenance: /claim_measure_map/0/manipulation needs an explicit decided record
- provenance: /claim_measure_map/0/comparator needs an explicit decided record
- provenance: /claim_measure_map/0/conclusion_scope needs an explicit decided record
- provenance: /claim_measure_map/0/inference_limits needs an explicit decided record
- provenance: /claim_measure_map/0/component_ids needs an explicit decided record
- provenance: /claim_measure_map/0/rival_explanations needs an explicit decided record
- provenance: /claim_measure_map/0/expected_result_patterns needs an explicit decided record
- provenance: /claim_measure_map/0/directly_encoded_effect needs an explicit decided record
- provenance: /components/0/mechanism needs an explicit decided record
- provenance: /components/0/implementation_status needs an explicit decided record
- provenance: /components/0/evidence_status needs an explicit decided record
- provenance: /components/0/included_in_study needs an explicit decided record
- provenance: /components/0/artifact_ids needs an explicit decided record
- provenance: /components/1/mechanism needs an explicit decided record
- provenance: /components/1/implementation_status needs an explicit decided record
- provenance: /components/1/evidence_status needs an explicit decided record
- provenance: /components/1/included_in_study needs an explicit decided record
- provenance: /components/1/artifact_ids needs an explicit decided record
- provenance: /components/2/mechanism needs an explicit decided record
- provenance: /components/2/implementation_status needs an explicit decided record
- provenance: /components/2/evidence_status needs an explicit decided record
- provenance: /components/2/included_in_study needs an explicit decided record
- provenance: /components/2/artifact_ids needs an explicit decided record
- provenance: /learning/offline_calibration/enabled needs an explicit decided record
- provenance: /learning/offline_calibration/parameters needs an explicit decided record
- provenance: /learning/offline_calibration/method needs an explicit decided record
- provenance: /learning/offline_calibration/data_and_selection needs an explicit decided record
- provenance: /learning/offline_calibration/freeze_point needs an explicit decided record
- provenance: /learning/within_run_state/enabled needs an explicit decided record
- provenance: /learning/within_run_state/state_variables needs an explicit decided record
- provenance: /learning/within_run_state/update_rule needs an explicit decided record
- provenance: /learning/within_run_state/memory_role needs an explicit decided record
- provenance: /learning/online_updates/enabled needs an explicit decided record
- provenance: /artifact_handoff/items needs an explicit decided record
- provenance: /results_access/prior_results needs an explicit decided record
- provenance: /results_access/registration_scope needs an explicit decided record
- provenance: /results_access/confirmatory_status needs an explicit decided record
- provenance: /results_access/prospective_scope needs an explicit decided record
- provenance: /results_access/reserved_runs_or_conditions needs an explicit decided record
- provenance: /results_access/access_controls needs an explicit decided record
- reviews.science: approval is not recorded
- reviews.science: supply the actual reviewer name
- reviews.science: supply a timezone-aware review time not in the future
- reviews.science: review digest does not match the current protocol
- reviews.implementation: approval is not recorded
- reviews.implementation: supply the actual reviewer name
- reviews.implementation: supply a timezone-aware review time not in the future
- reviews.implementation: review digest does not match the current protocol
- reviews.analysis: approval is not recorded
- reviews.analysis: supply the actual reviewer name
- reviews.analysis: supply a timezone-aware review time not in the future
- reviews.analysis: review digest does not match the current protocol

## Manual OSF handoff

Use the Simulation Studies form at https://osf.io/registries. Map the sections above to the live form; this is not an API import payload. Review the metadata, narrative, and attachments together. The public planning form has a repeated repetitions label above its nonconvergence prompt; map by the prompt's meaning if that repetition appears in the live form.

Attach the frozen protocol and supporting plans before submission. Verify the archived registration, required approvals, timestamp, and attachment hashes before confirmatory execution. Record the result in registration_record.json.
