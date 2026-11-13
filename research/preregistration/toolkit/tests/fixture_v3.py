"""Synthetic declarations for software tests. No actual research or approvals."""
import protocol_v3 as theory


def populate_contract(value):
    hids = [h["id"] for h in value["hypotheses"] if h["classification"] in {"primary", "secondary"}]
    c = theory.new_contract(hids)
    value["schema_version"] = 3
    value["test_contract"] = c
    c["inference"].update(study_type="mechanism_benchmark", target_level="computational_mechanism",
        phenomenon="Synthetic scalar contrast", allowed_conclusion="Synthetic mechanism compatibility only",
        excluded_conclusions=["No consciousness inference from this synthetic fixture"],
        theory_core_vs_implementation="Synthetic implementation predictions only", consciousness_inference="not_assessed")
    for a in c["accounts"]:
        a.update(name="Synthetic " + a["id"], version="Synthetic fixture v1", kind="mechanistic_account",
                 source_record_ids=["S1"], component_ids=["M1"], commitment="Synthetic commitment",
                 implementation_assumptions="Synthetic assumptions")
        a["bridge_assumptions"] = [{"assumption": "Synthetic bridge", "test_or_justification": "Synthetic bridge test",
                                     "violation_implication": "Synthetic bridge violation limits inference"}]
    value["artifact_handoff"]["items"].append({"id": "A_assurance", "kind": "analysis", "status": "captured",
        "location": "https://example.invalid/synthetic-only-assurance", "sha256": "e"*64,
        "immutable_version": None, "owner": "SYNTHETIC_TEST_ONLY", "reason": None})
    for contrast in c["contrasts"]:
        contrast.update(estimand=next(a["estimand"] for a in value["claim_measure_map"] if a["hypothesis_id"] == contrast["hypothesis_id"]),
            interval_method="Synthetic prespecified uncertainty interval", multiplicity_rule="Synthetic single primary rule",
            diagnosticity_reason="Synthetic exclusive regions", resource_matching="Synthetic matched resources")
        contrast["prediction_regions"] = [{"account_id": "T1", "specified": True, "lower": .03, "upper": None, "derivation": "Synthetic target margin"},
                                            {"account_id": "T2", "specified": True, "lower": -.01, "upper": .01, "derivation": "Synthetic negligible-effect interval"}]
        contrast["interpretations"] = {k: "Synthetic interpretation: " + k for k in theory.OUTCOMES}
        for check in contrast["validity_checks"]:
            check.update(pass_rule="Synthetic control expected outcome", passed=True,
                         evidence_artifact_id="A_assurance", failure_action="Synthetic invalidation rule")
    for a in c["design_assurance"]:
        a.update(strategy="decision_errors", independent_unit=value["execution"]["independent_unit"],
            planned_repetitions=value["execution"]["n_independent_repetitions"], minimum_effect_magnitude=.03,
            effect_scale_and_justification="Synthetic effect scale", assumptions_and_range="Synthetic generator range",
            calibration_sampling="Synthetic independent calibration draws", evidence_artifact_id="A_assurance")
        a["criteria"] = [{"scenario": s, "event": "rival_only" if s == "rival" else "target_only",
            "direction": "at_most" if s == "null" else "at_least", "threshold": .05 if s == "null" else .8,
            "scenario_definition": "Synthetic scenario: " + s, "count": 0 if s == "null" else 100, "total": 100}
            for s in theory.SCENARIOS]
        a["criteria"].extend({"scenario": s, "event": "invalid", "direction": "at_most", "threshold": .05,
            "scenario_definition": "Synthetic invalid-rate scenario: " + s, "count": 0, "total": 100} for s in theory.SCENARIOS)
    critical = c["critical_review"]
    critical.update(coordinator="SYNTHETIC_TEST_ONLY", coordinator_conflicts="Synthetic conflict disclosure",
                    roles_overlap=True, overlap_reason="Synthetic one-person software fixture",
                    disagreement_resolution="Synthetic documented resolution")
    for p in critical["perspectives"]:
        p.update(reviewer_name="SYNTHETIC_TEST_ONLY", relationship="internal_critic", conflicts="Synthetic conflict disclosure")
    work = c["execution"]
    work["masking"].update(mode="open_with_justification", method_or_limitation="Synthetic one-person limitation",
        custodian="SYNTHETIC_TEST_ONLY", analyst="SYNTHETIC_TEST_ONLY", analysis_lock_artifact_id="A_code",
        unblinding_gate="registration_archived_and_analysis_locked", access_log_location="Synthetic access log")
    work["replication"].update(mode="none_with_reason", independence_basis_or_limitation="Synthetic fixture does not claim replication",
        release_trigger="Synthetic after locked primary analysis", analysis_and_pooling_rule="Synthetic no pooling",
        failure_interpretation="Synthetic no replication claim")
    for key in ("all_registered_hypotheses", "all_attempts", "full_outcome_matrix", "deviations_with_exposure", "outcome_independent_release"):
        work["reporting"][key] = True
    for key in ("release_location", "release_deadline_rule", "amendment_rule", "interpretation_revision_rule"):
        work["reporting"][key] = "Synthetic fixture: " + key
    review = theory.critical_review_blank()
    review["perspective_records"] = [{"account_id": aid, "reviewer_name": "SYNTHETIC_TEST_ONLY",
        "design_and_interpretation_accepted": True, "source_record_ids": ["S1"],
        "source_locator": "Synthetic acceptance row", "reviewed_at_utc": "2020-01-01T00:00:00Z"} for aid in ("T1", "T2")]
    value["reviews"]["critical"] = review
    return value
