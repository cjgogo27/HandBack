# HandBack

**When should a teacher return control to a robot learner?**

A bounded Piper/Guava study: 7 methods, 12 paired scenes, one training seed.
The learning-value selector did **not** establish an advantage over support-based handback; the planned larger experiment was not run.

[Technical report](docs/report.md) · [Project page](https://cjgogo27.github.io/HandBack/) · [Results](data/stage_a.csv) · [Reproduction](docs/reproduction.md)

```bash
python -m pip install -e .
python -m handback.analysis --output reports/reproduced
python -m unittest discover -s tests -v
```

No GPU or network is needed after installation. This reproduces the published analysis and selector decisions, **not** the original training or simulator rollouts.

| Method | Joint success* | >5mm contact |
|---|---:|---:|
| Replay only | 5/12 | 2/12 |
| First support | 5/12 | 4/12 |
| Two scheduled supports | 5/12 | 3/12 |
| Learning-value exit | 6/12 | 4/12 |

*Task completion + 10 registered holds + maximum external robot contact depth ≤2mm. Includes three infrastructure re-executions; this is a simulation metric, not hardware safety certification. Learning-value exit and first support selected identical training treatments.

Code: [MIT](LICENSE). Report and derived results: [CC BY 4.0](DATA_LICENSE.md). [Data scope](data/README.md) · [Citation](CITATION.cff) · [Contact](mailto:cj3332740@outlook.com).
