# Protocol records, schema version 3

The shared v2 capture layer retains the original metadata, OSF narratives, hypotheses, execution plan, artifact pins, quality evidence, open decisions, and the original three review attestations. These shared records are described below. V3 additionally requires the [test and interpretation contract](TEST_CONTRACT.md), critical review, and the two new CSV exports. Legacy v1/v2 drafts remain readable but require migration and renewed review for a new freeze. This is the toolkit's local data model; it is not an OSF API import schema.

Unknown values remain null, empty, or explicitly not recorded. Drafts can be compiled at any stage. A local freeze requires complete declarations and consistent decisions, plus scientific, implementation, analysis, and critical review. These are self-reported records, not authentication or proof of scientific adequacy.

## Claim-to-measure map

One entry in `claim_measure_map` is required for every primary or secondary confirmatory hypothesis. `hypothesis_id` references the existing hypothesis record; `component_ids` references included components. Each map contains:

- `construct`, `operational_definition`, `metric_definition`, `estimand`, `mechanism`, `manipulation`, and `comparator`.
- `rival_explanations`: one or more objects with `explanation`, `discriminating_control`, and `distinguishing_result`.
- `expected_result_patterns`: `support`, `challenge`, and `inconclusive`.
- `conclusion_scope` and `inference_limits`.
- `directly_encoded_effect`: explicit true/false. If true, `encoded_effect_implications` must explain the limit of observing an effect that was designed into the mechanism.

The validator checks that these declarations exist and point to the intended records. It cannot evaluate whether a control actually rules out a rival or whether a conclusion is warranted. V3 links numerical evidence rules to the hypothesis, claim map, and test-contract contrast records.

## Components: implementation versus evidence

Each `components` entry has `id`, `name`, `role`, `mechanism`, `implementation_status`, `evidence_status`, `included_in_study`, `artifact_ids`, and `source_record_ids`.

| Field | Values |
| --- | --- |
| `role` | model, environment, analysis, learning, control, other |
| `implementation_status` | implemented, planned, analyst_proposed, not_recorded |
| `evidence_status` | demonstrated, verified, not_demonstrated, not_recorded |
| `included_in_study` | true, false, or null while unresolved |

Included confirmatory components must be implemented before freeze and have artifact/source references. An implemented component need not already have produced confirmatory results; do not run those merely to earn an evidence label. Demonstration/verification labels require evidence references and must not contradict an unimplemented status. Split an existing prototype and a future extension into different components when appropriate. Excluded future work can remain planned or analyst-proposed.

## Learning phases

`learning` contains three independent records:

| Phase | If enabled, specify |
| --- | --- |
| `offline_calibration` | `parameters`, `method`, `data_and_selection`, `freeze_point` |
| `within_run_state` | persistent `state_variables`, `update_rule`, `memory_role` |
| `online_updates` | `parameters`, `rule`, `signal_type`, `signal_definition`, `objective`, `schedule`, `evaluation_update_policy` |

Every phase has an explicit `enabled` boolean for a completed plan. Null means unresolved. A disabled phase keeps its active fields null/empty; it must not simultaneously declare active updates. Online signal types are supervised_error, temporal_difference, reward, unsupervised, and other. Changing an internal state is not automatically parameter learning. Naming an algorithm does not supply its objective or teaching signal.

## Artifact handoff

`artifact_handoff.items` records an ID and a disposition for code, config, environment, scenario_manifest, input_traces, equations, slides, and chat. Analysis and other artifacts are optional additional kinds.

Each item has `id`, `kind`, `status`, `location`, `sha256`, `immutable_version`, `owner`, and `reason`. Status is captured, requested, not_available, or not_applicable. Requested items need an owner and reason and remain open. Unavailable/inapplicable supporting artifacts need truthful reasons. A missing original chat can be documented as unavailable while later written decisions provide the scientific evidence.

Code, config, environment, and scenario_manifest are core artifacts and must be captured. A captured item needs a location and either a 64-hex SHA-256 digest or a declared immutable version. Floating aliases such as main, HEAD, and latest are not version pins. The code item's `immutable_version` must match `artifacts.code_commit_sha`. Environment and scenario-manifest hashes must match their existing execution artifact fields. One immutable code snapshot can contain several artifacts; use precise file/pointer locations and document their contents.

Complete the handoff with `confirmed_by` and a timezone-aware `confirmed_at_utc`. The validator compares declared pins; it does not download remote files or verify their bytes. Preserve actual input traces where available; if the DGM generates all inputs, document how the pinned generator/config/seed plan replaces an external trace.

## Prior results and prospective access

`results_access` requires a complete declaration with `declared_by` and `declared_at_utc`. For each prior result, capture this shape:

```json
{
  "description": null,
  "conditions_or_runs": null,
  "who_saw": [],
  "seen_when": null,
  "use": null,
  "influence_on_design": null,
  "source_record_ids": []
}
```

