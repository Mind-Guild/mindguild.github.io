# Mind Guild: working meeting to OSF simulation preregistration

Prepared for Mind Guild • Updated 12 November 2026 • Toolkit and schema version 2.0

**The meeting produces decisions; a structured protocol carries those decisions into code, analysis, and the OSF form.** AI can extract, organize, and check the plan. Researchers decide the scientific commitments and review the final registration.

Kevin's verified OSF profile: https://osf.io/user/zryq5. This is a contributor profile. A new simulation study needs its own registration. No OSF draft or registration has been created by this kit.

## 1. The pipeline

| Stage | Work | Concrete output | Completion condition |
| --- | --- | --- | --- |
| Capture | Preserve timestamped notes, slides, code/config/input snapshots, and prior-results disclosures. Keep speaker attribution explicit. | Source records, artifact handoff, and decision ledger | Suggestions, agreements, disagreements, and unknowns are distinguishable. |
| Specify | Connect each construct to a measure, estimand, manipulation, comparator, rival explanation, and conclusion limit. Record component and learning status separately. | Structured v2 `protocol.json` | Each confirmatory hypothesis has a complete claim-to-measure map. |
| Check feasibility | Implement and inspect generator, baselines, scoring, and analysis using disclosed pilot seeds and synthetic results. | Pilot log and quality evidence | The design can run; failures and information seen are documented. |
| Review and freeze | Resolve choices; have science, implementation, and analysis reviewed; pin code, dependencies, split manifest, and seed plan. | Local frozen packet and checksums | No unresolved confirmatory decisions; reviews refer to the same protocol digest. |
| Register | Complete OSF's Simulation Studies form, attach the frozen protocol and supporting plans, choose access, and submit. | OSF registration URL, timestamp, and status | The registration is completed and archived; the recorded plan precedes confirmatory runs. |
| Execute | Run the registered design and retain every planned run's status and provenance. | Run manifest, raw outputs, checkpoints, analysis outputs | Planned runs are accounted for, including failures. |
| Report | Compare each registered prediction with its estimate, uncertainty, and departures from plan. | Hypothesis-by-hypothesis report and deviation log | Planned and exploratory analyses remain identifiable. |

**The key boundary:** disclose exploratory work, then freeze and register before generating new confirmatory runs. V2 also supports a separately labeled analysis-only scope for already-generated outputs that remain uninspected; it does not describe their generation as prospective. Already-inspected confirmatory outputs cannot pass that gate. A local timestamp, uploaded protocol file, or saved OSF draft does not complete an OSF registration. State exactly what was generated and inspected and define the remaining unobserved target.

## 2. A 45-minute working meeting

Use `templates/meeting_worksheet.md`. One person facilitates; one person captures decisions. A person can cover multiple roles.

| Minutes | Decision to make |
| --- | --- |
| 0–5 | Which bounded claim are we testing, and what relevant results have we already seen? |
| 5–15 | What is the primary hypothesis, causal contrast, primary outcome, and result that would challenge it? |
| 15–25 | What exactly generates observations? Which factors vary? Which combinations are held out? What are the baselines and ablations? |
| 25–35 | What is an independent replication? How will we select repetition count, aggregate outcomes, quantify uncertainty, and handle failures? |
| 35–40 | Sketch expected figures and fill in support, contradictory, negligible, and inconclusive result patterns. |
| 40–45 | Read back decisions, unresolved questions, owners, implementation tasks, and review responsibilities. |

Do not force numerical choices merely to finish the meeting. Give unresolved decisions an owner and a resolution method. The subsequent pilot and review close them before registration.

Add the [ten-minute protocol close](templates/protocol_close.md) when the discussion has generated several possible studies. It captures the chosen claim, competing explanation, expected plot, implementation/learning status, results already seen, artifact owners, and explicit agreement status.

## 3. Translate ideas into testable commitments

Use this chain for every hypothesis:

**Claim → mechanism or manipulation → comparator → observable outcome → estimator → decision rule → scope of conclusion.**

For the initial occlusion study, the following is a **proposed design**, not an agreement extracted from a meeting:

