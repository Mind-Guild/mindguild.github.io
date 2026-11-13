"""Meaningful test-severity guards. All research records here are synthetic."""
import copy
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_build_packet import ROOT, compiler, synthetic_declaration, decide_fixture, attest_fixture
from test_v2_capture import legacy_fixture

theory = compiler.theory
SPEC = importlib.util.spec_from_file_location("calibration", ROOT/"scripts/calibrate_decisions.py")
calibration = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(calibration)


def renew(p): return attest_fixture(decide_fixture(p))


def v2_fixture():
    p = synthetic_declaration(); p.pop("test_contract"); p["reviews"].pop("critical"); p["schema_version"] = 2
    p["provenance"] = [r for r in p["provenance"] if not r["field_path"].startswith("/test_contract/")]
    return p


def theory_fixture():
    p = synthetic_declaration(); c = p["test_contract"]
    c["inference"].update(study_type="theory_discrimination", target_level="theory_prediction",
                           consciousness_inference="conditional_on_bridge_assumptions")
    c["accounts"][0]["kind"] = "theory"
    p["execution"].update(n_independent_repetitions=6, confirmatory_seed_blocks=[101,102,103,104,105,106])
    c["design_assurance"][0]["planned_repetitions"] = 6
    c["execution"]["replication"].update(mode="reserved_runs", reserved_seed_blocks=[105,106])
    return renew(p)


def calibration_input():
    return {"data_role": "synthetic_calibration", "generator_description": "Synthetic software fixture",
        "assumptions_and_range": "Synthetic fixed generator", "sampling_and_seed_derivation": "Synthetic independent draws",
        "records": [{"hypothesis_id": "H1", "scenario": scenario, "run_id": str(i), "interval": interval,
                     "true_estimand": truth, "valid": True}
                    for scenario, interval, truth in (("null",[-.005,.005],0), ("target",[.04,.06],.05), ("rival",[-.005,.005],0)) for i in range(3)]}


class DecisionMappingTests(unittest.TestCase):
    def test_uncertainty_interval_produces_all_six_categories(self):
        c = synthetic_declaration()["test_contract"]["contrasts"][0]
        for interval, outcome in (([.04,.06],"target_only"), ([-.005,.005],"rival_only"), ([.015,.02],"neither"), ([-.05,.1],"inconclusive")):
            self.assertEqual(theory.adjudicate(c, interval), outcome)
        c["prediction_regions"][0].update(lower=0,upper=.1)
        c["prediction_regions"][1].update(lower=-.1,upper=.1)
        self.assertEqual(theory.adjudicate(c,[.01,.02]),"both")
        self.assertEqual(theory.adjudicate(c,[.01,.02],False),"invalid")

    def test_boundaries_are_closed_and_no_prediction_is_not_null(self):
        c = synthetic_declaration()["test_contract"]["contrasts"][0]
        self.assertEqual(theory.adjudicate(c,[.03,.03]),"target_only")
        c["prediction_regions"][1].update(specified=False,lower=None,upper=None)
        self.assertEqual(theory.adjudicate(c,[.04,.05]),"inconclusive")
        self.assertFalse(theory.discriminating(c))

    def test_bad_intervals_and_boolean_bounds_are_rejected(self):
        c = synthetic_declaration()["test_contract"]["contrasts"][0]
        for interval in ([1,0],[False,1],[0,math.inf],[0],None):
            with self.assertRaises(ValueError): theory.adjudicate(c,interval)
        with self.assertRaises(ValueError): theory.bounds({"specified":True,"lower":True,"upper":1})
        with self.assertRaises(ValueError): theory.bounds({"specified":True,"lower":None,"upper":None})

    def test_wilson_interval_represents_monte_carlo_uncertainty(self):
        lo,hi=theory.wilson95(0,10)
        self.assertAlmostEqual(lo,0); self.assertGreater(hi,.05)
        self.assertLess(theory.wilson95(0,100)[1],.05)
        self.assertGreater(theory.wilson95(100,100)[0],.8)
        for count,total in ((True,100),(1,1),(101,100),(-1,100)):
            with self.assertRaises(ValueError): theory.wilson95(count,total)


