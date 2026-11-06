# LAW-FORGE-011 — THE GENUINE SIGNED COUNTERFACTUAL CRITIC

**Predeclared next experiment.** LAW-FORGE-010 successfully demonstrated the value of source-owned post-identification classical auditing: 24 training-witness grammar contradictions were revealed across 50 synthetic worlds compared with zero without auditing. But its claimed counterfactual critic **never ran**: XOR-with-positive-AND alternatives are all contradicted by a witnessed all-ones anchor, so that method always collapsed into classical diversity questioning.

This experiment freezes 010 and attempts a **non-vacuous, bounded classical signed-literal critic**, then compares it against the best classical controls on **new evaluator-authored mechanism families and input partitions**.

**Research-only stacked draft** on 010; no production merge, external network source, genuine independently authored data or actuation.

## The correction

Construct a challenger to the sole surviving 650-rule champion:

```text
mutant(x) = champion(x) XOR term(x)

term(x) = AND(positive-literals, NOT(negative-literals))
```

Every term must contain **at least one positive and one negative literal**, drawn from two or three distinct channels. The exhaustive grammar has:

- Two-literal mixed-sign conjunctions: 66 pairs × 2 = 132.
- Three-literal mixed-sign conjunctions: 220 triples × 6 = 1320.
- **1452 explicit signed counterfactual critics**.

These term functions are **false at all-zero and all-one** source input anchors, unlike 010's positive-only mutation. They therefore survive the witnessed anchors, except when other existing source observations refute them. The critic is not guaranteed to reflect the source's true missing logic. No critic is promoted to the trusted 650-rule hypothesis grammar or used to make direct predictions.

The chooser selects a source-owned question according to **the fraction of surviving signed critics contradicted by the current champion at that input, divided by its declared source query cost**. If critics are empty, it has an explicit classical diversity fallback, which must be counted transparently. New source-witnessed contradictions are passed to the inherited 009 minimal relative-to-grammar evidence verifier.

**Classical origin:** elementary Boolean function mutation testing and falsification. This does not constitute an original inference theorem.

## New owner mechanism family

The new owner code `source_owner.py` is physically separated from `signed_critic.py`, and its hidden outcome function is never imported by the learning or query-selection component.

Twelve new source mechanism classes use 12 binary control channels (4096 settings), with hidden feature positions varied by seed:

1. Four in-grammar controls: single bit; pairwise XOR; triple OR; triple AND.
2. Two explicitly signed-rule challenges: `a XOR (b AND NOT c)`; and `a XOR ((b AND NOT c) OR (d AND NOT e))`.
3. Four ordinary out-of-grammar challenges: conditional mux; three-bit majority; four-bit parity; four-bit threshold.
4. Two negative cases: a source that changes after training, and review-only hidden context.

Every world starts with the all-zeros / all-ones anchors plus two source-owned random observations. Its catalog offers 160 possible typed questions, with 192 disjoint review configurations and 256 further disjoint test configurations. Inputs, query catalog and risks are controlled by the authored synthetic source; no reviewer or test labels enter the training phase.

**Developer authored** is not the same as independently authored: these are not external sources, even though their class labels are withheld from the learner.

## Frozen controls and budgets

The exact same source initial observations, the genuine 009 classical Shannon entropy learner, a 12-unit *learning* phase, a 12-unit *post-identification audit* phase, and the same source catalog are given to each policy.

| Policy | Challenge chooser |
| --- | --- |
| `signed_counterfactual` | Score surviving signed Boolean mutational disagreements per source cost |
| `classical_diversity` | Maximize minimum Hamming distance to witnessed controls per cost |
| `classical_boundary` | Cost-aware nearest-observation (minimum-distance) boundary probes |
| `classical_fixed` | First permitted source question |
| `classical_seeded_random` | Deterministic source/evidence-bound random score per cost |
| `no_audit` | No extra questions; retains classical Shannon learning and reviewer gate |

No policy may spend more than 24 source-cost units total or 12 within auditing.

A model may be submitted to independent review only when its evidence does not contradict all frozen 650 rules; a witnessed grammar-gap certificate triggers HOLD instead. The independent review separately requires at least 16 covered predictions with **zero wrong covered predictions**. No heldout test prediction is allowed on a rejected source. The report distinguishes *training source-witnessed grammar gaps* from independent-review failures.

Development: twelve source classes × seeds 0 and 1 = **24 worlds**.

Final frozen evaluation: twelve source classes × **new seeds 7, 8, 9, 10** = **48 worlds**. These input partitions and challenge families differ from 010. Seed reuse is not a claim of independent human authorship.

Frozen method promotion requires at least **two more** training-witness contradictions on development than the best of *four* classical audit controls, **no higher total source cost** and **no additional approved test errors**. Anything else: `NO_METHOD_PROMOTION`. Even a win is proposal for human review only.

The runtime is a standard library Python **source-bound serialized reason cartridge** `motif.reason-cartridge.signed-falsifier.v1` plus a strict JSON-stdio `open/propose/ingest/diagnose/predict` desk. No live source execution, source-authenticating signature, new network permission or autonomous production admission is present.

## Grok Build donor, adjacent but not silently imported

User-provided Grok workspace archive includes a **substantive MOTIF-015C “The Forged Choir”** Python research patch and standalone archive. It is *not* merely a Grok UI scaffold.

Independent local sandbox check (the exact user-uploaded bytes, no network calls) showed **11/11 015C tests passed** and the standalone 512-forecast benchmark reproduced its reported figures: classical two-rumor grid Brier **0.198766**, one-rumor MOTIF grid **0.201929**, independence-only **0.271547**. These findings establish usefulness as a **research donor on correlated/falsified witness provenance**, not as a signed-Boolean query module or production service.

The 015C component is not copied into the 011 learner. Its hypotheses concern **correlated testimony and Bayesian uncertainty**, whereas 011's testbed has source-owned noiseless Boolean function calls. Mixing their posteriors would be scientifically wrong without a distinct experimental contract. A separate GRAFT-style branch/import with pinned source hash and native CI should review it before any downstream integration.

See `GROK-015C-INTAKE.md` for donor provenance, privacy/safety and relevant integration questions. The ZIP also contains generic `.grok/` skill files, scaffold code and app tooling; **the meaningful research is the artifact patch, not the generated browser app**.

## What remains unresolved

Does signed model mutation actually select better falsifying questions than classical coverage/diversity? A model can be left with one surviving rule that remains wrong, even after many audits. A minimal contradiction core only proves inconsistency with the **frozen 650-rule language**, not actual external truth. Loss of model-space coverage or source-dependent shifts may overwhelm all heuristics. The next step, if these controls fail, is better source-aware classical model criticism or a genuinely authenticated external source—not claiming emergence.

### Reproduce

```sh
python -m unittest discover -s experiments/law-forge-011 -p 'test_*.py' -v
python experiments/law-forge-011/trial.py > law-forge-011-results.json
```

Dedicated GitHub Actions reruns inherited 001–010 suites and 011 adversarial tests, executes the preregistered benchmark, preserves the portable signed cartridge and question proposal. **No result, benchmark win or CI pass is presumed before actual run evidence.**
