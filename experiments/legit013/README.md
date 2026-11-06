# MOTIF LEGIT-013 — The Self-Improvement Examiner

**Status: research HOLD, stacked draft only. No production promotion.**

## What actually happened

LEGIT-013 opens MOTIF's **real, previously generated** DAG search source from LEGIT-012 (`generated/search_dag_v3.py`), checks the pinned SHA-256, executes it on 32 synthetic training graphs, and profiles its intermediate bitset transitions.

An examiner then attempts to generate a shorter reasoning step using a small, **predefined six-condition/four-expression DSL**. It proposes hypotheses that fit observed training cases. A *real third-party Z3 SMT solver* challenges the hypotheses over arbitrary 152-bit candidate and evidence masks.

**Two incorrect hypotheses received genuine Z3 SAT counterexamples.** Those exact bitvector counterexamples entered the candidate learner. The two eventually accepted shortcuts passed Z3 UNSAT proof checks at widths 8, 152 and 256:

```python
if parent_mask == ALL_CANDIDATES:
    result = evidence_mask
elif parent_mask == 0:
    result = 0
else:
    result = parent_mask & evidence_mask
```

This is standard Boolean algebra, not a newly discovered law. The source transformer produced real new Python and executed it after exact source-template checking and mandatory Z3 proof.

A separate Z3 invocation also proves that the child survivor set cannot gain members outside either its parent or newly observed evidence, and that the zero/full fast paths preserve intersection semantics. The Boolean recurrence yields a structural induction argument across well-formed, topologically ordered evidence DAGs.

**The external formal prover is genuine.** The specifications and proof obligations are authored here; the work is not a third-party-blinded independent scientific validation.

## Source and proof artifacts

- `generated/optimized_search_v4.py` — actual generated Python recorded from green GitHub Actions.
- `generated/formal_certificate.json` — Z3 version, accepted guarded rewrites, two actual rejected hypotheses and finite proof receipt.
- `examiner.py` — reads the real previous generated source, profiles it, proposes rules, refines them from counterexamples, emits and rechecks the new source.
- `formal_oracle.py` — separate third-party Z3 proof interface; no fallback to unverified logic when Z3 is absent or inconclusive.
- `classical_control.py` — conventional independent classical comparison, including an optimized hand-coded zero/full-absorbing DP, not just an intentionally weak baseline.
- `benchmark.py` — unseen seeded graph tests and five-run timing per solver.

## Results from an actual Actions run

32 synthetic training graphs produced **24,904 observed transitions**. The profiler identified **509** full-parent cases and **9** empty-parent cases. The examiner emitted two Z3-proven rules.

Across **80 separately seeded synthetic held-out graphs**, all **116,966** graph-state outputs agreed with the previous solver and both classical implementations. The complete **6,561-state** Boolean evidence lattice was separately checked.

| Measured operation | Count |
| --- | ---: |
| Previous LEGIT-012 bitset intersections | 116,886 |
| **MOTIF's generated rewrite** | **115,513** |
| Strong hand-optimized classical DP | 115,515 |
| Generated branch skips | 1,373 |
| Strong classical branch skips | 1,371 |

The tiny two-intersection difference relative to the optimized conventional implementation is caused by different choices of a valid parent path; it is not an algorithmic superiority result.

An exploratory GitHub Actions timing on a single runner (medians over five batches of the same held-out graphs):

| Solver | Median batch duration |
| --- | ---: |
| Previously generated DAG solver | **161.55 ms** |
| **New Z3-proven generated solver** | **164.72 ms** |
| Strong hand-optimized classical DP | 177.14 ms |
| Unoptimized conventional DP | 176.08 ms |

**The generated rewrite was actually slightly slower than its immediate predecessor on this runner.** It did fewer primitive intersections, but adds branch checks. This is an important negative result: fewer operations do not automatically improve total runtime. These small timings do not establish statistically significant or transferable differences.

All observed output agreements and proofs are bounded to the declared Boolean input and graph contracts. The strong classical comparator provides the same basic optimization. We do **not** claim MOTIF surpassed optimized classical reasoning.

## Reproduce

The dedicated GitHub Actions job installs `z3-solver==4.16.0.0` (full-provenance release) and runs:

```bash
python -m unittest discover -s experiments/legit013 -p 'test_*.py' -v
python experiments/legit013/benchmark.py --emit
```

It archives the generated source, formal receipt, counterexamples, and the separate benchmark data. Additional tests ensure committed source and proof artifacts match a fresh regeneration and independent Z3 re-verification.

## Key limits and next milestone

1. The source-transformation language, trust boundary and performance objective were designed by the project—not independently learned.
2. Z3 certifies the **encoded bitvector identities**; it does not certify all Python execution behaviors or arbitrary algorithms.
3. The generated Python is restricted to exact known templates. The in-process execution environment is not a general sandbox.
4. Training and held-out graphs are seeded researcher-authored synthetic cases, not a third-party challenge.
5. The current optimization does **not** show runtime improvement over the immediate predecessor.
6. No user source identity, real-world witness record, live automation, server, GitHub branch, or production deployment was modified by generated code.
7. The draft remains unmerged and must undergo independent review before any integration.

**Next research frontier:** force the examiner to learn *where* algorithmic work is costly on independently authored tasks, distinguish a statistically reliable improvement from false microbenchmarks, and extend the proof system to verified global branch dominance, certificate reuse or factored dynamic programming. A known strong classical portfolio—not an easy baseline—must be the comparator.