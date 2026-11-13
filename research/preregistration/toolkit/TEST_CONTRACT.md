# V3 test-contract reference

Schema v3 retains all v2 capture records and adds `test_contract` plus `reviews.critical`. Read [SCHEMA.md](SCHEMA.md) for the shared records and [CRITIQUE.md](CRITIQUE.md) for the rationale. The blank JSON is the complete machine-readable shape. Every new choice starts unresolved; no study or reviewer approval is supplied by migration.

## Inference and competing accounts

`test_contract.inference` records:

| Field | Rule |
| --- | --- |
| `study_type` | `mechanism_benchmark` or `theory_discrimination`. |
| `target_level` | `functional_performance`, `computational_mechanism`, or `theory_prediction`. A theory-discrimination study uses the last; a benchmark does not. |
| `phenomenon` | Precisely identify what this simulation operationalizes. |
| `allowed_conclusion`, `excluded_conclusions` | Bound the claim before seeing outcomes. Exclusions are a nonempty list. |
| `theory_core_vs_implementation` | Identify whether a failed prediction bears on a core claim, an implementation, an auxiliary assumption, or a bridge to this task. |
| `consciousness_inference` | `not_assessed` or `conditional_on_bridge_assumptions`. Benchmarks must use `not_assessed`. Neither value means consciousness has been detected. |

`accounts` contains at least two explanations with stable `id`, `name`, explicit `version`, `kind` (`mechanistic_account` or `theory`), `source_record_ids`, included `component_ids` (which may be empty for a conceptual account), `commitment`, and `implementation_assumptions`. A theory-discrimination study names at least one actual theory account; the other can be a substantive mechanism alternative. Do not invent a competing consciousness theory solely to satisfy the template.

Each account's `bridge_assumptions` is a nonempty list of objects with `assumption`, `test_or_justification`, and `violation_implication`. This is where researchers state how the implemented system, task, and observable relate to the claim. Existence of a written bridge is not evidence that it is true.

## Quantitative contrasts and interpretation

Map each primary/secondary hypothesis exactly once in `contrasts`. Each entry has `hypothesis_id`, `target_account_id`, `rival_account_id`, an `estimand` identical to its claim-map estimand, `interval_method`, `multiplicity_rule`, `diagnosticity_reason`, and `resource_matching`.

`prediction_regions` contains one row per linked account:

```json
{"account_id":"T1","specified":null,"lower":null,"upper":null,"derivation":null}
```

After an actual decision, `specified` is true or false. True requires at least one finite numeric bound; null bounds mean minus/plus infinity. Bounds are inclusive and ordered. False means the account makes no prediction on this contrast: keep both bounds null and explain why in `derivation`. It does not mean zero effect. These are predictions about the common estimand, not confidence levels, observed outcomes, or a threshold invented after calibration.

The engine compares a prespecified uncertainty interval with each prediction region. Entire containment is compatible; no intersection is incompatible; partial intersection is uncertain. It then returns:

| Category | Mechanical meaning |
| --- | --- |
| `target_only` | Compatible with target, incompatible with rival. |
| `rival_only` | Compatible with rival, incompatible with target. |
| `both` | Entirely compatible with both. |
| `neither` | Entirely incompatible with both. |
| `inconclusive` | Any boundary straddling, or an unspecified account prediction. |
| `invalid` | A required validity condition failed. |

Every category requires a prespecified interpretation under `interpretations`. Compatibility is not proof of a theory; incompatibility challenges a stated prediction conditional on the auxiliary assumptions. A nonsignificant test is not automatically `neither`, and a wide interval is not a precise null effect.

For a primary theory-discrimination test, each region must permit at least one result excluded by the other. Identical, unspecified, or nested regions cannot pass this restricted engine's theory-discrimination gate. Benchmarks may retain such a comparison but cannot describe it as discriminating the accounts. Richer model-comparison designs need a reviewed extension, rather than fabricated opposing predictions.

`validity_checks` must include measurement, implementation, and negative-control records. Each has a specific `pass_rule`, `passed` true for freeze, `evidence_artifact_id`, and `failure_action`. Evidence points to a captured, SHA-256-pinned artifact of kind `analysis`, rather than merely to the code. These are feasibility/control results, not a reason to run the reserved confirmatory study before registration.

## Design assurance before freeze

Each confirmatory hypothesis has one `design_assurance` entry:

- `strategy`: `decision_errors` or `precision`.
- `independent_unit` and `planned_repetitions`: match the execution plan exactly.
- `minimum_effect_magnitude`: positive numeric magnitude, with `effect_scale_and_justification`.
- `assumptions_and_range`: generators, nuisance ranges, weakest effects, and circumstances in which the comparison is diagnostic. Assess a range rather than an easy single example.
- `calibration_sampling`: independent calibration replications, RNG/seed derivation, treatment of invalid runs, and uncertainty assumptions. Calibration replications are repetitions of the entire proposed experiment, not extra frames within one run.
- `evidence_artifact_id`: captured SHA-256-pinned analysis report containing the code/input links and condition-level results.
- `calibration_basis_sha256`: digest emitted by the calibration helper for this hypothesis. It binds scientific choices, prediction rules, criterion thresholds, the planned experiment size, and the replication partition/analysis plan. Editing these requires new calibration/review. Counts and report pins are excluded to avoid a hash cycle.
- `maximum_interval_width`: a positive width on the estimand scale when strategy is precision; otherwise null.
- `criteria`: scenario-level rate checks, described below.

