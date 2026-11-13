#!/usr/bin/env python3
"""Add missing undecided field records to a new v2/v3 protocol copy."""
import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))
from protocol_v2 import scaffold_provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="new JSON file; existing files are never overwritten")
    args = parser.parse_args()
    try:
        protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
        result = scaffold_provenance(protocol)
        encoded = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as destination:
            destination.write(encoded)
        added = len(result["provenance"]) - len(protocol["provenance"])
        print(f"Wrote {args.out}: {added} undecided records added. Existing decisions were not adopted or refreshed; rebuild review digests after changes.")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"Cannot scaffold provenance: {error}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