| Element | Candidate specification |
| --- | --- |
| Narrow claim | Persistent object representations improve color–object–location binding through occlusion. |
| Task | Track two differently colored balls; cue a target before occlusion; predict its location at a specified query time. |
| Comparison | Object-centric predictive model versus a global recurrent predictive model with matched observations, training budget, and comparable capacity. |
| Primary condition | Occlusion with held-out color × motion combinations; all primitive colors and motions occur in training. |
| Primary outcome | Identity-conditioned localization accuracy: a prediction falls within a fixed tolerance of the target and is closer to it than to a distractor. Fix tolerance, tie rules, and query timing before registration. |
| Primary estimand | Mean full-model minus baseline accuracy across independent training/evaluation blocks in the prespecified primary condition. |
| Mechanism check | Remove persistent object binding; compare loss of performance, including a visible control condition. Label secondary analyses and their multiplicity treatment. |
| Interpretation | A reliable advantage supports this operational claim under the tested generator. It does not establish phenomenal consciousness. |

Keep the first study bounded. Identity tracking, novel object–dynamics composition, and reward transfer are separable claims. A successor-feature reward-transfer advantage alone does not test composition of novel dynamics. For predictive rollouts, specify the actual learned transition/forward model as well as any successor features.

To prevent shortcut solutions, audit correlations between color, starting position, speed, query time, and label. A single object cannot reveal identity swaps. Keep simulator object IDs and hidden state out of model inputs unless they are an explicit, equally supplied condition. Establish identity before occlusion; do not let per-frame rematching hide swaps.

## 4. Plan expected results before looking at outcomes

Sketch a figure with x = condition, y = the primary metric, one series per model, and uncertainty over independent repetitions. Mark it **predicted / schematic**. Record the expected ordering, the minimum meaningful difference, and how each pattern will be interpreted. Predictions are not fabricated observations or guaranteed effects.

| Observed pattern | Prespecified interpretation to consider |
| --- | --- |
| Interval for the primary difference lies above the chosen meaningful-effect threshold | Supports the bounded superiority prediction. |
| Entire interval lies below zero | Evidence against the predicted direction for this comparison. |
| Entire interval is inside a prespecified negligible-effect region | Supports practical equivalence only if an equivalence procedure was selected in advance. |
| Interval spans meaningful benefit and negligible/adverse effects | Inconclusive; uncertainty is too large. |
| Sanity checks fail or outcome scoring is invalid | A measurement or implementation problem; document it before making a scientific claim. |

Choose one inferential procedure and exact interpretation rules. A nonsignificant result by itself does not falsify a theory. If several outcomes or contrasts are confirmatory, prespecify multiplicity handling or a hierarchical testing order.

## 5. Simulation details that must be fixed

- **Generator:** physics, distributions and numeric ranges, rendering, timestep, episode length, occlusion geometry, query timing, noise, action/observation schema, and fixed constants.
- **Splits:** explicit training, validation, and confirmatory scenario manifests; held-out combinations; distinct random streams; no checkpoint selection or probe fitting on the confirmatory set. Run a check that every held-out primitive is nevertheless represented in training.
- **Models:** exact configurations, parameter counts, training updates/data budget, tuning budget, checkpoint rule, probes, and ablations. State which resources are matched and report residual differences.
- **Replications:** independent training runs or matched blocks are the primary units; frames and episodes from one trained model are nested measurements. Fix training, generator, evaluation, and analysis RNG streams. Equal seed integers do not by themselves establish useful statistical pairing.
- **Estimator:** define within-episode, within-condition, and across-run aggregation, condition weights, confidence interval procedure, resampling unit, resample count, analysis RNG seed, and any alternative analysis triggers.
- **Stopping and failures:** fix the planned run count, training limit, crash retry cap, resume rule, nonconvergence classification, missing-outcome treatment, and study-interruption policy. Poor learning is an outcome, not an automatic exclusion. Preserve unsuccessful attempts.
- **Implementation:** inspect generator properties, split leakage, hand-calculated metric cases, and a complete dry run. Run analysis on synthetic positive, zero, and negative effects to check sign and interpretation.

Use development held-out combinations for piloting and reserve the final confirmatory combinations from model selection. Disjoint seed integers alone do not prevent leakage from repeated tuning on the final test regime. If prior pilots already informed the final design, disclose that information and define what fresh comparison remains prospective.

If methods share an evaluation panel, intervals across training runs alone are conditional on that panel. To target variability over new scenes, design independent evaluation panels per block or specify an analysis that represents the additional level of sampling. Sharing a panel within a genuinely independent block can support paired comparisons; document the construction.

