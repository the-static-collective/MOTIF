# MOTIF-GEOM-005 — Thought Space: optional geometry for ideas, words and relationships

**Status:** deterministic, isolated, synthetic research. The user requested a way for MOTIF to *choose* to think with conceptual geometry when useful, not to be permanently trapped in a 2-D chart. This adds an optional, reviewable scratchpad to MOTIF's experimental branches, not a deployed agent, LLM, semantic comprehension, or claim of machine consciousness.

## Contract

- Nodes represent explicit named ideas, words, claims, tasks, or resources, with a `kind` field.
- Directed, typed edges include `requires`, `enables`, `associated`, `contradicts`, `co_mentioned`, an origin ID, an unsigned confidence, and an observed/hypothetical bit. Conflicting claims remain conflicts, not graph traversal edges. A direction is never silently reversed in a reasoning path.
- Raw prose can generate *co-mention only* links through local tokenization. This is a deliberately weak record of text proximity, **not** an embedding, semantic meaning, a claim of truth, or an authenticated source.
- A hypothesis engine proposes missing associations when two nodes have at least two witnessed common neighbors supported by at least two distinct origin IDs. Echoes from a common origin cannot be counted as two independent witnesses. The proposal remains `HYPOTHESIS_ONLY`, never silently inserted as a fact. Distinct strings are only *claimed* origins; the prototype does not authenticate source independence.
- The `choose_thought_space()` operator selects a reasoning mode based on the question and available graph: `trace` (shortest path with source evidence), `bridge` (new associations), `cluster` (connected-group inventory), `contrast` (disagreements), or `inventory`. It independently chooses whether to draw a spatial representation; a caller can explicitly disable geometry or request a specific layout (`spring`, `radial`, `flower_hex`). The routing criteria are transparent heuristics, **not learned self-direction**.
- Spatial representations include spring-force, concentric radial, and an **optional Flower-of-Life/triangular-lattice** arrangement. Projection may be chosen by a simple edge-stress score for exploration or by task (radial for tracing). Coordinates are for viewing, never used as evidence of relatedness, causal identity, importance, or permission. No matter how beautiful a layout, **the typed, attributed source graph carries meaning**.

## Why this is connected to GEOM-004

GEOM-004 learns a reusable intermediate geometric *macro* from examples (a median constructed with line + midpoint). GEOM-005 gives MOTIF a separate optional vocabulary for relational paths, conflicts, candidate bridges and visual arrangements. These are isolated experimental modules; sharing a repository is not a proof of automatic cross-integration, and a geometric graph view is not a reasoning primitive added to GRAFT/CANNON without independent review.

## Controls and checks

- 16 unit tests enforce source labels, no external agency, directionality, contradiction separation, originality of hypothetical edges, provenance deduplication, explicit refusal to draw, display determinism and SVG escaping.
- A synthetic community-meal example is **fictional** (food shelf, storage, volunteers, meal, gathering): it is used only to exercise graph routing and two-witness candidate links, *not* to assert these resources exist.
- Ordinary classical BFS, common-neighbor prediction, basic connected components and force-directed layout are all **existing standard algorithms**. This prototype does not beat or transcend them; it packages them with evidence and a selectable interpretation. There is no trained semantic model, no empirical comparison to graph embedding libraries, and no demonstrated improvements to human or model reasoning.
- A no-geometry ablation must return the same typed reasoning answer with `projection: NONE`; no layout coordinate may become an epistemic fact. Source origin strings are not independently verified.

Run: `cd experiments/geometry-005 && python -m unittest -v test_thought_space.py && python demo.py`. Operator-facing JSON entry: `python interface.py example-input.json optional-view.svg` (prints reproducible typed evidence JSON; SVG requires geometry to be allowed).

## Next falsifiable frontier

Blind comparison of answer utility on user-supplied (permissioned) text over *matched* no-map, force, hex and radial controls, under predeclared questions; add schema-aware text extraction with contradiction detection and human validation, explore embedding spaces of more than two dimensions or non-Euclidean manifolds, and compare actual affordance gain. If geometry does not improve retrieval or decision quality on held-out tasks, disable it; do not convert visually appealing proximity into truth.
