# MOTIF FIELD-018 — THE CHAIN UNDER TEST

**Research-only / stacked on FIELD-017.** This experiment attempts the complete visual-to-physical-revision chain, reports exactly which stages actually executed, and treats failed integration prerequisites as measurable results rather than fabricating successful reconstruction.

## User's original intent

Give MOTIF the sketch and nine yard photographs, and have it: parse the ink and objects → build tentative 3D → propose alternate fence arrangements using spare materials → screen physics → revise a bad plan → expose the highest-value direct visual/measurement input. The autonomous system must not require the user to verbalize practical ingenuity each time.

## Actual outcome of this run

- REAL-source pass: **4 detached dashed-stroke groups** found using the predecessor FIELD-007 OpenCV detector on the user's rotated notebook image; actual image-source SHA-256 receipts recorded. These groups' meaning is **unverified**.
- REAL-source pass: **9 photos / 36 image-pair ORB+RANSAC tests**; all 36 HOLD rather than inventing shared 3D/yard coordinates.
- REAL-source semantic model: **NONE executed**. There is no installed Qwen3-VL semantic model and neither MapAnything nor Depth Anything 3 checkpoint was available in this local environment. The initial materials, if supplied as words, remain **USER_STATEMENT** rather than model-found photo objects.
- REAL-source 3D/physics: **HOLD**. No yard metric scale, panel sizes, verified camera poses or connectors. A schematic height or advertised 200-lb zip tie claim cannot become load capacity.
- CONTROLLED authored synthetic pass: **actual FIELD-017 search calls FIELD-016 evaluator, which calls FIELD-015 physics**. At budget 16, the nominal best-scored arrangement changes after a hypothetical porous panel width changes from 1.50 to 1.32 m. **The new best-scored candidate also FAILS the simplified physics screen; all evaluated alternatives are rejected.** FIELD-018 therefore adds a fail-closed \`selection_gate\`: the numerical winner is never offered as an operational recommendation. No actual object is moved or verified. The `MODEL_TENTATIVE` event **does not** become a measured fact.

These are **two separately reported runs**, not a claimed end-to-end successful fully autonomous real task. Their only shared semantics are the general problem type and architecture.

## Run locally

Python 3.11+, `numpy` and `opencv-python-headless`. From repo root:

```bash
pip install -r experiments/field018/requirements.txt
python experiments/field018/demo.py --out /tmp/public-synthetic-receipt.json
python -m unittest discover -s experiments/field018 -v
# PRIVATE: images are read only from local paths. No uploading, remote model or network requests.
python experiments/field018/demo.py --sketch /private/sketch.png \
  --photo /private/1.jpg --photo /private/2.jpg \
  --hint 'cage panel' --hint 'privacy screen' \
  --out /private/field018-real-receipt.json
```

Paths and private property images are never committed. Source code is public. Private reports may contain normalized sketch coordinates and photo hashes, and must be handled as private.

## Gate discipline

- **Source art / source pixels**: cryptographic hash and local OpenCV-derived marks only.
- **Photo-to-object semantics**: no model detector ran; never conflate class guesses with labels.
- **3D reconstruction**: verified correspondence, physically meaningful unit scale, and model uncertainty required before any site geometry claim.
- **Mechanical physics**: only if entered material assumptions are explicitly marked; free-body screening is not joint dynamics, gust response or certification.
- **Search**: only recombine existing candidate pieces/routes. Never invent dimensions, stronger fasteners, new permission or more favorable weather.
- **Next move**: confirm intended dashed line on the shared board and/or mark one real object and one independently measured dimension. That is a decision-useful interaction, not an instruction to use unsafe fencing.

## Reusable result

A real source did *not* pass the complete autonomy chain; it was stopped honestly at semantic interpretation and metric reconstruction. The synthetic mechanics→revision portion executes, but the follow-up exposed a critical distinction between *finding the least-bad scored layout* and *finding any viable layout*. FIELD-018 now reports `HOLD_NO_MODEL_ADMISSIBLE_LAYOUT` when the latter is absent. **The next work should prioritize actual local semantic visual inference and source registration**, not another layer of more intricate search on invented coordinates. Compare a real Qwen3-VL interpreter, CV-only, VLM-only, and VLM+critic on withheld images; require independent measured ground-truth and safety review. MapAnything and Depth Anything 3 are optional model adapters; no inference or CPU download happened here.

## Context

Stack predecessor draft PRs 284→285→288→290→293→295→299→304→307→309→310→312→313→315. Avoid direct merge of a stacked branch to `main` without reconciling dependencies. This experiment does not include or publish the user photos.