For planning a mean paired difference, an approximate 95% interval half-width is `h ≈ 1.96 × s_d / sqrt(R)`, where `s_d` is the SD across independent block differences and `R` is their count. Thus `R ≈ (1.96 × s_d / h)^2`. For illustration only, `s_d = .10` and `h = .03` gives 43 blocks after rounding up. This is a normal-approximation precision calculation, not a final sample size recommendation or a power calculation. Disclosed pilots can inform `s_d`; check the chosen interval procedure and computational budget before freezing. More episodes do not substitute for independent model runs. [4,5]

## 6. Use the kit

1. Fill the meeting worksheet and protocol close. Use `prompts/transcript_to_protocol.md` with the transcript, blank protocol, and [v2 record reference](SCHEMA.md) to produce a sourced draft.
2. Copy `templates/protocol.blank.json` into your study folder as `protocol.json`. The illustrative occlusion version is in `examples/occlusion.proposed.json`. Existing v1 protocols can be copied forward with `python scripts/migrate_protocol.py old-protocol.json --out protocol.json`; the migration preserves old content, adds unresolved v2 records, and clears active approvals while retaining their history.
3. Run the compiler from the kit folder with Python 3.10 or newer; no extra packages are required:

```bash
python scripts/build_packet.py examples/occlusion.proposed.json --out review-packet
```

It writes `osf_packet.md`, `readiness.json`, `protocol.snapshot.json`, `decision_ledger.csv`, and `artifact_handoff.csv`. Exit code 2 means unresolved decisions; exit code 0 means its mechanical checks pass. The example intentionally fails readiness. V2 checks structured scientific records, declared artifact pins, result-access boundaries, per-field agreement/value digests, seed overlap, and review digests. It does not verify scientific validity, remote artifact bytes, identities, or authenticated human agreement. Field counts are not a scientific readiness score.

4. Resolve blockers. To create missing field-record slots without adopting any values, run `python scripts/scaffold_provenance.py protocol.json --out protocol.capture.json`. Edit the new copy using the evidence and actual decisions. `decision_ledger.csv` supplies the current value digest for each tracked field; writing that digest does not itself document agreement. Each required field needs its origin, source/locator, decision owner, and decision record. Analyst proposals also need explicit human-adoption evidence. Record science, implementation, and analysis reviews against the completed protocol's `review_digest`. One researcher can cover several roles. Any scientific edit invalidates the corresponding field decision and changes the overall review digest. Use the selected completed file in the freeze command below.
5. Set `status` to `approved_for_freeze`, then create a new local freeze directory:

```bash
python scripts/build_packet.py protocol.capture.json --out frozen-v2 --freeze
```

The freeze contains the copied plan, rendered packet, hashes, and local freeze metadata. It is an archival convention, not an OSF timestamp or an access control. Protect the directory and version it. No network requests or simulations run through this script.

Compiler checks can be run with `python -m unittest discover -s tests -v`. Test fixtures are synthetic declarations used only to verify software behavior; they are not scientific plans or recorded human approvals.

## 7. Complete the OSF registration

Use the OSF **Simulation Studies** template, which follows ADEMP: aims, data-generating mechanisms, estimands/targets, methods, and performance measures. It also asks about repetitions, Monte Carlo uncertainty, failures, software, and reproducibility. It is a sensible starting point for this algorithm-comparison simulation; check the form against the final design. [1,2]

Open https://osf.io/registries or your My Registrations page and start a new draft. Use Kevin's profile when resolving the contributor identity; confirm all other contributors, their order, license, subjects, and access choice. Paste the packet into the corresponding form sections and attach the frozen protocol and supporting manifests/code snapshot before submission. Review the form against the attached files. [2,3]

As of 11 November 2026, OSF is transitioning its Projects functionality. New projects/components cease on 16 November 2026, and existing projects become read-only on 19 February 2027. Build ongoing collaboration around your versioned research repository and create registrations directly through the registration workflow. Submitted attachment files cannot be replaced; eligible form responses can receive transparent updates. Archive amended materials elsewhere and link the outputs as appropriate. [3]

After submission, verify the registration is archived and approvals complete. Record its URL, registration timestamp, status, and frozen protocol digest in `templates/registration_record.json`. Check those records before starting confirmatory runs. Public registrations receive a DOI; an embargoed record can be cited by its registration URL until public. [2]

