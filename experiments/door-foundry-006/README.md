# DOOR-FOUNDRY-006 — IMAGE-IN: THE VISUAL IMAGINATION APERTURE

**MOTIF can now read actual PNG image bytes, extract a tiny pixel-level scene, discover why its former operator family cannot express the requested image change, receive a genuinely generated new GRAFT visual transition program through CANNON, and produce a sequence of imagined future PNG images.**

This is **not** a neural image model or semantic photograph understanding. It is a reproducible, source-pinned **symbolic visual simulator**. The images are real PNG files, but deliberately small and restricted to three precise RGB colors: white empty, red rigid 2×2 block, and blue immovable obstacle. Each input image is 3–16 pixels wide and tall, 8-bit RGB/RGBA (opaque), noninterlaced and validated with CRC and bounded decompression. Ordinary photos, unknown colors, fonts, people, object identity and visual semantics are **not** understood.

## The actual source-owned crossing

1. **MOTIF visual_in.py** accepts two **real PNG files**: current image and hypothetical target. Its standard-library PNG decoder verifies bytes, CRC, size, format, palette, red block shape and fixed obstacles, then emits `motif.visual-gap.v0`. This is genuine image input, not text masquerading as pixels.
2. The original **GRAFT-029** program family performs only addition of graph facts. Image relocation needs old red pixels **removed** while the object's four pixels are retained. MOTIF supplies an invariant explaining why add-only cannot perform the visual relocation.
3. The **original unmerged GRAFT-030** source at exact commit `0347c492c5e517788c0cbd87ee6f57aef3ce2a81`, [GRAFT PR #26](https://github.com/the-static-collective/GRAFT/pull/26), constructs three different executable JS pixel transformation variants (copy, recolor, move) and tests them against independent training/selection/negative synthetic frames. Only the atomically *removing-and-adding* rigid move survives.
4. The **original CANNON-095** review code at exact commit `3f2210ba6272a9538843d093edb64d1b29d2f294`, [CANNON PR #95](https://github.com/the-static-collective/CANNON/pull/95), verifies the real source PNG bytes and original source module, reexecutes GRAFT generation and independently checks the generated program on eight entirely additional synthetic frame cases. The result is unsigned **HOLD**, not permission to execute externally or deploy.
5. **MOTIF-006 build.py** checks the same PNGs, source owners, exact GRAFT compiler and held CANNON evidence before compiling a new **runnable local MOTIF build**. The generated program, actual input PNG bytes, original PNG parser and fixed operator adapter are bundled with content-addressed receipts.
6. **MOTIF-006 run_visual.py** uses GRAFT's **actual generated JS program** as the transition operator in a bounded breadth-first search. Every proposed hypothetical frame is independently checked against a simple classical pixel-shift rule. It renders each intermediate *imagined* PNG and a single **imagined-storyboard.png** contact sheet.
7. A fair classical exact shift planner with the **same pixel interpretation and transition grammar** obtains the same minimum-length path. No algorithmic superiority is claimed.

## Demonstrated local imagination

The example is a genuine 9×8 PNG. The red 2×2 block starts left of a blue obstacle column; the target shows it on the right. The generated move operator must mentally route the block around the obstacle, not teleport or merely copy/repaint it.

**Verified on GitHub Actions:** 12 predicted PNG frames, 11 hypothetical moves, four counterfactual first-step images, and 11 classical minimum moves. No real object moved. Original GRAFT and CANNON suites, plus **20 MOTIF integration tests**, passed.

The held artifact includes **start.png**, **target.png**, the runnable generated source, **imagined-storyboard.png**, a frame-by-frame PNG folder and machine-readable provenance/plan receipts.

## Use your own tiny image

The actual reader accepts local PNG files matching the strict palette/geometry. The geometry must be fully visible, one red 2×2 block, blue immobile obstacles and no overlapping start/target red pixels:

```bash
python experiments/door-foundry-006/visual_in.py \
  --image my-current.png --goal my-target.png --out visual-gap.json
```

This produces a source-hashed `visual-gap.json` without contacting outside services. To build an executable, a fresh independent CANNON review must first be generated **for those actual image bytes**. A packet from the example is not transferable to arbitrary new input; its PNG hashes are bound to the exact example.

To reproduce the complete demonstrated pipeline from scratch, use the source-pinned GitHub workflow. The core commands, with checkouts named `motif-image-source`, `graft-source` and `cannon-source`, are:

```bash
python experiments/door-foundry-006/visual_in.py --demo --out image-inputs

node cannon-source/experiments/cannon-095/review.mjs \
  --graft graft-source --motif motif-image-source \
  --start image-inputs/start.png --goal image-inputs/target.png \
  --gap image-inputs/visual-gap.json --out evidence/cannon-visual-review.json

python experiments/door-foundry-006/build.py \
  --start image-inputs/start.png --goal image-inputs/target.png \
  --gap image-inputs/visual-gap.json \
  --receipt evidence/cannon-visual-review.json \
  --graft graft-source --out generated-visual-motif

python generated-visual-motif/run.py --out imagined-futures
```

Then open `imagined-futures/imagined-storyboard.png` to **look at what MOTIF simulated**, frame by frame.

## Limits and next frontier

This is a **finite, author-designed translation grammar** and a deterministic search over tiny raster states. The real image input does not imply recognition of arbitrary objects, camera access, learned optical mechanics, natural-image reasoning, a visual foundation model, subjective experience, open-ended program synthesis, or useful human outcomes. Actual authority remains absent; no external requests, private photo reads, automated owner merges, production deployment or contacts are performed.

Next: allow perceptual hypotheses from **larger or ordinary user-provided images** using a separately evaluated image encoder, preserve source pixels and uncertainty, infer multiple object/action grammars from before/after visual evidence, and test against classical vision/planning baselines before claiming any generalized visual imagination.

**Image input ≠ interpretation. Hypothetical frames ≠ observations. Source-valid code ≠ authorized action.**
