# MOTIF FIELD-006 — SKETCH IS EVIDENCE

**Question:** Can a general visual-reasoning system preserve what the user actually drew, and incorporate photographs, before reinterpreting the problem? The previous FIELD-005 diagram discarded the paper sketch's layout, labeled landmarks and many salient photo observations in favor of an oversimplified synthetic scene. This experiment fixes the **information-loss problem** before any claim of better artificial visual understanding.

## Implemented

- `atlas.py`: typed evidence-indexed sketch landmarks, user rules, photo claims, and source-coordinate traces. World-scale lengths and photo-camera poses are *not inferred*. Normalized sketch coordinates remain attached only to the source sketch. Original drawn marks remain visible in the atlas.
- `vision_contract.py`: typed, fail-closed validation of *hypothetical local VLM suggestions* for landmarks and handwritten dotted/solid line traces. Model labels cannot silently overwrite the user's marks or assert user intent. Photo bounding boxes cannot transform into property coordinates.
- `benchmark.py`: on an **author-created** abstract fixture, audits source label retention and provenance. Not a blind visual recognition test, a real-world field test, or a matched model evaluation.
- `test_atlas.py` and `test_vision_contract.py`: 37 tests, with adversarial checks against hallucinated coordinate frames, fake evidence provenance, unsafe image embedding, trace promotion and invalid references.
- `private_demo.py`: separate local demonstration using user-owned images (not for public GitHub) — consumes `private_yard_packet.json`, embeds their source sketch and photos in a local evidence board, and emits an explicit annotator-authored receipt. **DO NOT COMMIT these two private files or the generated preview.**

## What the photos and paper actually establish

The hand sketch labels trampoline, garage, backdoor, bus, driveway, neighbor fence and chain-link. The user's correction: dotted marks indicate a desired perimeter; existing solid-line fencing is movable inventory. Photographs show chain-link, a gate and wood slats, rigid small-animal cage panels, rolled fencing, netting, and other materials. They do **not** provide independent measured yard coordinates, structural capacities, or proof of a safe dog enclosure.

One useful source-supported distinction: the paper draws the *desired transformation*, and photos may show *possible material affordances*. A renderer that paints arbitrary boxes into a new map is not preserving that information.

## Run (offline stdlib core)

```
python -m unittest discover -v
python benchmark.py
```

For an opted-in local demonstration with personal images, save the source files locally and pass a reviewed private packet. No photo uploads are necessary. The default renderer embeds no private images.

## Baseline and experiment truth

Current input labels and image associations were authored by an assistant reviewing the supplied images. A score of 7/7 retained named landmarks only shows preservation *after annotation*: it says nothing about a standalone vision model independently detecting them. The preview is not a survey and must not be used to certify construction.

The next falsifiable evaluation should freeze a private set of unfamiliar photos/sketches with independently made annotations. Have a local open-weights VLM propose landmarks, desired/current line classes, cross-view relations and key material affordances, then run the source-registered renderer and critique. Compare with FIELD-005's plain model output, direct VLM Q&A, and human review at the same input/time budget. Measure: source-fact recall, unsupported claims, path/line quality, correct identification of useful transformations, safety errors, and additional user turns required.

In the fencing case, reversible fit tests come after distinguishing the user-drawn route and verifying actual gap lengths, anchoring and hazard controls. A 200-pound advertised tie rating is not equivalent to a stable post or fence assembly.