# MOTIF THOUGHT-012 — A question that survives a change of perspective

**State:** executable standard-library Python synthetic experiment, stacked on THOUGHT-010; no new live JAR;VIS service, Free Graph promotion, pen commitment or external action. The core is a deterministic classical graph analyst; no claim of independent model insight or newly discovered geometric laws.

## User motivation

The same thought can be explored abstractly, revisited through dependencies, contradictions and affordances, and later used in concrete planning. A **pencil** question should be allowed to *travel* between ways of looking at a problem, retain its identity and what was learned, and resist premature pen promotion. A change of map must not be treated as independent testimony.

## Actual source

Uses source-owned THOUGHT-007 `ThoughtField` for non-fungible concepts, manifestations, placements and replay, and THOUGHT-008 `ThoughtViews` for the underlying typed relation graph and actual geometric projections. The experiment is an isolated `experiments/thought-012` module; THOUGHT-006's pen ledger is not mutated, and THOUGHT-010's local door is not yet modified.

## A single cross-lens reasoning cycle

1. Seed a **question only** either from a structurally supported association candidate (two common authored neighbors, two *claimed* origin roots), **or from an explicit operator-selected pair of non-fungible manifestation IDs**. The second case stays `UNSOURCED_PENCIL_SEED`, requires *no* pretended independent witnesses, and can drive the human-facing desk. Neither is authenticated truth.
2. Bind the question to its stable manifestation IDs, exact relation witness IDs, source-evidence digest and source snapshot digest.
3. Carry the question through 0–3 inspections: **dependency** (declared prerequisites), **tension** (explicitly contradicting claims in a small neighborhood), **affordance** (declared `enables` relationships). Each inspection may add another source-grounded QUESTION_ONLY with original evidence IDs. A question is not a new asserted relation.
4. For each selected lens, optionally invoke the **actual** THOUGHT-008 projection and record a display digest/placement count. Geometry is *never read by* the question or eligibility logic; source-only inspection runs the same checks with zero projections.
5. Return a deterministic chained list of steps, carried question inventory and status. `resume()` recomputes from the frozen source, checks the old receipt, and refuses a changed evidence graph **or even a different field snapshot** until the operator revalidates.

**Reconsideration:** `feedback=['dependency']` declares that the operator found that lens unhelpful; it defers that lens without rewriting the original evidence. `policy='source_first'` ranks inspections by how many typed source-grounded questions they may expose. `policy='sequential'` uses the fixed dependency/tension/affordance order. Both are explicit classical policies, not model-learned judgment.

**Non-inference:** An unresolved requirement does not prove the associated idea is impossible. A contradiction link does not automatically refute the association. An absent edge does not mean the relationship is false. Even if all lenses agree, they share one authored graph—**not multiple independent witnesses**. No externally validated truth or PEN admission follows.

## Executed fictional specimen

- Original **association pencil**: could fictional `food` and `meal` be related? Four declared association edges support a common-neighbor candidate through `storage` and `volunteers`.
- **Dependency** adds two verification questions: a `van` and an `open venue` are listed as requirements. They have NOT been proven satisfied.
- **Tension** adds a question about an `open venue` vs `closed venue` contradiction. A separate, irrelevant disagreement about the word `home` is correctly excluded from this local cut.
- **Affordance** asks whether the declared `volunteers enables meal` relationship really works, including unresolved requirements.
- Total: **one initial pencil question, four further held questions**. A separate 010-facing CLI test demonstrates that *a single operator* can create an unsourced pencil seed without inventing independent evidence. The engine constructs three actual geometric projections when enabled, retaining identical source and identities throughout.
- A *source-only, no-map comprehensive comparator produces the same five questions*. Thus this is a question-management and representational workflow demonstration, **not an increase in intrinsic answer accuracy**.

## Security, provenance and implementation limits

- `AUTHORED` is input attribution, not verified truth; roots are unauthenticated strings.
- `HYPOTHESIS_ONLY` source edges never become witness relations. View positions cannot create a relation or a novel fact.
- The original THOUGHT-007 field is read-only, and no false identity merge is allowed. The two `Home` interpretations stay separate even with identical labels.
- Each step receipt hashes sequence, source digest, question inventory, reported witnesses, projection *display-only digest*, and prior receipt. SHA-256 is an integrity fingerprint, not a signature or proof of source authenticity.
- `resume` rejects stale sources and altered untrusted receipts, but cannot detect a complete malicious rewrite without a separately trusted head.
- This isolated experiment is **not** a live multiuser thinking service; questions are finite templates, not open-language understanding; routing does not learn; no PII, network, subprocess, message dispatch or third-party source imports.
- A `start(max_steps=0)` baseline stays at one association question. Three-lens inspection sees additional issues, but a matched *comprehensive no-map inspection* sees precisely the same issues at zero display cost. Do not claim better correctness or performance.

## Reproduce

From the repository:

```bash
cd experiments/thought-012
python -m unittest -v test_cross_lens.py
python benchmark.py
python demo.py
```

`demo.py` outputs `cross-lens-inquiry.svg`, `cross-lens-inquiry.json`, `demo-results.json`. The demo's concept and scene are **fictional synthetic fixture data**. Source graph and pen status remain unchanged. All development cases were designed with the engine; real-world performance is unknown.

## Next falsifiable trial

Freeze an unseen set of genuinely tricky interpretation tasks *before modifying policies*: tasks with misleading spatial closeness, implicit contradictions, unrelated tension, ambiguous labels, missing prerequisites and spurious root independence. Compare (A) fixed association lens, (B) source-only comprehensive analyst, (C) task-budgeted rotation, and (D) human-selected rotation with equal question/display cost; independent reviewers should judge useful novel questions, false implication rate, decision quality and time-to-answer. Keep no-map as default if rotation offers no measured advantage.

## Integration door

`cross_lens_door.py` is an **actual executable local, private, opt-in JSON CLI** that uses THOUGHT-010's existing strict request validator and idea-to-manifestation engine. Its caller explicitly supplies two **index IDs**, preserving duplicate-label non-fungibility. It never sends, stores, exports or admits data; its response remains `HOLD_FOR_OPERATOR_REVIEW`. One operator may sketch a question, but all their authored links have one declared root and are **not** considered independent sources.

A separate JAR;VIS Thought Room patch may eventually pin this code and expose an explicit **Cross-check these two ideas** button. This MOTIF PR alone does not change or deploy the JAR;VIS application.
