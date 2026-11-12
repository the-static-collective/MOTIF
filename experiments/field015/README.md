# MOTIF FIELD-015 — Matter Has Consequences

**Unmerged research experiment**, stacked onto FIELD-014. No pretrained checkpoint, user photos or private yard plan are committed, and no inference or physical field trial has been performed.

## What is executable

- **Two actual optional integration calls** in `reconstruction.py`: MapAnything's `MapAnything.from_pretrained(...).infer(...)` and Depth Anything 3's `DepthAnything3.from_pretrained(...).inference(...)`. The adapters only start after an explicit `--allow-local-inference`, check for a **locally existing checkpoint**, and refuse missing 3D geometry. Each output keeps checkpoint/source SHA-256, model-local points and its own scale state; neither automatically becomes registered site geometry.
- **`physics.py`**: simplified steady crosswind force `F=0.5*rho*v²*Cd*area*solidity`, tipping moment `F*h/2`, gravitational restoring torque `mass*g*footprint/2`, friction and optional linear-elastic member deflection. Actual Cd, mass, material modulus, cross-section, connections, soil, dynamic impacts and ambient wind are unknown until established by other evidence. Outputs explicitly HOLD or hypothetical failure.
- **`truss.py`**: true 2-D linear pin-jointed stiffness-matrix solve. A connected bar network without bracing remains singular, whereas an idealized triangulated network yields a finite displacement solution. It is not 3-D multibody dynamics, elastic-plastic frame FEA, structural approval or zip-tie shear/peel testing.
- **`lab.html`**: standalone offline, editable 2D/3D demo with synthetic default geometry, source sketch/photo upload, fast hypothetical wind/material changes, source-scoped model-witness JSON import, and event-scoped scene/receipt export. The initial dimensions are deliberately *not* taken from user's photographs.
- **`test_field015.py` + CI**: authored physical negative controls and mock model adapter tests. No checkpoint, paid API, location data or photo upload required.

## Reproduce

```sh
python -m pip install 'numpy>=1.26,<3'
cd experiments/field015
python -m unittest -v test_field015.py
python physics.py
python truss.py
# Open lab.html directly in your browser (all scripts embedded).
```

### Optional actual model calls on a capable, trusted machine

Follow official package installation and model checkpoint directions, then download a model locally first. The arguments below are **instructions, not proof that inference has run**:

```sh
python reconstruction.py --engine mapanything --checkpoint /path/to/map-anything-apache \
 --photos /private/a.jpg /private/b.jpg --output /private/map.json \
 --device cuda --allow-local-inference

python reconstruction.py --engine da3 --checkpoint /path/to/DA3-BASE \
 --photos /private/a.jpg /private/b.jpg --output /private/da3.json \
 --device cuda --allow-local-inference
```

MapAnything code is Apache-2.0 but its main pretrained weights are CC-BY-NC; choose the separately released **facebook/map-anything-apache** checkpoint if permissive use is required. Depth Anything 3 code is Apache-2.0; its **DA3-BASE/SMALL** checkpoints are Apache-2.0 but LARGE/GIANT model weights are non-commercial. Consult the current project model cards before deployment.

Official documentation: https://github.com/facebookresearch/map-anything and https://github.com/ByteDance-Seed/Depth-Anything-3

## Why the physical warnings matter

The original fencing puzzle contains salvaged cage panels, privacy fabric, strong zip ties, movable fences, chairs and a trampoline. This experiment **does not** infer rigidity or installed load capacity from an advertised 200-lb tie rating. A pair of connected panels can still topple together; a chair or trampoline is not automatically a verified structural anchor. Open mesh changes assumed wind area but introduces independent dog entrapment/edge hazards. A false sense of security near vehicle traffic is not an acceptable outcome.

**Illustrative 8 m/s scenario, not observed weather:** a 1.5 m × 1 m solid 5 kg panel with 0.35 m assumed base footprint, Cd 1.4 and friction coefficient .6 develops about 82 N lateral force and fails this simplified tipping model. An otherwise identical hypothetical mesh with solidity .2 develops about 16 N, but remains **HOLD**, not approved, because real material, anchors, connections and gust loading are unresolved.

## Next falsification

Use a **consented, physically measured, unrelated tabletop scene** with at least two overlapping photographs and independent measurements. Run MapAnything and DA3 as separate tentative witnesses, check point/cloud correspondence before registration, then test proposed material assemblies against known impossible or unstable controls. Compare single-model, two-model, geometry-only and physical-critique conditions, counting false confidence, actual fit, human corrections and time saved. Evaluate optional MuJoCo (Apache-2.0) or Project Chrono (BSD-3) only after geometry and physical property inputs are credible; **neither is executed by this PR**.

**Provenance boundary:** model prediction ≠ observed material property ≠ verified design ≠ physical construction authority. Never treat this experiment as certified dog containment.
