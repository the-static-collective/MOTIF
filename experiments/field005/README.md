# FIELD-005 — LOOK, DRAW, REFRAME, CHECK

**Status: draft research experiment stacked on FIELD-004. No live deployment.**

FIELD-004 proposed several 'unsaid' resourcefulness moves from an authored typed visual packet. FIELD-005 tests whether the same *general operators* can act across different domains and provides a inspectable **visual scratchpad**. It **does not yet demonstrate** a vision model independently finding those transformations in photos. No trained model was run in this experiment.

## Two visual jobs, not one

1. **Look**: optional local, opt-in Ollama vision model extracts *tentative* objects, features, boxes, possible affordances. Recognition isn't measurement, structural strength, ownership or permission. Some desired functions must still be given by the user.
2. **Draw**: a deterministic SVG diagram shows known objects, recorded present geometry, hypothetical target geometry, and operator proposals. Drawings are **not to scale**. A local model can optionally re-read a PNG rendering, offering another tentative critique—not a verified result. The scene graph is the source of record, not generated pixels.

## Install and run (stdlib-only offline core)

```sh
cd experiments/field005
python -m unittest discover -v
python benchmark.py   # outputs/*.svg, outputs/*.json
python demo.py --scenario yard --out outputs/demo-yard
python demo.py --scenario shelving --out outputs/demo-shelf
```

Optional local actual pixel input (requires a running **Ollama** with a downloaded image-capable model such as `qwen3-vl:2b-instruct`):

```sh
ollama pull qwen3-vl:2b-instruct
python demo.py --photos /path/to/local-photo.jpg --goal 'Make a useful boundary' \
  --function delineate --allow-local-images --out outputs/private-test
```

Photos are sent only to `http://127.0.0.1:11434/api/chat` (localhost); no external API. Local photo files are **not committed**. `--reread-local-sketch` additionally requires `cairosvg` and asks Ollama to critique a rasterized rendering. No model download, internet call, photo transmission, or account access occurs automatically.

## What is actually checked

- The same typed operators run on five **author-designed** scenarios: yard, makeshift shelving, rain shelter, tool organization, and temporary pathway.
- Target function, inventory, and evidence type are explicit. Reassign, relocate, compose, redraw and opportunistic support proposals remain conditional.
- Fixed objects never become 'movable' from a photo. Absent connectors produce missing-prerequisite questions, not imaginary connections.
- The critic retains structural/safety HOLD status. Drawing does not verify physics or image interpretation.
- The weak literal-current-use baseline has **zero** exact labels in these scenarios (by construction). Thus a numerical 'win' over that baseline has **no scientific significance**. Count operator families and false claims instead. A matched LLM planner, human reviewers, truly blind physical cases, and a genuine local VLM run are still needed.
- Tests use mocked local vision responses only: they do not imply the VLM extracted objects correctly.

## Relevant open foundations (checked November 2026)

| Role | Candidate | Notes |
|---|---|---|
| Main image-language model | [Qwen3-VL](https://github.com/QwenLM/Qwen3-VL) | 2B/4B compact variants via Ollama; stronger reasoning variants. Apache-2.0 model variants; verify exact checkpoint. |
| Low-resource fallback | [SmolVLM2](https://huggingface.co/HuggingFaceTB/SmolVLM2-2.2B-Instruct) | Apache-2.0; image/multi-image/video input. |
| Grounding and pointing | [Molmo2](https://github.com/allenai/molmo2) | Can help point to objects, especially multi-image correspondence. Verify exact checkpoint terms. |
| Open vocabulary object detection | [Grounding DINO](https://github.com/IDEA-Research/GroundingDINO) | Apache-2.0 code. Specialist stage, not a reasoner. |
| Object masks | [SAM 3.1](https://github.com/facebookresearch/sam3) | Promptable segment/tracking; Meta SAM-specific license, not Apache open source. GPU-heavy. |
| Scene depth | [Depth Anything 3](https://github.com/ByteDance-Seed/Depth-Anything-3) | Small/Base weights Apache-2.0; several larger variants non-commercial CC BY-NC. Depth ≠ metric scale without calibration. |
| Multi-view scene geometry | [VGGT](https://github.com/facebookresearch/vggt) | Commercial variant is separately gated; original checkpoint non-commercial. Heavy and unnecessary for first demo. |
| Sketch-as-thinking paradigm | [Visual Sketchpad](https://visualsketchpad.github.io/) | Draw intermediary visual marks, inspect and replan; architectural precedent, not a plug-and-play general spatial intelligence. |
| Practical drawing/geometry | [OpenCV](https://opencv.org/license/) + SVG | Apache-2.0 modern OpenCV; deterministic diagrams, masks, spatial tests. |

### Science boundary

A raster drawing generated from an inaccurate scene graph is still inaccurate. A vision model's *second reading of its own diagram* may amplify errors. We must evaluate against separately annotated holdouts and manual physical tests—not reward drawings for looking plausible.