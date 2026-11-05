# REASON-CARTRIDGE-004 — THE SELF-OBJECTING REASONER

**Status:** bounded synthetic experiment, draft review branch stacked on REASON-003 PR #77, itself on #73 and #70. It is not a production intelligence, real-world fact verifier, or grant of external operating authority.

## What changed

A normal classical proof tells us what follows **if the premises are true**. The self-objecting reasoner makes the dependence operational:

- A **positive proof** carries a shortest confirmed path *and* a minimum cut of confirmed edges whose justified retraction would invalidate all currently supported paths. Retracting evidence alone is **not** a proof that no path exists.
- A **negative proof** requires an explicitly complete finite edge universe and a checkable cut, then names a *least-premise-revision counterfactual route*. If no route is available even when every in-scope edge is allowed, only **changing the source scope** could overturn the negative conclusion.
- An **unknown** answer carries a source-owned information-value ranking and up to two hypothetical futures. These branches say what would follow **if** a fresh observation really arrived. They do not pretend the observation happened.
- **Contradictory witnesses** require local human review; another unreviewed vote cannot silently settle the dispute.
- **Open worlds** cannot yield negative proofs merely from a missing edge.
- A question whose modeled expected benefit is below its explicitly declared inquiry cost is not automatically asked.

Each output is a strict, replayable **`motif.reason.self-objecting-cartridge.v1`**. The packet includes its source-revision marker, actual source evidence ledger, source-content digest, declared assumed completeness, proof certificate if any, counterexample procedure, potential futures, and explicit no-authority declarations.

## Reuse without source laundering

The code loads the existing owner implementation in `experiments/reason-cartridge-003/objection.py` only after checking its **exact Git blob SHA** (`063e8a0839d41fcadfb5ad1cc3510be63bce725a`). It does not rewrite its results or silently substitute a new source. A content SHA identifies bytes, not authenticates a witness or grants permissions.

Packets are **recomputed** from the original structured inquiry on import, so rehashing a forged result, future or proof does not make it acceptable. A receiving organ must independently review all four epistemic statuses, bind an explicit `ADMIT_READ_ONLY` decision to that review, and may only suggest the resulting proposal.

No automatic web search, emails, database writes, human evidence adjudications, or physical actions are supported.

## Preregistered synthetic demonstration

The independent evaluator builds a four-node graph with two unknown edges:

- `S→B` is irrelevant because `B→T` is known absent.
- `A→T` is consequential because `S→A` is known present.

The source-owner question planner, with an explicit uniform-world assumption and declared asymmetric mistake costs, proposes **`A→T`**.

Four independently specified synthetic worlds (both outcomes of each unknown edge) give the following expected results:

| Controller | Average additional source observations | Correct final status |
|---|---:|---:|
| Consequence-ranked single question | **1** | 4/4 |
| Weak fixed source-declaration-order query baseline | 2 | 4/4 |
| Fully informed classical model | 0 (already knows all hidden edges) | 4/4 |

The optimal decision-aware classical active learner could match the consequence-ranked algorithm. We do **not** claim a new theorem, strong generalization, or superiority over classical Bayesian decision theory. This test measures a *useful interface* for choosing questions under missing information, compared with a deliberately weak fixed-order control. Probabilities and costs are explicitly hypothetical and not real risk estimates.

## Hostile validation / falsifiers

Unit tests explicitly attempt to alter the claimed conclusion, modify its refutation recipe, change a completeness assumption while recomputing the packet SHA, overwrite a witness, merge contradictory claims, and skip independent receiver review. They must fail/HOLD.

A future test should use **external source-owned evidence** rather than a complete synthetic graph. The key falsifier is whether an objecting cartridge yields a measurable improvement in correction time, calibrated abstention, or useful independent observations compared with strong matched classical active-learning and proof-repair algorithms.

## Reproduce

```sh
python -m unittest discover -s experiments/reason-cartridge-004 -p 'test_*.py' -v
python experiments/reason-cartridge-004/trial.py
```

Run the GitHub Actions `reason-cartridge-004.yml` workflow for inherited regression, experiment tests, independent receiver review, synthetic benchmark assertions, and an inspectable JSON receipt artifact.

**Limitations:** finite symbolic graph world, developer-authored source/grammar and prior, no causal claim about the external world, no authenticated real-world witnessing, no automatic dynamic sensor invention, no runtime GRAFT or live agent integration. Source-owned truth and local human review still govern all promotions.
