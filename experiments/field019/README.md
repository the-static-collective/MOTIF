# MOTIF FIELD-019 — THREE-WAY GEOMETRY

**Goal:** fuse (A) approximate top-down 2-D relations from a sketch, (B) perspective image observations, and (C) camera pose/intrinsics hypotheses, while using a real vertical height (here the user reports *most* yard fence panels are about **6 ft tall**) as a metric anchor. The computation must keep camera intrinsics, matching landmarks, perspective, sketch proportionality, and height provenance separate.

## Method

- `fusion.py` is an executable *conditional* factor-graph/bundle model with variable horizontal sketch scale (meters per drawing unit), two or more independent camera poses, marked vertical top/base pairs, shared ground plane, and one shared post-height anchor. It minimizes pixel reprojection residuals by OpenCV `solvePnP` + SciPy nonlinear least squares.
- If the rough sketch disagrees with the images, a **soft, bounded sketch correction proposal** is tested without modifying source evidence. It is held if corrections exceed the declared sketch distortion tolerance.
- A projective picture is not a second freely independent 'ruler': the image contains rays whose geometry depends on camera intrinsics, camera pose, and unknown scene depths. Those must be constrained or solved collectively, not guessed as known.
- Cross-view landmark identity and camera intrinsics must be independently reviewed in this prototype. **Never infer global yard geometry solely from 'six feet tall'.** A small residual is necessary but not sufficient, especially with inaccurate labels or repeated fencing patterns.
- The `synthetic.py` scene generates a metric 3-D arrangement, a perturbed sketch, and two rendered camera observations with independent noise. It performs a *real* numerical inverse solve on that artificial data. Negative controls alter a landmark or leave out calibration.
- `cross_domain_lab.html` is an **offline source-review interface**, not an in-browser 3-D optimizer. Users click common landmarks across sketch/photos and enter two-point post top/base matches. It produces a reviewable candidate JSON packet for the Python solver; it does not claim the solver ran. There is also a private preloaded standalone version of the user's sources held out of the public repository.

## Current trial boundaries

**Synthetic:** Actual numeric camera pose+scale inference runs and can be tested, plus contradictions are rejected.

**Actual user sources:** The notebook is unscaled; the photographs have no independently determined focal intrinsics and no human-reviewed cross-image post correspondences. The six-foot report applies to *most* panels, not necessarily each depicted gate/frame. The real-yard 3-D bundle is correctly **HOLD**. Source processing, not physical reconstruction, is all that has been achieved. The private board enables obtaining the missing relationships by **direct shared drawing** rather than natural-language descriptions.

## Runtime

```bash
pip install -r requirements.txt
python -m unittest discover -v
python synthetic.py
python run.py --sample synthetic
python run.py --sample private-hold
python run.py --input candidate_packet.json
```

`run.py` writes only local analysis JSON. The public synthetic packet contains no user images, addresses, photographs, or private geometry.

## Benchmarks and falsification

Tests must compare sketch-only, photo-only, photo+height, photo+sketch, and photo+sketch+height where calibration is supplied, as well as intentionally incorrect focal values, flipped labels, rough/nonproportional sketches, one-camera controls, repeated chain-link false matches, variable camera geometry, and false height assumptions. Evaluate held-out **physical** spans with ruler measurements, pose uncertainty, reprojection RMS, scale error, correction magnitude, contradiction detection, and unsafe downstream decisions. Synthetic success does **not** establish these real-world performance claims.

## Future open-source inference bridge

- [VGGT](https://github.com/facebookresearch/vggt) predicts tentative camera parameters, depth, point maps and tracks from multiple views. Use its output as *candidate hypotheses*, not certified cameras.
- [MapAnything](https://github.com/facebookresearch/map-anything) can take images together with optional calibration, pose/depth inputs. Use the specifically **Apache-licensed `facebook/map-anything-apache` weights** if commercial rights matter; other available weights are noncommercial.
- [OpenCV calib3d](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html) provides independent projective geometry and pose checks. Pair with SfM/COLMAP if genuine repeated image features are available.

Only a locally checked, source-registered model output may enter the solver, and only with explicit provenance. No cloud transfer, physical construction, automatic animal-containment assurance or inferred truss certification.
