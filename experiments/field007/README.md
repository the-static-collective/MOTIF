# FIELD-007 — INK BEFORE INTENT

**Research draft stacked on FIELD-006**. This experiment does something FIELD-006 explicitly could **not** do: it reads **actual pixels of a paper sketch**, finds groups of short separated strokes automatically, proposes candidate dotted-line fragments, and re-enters FIELD-006's provenance and review contract. It also performs conservative computer-vision feature correspondence among optional photos. **No model can yet assert a full dotted fence route, metric geometry, user intent, or a safe construction.**

## What is executable today

- `ink.py`: local OpenCV short-dash detection, long ruled-line suppression, independent raw-ink continuity check against falsely splitting a solid line into dashes, bounded H/V group search, candidate overlays and pixel-source SHA-256 receipts. Every candidate remains `TENTATIVE`.
- `views.py`: ORB+bidirectional ratio check+RANSAC image matching; repeats do not become ground-truth photo viewpoints, property coordinates or verified scene identity. Chain-link repetition creates false-match risks; the method HOLDs when evidence is weak.
- `loop.py`: bounded **look → group → check original ink → review source contract → reconstruct** loop. Calls FIELD-006 `review_model_packet` to preserve the user's unchanged sketch and user authority. A photo's pixels never become sketch or yard coordinates.
- `benchmark.py`: 18 author-generated, non-blind image cases (with ruled lines, distractors, solid strokes, incomplete routes), plus 8 rotated-angle stress cases. The benchmark is *not* an independently authored or blind vision evaluation and should not be presented as independent model reasoning.
- `test_ink.py`, `test_views.py`, `test_loop.py`: offline regression tests including negative cases.

The candidate overlay draws **measured ink fragments**, not an invented interpolated connection. Low-level computer vision has no understanding of what the line *means*. To discover the intended perimeter reliably from an unfamiliar image and use photos for affordance reasoning, a language-capable visual reasoner is still needed. FIELD-005 already offers an optional localhost Ollama image adapter, but a real Qwen3-VL inference was **not** executed in this experiment. A true model evaluation needs an installed model, consent, unfamiliar inputs, independently frozen labels and comparisons at matched budgets.

## Run

```sh
python -m pip install -r requirements.txt
cd experiments/field007
python -m unittest discover -v
python benchmark.py
python run.py --sketch /local/private/sketch.jpg --source-id paper --out-dir /local/private/results
# Optional: --atlas /local/private/field006-packet.json --photo photo1=/local/private/a.jpg
```

**Privacy:** Only program code, synthetic tests and documentation belong in the public repo. Never commit original property images, source locations, user-authored sketch geometry, local receipts, or private screenshots. The result can be locally inspected and deleted.

## Actual private dry run, Nov 11 2026 (not part of public repository)

- Original supplied paper sketch: **4 ink groups** detected without manually supplying any trace vertex locations (one horizontal dotted-like group, three vertical groups).
- Source sketch remained unchanged; **all four were gated as tentative** by the FIELD-006 contract. Some parts of the intended line remain unidentified; no continuous route was assembled.
- Nine distinct photographs registered. An ORB overlap attempt considered 36 photo pairs and **HOLD on all 36**: differing viewpoints did not offer sufficiently reliable geometric matches. That means *no automated photo-to-paper registration*, not that the photos contain no shared objects.
- User-provided statement that dotted lines indicate a desired fence remains authoritative **about the meaning of confirmed dotted strokes**, but the automatic pixel detector is not authorized to decide which marks the user intended. No automatic fence assembly, structural testing or real VLM inference occurred.

## Next falsification

1. **Blind real VLM on source images**: independent landmark/dash/solid labels, actual location and stroke uncertainty; compare model-only vs CV-only vs CV+VLM. Track both false line promotions and missed lines.
2. **Rerender and reread**: propose a vector trace from a model, rasterize over original, visually critique ungrounded segments and revise *without copying model assertions into observation*. Save a proof-like pixel support receipt.
3. **Spatial language**: maintain separate spaces for photo, sketch and hypothetical physical yard; evidence-backed cross-view identity before any placement.
4. **General practical transfer**: blindly compare unfamiliar shelf, doorway, workbench and garden layouts. Study whether adding visual working memory reduces user clarification turns **without** multiplying unsafe confident guesses.
5. **Field evaluation**: user-supervised cold fit, no dogs present, with explicit hazard checks and independent reality feedback. No real-world dog containment is certified by this code.

### Research truth

Current visual recognition is classical, source-bound pixel analysis, **not an open-weights vision model**. Synthetic benchmark coverage does not establish generalization. `HOLD` is a valid outcome when photos have insufficient shared features or a hand-drawn line cannot be mapped confidently. An advertised 200-lb zip-tie rating does not by itself validate the whole support network.