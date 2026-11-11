"""Meaningful boundary checks; synthetic fixtures are never study approvals."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_packet", ROOT / "scripts/build_packet.py")
compiler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compiler)


def synthetic_declaration():
    """A mechanically complete fixture with no scientific meaning."""
    value = json.loads((ROOT / "templates/protocol.blank.json").read_text())
    value.update(study_id="SYNTHETIC_TEST_ONLY", title="Synthetic validation fixture",
                 status="approved_for_freeze", prior_work_disclosure="Synthetic fixture only.",
                 outcome_access_before_registration="Synthetic fixture only.")
    value["metadata"].update(description="Synthetic fixture.", contributors=[{"name": "Test fixture"}],
                             license="No license", subjects=["Synthetic"], public_or_embargoed="public")
    value["source_records"] = [{"id": "S1", "location": "test source", "what_it_supports": "Synthetic fixture only"}]
    for key in compiler.SECTION_LABELS:
        value["sections"][key] = "Synthetic fixture: " + key
    hypothesis = value["hypotheses"][0]
    hypothesis.update(status="decided", source_record_ids=["S1"])
    for key in ("statement", "contrast", "outcome", "analysis", "interpretation_rule"):
        hypothesis[key] = "Synthetic fixture: " + key
    for key in compiler.TEXT_EXECUTION:
        value["execution"][key] = "Synthetic fixture: " + key
    value["execution"].update(n_independent_repetitions=3, evaluation_episodes_per_condition=2,
                              pilot_seed_blocks=[1], confirmatory_seed_blocks=[101, 102, 103])
    value["artifacts"].update(code_repository_url="https://example.invalid/test-only",
                              code_commit_sha="a" * 40, scenario_manifest_sha256="b" * 64,
                              environment_lock_sha256="c" * 64)
    for key in compiler.QUALITY_FIELDS:
        value["quality_evidence"][key] = "Synthetic fixture: " + key
    return attest_fixture(value)


def attest_fixture(value):
    digest = compiler.review_digest(value)
    for review in value["reviews"].values():
        review.update(reviewer_name="SYNTHETIC_TEST_ONLY", approved=True,
                      reviewed_at_utc="2020-01-01T00:00:00Z", review_digest=digest,
                      notes="Synthetic software fixture, not a real review.")
    return value


class BoundaryTests(unittest.TestCase):
    def test_complete_declaration_passes_mechanical_checks(self):
        self.assertEqual(compiler.validate(synthetic_declaration()), [])

    def test_example_is_blocked_and_preserves_proposals(self):
        value = json.loads((ROOT / "examples/occlusion.proposed.json").read_text())
        blockers = compiler.validate(value)
        self.assertTrue(any("open_decisions" in x for x in blockers))
        self.assertTrue(any("prior_work_disclosure" in x for x in blockers))
        self.assertTrue(any("proposed" in x.lower() for x in blockers))

    def test_reused_pilot_seeds_are_rejected(self):
        value = synthetic_declaration()
        value["execution"]["pilot_seed_blocks"] = [101]
        attest_fixture(value)
        self.assertTrue(any("overlap" in x for x in compiler.validate(value)))

    def test_seed_count_and_duplicates_are_rejected(self):
        value = synthetic_declaration()
        value["execution"]["confirmatory_seed_blocks"] = [101, 101]
        attest_fixture(value)
        blockers = compiler.validate(value)
        self.assertTrue(any("unique" in x for x in blockers))
        self.assertTrue(any("length" in x for x in blockers))

    def test_scientific_edit_invalidates_all_reviews(self):
        value = synthetic_declaration()
        value["hypotheses"][0]["contrast"] = "Changed scientific contrast"
        self.assertEqual(sum("digest does not match" in x for x in compiler.validate(value)), 3)

    def test_workflow_status_does_not_change_review_digest(self):
        value = synthetic_declaration()
        before = compiler.review_digest(value)
        value["status"] = "draft"
        value["reviews"]["science"]["notes"] = "Changed attestation only"
        self.assertEqual(before, compiler.review_digest(value))
        self.assertTrue(any(x.startswith("status:") for x in compiler.validate(value)))

    def test_freeze_blocks_incomplete_and_preserves_existing_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "freeze"
            result = subprocess.run([sys.executable, str(ROOT / "scripts/build_packet.py"),
                                     str(ROOT / "examples/occlusion.proposed.json"),
                                     "--out", str(out), "--freeze"], capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(out.exists())
            protocol = Path(temp) / "synthetic.json"
            protocol.write_text(json.dumps(synthetic_declaration()))
            command = [sys.executable, str(ROOT / "scripts/build_packet.py"), str(protocol),
                       "--out", str(out), "--freeze"]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            snapshot = (out / "protocol.snapshot.json").read_bytes()
            self.assertEqual(snapshot, protocol.read_bytes())
            for line in (out / "SHA256SUMS.txt").read_text().splitlines():
                expected, name = line.split("  ", 1)
                self.assertEqual(expected, compiler.sha256((out / name).read_bytes()))
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 3)
            self.assertEqual(snapshot, (out / "protocol.snapshot.json").read_bytes())

    def test_unknown_source_reference_is_blocked(self):
        value = synthetic_declaration()
        value["hypotheses"][0]["source_record_ids"] = ["not-a-supplied-source"]
        attest_fixture(value)
        self.assertTrue(any("reference supplied" in x for x in compiler.validate(value)))


if __name__ == "__main__":
    unittest.main()
