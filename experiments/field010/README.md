# MOTIF FIELD-010 — SHARED BOARD / PARALLEL REASONING

**Research-only prototype, stacked on unmerged FIELD-009.** Two independent decision branches run over a single append-only, user-correctable visual state. No real-world perception, autonomous construction, hardware actuation or physical safety certification.

## Try the board

**Browser demo:** Open `index.html` from a local HTTP server or as a local HTML file together with `core.js`, `fixture.js`, `app.js`. No external packages, CDNs or network calls are performed by the application itself.

```sh
python -m http.server 8765
# then open http://127.0.0.1:8765/index.html
```

- Upload a sketch to replace the **invented demo** and preserve the source pixels.
- Choose `+ Desired boundary`, then tap two endpoints on the original image. Use `Select / move` to drag whole items or reshape white endpoint handles.
- Select a line: label it, toggle movable/fixed, confirm or reject geometry, and record an optional measurement as rough guess or human-measured.
- Toggle an explicitly assumed sketch-proportionality tolerance to obtain rough, non-certified inferred length ranges from a human-entered known reference.
- Add supports and panels; use on-demand context actions from Branch B. Branch A re-examines hypothetical material reuse and drawing ratios after each change.
- Undo appends a compensating ledger entry. Export/import board JSON (without image bytes), or export an annotated SVG **which can contain personal sketch pixels**.

### Private version
A separate `.html` artifact may embed a human's uploaded sketch and photo thumbnails. That file is *private*, never committed to this repository; do not share it without the person's permission. The public demo contains only invented geometry and no personally identifying source assets.

## Code

- `workbench.py` — standard-library event reducer + two deterministic branch evaluators, digest.
- `bridge009.py` — real import of existing FIELD-009 geometry, source-scoped HOLD behavior.
- `core.js` — browser projections and worker-safe reasoning functions.
- `app.js`, `index.html`, `fixture.js` — private-local, responsive editable SVG interface.
- `test_workbench.py`, `test_core.js`, `test_bridge009.py` — regression suites.
- `ARCHITECTURE.md` — dataflow, event contracts, privacy, limitations and future widget grammar.
- `EVALUATION.md` — independently annotated evaluation plan and falsifiers.

```sh
python -m unittest discover -v
node test_core.js
```

## Nonclaims

The demo *does not automatically reconstruct geometry from newly uploaded photos*. The human currently draws or corrects geometry on top of the sketch; a future opt-in local vision proposal may seed the editable layer using FIELD-006/007/008. Labels may be candidate guesses. New drawings remain hypotheses; drag events are not observed physical movement. No plan should be treated as a substitute for checking sharp mesh, unstable supports, traffic exposure, entanglement, anchoring or secure animal containment.
