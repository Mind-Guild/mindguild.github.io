# V3 validation

Checked 13 November 2026.

- **81 standard-library tests passed.** They cover the existing capture/provenance/freeze boundaries plus claim-level restrictions, account versions and bridges, quantitative prediction regions, all six adjudication outcomes, sensitivity criteria and Wilson uncertainty, invalid-run accounting and denominator consistency, stale calibration, critical perspective acceptance, masking, replication, reporting, safe migration, and CLI output preservation.
- **The actual previous Bogdan Fly v2 capture was migrated to v3.** Its hypotheses, OSF narratives, 12 source records, learning declarations, and results-access records were preserved. Six new contract-group provenance rows remained undecided, active approvals were absent, and freeze was refused without creating a directory.
- **The occlusion example remains an analyst proposal.** The new scope is a candidate mechanism benchmark, not evidence of consciousness. No numerical region, calibration count, perspective acceptance, passed control, or OSF registration is supplied. Its generated review packet remains blocked.
- **Calibration tests use synthetic software fixtures.** They do not constitute scientific power calculations for either real candidate. Invalid runs are retained in denominators. Rate checks include calibration uncertainty and a separate invalid-rate criterion under every scenario.
- **Website/ZIP checks:** JSON parsing, links, section IDs, source-to-archive byte equality, and absence of generated Python caches are checked before publication. Browser QA verifies the updated guide and published download.

Run tests from the toolkit folder:

```bash
python -m unittest discover -s tests -v
```

Build the deliberately incomplete example:

```bash
python scripts/build_packet.py examples/occlusion.proposed.json --out review-packet
```

Expected exit code: 2. With `--freeze` and a new output directory it must refuse without creating that directory. A mechanically complete synthetic fixture is used to check successful archival, hashes, and non-overwrite behavior; it is not a researcher-approved study.

The helpers do not execute a simulator, retrieve artifact bytes, authenticate reviewers, register with OSF, or establish scientific validity. Reviewers must inspect calibration input/generator/code/report consistency and assess whether the tested assumptions warrant the stated conclusions.
