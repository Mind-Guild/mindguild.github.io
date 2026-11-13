#!/usr/bin/env python3
"""Summarize synthetic calibration intervals using the frozen decision mapping.

Does not generate simulations, tune a rule, authenticate input data, or provide
confirmatory evidence. Keep inputs, generator assumptions, code, and report pins.
"""
import argparse
import hashlib
import json
from pathlib import Path

import protocol_v2 as capture
import protocol_v3 as theory


def summarize(protocol, calibration):
    if not isinstance(protocol, dict) or type(protocol.get("schema_version")) is not int or protocol.get("schema_version") != 3:
        raise ValueError("Use a schema v3 protocol")
    if not isinstance(calibration, dict) or calibration.get("data_role") != "synthetic_calibration":
        raise ValueError("Input data_role must explicitly be synthetic_calibration")
    for key in ("generator_description", "assumptions_and_range", "sampling_and_seed_derivation"):
        if not isinstance(calibration.get(key), str) or not calibration[key].strip():
            raise ValueError("Supply calibration " + key)
    contract = protocol.get("test_contract")
    if not isinstance(contract, dict):
        raise ValueError("Missing test_contract")
    contrasts = {c.get("hypothesis_id"): c for c in capture.objects(contract.get("contrasts"))}
    assurance = {a.get("hypothesis_id"): a for a in capture.objects(contract.get("design_assurance"))}
    records = calibration.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("Supply synthetic calibration records")
    seen, groups, outcomes = set(), {}, []
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("Each calibration record must be an object")
        hid, scenario, run_id = row.get("hypothesis_id"), row.get("scenario"), row.get("run_id")
        if not isinstance(hid, str) or hid not in contrasts or hid not in assurance:
            raise ValueError("Each calibration record must link a declared contrast and assurance plan")
        if not isinstance(scenario, str) or scenario not in theory.SCENARIOS or not isinstance(run_id, str) or not run_id.strip():
            raise ValueError("Use null/target/rival scenarios and nonempty run IDs")
        identity = (hid, scenario, run_id)
        if identity in seen:
            raise ValueError("Duplicate calibration run ID within hypothesis/scenario")
        seen.add(identity)
        interval, valid = row.get("interval"), row.get("valid")
        outcome = theory.adjudicate(contrasts[hid], interval, valid)
        true_value = row.get("true_estimand")
        if not theory.finite_number(true_value):
            raise ValueError("Supply each synthetic run's finite true_estimand")
        counts = groups.setdefault((hid, scenario), {"total": 0, **{k: 0 for k in theory.OUTCOMES}, "coverage": 0, "precision_achieved": 0})
        counts["total"] += 1; counts[outcome] += 1
        if valid and interval[0] <= true_value <= interval[1]: counts["coverage"] += 1
        width = assurance[hid].get("maximum_interval_width")
        if valid and theory.finite_number(width) and width > 0 and interval[1] - interval[0] <= width: counts["precision_achieved"] += 1
        outcomes.append({"hypothesis_id": hid, "scenario": scenario, "run_id": run_id, "outcome": outcome})
    rows = []
    for (hid, scenario), counts in sorted(groups.items()):
        if counts["total"] < 2:
            raise ValueError("Each supplied scenario needs at least two independent calibration replicates")
        events = ("precision_achieved", "coverage") if assurance[hid].get("strategy") == "precision" else (("rival_only",) if scenario == "rival" else ("target_only",))
        for event in (*events, "invalid"):
            lo, hi = theory.wilson95(counts[event], counts["total"])
            rows.append({"hypothesis_id": hid, "scenario": scenario, "event": event,
                         "count": counts[event], "total": counts["total"], "rate": counts[event]/counts["total"],
                         "wilson95_lower": lo, "wilson95_upper": hi, "all_outcome_counts": counts})
    expected = {(hid, scenario) for hid in contrasts for scenario in theory.SCENARIOS}
    if set(groups) != expected:
        raise ValueError("Supply null, target, and rival calibration for every declared contrast")
    return {"data_role": "synthetic_calibration_summary", "criteria_results": rows, "outcomes": outcomes,
            "calibration_basis_sha256": {hid: theory.assurance_basis_digest(protocol, hid) for hid in contrasts},
            "scope": "Conditional design calibration, not confirmatory results or scientific validation. Wilson intervals assume independent Bernoulli calibration draws."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", type=Path)
    parser.add_argument("calibration", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        protocol_raw, calibration_raw = args.protocol.read_bytes(), args.calibration.read_bytes()
        protocol, inputs = json.loads(protocol_raw), json.loads(calibration_raw)
        result = summarize(protocol, inputs)
        result.update(protocol_file_sha256=hashlib.sha256(protocol_raw).hexdigest(),
                      calibration_input_sha256=hashlib.sha256(calibration_raw).hexdigest(),
                      decision_contract_sha256=capture.value_digest(protocol["test_contract"]["contrasts"]),
                      calibration_description={k: inputs.get(k) for k in ("generator_description", "assumptions_and_range", "sampling_and_seed_derivation")})
        encoded = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as output: output.write(encoded)
        print(f"Wrote synthetic calibration summary to {args.out}; pin it as an analysis artifact. No plan values or approvals were changed.")
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Cannot summarize calibration: {error}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
