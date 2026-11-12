# LAW-FORGE-001 — The First Scientific Discovery Trial

**Claim to test:** Can an initially memoryless two-port predictor recognize that its grammar is inadequate, propose a missing *temporal* distinction, choose a cheap discriminating synthetic experiment, and refuse a superficially convincing false law?

This is an **independent experimental branch** because MOTIF already has separate 027-numbered studies. It is not a claim that earlier MOTIF-011/012 concepts, MOTIF-026 GRAFT adapters, T5, Plan Z, or MEMENTO have been connected into this prototype.

## The invisible rule and the visible observation

Each opaque world accepts a binary pair of controls at each tick and returns one binary outcome. The oracle privately determines whether the latest outcome depends only on the present controls, or also on a previous control. The learner receives only immutable `Observation(Probe, outcome)` objects; it **never imports the oracle**, receives a family name, or sees held-out outcomes during its search.

The original grammar has only four current-control truth-table cells. In four of the worlds, two natural histories with identical current settings give opposite outcomes, disproving the memoryless description. The learner generates a finite vocabulary of anonymous candidate features — one lagged predicate per declared port — rather than being handed the hidden rule's name.

The initial histories deliberately confound the two prior control ports. Either lagged feature fits. MOTIF must propose a **specific off-diagonal synthetic experiment** that makes the two rival explanations disagree. The evaluator executes a typed local probe packet and returns its observation. No real API, file editing, generated code execution or real-world action is in this loop.

A separate **16-cell factorial local review**, including unseen two-tick histories, can reject the apparent discovery. The actual final 16-cell test is separately withheld. A second port-renamed destination world undergoes its own review; the source cartridge carries no permission to cross.

## Seven world families, fixed in advance

| Secret evaluator mechanism | Expected response |
| --- | --- |
| Instantaneous | Keep current-only model; do not invent memory. |
| First-port rising edge | Discover predictive previous-first-port feature. |
| Second-port rising edge | Discover predictive previous-second-port feature. |
| First-port sustained activation | Discover predictive previous-first-port feature. |
| Second-port sustained activation | Discover predictive previous-second-port feature. |
| Latent two-tick shift | **HOLD** after independent two-tick falsification. |
| Previous-port XOR | **HOLD**: selected single-lag grammar cannot explain independent data. |

These seven mechanisms were manually written by the experiment designer. The feature constructor and hold/review procedures are not novel AI algorithms. The causal role of a feature is *not established* merely because it predicts; no physical law, unrestricted grammar expansion, autonomous intelligence or open-domain learning is demonstrated.

## Matched baseline and method-level restraint

An adaptive disagreement selector is compared against a simple, **strong fixed classical diagnostic** that probes the two off-diagonal histories. Both have identical initial evidence, a maximum of two local queries, the same synthetic review, and identical final test partitions.

Development seeds 0–2 and separate evaluation seeds 3–7 are predeclared. Adaptive inquiry is marked `PROPOSE_ADAPTIVE_FOR_REVIEW` only if it produces at least two additional review-eligible development worlds without increasing error. Otherwise the output is `NO_METHOD_PROMOTION`.

The comparator was intentionally chosen to be competitive. Expecting a tie is not proof of a new superior inquiry method. No automatic policy promotion happens, even if the criterion were met.

## Three different kinds of failure

1. **Inadequate representation:** the original two-control grammar contradicts repeated outcomes; a finite one-lag feature can sometimes repair it.
2. **Unidentifiable cause:** a predictive port history may be a proxy. The study tests prediction, not causal attribution.
3. **Out-of-grammar world:** a second hidden memory step or an XOR of previous ports defeats the limited proposed grammar. Independent review must refuse prediction rather than relabel a contradiction as certainty.

## Portable artifacts and authority

`Probe.packet()` is a strict JSON-only local simulator packet; it may not contain addresses, URLs, credentials, scripts, host permissions or executable source. `Model.cartridge()` is a checksummed **prediction proposal** with `real_world_authority=false`, not a credential or attestation. SHA-256 identifies bytes, **not witnesses or authentic provenance**.

Independent synthetic review may return `ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW`; that is **not** admission or authorization. A human reviewer, destination owner, and source verification would be needed for any subsequent integration.

A future branch could link real MOTIF-011/012 cartridges, GRAFT's source-owned compiler, MEMENTO, and Plan Z under each project's contracts. None is wired into this experiment. Likewise the T5 semantic scout is deliberately absent.

## Reproduce

Python **3.10+**, standard library only:

```sh
python -m unittest discover -s experiments/law-forge-001 -p 'test_*.py' -v
python experiments/law-forge-001/trial.py > law-forge-results.json
python -m json.tool law-forge-results.json > /dev/null
```

A dedicated GitHub Actions workflow runs exactly these commands and retains the complete JSON benchmark receipt. The receipt includes method scores, a successful proposed concept, a refused latent-model example, negative transfer and the explicit nonclaims.

**Boundaries:** locally generated synthetic data; finite handcrafted grammar; deterministic Boolean outcomes; independent partitions only within the same seven generator families; small samples; no noisy physical witnesses; no neural inference; no real GRAFT compilation; no independent human usability study; no self-created grammar constructors, unrestricted self-modification, live autonomy or evidence of consciousness.

**Next falsifier:** change the procedural world's representational type (e.g., accumulating memory and delays beyond one tick) *after freezing the learner*, then ask whether it can propose and test a new feature constructor without the new rule being encoded in the test harness. If it fails, retain the failed case as the next research problem rather than expanding the claim.
