# MOTIF-IMMUNE-001 — Epistemic Virology

**Question:** Can a typed reasoning field recognize the *mechanisms* by which unverified statements become established claims, trace contaminated dependencies, and preserve the right to investigate strange ideas?

**Status:** executable, isolated, synthetic research experiment. This is not a deployed AI immune system, a sandbox for untrusted code, an antivirus, an authenticated reputation mechanism, or evidence of recursive self-improvement.

## What runs

- [immune.py](immune.py) accepts immutable claim-bearing records, checks graph parents/cycles, preserves root provenance, separates each **advertised** status from actual local verification, and refuses to elevate repeated testimony into proof.
- An explicit operator-requested mathematical checker exactly evaluates two bounded integer polynomials on the **11-point domain -5..5**. A success proves only that finite property, not unrestricted symbolic identity or a universal theorem.
- Untrusted payload strings, including role-override text, are never executed or passed to a privileged system.
- A false checked claim becomes **FALSIFIED**. Its dependents become **DEPENDENCY_REVIEW**, rather than having their truth presumed false. A descendant may independently recover **VERIFIED_FINITE** status through a new exact check. An explicitly withdrawn parent triggers the same dependency review.
- Unchecked and non-mathematical claims remain **HYPOTHESIS** or **HOLD**, not censored. A checked unfamiliar true finite identity remains acceptable.
- A typed **next action** is emitted for unresolved records: finite test, seek independent evidence, or recheck contaminated dependencies.
- The source lineage graph counts structural **declared upstream roots**; no claim is made that roots, identities, or alleged independence are externally authenticated.

## Predeclared test design

[oracle.py](oracle.py) creates **12 engineer-designed families**:

1. forwarded-consensus amplification;
2. apparent independent-source consensus;
3. counterfeit verification;
4. instruction/role spoofing in untrusted payload;
5. dormant parent error reactivation;
6. checked false mathematical statement;
7. withdrawn premise with downstream dependence;
8. independently checked recovery from a bad parent;
9. unfamiliar but checked true finite identity;
10. unfamiliar unreviewed true hypothesis;
11. unknown claim beyond the verifier's grammar;
12. parent verification that must **not** automatically confer verification on children.

Fixture labels and expectations live in a separate evaluator module. The defender does not import them. Developer seeds **0..9** and held-out seeds **200..239** vary the claims, wording, and record IDs. They do **not** vary the family grammar and are therefore only a narrow robustness test, not a blinded novel-attack evaluation.

[benchmark.py](benchmark.py) measures exact states, contamination reviews, false promotion, preservation of checked valid novelties, and source checks, with both:

- **naive counting control:** promotes three apparent reports or an asserted authoritative label;
- **strong classical control:** explicitly runs the *same finite checker* on the reviewed target. Its binary promotion accuracy should **tie** the immune field. The graph field's additional output is dependency tracing and typed recovery.

The weaker control is intentionally vulnerable and must not be presented as evidence of superiority over real contemporary defensive methods. Both controls see the same public records and operator review requests. The strong classical control does not perform causal ancestry tracing, so exact status parity is not its assigned task.

## Reproduce

Python 3.10+, standard library only:

```sh
cd experiments/immune001
python -m unittest -v test_immune.py
python benchmark.py
```

A dedicated GitHub Actions workflow runs these commands and publishes the JSON report in its log. No model provider, credential, network access, shell execution from evidence, or external automation is required.

## Gates and falsifiers

A valid check must not be silently inherited by downstream claims. Forwarding must not increase the number of upstream roots. Claimed system status, document repetition, and prompt-like strings must not grant authority. Invalid graph structures must HOLD. A checked false root must trigger review of dependents, but separately checked true children must survive. Unknown and novel hypotheses must remain available for future exploration. A strong verifier baseline must be shown, even if MOTIF merely ties it.

## Important limitations

1. The verification gate is deliberately tiny: a complete finite polynomial comparison on eleven integer inputs. No unrestricted formal proof, witness authentication, or cryptographic attestation is implemented.
2. The fixture family taxonomy, data grammar, target outcomes, and scenario generation are engineered by this project, rather than discovered independently.
3. This evaluates *graph bookkeeping under adversarial data*, not real AI agents exposed to untrusted internet content; instruction-looking strings are inert by construction.
4. SOURCE IDs and structural roots are not sufficient to establish actual independence. Copies that strip all upstream relationships can fool the origin counter, although they still cannot pass the local proof gate.
5. The experiment has no learned immune repertoire or out-of-family adaptive recognition. No claims about autonomy, universal intellectual immunity, novel mathematics, or recursive improvement are warranted.
6. Computation is bounded to prevent uncontrolled recursion; malformed evidence or requests are rejected before promotion.

## Proposed IMMUNE-002 (not implemented here)

Challenge an actual model-mediated reader with **unseen** paraphrases and long-range injection chains; measure task correctness, attack success, benign rejection, false provenance confidence, attribution to the first corrupted edge, and repair cost against capable prompt-injection defenses. Keep read-only retrieval, typed tool capability boundaries, and separately authenticated evidence. Build an adversarial provenance dataset from independently authored documents before evaluating any training/adaptation gains.
