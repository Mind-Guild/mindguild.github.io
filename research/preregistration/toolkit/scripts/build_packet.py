#!/usr/bin/env python3
"""Compile a declared simulation protocol into a local OSF review packet.

Standard library only. No network, simulation execution, or OSF submission.
Mechanical readiness is not scientific validation or authenticated approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))
import protocol_v2 as capture


SECTION_LABELS = {
    "aims": "Aims — research questions and hypotheses",
    "data_generating_parameters": "Data-generating mechanism — parameters",
    "varied_factors": "Data-generating mechanism — varied factors",
    "factor_values_and_constants": "Data-generating mechanism — values and constants",
    "factor_combinations_and_condition_count": "Data-generating mechanism — combinations and condition count",
    "estimands_and_targets": "Estimands and targets",
    "methods_and_extracted_quantities": "Included methods and extracted quantities",
    "performance_measures": "Performance measures",
    "monte_carlo_uncertainty": "Handling Monte Carlo uncertainty",
    "repetition_count_rationale": "Number of simulation repetitions — rationale",
    "missingness_and_nonconvergence": "Missing values and nonconvergence",
    "interpretation_and_analysis": "Interpretation and analysis of performance measures",
    "software_and_packages": "Statistical software and packages",
    "computational_environment": "Planned computational environment",
    "reproducibility_measures": "Reproducibility measures",
    "additional_notes": "Additional notes for preregistration",
}
TEXT_EXECUTION = (
    "independent_unit", "rng_stream_derivation", "training_budget",
    "hyperparameter_selection", "checkpoint_selection", "stopping_rule",
    "failure_rule", "test_access_rule", "run_command", "analysis_command",
)
QUALITY_FIELDS = (
    "generator_properties", "split_leakage_check", "metric_synthetic_cases", "full_dry_run",
)
PLACEHOLDER = capture.PLACEHOLDER


def canonical(value):
    return capture.canonical(value)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def review_digest(protocol):
    # Workflow status and attestations are excluded; scientific content is included.
    return sha256(canonical({k: v for k, v in protocol.items() if k not in {"reviews", "status"}}))


def get(protocol, path, default=None):
    value = protocol
    for key in path.split("."):
        if not isinstance(value, dict):
            return default
        value = value.get(key)
    return default if value is None else value


def valid_datetime(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed <= datetime.now(timezone.utc)
    except (AttributeError, TypeError, ValueError):
        return False


def validate(protocol):
    blockers = []

    def require_text(path):
        value = get(protocol, path)
        if not isinstance(value, str) or not value.strip():
            blockers.append(f"{path}: supply a nonempty, specific value")
        elif PLACEHOLDER.search(value):
            blockers.append(f"{path}: resolve proposed or placeholder content")

    def require_list(path):
        value = get(protocol, path)
        if not isinstance(value, list) or not value:
            blockers.append(f"{path}: supply a nonempty list")
            return []
        return value

    version = protocol.get("schema_version")
    if type(version) is not int or version not in {1, 2}:
        blockers.append("schema_version: supported values are legacy 1 (draft only) and 2")
    elif version == 1:
        blockers.append("schema_version: legacy v1 is draft-only; run scripts/migrate_protocol.py before freeze")
    if protocol.get("status") != "approved_for_freeze":
        blockers.append("status: use approved_for_freeze only after resolving and reviewing the plan")
    for field in ("study_id", "title", "metadata.description", "metadata.license",
                  "prior_work_disclosure", "outcome_access_before_registration"):
        require_text(field)
    contributors = require_list("metadata.contributors")
    for i, person in enumerate(contributors):
        if not isinstance(person, dict) or not isinstance(person.get("name"), str) or not person["name"].strip():
            blockers.append(f"metadata.contributors[{i}]: supply a contributor name")
    subjects = require_list("metadata.subjects")
    if any(not isinstance(x, str) or not x.strip() for x in subjects):
        blockers.append("metadata.subjects: use nonempty taxonomy labels")
    access = get(protocol, "metadata.public_or_embargoed")
    if not isinstance(access, str) or access not in {"public", "embargoed"}:
        blockers.append("metadata.public_or_embargoed: choose public or embargoed")
    elif access == "embargoed":
        value = get(protocol, "metadata.embargo_end_date")
        try:
            date = datetime.strptime(value, "%Y-%m-%d").date()
            if date <= datetime.now(timezone.utc).date():
                raise ValueError
        except (TypeError, ValueError):
            blockers.append("metadata.embargo_end_date: supply a future YYYY-MM-DD date; verify OSF's allowed range")

    sources = require_list("source_records")
    source_ids = []
    for i, source in enumerate(sources):
        if not isinstance(source, dict) or any(not isinstance(source.get(k), str) or not source[k].strip()
                                               for k in ("id", "location", "what_it_supports")):
            blockers.append(f"source_records[{i}]: supply id, location, and what_it_supports")
        else:
            source_ids.append(source["id"])
    if len(source_ids) != len(set(source_ids)):
        blockers.append("source_records: IDs must be unique")
    for key in SECTION_LABELS:
        require_text(f"sections.{key}")

    hypotheses = require_list("hypotheses")
    primary_count = 0
    hypothesis_ids = []
    for i, hypothesis in enumerate(hypotheses):
        if not isinstance(hypothesis, dict):
            blockers.append(f"hypotheses[{i}]: must be an object")
            continue
        hid = hypothesis.get("id")
        if not isinstance(hid, str) or not hid.strip():
            blockers.append(f"hypotheses[{i}]: supply a stable ID")
        else:
            hypothesis_ids.append(hid)
        if not isinstance(hypothesis.get("classification"), str) or hypothesis.get("classification") not in {"primary", "secondary", "exploratory"}:
            blockers.append(f"hypotheses[{i}]: choose primary, secondary, or exploratory")
        primary_count += hypothesis.get("classification") == "primary"
        if hypothesis.get("status") != "decided":
            blockers.append(f"hypotheses[{i}]: statement has not been marked decided")
        for key in ("statement", "contrast", "outcome", "analysis", "interpretation_rule"):
            value = hypothesis.get(key)
            if not isinstance(value, str) or not value.strip() or PLACEHOLDER.search(value):
                blockers.append(f"hypotheses[{i}].{key}: supply resolved, specific text")
        refs = hypothesis.get("source_record_ids")
        if not isinstance(refs, list) or not refs or any(not isinstance(x, str) or x not in source_ids for x in refs):
            blockers.append(f"hypotheses[{i}].source_record_ids: reference supplied source IDs")
    if primary_count != 1:
        blockers.append("hypotheses: this MVP requires exactly one primary hypothesis; explicitly adapt validation for a multi-primary design")
    if len(hypothesis_ids) != len(set(hypothesis_ids)):
        blockers.append("hypotheses: IDs must be unique")

    for field in TEXT_EXECUTION:
        require_text(f"execution.{field}")
    count = get(protocol, "execution.n_independent_repetitions")
    if type(count) is not int or count < 2:
        blockers.append("execution.n_independent_repetitions: supply an integer of at least 2, justified by the analysis")
    episodes = get(protocol, "execution.evaluation_episodes_per_condition")
    if type(episodes) is not int or episodes < 1:
        blockers.append("execution.evaluation_episodes_per_condition: supply a positive integer")
    seeds = {}
    for name in ("pilot_seed_blocks", "confirmatory_seed_blocks"):
        value = get(protocol, f"execution.{name}")
        if not isinstance(value, list) or any(type(x) is not int or x < 0 for x in value):
            blockers.append(f"execution.{name}: supply a list of nonnegative integer block seeds")
            seeds[name] = []
        else:
            seeds[name] = value
            if len(value) != len(set(value)):
                blockers.append(f"execution.{name}: seed blocks must be unique")
    confirmatory = seeds["confirmatory_seed_blocks"]
    if not confirmatory or len(confirmatory) != count:
        blockers.append("execution.confirmatory_seed_blocks: length must equal the independent repetition count")
    if set(seeds["pilot_seed_blocks"]) & set(confirmatory):
        blockers.append("execution: pilot and confirmatory seed blocks overlap")

    require_text("artifacts.code_repository_url")
    commit = get(protocol, "artifacts.code_commit_sha", "")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", commit):
        blockers.append("artifacts.code_commit_sha: supply a full 40- or 64-hex commit ID")
    for field in ("scenario_manifest_sha256", "environment_lock_sha256"):
        value = get(protocol, f"artifacts.{field}", "")
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
            blockers.append(f"artifacts.{field}: supply a 64-hex SHA-256 digest")
    for field in QUALITY_FIELDS:
        require_text(f"quality_evidence.{field}")
    if protocol.get("open_decisions") != []:
        blockers.append("open_decisions: resolve the list before freeze")

    if type(version) is int and version == 2:
        blockers.extend(capture.validate_v2(protocol))
    digest = review_digest(protocol)
    for role in ("science", "implementation", "analysis"):
        review = get(protocol, f"reviews.{role}", {})
        if not isinstance(review, dict):
            blockers.append(f"reviews.{role}: must be an object")
            continue
        if review.get("approved") is not True:
            blockers.append(f"reviews.{role}: approval is not recorded")
        if not isinstance(review.get("reviewer_name"), str) or not review["reviewer_name"].strip():
            blockers.append(f"reviews.{role}: supply the actual reviewer name")
        if not valid_datetime(review.get("reviewed_at_utc")):
            blockers.append(f"reviews.{role}: supply a timezone-aware review time not in the future")
        if review.get("review_digest") != digest:
            blockers.append(f"reviews.{role}: review digest does not match the current protocol")
    return blockers


def render(value):
    if value is None or value == "" or value == []:
        return "**MISSING — decision required**"
    if isinstance(value, (dict, list)):
        return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```"
    return str(value)


def packet(protocol, report):
    lines = [f"# {protocol.get('title') or 'Untitled simulation study'}", "",
             "**Local review packet. This document is not an OSF registration.**", "",
             f"Study ID: {protocol.get('study_id') or 'MISSING'}  ",
             f"Mechanical readiness: {report['status']}  ",
             f"Review digest: `{report['review_digest']}`", "",
             "## Metadata", "", render(protocol.get("metadata")), "",
             "## Prior work and outcome access", "",
             render(protocol.get("prior_work_disclosure")), "",
             render(protocol.get("outcome_access_before_registration")), ""]
    for key, title in SECTION_LABELS.items():
        lines.extend(["## " + title, "", render(get(protocol, "sections." + key)), ""])
        if key == "aims":
            lines.extend(["### Explicit hypothesis records", "", render(protocol.get("hypotheses")), ""])
    lines.extend([capture.structured_packet(protocol), ""])
    for key, title in (("execution", "Execution plan"), ("artifacts", "Pinned artifacts"),
                       ("quality_evidence", "Implementation evidence"), ("source_records", "Source records"),
                       ("reviews", "Review attestations"), ("open_decisions", "Open decisions")):
        value = protocol.get(key)
        displayed = "None remaining." if key == "open_decisions" and value == [] else render(value)
        lines.extend(["## " + title, "", displayed, ""])
    lines.extend(["## Mechanical blockers", ""])
    lines.extend(["- " + item for item in report["blockers"]] or ["No mechanical blockers found. Human review remains responsible for scientific adequacy."])
    lines.extend(["", "## Manual OSF handoff", "",
                  "Use the Simulation Studies form at https://osf.io/registries. Map the sections above to the live form; this is not an API import payload. Review the metadata, narrative, and attachments together. The public planning form has a repeated repetitions label above its nonconvergence prompt; map by the prompt's meaning if that repetition appears in the live form.", "",
                  "Attach the frozen protocol and supporting plans before submission. Verify the archived registration, required approvals, timestamp, and attachment hashes before confirmatory execution. Record the result in registration_record.json.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--freeze", action="store_true", help="require readiness; create a new local freeze directory")
    args = parser.parse_args()
    try:
        raw = args.protocol.read_bytes()
        protocol = json.loads(raw)
        if not isinstance(protocol, dict):
            raise ValueError("protocol root must be a JSON object")
        blockers = validate(protocol)
        report = {"status": "BLOCKED" if blockers else "READY_FOR_LOCAL_FREEZE",
                  "schema_version": protocol.get("schema_version"),
                  "review_digest": review_digest(protocol), "protocol_file_sha256": sha256(raw),
                  "blockers": blockers,
                  "scope": "Declared records and consistency only; no verification of scientific validity, remote artifact bytes, identities, or authenticated human agreement.",
                  "capture_outputs": ["decision_ledger.csv", "artifact_handoff.csv"],
                  "decision_status_counts": {status: sum(row["decision_status"] == status for row in capture.decision_rows(protocol))
                                             for status in sorted(capture.DECISION_STATES)},
                  "count_interpretation": "Field/status counts are not a scientific readiness score."}
        if args.freeze and blockers:
            print(f"Freeze refused: {len(blockers)} unresolved checks. Build a draft packet without --freeze to inspect them.")
            return 2
        args.out.mkdir(parents=True, exist_ok=not args.freeze)
        (args.out / "protocol.snapshot.json").write_bytes(raw)
        (args.out / "readiness.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (args.out / "osf_packet.md").write_text(packet(protocol, report), encoding="utf-8")
        decision_rows = capture.decision_rows(protocol)
        headers = list(decision_rows[0]) if decision_rows else ["field_path", "decision_status", "current_value_digest"]
        (args.out / "decision_ledger.csv").write_text(capture.csv_text(decision_rows, headers), encoding="utf-8")
        handoff = protocol.get("artifact_handoff", {})
        items = capture.objects(handoff.get("items")) if isinstance(handoff, dict) else []
        (args.out / "artifact_handoff.csv").write_text(capture.csv_text(items,
            ["id", "kind", "status", "location", "sha256", "immutable_version", "owner", "reason"]), encoding="utf-8")
        if args.freeze:
            freeze = {"local_frozen_at_utc": datetime.now(timezone.utc).isoformat(),
                      "protocol_file_sha256": sha256(raw), "review_digest": report["review_digest"],
                      "osf_registration": "Pending: local freeze does not register the study."}
            (args.out / "freeze.json").write_text(json.dumps(freeze, indent=2) + "\n", encoding="utf-8")
            files = sorted(p for p in args.out.iterdir() if p.is_file())
            (args.out / "SHA256SUMS.txt").write_text("".join(f"{sha256(p.read_bytes())}  {p.name}\n" for p in files), encoding="utf-8")
        print(f"{report['status']}: {len(blockers)} blockers; packet: {args.out / 'osf_packet.md'}")
        print(f"Review digest: {report['review_digest']}")
        return 2 if blockers else 0
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print(f"Cannot build packet: {error}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

