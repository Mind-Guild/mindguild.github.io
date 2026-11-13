"""Declared test severity and interpretation contracts for schema v3.

Original Mind Guild engineering choices informed by adversarial theory testing.
These checks do not authenticate review, validate scientific bridges, retrieve
artifacts, or establish consciousness. Calibration is conditional on its model.
"""
from __future__ import annotations

import copy
import math

import protocol_v2 as capture

OUTCOMES = ("target_only", "rival_only", "both", "neither", "inconclusive", "invalid")
SCENARIOS = ("null", "target", "rival")
CONTRACT_GROUPS = ("inference", "accounts", "contrasts", "design_assurance", "critical_review", "execution")


def new_contrast(hypothesis_id="H1"):
    return {"hypothesis_id": hypothesis_id, "target_account_id": "T1", "rival_account_id": "T2",
            "estimand": None, "interval_method": None, "multiplicity_rule": None,
            "diagnosticity_reason": None, "resource_matching": None,
            "prediction_regions": [{"account_id": aid, "specified": None, "lower": None, "upper": None,
                                    "derivation": None} for aid in ("T1", "T2")],
            "interpretations": {key: None for key in OUTCOMES},
            "validity_checks": [{"kind": kind, "pass_rule": None, "passed": None,
                                 "evidence_artifact_id": None, "failure_action": None}
                                for kind in ("measurement", "implementation", "negative_control")]}


def new_contract(hypothesis_ids=("H1",)):
    return {
        "inference": {"study_type": None, "target_level": None, "phenomenon": None,
                      "allowed_conclusion": None, "excluded_conclusions": [],
                      "theory_core_vs_implementation": None, "consciousness_inference": None},
        "accounts": [{"id": aid, "name": None, "version": None, "kind": None,
                      "source_record_ids": [], "component_ids": [], "commitment": None,
                      "implementation_assumptions": None,
                      "bridge_assumptions": [{"assumption": None, "test_or_justification": None,
                                              "violation_implication": None}]}
                     for aid in ("T1", "T2")],
        "contrasts": [new_contrast(hid) for hid in hypothesis_ids],
        "design_assurance": [{"hypothesis_id": hid, "strategy": None, "independent_unit": None,
                              "planned_repetitions": None, "minimum_effect_magnitude": None,
                              "effect_scale_and_justification": None, "assumptions_and_range": None,
                              "calibration_sampling": None, "evidence_artifact_id": None,
                              "calibration_basis_sha256": None,
                              "maximum_interval_width": None, "criteria": []}
                             for hid in hypothesis_ids],
        "critical_review": {"coordinator": None, "coordinator_conflicts": None, "roles_overlap": None,
                            "overlap_reason": None, "disagreement_resolution": None, "unresolved_disputes": [],
                            "perspectives": [{"account_id": aid, "reviewer_name": None, "relationship": None,
                                              "conflicts": None, "endorsement_source_id": None}
                                             for aid in ("T1", "T2")]},
        "execution": {
            "masking": {"mode": None, "method_or_limitation": None, "custodian": None, "analyst": None,
                        "analysis_lock_artifact_id": None, "unblinding_gate": None, "access_log_location": None},
            "replication": {"mode": None, "reserved_seed_blocks": [], "independent_code_artifact_id": None,
                            "independence_basis_or_limitation": None, "release_trigger": None,
                            "analysis_and_pooling_rule": None, "failure_interpretation": None},
            "reporting": {"all_registered_hypotheses": None, "all_attempts": None,
                          "full_outcome_matrix": None, "deviations_with_exposure": None,
                          "outcome_independent_release": None, "release_location": None,
                          "release_deadline_rule": None, "amendment_rule": None,
                          "interpretation_revision_rule": None},
        },
    }


def critical_review_blank():
    return {"reviewer_name": None, "approved": False, "reviewed_at_utc": None,
            "review_digest": None, "notes": None, "perspective_records": []}


