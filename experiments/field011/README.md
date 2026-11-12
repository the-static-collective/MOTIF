# MOTIF FIELD-011 — FIRST DRAFT WITHOUT A CONVERSATION

**Research draft, stacked on FIELD-010.** A source sketch can now generate tentative, **directly manipulable** line proposals on the shared browser board. Two existing FIELD-010 reasoning branches re-evaluate that board as candidates are confirmed, rejected, moved or measured. The user need not supply the initial line vertices or translate a visual correction into chat.

## The implemented crossing

```text
User gives sketch image (original is preserved and displayed)
     │
     ├── Browser-only zero-install short dark-stroke detector (heuristic)
     │      OR
     └── More conservative local Python FIELD-007/OpenCV extractor (source-backed)
                     ↓
     FIELD-011 draft envelope: source digest, original pixel coordinates,
     aspect-correct SVG coordinates, tentative editable items, uncertainty
                     ↓
       Strong schema checks + image digest binding + no overwrite
                     ↓
        append-only machine proposal events (NOT user-asserted facts)
                     ↓
       FIELD-010 board — direct drag / confirm / reject / trace / measure
                     ↓
             parallel A solver / B clarification branch
```

The original photo/sketch is **not** replaced by the generated lines. Photos remain a separate reference gallery, never mapped automatically onto the sketch. Every proposed stroke has its original image coordinates and the source image SHA-256 digest. The hash is a local consistency receipt, **not source authentication**.

### What can actually run now

- `draft.js` is dependency-free and works in an ordinary offline browser. It detects some short, dark, collinear stroke clusters **from uploaded image pixels**. It may over-detect handwriting or miss angled/fragmented ink. Each hit is labeled *possible*, not accepted as the intended boundary.
- `autodraft.py` uses the actual `experiments/field007/ink.py` (OpenCV) instead of fabricating detection results. It returns a portable proposed-edit packet, suitable for `Import local vision draft`. The operator supplies only the source image and an output location.
- `field010/app.js` and `index.html` gain automatic local draft after sketch upload, optional import of independently generated draft JSON, evidence review cards and one-click confirm/reject. A source replacement **resets the old board after warning**, rather than assigning old positions to a different drawing.
- `sha256Bytes` provides a checked fallback for file/offline browser contexts where Web Crypto is unavailable. It is not an authentication signature.
- An optional adapter validates structured **model-authored dotted-mark proposals** as tentative; no VLM was installed, run, or falsely credited. It does **not** independently validate the model's pixel claims. FIELD-008's independent pixel critic is still needed before treating VLM proposals as pixel-supported.

### Run without installing anything

Open `MOTIF_FIELD011_Upload_Your_Own.html`, upload one sketch, and inspect tentative candidates. Confirm or reject each detected stroke. Drag endpoints, add missing routes, enter measurements or approximate ratios, and save board JSON locally. With zero matching strokes, the detector must abstain; you can draw or import a local Python draft.

The pre-filled **public** HTML example uses an invented sketch; the private workbench (created only in the user's conversation) includes the user's actual sketch and photo thumbnails, and must **not** be committed or publicly distributed.

### Run source-quality local extraction

```sh
python -m pip install -r experiments/field007/requirements.txt
python experiments/field011/autodraft.py \
  --sketch /private/sketch.png \
  --out /private/draft.json
# For a sketch where the *user explicitly stated* dashed marks are the desired route:
python experiments/field011/autodraft.py --sketch /private/sketch.png \
  --out /private/draft.json --user-says-dotted-is-desired
```

Then import `draft.json` using the board's `Import local vision draft` button after loading the **exact same sketch image**. The image SHA-256 digest must match.

### Tests

```sh
cd experiments/field011
python -m unittest discover -v
node test_draft.js
# Parent stack (separately)
cd ../field010
python -m unittest discover -v
node test_core.js
```

The dedicated GitHub workflow uses the existing tracked FIELD-007 and FIELD-010 source. No image upload, private file, external vision inference or network service is needed to run these tests.

## Observed private demonstration (NOT in GitHub)

The existing FIELD-007 extraction proposed **four** tentative dashed-stroke groups from the user's source sketch without manually supplied vertices. The experimental browser-only heuristic proposed **13** groups on the same source: several may be spurious; neither set is a verified complete route. The separate private HTML starts with four OpenCV-derived editable hints and the original sketch beneath, plus nine private reference thumbnails. This is *real source-pixel processing*, **not natural-language comprehension or yard reconstruction**.

A headless Chromium interaction test opened both the standalone public and private HTML via document loading, confirmed one tentative mark, undid that correction, and reran drafting without duplicate insertion. Uploading the actual source into the generic HTML created 13 tentative proposals, and replacing the source reset its prior evidence state rather than contaminating a second sketch.

## Do not claim

- The system knows which original stroke is an intended fence until human review or independent visual interpretation with defensible evidence.
- Clustering disconnected strokes means the drawn route is physically continuous.
- A sketch, a known measurement in another depth plane, or a photo creates reliable yard measurements.
- A photo depicts a safe connection, gate, anchoring, tie rating, animal enclosure or traffic barrier.
- Two code paths constitute autonomous model discovery. They are authored CV/geometry methods.
- The UI persists reasoning while closed or calls a model in the background. It recomputes when browser state changes; Web Workers are only local calculations.

The next hard experiment is a **real local VLM** proposing landmarks and segment labels from held-out unfamiliar drawings and photos, with FIELD-008 pixel critique and the human board as a falsifiable correction surface. See `EVALUATION.md`.
