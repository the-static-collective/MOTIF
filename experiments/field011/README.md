# FIELD-011 — Automatic first draft, human-editable correction

**Research draft, stacked on FIELD-010.** The aim is a photo/sketch → inspectable initial board → human direct correction → two parallel reasoning branches path with fewer clarification turns.

## Source-grounded offline path (implemented in this branch)

`autodraft.py` imports the **actual** FIELD-007 `ink.py`, analyzes a local sketch, and exports tentative, directly editable FIELD-010 objects. It provides the line positions; the person does not need to type coordinates or describe each ink mark in words.

```sh
python -m pip install -r experiments/field007/requirements.txt
python experiments/field011/autodraft.py --sketch /private/sketch.png --out /private/board.json
```

Open the existing FIELD-010 workbench. Import `board.json`, then select the **same source image** as its background. Individual machine-generated fragments can be dragged, reshaped, confirmed, rejected, removed or measured. A separate `board.draft.json` is emitted with the source hash and uncertainty. No source photograph is ever committed or uploaded by this program.

## Independently tested local browser augmentation (conversation package)

The associated downloadable FIELD-011 package also includes a standalone HTML with:
- no-install browser-only sketch pixel auto-drafting after image upload,
- imported OpenCV proposal review cards and one-click confirm/reject,
- original sketch preserved under the editable candidate lines,
- a live FIELD-010 dual-branch solver / interface clarification surface,
- source replacement protection and optional physical-length/ratio fields.

The browser-only detector is less selective than the local Python detector and may mistake handwriting for broken lines; these must stay tentative. The private workbench containing the original user's property images is intentionally **not** in GitHub.

## Research limits

- A detected dashed mark is **not** a verified statement of intended geometry. Joining short ink marks into a segment is hypothetical.
- In the private user sketch, local FIELD-007 detected four tentative ink groups. Neither their physical lengths nor a complete desired perimeter was recovered.
- No real vision-language model inference, automatic interpretation of arbitrary photographs, photo-to-yard registration, dog containment trial, structural load testing, independent generalization or autonomous physical construction has been demonstrated.
- The existing FIELD-010 browser branches are deterministic, author-programmed logic triggered by board events, not a background model or learned neural thought process.
- No surveyed geometry can be inferred from one uncalibrated sketch or an unrectified perspective photo.

## Reproduce

```sh
cd experiments/field011
python -m unittest discover -v
```

See `EVALUATION.md` for matched baselines and honest falsification criteria.