class ContractTests(unittest.TestCase):
    def test_complete_benchmark_and_theory_declarations_pass(self):
        self.assertEqual(compiler.validate(synthetic_declaration()),[])
        self.assertEqual(compiler.validate(theory_fixture()),[])

    def test_benchmark_cannot_claim_consciousness_evidence(self):
        p=synthetic_declaration(); p["test_contract"]["inference"]["consciousness_inference"]="conditional_on_bridge_assumptions"
        self.assertTrue(any("benchmark cannot claim" in x for x in compiler.validate(renew(p))))

    def test_theory_claim_requires_version_and_bridge_assumptions(self):
        p=theory_fixture(); p["test_contract"]["accounts"][0].update(version=None,bridge_assumptions=[])
        errors=compiler.validate(renew(p))
        self.assertTrue(any("version:" in x for x in errors)); self.assertTrue(any("bridge_assumptions" in x for x in errors))

    def test_identical_or_nested_predictions_cannot_be_primary_theory_test(self):
        for region in ({"lower":.03,"upper":None},{"lower":0,"upper":None}):
            p=theory_fixture(); p["test_contract"]["contrasts"][0]["prediction_regions"][1].update(region)
            self.assertTrue(any("exclusive possible result" in x for x in compiler.validate(renew(p))))

    def test_missing_hypothesis_contrasts_and_assurance_are_blocked(self):
        p=synthetic_declaration(); p["test_contract"].update(contrasts=[],design_assurance=[])
        errors=compiler.validate(renew(p))
        self.assertEqual(sum("missing confirmatory hypothesis H1" in x for x in errors),2)

    def test_estimand_cannot_drift_from_claim_map(self):
        p=synthetic_declaration(); p["test_contract"]["contrasts"][0]["estimand"]="A different estimand"
        self.assertTrue(any("linked claim_measure_map estimand" in x for x in compiler.validate(renew(p))))

    def test_unfavorable_inconclusive_and_invalid_interpretations_required(self):
        for key in ("rival_only","both","neither","inconclusive","invalid"):
            p=synthetic_declaration(); p["test_contract"]["contrasts"][0]["interpretations"][key]=None
            self.assertTrue(any("interpretations."+key in x for x in compiler.validate(renew(p))))

    def test_quality_control_failure_blocks_freeze(self):
        p=synthetic_declaration(); p["test_contract"]["contrasts"][0]["validity_checks"][0]["passed"]=False
        self.assertTrue(any("must pass before freeze" in x for x in compiler.validate(renew(p))))

    def test_point_rate_without_sufficient_calibration_precision_is_blocked(self):
        p=synthetic_declaration(); p["test_contract"]["design_assurance"][0]["criteria"][0]["total"]=10
        self.assertTrue(any("Wilson bound does not meet" in x for x in compiler.validate(renew(p))))

    def test_assurance_counts_unit_and_run_count_must_be_consistent(self):
        for change, text in (({"planned_repetitions":99},"planned independent repetition"),({"independent_unit":"frames"},"execution.independent_unit"),({"evidence_artifact_id":"A_code"},"analysis report")):
            p=synthetic_declaration(); p["test_contract"]["design_assurance"][0].update(change)
            self.assertTrue(any(text in x for x in compiler.validate(renew(p))))

    def test_precision_route_requires_width_coverage_and_all_scenarios(self):
        p=synthetic_declaration(); a=p["test_contract"]["design_assurance"][0]
        a.update(strategy="precision",maximum_interval_width=.1,criteria=[{"scenario":s,"event":e,"direction":"at_least","threshold":.8,
            "count":100,"total":100,"scenario_definition":"Synthetic precision scenario"} for s in theory.SCENARIOS for e in ("precision_achieved","coverage")])
        a["criteria"].extend({"scenario":s,"event":"invalid","direction":"at_most","threshold":.05,
            "count":0,"total":100,"scenario_definition":"Synthetic invalid-rate scenario"} for s in theory.SCENARIOS)
        self.assertEqual(compiler.validate(renew(p)),[])
        a["criteria"].pop(); self.assertTrue(any("missing scenario/event/direction" in x for x in compiler.validate(renew(p))))

    def test_new_contract_values_invalidate_their_field_decision(self):
        p=synthetic_declaration(); p["test_contract"]["inference"]["allowed_conclusion"]="A different limit"
        attest_fixture(p)
        self.assertTrue(any("stale decision" in x for x in compiler.validate(p)))

    def test_renewed_approvals_cannot_reuse_calibration_after_generator_change(self):
        p=synthetic_declaration(); previous=p["test_contract"]["design_assurance"][0]["calibration_basis_sha256"]
        p["sections"]["data_generating_parameters"]="A changed synthetic generator"
        renew(p)
        p["test_contract"]["design_assurance"][0]["calibration_basis_sha256"]=previous
        attest_fixture(p)
        self.assertTrue(any("calibration is missing or stale" in x for x in compiler.validate(p)))

    def test_replication_partition_changes_invalidate_calibration_basis(self):
        p=theory_fixture(); basis=theory.assurance_basis_digest(p,"H1")
        p["test_contract"]["execution"]["replication"]["reserved_seed_blocks"]=[103,104]
        self.assertNotEqual(theory.assurance_basis_digest(p,"H1"),basis)

    def test_malformed_contract_diagnoses_without_crashing(self):
        p=synthetic_declaration()
        for key in theory.CONTRACT_GROUPS: p["test_contract"][key]=None
        self.assertGreater(len(compiler.validate(p)),10)


