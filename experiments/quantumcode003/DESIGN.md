# QC-003 — THE APERTURE THAT DID NOT EXIST IN THE LOCAL MODEL

**Research status:** deterministic synthetic experiment / classical graph rewriting / local-preview-only / no production installation.

## Source lineage

This experiment continues the user's "Quantum Code / it writes itself" research in [National Treasure's glyph-circuit case](https://github.com/the-static-collective/national-treasure/blob/main/cases/quantum-code-glyph-circuit/README.md) and the [Primal Overlap](https://github.com/the-static-collective/national-treasure/blob/main/cases/quantum-code-glyph-circuit/PRIMAL-OVERLAP.md) question: **what operation survives when domain-specific symbol meaning is removed?**

[Daily Slice: The Field Is Not the Message](https://github.com/the-static-collective/the-daily-slice/blob/main/slices/2026/08/2026-08-26/the-field-is-not-the-message.md) distinguishes field, path, glyph, meaning and authority. [The Secret Key Is the Decompressor](https://github.com/the-static-collective/the-daily-slice/blob/main/slices/2026/08/2026-08-27/022100-the-secret-key-is-the-decompressor.md) observes that representation alone cannot fix its realization. Those are sources of the **engineering analogy**, not evidence that graph rewrites are quantum phenomena.

- [QC-001 / PR #182](https://github.com/the-static-collective/MOTIF/pull/182) used predeclared named shape changes and decoder-specific lookup.
- [QC-002 / PR #185](https://github.com/the-static-collective/MOTIF/pull/185) inferred anonymous graph edits, but was given a **two-anchor aperture and opaque intervention cue** and could only create **one fresh vertex per primitive**.
- **QC-003** no longer supplies an action name, an intervention cue, or anchor roles in its **training records**. It derives changed anchors from the before/after graph delta, supports two-new-vertex effects, and discovers when a local observation alphabet cannot distinguish two source conditions. It then constructs and tests a *relational fixed-point observation*.

This is NOT the first learning, graph rewriting, planning, or macro induction ever performed by MOTIF; see MOTIF-002, -006 and LEGIT-021. It is a deliberately scoped complementary test.

## The question and precommitment

**Can a learner infer two genuinely different edge-local rewrite schemas and determine that the currently available local descriptors fail to select between them, so that it must add a well-typed new relational question?**

The frozen hidden evaluator is an ordinary classical graph function:

- If deleting an existing edge would **disconnect its endpoints**, RETAIN the edge and insert a second two-new-vertex path between its ends.
- If another path already connects its endpoints, REPLACE that edge with a two-new-vertex path.

The learner is **not** provided the names or meanings "bridge," "cycle," "retain," "replace," or "alternative path" as labels. It gets unlabeled simple undirected before/after graphs, and no action cue or target anchor in the episode schema. The evaluated truth function is kept separate from the learner.

The permitted structural grammar is nonetheless hard-coded: simple undirected graphs, exactly two inferable old boundary vertices, **one to three fresh vertices**, anchor-local edge edits, and an existing source edge. The learner cannot invent an arbitrary new type of graph transformation or rewrite Python source.

## Prevent the easy shortcut

TRAIN consists of **three source worlds**; each world supplies two demonstrations, one from a long cycle and one from a long tail attached to that same cycle. Each pair has:

- exactly the same *original graph*, so its size, global edge count, component count and parity match;
- the changed edge's endpoints of equal degree 2;
- no common neighbors;
- matching radius-two egonet vertex/edge counts;
- distinct vertex names and sizes across source worlds;
- two different **graph delta** outcomes.

VALIDATE uses two *larger* paired worlds and separate receipts. TEST uses four larger worlds, including a new chord and a second tail absent in training.

No feature search uses TEST data. The source records deliberately omit target anchors and operation labels. During evaluation, the **evaluator** can recover its own ground-truth changed edge from the held-out after-graph; at inference time the **learner must enumerate all possible edge rewrites**, not silently choose one it was told.

### Finite observation search

First attempt seven low-complexity descriptors: shared-neighbor count, endpoint degree pair, radius-two egonet vertex/edge counts, graph size parity, edge-count parity and pre-cut connectivity.

The training pair construction means **none can deterministically map a descriptor to the two different edit families**. When that happens, a bounded grammar lift proposes the composite expression:

    (original graph − candidate edge)
        → NEIGHBOR relation
        → repeatedly expand reachable set to FIXPOINT
        → CHECK whether opposite endpoint is reachable

That constructs a new **feature program in the tested feature vocabulary**. This is standard classical transitive closure, not a newly discovered mathematical law. Data determines whether to select it; the researcher supplied its constructors and allowed lift.

### Expected evidence

1. The learner induces **two** canonically normalized graph-edit templates with **two freshly added vertices** each. It discovers anchor roles via graph delta and is invariant to relabeling.
2. All seven local descriptors fail to distinguish the two effects. A finite closure feature separates them on TRAIN and is **independently verified** on VALIDATE.
3. In the **8 held-out episodes**, predict **8/8** correctly by enumerating all source-edge futures and checking the held-out target. For each test source graph, **all** eligible original edges must have predicted effects matching the oracle (no missed or falsely assigned alternatives).
4. A **separately implemented union-find** edge-deletion oracle predicts the same future effects; expect a classical tie, not a claimed advantage.
5. A **recursive self-change** occurs on a bridge edge: a first local graph transformation introduces an alternate path and turns the same old edge into a nonbridge; the feature program now selects the other learned rewrite. A two-step source-pinned macro must replay exactly, and changed sources or forged outcomes must HOLD.
6. Reject unverified provenance, duplicated IDs, cross-split ID reuse, nonlocal graph changes, too many new nodes, unsupported boundaries, status escalation, and a staged contradictory validation example.

**Negative result interpretation:** if the paired local descriptors can distinguish the outcomes, the demonstrated need for an enlarged aperture is false. If fixed-point relation cannot validate on the separate worlds, HOLD. If an ordinary union-find baseline wins or ties, admit it plainly. This is *not* proof of recursive general intelligence.

## Independent oracle and unavoidable information limits

The evaluator implements standard **union-find** to decide whether the old edge is a bridge. The feature learner independently implements a monotonically expanding **neighbor closure on the edge-deleted graph**. The two methods produce the same answer in this domain, which is a correctness check, **not independent physical evidence**.

The learner can infer the changed anchors during TRAIN because before/after pairs directly reveal the altered vertices and edges. But this does not solve causal attribution or hidden action discovery when multiple edits happen at once. At deployment without a cue, the learner emits *a set of possible local futures*, not a single asserted actual future. Exact target prediction would be unjustified because a human or actor might have selected any edge.

The feature compiler currently offers exactly **one new fixed-point generator** after local failure. Therefore it demonstrates a **specific data-driven representation lift within a researcher-authored typed DSL**, not open-ended invention of arbitrary primitives.

Witness checksums are local integrity values, **not digital signatures of true-world witnesses**. All graphs, action effects and receipts are authored synthetic fixtures. A passing CI job is not proof of production use. No external action, authority transfer, merge, quantum hardware, quantum speed-up, physical glyph phenomenon, or self-modifying executable code occurs.

## Reproduce

Requires only Python 3.10+ and the stacked QC-002 module.

    cd experiments/quantumcode003
    python -m unittest -v test_aperture.py
    python aperture.py

Dedicated GitHub Actions workflow: .github/workflows/quantum-code-003.yml.

## Next independent pressure

Replace the **single prescribed closure lift** with an enumerated space of safe typed relational programs (join, composition, bounded quantification, transitive closure, quotient/automorphism invariance) and explicitly enforce cost penalties; test which expression is selected on independently authored blind worlds with counterexamples engineered to defeat reachability. Compare with existing graph kernel, message-passing GNN and classical ILP/SyGuS methods under matched data/compute budgets. Preserve any failures, particularly unstable feature choice under domain shift.

**The witness is a feature program and an observed finite result—not a verdict about quantum physics.**
