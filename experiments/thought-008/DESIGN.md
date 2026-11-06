# MOTIF THOUGHT-008 — Parallel Geometric Thought Fields

**Stage:** executable, standard-library-only synthetic research. Branch stacked on THOUGHT-007; not deployed or merged. Does **not** claim emergent intelligence, semantic understanding, improved answers, autonomous selection, verified evidence, or outside action rights.

## What this is

THOUGHT-006 supplied a reviewable *PENCIL/PEN* working-belief ledger. THOUGHT-007 separated a concept, an occurrence of a phrase, an interpreted manifestation, and a view-specific placement. **THOUGHT-008** takes a *frozen THOUGHT-007 snapshot* and separately supplied attributed relationships, then produces **six views of the same unchanged source field in one run**:

| View | Purpose | Source logic |
|---|---|---|
| **Association** | Sketch neighborhoods and identify structurally missing connections | Common-neighbor questions, requiring >=2 shared authored neighbors and >=2 *claimed* source roots |
| **Dependency** | Trace declared prerequisite arrows and report cycles | Directed `requires`; BFS; DFS for cycles |
| **Tension** | Keep attributed opposing claims visible | Explicit `contradicts` edges only; never auto-collapse |
| **Affordance** | Explore conditional openings from a chosen starting manifestation | Directed `enables` reachability plus separately recorded unmet `requires` |
| **Flower hex** | Explore sixfold lattice packing as an alternate arrangement | Regular axial-coordinate placement; no new semantic inference |
| **NONE** | Answer without placing thoughts on a map | Same underlying evidence/typed question index, no coordinates |

These views are *interpretations of a shared snapshot*, not six new independent witnesses. Every view retains the same SHA-256 **source evidence fingerprint**, same source relations and same IDs. Different projections are **not** allowed to change confidence, node meaning, truth, pen state, causal direction or external authority.

Existing THOUGHT-007 authored placements are preserved, **including two placements of the same manifestation within one view**. Every missing placement is generated as display-only and does not become an event in the THOUGHT-007 log. Different manifestations of the same concept remain different nodes. A concept label is never used as an identifier.

### Source contract

`ThoughtViews(field_snapshot, relations)` reads a THOUGHT-007 `.snapshot()` and a bounded list of six-field source relations:

```json
{"id":"r:1","source":"m:food","target":"m:storage","predicate":"associated","origin":"claimed:source","status":"AUTHORED"}
```

The `AUTHORED` flag means **someone provided this relationship as part of the input graph**. It is *not* a mathematical proof, witnessed event or authenticated truth. `HYPOTHESIS_ONLY` input is retained for drawing/audit but excluded from supported-path and bridge logic. Roots are declared strings and are not verified independent sources.

The **read-only `interop.from_ledger_snapshot()` adapter** requires an explicit mapping from THOUGHT-006 node IDs to THOUGHT-007 manifestation IDs. It never chooses this mapping based on equal words. A 006 `PEN_SCOPED` and unchallenged working conclusion maps to `AUTHORED` *only as a scoped source assertion*. Pencil, challenged or withdrawn statements become `HYPOTHESIS_ONLY`. Unsupported legacy predicates and unmapped contexts are reported as skipped. THOUGHT-006 and THOUGHT-007 source logs are never modified.

A caution: this first relational packet tracks only one declared origin string per edge. It does **not** establish an authenticated chain of independent source roots or retain the full legacy PEN justification. A later revision must add richer proof objects before relying on this as a source-verification mechanism.

### The scientific comparator and limits

`engine.evidence_index(anchor)` is a source-only, no-layout **classical graph baseline**. It is computed identically when running one geometry, all geometries, or `NONE`. Association bridging uses common-neighbor rules; dependency uses BFS and DFS; affordance uses BFS. Spring force and axial hex lattice are standard layouts. **This milestone does not improve answer quality over the no-map baseline**, because all semantic inferences are deliberately isolated from display positions. This is a feature of the epistemic safety gate, not a claim of better thinking.

It supplies an execution substrate for the next hypothesis: **THOUGHT-009**, which can try generating *new questions* from multiple views, validate them independently against source assertions, and benchmark against a matched no-map control. Geometry may be disabled whenever it isn't helpful. A visually nearby pair is never automatically related.

### Reproduce

```sh
cd experiments/thought-008
python -m unittest -v test_multiview.py
python demo.py
python benchmark.py
```

The demo writes `parallel-thought-fields.svg`, `parallel-thought-fields.json` and `experiment-results.json` locally. The fixture is fictional: community meal, food, transport and ambiguous meanings of **home**. It includes disputed venue claims and an explicitly **hypothetical** shelter/belonging association.

### Verification / falsification

- Exact same semantic input digest and unchanged 007 log after all views; exact 007 event replay.
- Multiple placements for one manifestation in the same association view, alongside two non-interchangeable interpretations of `home`.
- Moving/reprojecting source placements cannot create a supported association or change relation status.
- No-map and multi-map source-only answers match byte-for-byte.
- Directional `requires` never reversed, dependencies cycles visibly reported, conditional affordances do not become plans or actions.
- Contradictory and hypothetical links do not enter positive association inference.
- Explicit 006-to-007 binding; no accidental unification by label; challengers degrade an existing pen-derived edge to hypothesis.
- Deterministic results for fixed seed, bounded input, escaped SVG user labels, zero imported authority.

Potential falsifiers: generated positions alter the evidence index; identity fusion occurs across contexts; a `HYPOTHESIS_ONLY` edge silently influences proof; hex layout gets treated as evidence; no-map and multi-map evidence indexes diverge; upstream PEN statuses are modified; synthetic cycle goes unreported.

## Next stage: THOUGHT-009

Build task-conditioned *zero/one/many-view selection* with explicit cost and abstention, independent counterexample/corroboration verification, and a preregistered held-out benchmark against the exact same classical no-map and single-map controls. The value of multiple maps must be **measured**, not assumed.
