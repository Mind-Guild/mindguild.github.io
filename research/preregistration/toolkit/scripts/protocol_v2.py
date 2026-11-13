"""Structured capture, provenance, and prospective-access checks for schema v2.

These checks validate declarations and consistency, not scientific truth,
remote artifact bytes, identities, or authenticated human agreement.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import html
import io
import json
import re
from datetime import datetime, timezone

CORE_ARTIFACTS = {"code", "config", "environment", "scenario_manifest"}
CAPTURE_KINDS = ("code", "config", "environment", "scenario_manifest", "input_traces", "equations", "slides", "chat")
DECISION_STATES = {"decided", "proposed", "deferred", "rejected", "not_recorded"}
ORIGINS = {"meeting", "artifact", "researcher_followup", "analyst_proposal", "not_recorded"}
PLACEHOLDER = re.compile(r"\b(TBD|TODO|UNRESOLVED|TO BE CONFIRMED)\b|\[INSERT|^\s*PROPOSED\s*:", re.I)
BASE_SCIENTIFIC_PATHS = (
    "/prior_work_disclosure", "/outcome_access_before_registration",
    "/sections/aims", "/sections/data_generating_parameters", "/sections/varied_factors",
    "/sections/factor_values_and_constants", "/sections/factor_combinations_and_condition_count",
    "/sections/estimands_and_targets", "/sections/methods_and_extracted_quantities",
    "/sections/performance_measures", "/sections/monte_carlo_uncertainty",
    "/sections/repetition_count_rationale", "/sections/missingness_and_nonconvergence",
    "/sections/interpretation_and_analysis", "/execution/independent_unit",
    "/execution/n_independent_repetitions", "/execution/evaluation_episodes_per_condition",
    "/execution/pilot_seed_blocks", "/execution/confirmatory_seed_blocks",
    "/execution/rng_stream_derivation", "/execution/training_budget",
    "/execution/hyperparameter_selection", "/execution/checkpoint_selection",
    "/execution/stopping_rule", "/execution/failure_rule", "/execution/test_access_rule",
)
CLAIM_FIELDS = (
    "construct", "operational_definition", "metric_definition", "estimand", "mechanism",
    "manipulation", "comparator", "conclusion_scope", "inference_limits",
)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def value_digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def valid_datetime(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed <= datetime.now(timezone.utc)
    except (AttributeError, TypeError, ValueError):
        return False


def new_claim(hypothesis_id="H1"):
    return dict(hypothesis_id=hypothesis_id, component_ids=[], **{key: None for key in CLAIM_FIELDS},
                rival_explanations=[{"explanation": None, "discriminating_control": None, "distinguishing_result": None}],
                expected_result_patterns={"support": None, "challenge": None, "inconclusive": None},
                directly_encoded_effect=None, encoded_effect_implications=None)


def new_component(component_id="M1"):
    return {"id": component_id, "name": None, "role": None, "mechanism": None,
            "implementation_status": "not_recorded", "evidence_status": "not_recorded",
            "included_in_study": None, "artifact_ids": [], "source_record_ids": []}


def new_records():
    return {
        "claim_measure_map": [new_claim()],
        "components": [new_component()],
        "learning": {
            "offline_calibration": {"enabled": None, "parameters": [], "method": None,
                                    "data_and_selection": None, "freeze_point": None},
            "within_run_state": {"enabled": None, "state_variables": [], "update_rule": None, "memory_role": None},
            "online_updates": {"enabled": None, "parameters": [], "rule": None, "signal_type": None,
                               "signal_definition": None, "objective": None, "schedule": None,
                               "evaluation_update_policy": None},
        },
        "provenance": [],
        "artifact_handoff": {
            "items": [{"id": "A_" + kind, "kind": kind, "status": "requested", "location": None,
                       "sha256": None, "immutable_version": None, "owner": None, "reason": None}
                      for kind in CAPTURE_KINDS],
            "confirmed_by": None, "confirmed_at_utc": None,
        },
        "results_access": {
            "declaration_status": "incomplete", "declared_by": None, "declared_at_utc": None,
            "prior_results": [], "no_prior_results_reason": None,
            "registration_scope": None, "confirmatory_status": None,
            "prospective_scope": None, "reserved_runs_or_conditions": None, "access_controls": None,
        },
    }


def provenance_record(field_path):
    return {"field_path": field_path, "origin": "not_recorded", "decision_status": "not_recorded",
            "source_record_ids": [], "source_locator": None, "speaker_label": None,
            "speaker_attribution": "unresolved", "decision_by": None, "decision_record": None,
            "recorded_at_utc": None, "value_digest": None,
            "analyst_adoption": {"adopted_by": None, "source_record_id": None, "adopted_at_utc": None}}


def migrate_v1(protocol, original_sha256=None):
    """Copy legacy content without inferring new choices or retaining approvals."""
    if not isinstance(protocol, dict) or type(protocol.get("schema_version")) is not int or protocol["schema_version"] != 1:
        raise ValueError("Migration requires a schema_version 1 protocol")
    reserved = set(new_records()) & set(protocol)
    if reserved:
        raise ValueError("Legacy input already contains v2 fields; resolve them before migrating: " + ", ".join(sorted(reserved)))
    result = copy.deepcopy(protocol)
    result.update(new_records())
    result["schema_version"] = 2
    result["status"] = "draft"
    hypotheses = protocol.get("hypotheses", [])
    result["claim_measure_map"] = [new_claim(h.get("id")) for h in hypotheses
                                   if isinstance(h, dict) and h.get("classification") in {"primary", "secondary"}]
    old_reviews = copy.deepcopy(protocol.get("reviews"))
    result["reviews"] = {role: {"reviewer_name": None, "approved": False, "reviewed_at_utc": None,
                               "review_digest": None, "notes": None}
                         for role in ("science", "implementation", "analysis")}
    result["migration"] = {"from_schema_version": 1, "original_protocol_sha256": original_sha256 or value_digest(protocol),
                           "original_hash_basis": "file_bytes" if original_sha256 else "canonical_json",
                           "previous_status": protocol.get("status"), "previous_reviews": old_reviews,
                           "note": "Legacy values preserved. New fields are unresolved; old approvals are historical only."}
    if not isinstance(result.get("open_decisions"), list):
        result["open_decisions"] = []
    result["open_decisions"].append({"id": "V2_CAPTURE", "decision": "Complete the v2 structured records and renew the three reviews.", "owner": None})
    return result


def pointer_value(document, path):
    if not isinstance(path, str) or not path.startswith("/") or re.search(r"~(?![01])", path):
        raise ValueError("Use a valid absolute JSON Pointer")
    value = document
    for raw in path[1:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and key in value:
            value = value[key]
        elif isinstance(value, list) and re.fullmatch(r"0|[1-9][0-9]*", key) and int(key) < len(value):
            value = value[int(key)]
        else:
            raise ValueError("Pointer does not resolve")
    return value


def objects(value):
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def required_provenance_paths(protocol):
    """Scientific decisions to trace; metadata and review attestations are separate."""
    paths = list(BASE_SCIENTIFIC_PATHS)
    for i, hypothesis in enumerate(protocol.get("hypotheses", []) if isinstance(protocol.get("hypotheses"), list) else []):
        if isinstance(hypothesis, dict) and hypothesis.get("classification") in {"primary", "secondary"}:
            paths.extend(f"/hypotheses/{i}/{key}" for key in ("statement", "contrast", "outcome", "analysis", "interpretation_rule"))
    for i, claim in enumerate(protocol.get("claim_measure_map", []) if isinstance(protocol.get("claim_measure_map"), list) else []):
        if not isinstance(claim, dict):
            continue
        keys = [*CLAIM_FIELDS, "component_ids", "rival_explanations", "expected_result_patterns", "directly_encoded_effect"]
        if claim.get("directly_encoded_effect") is True:
            keys.append("encoded_effect_implications")
        paths.extend(f"/claim_measure_map/{i}/{key}" for key in keys)
    for i, component in enumerate(protocol.get("components", []) if isinstance(protocol.get("components"), list) else []):
        if isinstance(component, dict):
            paths.extend(f"/components/{i}/{key}" for key in
                         ("mechanism", "implementation_status", "evidence_status", "included_in_study", "artifact_ids"))
    learning = protocol.get("learning", {})
    if isinstance(learning, dict):
        for phase in ("offline_calibration", "within_run_state", "online_updates"):
            record = learning.get(phase, {})
            paths.append(f"/learning/{phase}/enabled")
            if isinstance(record, dict) and record.get("enabled") is True:
                paths.extend(f"/learning/{phase}/{key}" for key in new_records()["learning"][phase] if key != "enabled")
    paths.extend(("/artifact_handoff/items", "/results_access/prior_results",
                  "/results_access/registration_scope", "/results_access/confirmatory_status",
                  "/results_access/prospective_scope", "/results_access/reserved_runs_or_conditions",
                  "/results_access/access_controls"))
    if type(protocol.get("schema_version")) is int and protocol["schema_version"] == 3:
        paths.extend("/test_contract/" + key for key in
                     ("inference", "accounts", "contrasts", "design_assurance", "critical_review", "execution"))
    return list(dict.fromkeys(paths))


def validate_v2(protocol):
    errors = []

    def obj(value, label):
        if not isinstance(value, dict):
            errors.append(label + ": supply an object")
            return {}
        return value

    def array(value, label, nonempty=False):
        if not isinstance(value, list) or (nonempty and not value):
            errors.append(label + ": supply " + ("a nonempty list" if nonempty else "a list"))
            return []
        return value

    def text(value, label):
        if not isinstance(value, str) or not value.strip() or PLACEHOLDER.search(value):
            errors.append(label + ": supply resolved, specific text")

    def enum(value, choices, label):
        if not isinstance(value, str) or value not in choices:
            errors.append(label + ": choose " + ", ".join(sorted(choices)))

    def boolean(value, label):
        if type(value) is not bool:
            errors.append(label + ": explicitly choose true or false")

    def string_list(value, label, nonempty=True):
        values = array(value, label, nonempty)
        for i, entry in enumerate(values):
            text(entry, f"{label}[{i}]")
        return values

    sources = {x.get("id") for x in objects(protocol.get("source_records")) if isinstance(x.get("id"), str)}

    def refs(value, allowed, label, nonempty=True):
        values = array(value, label, nonempty)
        if any(not isinstance(x, str) or x not in allowed for x in values):
            errors.append(label + ": reference existing IDs")
        if all(isinstance(x, str) for x in values) and len(values) != len(set(values)):
            errors.append(label + ": IDs must be unique")

    handoff = obj(protocol.get("artifact_handoff"), "artifact_handoff")
    items = array(handoff.get("items"), "artifact_handoff.items", True)
    artifact_ids, captured_kinds = set(), set()
    for i, value in enumerate(items):
        label = f"artifact_handoff.items[{i}]"
        item = obj(value, label)
        aid = item.get("id")
        text(aid, label + ".id")
        if isinstance(aid, str):
            if aid in artifact_ids:
                errors.append(label + ": duplicate artifact ID")
            artifact_ids.add(aid)
        enum(item.get("kind"), set(CAPTURE_KINDS) | {"analysis", "other"}, label + ".kind")
        enum(item.get("status"), {"captured", "requested", "not_available", "not_applicable"}, label + ".status")
        if item.get("status") == "captured":
            text(item.get("location"), label + ".location")
            digest, version = item.get("sha256"), item.get("immutable_version")
            if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", digest)):
                errors.append(label + ".sha256: use a 64-hex SHA-256 digest")
            pinned_version = isinstance(version, str) and version.strip() and version.lower() not in {"main", "master", "head", "latest", "dev", "unknown"} and not PLACEHOLDER.search(version)
            if not (isinstance(digest, str) and re.fullmatch(r"[a-fA-F0-9]{64}", digest)) and not pinned_version:
                errors.append(label + ": pin a SHA-256 digest or a declared immutable version")
            kind = item.get("kind")
            if isinstance(kind, str):
                captured_kinds.add(kind)
            old = protocol.get("artifacts", {})
            old = old if isinstance(old, dict) else {}
            if kind == "code" and version != old.get("code_commit_sha"):
                errors.append(label + ": code immutable_version must match artifacts.code_commit_sha")
            expected = {"environment": "environment_lock_sha256", "scenario_manifest": "scenario_manifest_sha256"}.get(kind if isinstance(kind, str) else "")
            if expected and digest != old.get(expected):
                errors.append(label + ": SHA-256 must match artifacts." + expected)
        else:
            text(item.get("reason"), label + ".reason")
            if item.get("status") == "requested":
                text(item.get("owner"), label + ".owner")
                errors.append(label + ": requested capture is still open")
    kinds = {x.get("kind") for x in objects(items) if isinstance(x.get("kind"), str)}
    for kind in CAPTURE_KINDS:
        if kind not in kinds:
            errors.append("artifact_handoff: record a disposition for " + kind)
    for kind in sorted(CORE_ARTIFACTS - captured_kinds):
        errors.append("artifact_handoff: capture the core " + kind + " artifact")
    text(handoff.get("confirmed_by"), "artifact_handoff.confirmed_by")
    if not valid_datetime(handoff.get("confirmed_at_utc")):
        errors.append("artifact_handoff.confirmed_at_utc: supply a timezone-aware confirmation time")

    components = array(protocol.get("components"), "components", True)
    component_ids, included = set(), set()
    for i, value in enumerate(components):
        label = f"components[{i}]"
        component = obj(value, label)
        cid = component.get("id")
        for key in ("id", "name", "mechanism"):
            text(component.get(key), label + "." + key)
        if isinstance(cid, str):
            if cid in component_ids:
                errors.append(label + ": duplicate component ID")
            component_ids.add(cid)
        enum(component.get("role"), {"model", "environment", "analysis", "learning", "control", "other"}, label + ".role")
        enum(component.get("implementation_status"), {"implemented", "planned", "analyst_proposed", "not_recorded"}, label + ".implementation_status")
        enum(component.get("evidence_status"), {"demonstrated", "verified", "not_demonstrated", "not_recorded"}, label + ".evidence_status")
        boolean(component.get("included_in_study"), label + ".included_in_study")
        if component.get("included_in_study") is True:
            if isinstance(cid, str):
                included.add(cid)
            if component.get("implementation_status") != "implemented":
                errors.append(label + ": a confirmatory component must be implemented before freeze")
            if component.get("evidence_status") == "not_recorded":
                errors.append(label + ": record the selected component's demonstration/verification status explicitly")
            refs(component.get("artifact_ids"), artifact_ids, label + ".artifact_ids")
            refs(component.get("source_record_ids"), sources, label + ".source_record_ids")
        else:
            refs(component.get("artifact_ids"), artifact_ids, label + ".artifact_ids", False)
            refs(component.get("source_record_ids"), sources, label + ".source_record_ids", False)
        if isinstance(component.get("evidence_status"), str) and component.get("evidence_status") in {"demonstrated", "verified"}:
            if component.get("implementation_status") != "implemented":
                errors.append(label + ": demonstration/verification contradicts an unimplemented status; split prototype and future components")
            refs(component.get("artifact_ids"), artifact_ids, label + ".artifact_ids")
            refs(component.get("source_record_ids"), sources, label + ".source_record_ids")
    if not included:
        errors.append("components: identify at least one implemented component included in the study")

    hypotheses = {x.get("id"): x for x in objects(protocol.get("hypotheses")) if isinstance(x.get("id"), str)}
    mapped = []
    for i, value in enumerate(array(protocol.get("claim_measure_map"), "claim_measure_map", True)):
        label = f"claim_measure_map[{i}]"
        claim = obj(value, label)
        hid = claim.get("hypothesis_id")
        if not isinstance(hid, str) or hid not in hypotheses:
            errors.append(label + ".hypothesis_id: reference an existing hypothesis")
        else:
            mapped.append(hid)
        refs(claim.get("component_ids"), included, label + ".component_ids")
        for key in CLAIM_FIELDS:
            text(claim.get(key), label + "." + key)
        for j, rival in enumerate(array(claim.get("rival_explanations"), label + ".rival_explanations", True)):
            rival = obj(rival, label + f".rival_explanations[{j}]")
            for key in ("explanation", "discriminating_control", "distinguishing_result"):
                text(rival.get(key), label + f".rival_explanations[{j}]." + key)
        patterns = obj(claim.get("expected_result_patterns"), label + ".expected_result_patterns")
        for key in ("support", "challenge", "inconclusive"):
            text(patterns.get(key), label + ".expected_result_patterns." + key)
        boolean(claim.get("directly_encoded_effect"), label + ".directly_encoded_effect")
        if claim.get("directly_encoded_effect") is True:
            text(claim.get("encoded_effect_implications"), label + ".encoded_effect_implications")
    if len(mapped) != len(set(mapped)):
        errors.append("claim_measure_map: map each hypothesis at most once")
    for hid, hypothesis in hypotheses.items():
        if hypothesis.get("classification") in {"primary", "secondary"} and hid not in mapped:
            errors.append("claim_measure_map: missing confirmatory hypothesis " + hid)

    learning = obj(protocol.get("learning"), "learning")
    for phase in ("offline_calibration", "within_run_state", "online_updates"):
        label = "learning." + phase
        record = obj(learning.get(phase), label)
        boolean(record.get("enabled"), label + ".enabled")
        defaults = new_records()["learning"][phase]
        if record.get("enabled") is True:
            list_key = "state_variables" if phase == "within_run_state" else "parameters"
            string_list(record.get(list_key), label + "." + list_key)
            for key in defaults:
                if key not in {"enabled", list_key, "signal_type"}:
                    text(record.get(key), label + "." + key)
            if phase == "online_updates":
                enum(record.get("signal_type"), {"supervised_error", "temporal_difference", "reward", "unsupervised", "other"}, label + ".signal_type")
        elif record.get("enabled") is False:
            if any(record.get(key) not in (None, [], "") for key in defaults if key != "enabled"):
                errors.append(label + ": disabled phase must not declare active parameters, rules, or signals")

    access = obj(protocol.get("results_access"), "results_access")
    if access.get("declaration_status") != "complete":
        errors.append("results_access.declaration_status: a complete disclosure is required")
    text(access.get("declared_by"), "results_access.declared_by")
    if not valid_datetime(access.get("declared_at_utc")):
        errors.append("results_access.declared_at_utc: supply a timezone-aware declaration time")
    prior = array(access.get("prior_results"), "results_access.prior_results")
    if not prior:
        text(access.get("no_prior_results_reason"), "results_access.no_prior_results_reason")
    elif access.get("no_prior_results_reason") not in (None, ""):
        errors.append("results_access.no_prior_results_reason: clear the no-results explanation when prior results are listed")
    for i, value in enumerate(prior):
        label = f"results_access.prior_results[{i}]"
        record = obj(value, label)
        for key in ("description", "conditions_or_runs", "seen_when", "use", "influence_on_design"):
            text(record.get(key), label + "." + key)
        string_list(record.get("who_saw"), label + ".who_saw")
        refs(record.get("source_record_ids"), sources, label + ".source_record_ids")
    enum(access.get("registration_scope"), {"new_simulation_runs", "analysis_of_uninspected_outputs"}, "results_access.registration_scope")
    enum(access.get("confirmatory_status"), {"not_generated", "generated_uninspected", "already_inspected", "not_recorded"}, "results_access.confirmatory_status")
    required_state = {"new_simulation_runs": "not_generated", "analysis_of_uninspected_outputs": "generated_uninspected"}.get(access.get("registration_scope") if isinstance(access.get("registration_scope"), str) else "")
    if required_state and access.get("confirmatory_status") != required_state:
        errors.append("results_access: registration scope requires " + required_state + "; disclose observed outputs as prior work and reserve a genuinely unobserved target")
    for key in ("prospective_scope", "reserved_runs_or_conditions", "access_controls"):
        text(access.get(key), "results_access." + key)

    records = array(protocol.get("provenance"), "provenance")
    by_path = {}
    for i, value in enumerate(records):
        label = f"provenance[{i}]"
        record = obj(value, label)
        path = record.get("field_path")
        try:
            current = pointer_value(protocol, path)
            if path.split("/")[1] in {"provenance", "reviews", "status", "migration"}:
                raise ValueError("Target must be scientific content, not an attestation")
        except ValueError as error:
            errors.append(label + ".field_path: " + str(error))
            continue
        if path in by_path:
            errors.append(label + ".field_path: duplicate current provenance record")
        by_path[path] = record
        enum(record.get("origin"), ORIGINS, label + ".origin")
        enum(record.get("decision_status"), DECISION_STATES, label + ".decision_status")
        enum(record.get("speaker_attribution"), {"identified", "unresolved", "not_applicable"}, label + ".speaker_attribution")
        if record.get("speaker_attribution") == "identified":
            text(record.get("speaker_label"), label + ".speaker_label")
        refs(record.get("source_record_ids"), sources, label + ".source_record_ids", record.get("decision_status") == "decided")
        if record.get("value_digest") is not None and record.get("value_digest") != value_digest(current):
            errors.append(label + ".value_digest: stale decision; the field value changed")
        if record.get("decision_status") == "decided":
            if record.get("origin") == "not_recorded":
                errors.append(label + ": decided content needs a recorded origin")
            for key in ("source_locator", "decision_by", "decision_record"):
                text(record.get(key), label + "." + key)
            if not valid_datetime(record.get("recorded_at_utc")):
                errors.append(label + ".recorded_at_utc: supply a timezone-aware decision-record time")
            if record.get("value_digest") != value_digest(current):
                errors.append(label + ".value_digest: bind the decision to the current field value")
            if record.get("origin") == "analyst_proposal":
                adoption = obj(record.get("analyst_adoption"), label + ".analyst_adoption")
                text(adoption.get("adopted_by"), label + ".analyst_adoption.adopted_by")
                if not isinstance(adoption.get("source_record_id"), str) or adoption.get("source_record_id") not in sources:
                    errors.append(label + ".analyst_adoption.source_record_id: link explicit human adoption evidence")
                if not valid_datetime(adoption.get("adopted_at_utc")):
                    errors.append(label + ".analyst_adoption.adopted_at_utc: record when human adoption occurred")
    for path in required_provenance_paths(protocol):
        if by_path.get(path, {}).get("decision_status") != "decided":
            errors.append("provenance: " + path + " needs an explicit decided record")
    return errors


def decision_rows(protocol):
    existing = {x.get("field_path"): x for x in objects(protocol.get("provenance")) if isinstance(x.get("field_path"), str)}
    paths = list(dict.fromkeys([*required_provenance_paths(protocol), *existing]))
    rows = []
    for path in paths:
        record = existing.get(path, {})
        try:
            value = pointer_value(protocol, path)
            digest = value_digest(value)
        except ValueError:
            value, digest = None, "UNRESOLVED_POINTER"
        rows.append({"field_path": path, "decision_status": record.get("decision_status", "not_recorded"),
                     "origin": record.get("origin", "not_recorded"), "source_record_ids": json.dumps(record.get("source_record_ids", [])),
                     "source_locator": record.get("source_locator"), "speaker_label": record.get("speaker_label"),
                     "speaker_attribution": record.get("speaker_attribution", "unresolved"),
                     "decision_by": record.get("decision_by"), "decision_record": record.get("decision_record"),
                     "recorded_at_utc": record.get("recorded_at_utc"), "recorded_value_digest": record.get("value_digest"),
                     "current_value_digest": digest, "current_value": json.dumps(value, ensure_ascii=False)})
    return rows


def scaffold_provenance(protocol):
    """Add undecided capture rows; never refresh or adopt an existing decision."""
    if not isinstance(protocol, dict) or type(protocol.get("schema_version")) is not int or protocol["schema_version"] not in {2, 3}:
        raise ValueError("Scaffolding requires a schema_version 2 or 3 protocol")
    if not isinstance(protocol.get("provenance"), list):
        raise ValueError("Existing provenance must be a list; repair it explicitly")
    result = copy.deepcopy(protocol)
    existing = {r.get("field_path") for r in objects(result["provenance"]) if isinstance(r.get("field_path"), str)}
    for path in required_provenance_paths(result):
        if path in existing:
            continue
        record = provenance_record(path)
        try:
            record["value_digest"] = value_digest(pointer_value(result, path))
        except ValueError:
            pass
        result["provenance"].append(record)
    return result


def csv_text(rows, headers):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=headers, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def cell(value):
    if value is None or value == "" or value == []:
        return "Missing"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    return html.escape(str(value), quote=False).replace("|", "\\|").replace("\n", " ")


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |",
                      *("| " + " | ".join(cell(x) for x in row) + " |" for row in rows)])


def structured_packet(protocol):
    lines = ["## Structured scientific records (schema v2)", "",
             "These records supplement the OSF form. Mechanical validation checks declared decisions and consistency; scientific adequacy and actual agreement remain human responsibilities.", ""]
    for claim in objects(protocol.get("claim_measure_map")):
        lines.extend(["### Claim-to-measure map: " + cell(claim.get("hypothesis_id")), "",
                      table(["Decision", "Specification"], [(key.replace("_", " "), claim.get(key)) for key in CLAIM_FIELDS] +
                            [("component IDs", claim.get("component_ids")), ("directly encoded effect", claim.get("directly_encoded_effect")),
                             ("interpretation of encoded effect", claim.get("encoded_effect_implications"))]), "",
                      table(["Rival explanation", "Discriminating control", "Distinguishing result"],
                            [(r.get("explanation"), r.get("discriminating_control"), r.get("distinguishing_result")) for r in objects(claim.get("rival_explanations"))]), "",
                      "Expected result patterns: " + cell(claim.get("expected_result_patterns")), ""])
    lines.extend(["### Component status", "", table(["ID / component", "Implementation", "Evidence", "Included?", "Artifacts / sources"],
                  [(str(c.get("id")) + " / " + str(c.get("name")), c.get("implementation_status"), c.get("evidence_status"), c.get("included_in_study"),
                    {"artifacts": c.get("artifact_ids"), "sources": c.get("source_record_ids")}) for c in objects(protocol.get("components"))]), ""])
    learning = protocol.get("learning", {})
    learning = learning if isinstance(learning, dict) else {}
    lines.extend(["### Calibration, state dynamics, and learning", "", table(["Phase", "Declaration"], [(key.replace("_", " "), learning.get(key)) for key in ("offline_calibration", "within_run_state", "online_updates")]), ""])
    handoff = protocol.get("artifact_handoff", {})
    handoff = handoff if isinstance(handoff, dict) else {}
    access = protocol.get("results_access", {})
    access = access if isinstance(access, dict) else {}
    prior = objects(access.get("prior_results"))
    lines.extend(["### Artifact handoff", "", table(["ID / kind", "Status", "Location", "Pin", "Owner / reason"],
                  [(str(a.get("id")) + " / " + str(a.get("kind")), a.get("status"), a.get("location"), a.get("sha256") or a.get("immutable_version"),
                    {"owner": a.get("owner"), "reason": a.get("reason")}) for a in objects(handoff.get("items"))]), "",
                  "Handoff confirmation: " + cell({key: handoff.get(key) for key in ("confirmed_by", "confirmed_at_utc")}), "",
                  "### Prior results and prospective boundary", "",
                  table(["Declaration", "Value"], [(key.replace("_", " "), access.get(key)) for key in
                        ("declaration_status", "declared_by", "declared_at_utc", "registration_scope", "confirmatory_status",
                         "prospective_scope", "reserved_runs_or_conditions", "access_controls")]), "",
                  table(["Previous result", "Who / when", "Conditions / use", "Design influence / sources"],
                        [(r.get("description"), {"who": r.get("who_saw"), "when": r.get("seen_when")},
                          {"conditions": r.get("conditions_or_runs"), "use": r.get("use")},
                          {"influence": r.get("influence_on_design"), "sources": r.get("source_record_ids")}) for r in prior]) if prior
                  else "No-prior-results explanation: " + cell(access.get("no_prior_results_reason")), "",
                  "### Per-field provenance", "", "The full decision ledger includes current value digests in `decision_ledger.csv`. Unknown speakers remain unresolved; proposals require explicit adoption.", "",
                  table(["Field", "Decision / origin", "Source / locator", "Speaker attribution", "Decision owner"],
                        [(r["field_path"], r["decision_status"] + " / " + r["origin"], str(r["source_record_ids"]) + " / " + str(r["source_locator"]),
                          str(r["speaker_attribution"]) + " / " + str(r["speaker_label"]), r["decision_by"]) for r in decision_rows(protocol)]), ""])
    return "\n".join(lines)
