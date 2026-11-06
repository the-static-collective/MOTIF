# LEGIT-001 — Reason Routing / Stranger Gate (first executable slice)

**Status: draft experimental branch. Synthetic only. No autonomous tool use, code
generation, network activity, external authority, deployment, or claims of
general intelligence.**

## Question

Can MOTIF select **which reasoning method to use**, rather than merely execute
a method someone already selected? Can it recognize that one question appears
worthless immediately but opens a *second useful question*?

This first slice implements **finite Bayesian metareasoning**. It deliberately
uses classical mathematics. Its primary adversary is an **independent
implementation of the same strong classical lookahead**, and its ablation is a
shortsighted one-step router. Beating the myopic version is not a novel
algorithmic result, and tying the classical reference is expected.

## What actually executes

`router.py` accepts a strict, bounded, **synthetic-only** task: up to eight
world hypotheses with explicit prior probabilities and yes/no answers, up to
five question likelihood tables with explicit costs, an abstention loss, and a
maximum cost/number of synthetic queries.

It emits one inspectable, inert routing recommendation:

- `PREDICT_TRUE` / `PREDICT_FALSE`: use the supported finite model without
  an additional investigation;
- `ASK_SYNTHETIC`: select an *unsent* observation ticket that reduces
  expected decision loss sufficiently to cover its cost;
- `ABSTAIN`: refuse to pretend a useful answer is available;
- `PROPOSE_GRAMMAR_REVIEW_HELD`: report a **declared** representation gap;
  this is not a proof of impossibility or permission to synthesize an operator.

At each step the router receives only a list of synthetic observations that
an **independent challenge harness** supplies after the proposal. It does not
import the harness, execute the observation, infer user consent, or modify any
files. Content digests permit byte-level replay; they do not authenticate
sources. Queries cannot repeat and budgets are enforced.

Its planning objective is *expected terminal 0/1 error or abstention loss plus
explicit future question costs*. The two-step router can recognize a
complementary pair of experiments whose first question alone does not improve
decision quality. This is the limited affordance connection to MOTIF-003:
an information-gathering step creates another valuable option.

## Controls and scoring

`stranger_gate.py` contains **184 authored synthetic cases** in seven
registered families: XOR, OR, biased priors, uninformative sensors, a
one-question budget, expensive sensors, and declared grammar gaps. Each run
chooses a hidden world under the declared prior and samples noisy readings.
The true world and readings are omitted from the router input and only
revealed to the evaluator when appropriate.

Five policies face exactly the same tasks, truth values, sensor outcomes and
costs:

1. MOTIF finite two-step routing.
2. An independently coded **exact classical two-step** decision-tree solver.
3. One-step myopic routing (ablation).
4. Prior-only immediate prediction or abstention.
5. Always abstain.

The report distinguishes **prediction coverage**, **covered error rate**,
**mean realized total loss**, **synthetic query count**, and **unscored HELD
grammar gaps**. Unlike an accuracy-only competition, abstentions and paid
inquiries have explicit consequences.

```bash
python -m unittest discover -s experiments/legit001 -p 'test_*.py' -v
python experiments/legit001/benchmark.py
```

The dedicated GitHub Actions workflow runs the entire test suite and prints
the benchmark report; no credentials or paid models are required.

## Important scientific nonclaims

- **No independent unseen tasks yet.** The suite is authored in this PR,
  not obtained from outside, and does not constitute the proposed real
  Stranger Gate against independent repository bugs.
- **No new learned routing policy.** The router enumerates a finite,
  manually declared hypothesis/query grammar. Its policy is classical
  value-of-information optimization.
- **No classical superiority.** Exact lookahead should tie the independent
  classical solver. The myopic ablation can lose when two questions have
  complementary value, but that is textbook metareasoning.
- **No actual GRAFT/CANNON/Plan Z integration** in this slice. The missing
  grammar branch is a HOLD only, not an automatic invention pathway.
- **No calibrated real-world witnesses.** Priors, sensor likelihoods,
  query prices and losses are assumptions of the benchmark designer.
- **No true source authentication.** Hashes protect against accidental
  content divergence, not malicious provenance.
- **No transfer claim.** The hypothesis space, costs, queries, outcome
  schema and utility policy are developer-defined.

## Falsification gates for graduation

1. Import frozen, **independently authored** bug/inquiry tasks and their
   source-owned evaluation procedure without giving MOTIF the solution.
2. Make classical **same-evidence, same-compute** baselines compete alongside
   explicit ablations. Publish losses, refusal quality and failure traces.
3. Test **unseen representations and hidden common causes**, not only
   predictable members of a declared family.
4. Use source-owned, separately reviewed CANNON/GRAFT adapters only if
   objective evidence shows a real missing method; no self-admission.
5. Add real-world evidence collection only through separately authorized,
   bounded, read-only connectors; do not infer permission from graph facts.
6. Consolidate the proven components into a versioned kernel **after**
   independent evaluation, rather than merging all experimental branches.

The immediate scientific objective is **to learn where routing fails**,
not to manufacture a favorable benchmark. A discovered classical tie or loss
is a valid result.
