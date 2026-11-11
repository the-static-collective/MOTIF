# MOTIF FIELD-009 — ROUGH RATIOS / ONE REFERENCE

**Status:** proposed research-only experiment stacked on FIELD-008. No direct photo-to-yard map, real physical length, or safe assembly was demonstrated. This project explores how MOTIF can use *dimensionless ratios* when measurements are absent and *conditional* one-reference geometric estimates when one real length is supplied.

## Reasoning stages

1. **Read source traces without filling missing lines.** A hand sketch is evidence of intent and relative layout, not automatically an engineering drawing. FIELD-007 can produce tentative disconnected ink groups. `sketch_adapter.py` compares their *drawn* spans but never asserts these are complete fence runs.
2. **Ratio first.** In a declared plan/rectified plane, compare trace A to trace B. In an unscaled sketch, return a numerical *drawn ratio only*, with no claimed physical ratio. If the user independently asserts approximate proportionality, return a **conditional hypothesis range** specified by an explicit distortion tolerance. That tolerance is not a probability or calibrated physical-error guarantee.
3. **One length plus geometry.** For a metrically scaled drawing or a separately confirmed near-orthographic/rectified plane, a known segment sets scale: `estimated_length ≈ known_length × (target_drawn_length/reference_drawn_length)`. For approximate sketches, propagate broad assumed distortion bounds. Measurement sources and coordinate frames must match. Never silently transfer scales between photos.
4. **Photographic perspective:** One known dimension in an unrectified photo does **not** yield other ground distances at varying depths. `rectify.py` permits a specific additional case: independently reviewed corners of a flat rectangle with one known physical width **and independently known width:height ratio**. A homography maps points on that same plane only. This is conditional, not arbitrary 3-D inference.
5. **What-if → critique.** `planner.py` compares explicitly proposed routes, ranks *drawn* lengths, carries intervals, refuses to declare a physically shortest route when the scale or the intervals are uncertain, and nominates a concrete next measurement that could resolve the choice.
6. **Candidate material count is conditional.** Panel count does not certify a gate, anchor, zip-tie strength, tipping resistance, entanglement clearance, or secure dog confinement.

## Executable studies

Run with Python >=3.11, `numpy` and `opencv-python-headless` for the optional homography/ink adapter:

```bash
pip install -r requirements.txt
python -m unittest discover -v
python demo.py
```

Output from `demo.py` is a **source-free hypothetical**: two different drawn routes, a drawn 40-pixel reference, and an imaginary independently measured 4-foot panel. Without that measurement the solver reports *drawn* ratios of 3.75 and 2.63 with no physical lengths. With the hypothetical 4-foot length and a **human-assumed ±40% sketch proportionality tolerance**, the estimated longer route has an illustrative 7.96–23.96-foot envelope; the shorter route has 5.30–17.61 feet. Their intervals overlap, so the model MUST NOT claim the shorter *drawn* route is demonstrably physically shorter.

These are **author-written synthetic scenes with scripted known inputs**, not autonomous measurement, a blind spatial benchmark, or a valid fence plan.

`sketch_adapter.py` is explicitly optional and source-bound. In private trial against the user's original sketch, FIELD-007 still produced four disconnected tentative ink groups; FIELD-009 computed only spans relative to the longest ink group. **Zero real-world lengths were inferred and no source photos were committed.**

## Required HOLD gates

- Source ID or coordinate plane differs between reference and target.
- The image has uncorrected perspective, unknown depth, or unsupported off-plane objects.
- A supposed known measurement is model-guessed or lacks independent provenance.
- Sketch has no agreed approximate proportionality (ratio may remain `DRAWN_ONLY`).
- Multiple verified references imply contradictory scales.
- A manually assumed shape (e.g. 'square') is presented as an observed physical fact.
- Upper/lower route ranges overlap and the decision hinges on their ranking.

## Falsification program

Freeze independent human-labelled novel sketches, deliberate non-scale drawings, ordinary phone photos with changing depth, known reference widths, and known material limits. Test measured route errors and calibration on held-out physical dimensions, not just whether the model can repeat the formula. Compare ratio-only, anchored, geometric homography, VLM-only and VLM+critic conditions. Require abstention on perspective/occlusion/contradictory anchors, quantify hypothesis false positives, and measure *next measurement usefulness* and downstream work saved.

## Sources / physical geometry limits

Single-view metrology requires stronger geometric assumptions than a single recognizable object: https://www.robots.ox.ac.uk/~lav/Papers/criminisi_etal_ijcv2000/

OpenCV perspective transforms apply to a verified common plane, not arbitrary 3-D objects: https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html

**No actual model inference, animal containment trial, or structural verification took place.**