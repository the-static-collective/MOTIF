# LAW-FORGE-003 — First measured operator-foundry trial

**Date:** November 5, 2026  
**Source commit:** `f1093faae90573b1c41b5a26af734ccdb0364f99`  
**GitHub Actions:** [Dedicated Law Forge 003 operator-foundry run](https://github.com/the-static-collective/MOTIF/actions/runs/42075801190). Dedicated run passed, including **14 inherited LAW-FORGE-001**, **18 inherited LAW-FORGE-002**, and **16 new LAW-FORGE-003** adversarial tests (48 tests total), synthetic benchmark receipt generation, and artifact upload.

The full `law-forge-003-results.json` workflow artifact is available for 30 days. This markdown retains the summary beyond artifact expiry.

## New executable capability — NAND-only operator circuit

The learner's program library contains **only NAND** as the logic primitive, plus input wire indices and an externally supplied left-fold interpreter. A deterministic exhaustive search constructed and verified:

- **Four-gate XOR** netlist, no named XOR instruction supplied to the constructor:
  ```json
  {"primitive":"NAND","wires":2,"gates":[[0,1],[0,2],[1,2],[3,4]],"output_pin":0}
  ```
  Computing the output from the final wire gives `0,1,1,0` on ordered pairs `00,01,10,11`.
- **Three-gate OR**, independently derived from the same NAND-only search.
- **Two-gate AND**, independently derived from the same NAND-only search.

The interpreter executed the resulting circuit over held-out longer binary sequences. These circuits implement known Boolean functions; the novelty is the evidence-guided **circuit construction workflow within our experimental stack**, not an invented mathematical primitive.

## Predeclared development stage: seven families × two seeds

| Method | Review-eligible worlds | Held worlds | Local queries | Held-out predictions covered | Wrong covered |
| --- | ---: | ---: | ---: | ---: | ---: |
| NAND synthesis + adaptive query | **6/14** | 8 | 14 | 537 | 0 |
| NAND synthesis + fixed classical query | **6/14** | 8 | 14 | 537 | 0 |
| Direct classical truth-table + fixed query | **6/14** | 8 | 14 | 537 | 0 |

## Separate final evaluation: seven families × five unused seeds

| Method | Review-eligible worlds | Held worlds | Local queries | Held-out predictions covered | Wrong covered |
| --- | ---: | ---: | ---: | ---: | ---: |
| NAND synthesis + adaptive query | **15/35** | 20 | 35 | 1,329 | 0 |
| NAND synthesis + fixed classical query | **15/35** | 20 | 35 | 1,329 | 0 |
| Direct classical truth-table + fixed query | **15/35** | 20 | 35 | 1,329 | 0 |

All three methods spent identical declared local probe cost: 42 units during development and 105 during final evaluation. All trained operator proposals remained merely `PROPOSAL_ONLY` until separate synthetic review. **Only three of seven mechanism families passed review**: parity, any-on, all-on. Four failed under independently sampled length/phase stress: exactly-one, majority, hidden-width effect, deliberate phase shift. The 20 held final-evaluation worlds made **zero approved test predictions**, not 100% correct predictions.

## Method-selection result

`NO_METHOD_PROMOTION`.

NAND circuit synthesis ties an ordinary classical truth-table fold baseline under equal query budget. Its contribution is an executable **physical-gate-style network representation** that is auditable and transferable after review, not improved predictive accuracy or better question selection. A four-gate NAND circuit may be less computationally efficient than a classical Boolean truth table; no reliable physical Joules or hardware timings were measured.

The result is a **finite, researcher-authored synthetic exercise**. Five seeds per mechanism vary evaluation sequences; they do not create independent scientific domains. No real sensor, real GRAFT executable adapter, autonomous code deployment, online discovery, third-party permission, new memory primitive, safety-critical inference, or general causal-science competence was demonstrated.

## Integrity and provenance

- Source-separated evaluator `world.py` owns hidden mechanisms, receives typed local query packets and generates review/test evidence.
- Researcher `foundry.py` has no import of hidden rule names, has strict NAND-only gate validation, cannot execute arbitrary code and cannot dispatch a query.
- Training and at most one synthetic query are the only inputs to circuit selection; review and test labels never update hypotheses.
- `Operator.from_packet()` checks schema, wire bounds, Boolean signatures, netlist consistency, content hash and `real_world_authority=false`.
- Source checksum identifies content but **does not authenticate a witness**. A destination re-reviews even a matching circuit and rejects a mismatched hidden rule.

**Next genuine vertical:** freeze this operator language, then present an independently authored domain requiring an unprovided computation primitive, such as temporal state, variable arity, or graph edges. The next experiment must test whether the system invents a new *operator definition mechanism*, rather than simply enumerating known NAND functions. If it cannot, preserving that failure is the correct result.
