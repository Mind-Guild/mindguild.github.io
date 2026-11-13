"""Scientific-record boundary tests. All names and attestations are synthetic."""
import copy
import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_build_packet import ROOT, attest_fixture, compiler, decide_fixture, synthetic_declaration

capture = compiler.capture


def renew_fixture(value):
    return attest_fixture(decide_fixture(value))


def legacy_fixture():
    value = synthetic_declaration()
    value.pop("test_contract", None)
    value["reviews"].pop("critical", None)
    for key in capture.new_records():
        del value[key]
    value["schema_version"] = 1
    return value


class ClaimAndComponentTests(unittest.TestCase):
    def test_confirmatory_claim_needs_map_and_rival(self):
        for change, expected in ((lambda p: p.update(claim_measure_map=[]), "missing confirmatory hypothesis"),
                                 (lambda p: p["claim_measure_map"][0].update(rival_explanations=[]), "rival_explanations")):
            value = synthetic_declaration(); change(value); renew_fixture(value)
            self.assertTrue(any(expected in x for x in compiler.validate(value)))

    def test_encoded_effect_needs_interpretation_limit(self):
        value = synthetic_declaration()
        value["claim_measure_map"][0]["directly_encoded_effect"] = True
        renew_fixture(value)
        self.assertTrue(any("encoded_effect_implications" in x for x in compiler.validate(value)))
        value["claim_measure_map"][0]["encoded_effect_implications"] = "Only validates the engineered synthetic circuit."
        renew_fixture(value)
        self.assertEqual(compiler.validate(value), [])

    def test_planned_component_cannot_be_confirmatory(self):
        value = synthetic_declaration()
        value["components"][0].update(implementation_status="planned", evidence_status="not_demonstrated")
        renew_fixture(value)
        self.assertTrue(any("must be implemented" in x for x in compiler.validate(value)))

    def test_excluded_future_component_can_remain_a_proposal(self):
        value = synthetic_declaration()
        future = capture.new_component("M2")
        future.update(name="Future circuit", role="model", mechanism="Future mechanism", implementation_status="analyst_proposed",
                      evidence_status="not_demonstrated", included_in_study=False)
        value["components"].append(future)
        renew_fixture(value)
        self.assertEqual(compiler.validate(value), [])
        self.assertEqual(value["components"][1]["implementation_status"], "analyst_proposed")

    def test_demonstrated_status_does_not_imply_implemented(self):
        value = synthetic_declaration()
        value["components"][0]["implementation_status"] = "planned"
        renew_fixture(value)
        self.assertTrue(any("demonstration/verification contradicts" in x for x in compiler.validate(value)))

    def test_unknown_component_artifact_is_blocked(self):
        value = synthetic_declaration(); value["components"][0]["artifact_ids"] = ["missing"]
        renew_fixture(value)
        self.assertTrue(any("artifact_ids: reference existing IDs" in x for x in compiler.validate(value)))

    def test_selected_component_evidence_status_cannot_be_unknown(self):
        value = synthetic_declaration(); value["components"][0]["evidence_status"] = "not_recorded"
        renew_fixture(value)
        self.assertTrue(any("demonstration/verification status explicitly" in x for x in compiler.validate(value)))


