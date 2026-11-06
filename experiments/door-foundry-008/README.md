# MOTIF-008 — THREE WITNESSES: WORDS, PICTURES, AND LOGIC

A bounded bidirectional critic for MOTIF's existing text/image synthesis. It explicitly tests **where source text, a hypothesized PNG scene, and the source-generated visual planner disagree**.

**The central rule:** An image created from a text prompt is not evidence that the imagined scene exists. Its *metric geometry* is a modeled assumption. A freshly supplied explicit textual constraint must not be silently overwritten by the visual planner's attractive, valid-looking animation.

## Four source-native experiments

**1. TEXT VETOES IMAGE:** Original instruction + “Keep the crate on the same row throughout.” Existing **GRAFT-generated visual program** produces a legitimate 11-step picture detour around a finite blue wall, but this detour goes up/down and therefore violates the source text. The critic then runs a **complete finite reachable-state closure** using only horizontal transformations **through the genuine source-generated program**. No horizontal-only path exists. State `TEXT_VETOES_VISUAL_PLAN`; it refuses to present the pretty animation as a solution.

**2. IMAGE CHALLENGES WORDS:** Original instruction + “The wall makes the destination unreachable.” The original source-owned generated visual code produced twelve actual PNG frames that reach the goal while preserving the stationary obstacle layer. The critic *independently rereads each PNG*, reconstructs its moves and checks the source review and receipt. This constitutes a **counterexample to the added claim within the chosen modeled geometry**, not proof about a physical wall. State `IMAGE_COUNTEREXAMPLE_UNDER_ASSUMED_GEOMETRY`.

**3. TEXT REVISES IMAGE:** Original instruction + “The blue wall stretches from top to bottom.” The original text-to-image renderer had **assumed** a short wall with room around it. The new direct statement overrides that assumed height. The critic generates a **new actual PNG start/goal pair** with a full-height blue barrier and uses the original GRAFT-generated program to explore every reachable state. Under the revised model the goal is unreachable. State `TEXT_OVERRIDES_UNGROUNDED_PICTURE_ASSUMPTION`. The revision's images are **locally verified, not separately CANNON-reviewed as new source images**; source-code identity remains the original GRAFT/CANNON experiment.

**4. AGREEMENT CONTROL:** Original instruction + “Do not move through the blue wall.” The images contain a path respecting the wall; the source-generated and classical pixel tests agree. State `TEXT_IMAGE_LOGIC_AGREE`.

These are two directions of useful correction, one model repair, and one positive control. No rule is promoted automatically.

## Architecture

```text
SOURCE TEXT + EXPLICIT CLAUSE
  | (classical finite grammar; no model guess)
  v
TEXT-007 typed relational SceneIR + assumptions
  |
  v
MOTIF-006 original binary PNG image-in
  |
  v
GRAFT-030 original generated visual JS  <- CANNON-095 independent original review
  |
  v
IMAGINED FUTURE PNGs (not observed)
  |
  v
MOTIF-007 image-reading and coordinate reconstruction
  |                    |
  |              source text constraint/claim
  v                    v
   MOTIF-008 THREE-WITNESS CROSS EXAMINATION
    TEXT / IMAGE / COMPLETE CLASSICAL GRAPH CLOSURE
  |
  +-- HOLD unsupported / ambiguous words
  +-- REJECT invalid apparent visual solution
  +-- COUNTEREXAMPLE to a claim, conditional on model assumptions
  +-- REGENERATE image under newly stated geometry
  +-- AGREEMENT where representations actually coincide
```

### Why no T5 yet?

The parser and graph critic are cheap, deterministic, zero-cost, source-verifiable, and have good negative controls. T5 might *propose* candidate interpretations of more natural text in a later experiment. It should not be granted a privileged voice; every candidate must pass source-text entailment, typed evidence, image reinterpretation and classical reachability, and it must demonstrably improve coverage versus a comparable deterministic parser. **No T5 is used in this experiment.**

### Safety and epistemic limits

- This is **one very narrow grammar**: an existing red crate/blue wall instruction plus one of four exact constraint/claim suffixes. Arbitrary natural language is refused rather than guessed.
- The *source* and initial images are the original MOTIF-007 synthetic 9×8 pixel models. No semantic understanding of real photos or people.
- Complete unreachability is proven only for tiny finite model states under one specific finite action grammar and source-checked GRAFT visual program, never for reality.
- A pixel counterexample can disprove a universal path claim **inside the chosen picture**, but the original renderer's unobserved wall height prevents concluding anything about a physical destination.
- Original CANNON review verifies program source and earlier independent synthetic tests; it does **not sign newly rendered images**, authenticate witnesses, or authorize external work.
- A same-information classical raster-translation planner already matches the visual moves; no speed, intelligence, or generality advantage is claimed.
- PNG images are local and synthetic. No real-world actions, external network requests, API access, human contact, production installs, automatic merges or canon promotion occur.
- Original previous PRs retain their unmerged custody; new branch is stacked on **MOTIF #86**.

## Reproduction

The original `.github/workflows/door-foundry-008.yml` checks out exact **GRAFT-030 / CANNON-095 / MOTIF-006 source** commits, runs MOTIF-007 classical text parsing, GRAFT source-owning generation and CANNON verification on actual images, runs original MOTIF-006 imagination and MOTIF-007 frame-derived narration, and then performs all four cross-examination experiments. It runs adversarial tests against altered PNGs, forged claims, unsafe language, source tampering and authority and publishes an evidence artifact containing all original and revised PNGs and the four human-readable witness reports.

A useful next experiment is to automatically vary scene geometry under an unresolved text clause, preserve **multiple alternative world models**, and ask which new **observation** would most efficiently distinguish them, comparing the question-selection budget to classical active-learning baselines. Only then consider a small T5 proposing additional textual scene candidates; do not let a model silently manufacture facts.