def migrate_to_v3(protocol, original_sha256=None):
    """Preserve original records/history; never infer scientific commitments."""
    if not isinstance(protocol, dict) or type(protocol.get("schema_version")) is not int or protocol["schema_version"] not in {1, 2}:
        raise ValueError("Migration requires a schema_version 1 or 2 protocol")
    if "test_contract" in protocol:
        raise ValueError("Legacy input already contains test_contract; reconcile it explicitly")
    old = copy.deepcopy(protocol)
    result = capture.migrate_v1(protocol, original_sha256) if protocol["schema_version"] == 1 else copy.deepcopy(protocol)
    hids = [h.get("id") for h in capture.objects(result.get("hypotheses"))
            if h.get("classification") in {"primary", "secondary"}]
    result["test_contract"] = new_contract(hids)
    result["schema_version"] = 3
    result["status"] = "draft"
    result["reviews"] = {role: {"reviewer_name": None, "approved": False, "reviewed_at_utc": None,
                               "review_digest": None, "notes": None}
                         for role in ("science", "implementation", "analysis")}
    result["reviews"]["critical"] = critical_review_blank()
    result["migration"] = {"from_schema_version": old["schema_version"],
                           "original_protocol_sha256": original_sha256 or capture.value_digest(old),
                           "original_hash_basis": "file_bytes" if original_sha256 else "canonical_json",
                           "previous_status": old.get("status"), "previous_reviews": old.get("reviews"),
                           "previous_migration": old.get("migration"),
                           "note": "Original study records preserved. New test contract unresolved; all active reviews require renewal."}
    if not isinstance(result.get("open_decisions"), list):
        result["open_decisions"] = []
    result["open_decisions"].append({"id": "V3_TEST_CONTRACT", "decision": "Resolve the inference, prediction, assurance, critical-review, and execution contract.", "owner": None})
    return result


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def bounds(region):
    if not isinstance(region, dict) or region.get("specified") is not True:
        raise ValueError("Prediction is not specified")
    lo, hi = region.get("lower"), region.get("upper")
    if lo is None and hi is None:
        raise ValueError("A prediction needs at least one finite bound")
    if any(x is not None and not finite_number(x) for x in (lo, hi)):
        raise ValueError("Prediction bounds must be finite numbers or null")
    lo, hi = (-math.inf if lo is None else lo), (math.inf if hi is None else hi)
    if lo > hi:
        raise ValueError("Prediction lower bound exceeds upper bound")
    return lo, hi


def discriminating(contrast):
    """Each account must allow a nonempty outcome region the other excludes."""
    regions = {r.get("account_id"): r for r in capture.objects(contrast.get("prediction_regions"))
               if isinstance(r.get("account_id"), str)}
    try:
        a = bounds(regions[contrast["target_account_id"]])
        b = bounds(regions[contrast["rival_account_id"]])
    except (KeyError, TypeError, ValueError):
        return False
    return (a[0] < b[0] or a[1] > b[1]) and (b[0] < a[0] or b[1] > a[1])


def adjudicate(contrast, interval, valid=True):
    """Apply closed prediction regions to a prespecified uncertainty interval.

    This is a compatibility table, not an automatic verdict on a theory.
    Partial intersection is inconclusive, never a null result or refutation.
    """
    if type(valid) is not bool:
        raise ValueError("valid must be true or false")
    if not isinstance(interval, list) or len(interval) != 2 or not all(finite_number(x) for x in interval) or interval[0] > interval[1]:
        raise ValueError("Supply an ordered finite two-number uncertainty interval")
    if not valid:
        return "invalid"
    regions = {r.get("account_id"): r for r in capture.objects(contrast.get("prediction_regions"))
               if isinstance(r.get("account_id"), str)}
    states = []
    for aid in (contrast.get("target_account_id"), contrast.get("rival_account_id")):
        try:
            lo, hi = bounds(regions[aid])
        except (KeyError, TypeError, ValueError):
            return "inconclusive"
        if lo <= interval[0] <= interval[1] <= hi:
            states.append("compatible")
        elif interval[1] < lo or interval[0] > hi:
            states.append("incompatible")
        else:
            states.append("uncertain")
    if "uncertain" in states:
        return "inconclusive"
    return {("compatible", "compatible"): "both", ("incompatible", "incompatible"): "neither",
            ("compatible", "incompatible"): "target_only", ("incompatible", "compatible"): "rival_only"}[tuple(states)]


def wilson95(count, total):
    """Two-sided 95% Wilson interval; independent Bernoulli calibration draws."""
    if type(count) is not int or type(total) is not int or total < 2 or count < 0 or count > total:
        raise ValueError("Use integer counts with 0 <= count <= total and total >= 2")
    z = 1.959963984540054
    p = count / total
    denominator = 1 + z*z/total
    center = (p + z*z/(2*total))/denominator
    radius = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total))/denominator
    return max(0.0, center-radius), min(1.0, center+radius)


