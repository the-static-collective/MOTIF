# MOTIF — INVENTION-DIAGNOSIS-001: Ask why before changing yourself

**Status:** bounded, local, synthetic diagnostic controller. **Not** an autonomous self-modifying agent, independently authenticated science, a secure execution sandbox, or a general-purpose cause-of-failure classifier. Draft branch stacked on `experiment/control-flow-growth-001-20261109` and all preceding unmerged experiments.

## Research question

> Instead of always building a more complicated algorithm when MOTIF cannot answer a question, can it inspect what is known/unknown, ask and execute the **next relevant diagnostic question**, differentiate between insufficient evidence, corrupted observations, a computation budget, a missing program operator, and an unwarranted task definition, then show what happened—with an inspectable receipt?

The controller does **not** get fixture labels such as `corrupt_sensor` or `missing_control` as inputs. It sees typed observations, local tool state, a permitted question domain, and budget/authority constraints. It chooses one of a handful of **researcher-authored deterministic routes**, not an unrestricted learned causal policy.

## What it actually executes

All modules below are imported from the **real earlier MOTIF experiments**; they are not invented replacement algorithms.

| Observed symptom | Question automatically asked | Action performed | Conclusion within scope |
| --- | --- | --- | --- |
| Existing 62-program operator grammar has several plausible explanations | What next intervention best distinguishes the survivors? | Perform actual graph intervention, then frozen held-out validation | Use existing model if validated; no needless language growth |
| Real observation instruments disagree | Can the readings be reconciled? | Cross-check the two original implementations and preserve provenance | **HOLD**, cannot attribute which sensor is wrong |
| Installed loop program returns an actual `TRUNCATED` metered execution | Could authorized extra computation finish the same program? | Reproduce truncation, increase fuel within a declared cap, rerun, independently compare | Correct output without changing programming grammar |
| All 62 old operator programs contradict the five-cycle measurements, with agreeing local readouts | Does building a third-loop composition help? | Invoke actual `controlflow.discover`, run held-out and OOD tests, emit child and run it in another interpreter | Proposal for new local program, **never installed** |
| Both apparent witnesses claim the same root | Do we have two independent sources? | Reject the purported second witness | **HOLD**, copied reports are not corroboration |
| Measurement task's meaning not warranted | What is the intended quantity and who can establish it? | Stop automatically | **HOLD**, no silent invention of a new target |

Budget: cross-check / one added probe / frozen validation cost 1 each; bounded compute retry cost 2; grammar-growth research costs 4. These are **declared local accounting units**, not calibrated runtime/financial costs. Five-stage default maximum; no user-provided shell, repository mutations, external connector calls or remote execution.

### Evidence receipts

Each local action records `next_question`, `action_executed`, the measured or computed result, cost, remaining budget, source constraints and whether an actual external side effect occurred. Model claims stay conditional (`I`) even when finite arithmetic has been verified (`F_LOCAL`). A digest detects changes to the evidence object; it does **not** establish authenticity. Two graph algorithms are different code implementations but run on the **same synthetic graph**; their agreement cannot establish independent external truth.

## Reproduce

From a checked-out MOTIF branch containing the preceding stacked experiments (Python 3.11+, standard library):

```sh
cd experiments/inventiondiagnosis001
python -m unittest -v test_diagnosis.py
python diagnosis.py
python benchmark.py
```

Run the specified dedicated GitHub Actions workflow for upstream regressions and the newest suite. The prior `CONTROL-FLOW-GROWTH-001` child is a generated **Python program running in a separate interpreter**. This is not a sandbox: only known trusted repository files are invoked, and SHA-256 pins are change detection, not authorship verification.

## Local results (fixed, author-authored scenarios)

- **41 new tests passed** locally.
- **34/34 deliberately designed synthetic scenarios** routed to their expected outcome over 7 seeded variants of each of four core failure types and six additional refusal cases. The expectation labels were written by the same experimenter; this is **not** unseen failure classification accuracy.
- Insufficient evidence: an additional selected probe and an independent fixture validation; old repertoire retained.
- Missing control-flow capability: a real new triple-loop AST is learned; 10 fresh test graphs and 8 OOD graph checks pass, as does the pinned generated child. No installation.
- Contradictory instruments: **HOLD**; no unsupported grammar expansion.
- Resource limit: reproduce a truncated interpreter, reexecute with authorized fuel and cross-check outcome; no grammar expansion.
- Both-witness collusion negative control: source authenticity still **unproven**, and the system can only reason conditionally. It does not claim to identify all coordinated falsehoods.
- For comparison, a simplistic *always-grow* rule would attempt four grammar expansions on the four core symptoms, of which three are unnecessary under these fixtures. This is a cost/coverage comparison against a deliberately weak heuristic, **not** a general benchmark of self-improvement or intelligence.
- All tested actions are local and synthetic; the current code performs **zero external actions** and **zero autonomous repository edits**.

## Honest limitations / next experiment

1. A diagnostic route is still hand-authored and the possible failure families are known at design time.
2. Separate source implementations share a graph representation and can be wrong together. Neither source truth nor independence has been externally attested.
3. Budget units and thresholds are researcher preferences, not optimized utility, real financial cost or calibrated resource models.
4. Missing five-cycle control flow is already addressed by an existing MOTIF predecessor; this reuses and verifies that capability instead of inventing new general code.
5. We have not demonstrated diagnosis on independent novel task categories, autonomous semantic debugging, recursive self-improvement or deployment.

**Next frontier:** blind diagnosis with externally authored faults and task families, predeclared expected losses, and tests that distinguish *repairing the cause* from merely obtaining a good answer. Retain a modification only after a separately governed approval gate.
