# Five robotics releases: lessons for the HandBack results page

Checked 2026-10-23. These are five well-known public robotics code projects, not a formal popularity ranking. Official repositories, project-page text, media elements/captions, and reproduction instructions were inspected. Video files were **not played or downloaded**; descriptions below concern their displayed organization and labels, not independent confirmation of the robot behaviors. No external assets should be copied into HandBack.

## What the five projects show

| Project and official sources | Presentation actually checked | Failure / limitation presentation | Concrete HandBack adaptation |
|---|---|---|---|
| **LeRobot** — [GitHub](https://github.com/huggingface/lerobot), [official Hub page](https://huggingface.co/lerobot), [dataset browser](https://huggingface.co/spaces/lerobot/visualize_dataset) | README separates data format, policies, training and evaluation; MP4/images are associated with Parquet state/action records. The Hub page connects models, datasets, documentation, and an episode-viewer Space. The Space wrapper advertises an embedded application, but that application was not interacted with. | The inspected landing page is a tool ecosystem page, not a controlled success/failure comparison. No dedicated failed-rollout gallery was identified there; this does not establish that none exists elsewhere. | Every displayed HandBack episode should have a method, seed, outcome and evidence identifier; keep downloadable structured results beside the visual. Do not create an unnecessary live server or change our evidence format simply to imitate LeRobot. |
| **OpenVLA** — [GitHub](https://github.com/openvla/openvla), [project page](https://openvla.github.io/) | Short introduction and Paper/Code/Models links; benchmark figures; galleries grouped by robot, task and generalization condition. Text distinguishes zero-shot from fine-tuned policies and labels video playback speed. Comparison rows place different methods on the same named task. | The page explicitly marks outcomes with success, failure and partial-result symbols; it states cases where another method performs better and provides a failed semantic-generalization example. | Show matched-scene comparisons, explicit pass/fail/unknown labels, and the full primary table above examples. Never present a selected V success as proof that V outperforms S1. |
| **ACT / ALOHA** — [ACT GitHub](https://github.com/tonyzhaozh/act), [project page](https://tonyzhaozh.github.io/aloha/) | Hardware and algorithm sections are separated. The page describes real-time rollouts, demonstration count, task conditions, and policy observation views. Reactiveness and robustness sections use galleries. README gives episode visualization, training and evaluation commands; evaluation saves rollout videos. | Galleries explicitly include “Open Cup (failure)” and “Slot Battery (failure).” The observation section distinguishes what the policy sees from external demonstrations. | Separate native policy images from any derived diagnostic render; label external contact diagnostics as offline evidence. Pair successes with a failure rather than showing only attractive examples. |
| **Diffusion Policy** — [GitHub](https://github.com/real-stanford/diffusion_policy), [project page](https://diffusion-policy.cs.columbia.edu/) | The page uses a compact overview, mechanism figures, task-specific sections, comparisons, and a full-results link. Push-T shows aggregate end states and example rollout episodes as different layers. README documents data/config downloads, single-seed runs, logs, checkpoints, media and evaluation. | Push-T captions name baseline failure modes, including getting stuck and prematurely entering the end-zone; timed disturbance captions are given separately. | Display an aggregate result chart and all run-level outcomes before a few visual examples. Keep “task passed but contact screen failed” distinct from ordinary task failure. Provide generated-table commands rather than a screenshot-only result. |
| **robomimic** — [GitHub](https://github.com/ARISE-Initiative/robomimic), [homepage](https://robomimic.github.io/), [study page](https://robomimic.github.io/study/) | Homepage is a short gateway to code/docs/paper/study. The study page proceeds from challenges to tasks, reset distributions, dataset quality, algorithm/observation design, and lessons, with figures and galleries. README links benchmark/data reproduction and setup. | The study page explicitly discusses offline RL struggling on human data, paired success/failure data, and training/evaluation mismatch. It does not only advertise a winning policy. | Strongest structural model for our exploratory report: question → frozen design → observed results → mechanism audit → limits. Include reset/initial-state matching and the S1/V identical-treatment finding beside performance. |

## Directly verified media structure

The independent HTML probe `probe_showcase_html.py` generated `robotics_showcase_media_probe.json`. Counts include repeated page elements and do not measure unique experiments or verified playback. The script downloaded only HTML; it did not retrieve the media URLs.

| Inspected page | `<video>` elements | `<iframe>` elements | `<img>` elements | Scope limitation |
|---|---:|---:|---:|---|
| LeRobot Hub organization page | 0 | 0 | 55 | Includes avatars and other UI images; its separate viewer Space uses an iframe. |
| OpenVLA project | 51 | 0 | 7 | Captions and source elements inspected; videos not watched. |
| ACT / ALOHA project | 19 | 0 | 1 | Failure-gallery captions inspected; videos not watched. |
| Diffusion Policy project | 26 | 0 | 21 | Results and failure captions inspected; videos not watched. |
| robomimic study | 53 | 1 | 19 | Includes dataset/task/example videos; not 53 independent evaluations. |

## Recommended HandBack page: one page, evidence first

1. **Title and finding.** “A bounded feasibility study of learning-value-based control return.” Immediately state that the implementation did not meet the expansion gate and that V/S1 made identical choices on six parents. Link Code, Report, Results, Recompute.
2. **The aggregate result.** Seven-method count chart and table with a shared denominator of 12, retaining raw task success, completion+holding, joint contact-screened success, and >5 mm contact. Explain the 2 mm engineering screen and three retries in plain sight.
3. **Matched-scene viewer.** A method/seed selector or a small grid of the same scene under V, S1 and replay-only B; each card shows the native final image, task/hold/contact status, and maximum logged contact depth. Link the corresponding run-level record. Missing or occluded views remain labelled unknown visually, even if the independent task predicate is available.
4. **What changed—and did not.** A six-parent prefix-choice matrix makes V=S1 visible. Do not label a numerical-weight difference as a learned selection effect.
5. **Failure gallery.** A small, disclosed selection covering: object left outside basket; task success with deep robot contact; gripper-occluded end view; infrastructure-interrupted attempt. These are case illustrations, not an unbiased success-rate estimate.
6. **Robustness and reproducibility.** Original-attempt bounds, logical-unit/physical-attempt counts, code/data hashes and CPU recomputation command. Distinguish result recomputation from full simulation/training regeneration. End with scope and links, not speculative future-work claims.

### Media integrity rules

- Prefer original episode videos if they already exist, can be recovered without restarting experiments, and can be redistributed. Add controls, poster, task/method/seed caption, real duration and explicit speed if accelerated; load metadata only by default.
- If only original stills are available, publish an image viewer. Do not turn sampled observations into a purported continuous recording. A slideshow must be labelled “sampled policy observations,” with no implication of continuous motion.
- Mark derived CAD/peak-contact renders as **offline reconstruction**, not native camera evidence. Registration error means those renders must not be shown as exact physical penetration ground truth.
- The main table uses the frozen simulator predicate and contact logs; a visually ambiguous still does not override it or certify release/holding. Show both sources with their different limits.
- Do not visually hide partials or task failures, autoplay a success montage as the primary finding, or use green “validated” badges for this failed feasibility test.
- Webpage captions must not say “safe,” “generalizes,” “reduces API cost,” “significant improvement,” or “new SOTA” on the basis of the current study.
- GitHub Pages can host this static page directly from `docs/`; interactive charts should derive from committed result JSON/CSV. Large authentic videos can be separately versioned if needed, but the short report, key images and structured outcomes should remain inspectable on GitHub.

## Verification boundaries

The repositories, linked webpages, media tags and described text were checked; rendering consistency, video playback, external benchmark correctness, all datasets and current installation success were not. The failed LeRobot `visualizing_datasets` documentation URL was not used as evidence; the official README, organization page and viewer Space supplied the verified entry points. This note recommends presentation structure and does not change HandBack's experimental conclusions.