def assurance_summary(protocol):
    contract = protocol.get("test_contract", {})
    contract = contract if isinstance(contract, dict) else {}
    rows = []
    for a in capture.objects(contract.get("design_assurance")):
        for c in capture.objects(a.get("criteria")):
            try:
                lo, hi = wilson95(c.get("count"), c.get("total"))
                threshold = c.get("threshold")
                met = finite_number(threshold) and ((hi <= threshold) if c.get("direction") == "at_most" else (lo >= threshold))
            except ValueError:
                lo = hi = None
                met = False
            rows.append({"hypothesis_id": a.get("hypothesis_id"), "scenario": c.get("scenario"),
                         "event": c.get("event"), "count": c.get("count"), "total": c.get("total"),
                         "wilson95_lower": lo, "wilson95_upper": hi, "direction": c.get("direction"),
                         "threshold": c.get("threshold"), "criterion_met": met})
    return rows


def assurance_basis_digest(protocol, hypothesis_id):
    """Bind calibration to scientific choices without a report/hash cycle.

    Outcome counts, report artifacts, provenance and review attestations are
    excluded. Changing decision thresholds, generators, sample sizes, models,
    learning rules or the interpretation contract invalidates calibration.
    """
    contract = protocol.get("test_contract", {})
    contract = contract if isinstance(contract, dict) else {}
    assurance = next((a for a in capture.objects(contract.get("design_assurance")) if a.get("hypothesis_id") == hypothesis_id), {})
    plan = {k: v for k, v in assurance.items() if k not in {"criteria", "evidence_artifact_id", "calibration_basis_sha256"}}
    plan["criteria"] = [{k: v for k, v in c.items() if k not in {"count", "total"}}
                        for c in capture.objects(assurance.get("criteria"))]
    basis = {k: protocol.get(k) for k in ("sections", "execution", "hypotheses", "claim_measure_map", "components", "learning", "artifacts")}
    basis.update(inference=contract.get("inference"), accounts=contract.get("accounts"),
                 contrasts=contract.get("contrasts"), assurance_plan=plan)
    return capture.value_digest(basis)


def prediction_rows(protocol):
    contract = protocol.get("test_contract", {})
    contract = contract if isinstance(contract, dict) else {}
    return [{"hypothesis_id": c.get("hypothesis_id"), "account_id": r.get("account_id"),
             "estimand": c.get("estimand"), "specified": r.get("specified"), "lower_inclusive": r.get("lower"),
             "upper_inclusive": r.get("upper"), "derivation": r.get("derivation"),
             "both_exclusive_regions_exist": discriminating(c)}
            for c in capture.objects(contract.get("contrasts")) for r in capture.objects(c.get("prediction_regions"))]


