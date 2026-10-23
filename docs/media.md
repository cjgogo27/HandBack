# Visual evidence and replay provenance

## What the website displays

| Media | Source | Limitation |
|---|---|---|
| 84 final-observation images | Lossless 480×360 display crops from nine archived native-image review panels | Last saved model observation, not a post-hold camera certificate; occlusion remains |
| Three H.264 observation replays | Original 640×480 native observations for V/4062104002, V/4062104006, V/4062104008 | Discrete saved observations at 1 image/s; no interpolation, no continuous motion footage, no real-time claim |
| Two peak-contact diagnostics | Existing U/V derived renders from logged body poses | Not native camera frames; imperfect registration; not exact visual overlap or hardware safety proof |

The three replay cases are post hoc illustrations of joint success, incomplete task, and completion with failed contact screen. They cannot estimate success rate. Burned-in labels occupy an added band above the uncropped source image; no scene pixels are invented. The method comparison always uses the complete numerical table, not a selected successful clip.

No new robot actions, physics integration or model requests were performed to create these media. Both selected V/S1 scene-4002 image sequences contain the original saved observations; the two methods' 16 image hashes match in that scene, which is a local observation equality, not global policy equality.

## Download original media sources

[Versioned source archive](https://github.com/cjgogo27/HandBack/releases/download/v0.1.0/handback-media-sources-v0.1.0.zip) · [Archive SHA256 and size](../data/media_sources_archive.json) · [Per-display provenance](../data/media_manifest.json)

The ZIP contains four selected episode observation folders (V/4002, S1/4002, V/4006, V/4008), nine original review panels, two derived peak frames, display-code metadata and an `archive_index.json` with file hashes. It is **not** the complete native trajectory or training dataset. The source archive is about 44 MB, suitable for a GitHub release asset; Hugging Face is unnecessary for this compact evidence release.

Rebuild using `scripts/build_media.py --source-root <extracted-directory>`. The original-source index and per-episode manifests use relative paths. `media_manifest.json` links original native-image hashes, panel hashes, crop transforms, and exported hashes. Check the archive checksum before extracting.

## Attribution

These are this study's simulation outputs, using Guava/robosuite/Piper scene assets. Underlying meshes/models remain subject to their upstream terms and are not redistributed here. The media do not depict a physical robot or a human participant. The repository's MIT grant does not relicense embedded third-party asset designs. See [external dependencies](../THIRD_PARTY.md).
