# LAW-FORGE-004 — Verified Grammar Breaker results

**Date:** November 5, 2026.  
**Verified dedicated CI:** [Law Forge 004 — Grammar Breaker, run #7](https://github.com/the-static-collective/MOTIF/actions/runs/42078853228), source commit `bf6dca08fb7e9fc518d20b03e5aff811231f6186`.  
**Checks:** All **64 tests passed** across four inherited/current experimental suites (14 + 18 + 16 + 16). Source-separate synthetic benchmark JSON was generated and validated; a complete workflow artifact `law-forge-004-receipt` was uploaded with 30-day retention.

An earlier run exposed a genuine review-coverage weakness: duplicate long observations could satisfy the reviewer when only length variety, not distinct samples, was checked. The reviewer now requires >=64 **different** sequences, including >=12 distinct sequences at each length 8–11. A new test with repeated, single-length examples verified the repair. Final CI passed.

## Predeclared development — eight authored families × two seeds (16 worlds)

| Method | Review-eligible | HELD | Membership queries | Covered withheld predictions | Wrong covered predictions |
|---|---:|---:|---:|---:|---:|
| One-bit scalar fold only | 4 | 12 | 496 | 3,120 | 0 |
| Proposed stateful grammar upgrade | **10** | 6 | 3,184 | 7,800 | 0 |
| Strong classical gated control | **10** | 6 | 3,184 | 7,800 | 0 |
| Full-table classical control | **10** | 6 | 4,080 | 7,800 | 0 |

## Separately frozen evaluation — same eight families × five unseen seeds (40 worlds)

| Method | Review-eligible | HELD | Membership queries | Covered withheld predictions | Wrong covered predictions |
|---|---:|---:|---:|---:|---:|
| One-bit scalar fold only | 10 | 30 | 1,240 | 7,872 | 0 |
| Proposed stateful grammar upgrade | **25** | 15 | 7,960 | 19,680 | 0 |
| Strong classical gated control | **25** | 15 | 7,960 | 19,680 | 0 |
| Full-table classical control | **25** | 15 | 10,200 | 19,680 | 0 |

The stateful method proposed **20 finite-state operator packets** across 40 worlds. **15 of those proposals were review-eligible**, while five nonstationary phase-shift proposals were independently falsified. The remaining positive 10 worlds (parity/any-on) retained the simpler scalar fold and needed only 31 synthetic observations each. The five-state hidden mechanism and prime-count challenge produced no approved new stateful machine.

**Held is not correct:** the 15 held worlds made zero authorized final-test predictions, not 100% correct predictions. No error measurement on abstained cases was converted to success.

### Actual executable state mechanism

The three-state pattern-detector machine inferred from typed observations (no evaluator rule labels) has transitions:

```json
{"transitions": [[1,0],[1,2],[1,0]],
 "start_state":0,
 "state_count":3}
```

The output bits and evidence checksum are preserved in the full JSON receipt. The `StateProgram.trace()` interpreter executes the discovered state transitions one event at a time and preserves the state across the word, allowing output only after the stream completes.

Separate four-state programs were inferred for a three-symbol suffix and an occurrence pattern. They passed independent long-stream review and final withheld tests in this small authored generator family.

### Method selection and provenance

`NO_METHOD_PROMOTION`: the proposed method **ties** the strong classical gated table learner in every predeclared metric. It uses fewer queries than an ungated classical full-table protocol only because it retains the known simpler fold when that already fits—an ordinary classical efficiency optimization, not evidence of novel AI inquiry.

The same four-state interpretation, maximum seven-symbol membership training horizon, binary event interface and classical residual-signature method were **supplied** to the learner. MOTIF inferred machine state partitions and transitions. It did **not** invent automata theory or new computational mathematics, nor acquire arbitrary code execution or real-world authority.

All experiments are *synthetic*, all generator worlds are hand-designed, and seeds vary samples rather than independently authored laws. Checksum identifies byte content, not a real person's signature or permission. Review-eligible prediction still requires human review before any integration. The draft branch is not merged and no external GRAFT, MCP, network or deployment service was modified.

### Next decisive question

Freeze the binary-stream finite-state interpreter. Present an independently authored world whose needed observations **cannot be expressed as finite binary words or four-state machines** (such as relational graph changes, dynamic resource identity, physical time). Can the system propose a new computational substrate with interpretable contracts and source-owned tests? If it cannot, preserve the non-identifiability as a failure rather than retrofitting the test fixture.