class GovernanceAndExecutionTests(unittest.TestCase):
    def test_internal_critic_is_not_recorded_as_proponent_endorsement(self):
        p=synthetic_declaration(); p["test_contract"]["critical_review"]["perspectives"][0]["relationship"]="proponent"
        self.assertTrue(any("actual proponent involvement" in x for x in compiler.validate(renew(p))))

    def test_critical_review_needs_each_perspective_acceptance(self):
        p=synthetic_declaration(); p["reviews"]["critical"]["perspective_records"].pop()
        self.assertTrue(any("missing design/interpretation acceptance" in x for x in compiler.validate(p)))

    def test_undisclosed_overlapping_roles_block(self):
        p=synthetic_declaration(); p["test_contract"]["critical_review"]["roles_overlap"]=False
        self.assertTrue(any("overlapping people/roles" in x for x in compiler.validate(renew(p))))

    def test_unresolved_dispute_and_reviewer_mismatch_block(self):
        p=synthetic_declaration(); p["test_contract"]["critical_review"]["unresolved_disputes"]=["Synthetic disagreement"]
        p["reviews"]["critical"]["perspective_records"][0]["reviewer_name"]="A different synthetic person"
        errors=compiler.validate(renew(p))
        self.assertTrue(any("unresolved_disputes" in x for x in errors)); self.assertTrue(any("assigned perspective" in x for x in errors))

    def test_masking_claim_cannot_reuse_same_custodian_and_analyst(self):
        p=synthetic_declaration(); p["test_contract"]["execution"]["masking"]["mode"]="masked"
        self.assertTrue(any("separate custodian" in x for x in compiler.validate(renew(p))))

    def test_unblinding_gate_and_analysis_pin_required(self):
        p=synthetic_declaration(); p["test_contract"]["execution"]["masking"].update(unblinding_gate="anytime",analysis_lock_artifact_id="missing")
        errors=compiler.validate(renew(p))
        self.assertTrue(any("unblinding_gate" in x for x in errors)); self.assertTrue(any("analysis_lock_artifact_id" in x for x in errors))

    def test_theory_test_cannot_omit_replication_or_reserve_all_runs(self):
        p=theory_fixture(); rep=p["test_contract"]["execution"]["replication"]
        rep.update(mode="none_with_reason",reserved_seed_blocks=[])
        self.assertTrue(any("replication plan" in x for x in compiler.validate(renew(p))))
        rep.update(mode="reserved_runs",reserved_seed_blocks=p["execution"]["confirmatory_seed_blocks"])
        self.assertTrue(any("leave at least two" in x for x in compiler.validate(renew(p))))

    def test_report_cannot_drop_invalid_or_unfavorable_runs(self):
        p=synthetic_declaration(); p["test_contract"]["execution"]["reporting"]["all_attempts"]=False
        self.assertTrue(any("regardless of favorable" in x for x in compiler.validate(renew(p))))


