# MOTIF FIELD-012 — OBJECTS, NOT JUST LINES

**Status:** experimental visual reasoning / shared-board research; stacked on FIELD-011 (and all its unmerged predecessors). The user wants the machine to offer a *physical-material inventory and editable hypothetical placements* from the same photographs and sketch, rather than asking them to translate everything into text.

## Working affordance crossing

```
Sketch: rough desired boundaries ----> editable plan coordinates (FIELD-011)
Photographs: object regions ---------> separate photo-normalized coordinates
                        |                  |
                        v                  v
                    Evidence + possible role tags (not verified properties)
                        |
                        v
            [ Reasoning A ]      [ Reasoning B ]
        alternative-use/placement   direct photo bbox/role/mobility/width UI
                        \                  /
                         \------ event ledger -----/
                              |
                       separate unscaled ghost
                              |
                     optional human placement
                              |
                      replanning & inspection
```

**What is executable:** Browser users can drag a box around an object in any reference photo; mark possible roles (`boundary_module`, `support_candidate`, `flexible_barrier`, `visual_cue`, `unknown`); confirm/reject the **description**; record mobility and an approximate/independently measured width; preview an illustrative ghost on a desired boundary; and put a **tentative** object copy onto the shared board. Two existing workers reevaluate hypotheses and next-step interaction options from the same replayable event stream. Undo returns to prior semantic and geometric state. Photos never leave the browser by default.

**What is deliberately not claimed:** The interface does **not** automatically find or classify objects from photos on its own. The optional `local_vlm.py` is an opt-in loopback-only Ollama call that can generate **tentative** source-bounded object regions; it was tested with mocked responses only. Its real execution requires an appropriately provisioned local multimodal model and explicit consent. A clicked region, a model bbox, a human description, or an illustrative ghost **does not** establish dimensions, joint capacity, an existing-world location, assembly stability, or safe dog containment. No photo was projected into sketch coordinates. The ghost is 28% of a target **for visualization**, not a material size estimate.

## Try it

Use the standalone HTML prototypes supplied with this experiment; no account, server or network needed:

- `MOTIF_FIELD012_Public_Object_Demo.html` — invented sketch and **drawn synthetic material picture**, with interactive photo-region tagging.
- `MOTIF_FIELD012_Upload_Your_Own.html` — upload your own sketch and photographs locally.
- `MOTIF_FIELD012_Private_Object_Workbench.html` — generated in the user's conversation only. Contains personally supplied property imagery; **not** in public GitHub.

Workflow: choose a photo thumbnail → draw a box around a material → label and assign a candidate role → select **Add photo-region hypothesis** → preview a position near a desired boundary → optionally place a **tentative copy** → move/resize that board copy → record an estimated measurement → see both branches update. Confirming a description confirms only that description, never a load rating.

## Optional local vision model

With Python 3.11+ and Ollama running locally, with an appropriate compatible Qwen3-VL checkpoint installed:

```
python experiments/field012/local_vlm.py \
  --photo /your/local/image.jpg --photo-id photo-0 \
  --model qwen3-vl:2b-instruct --consent-local-model \
  --output /your/private/material-candidates.json
```

Open the **same photo bytes** in the workbench and select **Import local VLM candidates**. The object packet must match the current photograph's SHA-256 and workbench photo ID, and must contain only tentative model observations. The notebook images previously used in the private demo were downsampled before embedding, so packets generated from their original full-resolution photo files will correctly fail source-hash matching. Upload those original files directly as new photo sources to import corresponding packets.

No external API calls are made. The adapter uses `http://127.0.0.1:11434/api/chat` only after explicit `--consent-local-model`; the `--model` argument selects an already installed local model, not an auto-download. Do not run with a network-exposed localhost service or share private photos without permission.

## Verification

```
cd experiments/field012
node test_material.js
python -m unittest -v test_local_vlm.py
cd ../field010 && node test_core.js
```

Mock-controlled negative cases ensure a model cannot assert measured dimensions, user confirmation, verified stability or photo-to-yard coordinate registration. Tests cover source hashes, changing roles, fixed material refusal, bad boxes, undo, as well as both branch reactions. Standalone public and private interfaces were exercised in Chromium by selecting a photo region, adding a material, previewing a ghost and placing a tentative copy. No real VLM inference was performed.

## New experimental questions

1. Can a real locally provisioned VLM identify actual reusable pieces in unfamiliar photographs, and are the boxes accurate?
2. Does object-aware photo tagging reduce clarification time relative to conversational description?
3. Do interactive ghost placements help human decisions without introducing false certainty?
4. Does event replay preserve the precise human-vs-machine ownership of a particular material claim?
5. Can we propose an *actually new* physical combination that an independent practitioner judges usable and safe, and how much extra confirmation does that require?

See `EVALUATION.md` for frozen, independently labeled benchmark design. None of these future outcomes has been claimed.
