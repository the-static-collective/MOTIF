# LAW-FORGE-002 — THE CONSTRUCTOR FORGE

**Question:** Once LAW-FORGE-001 discovers that its *entire available one-feature-per-port vocabulary* cannot describe observed outcomes, can a separate, auditable procedure assemble a new feature **program** from generic operations, identify it through a deliberate experiment, and transfer it only after independent review?

**Scope:** Source-separated, finite, standard-library synthetic research. This is a stacked draft experiment on LAW-FORGE-001; do not merge either branch automatically.

## What changes

LAW-FORGE-001 can select a single previously available lagged feature. LAW-FORGE-002 adds an explicit bounded grammar-expansion mechanism:

```text
typed observations from LAW-FORGE-001
       │
       ├─ old grammar still fits? ─ YES ─> retain incumbent; 0 probes
       │
       └─ all old models contradicted
                      │
                compose NEW feature ASTs
                      │
                 LAG(port 0)
                 LAG(port 1)
                 AND(LAG0,LAG1)
                 OR (LAG0,LAG1)
                 XOR(LAG0,LAG1)
                      │
              fit each synthetic truth table
                      │
             more than one fits? ─ YES ─> propose discriminating probe
                      │                            │
                      │                    evaluator executes probe
                      │                            │
                      └────────────── revised evidence, refit
                                         │
                           sole candidate? otherwise HOLD
                                         │
                     independent 16-cell, two-tick falsifier
                                         │
                              eligible to propose
                             prediction-only cartridge
                                         │
                    independently review transfer destination
```

The learner is **not told the secret mechanism's name**. It constructs candidate ASTs from an interpreter containing the generic Boolean primitives AND, OR, XOR and two lag selectors. Its selected expression is represented as strict typed JSON, not arbitrary generated code. Parser rejects unknown opcodes, deep trees, extra keys, privileged actions and tampered SHA-256 identifiers.

This **is** bounded *composition of a feature constructor*. It is **not** invention of XOR, new mathematics, a truly open-ended programming language, or unrestricted autonomous code writing. Such claims would require capabilities and independent trials not supplied by this prototype.

## Five hidden evaluation families

| World | Initial observation | Independent falsifier / correct decision |
| --- | --- | --- |
| Previous-port XOR | Three lagged states fit OR and XOR | Probe the withheld fourth state, prefer XOR, independently review |
| Previous-port OR | Same three lagged states fit OR and XOR | Probe fourth state, prefer OR, independently review |
| Current-only mechanism | Original LAW-FORGE-001 grammar explains it | Keep incumbent, do not synthesize |
| Hidden two-tick memory | Training and one-step inquiry initially resemble XOR | New two-tick review cases refute false one-tick concept: HOLD |
| Artificial mechanism shift | Inquiry resembles XOR | Review shifts to OR; reject rather than promote |

The *world evaluator* imports the new constructor learner; the learner does **not** import the evaluator. The evaluator alone executes the permitted local simulator step after receiving a `Probe.packet()`. The experiment contains no real instruments or GRAFT compilation.

## Three matched methods

- `old_only`: existing LAW-FORGE-001 vocabulary; hold when it fails.
- `fixed`: new AST composer, but a predeclared classical fourth-history diagnostic probe.
- `adaptive`: same new AST composer, choosing a one-bit disagreement probe by finite information gain.

All methods see the same 12 natural observations, have at most **one synthetic inquiry**, receive the same 16-case independent local review, and are judged on a separately withheld 16-case test. Development seeds 0–1 and evaluation seeds 2–6 are disjoint. **Do not claim adaptive superiority if it ties the strong fixed classical strategy.**

A frozen simple method-promotion rule demands adaptive produce >=2 extra review-eligible *development* worlds with no extra covered errors compared to fixed; otherwise `NO_METHOD_PROMOTION`. Even a win would be a **review proposal**, not automatic policy mutation.

For transfer, a successful source cartridge is independently reviewed against a renamed, same-mechanism destination world. A destination world governed by a different hidden mechanism must refuse it. Source checksum does not authenticate origin or confer destination authority.

## Reproduce

Python 3.10+, standard library only; run from repository root:

```sh
python -m unittest discover -s experiments/law-forge-002 -p 'test_*.py' -v
python experiments/law-forge-002/trial.py > law-forge-002-results.json
python -m json.tool law-forge-002-results.json > /dev/null
```

A dedicated GitHub Actions workflow reruns the test and saves the complete synthetic benchmark JSON with source-linked CI evidence. Results must be reported from the actual run.

## Research boundaries

- Exactly **two Boolean ports**, **one lagged timestep**, **two lag atoms** and **three pre-supplied Boolean combinators**. Finite trees of size 3 only; no recursive generated user code.
- The five worlds and distribution shifts are **hand-designed toy mechanisms**. Seeds change old-history patterns, not hidden function families.
- Independent review is within the same generator family; it is independent of training *data* but not independent science or externally created models.
- Test labels stay only in evaluator partitions and never train candidates or choose an experiment; the method portfolio is held fixed before scoring.
- No inference about physical causality, societal welfare, AI consciousness, internet actions, financial or safety decisions.
- No GRAFT, Plan Z, MEMENTO, or T5 are newly wired in this branch. Their source-owned contracts remain separate.
- All outputs remain `PROPOSAL_ONLY` / `ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW`; never automatic admission.

## The third vertical

Once a composed expression survives independently generated domain families, have an *external* grammar-expansion challenger generate a new kind of raw sensor, time delay, or relation arity **not anticipated by the current AST**. Freeze the learner before exposing that domain, then see if it can propose a new **operator definition**, not just compose known primitives. If not, retain its HOLD as the valid scientific result.