class LearningTests(unittest.TestCase):
    def test_state_dynamics_can_exist_without_online_learning(self):
        value = synthetic_declaration()
        self.assertTrue(value["learning"]["within_run_state"]["enabled"])
        self.assertFalse(value["learning"]["online_updates"]["enabled"])
        self.assertEqual(compiler.validate(value), [])

    def test_disabled_learning_cannot_declare_weight_updates(self):
        value = synthetic_declaration(); value["learning"]["online_updates"]["parameters"] = ["weights"]
        renew_fixture(value)
        self.assertTrue(any("disabled phase must not declare" in x for x in compiler.validate(value)))

    def test_named_learning_rule_is_not_enough(self):
        value = synthetic_declaration()
        value["learning"]["online_updates"].update(enabled=True, parameters=["decoder_weights"], rule="PES")
        renew_fixture(value)
        errors = compiler.validate(value)
        for key in ("signal_definition", "objective", "schedule", "evaluation_update_policy"):
            self.assertTrue(any(key in x for x in errors))

    def test_complete_online_learning_record_passes(self):
        value = synthetic_declaration()
        value["learning"]["online_updates"].update(enabled=True, parameters=["decoder_weights"], rule="Synthetic update rule",
            signal_type="supervised_error", signal_definition="Synthetic teacher minus prediction", objective="Synthetic prediction error",
            schedule="Synthetic update at each training step", evaluation_update_policy="Freeze updates during synthetic evaluation")
        renew_fixture(value)
        self.assertEqual(compiler.validate(value), [])

    def test_offline_calibration_needs_data_and_freeze_boundary(self):
        value = synthetic_declaration(); value["learning"]["offline_calibration"]["enabled"] = True
        renew_fixture(value)
        errors = compiler.validate(value)
        self.assertTrue(any("data_and_selection" in x for x in errors))
        self.assertTrue(any("freeze_point" in x for x in errors))


class ProvenanceTests(unittest.TestCase):
    def test_missing_or_proposed_primary_decision_blocks_freeze(self):
        for state in (None, "proposed"):
            value = synthetic_declaration(); path = "/hypotheses/0/statement"
            record = next(r for r in value["provenance"] if r["field_path"] == path)
            if state is None:
                value["provenance"].remove(record)
            else:
                record["decision_status"] = state
            attest_fixture(value)
            self.assertTrue(any(path + " needs an explicit decided record" in x for x in compiler.validate(value)))

    def test_field_edit_invalidates_its_decision_even_if_reviews_are_renewed(self):
        value = synthetic_declaration(); value["hypotheses"][0]["outcome"] = "Changed outcome"
        attest_fixture(value)
        self.assertTrue(any("stale decision" in x for x in compiler.validate(value)))

    def test_malformed_and_nonresolving_pointers_are_diagnostics(self):
        for path in ("hypotheses/0/outcome", "/hypotheses/01/outcome", "/hypotheses/50/outcome", "/~2bad", "/reviews/science"):
            value = synthetic_declaration(); record = capture.provenance_record(path); value["provenance"].append(record)
            attest_fixture(value)
            self.assertTrue(any(".field_path:" in x for x in compiler.validate(value)), path)

    def test_json_pointer_escaping_is_resolved(self):
        self.assertEqual(capture.pointer_value({"a/b": {"~c": 3}}, "/a~1b/~0c"), 3)

    def test_duplicate_current_records_are_rejected(self):
        value = synthetic_declaration(); value["provenance"].append(copy.deepcopy(value["provenance"][0]))
        attest_fixture(value)
        self.assertTrue(any("duplicate current provenance" in x for x in compiler.validate(value)))

    def test_analyst_proposal_needs_explicit_human_adoption(self):
        value = synthetic_declaration(); record = value["provenance"][0]; record["origin"] = "analyst_proposal"
        attest_fixture(value)
        self.assertTrue(any("analyst_adoption" in x for x in compiler.validate(value)))
        record["analyst_adoption"].update(adopted_by="SYNTHETIC_TEST_ONLY", source_record_id="S1", adopted_at_utc="2020-01-01T00:00:00Z")
        attest_fixture(value)
        self.assertEqual(compiler.validate(value), [])

    def test_unresolved_original_speaker_is_preserved(self):
        value = synthetic_declaration(); record = value["provenance"][0]
        record.update(origin="meeting", speaker_label="Unresolved participant", speaker_attribution="unresolved",
                      decision_record="Synthetic later written acceptance by the named decision owner")
        attest_fixture(value)
        self.assertEqual(compiler.validate(value), [])
        self.assertEqual(record["speaker_attribution"], "unresolved")


