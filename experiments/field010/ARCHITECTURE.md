# FIELD-010 — The Shared Board Contract

## Intent
A person should be able to provide a drawing or photograph and correct MOTIF's *picture of the problem* by acting on that picture, not having to translate it into language. The system may independently explore useful options while issuing small, optional, context-sensitive interaction requests. Every correction re-enters the same evidence state.

## Topology

```text
original sketch  ───────────────┐          photos (separate witnesses)
       │                        │                      │
FIELD-006 source atlas     FIELD-007/008         future local VLM
       │                 candidate traces               │
       └────────────┬───────────┴───────────────────────┘
                    ↓
          source-scoped editable scene
                    │
     immutable baseline + append-only USER EDITS
                    │
          validated event replay (FIELD-010)
                    │ versioned snapshot
          ┌─────────┴──────────┐
          ▼                    ▼
 A · autonomous solver   B · interface reasoning
 (FIELD-004/009 links)   (needs-driven UI choices)
          │                    │
   hypotheses, ratios     prompts, empty measurement
   conditional length     fields, edit affordances
   safety HOLDs           optional corrections
          └─────────┬──────────┘
                    ▼
             shared visual board
                    │
           user's direct edits
                    │
             append-only events
                    └───────────→ new snapshot
```

### Actual implementation

- `workbench.py`: source-bound Python project validation; append-only event replay; two deterministic read-only branch evaluators; proof-like SHA-256 digest of its **own output**, not proof the source is true.
- `bridge009.py`: imports *actual* previous `experiments/field009/geometry.py` on the stacked MOTIF branch; calibrated sketch estimates remain conditional and reject guessed references. No photo-to-map transformation.
- `core.js`: browser replay and two portable deterministic evaluators. The two computations run in **separate local Web Workers**, with synchronous timers as a fallback; result version numbers prevent stale plans overwriting newer edits.
- `index.html` + `app.js`: SVG board. Upload a sketch locally, draw and drag line segments, edit endpoints precisely, add panels/supports, mark fixed/movable/status, attach a measurement to any line, add approximate ratio assertions, save board JSON, import JSON, export annotated SVG, use optional photographic references. All user edits are local. No external JS, CDN, telemetry or API requests.
- `fixture.js`: invented public scenario only. Real property photos and sketch are never part of the GitHub branch.

### Evidence authority

| Source | Entitlement | Limit |
| --- | --- | --- |
| Uploaded sketch | Original visual evidence | Doesn't prove scale or which marks are intended fencing. |
| Photo | Independent view/witness | Pixel positions cannot be pasted into sketch coordinates without registration. |
| CV/VLM proposal | Candidate claim | Must be source-linked and editable, not silently accepted as user intent. |
| User drag / correction | User-approved digital edit | Doesn't prove the physical piece was moved or that construction works. |
| `user_measured` length | Human-entered reference | Doesn't establish the whole hand sketch is proportional; estimates require separately enabled distortion assumption. |
| `rough_guess` length | Hypothesis | Cannot calibrate physical distances. |
| Model arrangement | Speculative plan | Cannot certify tipping resistance, zip ties, gates or animal welfare. |

### Explicit interaction events

```json
{
  "id":"e-001", "type":"endpoint", "source":"HUMAN_BOARD_EDIT_NOT_PHYSICAL_OBSERVATION",
  "time":"2026-11-11T00:00:00Z", "target":"target-one",
  "index":1, "point":[0.50,0.44]
}
```

`type` can be `add`, `move`, `endpoint`, `set`, `measure`, `ratio`, `proportional`, `remove` or `revert`. All coordinates are in normalized *sketch* space, not latitude/longitude, not photo pixels, not surveyed feet. A `revert` references a prior event and updates the projected state without deleting that event. The uploaded source image is not serialized in JSON automatically.

### Why separate workers?

The architecture deliberately avoids requiring the user to finish a chat answer before the machine can compute. Whenever version `v` changes, both evaluators receive the **same immutable snapshot** and can return separately. Only the current version may update the display. Future routing may replace the current authored heuristics with reviewed MOTIF cartridges or a local multimodal planner, but their proposed widgets must be selected from a bounded, accessibility-tested widget grammar, **not model-generated executable JavaScript**.

### Future extension to actually learned UI generation

`InterfaceProposal = {reasoning_snapshot, capability_needed, suggested_widget_kind, target_evidence, expected_information_value, priority, optional:true}`. `suggested_widget_kind` must be in an audited registry (`trace`, `measure`, `confirm`, `ratio`, `mobility`, `zone`, `compare`, `observe`). The user can ignore it. Information value should eventually be measured by how often the answer actually changes the plan, not inferred solely from a higher prompt score.

### Current boundary

This first implementation is **not** an installed VLM, not automatic image-to-CAD reconstruction, not a learned natural-language-to-widget compiler, and not a live background agent. The browser ships human-authored example geometry, or accepts manual trace edits over an uploaded image. The photo-gallery only displays images; it does not independently interpret them. Workers react to edits, and the Python library can be executed independently.

Integration obligations: preserve the deeper FIELD-009 interval/HOLD mechanics via `bridge009.py`; keep arbitrary speculative arrangements in the hypothetical graph; do not treat connection of cage panels, chairs or trampolines as safe for unsupervised dogs without independent physical checks.
