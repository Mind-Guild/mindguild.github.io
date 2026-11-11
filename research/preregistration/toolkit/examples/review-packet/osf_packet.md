# Persistent object representations and identity-location binding through occlusion

**Local review packet. This document is not an OSF registration.**

Study ID: MG-OCC-001  
Mechanical readiness: BLOCKED  
Review digest: `9159f7c76f43f9c7dd208f0f060f147f2064ff05eea3ea7aa3661ae649664a1d`

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
  }
]
```

## Mechanical blockers

- status: use approved_for_freeze only after resolving and reviewing the plan
- metadata.description: resolve proposed or placeholder content
- metadata.license: supply a nonempty, specific value
- prior_work_disclosure: supply a nonempty, specific value
- outcome_access_before_registration: supply a nonempty, specific value
- metadata.subjects: supply a nonempty list
- metadata.public_or_embargoed: choose public or embargoed
- sections.data_generating_parameters: resolve proposed or placeholder content
- sections.varied_factors: resolve proposed or placeholder content
- sections.factor_values_and_constants: resolve proposed or placeholder content
- sections.factor_combinations_and_condition_count: resolve proposed or placeholder content
- sections.estimands_and_targets: resolve proposed or placeholder content
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