class HandoffAndExposureTests(unittest.TestCase):
    def test_uncaptured_core_artifact_blocks_freeze(self):
        value = synthetic_declaration(); item = value["artifact_handoff"]["items"][1]
        item.update(status="requested", reason="Awaiting exact config", owner="Synthetic owner")
        renew_fixture(value)
        errors = compiler.validate(value)
        self.assertTrue(any("requested capture is still open" in x for x in errors))
        self.assertTrue(any("capture the core config" in x for x in errors))

    def test_unavailable_supplement_needs_reason(self):
        value = synthetic_declaration(); item = next(a for a in value["artifact_handoff"]["items"] if a["kind"] == "chat")
        item.update(status="not_available", reason=None); renew_fixture(value)
        self.assertTrue(any(".reason:" in x for x in compiler.validate(value)))
        item["reason"] = "Synthetic chat was unavailable; decisions are recorded in the follow-up source."
        renew_fixture(value)
        self.assertEqual(compiler.validate(value), [])

    def test_floating_artifact_version_is_not_a_pin(self):
        value = synthetic_declaration(); item = value["artifact_handoff"]["items"][1]
        item.update(sha256=None, immutable_version="main"); renew_fixture(value)
        self.assertTrue(any("pin a SHA-256" in x for x in compiler.validate(value)))

    def test_artifact_pin_must_match_execution_metadata(self):
        value = synthetic_declaration(); item = next(a for a in value["artifact_handoff"]["items"] if a["kind"] == "environment")
        item["sha256"] = "e" * 64; renew_fixture(value)
        self.assertTrue(any("SHA-256 must match artifacts.environment_lock_sha256" in x for x in compiler.validate(value)))

    def test_access_declaration_cannot_stay_incomplete(self):
        value = synthetic_declaration(); value["results_access"]["declaration_status"] = "incomplete"
        renew_fixture(value)
        self.assertTrue(any("complete disclosure" in x for x in compiler.validate(value)))

    def test_already_seen_confirmatory_outputs_are_blocked(self):
        value = synthetic_declaration(); value["results_access"]["confirmatory_status"] = "already_inspected"
        renew_fixture(value)
        self.assertTrue(any("genuinely unobserved target" in x for x in compiler.validate(value)))

    def test_previous_demo_with_new_reserved_runs_is_valid(self):
        value = synthetic_declaration()
        value["results_access"]["no_prior_results_reason"] = None
        value["results_access"]["prior_results"] = [{"description": "Synthetic earlier demonstration", "conditions_or_runs": "Synthetic pilot block 1",
            "who_saw": ["Synthetic team"], "seen_when": "Before the synthetic protocol", "use": "Pilot inspection",
            "influence_on_design": "Informed the synthetic input range", "source_record_ids": ["S1"]}]
        renew_fixture(value)
        self.assertEqual(compiler.validate(value), [])

    def test_prior_results_cannot_also_be_declared_absent(self):
        value = synthetic_declaration()
        value["results_access"]["prior_results"] = [{"description": "An earlier synthetic demonstration"}]
        renew_fixture(value)
        self.assertTrue(any("clear the no-results explanation" in x for x in compiler.validate(value)))

    def test_existing_uninspected_outputs_need_analysis_only_scope(self):
        value = synthetic_declaration(); value["results_access"]["confirmatory_status"] = "generated_uninspected"
        renew_fixture(value)
        self.assertTrue(any("registration scope requires" in x for x in compiler.validate(value)))
        value["results_access"]["registration_scope"] = "analysis_of_uninspected_outputs"
        renew_fixture(value)
        self.assertEqual(compiler.validate(value), [])


