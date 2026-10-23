# Reproduction

## 1. Recompute the public analysis

Python 3.10+; CPU; NumPy. No credentials, model, GPU, simulator or API calls.

```bash
python -m pip install -e .
python -m handback.analysis --root . --output reports/reproduced
python -m unittest discover -s tests -v
```

Expected: 84 logical units, three retry units, V joint successes 6/12, S1/S2 5/12, both screening gates false, and V/S1 selection equality true.

The CLI independently aggregates the CSV, cross-checks it against exported contact/predicate audits, refits the out-of-fold selector and reproduces its choices, compares realized training schedules, and recomputes original-attempt censoring bounds. These are checks on **derived public evidence**, not fresh reconstruction from raw physical logs.

## 2. Regenerate figures and the static report

```bash
python -m pip install -e ".[figures,docs]"
python scripts/make_figures.py
python scripts/build_site.py
python scripts/validate_release.py
```

The landing page is `docs/index.html`; its galleries and filters use local JavaScript, with no external services or telemetry. The static article is `docs/report.html`, generated from canonical `docs/report.md`.

To rebuild display media as well, download and verify the media-source ZIP from the versioned GitHub release, extract it, then run:

```bash
python -m pip install -e ".[media]"
python scripts/build_media.py --source-root /path/to/extracted-media-sources
```

See [media provenance](media.md): these are saved observations, not continuous motion videos. Re-encoding may change MP4 bytes across FFmpeg versions; the source PNG hashes remain the primary provenance.

## 3. Reuse the computational primitives

- `handback.features.public_features`: ten observed-prefix features; no simulator-truth argument.
- `handback.selector.select`: sequential S1/S2/V/fixed selection over a callback; later callbacks are not read after handback.
- `handback.selector.crossfit`: six-parent leave-one-parent-out fitting with fixed L2=1.
- `handback.support`: visual/action memory distances and strict tool-argument encoding, explicitly adapted to Piper.
- `handback.contacts.raw_peaks`: streamed external-robot contact maxima, registered cutoff and extra holds separated.

The earlier logistic `features.choose` prototype is retained for provenance; the final experiment uses `selector.select` and the visual/action gate. Unit tests are behavioral counterexamples, not evidence of robotic task success.

## 4. What cannot be rerun from this release

Full acquisition, training, rendering and evaluation depend on the local SFT checkpoint-99, original six-parent teacher library, historical replay inputs, SAM3 service, Piper/CAD adapters, MuJoCo compiled models and raw physical logs. Those are **not distributed here**, and the original study was not vanilla Guava. In particular, `move.motion_mode` is part of the Piper adaptation, not an official Guava argument. Removing it or replaying with a different registry would change the treatment.

Do not describe this package as a turnkey simulator benchmark or an end-to-end training reproduction. Upstream source is linked for context, not as a substitute for missing experiment artifacts. Training treatment, adapter and source hashes are released so an independently obtained archive can be compared to the recorded version.

No raw training dataset is claimed released. The compact numerical evidence fits GitHub; a Hugging Face repository is therefore not required for this version.
