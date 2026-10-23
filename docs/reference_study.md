# HandBack: report and release precedents

Checked 2026-10-23. This is a writing/release study, not a new literature review claiming novelty or a reproduction of these projects. Sources below are original papers, author project pages, and author repositories. Reading scope: abstracts plus the explicitly listed core sections; not a claim that every page, proof, appendix, video, or implementation was examined. No external project was installed or rerun for this study.

## Ten original technical papers/reports

| Work | Original source and checked sections | Useful reporting pattern for HandBack |
|---|---|---|
| **AutoIntervene: Calibrated Intervention for Action-Chunking Imitation Learning Policies** (2026), Jinhe Tang and Weiming Zhi | [Paper](https://arxiv.org/html/2608.07065), §III-C control selection, §III-D adaptation, §IV main and handoff comparisons | Separate control-transfer performance from subsequent policy adaptation; show control-data time beside success. For HandBack, say the support baselines are a tool-level adaptation, not a reproduction of the original monitor. |
| **Efficient Recovery Learning using Model Predictive Meta-Reasoning** (2023 revision), Shivam Vats, Maxim Likhachev, Oliver Kroemer | [Paper](https://arxiv.org/html/2209.13605v2), §V-B and §VI-B | Define the quantity optimized by training-resource allocation and compare to simpler allocation. Do not claim that expected learning progress in recovery allocation is new. |
| **A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning** (2011), Stéphane Ross, Geoffrey J. Gordon, J. Andrew Bagnell | [Paper](https://arxiv.org/pdf/1011.0686), Algorithm 3.1, assumptions around Theorems 3.1–3.2, §5 | State exactly which data distribution an update uses, keep guarantees conditional, and distinguish algorithms from finite empirical tests. |
| **HG-DAgger: Interactive Imitation Learning with Human Experts** (2018 preprint), Michael Kelly et al. | [Paper](https://arxiv.org/pdf/1810.02890), §II, Algorithm 1, §III–IV | Make expert and novice control authority explicit. Its risk threshold is not a general safety certificate; HandBack must likewise distinguish support acceptance from verified successful return. |
| **Human-in-the-Loop Imitation Learning using Remote Teleoperation** (2020 preprint), Ajay Mandlekar et al. | [Paper](https://arxiv.org/pdf/2012.06733), §IV-C IWR, §V tables I–IV, conclusion | Use crossed dataset/method comparisons to distinguish better collected data from better training. Report equal-budget full-demonstration and replay controls. |
| **Deep Reinforcement Learning at the Edge of the Statistical Precipice** (2021), Rishabh Agarwal et al. | [Paper](https://arxiv.org/html/2108.13264), §§3–6, Appendix A.1 and A.5 | Put uncertainty and run-level records before rankings. HandBack has one training seed and one task: do not borrow multi-task bootstrap machinery to manufacture confidence or claim significance. |
| **Deep Reinforcement Learning that Matters** (2018 publication; 2017 preprint), Peter Henderson et al. | [Paper](https://arxiv.org/pdf/1709.06560), experimental analysis, codebase/random-seed discussion, discussion and recommendations | Report implementation, seed, evaluation, and checkpoint choices explicitly. A small score difference is not evidence of an algorithmic mechanism. |
| **Implementation Matters in Deep Policy Gradients: A Case Study on PPO and TRPO** (2020), Logan Engstrom et al. | [Paper](https://arxiv.org/pdf/2005.12729), §§3–4 and code-level optimization ablations | Inspect realized treatment, not just method names: record selection, examples, order, hyperparameters, and weight differences before attributing gains. |
| **What Matters in Learning from Offline Human Demonstrations for Robot Manipulation** (2021), Ajay Mandlekar et al. | [Paper](https://arxiv.org/html/2108.03298), §3 study design, §4.1–4.2 tables, §4.5 policy selection, §5 | Organize a study around questions, controls, and lessons. Separate raw task success, completion/holding, and contact screens. Disclose model selection rather than presenting the best checkpoint as automatic. |
| **LIBERO: Benchmarking Knowledge Transfer for Lifelong Robot Learning** (2023), Bo Liu et al. | [Paper](https://arxiv.org/html/2306.03310), §§4.2–4.4, §5 metrics/results, §7 limitations | Fix task suites and disentangle the factor being tested; publish task/config/data access. HandBack should keep its single-task scope visible rather than imitate benchmark breadth. |

These are ten distinct original technical studies; they are not all documents self-labelled “technical report.” Several are conference papers or preprints. Their publication status does not transfer to HandBack.

## Five checked publication organizations

| Project | What was actually checked | Release organization | Adopt / do not adopt |
|---|---|---|---|
| **robomimic** | [Homepage](https://robomimic.github.io/), [repository](https://github.com/ARISE-Initiative/robomimic), README's benchmark/data/Docker links | A compact project landing page links the study paper, study website, documentation, code; the repository separates examples, tests, docs, and package. README records migration of datasets to Hugging Face. | Adopt a short front door with separate evidence/reproduction details. Do not imply HandBack provides robomimic-scale framework or full datasets. |
| **LIBERO** | [Repository](https://github.com/Lifelong-Robot-Learning/LIBERO), README's website/paper/docs links, installation, dataset download, training/evaluation examples | GitHub contains code/config/examples; a [project website](https://libero-project.github.io/) and docs are separate; dataset downloader supports [Hugging Face](https://github.com/Lifelong-Robot-Learning/LIBERO#datasets). The website's body was not extractable in this browser, so its visual design was not assessed. | Adopt explicit setup, data retrieval, task identity, train/eval split. Do not ship bulky data to HF merely to copy this form. |
| **rliable** | [Author page](https://agarwl.github.io/rliable/), [repository](https://github.com/google-research/rliable), paper Appendix A.1 | Landing page links paper, library, Colab, explanations, poster/slides; repository contains tests and an analysis notebook. Repository was displayed as archived/read-only at the check date. | Closest analysis-release pattern: small auditable data + executable analysis + paper. Do not imply its uncertainty estimators validate a one-seed HandBack result. |
| **Implementation Matters** | [Repository](https://github.com/MadryLab/implementation-matters), [raw README](https://raw.githubusercontent.com/MadryLab/implementation-matters/master/README.md), paper §§3–4 | Repository-first release: concise README, implementation toggles, config generation and training commands, explicit MuJoCo prerequisite and output format; a special website is not required. | Adopt minimal README and explicit knobs. For HandBack, separately label CPU result recomputation versus full GPU experiment regeneration. |
| **AutoIntervene** | [Author project page](https://aus.bot/research/autointervene/), method/video/result/citation sections, [paper](https://arxiv.org/html/2608.07065) | A research webpage explains four stages, gives task videos and tables, and links the paper. No code link was found in the inspected page; this is not confirmation that code exists or is unavailable everywhere. Video content itself was not reviewed in this study. | Adopt one concise result page linked to detailed evidence. Do not copy a promotional success framing, or call this an open-code precedent. |

The five cases show three valid forms: repository-first, paper+repository+analysis notebook, and webpage+paper. A project webpage is an entry point, not additional evidence. HandBack can keep all content in one GitHub repository and optionally render `docs/` with GitHub Pages.

## Recommended framing and structure

**Working report title:** *HandBack: A Bounded Feasibility Study of Learning-Value-Based Control Return in Piper Manipulation*.

The report should lead with: the completed bounded study did not pass its expansion criteria; realized value-based and first-support treatments were identical on the six parent cases, preventing attribution of their numerical score difference. This is not a proof that all learned control-return methods fail.

Suggested short report (roughly 4–6 pages if typeset; do not pad to fit a page count):

1. **Question and result:** distinguish immediate returnability from benefit after a policy update; state the failed gate in the abstract.
2. **Frozen protocol:** one task, six teacher parents, fixed prefix lengths, seven methods, 12 matched scenes, one training seed; what the student and selector can observe; 24 optimizer steps versus non-matched FLOPs.
3. **Results:** one primary table; realized choices/training-treatment table; reused immediate-return probes explicitly separate from new-scene tests.
4. **Identification and interruption audit:** identical S1/V choices and data; unexplained numerical weight divergence; 84 logical units versus 87 actual attempts; three preserved partials and first-attempt bounds.
5. **Measurement and cost:** engineering contact thresholds, geometry/visual limits, complete teacher-library acquisition already paid, no demonstrated online query savings.
6. **Conclusion and reuse:** no Stage B; reusable protocol, source snapshots, decision audit, outcome recomputation, contact/predicate checks; precise limits on broader claims.

Recommended repository boundary:

```text
README.md                  # question, one-sentence finding, one command, three links
REPORT.md                  # readable short technical report
docs/index.html            # same claim and result, optional static landing page
data/                      # small run-level results, decisions, sensitivity and cost records
src/                       # portable selection / analysis core
scripts/                   # regenerate tables + verify small public bundle
tests/                     # meaningful expected-value and consistency checks
provenance/                # frozen protocol, source hashes, dependencies and exclusions
LICENSE / THIRD_PARTY.md   # explicitly separate newly authored code and external assets
```

Public reproduction levels must be distinct:

- **Result recomputation:** run on the released small evidence bundle without H200, teacher API, model weights, or private paths; expected table values asserted.
- **Full experiment regeneration:** requires compatible Piper simulation/control assets, trained starting checkpoint, dependencies, teacher access, and GPU resources. If these are not released, say so. Do not call the small bundle a complete simulator reproduction.

Do not export credentials, user-machine paths, internal host/IP addresses, unrelated logs, private model weights, or third-party assets without redistribution rights. Sanitizing metadata must not silently alter raw experimental evidence; publish a derived view plus a transformation/provenance description.

## Concrete writing rules

- State **“did not meet the predeclared feasibility gate”**, not “proved ineffective,” “safe,” “novel,” “state of the art,” or “validated generalization.”
- Put the S1/V identical treatment finding beside the main score table, not only in limitations.
- Label the old return probes as reused executions; do not add method rows to obtain a fictitious number of independent tests.
- Do not invent error bars or p-values from 12 scenes as though they were independent training seeds.
- Distinguish original predicate, completed-and-held, and contact-screened joint outcome; explain that a 2 mm simulation threshold is not a hardware safety standard.
- Keep failures, no-handoff choices, interrupted attempts, and exclusion reasons. Never call missing observations successes or failures unless a monotone logged condition logically determines the result.
- No need for an inflated contributions list or ten borrowed citations in the short report. A few direct related works plus the evaluation references suffice; this reading note can be the source-list appendix.
- The release is an exploratory technical report and artifact bundle, not a claim of peer review, an external replication, a safety certification, or a complete reproduction of AutoIntervene.

## Verification performed for this note

All ten paper identities and cited section claims were checked against arXiv/PDF primary text; the rliable paper was also available through the [NeurIPS proceedings](https://proceedings.neurips.cc/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf). The five organization cases were checked through author pages/repositories as listed. No benchmark numbers from these works are reused as HandBack data. No claim is made that their code currently installs successfully. The note's recommendations are editorial judgments, not results of a comparison experiment.