def validate_v3(protocol, review_digest):
    errors = []

    def obj(v, label):
        if not isinstance(v, dict): errors.append(label + ": supply an object"); return {}
        return v

    def array(v, label, nonempty=False):
        if not isinstance(v, list) or (nonempty and not v): errors.append(label + ": supply a list" + (" with entries" if nonempty else "")); return []
        return v

    def text(v, label):
        if not isinstance(v, str) or not v.strip() or capture.PLACEHOLDER.search(v): errors.append(label + ": supply resolved, specific text")

    def enum(v, allowed, label):
        if not isinstance(v, str) or v not in allowed: errors.append(label + ": choose " + ", ".join(sorted(allowed)))

    def boolean(v, label):
        if type(v) is not bool: errors.append(label + ": explicitly choose true or false")

    def texts(v, label):
        for i, item in enumerate(array(v, label, True)): text(item, label + f"[{i}]")

    def refs(v, allowed, label, nonempty=True):
        seq = array(v, label, nonempty)
        if any(not isinstance(x, str) or x not in allowed for x in seq): errors.append(label + ": reference existing IDs")
        elif len(seq) != len(set(seq)): errors.append(label + ": IDs must be unique")

    sources = {s.get("id") for s in capture.objects(protocol.get("source_records")) if isinstance(s.get("id"), str)}
    components = {c.get("id") for c in capture.objects(protocol.get("components")) if c.get("included_in_study") is True and isinstance(c.get("id"), str)}
    handoff = protocol.get("artifact_handoff", {})
    items = capture.objects(handoff.get("items")) if isinstance(handoff, dict) else []
    artifacts = {a.get("id"): a for a in items if isinstance(a.get("id"), str)}

    def artifact(aid, label, report=False):
        a = artifacts.get(aid) if isinstance(aid, str) else None
        if not a or a.get("status") != "captured" or (report and (a.get("kind") != "analysis" or not isinstance(a.get("sha256"), str))):
            errors.append(label + ": reference a captured" + (" SHA-256-pinned analysis report" if report else " artifact"))

    contract = obj(protocol.get("test_contract"), "test_contract")
    inf = obj(contract.get("inference"), "test_contract.inference")
    enum(inf.get("study_type"), {"mechanism_benchmark", "theory_discrimination"}, "test_contract.inference.study_type")
    enum(inf.get("target_level"), {"functional_performance", "computational_mechanism", "theory_prediction"}, "test_contract.inference.target_level")
    enum(inf.get("consciousness_inference"), {"not_assessed", "conditional_on_bridge_assumptions"}, "test_contract.inference.consciousness_inference")
    for k in ("phenomenon", "allowed_conclusion", "theory_core_vs_implementation"): text(inf.get(k), "test_contract.inference." + k)
    texts(inf.get("excluded_conclusions"), "test_contract.inference.excluded_conclusions")
    if inf.get("study_type") == "mechanism_benchmark" and (inf.get("target_level") == "theory_prediction" or inf.get("consciousness_inference") != "not_assessed"):
        errors.append("test_contract.inference: a mechanism benchmark cannot claim a consciousness-theory test")
    if inf.get("study_type") == "theory_discrimination" and inf.get("target_level") != "theory_prediction":
        errors.append("test_contract.inference: theory discrimination must name theory_prediction as its target")

    accounts, seen = {}, []
    for i, value in enumerate(array(contract.get("accounts"), "test_contract.accounts", True)):
        label = f"test_contract.accounts[{i}]"; a = obj(value, label)
        for k in ("id", "name", "version", "commitment", "implementation_assumptions"): text(a.get(k), label + "." + k)
        aid = a.get("id")
        if isinstance(aid, str): accounts[aid] = a; seen.append(aid)
        enum(a.get("kind"), {"mechanistic_account", "theory"}, label + ".kind")
        refs(a.get("source_record_ids"), sources, label + ".source_record_ids")
        refs(a.get("component_ids"), components, label + ".component_ids", False)
        for j, b in enumerate(array(a.get("bridge_assumptions"), label + ".bridge_assumptions", True)):
            b = obj(b, label + f".bridge_assumptions[{j}]")
            for k in ("assumption", "test_or_justification", "violation_implication"): text(b.get(k), label + f".bridge_assumptions[{j}]." + k)
    if len(seen) != len(set(seen)): errors.append("test_contract.accounts: duplicate account IDs")
    if len(accounts) < 2: errors.append("test_contract.accounts: name at least two competing explanations; a benchmark can use mechanistic accounts")
    if inf.get("study_type") == "theory_discrimination" and not any(a.get("kind") == "theory" for a in accounts.values()):
        errors.append("test_contract.accounts: a theory-discrimination claim requires an explicitly versioned theory account")

    hypotheses = {h.get("id"): h for h in capture.objects(protocol.get("hypotheses")) if isinstance(h.get("id"), str)}
    confirmatory = {hid for hid, h in hypotheses.items() if h.get("classification") in {"primary", "secondary"}}
    claims = {c.get("hypothesis_id"): c for c in capture.objects(protocol.get("claim_measure_map")) if isinstance(c.get("hypothesis_id"), str)}
    mapped = []
    for i, value in enumerate(array(contract.get("contrasts"), "test_contract.contrasts", True)):
        label = f"test_contract.contrasts[{i}]"; c = obj(value, label); hid = c.get("hypothesis_id")
        if not isinstance(hid, str) or hid not in confirmatory: errors.append(label + ".hypothesis_id: link a confirmatory hypothesis")
        else: mapped.append(hid)
        for k in ("estimand", "interval_method", "multiplicity_rule", "diagnosticity_reason", "resource_matching"): text(c.get(k), label + "." + k)
        if isinstance(hid, str) and hid in claims and c.get("estimand") != claims[hid].get("estimand"):
            errors.append(label + ".estimand: must equal the linked claim_measure_map estimand")
        pair = [c.get("target_account_id"), c.get("rival_account_id")]
        refs(pair, accounts, label + ".account_ids")
        regions = array(c.get("prediction_regions"), label + ".prediction_regions", True)
        region_ids = []
        for j, r in enumerate(regions):
            rlabel = label + f".prediction_regions[{j}]"; r = obj(r, rlabel)
            aid = r.get("account_id")
            if isinstance(aid, str): region_ids.append(aid)
            boolean(r.get("specified"), rlabel + ".specified"); text(r.get("derivation"), rlabel + ".derivation")
            if r.get("specified") is True:
                try: bounds(r)
                except ValueError as e: errors.append(rlabel + ": " + str(e))
            elif r.get("specified") is False and (r.get("lower") is not None or r.get("upper") is not None):
                errors.append(rlabel + ": no-prediction records must not contain bounds")
        if len(regions) != 2 or len(region_ids) != 2 or set(region_ids) != {x for x in pair if isinstance(x, str)}:
            errors.append(label + ": supply one prediction region for each of the two linked accounts")
        if inf.get("study_type") == "theory_discrimination" and isinstance(hid, str) and hypotheses.get(hid, {}).get("classification") == "primary" and not discriminating(c):
            errors.append(label + ": the primary theory test needs an exclusive possible result for each account; shared/unspecified predictions cannot discriminate")
        interpretations = obj(c.get("interpretations"), label + ".interpretations")
        for key in OUTCOMES: text(interpretations.get(key), label + ".interpretations." + key)
        checks = array(c.get("validity_checks"), label + ".validity_checks", True)
        kinds = []
        for j, check in enumerate(checks):
            qlabel = label + f".validity_checks[{j}]"; check = obj(check, qlabel); kinds.append(check.get("kind"))
            for key in ("pass_rule", "failure_action"): text(check.get(key), qlabel + "." + key)
            if check.get("passed") is not True: errors.append(qlabel + ".passed: measurement/implementation/control checks must pass before freeze")
            artifact(check.get("evidence_artifact_id"), qlabel + ".evidence_artifact_id", True)
        for kind in ("measurement", "implementation", "negative_control"):
            if kind not in kinds: errors.append(label + ".validity_checks: missing " + kind)
    if len(mapped) != len(set(mapped)): errors.append("test_contract.contrasts: duplicate hypothesis mapping")
    for hid in sorted(confirmatory - set(mapped)): errors.append("test_contract.contrasts: missing confirmatory hypothesis " + hid)

    execution = protocol.get("execution", {}); execution = execution if isinstance(execution, dict) else {}
    assured = []
    for i, value in enumerate(array(contract.get("design_assurance"), "test_contract.design_assurance", True)):
        label = f"test_contract.design_assurance[{i}]"; a = obj(value, label); hid = a.get("hypothesis_id")
        if not isinstance(hid, str) or hid not in confirmatory: errors.append(label + ".hypothesis_id: link a confirmatory hypothesis")
        else: assured.append(hid)
        enum(a.get("strategy"), {"decision_errors", "precision"}, label + ".strategy")
        for k in ("independent_unit", "effect_scale_and_justification", "assumptions_and_range", "calibration_sampling"): text(a.get(k), label + "." + k)
        if a.get("independent_unit") != execution.get("independent_unit"): errors.append(label + ".independent_unit: must match execution.independent_unit")
        if type(a.get("planned_repetitions")) is not int or a.get("planned_repetitions") != execution.get("n_independent_repetitions"):
            errors.append(label + ".planned_repetitions: must match the planned independent repetition count")
        if not finite_number(a.get("minimum_effect_magnitude")) or a.get("minimum_effect_magnitude", 0) <= 0:
            errors.append(label + ".minimum_effect_magnitude: justify a positive numeric minimum meaningful effect")
        artifact(a.get("evidence_artifact_id"), label + ".evidence_artifact_id", True)
        if a.get("calibration_basis_sha256") != assurance_basis_digest(protocol, hid):
            errors.append(label + ".calibration_basis_sha256: calibration is missing or stale for the current generator, decision contract, or design; rerun/review it")
        if a.get("strategy") == "precision":
            if not finite_number(a.get("maximum_interval_width")) or a.get("maximum_interval_width", 0) <= 0: errors.append(label + ".maximum_interval_width: supply a positive width on the estimand scale")
            if inf.get("study_type") == "theory_discrimination": errors.append(label + ": a theory-discrimination claim needs decision_errors calibration, not precision alone")
        required = {(s, e, d) for s, e, d in (("null", "target_only", "at_most"), ("target", "target_only", "at_least"), ("rival", "rival_only", "at_least"))} if a.get("strategy") == "decision_errors" else {(s, e, "at_least") for s in SCENARIOS for e in ("precision_achieved", "coverage")}
        required |= {(s, "invalid", "at_most") for s in SCENARIOS}
        observed = []
        for j, v in enumerate(array(a.get("criteria"), label + ".criteria", True)):
            rlabel = label + f".criteria[{j}]"; c = obj(v, rlabel)
            enum(c.get("scenario"), set(SCENARIOS), rlabel + ".scenario")
            enum(c.get("event"), {"target_only", "rival_only", "precision_achieved", "coverage", "invalid"}, rlabel + ".event")
            enum(c.get("direction"), {"at_most", "at_least"}, rlabel + ".direction")
            text(c.get("scenario_definition"), rlabel + ".scenario_definition")
            identity = (c.get("scenario"), c.get("event"), c.get("direction"))
            if all(isinstance(x, str) for x in identity): observed.append(identity)
            threshold = c.get("threshold")
            if not finite_number(threshold) or not 0 < threshold < 1: errors.append(rlabel + ".threshold: supply a probability strictly between 0 and 1")
            try:
                lo, hi = wilson95(c.get("count"), c.get("total"))
                if finite_number(threshold) and ((c.get("direction") == "at_most" and hi > threshold) or (c.get("direction") == "at_least" and lo < threshold)):
                    errors.append(rlabel + ": 95% Wilson bound does not meet the prespecified assurance threshold")
            except ValueError as e: errors.append(rlabel + ": " + str(e))
        for key in sorted(required - set(observed)): errors.append(label + ".criteria: missing scenario/event/direction " + "/".join(key))
        if len(observed) != len(set(observed)): errors.append(label + ".criteria: duplicate scenario/event/direction")
        for scenario in SCENARIOS:
            rows = [r for r in capture.objects(a.get("criteria")) if r.get("scenario") == scenario]
            totals = [r.get("total") for r in rows]
            if totals and all(type(n) is int for n in totals) and len(set(totals)) != 1:
                errors.append(label + ".criteria: events in one scenario must use the same complete-run denominator")
            counts = {r.get("event"): r.get("count") for r in rows if isinstance(r.get("event"), str)}
            invalid = counts.get("invalid")
            if totals and type(totals[0]) is int and type(invalid) is int:
                for event in ("target_only", "rival_only", "precision_achieved", "coverage"):
                    if type(counts.get(event)) is int and counts[event] + invalid > totals[0]:
                        errors.append(label + ".criteria: invalid and valid-event counts contradict the scenario denominator")
                if all(type(counts.get(k)) is int for k in ("target_only", "rival_only")) and counts["target_only"] + counts["rival_only"] + invalid > totals[0]:
                    errors.append(label + ".criteria: mutually exclusive outcome counts exceed the scenario denominator")
    if len(assured) != len(set(assured)): errors.append("test_contract.design_assurance: duplicate hypothesis mapping")
    for hid in sorted(confirmatory - set(assured)): errors.append("test_contract.design_assurance: missing confirmatory hypothesis " + hid)

    critical = obj(contract.get("critical_review"), "test_contract.critical_review")
    for k in ("coordinator", "coordinator_conflicts", "disagreement_resolution"): text(critical.get(k), "test_contract.critical_review." + k)
    boolean(critical.get("roles_overlap"), "test_contract.critical_review.roles_overlap")
    if critical.get("roles_overlap") is True: text(critical.get("overlap_reason"), "test_contract.critical_review.overlap_reason")
    if critical.get("unresolved_disputes") != []: errors.append("test_contract.critical_review.unresolved_disputes: resolve design/interpretation disputes or narrow the study before freeze")
    reviewers, names = {}, [critical.get("coordinator")]
    for i, v in enumerate(array(critical.get("perspectives"), "test_contract.critical_review.perspectives", True)):
        label = f"test_contract.critical_review.perspectives[{i}]"; p = obj(v, label); aid = p.get("account_id")
        if not isinstance(aid, str) or aid not in accounts: errors.append(label + ".account_id: link an account")
        elif aid in reviewers: errors.append(label + ": duplicate account perspective")
        else: reviewers[aid] = p
        for k in ("reviewer_name", "conflicts"): text(p.get(k), label + "." + k)
        names.append(p.get("reviewer_name"))
        enum(p.get("relationship"), {"proponent", "informed_proxy", "internal_critic"}, label + ".relationship")
        if p.get("relationship") == "proponent" and (not isinstance(p.get("endorsement_source_id"), str) or p.get("endorsement_source_id") not in sources):
            errors.append(label + ".endorsement_source_id: substantiate actual proponent involvement; otherwise label an informed proxy or internal critic")
    for aid in accounts:
        if aid not in reviewers: errors.append("test_contract.critical_review: missing perspective for " + aid)
    real_names = [n for n in names if isinstance(n, str)]
    if len(real_names) != len(set(real_names)) and critical.get("roles_overlap") is not True:
        errors.append("test_contract.critical_review: disclose overlapping people/roles and the resulting limitation")

    review = obj(protocol.get("reviews"), "reviews").get("critical", {})
    review = obj(review, "reviews.critical")
    accepted = []
    for i, v in enumerate(array(review.get("perspective_records"), "reviews.critical.perspective_records", True)):
        label = f"reviews.critical.perspective_records[{i}]"; r = obj(v, label); aid = r.get("account_id")
        if not isinstance(aid, str) or aid not in reviewers: errors.append(label + ".account_id: link an assigned perspective")
        else:
            accepted.append(aid)
            if r.get("reviewer_name") != reviewers[aid].get("reviewer_name"): errors.append(label + ": reviewer must match the assigned perspective")
        if r.get("design_and_interpretation_accepted") is not True: errors.append(label + ": explicit acceptance of design and outcome interpretations is required, not agreement with the theory")
        refs(r.get("source_record_ids"), sources, label + ".source_record_ids")
        text(r.get("source_locator"), label + ".source_locator")
        if not capture.valid_datetime(r.get("reviewed_at_utc")): errors.append(label + ".reviewed_at_utc: record a timezone-aware acceptance time")
    if len(accepted) != len(set(accepted)): errors.append("reviews.critical: duplicate account acceptance")
    for aid in reviewers:
        if aid not in accepted: errors.append("reviews.critical: missing design/interpretation acceptance for " + aid)
    if review.get("reviewer_name") != critical.get("coordinator"): errors.append("reviews.critical: coordinator name must match the declared critical-review plan")
    if review.get("approved") is not True: errors.append("reviews.critical: approval is not recorded")
    if not capture.valid_datetime(review.get("reviewed_at_utc")): errors.append("reviews.critical: supply a timezone-aware review time")
    if review.get("review_digest") != review_digest: errors.append("reviews.critical: review digest does not match the current protocol")

    work = obj(contract.get("execution"), "test_contract.execution")
    mask = obj(work.get("masking"), "test_contract.execution.masking")
    enum(mask.get("mode"), {"masked", "open_with_justification"}, "test_contract.execution.masking.mode")
    for k in ("method_or_limitation", "custodian", "analyst", "access_log_location"): text(mask.get(k), "test_contract.execution.masking." + k)
    if mask.get("mode") == "masked" and mask.get("custodian") == mask.get("analyst"): errors.append("test_contract.execution.masking: masked access needs a separate custodian or an explicit open-with-justification limitation")
    if mask.get("unblinding_gate") != "registration_archived_and_analysis_locked": errors.append("test_contract.execution.masking.unblinding_gate: require registration_archived_and_analysis_locked")
    artifact(mask.get("analysis_lock_artifact_id"), "test_contract.execution.masking.analysis_lock_artifact_id")
    rep = obj(work.get("replication"), "test_contract.execution.replication")
    enum(rep.get("mode"), {"reserved_runs", "independent_implementation", "none_with_reason"}, "test_contract.execution.replication.mode")
    for k in ("independence_basis_or_limitation", "release_trigger", "analysis_and_pooling_rule", "failure_interpretation"): text(rep.get(k), "test_contract.execution.replication." + k)
    seeds = array(rep.get("reserved_seed_blocks"), "test_contract.execution.replication.reserved_seed_blocks")
    valid_seeds = all(type(x) is int and x >= 0 for x in seeds)
    if not valid_seeds or (valid_seeds and len(seeds) != len(set(seeds))): errors.append("test_contract.execution.replication.reserved_seed_blocks: use unique nonnegative integer block seeds")
    if rep.get("mode") == "reserved_runs":
        planned = execution.get("confirmatory_seed_blocks", [])
        planned = planned if isinstance(planned, list) and all(type(x) is int for x in planned) else []
        if valid_seeds and (len(seeds) < 2 or not set(seeds) <= set(planned) or len(set(planned) - set(seeds)) < 2):
            errors.append("test_contract.execution.replication: reserve at least two planned blocks and leave at least two for the initial test")
    elif seeds: errors.append("test_contract.execution.replication: reserved seed blocks apply only to reserved_runs")
    if rep.get("mode") == "independent_implementation":
        aid = rep.get("independent_code_artifact_id"); artifact(aid, "test_contract.execution.replication.independent_code_artifact_id")
        if isinstance(aid, str) and artifacts.get(aid, {}).get("kind") == "code": errors.append("test_contract.execution.replication: reference a separately pinned independent implementation, not the primary code artifact")
    elif rep.get("independent_code_artifact_id") is not None: errors.append("test_contract.execution.replication: clear independent_code_artifact_id unless that mode is selected")
    if inf.get("study_type") == "theory_discrimination" and rep.get("mode") == "none_with_reason": errors.append("test_contract.execution.replication: a theory-discrimination study needs a reserved-run or independent-implementation replication plan")
    reporting = obj(work.get("reporting"), "test_contract.execution.reporting")
    for k in ("all_registered_hypotheses", "all_attempts", "full_outcome_matrix", "deviations_with_exposure", "outcome_independent_release"):
        if reporting.get(k) is not True: errors.append("test_contract.execution.reporting." + k + ": commit to reporting regardless of favorable, unfavorable, inconclusive, or invalid outcomes")
    for k in ("release_location", "release_deadline_rule", "amendment_rule", "interpretation_revision_rule"): text(reporting.get(k), "test_contract.execution.reporting." + k)
    return errors


