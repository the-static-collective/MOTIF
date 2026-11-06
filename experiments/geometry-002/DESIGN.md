# MOTIF-GEOM-002 — The Geometry That Discovers Its Own Rules

**Status:** Finite, deterministic **synthetic development** experiment. Python 3.10+ stdlib only. Candidate hypotheses remain **HOLD** until human review. This is classical lattice fitting, not a newly invented law of nature or evidence that a sacred geometry encodes consciousness.

## Actual question

If MOTIF sees only a list of finite two-dimensional point coordinates, can it infer a repeatable geometric rule **without being given the lattice angle, position, rotation, scale, family, or missing coordinates**? Can it avoid claiming that absent points or random arrangements are established facts?

This builds on [MOTIF-GEOM-001](../geometry-001/DESIGN.md), the exact 19-circle flower-of-life construction. The predecessor assumes an upright, anchored, calibrated triangular lattice. This experiment withholds those parameters, and tests square and oblique constructions as *foreign* geometry rather than labeling every grid a Flower of Life.

## What is and isn't supplied

**Supplied**: a 2D Euclidean coordinate field, with an explicit model prior that the world, if periodic, has a **near-equal-length pair of independent lattice steps**. The synthetic generator adds translation, rotation, a scale unknown to the inference algorithm, position noise, missing points, and unrelated distractors. The algorithm is allowed to use classical computation and a bounded local-search tolerance. It receives no generator family label.

**Not supplied**: the angle (the fit can find ~60°, ~73°, ~90°), lattice origin, basis vectors, circle radius, true missing centers, ground-truth model, true neighbor identities, or outlier identities. Source reliability, coordinate calibration, image segmentation, perspective, non-Euclidean distances and permission to do anything external are **not** supplied or inferred.

## Procedure

1. Estimate the local spacing using the median nearest-observation distance; collect short vectors between witnessed points.
2. For each observed anchor, enumerate independent local basis-vector pairs satisfying the documented **near-equal-step prior** (length ratio 0.78–1.28; minimum normalized area 0.61). Candidate angle is determined from the input—not selected from 60°/90° templates.
3. Snap observed points to integer lattice coordinates, allowing a loose provisional match; independently least-squares refine the affine basis.
4. Perform **strict final inlier selection** (0.125 × estimated unit) and rank by independent observed support, then residual. Reduce equivalent lattice bases using classical two-dimensional Gauss reduction. Reject duplicate observations, degenerate 1D fits, inadequate coverage, or excessive residual. The model has an explicit threshold (**68% coverage, at least 8 observations**).
5. Only after acceptance, label the measured acute basis angle as triangular (~60°, within 5°), square (~90°, within 5°), or oblique (otherwise). These names label finite hypotheses, not universal symmetry proofs.
6. Locate strongly supported missing-center **proposals** with at least four witnessed neighbor positions. Do not promote proposals to observations. Do not extrapolate low-support boundary cells as known continuations.
7. Export reproducible payloads with a SHA-256 **integrity checksum** and explicit `admission: HOLD`. This checksum is **not a signature** and does not authenticate any source. Render observed circles and inferred circles with different marks.

## Frozen synthetic development benchmark (not external, blind, or preregistered)

Run `python benchmark.py` and `python -m unittest -v test_discovery.py` from this directory. Seeds and generator are committed in `benchmark.py` so results are reproducible and falsifiable. **The fixtures were developed alongside the method**, so these figures should not be interpreted as unbiased real-world accuracy.

- 36 known synthetic geometries (12 each triangular, square, 73° oblique), with 3 masked centers, two distractors and light jitter per world.
- 24 synthetic nonlattice controls: uniform random points, nearly collinear observations and noisy nonperiodic rings.
- Compare exactly the same candidate enumeration with and without least-squares refinement; report coverage and normalized residual without claiming an independent state-of-the-art baseline.
- The 4-neighbor hole rule is intentionally conservative. It can infer supported inner holes but generally **will not invent low-support boundary holes**.
- Monitor false geometry acceptance, wrong-family classification, extra missing-center hypotheses, refusal rates, and premature transfer into observed state.

**Observed development run (locally executed):** 36/36 models proposed, 36/36 geometric family labels correct, **60/108 masked centers recovered**, 0 extra hole proposals, and 24/24 nonlattice cases held. These are **not** generalization rates; performance on previously unseen, different missingness, higher noise and adversarial patterns is untested. Least-squares refinement lowers reconstruction residual but does not change acceptance in these particular fixtures; the algorithm is classical.

## Evidence and restraints

- `discover.py`: finite local candidate enumeration, least-squares affine fitting, 2D basis reduction, conservative missing-cell support and HOLD.
- `cartridge.py`: canonical JSON evidence with re-execution; no external authority.
- `test_discovery.py`: 10 executable tests including foreign angles, corrupt payload, rotation/translation/scale variation, and random/degenerate refusals.
- `benchmark.py`: generated fixed development results, including the misses and negative controls; no carefully selected anecdote in place of the complete table.
- `demo.py`: one standalone masked-circle discovery, `flower-discovery.svg`, `experiment-results.json` and `example-discovery-cartridge.json` (generated locally or by CI).

## Next falsifier (not claimed)

Freeze independent holdout distributions **before modifying the method**. Compare to robust RANSAC, lattice Hough, Fourier/spectral and classical crystallographic lattice fitters under matched runtime and observations. Add adversarial aliasing, overlapping lattices, unknown viewing perspective, variable circle sizes and non-Euclidean noise. Measure false confidence and error severity, not just pattern completion. Only then consider an explicit, reviewed crossing into MOTIF reason cartridges or MOTIF's other experimental branches.
