# THOUGHT-007 — Non-fungible thought instances

**Status:** isolated, standard-library-only **synthetic development experiment**, extending the [full-stack Thought Fields RFC](../../docs/THOUGHT-FIELDS-006-010-FULL-STACK-RFC.md) and THOUGHT-006. Review-only branch. No deployment, network access, signed identity, verified semantic comprehension, or external action authority.

## Question

Can one expression refer to multiple possible concepts **without collapsing them**, and can one persistent concept have multiple context-specific, non-interchangeable manifestations, each appearing in several simultaneous placements, while keeping identity, evidence and pencil/pen state independent from visualization?

### Five intentionally separate identities

- **Concept:** immutable unique `concept_id` for one *interpreted* referent, with revisioned human-readable label/description and a declared origin. Two concepts may share the same word but remain distinct.
- **Expression:** uniquely sourced text/word occurrence (e.g. `"home"`) with declared origin and utterance context. An expression is not a concept.
- **Referent proposal:** a hypothesis linking an expression to *one* possible concept; multiple proposals can coexist. No automatic disambiguation or concept merger.
- **Manifestation:** unique context-local occurrence of a concept with separate role, phase and parent/fork lineage. It does not become a new concept merely because it is duplicated.
- **Placement:** unique drawing/view occurrence of one manifestation in one view. Multiple placements of the same manifestation **in the same view** are allowed. Position is bounded float x/y or `None` for the NONE view, never source evidence.

**Additional object:** `EquivalenceProposal` has status `HYPOTHESIS_ONLY` and never merges or aliases concepts. Two equal labels, co-mentions, neighboring screen positions or flower-hex placements may NOT initiate identity merging or promote an assertion.

### Epistemic separation from THOUGHT-006

This layer deliberately does **not** change `Assertion`, `PENCIL`, `PEN`, commitment state, confidence or action authority in THOUGHT-006. A legacy `NODE` may be imported as a **distinct concept for that explicit legacy ID**, not a verified real-world referent. The adapter intentionally imports names only; source claims and pen states remain in the ledger and require separately justified linkage in later work.

The `PEN_CONTEXT` manifestation phase is a label for viewing an *existing* context, **not an authority grant or a pen commitment**. It cannot call ledger `.commit()` and cannot produce trusted facts. This experiment has no mechanism to enter a new pen state.

### Executed operations

- `concept`, `revise_concept`, `expression`, `propose_referent`.
- `manifest` for context-specific instances; `parent_id` permits a fork **only of the same concept**.
- `view` with `association`, `dependency`, `tension`, `timeline`, `affordance`, `flower_hex`, or `NONE` lenses; for now a view is a **named projection container**, not a full reasoning renderer (that's THOUGHT-008).
- `place`, `move`, `remove_placement`; removal retires only the placement, not its manifestation or concept. No destructive delete.
- `propose_equivalence`: only a hypothesis, never `merge`.
- `semantic_snapshot`: stable under changes to views and placements; `snapshot` includes them, event count and hash tip.
- `occurrences`: enumerate a concept's manifestations and active appearances without collapsing their identities.

### Persistence and boundary

One local `JSONL` append-only hash-chained log; deterministic canonical replays check IDs, referents, lineage, typed views, coordinate bounds, `NONE` projection and event order. File fsync + stale writer check, but this is **not** a transactionally locked multi-writer database. The hash chain detects inconsistent/corrupt local replay relative to a trusted hash tip; it **does not** authenticate the original author or make the record tamper-proof against complete file replacement.

A demonstration uses `home` as two context-specific concepts, multiple manifestations of shelter, and placements in association, dependency, hex and no-map views. The label is not used to infer identity. Separate source labels are asserted, not externally verified. No identities or conclusions depend on layout positions.

## Reproduce

```sh
cd experiments/thought-007
python -m unittest -v test_field.py
python demo.py > experiment-results.json
```

All results are **synthetic tests developed with the algorithm**, not blind accuracy evaluations or demonstrated gains in intelligence. Compare with a classical unique-ID graph and a one-node-per-word control in subsequent held-out tests before claiming usefulness.

## THOUGHT-008 exit gate

Introduce *parallel* independently rendered association, dependency, tension, flower-hex and NONE projections from the same frozen semantic snapshot; support multiple manifestations and placements. Change any coordinate/layout and verify semantic identity + pen ledger evidence stays byte-for-byte unchanged. Compare answer quality with one-view and no-view controls; respect explicit contradictions and source independence. Never infer an association from distance alone.
