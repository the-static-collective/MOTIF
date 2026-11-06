# MOTIF-LEGIT-012: Certified Search-DAG Transformer

**Status:** draft experimental branch. Research HOLD; not production.

## What was executed

LEGIT-012 reads and SHA-256 checks MOTIF's *actual* previously generated LEGIT-011 Python search source at `experiments/legit011/generated/search_v2.py`. The source's `build_index`, `choose`, and incremental `BitAnd` are inspected. The original catalog of 152 independently verified candidate methods remains intact.

A 24-choice typed transformation grammar proposes new search implementations. An independently implemented classical scanner supplies counterexamples. After **four counterexamples**, the source generator selected:

`JOIN=AND; MODE=REUSE_PARENT; PICK=FIRST; EMPTY=HOLD`.

It emits executable Python that caches each partial evidence state's surviving-program bitset and computes a child by intersecting one parent's result with its one new evidence constraint. The resulting source is saved in `generated/search_dag_v3.py`, with an inspectable proof packet at `generated/search_dag_proof.json`.

This is source-level algorithm transformation with a fixed template compiler, not free-form software self-modification. Generated code executes only after exact template matching and separate finite semantic verification.

## Complete bounded correctness check

The independent verifier enumerated all **3^8 = 6,561** possible partial truth assignments over eight Boolean rows. Their lattice contains **34,992** one-observation parent edges, including multi-parent joins. The generated solver matches BOTH independently written conventional linear scanning and classical indexed dynamic programming on every state.

The membership recurrence is `survives(child) = survives(parent) AND matches(new observation)`. The local transition has a four-case Boolean truth-table check. Structural induction on the topologically validated DAG justifies the recurrence within its stated assumptions; independent code also checks multi-parent agreement.

This is a finite verification plus an induction argument, **not** external SAT/SMT or proof-assistant certification.

## Held-out seeded synthetic graph benchmark

80 test DAGs, light/medium/dense; **97,659** state outputs correct, including **97,579** incremental updates. Every one matches optimized conventional memoized DP, with precisely **97,579** bitset updates in both.

The earlier full-scan algorithm used **4,276,425 candidate/row comparisons**. Those comparisons are different work units from bitset intersections; their ratio is not an algorithmic speedup.

Exploratory single-runner medians across five repeated batches of all 80 graphs:

| Implementation | Median |
| --- | ---: |
| Previous conventional full scan | 375.13 ms |
| **MOTIF-generated DAG solver** | **108.06 ms** |
| Strong conventional cached DAG DP | 115.75 ms |

The strong classical comparator amortizes index creation over the same batch. Its bitset operation count matches the generated source exactly. Source generation and verification costs are separate; these timings do not establish a statistically replicated or general efficiency advantage.

## Reproduce

```bash
python -m unittest discover -s experiments/legit012 -p 'test_*.py' -v
python experiments/legit012/benchmark.py --emit
```

The branch contains independent reference implementations, generated source, counterexample transcript, finite proof, held-out measurements and adversarial mutation tests. A dedicated CI job archives the actual results.

## Boundaries and next gate

This is a hand-designed typed language for evidence-filtering DAGs, with training and tests authored by the assistant. It is not independent blinded evaluation or an arbitrary graph solver. No third-party formal prover, novel mathematical primitive, automatically promoted production code, or verified real-world source authentication is claimed.

A genuinely harder next test would explore dominance pruning, partial evaluation, and reusable proof certificates under external SMT/proof-assistant checking, with independently sourced tasks and resource-matched optimized classical solvers.