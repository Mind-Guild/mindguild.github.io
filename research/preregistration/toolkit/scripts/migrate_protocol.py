#!/usr/bin/env python3
"""Copy a v1/v2 protocol to v3, preserving content and clearing active reviews."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))
from protocol_v3 import migrate_to_v3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="new JSON file; existing files are never overwritten")
    args = parser.parse_args()
    try:
        raw = args.protocol.read_bytes()
        protocol = json.loads(raw)
        result = migrate_to_v3(protocol, hashlib.sha256(raw).hexdigest())
        encoded = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as destination:
            destination.write(encoded)
        print(f"Migrated to {args.out}. New records are unresolved; all active reviews require renewal.")
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(f"Cannot migrate protocol: {error}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