## 8. Carry the same plan through execution and reporting

Use `templates/run_manifest.csv` to account for each planned method × block × condition and every attempt. Store raw outputs and checksums without discarding failures. Keep `templates/deviations.csv` current. For a change, record what changed, why, when, who approved it, and what results were visible then. Preserve the original plan and make an OSF update or new registration appropriate to the change; subsequent registration cannot make previously observed analyses prospective.

The final report should list every registered hypothesis, its prespecified contrast, estimate, uncertainty, interpretation, and deviations. Put new questions and unplanned analyses in an explicitly exploratory section. Attach schematic expectations and actual results separately.

## 9. Smallest implementation package

For your next coworking session, complete these work items in order:

1. Capture one hypothesis and produce the sourced decision ledger.
2. Implement two-object occlusion trajectories, a split manifest, and deterministic scoring.
3. Run a simple motion-prediction sanity baseline and test scoring on known identity swaps.
4. Implement the two comparable predictive models and run a disclosed feasibility pilot.
5. Select independent repetition count and exact analysis, resolve remaining fields, review, freeze, and register.

The MVP is complete when a researcher can trace one claim from the meeting into an executable design and a complete OSF registration packet. Full API submission and a dashboard can be added later. They are not prerequisites for a useful first study.

## 10. Structured study records in v2

The video-based pipeline test identified five additions that are now part of the template, prompt, packet, and freeze checks:

| Record | What it captures | Freeze behavior |
| --- | --- | --- |
| `claim_measure_map` | Construct, operational definition, metric/estimand, mechanism, control, rival explanations, expected result patterns, and conclusion limits. | Every confirmatory hypothesis needs a linked map. A directly encoded effect requires an explicit interpretation limit. |
| `components` | Separate implementation and evidence states, inclusion in this study, artifact IDs, and source IDs. | Selected components must be implemented. Demonstrated behavior is distinct from verification; excluded future components can remain planned. |
| `learning` | Offline calibration, within-run state dynamics, and online parameter updates, including the objective and teaching/error/reward signal when applicable. | Each phase is explicitly enabled or disabled. A named learning rule without its signal/objective is incomplete. |
| `provenance` | Field path, source/locator, agreement status, original speaker attribution, actual decision owner, and value digest. | Proposals are not treated as decisions. Unknown speakers remain unresolved. Changed values require renewed field decisions and review. |
| `artifact_handoff` and `results_access` | Versioned artifacts; prior results, who saw them and when, influence on design, reserved runs, and the prospective scope. | Missing core artifacts, incomplete exposure declarations, and already-inspected confirmatory targets block freeze. |

The [schema reference](SCHEMA.md) explains the record shapes, conditional requirements, provenance workflow, and migration. The [changelog](CHANGELOG.md) describes the v2 compatibility change. Ordinary study outputs continue to use the same run manifest and deviation log.

## Sources

Checked 11 November 2026. The workflow and example above are original recommendations; linked sources establish the OSF options and underlying methodological guidance.

1. Center for Open Science. Simulation Studies preregistration template introduction: https://www.cos.io/blog/introducing-the-simulation-studies-preregistration-template
2. OSF. Registration guide and template list: https://help.osf.io/article/330-welcome-to-registrations
3. OSF. Projects transition: registration questions and use cases: https://help.osf.io/article/768-osf-projects-transition-registration-questions-and-use-cases ; transition dates: https://help.osf.io/article/770-registrations
4. Morris, White & Crowther (2019). Using simulation studies to evaluate statistical methods. https://doi.org/10.1002/sim.8086
5. Agarwal et al. (2021). Deep Reinforcement Learning at the Edge of the Statistical Precipice. https://arxiv.org/abs/2108.13264
6. Siepe et al. (2024). Simulation studies for methodological research in psychology. https://doi.org/10.1037/met0000695
7. OSF-linked public planning form (consulted to align section headings): https://docs.google.com/document/d/1aA9kdjUS2dGtti45QdgxKUAuQMaOjvHMWyjxTtSpl_8/edit

Context used: `paper outline 20261106.docx` and the available opening sections of `Draft Position Paper 20261104.docx`, plus your current occlusion-task direction. These motivate the example; they do not establish finalized numerical design decisions or completed implementations.

