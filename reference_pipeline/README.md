# Frozen pipeline references

These six project-written scripts document the **performed** pooled update, evaluation instrumentation, raw-contact recomputation, predicate reconstruction and derived rendering. Source SHA256 and export transformations are in `data/export_manifest.json`.

They are not installed by the package and are **not a standalone runnable pipeline**. Private storage roots are replaced by non-resolving `artifact://` identifiers. They depend on undistributed original runtime adapters, model weights, data and services. Do not execute them with guessed substitutions or treat a failed import as a request to create a new collection run. No launcher, credentials or remote SSH helper is included.

Use `src/handback/` for the portable, tested computational primitives and `docs/reproduction.md` for the supported CPU analysis path. The reference scripts retain the original tool-contract adaptation, evaluation loss masking, control logging and explicit completion handling so these implementation choices can be inspected instead of inferred from prose.