Each criterion records `scenario`, `scenario_definition`, `event`, `direction`, `threshold`, `count`, and `total`. Counts are integers with `0 <= count <= total`, total at least two, and probability thresholds strictly between zero and one. Thresholds are researcher decisions; the template provides no default power, alpha, meaningful effect, or calibration sample count.

For `decision_errors`, require these checks:

| Synthetic scenario | Event | Direction |
| --- | --- | --- |
| null | target_only | at_most |
| target, at the minimum meaningful effect | target_only | at_least |
| rival | rival_only | at_least |

For `precision`, require `precision_achieved` and `coverage`, both `at_least`, under null, target, and rival scenarios. A theory-discrimination study must use decision-error calibration; precision alone does not establish discrimination in this implementation.

Both strategies additionally require an `invalid` event with an `at_most` threshold in every scenario. This prevents an unusable null simulation from appearing acceptable merely because it never favors the target. Invalid-rate thresholds, like the other thresholds, are explicit researcher choices.

The compiler computes a two-sided 95% Wilson interval for each rate. An `at_most` criterion passes only if its upper bound is at or below the chosen limit; `at_least` passes only if its lower bound is at or above the chosen minimum. These intervals quantify calibration uncertainty conditional on independent draws; they do not certify the scientific generator or provide a simultaneous guarantee across all criteria. Account for the full decision procedure and multiplicity in the simulation and written plan.

Use the helper on actual synthetic calibration output:

```bash
python scripts/calibrate_decisions.py protocol.capture.json calibration-input.json --out calibration-report.json
```

Start with `templates/calibration_input.blank.json`, replace every placeholder with genuine generated intervals and known synthetic estimands, and include all three scenarios for every contrast. The helper does not generate simulations or fill approvals. Each record has `hypothesis_id`, `scenario`, unique `run_id` within hypothesis/scenario, `interval` (two ordered finite numbers), `true_estimand`, and boolean `valid`. Invalid runs remain in the denominator, with their outcome counts reported. Width/coverage events require validity. Keep the generator, input records, report, and code versions. Inspect and transfer the report counts and basis digest into the protocol, then pin the report as an analysis artifact. The helper never overwrites an existing output.

Review the supplied counts against the pinned report: the compiler does not fetch remote bytes. Its basis digest detects declared scientific changes; it does not authenticate that the report was produced from those choices or prevent invented counts.

## Critical review with proportional roles

`critical_review` specifies `coordinator`, `coordinator_conflicts`, boolean `roles_overlap`, `overlap_reason` when roles overlap, `disagreement_resolution`, and an empty `unresolved_disputes` list at freeze. Each account gets one `perspectives` record containing `account_id`, actual `reviewer_name`, `relationship` (`proponent`, `informed_proxy`, or `internal_critic`), `conflicts`, and `endorsement_source_id` if claiming actual proponent involvement.

One person can cover multiple roles with an explicit limitation. This is internal critical review, not independent adversarial collaboration. The tool cannot verify the person's expertise or identity.

The `reviews.critical` attestation uses the same name, approval, time, digest, and notes fields as the existing reviews; its `reviewer_name` matches the coordinator. It also contains `perspective_records`, one per account, each recording the assigned reviewer, `design_and_interpretation_accepted` true, source IDs, source locator, and review time. Acceptance concerns the fairness of the design and all outcome interpretations, not belief in the account or theory. All four review roles refer to the current overall review digest.

## Execution, replication, and reporting

`test_contract.execution.masking` specifies mode `masked` or `open_with_justification`, `method_or_limitation`, custodian, analyst, captured `analysis_lock_artifact_id`, `access_log_location`, and gate `registration_archived_and_analysis_locked`. A masked claim uses distinct custodian and analyst identifiers. Actual access control and registration checks must be implemented outside this local compiler; the label creates no access barrier.

`replication.mode` is `reserved_runs`, `independent_implementation`, or `none_with_reason`. All modes need an independence basis or limitation, release trigger, analysis/pooling rule, and failure interpretation. Reserved runs use a unique subset of planned confirmatory seeds, with at least two independent blocks in the initial test and two in the reserved stage. Describe separate evaluation panels and RNG streams; distinct integers alone do not establish independence. An independent implementation has its own captured artifact, separate from the primary code artifact, and an actual independence rationale. A benchmark can explicitly decline a replication claim; theory discrimination requires one of the first two plans. A fresh-seed replication is not automatically an independent implementation or a biological replication.

`reporting` commits true to all registered hypotheses, all attempts, the full outcome matrix, deviations with exposure, and outcome-independent release. Supply release location/deadline rule, amendment rule, and interpretation-revision rule. Preserve original interpretations and date any revised explanation with the outcomes visible then. Do not overwrite an original registration or retroactively label new interpretations confirmatory.

## Migration and artifacts

```bash
python scripts/migrate_protocol.py old-v1-or-v2.json --out protocol.v3.json
python scripts/scaffold_provenance.py protocol.v3.json --out protocol.capture.json
python scripts/build_packet.py protocol.capture.json --out review-packet
```

V1 and v2 remain draft-readable but cannot create new freezes with this version. Existing frozen directories are left intact. Migration preserves source study records, prior decision records, and review/migration history, resets active approval, and adds unresolved v3 choices. The scaffold adds six undecided provenance rows for the contract groups; their value digests bind the full nested content. It does not refresh old decisions, adopt proposals, compute calibration, or approve the plan.

Packets add `prediction_matrix.csv` and `design_assurance.csv` to the existing five outputs. Freeze remains a local archival convention. Attach the human-reviewed contract and calibration materials alongside the OSF form; no API submission is performed.
