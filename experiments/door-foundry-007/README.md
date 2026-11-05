# MOTIF-007 — THE PICTURE-THOUGHT BRIDGE

This is the first **text → internal picture → generated visual transitions → checked text** research crossing.

**Problem:** ordinary text can describe spatial relations. A planner that reasons only with words can miss a collision or spatial impossibility; a visual workbench lets a model externalize a candidate arrangement and subject it to geometric tests. Crucially, the resulting "picture" is **an assumed, synthetic model** of the text, not a witnessed scene.

## What works now

1. **Constrained English in.** `text_to_visual.py` recognizes two explicitly documented sentence forms describing one red block/crate/square relative to one blue wall/barrier, including left↔right and above↔below. It does not generalize to open-ended speech. Unknown objects, extra clauses, changed physics, negation and contradictory directions are refused.
2. **A typed relational scene.** The parser preserves relationships and marks its fixed-size grid, wall length, block dimensions and chosen coordinates as **assumptions not given by the text**.
3. **Actual pictures.** The scene is rendered as binary PNG current and goal images using **original MOTIF-006** source. A *separate pixel decoding and geometry routine* rereads the PNGs and verifies that they express the original text's spatial relations.
4. **Original source owners.** The actual image pair goes to **original CANNON-095**, which calls **original GRAFT-030** to independently verify newly compiled visual rewrite code and withheld synthetic cases. The existing MOTIF-006 builder reassembles a held, runnable, local generated-program planner using those very PNGs, NOT a receipt from another image.
5. **Imagined future pictures.** Existing MOTIF-006 code searches candidate states and writes every hypothetical future as a real PNG and a storyboard. It controls collisions, object conservation and the stationary obstacle layer.
6. **Grounded language back out.** `narrate.py` re-reads **actual PNG outputs**, reconstructs the block's grid coordinates and motion between frames, checks them against the visual receipt and source text, and then writes a detailed human-readable **picture-reasoning.md** with before/after ASCII images and a direction-by-direction explanation. It refuses mismatches.
7. **Ambiguity as alternatives.** “A red crate is beside a blue wall. Move it to the other side.” produces **two separate hypothetical image worlds**, not a silently selected interpretation. No actual GRAFT work is authorized for an unresolved interpretation. An explicit `--choose left|right` can select one, and the choice is recorded.

## Fast usage

```sh
python experiments/door-foundry-007/text_to_visual.py \
  --text "A red crate starts left of a blue wall. Move it to the right of the wall." \
  --out text-scenes
```

That command works locally with Python standard library and the inherited original MOTIF-006 `visual_in.py`; it outputs a text interpretation receipt and actual images under `text-scenes/H01/`.

You can also ask for a deliberately ambiguous visual thought:

```sh
python experiments/door-foundry-007/text_to_visual.py \
  --text "A red crate is beside a blue wall. Move it to the other side." \
  --out alternative-scenes
```

This gives two source-labeled PNG hypotheses and an unresolved question, rather than false certainty.

The full original GRAFT/CANNON source-checking + multi-step picture generation + independent text narration is in the GitHub Actions workflow. Its downloadable artifact contains original text scene specifications, actual start/goal PNGs, generated program, counterfactual image choices, full storyboard and grounded narrative.

## Why T5 is optional, not fundamental

The **deterministic grammar is the reference model**, and it is cheap, inspectable, offline, testable and free. A small T5 text-to-text model could later serve as a *proposer of structured SceneIR candidates* for messy sentences, not as an authority on scene truth or the source of all geometry. Any T5 proposal would need a stricter validation gate than mere JSON parsing: literal text grounding, typed scene contracts, competing hypotheses, independent visual roundtrip, refusal of contradictions, and a test set where it outperforms an equally budgeted classical parser. No T5 model is connected or invoked here.

## Honest limits

- **Text understanding:** two deliberately narrow English templates, a few synonyms, one rigid object and one obstacle.
- **Visual understanding:** original 3-color, tiny-grid RGB PNGs; not photographs, image semantics, visual perception of humans, or neural imagination.
- **Geometry:** synthetic assumptions, not truths inferred from prose.
- **Reasoning:** search over model states, not subjective visualization or evidence of consciousness.
- **Generalization:** not yet tested beyond this grammar.
- **Classical baseline:** same-information classical pixel-shift planning matches the generated GRAFT visual operator's minimum-step result. **No superiority claim.**
- **Security and custody:** original code hashes and independent source-owner receipts are content proofs, not real operator consent. No network, production deployment, authorized human action, automatic merge or model-training use.

## The next real test

Give MOTIF ordinary **unstructured text or a moderately sized arbitrary image**, let both produce uncertain, separately labeled hypotheses for the *same scene*, and compare downstream planning agreement against gold-pixel fixtures and an equally resourced classical parsing/vision baseline. A T5 node becomes justified if it measurably resolves ambiguity without introducing undocumented visual facts.

**Imagining a picture is not observing one. Turning text into imagery is valuable only when the new geometry creates additional falsifiable checks.**
