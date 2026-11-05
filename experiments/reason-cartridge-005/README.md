# REASON-CARTRIDGE-005 — THE META-OBJECTION ECONOMY

**Status:** source-pinned, finite synthetic experiment. Stacked on experimental REASON-004 draft PR #80, then #77 / #73 / #70; not merged, deployed, authorized for external operations, or evidence of general-purpose reasoning transfer.

## Research question

Can a reasoner **criticize its own objections**, avoid pursuing objections defeated by an existing alternate proof, investigate potentially material objections only when a *declared* model says the expected gain warrants it, and retain **two different portable lessons**?

1. **DEFENSE:** an objection was insufficient. Keep the alternate proof, with its premises and precise source revision; never claim objections fail universally.
2. **CORRECTION:** a separately owned synthetic source supplied genuinely new evidence that changed a conclusion. Keep the prior claims, supersession receipt, revised source-owned proof, and the condition under which the revision applies.

The system also supports **OWNER_DEFENSE**: the source owner reviewed a potentially material objection but did not validate it. That is distinct from merely showing an objection would be immaterial if true.

## What works

- `engine.py` checks the exact Git blob SHA (`334fe8feb389cfa2aa7a418e31c433ae3f6ae9e3`) of the existing REASON-004 source before importing it. Source revision shifts cause HOLD. REASON-004 itself pins the REASON-003 source.
- A finite objection language distinguishes `RETRACT_PRESENT` and `REVIEW_ABSENCE` over at most 3 named directed edges.
- The **objection-to-objection** procedure runs a counterfactual source-owned proof. If an alternate *real-witness-supported* path survives an alleged retraction, the attack cannot invalidate this proof. If no proof remains, the objection is **material**, *not yet true*.
- The bounded meta-critic reviews at most eight unique objections and at most **one** synthetic owner probe per run. Duplicate patterns, missing permissions, source revision changes and unknown methods HOLD.
- A declared toy cost model includes probability of correction, benefit if corrected (cost of not investigating), owner verification cost, and reasoning cost. The critic stops when the modeled net value is nonpositive. These costs and probabilities are **hypothetical, not measured or calibrated**. An optimal classical decision-theoretic planner could do equally well.
- `ToyOwner` is a fixture that privately holds synthetic edge truths. A reviewed revision preserves prior claims in a receipt, so a corrected proof is not silently rewritten. This fixture is not an authenticated human or real-world sensor. All outputs remain data-only, read-only suggestions; no network queries, credentials, messages, live mutation, real-world authorization or learner-created executable programs.
- `motif.reason.meta-objection-cartridge.v1` validates exact owner contracts, replayed source-owned evidence, evidence and proof correctness, and limits its claimed authority. A content SHA is **not an identity signature**; packet validation alone cannot prove that a third party's claimed revision occurred. This is why the experiment remains synthetic.
- `Receiver` independently tests unlike **defense** and **material-objection** cases and requires a review-digest-bound `ADMIT_READ_ONLY` decision. `Memory` recalls defenses or corrections only for the **exact source graph, revision and objection**, never promotes them to broad rules without fresh evidence.

## Reproducible synthetic trial

The preregistered cases intentionally include proof fragility, counterexamples, incorrect witnesses, and a cost-sensitive stop.

| Fixture | Outcome | Meta-critic owner reviews | Naive always-review |
|---|---|---:|---:|
| Two redundant proven paths, two one-edge attacks | 2 proof defenses | 0 | 2 |
| Fragile positive proof, source retracts one premise | 1 conditional correction | 1 | 1 |
| Fragile positive proof, source confirms attacked premise | 1 owner rebuttal | 1 | 1 |
| Negative proof, source verifies missing link is present | 1 conditional correction | 1 | 1 |
| Review deliberately costs more than declared expected benefit | HOLD without probe | 0 | 1 |
| **Total** | **2 corrections, 3 defenses/rebuttals** | **3** | **6** |

This is a controlled simulation where the full synthetic owner knows the answer. The always-review baseline is deliberately weak; classical expected-value-of-information and theorem-proving methods are more appropriate strong future controls. Thus the result would **not** establish improvement beyond established decision theory.

The independent receiver evaluates four *different* graph situations (two defended, two material), with no training examples reused.

## Run

```sh
python -m unittest discover -s experiments/reason-cartridge-005 -p 'test_*.py' -v
python experiments/reason-cartridge-005/trial.py
```

The GitHub Actions workflow `.github/workflows/reason-cartridge-005.yml` additionally executes full inherited REASON-001/002/003/004 regression, checks the synthetic performance receipt, and publishes it.

## Meaningful falsifiers

- A one-edge objection to two genuinely independent confirmed routes must fail to refute the conclusion, and the returned alternate path must remain checkable.
- A correction must have a changed conclusion **and** a source-attributed revised premise receipt; replaying an altered proof/receipt, even with a recomputed content checksum, must HOLD.
- A supposedly valid material objection which the owner rejects cannot be recorded as a correction.
- Source owner not available, open world without proof, duplicate objections, no useful question, expired budget or unreviewed receiver must not create an external action.
- A cached correction cannot jump to a different source graph or hypothesis context.
- Strong classical controls may tie or outperform the meta-critic and must not be misrepresented.

## Next frontier

Use genuinely independent user-approved, versioned source-owned witnesses from an actual reasoning system, and measure **adaptive query regret**, retained method quality on unseen problems, and epistemic calibration against matched classical VOI and proof-maintenance algorithms. Only promote broadly reusable rules after independently validated transfer, and only promote real-world effects through separately approved owner permissions.