class CalibrationAndMigrationTests(unittest.TestCase):
    def test_calibration_reports_all_outcomes_and_input_coverage(self):
        result=calibration.summarize(synthetic_declaration(),calibration_input())
        self.assertEqual(len(result["criteria_results"]),6)
        self.assertEqual(result["criteria_results"][0]["count"],0)
        self.assertEqual(sum(r["all_outcome_counts"]["total"] for r in result["criteria_results"] if r["event"]!="invalid"),9)

    def test_invalid_runs_stay_in_denominator(self):
        inputs=calibration_input(); inputs["records"][3]["valid"]=False
        result=calibration.summarize(synthetic_declaration(),inputs)
        row=next(r for r in result["criteria_results"] if r["scenario"]=="target")
        self.assertEqual((row["count"],row["total"]),(2,3)); self.assertEqual(row["all_outcome_counts"]["invalid"],1)

    def test_invalid_null_calibration_cannot_pass_by_suppressing_false_positives(self):
        p=synthetic_declaration(); rows=p["test_contract"]["design_assurance"][0]["criteria"]
        next(r for r in rows if r["scenario"]=="null" and r["event"]=="invalid")["count"]=100
        self.assertTrue(any("Wilson bound does not meet" in x for x in compiler.validate(renew(p))))

    def test_scenario_event_denominators_must_match(self):
        p=synthetic_declaration(); rows=p["test_contract"]["design_assurance"][0]["criteria"]
        next(r for r in rows if r["scenario"]=="null" and r["event"]=="invalid")["total"]=200
        self.assertTrue(any("same complete-run denominator" in x for x in compiler.validate(renew(p))))

    def test_calibration_rejects_duplicates_missing_scenarios_and_unlabeled_data(self):
        for mutate in (lambda d:d["records"].append(copy.deepcopy(d["records"][0])),
                       lambda d:d.update(records=d["records"][:3]), lambda d:d.update(data_role="confirmatory")):
            data=calibration_input(); mutate(data)
            with self.assertRaises(ValueError): calibration.summarize(synthetic_declaration(),data)

    def test_v2_migration_preserves_data_and_history_and_clears_approvals(self):
        old=v2_fixture(); before=copy.deepcopy(old); new=theory.migrate_to_v3(old)
        self.assertEqual(old,before)
        for key in ("hypotheses","sections","source_records","learning","provenance","results_access"):
            self.assertEqual(old[key],new[key])
        self.assertEqual(new["migration"]["previous_reviews"],old["reviews"])
        self.assertTrue(all(not r["approved"] for r in new["reviews"].values()))
        self.assertIsNone(new["test_contract"]["inference"]["study_type"])
        scaffold=compiler.capture.scaffold_provenance(new)
        added=[r for r in scaffold["provenance"] if r["field_path"].startswith("/test_contract/")]
        self.assertEqual(len(added),6); self.assertTrue(all(r["decision_status"]=="not_recorded" for r in added))

    def test_v1_can_migrate_directly_to_v3(self):
        old=legacy_fixture(); new=theory.migrate_to_v3(old)
        self.assertEqual(new["schema_version"],3); self.assertEqual(new["hypotheses"],old["hypotheses"])
        self.assertIsNone(new["learning"]["online_updates"]["enabled"])
        self.assertTrue(compiler.validate(new))

    def test_v2_freeze_is_blocked_and_v3_outputs_include_contract_exports(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"protocol.json"; p.write_text(json.dumps(v2_fixture())); out=Path(temp)/"freeze"
            command=[sys.executable,str(ROOT/"scripts/build_packet.py"),str(p),"--out",str(out),"--freeze"]
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,2); self.assertFalse(out.exists())
            p.write_text(json.dumps(synthetic_declaration()))
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
            for name in ("prediction_matrix.csv","design_assurance.csv"): self.assertTrue((out/name).exists())
            self.assertIn("Test and interpretation contract",(out/"osf_packet.md").read_text())

    def test_calibration_cli_never_overwrites_and_hashes_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"protocol.json"; p.write_text(json.dumps(synthetic_declaration()))
            data=Path(temp)/"calibration.json"; data.write_text(json.dumps(calibration_input())); out=Path(temp)/"report.json"
            command=[sys.executable,str(ROOT/"scripts/calibrate_decisions.py"),str(p),str(data),"--out",str(out)]
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
            before=out.read_bytes(); report=json.loads(before)
            self.assertEqual(len(report["calibration_input_sha256"]),64)
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,3); self.assertEqual(out.read_bytes(),before)


if __name__ == "__main__": unittest.main()
