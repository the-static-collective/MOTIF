# MOTIF — SEMANTIC-ADAPTER-001: A connection that preserves meaning

**Status:** executable, bounded synthetic research; no generic natural-language interpretation, no independent world-grounding, no autonomous mainline edits, no real-world actions.

## Research question

> Can MOTIF infer a missing bridge from the executable behavior of existing modules, rather than being handed examples of what the target `Move` records should be—and can it detect type-preserving semantic shifts?

This experiment extends the stacked **ADAPTER-INVENTION-001**. It still composes actual **MOTIF-003** action dictionaries into actual **SELF-MIRROR-001** `Move` dataclasses and calls the real downstream policy. Unlike 001, it does **not consume manually labeled Move targets**. Instead, it runs a fixed family of controlled synthetic graph worlds through the upstream module, then independently re-evaluates *declared behavioral invariants* to derive the target fields. The resulting five formulas are selected from the 001 finite expression grammar and frozen before testing.

### Behavioral semantics, not just shape

- `immediate` = difference in the **declared synthetic utility** before/after a move.
- `affordances` = number of **newly available synthetic action identities** after the rewrite, independently reconstructed from the action relation.
- `reach` = independently enumerated, bounded **distinct possible future worlds**; truncated search is preserved.
- `name` = source operator plus bound roles, with unique identities.
- `truncated` = whether the supplied bounded simulation reached its declared search cap.

A runnable, fixed-template child is written in an explicit staging folder. It pins exact file bytes across the source, target, prior synthesizer, mathal prerequisites, and this experiment; it then imports real MOTIF modules in a separate interpreter and checks a held-out synthetic probe. The child **is not a secure sandbox** and does not run arbitrary generated Python code.

### Run

From a full checkout of this stacked experiment branch:

```bash
cd experiments/semanticadapter001
python -m unittest -v test_semanticadapter.py
python semanticadapter.py
python benchmark.py
```

Python 3.10+, standard library. The test suite includes actual source imports, independent BFS, hypothesis fitting and abstention, target semantics, generated child execution, source drift, and adversarial schema-preserving field swaps. The GitHub workflow also runs all prerequisite stacked suites.

### Why this matters

A purely typed field adapter can silently accept a source that swaps `immediate_delta` and `reachable_after_first_move`; both are valid integers. The behavioral gate replays the proposed action against its declared synthetic world and detects that contradiction. This is **validation against a supplied semantics**, not a proof that the supplied semantics describes the physical world.

### Crucial limitations and stronger controls

- The list of candidate transforms is inherited from the manually written finite 001 grammar. The behavioral expectations and task utility are manually declared. Thus this is **not unsupervised discovery of semantics**, nor invention of a general new algorithm.
- The existing handwritten `SELF-MIRROR-001` bridge is the strong control for correct synthetic outputs. Our proposal is expected to **tie**, not outperform it on unmodified fixtures.
- Train, validation and held-out worlds use the **same toy simulator family** with different declared marker nodes. They test frozen replay and certain controlled interventions, **not transfer to an unrelated environment**.
- Some numerical swaps cannot be detected if the numbers happen to be equal. Negative reach values are caught by type checks; those cases are not counted as novel semantic detections.
- The independent checker uses the same authored transition and utility definitions, although its search implementation is separate. **Common-mode bugs can fool both source and checker**. Source hashes detect mutation, not authorship or correctness.
- A generated subprocess is *not* isolation from adversarial trusted Python dependencies. No arbitrary tool invocations, internet, external writes, auto merge, or deployment are authorized.
- Passing finite fixtures justifies `F_LOCAL_FINITE_REPLAY` for exact checks, while the adapter's overall epistemic status remains **`I_SYNTHESIZED_BEHAVIORAL_CONTRACT`**. No real-world truth claim is promoted.

## Next question

Can MOTIF recover semantic constraints from truly different module families and independently grounded interventions, with fewer manually declared invariants? Compare against classical synthesis and property-based testing. A failure on an unseen family should be retained rather than interpreted as success.

**Stack ancestry:** new branch based on `experiment/adapter-invention-001-20261108`, which itself depends on the unmerged SELF-ASSEMBLY, NEXT-STEP and nunuMATH PRs.
