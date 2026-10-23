# External dependencies and boundaries

| Project | Role | Redistributed here? |
|---|---|---|
| [Guava](https://github.com/hdacnw/guava-release) | Original task/tool framework and configuration reference | No upstream source or assets |
| [robosuite](https://github.com/ARISE-Initiative/robosuite) | Simulator framework; experiment used an author fork | No |
| [MuJoCo](https://github.com/google-deepmind/mujoco) | Physics and original offline geometry analyses | No binaries or compiled models |
| [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) | Source model for the local SFT student | No weights |
| NumPy / Matplotlib / Python-Markdown | Released analysis and optional figures/site build | Installed from their own distributions |

The selector, feature extractor, support encoder and contact primitive are extracted from project-written experiment code, with import/path packaging documented in `data/export_manifest.json`. They are not copies of AutoIntervene's implementation. The support baseline is an explicit Piper adaptation, not a claim to reproduce its original benchmark.

The original environment's assets and model adapters are not implied to be interchangeable with upstream defaults. Consult each linked project's license for independent reuse.
