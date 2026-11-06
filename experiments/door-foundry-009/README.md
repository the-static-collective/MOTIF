# MOTIF-009 — THE QUESTION THAT RESOLVES THE PICTURE

**Instead of choosing one convincing image from ambiguous text, retain multiple image worlds and calculate which question would most usefully distinguish them.**

This source-native, fully local experiment builds on [MOTIF #89](https://github.com/the-static-collective/MOTIF/pull/89). It reuses unchanged MOTIF-007's finite ambiguous-text parser, source-generated PNG images and original MOTIF-006 image decoder; MOTIF-008's complete finite reachability; and the original GRAFT-030 source-generated executable reviewed by CANNON-095.

## Four actual PNG hypotheses

Original wording: **“A red crate is beside a blue wall. Move it to the other side.”**

MOTIF-007 preserves left/right as two possible pictures, not as observed facts. MOTIF-008 identified another renderer assumption: **the wall's extent**. We form a 2×2 model family, each represented by a real, byte-hashed, pixel-decoded binary PNG start/goal pair:

| World | Crate side | Wall extent | Native generated-program reachability |
| --- | --- | --- | --- |
| LEFT_PARTIAL | left | short | yes |
| RIGHT_PARTIAL | right | short | yes |
| LEFT_FULL | left | full-height | no |
| RIGHT_FULL | right | full-height | no |

The generated original GRAFT program itself evaluates transitions in all four scenes, under the prior original CANNON source review. **CANNON did not separately review the freshly rendered full-wall image pair; these are marked newly locally validated only.** No true world is selected.

## Ask for decision relevance, not abstract curiosity

The example cost function is entirely **hypothetical**, declared by the experimenter and not calibrated to anyone's real life. Prior weights for the four worlds are **1,1,4,4** (20% partial wall, 80% full wall). Synthetic losses are: wait/hold without action **2**, falsely call a viable route impossible **5**, wrong-direction or blocked route **10**. Question prices are:

- **ASK_START_SIDE**, price 0.1 unit: Is the crate initially LEFT or RIGHT of the wall?
- **ASK_WALL_EXTENT**, price 0.3 unit: Does the wall stretch top to bottom?
- **ASK_EXACT_SCENE**, price 2.1 units: Obtain a complete independent scene description.

`decision.py` searches every stop/action/question branch of a **two-question adaptive decision tree**, including alternative simulated answers and possible stopping after one response. It calculates value of information as *reduction in expected decision loss net of asking cost*, not merely reduction in entropy.

Expected loss in this declared synthetic setup:

| Policy | Expected synthetic loss |
| --- | ---: |
| Best action without asking (prematurely declare unreachable) | 1.00 |
| Best policy with at most one question: **wall extent** | **0.70** |
| Optimal with up to two: **wall extent**, then side only if needed | **0.32** |
| Always abstain / hold | 2.00 |
| Greedy entropy-per-question-cost first, with optimal second | 0.40 |

An entropy-per-query-cost heuristic asks **start side first**, because side supplies 1.00 bit while wall extent supplies ~0.722 bits, and side is cheaper. This is the *wrong* question under the declared decision loss and branching costs. Choosing extent first avoids paying for the side when the full-height wall makes moving impossible in the chosen model.

**Value of asking** compared to the best no-question decision is **0.68 hypothetical loss units**. A separate direct classical exhaustive enumerator reproduces all optimal results. Thus **no superiority over a same-information classical active-learning algorithm is claimed**.

A test where the wall is even more likely to be full, and another where questions are too expensive, correctly choose **not to ask at all**.

## Evidence custody

The workflow replays original GRAFT-030 and CANNON-095 against authentic MOTIF-007 PNG imagery, uses the already-held native generated operator to explore each world, and creates source-byte-addressed artifacts:

- Four distinct binary PNG hypothetical current states and four target images.
- Original MOTIF-006 image-gap receipts for each candidate, checked for pixel/relation validity.
- A complete `active-question.json` including all priors, hypothetical costs, unsent questions, adaptive branches, comparison to an entropy heuristic, and a conventional classical exhaustive-control result.
- `question-for-human.md`: a proposed question explicitly **not sent** to anyone.
- Synthetic oracle traces for all four possible worlds, explicitly labeled as tests, **not actual replies**.

Source and test gates reject mutated original ambiguity receipts, changed PNGs, self-rehashed false authority, invalid prior distributions or costs, and any attempt to overwrite evidence.

No T5 or generative vision model is used. No live photo source, person, API, outside database or physical device is queried. No image is claimed to depict reality; no real reply, scene truth, deployment, repository mutation by the running program, promotion, or actual action occurs.

## Run

Use `.github/workflows/door-foundry-009.yml` for the full independently pinned GRAFT/CANNON/MOTIF source workflow. After original source checkouts and the MOTIF-007/MOTIF-006 evidence have been built, the new questioner runs as:

```sh
python experiments/door-foundry-009/visual_question.py \
  --ambiguous ambiguous-scenes \
  --base text-scenes \
  --imagined imagined-futures \
  --build generated-visual-motif \
  --out evidence/active-question
```

The unit suite runs as:

```sh
python -m unittest discover -s experiments/door-foundry-009 -p 'test_question.py' -v
```

## Next frontier

A real user-controlled question/answer interface could connect this proposal engine to an actual operator, but an unanswered question must never be treated as answered. Future empirical tests should calibrate priors and questioning cost, test unfamiliar scene grammars and compare question quality to matched-budget classical value-of-information methods. T5 could propose broader interpretations but never certify an unobserved world.

**Asked in simulation ≠ asked in reality. A hypothetical answer ≠ evidence. Evidence ≠ authority.**