class MigrationAndOutputTests(unittest.TestCase):
    def test_scaffold_adds_unapproved_records_and_preserves_input(self):
        value = synthetic_declaration(); value["provenance"] = []; before = copy.deepcopy(value)
        result = capture.scaffold_provenance(value)
        self.assertEqual(value,before)
        self.assertEqual(len(result["provenance"]),len(capture.required_provenance_paths(value)))
        self.assertTrue(all(r["decision_status"] == "not_recorded" and r["decision_by"] is None for r in result["provenance"]))
        self.assertTrue(any("needs an explicit decided record" in x for x in compiler.validate(result)))

    def test_scaffold_does_not_refresh_stale_decisions(self):
        value = synthetic_declaration(); value["hypotheses"][0]["statement"] = "Changed statement"
        result = capture.scaffold_provenance(value)
        self.assertEqual(result["provenance"],value["provenance"])
        self.assertTrue(any("stale decision" in x for x in compiler.validate(result)))

    def test_scaffold_is_idempotent_and_rejects_legacy(self):
        value = capture.scaffold_provenance(synthetic_declaration())
        self.assertEqual(capture.scaffold_provenance(value),value)
        with self.assertRaises(ValueError): capture.scaffold_provenance(legacy_fixture())

    def test_scaffold_cli_never_overwrites(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)/"draft.json"; source.write_text((ROOT/"templates/protocol.blank.json").read_text())
            out = Path(temp)/"capture.json"; command = [sys.executable,str(ROOT/"scripts/scaffold_provenance.py"),str(source),"--out",str(out)]
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
            before = out.read_bytes()
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,3)
            self.assertEqual(before,out.read_bytes())

    def test_v1_cannot_freeze_under_v2_compiler(self):
        errors = compiler.validate(legacy_fixture())
        self.assertTrue(any("legacy v1 is draft-only" in x for x in errors))

    def test_migration_preserves_old_content_and_resets_only_active_reviews(self):
        original = legacy_fixture(); before = copy.deepcopy(original)
        migrated = capture.migrate_v1(original)
        self.assertEqual(original, before)
        self.assertEqual(migrated["hypotheses"], original["hypotheses"])
        self.assertEqual(migrated["sections"], original["sections"])
        self.assertEqual(migrated["source_records"], original["source_records"])
        self.assertEqual(migrated["migration"]["previous_reviews"], original["reviews"])
        self.assertFalse(any(r["approved"] for r in migrated["reviews"].values()))
        self.assertEqual(migrated["provenance"], [])
        self.assertIsNone(migrated["learning"]["online_updates"]["enabled"])
        self.assertTrue(compiler.validate(migrated))

    def test_migration_rejects_v2_and_does_not_overwrite(self):
        with self.assertRaises(ValueError): capture.migrate_v1(synthetic_declaration())
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)/"v1.json"; source.write_text(json.dumps(legacy_fixture()))
            out = Path(temp)/"v2.json"; command = [sys.executable,str(ROOT/"scripts/migrate_protocol.py"),str(source),"--out",str(out)]
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
            unchanged = out.read_bytes()
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,3)
            self.assertEqual(unchanged,out.read_bytes())

    def test_draft_build_exports_ledgers_without_altering_or_adopting_input(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp)/"draft.json"; source.write_text((ROOT/"templates/protocol.blank.json").read_text())
            before = source.read_bytes(); out = Path(temp)/"packet"
            result = subprocess.run([sys.executable,str(ROOT/"scripts/build_packet.py"),str(source),"--out",str(out)],capture_output=True)
            self.assertEqual(result.returncode,2)
            self.assertEqual(before,source.read_bytes())
            rows = list(csv.DictReader(io.StringIO((out/"decision_ledger.csv").read_text())))
            self.assertTrue(rows)
            self.assertTrue(all(r["decision_status"] == "not_recorded" for r in rows))
            self.assertTrue((out/"artifact_handoff.csv").exists())
            self.assertIn("Component status",(out/"osf_packet.md").read_text())

    def test_boolean_is_not_a_schema_version(self):
        value = synthetic_declaration(); value["schema_version"] = True
        self.assertTrue(any(x.startswith("schema_version:") for x in compiler.validate(value)))

    def test_empty_structured_records_are_reported_without_crashing(self):
        value = synthetic_declaration()
        for key in capture.new_records(): value[key] = None
        self.assertGreater(len(compiler.validate(value)), 5)


if __name__ == "__main__":
    unittest.main()