def structured_packet(protocol):
    c = protocol.get("test_contract", {}); c = c if isinstance(c, dict) else {}
    lines = ["## Test and interpretation contract (schema v3)", "",
             "This is Mind Guild's methodological adaptation, not a review or endorsement by Lucia Melloni or COGITATE. Compatibility categories test the stated operational predictions; they do not establish consciousness or eliminate an entire theory.", "",
             capture.table(["Inference decision", "Commitment"], [(k, v) for k, v in (c.get("inference") or {}).items()]) if isinstance(c.get("inference"), dict) else "Missing inference contract.", "",
             "### Competing accounts and bridge assumptions", "",
             capture.table(["Account / version", "Commitment", "Implementation / bridges"],
                           [(str(a.get("id")) + " / " + str(a.get("name")) + " / " + str(a.get("version")), a.get("commitment"),
                             {"components": a.get("component_ids"), "implementation": a.get("implementation_assumptions"), "bridges": a.get("bridge_assumptions")})
                            for a in capture.objects(c.get("accounts"))]), "",
             "### Quantitative prediction matrix", "", "Bounds are inclusive; null is unbounded. Apply the declared uncertainty interval, not a significance label. A partial intersection is inconclusive. No prediction is not a prediction of no effect.", "",
             capture.table(["Hypothesis", "Account", "Specified?", "Lower", "Upper", "Derivation"],
                           [(r["hypothesis_id"], r["account_id"], r["specified"], r["lower_inclusive"], r["upper_inclusive"], r["derivation"]) for r in prediction_rows(protocol)]), ""]
    for contrast in capture.objects(c.get("contrasts")):
        lines.extend(["### Outcomes and validity: " + capture.cell(contrast.get("hypothesis_id")), "",
                      capture.table(["Result pattern", "Agreed interpretation"], [(k, (contrast.get("interpretations") or {}).get(k)) for k in OUTCOMES]) if isinstance(contrast.get("interpretations"), dict) else "Missing outcome matrix.", "",
                      "Both accounts have an exclusive possible result: " + str(discriminating(contrast)), "",
                      capture.table(["Test decision", "Specification"], [(k, contrast.get(k)) for k in ("estimand", "interval_method", "multiplicity_rule", "diagnosticity_reason", "resource_matching", "validity_checks")]), ""])
    lines.extend(["### Design assurance", "", "95% Wilson intervals describe calibration-rate Monte Carlo uncertainty under independent calibration draws. Passing is conditional on the stated synthetic generator and assumptions. These are not confirmatory study results.", "",
                  capture.table(["Hypothesis", "Scenario / event", "Count / total", "95% Wilson interval", "Criterion", "Met?"],
                                [(r["hypothesis_id"], str(r["scenario"]) + " / " + str(r["event"]), str(r["count"]) + " / " + str(r["total"]),
                                  [r["wilson95_lower"], r["wilson95_upper"]], str(r["direction"]) + " " + str(r["threshold"]), r["criterion_met"]) for r in assurance_summary(protocol)]), "",
                  capture.table(["Hypothesis", "Assurance assumptions"], [(a.get("hypothesis_id"), a) for a in capture.objects(c.get("design_assurance"))]), "",
                  "### Critical review and execution safeguards", "",
                  capture.table(["Commitment", "Specification"], [("critical review", c.get("critical_review")), ("masking / replication / reporting", c.get("execution"))]), ""])
    return "\n".join(lines)
