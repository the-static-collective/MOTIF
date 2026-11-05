# LAW-FORGE-002 — Verified first experimental results

**Run date:** 2026-11-05.  
**Source:** [GitHub Actions: MOTIF Law Forge 002 run 9](https://github.com/the-static-collective/MOTIF/actions/runs/42074217654), on commit `12f4966e0bc5709d77e59825b03e5677d6b6a60d`.  
**CI:** success — inherited LAW-FORGE-001 **14 tests**, constructor experiment **18 tests**, benchmark JSON generated and validated; original complete `law-forge-002-receipt` stored as workflow artifact (30-day retention).

## Development: five handcrafted families × two seeds (10 simulations)

| Predeclared method | Independently review-eligible | HELD | New constructor proposals | Local probes | Covered test cases | Wrong covered predictions |
|---|---:|---:|---:|---:|---:|---:|
| Old grammar only | 2/10 | 8/10 | 0 | 0 | 32 | 0 |
| Fixed classical diagnostic | 6/10 | 4/10 | 8 | 8 | 96 | 0 |
| Adaptive information-gain diagnostic | 6/10 | 4/10 | 8 | 8 | 96 | 0 |

## Frozen separate evaluation: same five families × five unused seeds (25 simulations)

| Predeclared method | Independently review-eligible | HELD | New constructor proposals | Local probes | Covered test cases | Wrong covered predictions |
|---|---:|---:|---:|---:|---:|---:|
| Old grammar only | 5/25 | 20/25 | 0 | 0 | 80 | 0 |
| Fixed classical diagnostic | 15/25 | 10/25 | 20 | 20 | 240 | 0 |
| Adaptive information-gain diagnostic | 15/25 | 10/25 | 20 | 20 | 240 | 0 |

**Result:** the expanded feature-program grammar improves *review-eligible coverage on these toy worlds*, compared with the old single-lag grammar. **Adaptive questioning provides no measured advantage over the fixed, strong classical inquiry**: same local probe counts and outcomes. Explicit method decision: `NO_METHOD_PROMOTION`.

For the composite-grammar methods, the extra 10 HELD worlds consist of **five hidden-two-tick mechanisms** and **five deliberate distribution shifts**. The 20 constructor proposals include **10 later rejected by independent review**; a proposal is not a successful discovery. The immediate current-only world retains the original grammar without any probe.

**Important selection caveat:** wrong predictions are counted *only where prediction was independently review-eligible*. The 10 HELD evaluation worlds have zero coverage, not certified correctness. The old grammar's 20 HELD cases likewise are not solved. The total sample is 25 procedural repetitions of **five** hand-designed hidden mechanisms, not 25 independent scientific domains.

## What the experiment actually accomplished

1. Created read-only, portable **feature-program ASTs** from known primitive Boolean operations (`AND`, `OR`, `XOR`) and lagged input selectors, with no world-rule labels supplied to the learner.
2. Rejected the original individually lagged feature grammar when historical observations contradicted it.
3. Probed a previously unseen two-port history setting to distinguish the `OR` and `XOR` constructors.
4. Independently reviewed each proposal on two-tick, 16-cell evaluator partitions; retained explicit falsifications and abstention.
5. Validated that a destination with the same mechanism but renamed ports is re-reviewed, while a different hidden mechanism rejects the source proposal.
6. Rejected schema/authority escalation, arbitrary source execution, malformed data, incomplete review and tampered cartridge identifiers in the adversarial test suite.

## Unresolved frontier

**No new primitive operator was invented.** The synthesizer combines previously supplied generic operations. This experiment cannot demonstrate general causal science, unrestricted source discovery, continuous autonomous learning, open-ended code synthesis, arbitrary GRAFT adapter creation or real-world permissions. It does establish an inspectable composition-and-falsification layer to challenge further.

The prior first CI attempt failed from a local Python import-path collision between the stacked experiments; the imports were corrected and the cited later full run passed. That debugging fix is part of the implementation history, not evidence about the learning algorithm.

**Next controlled falsifier:** freeze the existing operation set, introduce an independently authored relational, delayed or continuous-valued world family *not implementable by the current AST*, then require the learner to propose a genuinely new **operator definition** rather than recombine familiar primitives. Do not change the hidden evaluator to make the test pass after inspecting its held-out labels.
