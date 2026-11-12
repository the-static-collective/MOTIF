# FIELD-018 evaluation / falsification plan

### Two separate result lanes (never merge their claims)
- **Actual private sources**: photo count, source hashes, genuine source-pixel stroke matches, cross-view photo correspondence; any failure to establish meaning or physical measurement must HOLD. A real source cannot inherit physical measurements from a synthetic test fixture.
- **Independent synthetic control**: force a revision after a known wrong size or wind/clearance violation; inspect FIELD-015's actual numeric screen and FIELD-017's evaluated count. A successful synthetic revision is not proof of general capability.

### Intended blind follow-up
Freeze independently annotated new sketches/photos and physically measured object dimensions *before* model inference. For each unseen case, run CV only, open-weights VLM only, VLM+geometric critic, VLM+critic+3D/physics, and direct human assessment under matched cost budgets. Evaluate semantic object precision/recall, reliable cross-view scale, containment-relevant hazard misses, candidate usefulness, number of corrections, and wall-clock plus compute. Use wrong-scale, decorative dashed lines, reflections, repeating chain link, and false boxes as adversarial controls. Strong baseline: conventional VLM plus ordinary search using identical extracted facts. No claims of superior planning from a preprogrammed scene.

### Primary falsifiers
1. 3D has exact metric lengths with no independent scale: **FAIL**.
2. Vision-only label treated as independently measured material property: **FAIL**.
3. Synthetic measurement silently displayed as a user measurement: **FAIL**.
4. 200-lb advertised tie rating treated as verified installed support: **FAIL**.
5. A layout found after fewer than the allowed counted actual physics screens: **FAIL**.
6. No independent validation of modeled dog safety yet reports a safe enclosure: **FAIL**.
7. A new private photo/sketch placed in a public GitHub commit: **FAIL**.

### Real demonstrated bottleneck
The current local environment has no usable model checkpoint and no GPU. Source pixel inference runs; photo object interpretation and metric photogrammetry do not. The experiment is a diagnostic integration test with genuine partial output, not a live all-stage VLM demonstration.

8. After a measurement makes every candidate fail, a least-bad scored candidate is displayed as an approved physical plan: **FAIL**. FIELD-018 adds a separate fail-closed selection gate.
