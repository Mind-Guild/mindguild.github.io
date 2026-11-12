# V2 validation

Checked 12 November 2026.

- **46 standard-library tests passed.** The cases cover valid completed declarations, incomplete drafts, claim/rival/scope records, component readiness, learning-phase distinctions, provenance paths and stale decisions, explicit analyst-proposal adoption, artifact pins, prospective results access, safe migration/scaffolding, and freeze/output behavior.
- **The previous Bogdan Fly draft was migrated and scaffolded.** Its hypotheses, OSF narratives, and 12 source records were preserved. New learning/access choices remained unknown, active approvals were absent, and the freeze remained blocked without creating a freeze directory.
- **The occlusion example remains a proposal.** Its structured additions are labeled as analyst proposals. Unknown quantities, capture items, adoption, and reviews remain open. The generated packet includes the decision and artifact CSV exports.
- **The website and ZIP are generated from the same toolkit source.** JSON parsing, relative links, section anchors, and archive integrity are checked before publication.

Run the software tests from this toolkit folder:

```bash
python -m unittest discover -s tests -v
```

Compile the intentionally incomplete worked example:

```bash
python scripts/build_packet.py examples/occlusion.proposed.json --out review-packet
```

Expected exit code: 2. To inspect the freeze boundary, use the same command with a new output directory and `--freeze`; it must refuse the incomplete protocol. The helpers do not perform a simulator run or an OSF submission. Passing tests does not verify a study's scientific claims or authenticate its review attestations.
