# MOTIF FIELD-013 — First Look Without a Pointing Finger

**Status:** Experimental, stacked on unmerged FIELD-012. Offline browser fallback + optional explicit localhost Qwen3-VL batch path. Not deployed; not a verified physical planning system.

## What changed

Previous FIELD-012 required a human to draw photo boxes or import a manually run image-model result. Here the **browser starts analyzing pixels when photographs arrive**, proposes tentative *visual regions* with source hash and pixel-normalized bounding rectangles, and lets a person reject, relabel and correct them without a prose conversation. It does not identify objects: foliage and textured ground often score highly. No false material name is inferred from pixel saliency.

A separate explicitly enabled, localhost-only path (`batch_vlm.py`) can ask an independently installed open-weights Qwen3-VL/Ollama vision model to identify possible materials in up to 20 uploaded images. The response is normalized through the prior FIELD-012 validator and stays `LOCAL_VLM_TENTATIVE` with no measured size, known mobility, registered yard position or assembly safety. **This workflow was tested with a fake model transport, not a real model checkpoint; no Ollama model was installed in the execution environment.**

`plan.js` uses confirmed or merely hypothesized material roles alongside *existing desired-route geometry* to produce non-committal pairings and a distinct support-network hypothesis. Unknown regions produce clarification controls rather than invented fencing plans. Each pairing explicitly holds on physical fit, photo-to-yard registration and joint stability.

### Run

No dependencies for browser use. Open `MOTIF_FIELD013_Upload_Your_Own.html` (single-file download), upload a sketch and one or more images. The browser finds pixels and offers editable regions. It does **not** contact external services. The private preloaded version contains personal photographs and must not be published.

Optional real open-weights model route **on a machine with an installed Ollama multimodal model**:

```bash
python experiments/field013/batch_vlm.py \
  --photo photo-0=/private/photo0.jpg \
  --photo photo-1=/private/photo1.png \
  --model qwen3-vl:2b-instruct \
  --consent-local-model \
  --output /private/tentative-model-packet.json
```

Import the JSON batch into the browser through **Import local VLM candidates**. Exact photo SHA-256 hashes must match locally loaded images. Model output is structured, bounded, and rejected on bad coordinates or unsupported claims. A local model may be inaccurate or wrong; importing is not independent verification. A local Ollama model and resources are required; on old macOS systems use another compatible host, not unsupported installs.

### Tests

```bash
cd experiments/field013
node test_scan.js
python -m unittest -v test_batch.py
# Regression tests from parent branch:
node ../field012/test_material.js
node ../field010/test_core.js
python -m unittest discover -s ../field012 -p 'test_*.py'
```

## Privacy, capability and failure boundaries

- Sketch and photos are not sent to an external provider by the browser. Calling an Ollama model requires an explicit flag and uses only 127.0.0.1.
- No personal photos, private coordinates or generated private previews belong in public GitHub sources.
- Local browser saliency is **real image processing**, but is not object recognition, detection accuracy, or novel learned visual reasoning.
- Apparent visual material roles are hypotheses: a chair, cage, trampoline, mesh, or zip tie is not a proven anchor or safe dog barrier.
- The UI's plan previews remain illustrative: no homography, calibrated physical dimensions, joint-capacity calculation, or certified containment.
- A visible zero-turn edit surface is not proof of fewer user clarification turns until a human comparison study is conducted.
- The study includes a negative result: initial unclassified saliency proposals on nine private yard photos clustered around leaves, ground clutter and other textured regions, not reliably around reusable materials. **A real semantic vision model is still the missing bridge.**

## Next falsifiable milestone

Run Qwen3-VL or comparable local VLM on a **held-out, independently annotated and user-authorized** set of practical reuse photos. Measure material/object precision and recall, region overlap, role plausibility, number of corrections, visual-reasoning improvements, false joins between photos and drawing, and safe abstention. Compare semantic VLM, classical saliency, manually marked regions and VLM+pixel critic under matched inference budgets; include different depths, clutter, curved objects, reflective surfaces and negative controls. Do not promote a tool to main without evidence.
