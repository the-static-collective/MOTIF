# MOTIF CONTROL-FLOW-GROWTH-001 — From a missing loop depth to executable syntax

**Status:** synthetic, local experiment, stacked on `OPERATOR-INVENTION-001`. Its results are not evidence of human-level, unrestricted algorithm invention, a mathematically novel theorem, a secure execution sandbox, or a self-deploying agent.

## Research question

Can MOTIF diagnose that the fixed one/two-loop grammar of `OPERATOR-INVENTION-001` is insufficient for a **new** graph measurement, apply a *generic syntax-tree transformation* to expand the grammar, construct a fitting program, verify it against unseen examples and a strong conventional baseline, and execute the generated source in another Python interpreter?

We chose the change in the number of **simple five-vertex cycles** after adding an absent edge. This was not the target of the previous operator experiment. Each new five-cycle corresponds to one simple length-four path between the endpoints of the proposed edge. The oracle measures five-cycles by counting unordered 5-vertex subsets and canonical cyclic permutations—not by executing the target path-counting algorithm. A separate handwritten DFS counts simple length-four paths **only for evaluation**.

## What the program was permitted to construct

The existing predecessor grammar has 62 candidate programs with at most two loop binders. It is tested **first** against graph interventions; the surviving version space becomes empty after 10 witnessed synthetic cases. That's an observed failure of **that finite grammar**, not proof of mathematical impossibility.

A researcher supplied the **generic** AST productions `ForEach(variable, body)`, `IfEdges(conjunction, body)` and `Increment()`, plus a depth cap, typed edge tests, and a distinct-vertex guard. No candidate named `five_cycle` or `four_edge_path` is offered. The extension uses a generic recursive `ForEach` wrapping transformation to create a *third loop*, then enumerates connected, four-edge tree predicates over `a,b,x,y,z`. Programs equivalent under renaming `x,y,z` collapse to the same canonical candidate. This produces **52** candidate three-binder programs, including intentionally incorrect trees and non-distinct walks. The search remains finite and purpose-designed for simple graphs.

The learner selects graph probes by disagreement among candidate outputs **without reading the answers in advance**. It reveals the target oracle after choosing a probe, filters the candidates, then freezes a surviving expression and checks an independent validation split. Further `test` and `ood` graph cases are not supplied to the synthesizer. Counterexamples lead to HOLD rather than quiet retuning.

## Measured local result

| Measure | Outcome |
| --- | --- |
| Previous source-operator candidates | 62 |
| Observations to falsify prior finite grammar | 10 |
| Composed third-loop candidates | 52 |
| New selected training interventions | 3 |
| Held-out graphs | **24/24**, all checked by AST, emitted Python, and separate DFS |
| Larger OOD graphs | **20/20**, all three implementations agree |
| Random 3-query selections, same grammar | 3/12 validation successes |
| Random 8-query selections, same grammar | 7/12 validation successes |
| A third loop disallowed | `HOLD_MAX_LOOP_DEPTH_BELOW_NEEDED` |
| All-distinctness guard disallowed | `HOLD_NO_COMPOSABLE_PROGRAM` |
| Tampered validation measurements | `HOLD_VALIDATION_COUNTEREXAMPLE` |
| Generated child in fresh interpreter | `F_LOCAL_CHILD_REPLAY` |

The inferred AST corresponds to a legitimate length-four simple path count, implemented as **three nested Python `for` loops** and a conjunctive edge predicate. The compiler derives that source from compositional AST nodes: its source is not a static prewritten triple-loop solution. The strong handwritten DFS matches every outcome; the generated solution does **not** outperform the classical algorithm. These test and OOD sets share the graph-generating rules and task mathematics. Random-search results cover only 12 random seeds and should not be generalized into broad active-learning superiority.

There is an important accounting distinction: **10** preliminary probes established that the existing grammar was insufficient. The subsequently **3** selected probes fit the extended grammar. Validation used a separate 24-example split. The prototype does not yet reuse preliminary evidence in the extended search, so these are 13 *training probe calls* across two phases, not necessarily 13 unique graph IDs (some inputs were reconsidered in the new phase). This is an explicit research limitation rather than the most resource-efficient possible strategy.

## Run

From the full stacked checkout, Python 3.11+ standard library:

```bash
cd experiments/controlflow001
python -m unittest -v test_controlflow.py
python controlflow.py
python benchmark.py
```

The dedicated workflow also reruns directly relevant FIR / MATHAL / graph / source-program regressions before exercising the new experiment. **36** targeted tests check the mathematical oracle against independent DFS, first-order grammatical failure, actual recursive AST shape, source emission, adversarial corruption, primitive ablations, split leakage, vertex renaming, mutable-source tampering, source hashing, refusal on copied/linked files, and independent generated-child execution.

## Epistemic and operational limits

- This is synthesis in an author-written grammar. A human authored `ForEach`, `IfEdges`, `Increment`, the distinctness condition, depth cap, and the graph transition oracle. MOTIF selected a *composition*; it did **not** invent the semantics of iteration or arbitrary control flow.
- A generated subprocess is **not** a security sandbox. Only a trusted local checked-out repository is used. SHA-256 pins detect byte changes, not author/source authenticity. Unlisted transitives may exist.
- The generated program is not installed, registered as a production cartridge, or deployed. It writes only to an expressly selected local child-output folder. This draft PR does not modify `main` or grant the child GitHub write authority.
- Held-out matches are `F_LOCAL` computational replay; all general or physical-world extrapolations remain `I` proposals.

## The next useful question

Can MOTIF distinguish **insufficient evidence**, **a missing compositional operator**, **an inaccurate observation model**, and **a genuine need for a new program primitive**—before changing its language? A stronger experiment should include multiple unrelated tasks and evaluate the **value and complexity cost** of a proposed grammar change, not merely show that deeper loops solve longer paths.
