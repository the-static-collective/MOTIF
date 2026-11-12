# MOTIF FIELD‑016 — REVISION IN MATTER

**Research status:** executable authored planner; no deployed vision-model inference, no ground-truthed site reconstruction, no structural safety certification, no observed construction. Stacked on FIELD‑015, whose `physics.screen`, `physics.assembly_screen`, and `reconstruction.report_pair` are **actually imported and executed**, not merely described.

## Scientific question

Can a symbolic visual-physical assistant independently (1) propose alternative configurations of available material, (2) identify an apparent flaw from simplified engineering constraints, (3) revise the configuration, and (4) select a specific measurement that could falsify its leading hypothesis—without inventing permission, measured geometry or material capacities?

## Working implementation

- `engine.py`: bounded combination search (three-piece cap), two route choices, nominal coverage, FIELD‑015 panel wind/tipping/sliding screen, FIELD‑015 **assembly connectivity** inspection, clearance test relative to a *user-declared* threshold, ranked candidates, next input, immutable revisions, and source/evidence receipts. Each proposal emits a **hypothetical local 3D coordinate list**; photographs and sketch coordinates are explicitly *not* registered to that frame.
- `bridge015.py`: imports the **actual** FIELD‑015 MapAnything/Depth Anything 3 reconstruction witness contract and preserves `HOLD` on model-to-model alignment or unverified physical scale. Reconstructed point clouds are never silently used as panel dimensions or world locations.
- `ui.js`: separate offline JS comparison/interaction version. Three hypothesized panel classes, route alternatives, editable dimensions, wind scenario, reversible event history. The UI uses a simplified analytical force equation; not the Python numerical kernel. No network or model inference.
- `index.html`: interactive isometric 3D projection of hypothesis, drag-to-orbit, editable materials and routes, rejection/unknown flags, direct measurement prompts, undo and local JSON export. User edits immediately update the corresponding offline search. **The canvas is an illustrative geometric model, not an image-derived mesh.**
- `test_engine.py`, `test_bridge015.py`, `test_ui.js`: free-body and evidence regression tests, negative cases, source exclusion, 3D gap, and changes due to measured lengths. A dedicated GitHub workflow reruns all offline checks.

### Run from a complete MOTIF checkout

```sh
cd experiments/field016
python -m unittest discover -v
python engine.py  # emits transparent synthetic report
node test_ui.js
```

Python test requires `numpy` because importing FIELD‑015 reconstruction invokes its numerical tools. There are no online network requirements. Open `index.html` from the local folder with `ui.js` alongside, or use the bundled fully inlined offline HTML artifact.

## Observed authored synthetic result

In a deliberately invented yard with two routes (2.4m and 1.5m) and three fictional panels (privacy, cage, porous), the bounded planner initially selects an *unverified* 1.5m porous-panel hypothesis for the shorter relocated route. The common free-body screen estimates 16.46 N wind force under an **illustrative** 8m/s wind case (no local meteorology or field testing). The system HOLDs installation safety, including unknown ground clearance and joints.

When a deliberately simulated independent width measurement changes that porous panel from 1.5m to **1.32m**, it cannot cover the 1.5m route alone. The candidate is removed and the planner recomputes the remaining options. A different option may mathematically cover the span but the simplified physics model can fail it; the planner does not declare a safe installation. A separate case changes clearance to 0.12m against a hypothetical user-specified 0.06m maximum and marks the proposed panel as failing that stated gap criterion.

These fixture values are **not drawn from the user's actual property**. The saved sketches and photos from prior work were not used to derive fabricated material masses, dimensions, wind speed, or support strength.

## Critical safety/epistemic fences

1. **Strong zip ties ≠ structural joint proof.** A package label's 200-lb advertised tensile rating is not installed working capacity, peel, creep, UV/cold response, load sharing, or support stability.
2. **Topology ≠ bracing.** A connected network of panels isn't assumed to be a rigid, stable frame. `assembly_screen` explicitly returns unverified load sharing.
3. **Mesh needs animal hazard review.** Thin netting and large openings can entangle paws, heads or collars, regardless of nominal wind-screen results.
4. **One hand-drawn ratio ≠ 3D survey.** The UI's local x/y/z coordinates are hypothetical; neither MapAnything nor DA3 was run or approved as geometric truth.
5. **Free-body screen ≠ structural engineering analysis.** The model ignores gust factors, design standards, complex connection forces, torsion, soil anchorage, impact, fatigue, and actual materials.
6. **Model H HOLD is not “safe.”** A lower computed wind force does not prove containment, support or fitness for use.
7. No automated physical execution and no public property photos or coordinates committed.

## Falsification path

For unfamiliar independently measured material reconfiguration tasks, freeze the initial evidence and later field outcomes. Compare (a) first-fit baseline, (b) symbolic planner without physics, (c) planner plus physical critic, (d) planner plus critic plus the interactive board. Evaluate number of actually fitting plans, correctly diagnosed failure mechanisms, counterexample adaptation, hazard misses, material efficiency, uncertainty calibration, and human correction time. Optional real MapAnything/DA3 runs require separate local installation and opt-in; compare their recovered geometry only after independent site measurements and auditable coordinate-frame registration. **No such blind physical benchmark has been run yet.**
