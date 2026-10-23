# Data card: HandBack bounded validation

This directory is a **derived research evidence dataset**, not a robot SFT dataset.

| File | Unit / purpose |
|---|---|
| `stage_a.csv` | 84 logical method×scene rows; all successes and failures |
| `first_attempt_bounds.csv` | Seven method-level bounds without substituting retries |
| `selection.json` | Six parents, ten-dimensional public features, development labels, OOF models and causal selection traces |
| `returnability.json` | Method selections evaluated against reused same-state executions; shared executions are not independent replications |
| `contact_audits.jsonl` | 84 derived raw-log audit records with source/image hashes |
| `predicate_audits.jsonl` | 84 derived task-predicate reconstruction records |
| `mechanism_audit.json` / `tensor_comparison.json` | Realized schedules, saved-weight checks and numerical V/S1 differences |
| `interruption_audit.json` | Three original interrupted attempts, observed contact lower bounds and retry comparisons |
| `geometry_*.json` | Six saved-state CAD diagnostics and explicit certification limits |
| `costs.json` | Project-level measured cost summaries; nested timers must not be added |
| `model_pairing.json` | Same-scene compiled-model identity across methods |
| `recorded_stage_a.json` | Recorded screen output; CSV aggregation is checked against it |
| `export_manifest.json` | Original artifact hashes, export hashes and transformations |
| `closure_verification.json` | Original closure-check record, path-sanitized; not a new external replication |
| `media_manifest.json` / `media_sources_archive.json` | Display-media lineage, source-image hashes and release-archive integrity |

## Columns and units

`method`: U/B/F4/Fbest/S1/S2/V. `seed`: paired simulation scene ID, not a participant. `original_predicate`: terminal task predicate. `complete_and_held`: predicate plus explicit completion and ten registered holds. `joint_1mm/2mm/5mm`: completion plus external-contact bound. `external_depth_mm`: registered-interval maximum in **millimetres**. `infrastructure_retry`: one only for V/4062104004, S1/4062104007 and S1/4062104011.

JSON contact distances/peaks with suffix `_m` use **metres**. A maximum includes control actions and registered holds; twenty additional audit-only simulation steps are excluded from the primary metric and reported separately. Robot self-contacts and object–object contacts are not part of the external-robot metric. Zero external depth does not prove task success or physical validity.

## Provenance and exclusions

Exported from the closed 22–23 October 2026 single-task study. Originals remain unchanged. `artifact://...` is a stable identifier replacing private storage roots, **not a resolvable download link**. Source hashes document lineage; they do not make unavailable raw files verifiable by readers. Field names such as `raw` in the recorded result mean complete-and-held, not merely the original predicate; use the explicit CSV columns.

No new trajectories were generated for this release. No interrupted case was silently removed. Selected camera observations/review panels are available in the media-source release archive; display crops and labelled replays are in `docs/assets/media/`. Full raw native conversations, raw `.gz` physical logs, MuJoCo binaries, executable snapshots and model weights are not bundled. Original 84-run image/physical checks were internal record checks, not independent external replication. Evaluator truth was used offline only.

The derived numbers and audit summaries are CC BY 4.0. Upstream datasets/models/assets are not relicensed or redistributed. These files do not establish real-robot safety or suitability for training.