Approximate historical times can be described truthfully in `seen_when`; do not invent timestamp precision. If the prior-results list is empty, supply `no_prior_results_reason` and confirm the declaration. An empty list alone does not establish that nothing has been seen.

| Registration scope | Required confirmatory status | Meaning |
| --- | --- | --- |
| `new_simulation_runs` | `not_generated` | The plan precedes generation of the reserved confirmatory runs. |
| `analysis_of_uninspected_outputs` | `generated_uninspected` | Only the new analysis is prospective; generation is already complete and disclosed. |

Also specify `prospective_scope`, `reserved_runs_or_conditions`, and `access_controls`. An already-inspected target cannot pass either scope. Record those outputs as prior work and define a new unobserved target if appropriate. A later registration cannot change when an earlier analysis occurred.

## Per-field provenance

`provenance` contains one current record per tracked field, using absolute JSON Pointer paths. For example:

```json
{
  "field_path": "/hypotheses/0/statement",
  "origin": "meeting",
  "decision_status": "proposed",
  "source_record_ids": ["S1"],
  "source_locator": "meeting transcript 18:39–19:09",
  "speaker_label": "Unresolved participant",
  "speaker_attribution": "unresolved",
  "decision_by": null,
  "decision_record": null,
  "recorded_at_utc": null,
  "value_digest": null,
  "analyst_adoption": {
    "adopted_by": null,
    "source_record_id": null,
    "adopted_at_utc": null
  }
}
```

Origins are meeting, artifact, researcher_followup, analyst_proposal, and not_recorded. Decision states are decided, proposed, deferred, rejected, and not_recorded. Speaker attribution is identified, unresolved, or not_applicable; identified attribution requires a label/name. A named later decision owner can accept a proposal while the original speaker remains unresolved. Do not retroactively invent attribution.

The required field list is generated by `required_provenance_paths` in `scripts/protocol_v2.py`; it covers confirmatory hypothesis content, core OSF scientific narratives, execution choices, claim-map fields, component status/inclusion, active learning declarations, the artifact list, the prospective boundary, and all six v3 test-contract groups. Containers such as rival explanations and the artifact list can be tracked as a whole: changes to any contained value invalidate the container's digest. Additional resolvable scientific-field paths may be recorded. Provenance and review attestations cannot target themselves.

A decided record requires a known source ID, a precise locator, actual `decision_by` and `decision_record`, a timezone-aware recording time, and the SHA-256 of the canonical JSON field value in `value_digest`. If the origin is analyst_proposal, also record actual human adoption, its source ID, and time. These fields do not authenticate people; their purpose is to expose the evidence for review. Proposals do not become agreed merely because the draft is fluent or complete-looking.

## Capture workflow

1. Populate the scientific plan and structured records from supplied evidence. Mark unknowns and proposals honestly.
2. Run the packet compiler. It writes the readable packet, readiness diagnostics, a protocol snapshot, `decision_ledger.csv`, `artifact_handoff.csv`, `prediction_matrix.csv`, and `design_assurance.csv`.
3. To initialize missing provenance rows without approving values:

```bash
python scripts/scaffold_provenance.py protocol.json --out protocol.capture.json
```

The helper adds only undecided records and current field digests. It never refreshes an existing stale decision, adopts a proposal, or overwrites a file. The CSV is a review export, not an import path: edit the selected JSON source. The whole protocol remains subject to the scientific, implementation, analysis, and critical reviews.

4. After actual decisions, record evidence and agreement status in that JSON. Use the decision ledger's current digests after checking the corresponding values. An edited value requires renewed field agreement and overall review. An implementation/evidence claim can be agreed as a characterization of status without implying that a future component is built.
5. Review the completed protocol and attempt a local freeze using a new directory. Verify actual OSF registration separately before executing the prospective work.

## Migrate a v1 or v2 study

```bash
python scripts/migrate_protocol.py old-protocol.json --out protocol.v3.json
python scripts/scaffold_provenance.py protocol.v3.json --out protocol.capture.json
python scripts/build_packet.py protocol.capture.json --out review-packet
```

The migration copies legacy scientific values, preserves old status/reviews under `migration` as history, resets active reviews, and adds unresolved structured records. It never infers a new primary claim, component readiness, learning mode, results-access declaration, or human agreement. It refuses existing output files and ambiguous legacy inputs that already use v2 field names. V1/v2 drafts remain readable by the compiler but cannot create a new freeze until migrated. V2 source decisions are preserved; six unresolved test-contract groups and the critical review are added. Missing records in a v3 input are diagnosed rather than silently supplied during compilation.

All helpers use Python 3.10+ and the standard library. No helper submits to OSF, sends messages, downloads evidence artifacts, or runs a simulator.
