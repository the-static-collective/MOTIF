# FIELD‑016 evaluation & limits

| Observable | Test / source | What it establishes | What it cannot establish |
| --- | --- | --- | --- |
| Candidate combinations | Python `engine.propose` | Bounded enumeration of ≤3 materials for author-provided spans | Unknown geometry or complete constraint satisfaction |
| First synthetic route | `test_first_uses_relocation...` | Decision changes relative to direct-only route | Real yard layout practicality |
| One changed measurement | `test_measured_width_can_falsify_first` | The leading proposal is invalidated and alternatives reconsidered | Any subsequent proposal is safe |
| Free-body numerical model | Actual FIELD‑015 `physics.screen` | Correct invocation and consistency of the simplified load equations | Dynamic wind/fastener/soil/failure physics |
| Connected panels | Actual FIELD‑015 `assembly_screen` | Connectivity and unverified load sharing are distinct | Structural stability or installed tie capacity |
| Source and 3D model bridge | Actual FIELD‑015 `reconstruction.report_pair` | Model frame agreement cannot silently become surveyed geometry | Real reconstruction quality; both inference engines unexecuted |
| Browser UI | Playwright interaction | Editable material width affects candidate list; 3D sketch renders | Cross-device deployed performance |
| Sketch/privacy | No private user images in public code | Public experiment synthetic only | Any inferred property dimension |

**Benchmark gaps:** no independent blind cases, no human measured physical error, no comparative runtime budget, no object detection model, no observed materials, no measured winds, no real pet use. User-visible claims must remain appropriately restricted. Inputs `width=1.5m`, `mass=5kg`, `wind=8m/s`, `gap=0.06m` are invented demonstration values, not measurements or normative thresholds.
