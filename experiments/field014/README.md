# MOTIF FIELD-014 — REALITY HAS DEPTH

**Status:** exploratory browser prototype, stacked on FIELD-013. Independent model vision, multi-view reconstruction, and structural engineering are NOT demonstrated.

## Objective

The user noted that reality is unforgivingly three-dimensional. FIELD-010–013 let people and two heuristic reasoning branches inspect a shared 2D sketch, import photo-region material hypotheses and consider alternative uses. But a drawn line can look complete even when a fence panel floats above the ground or crosses another segment at a different elevation. FIELD-014 is a genuine independent 3D *scene representation* (x,y,z coordinates, camera projection, ground-plane ray intersection, 3D mesh face generation and OBJ vertices) and a paired 2D editor. It deliberately does **not** pretend a single photo or informal sketch produces a 3D survey.

## Run

Open the standalone `MOTIF_FIELD014_3D_Lab.html` (included in the ZIP) in a capable browser, or serve `experiments/field014/index.html` and adjacent `experiments/field010/core.js` + `fixture.js` through a local static HTTP server.

```bash
node experiments/field014/test_scene3d.js
```

This browser app is local-only: no network requests, libraries, API calls, telemetry or generated private imagery. The public generic demo begins with an explicitly invented 2D sample from FIELD-010; the private file shared separately with the user embeds their sketch and photographic thumbnails but is NOT committed to this repository.

## How to use

1. **Start from shared evidence:** import a previously exported FIELD-010/011/012/013 JSON board, optionally display the original sketch and separately attached photographs. Never assume a photo pixel is a yard coordinate.
2. **Compare live views:** 2D map and 3D perspective read the exact same source-plus-event state. Drag a movable segment in 2D, or toggle `Move in 3D` to drag it along the ground plane. `Orbit 3D`, `Perspective`, `Top` and wheel zoom manipulate the camera, not observations.
3. **Add depth:** edit height, ground clearance and thickness of a tentative object. Values are illustrative scene units unless independently constrained. A visibly raised bottom creates a named `GROUND_GAP` in the geometry critique; a planar crossing with disjoint vertical spans gets its own flag.
4. **If known:** enter one source-bound real measurement and explicitly assert sketch proportionality with an uncertainty tolerance. Without both, distances remain drawn-only; a real-world metric fit is still unverified. Photo depth or actual camera pose are not inferred.
5. **Inspect parallel outputs:** Branch A detects 3D clearance/crossings, unverified supports and proposes conditional material placements. Branch B nominates measurement/height/support inputs. Neither branch auto-executes physical actions.
6. **Save:** export append-only local event-sourced JSON or illustrative 3D OBJ mesh. Undo adds a `revert` record, preserving history. Images do not travel in JSON exports.

## Data and authority contract

- **Original:** validated FIELD-010 `motif.field010.v1` board, including source-bound marks, user edits, tentative status and photo material records.
- **FIELD-014 events:** `position`, `height`, `clearance`, `thickness`, `calibrate`, `confirm`, `add_support`, `add_barrier`, `remove_support`, and `revert`. All are domain-constrained, finite-number validated and replayed from source.
- **3D scene:** the x/z dimensions are normalized sketch diagram units. The y axis is upright. Each barrier is an extruded rectangular prism with explicit bottom and height; supports are illustrative posts; an access gap has no solid prism.
- **Measurements:** `diagram_only` by default. An independently entered `user_measured` reference and an explicit proportionality assumption can yield *conditional* meters per drawing unit; nonuniform sketch distortion is an assumed bounded range, not a confidence interval. No photo depth is mapped to the scene.
- **Suggestions:** source-linked and tentative; alternate visual placements are ghosts until explicitly changed. A staged photo material stays `PHOTO_MATERIAL_UNREGISTERED`.
- **HOLD:** no tip-load proof, tie/joint certification, permission to move objects, paw/head safety, underflow containment, actual attachment, real photo-to-yard registration, or autonomous real-world test.

## Architecture and open-source options

This first 3D viewer uses **real 3D projective math in dependency-free Canvas 2D**: a pinhole camera, perspective projection, orbit/pitch, ground ray intersection, extruded face mesh and depth sorting. It is not photogrammetry. This keeps the offline prototype usable on older hardware without GL drivers or modern dependencies. A later renderer could use Three.js (MIT), while independent reconstruction experiments can test the open-source **MapAnything** (Apache-2.0) or **Depth Anything 3** (Apache-2.0 repository; verify individual checkpoints) for *tentative* point maps and cameras. Qwen3-VL object candidates can be imported via FIELD-013's existing adapter, and only humans can place an unregistered object on the 3D map.

MapAnything: https://github.com/facebookresearch/map-anything
Depth Anything 3: https://github.com/ByteDance-Seed/Depth-Anything-3
Three.js: https://threejs.org/

## Core non-obvious limitation

A projected 3D prism is meaningful even with completely arbitrary height and scale: it reveals exactly **where** we are making assumptions. It does **not** establish those assumptions are correct. Thus, `GROUND_GAP` is a critique of the *current modeled hypothesis*; it must not be reported as an observed real gap. Same for support points, intersecting shapes, and ghost arrangements.

## Validation

The source-only suite covers 3D projection/ray intersection, crossing-vs-height disagreement, raised ground gaps, validity of measurements and undos, source preservation, unregistered photo material staging, no physical-scale hallucination and safe export metadata. These are authored synthetic cases; neither model perception nor a field installation was independently validated. See `EVALUATION.md`.
