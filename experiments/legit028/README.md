# MOTIF LEGIT-028 — THE INFORMATION GEOMETRY FRONTIER

**Research status: HOLD. Unmerged stacked draft.** The goal is to test
whether a question-selector can recognize that *observation entropy*
and *actual value for its goal* are different quantities, compare
candidate interpretations of value on training-only problems, and
adopt or refuse a more sophisticated conditional-information
procedure before it encounters future research cases.

## The central falsification

A mathematical question can produce many different observations and
yet never distinguish the two hypotheses whose difference we seek.

Example: a probe observing `(n,n)` with variable n generates
high entropy but **zero witnesses**. A probe yielding `(0,1)` on every
example has constant output and **zero joint entropy** but a
**guaranteed witness**.

Therefore `maximize H(observation)` is not generally equivalent to
`maximize probability of exact distinguishing evidence`.

The trial tests this empirically and includes the example as a
regression test. Equal observations do **not** establish graph
isomorphism, polynomial identity or constraint equivalence.

## Three typed observation geometries

| Mathematical question | Observation alphabet | Verifiable goal |
| --- | --- | --- |
| Graph source F, targets G1/G2 | Exact unbounded integer counts hom(F,G) | Find F yielding unequal exact homomorphism counts. |
| Polynomial modular evaluation (x,p) | Residue in 0..p-1 | Find differing exact modular residues: proves polynomial nonidentity. |
| Bounded integer assignment (x,y) | Boolean truth value | Find assignment giving unequal formula truth values: proves nonequivalence. |

Graphs use pinned NetworkX 3.4.2 Atlas data and the actual LEGIT-025
five-vertex source grammar; all candidate methods have access to the
same **21** probes. Polynomial questions use the **35** exact
modular observations from LEGIT-027. Constraint questions use the
**36** finite assignments. Original math generators are
engineer-authored and deliberately condition on old-probe failures.

## Interpretable candidate research strategies

The system measures each candidate question on training cases:

1. Raw distinct observed values (the transferred LEGIT-026 heuristic).
2. Shannon entropy of the joint observation pair.
3. Entropy of the binary **witness** indicator.
4. Empirical probability of producing an exact witness.
5. A conditional, Beta-smoothed witness-probability estimator that
   updates after each observed failed question.
6. A conditional *value-of-information proxy*: witness probability
   plus a bounded normalized conditional joint-output entropy term.

The adaptive methods calculate training-case similarity using
**ordinal ranks computed entirely from training observations**. They
condition on the actual previous failed question/answer pairs of
the currently evaluated task. They do not open future outcomes for
questions they have not actually asked. A negative reply updates
the selector; a positive reply is independently verified.

The sixth strategy is explicitly a **VOI heuristic proxy**, not a
proved solution to optimal Bayesian experimental design. The method
does not have a calibrated Bayesian posterior over all possible
mathematical objects. The training priors and kernels are
engineer-designed.

## Strong conventional comparators

- **Classical residual greedy**: maximize the number of training
  cases newly distinguished after previously solved cases are removed.
- **Canonical complete enumeration**: fixed deterministic question
  order.
- **Old insufficient grammar**: the ten connected <=4 graph probes
  or two old non-graph probes. Should abstain, never falsely prove
  equality.

All full methods use exactly the same candidate question grammar.
Their difference is which question they ask next, not which answers
are allowed.

A domain-level meta-selector performs **leave-one-training-world-out**
cross-validation, averaging the number of questions per task by world.
It compares the best experimental geometry method with the
conventional residual greedy; a **0.025-question complexity penalty**
and a conservative tie breaker prevent promoting an unsupported
change. This is a bounded engineer-written selection protocol,
not autonomous invention of a new mathematical algorithm.

## Worlds and information isolation

Training:
- Graphs: the four previously used LEGIT-026 training worlds
  (Atlas training, prior seeded cases, and two other graph seeds).
- Algebra/constraints: the two LEGIT-027 training seeds 27011/27012.

New evaluation (constructed **after** all strategy hashes are frozen):
- Graphs: fresh seeded 8-node worlds 28001/28002, each selecting eight
  nonisomorphic graph pairs with all old 4-node hom counts identical.
- Algebra/constraints: fresh generator seeds 28011/28012, each
  selecting sixteen problems whose two old cheap probes are
  inconclusive but a later exact witness exists.

These are **not independent externally blinded challenges**. Graph
pairs come from engineer-selected and seeded publicly reproducible
generators; modular polynomial and constraint problem authorship is
also internal. Evaluating on similarly filtered cases is not
evidence of open-world success.

Both the proposed and **independently implemented exact oracle**
observe each actual asked question, including each negative result.
No finite list of negative questions may be promoted to a
mathematical equality certificate.

## Research evidence and reproducibility

The experiment records training-world CV results for each of the
eight candidate strategies, the empirically observed alphabet
geometry, SHA-256 fingerprints of every fitted training-only method,
the frozen combined hash, full future positive/negative question
traces, independent verification and CPU time including verification.

```sh
python -m pip install --only-binary=:all: networkx==3.4.2
python -m unittest discover -s experiments/legit028 -p 'test_*.py' -v
python experiments/legit028/run_information_geometry.py --emit > /tmp/motif-legit028-evidence.json
```

The pinned GitHub Actions run archives the full report as
`MOTIF-LEGIT028-INFORMATION-GEOMETRY-RESEARCH-HOLD`.

## Measured results — information geometry is task dependent

**First green experiment (CI run `42750210074`): 12 tests passed.**
The second revision adds retrospective regret diagnostics but does not
change training selection or the mathematical hypotheses.

The training-only selector adopted different strategies:

| Domain | Training observation alphabet | CV-selected question-value theory |
| --- | --- | --- |
| Graph-homomorphism witness | Many exact counts | Raw observation diversity |
| Polynomial modular counterexample | Variable finite residues | Failure-conditioned estimated witness probability |
| Integer constraint countermodel | Boolean | Marginal probability of an exact witness |

The outcome is **mixed, not a general win**. Across separate, fixed
engineer-generated future worlds:

| Full question strategy | Graph (16 cases) | Polynomial (32 cases) | Boolean constraints (32 cases) |
| --- | ---: | ---: | ---: |
| Canonical fixed | 47 | 458 | 377 |
| Classical residual greedy | **19** | **67** | **289** |
| Raw observation diversity | **19** | 51 | 377 |
| Joint Shannon entropy | 33 | **47** | 280 |
| Bernoulli witness entropy | 43 | 66 | 293 |
| Marginal witness probability | 21 | 81 | 293 |
| Contextual witness-probability estimator | 21 | 70 | 279 |
| Contextual information-value heuristic proxy | 21 | 91 | **267** |
| **Training-CV selected router** | **19** | **70** | **293** |
| Old insufficient grammar | 0/16 solved | 0/32 solved | 0/32 solved |

Counts are the **number of actual source questions asked**; each
complete method found a mathematically verified witness for every case.

On the graph cases the selected raw-diversity method **matched** the
strong conventional planner with 19 questions. On polynomial tasks the
selected contextual posterior took **70 vs the conventional 67**, while
*unselected, evaluated only after freeze* joint entropy took 47.
On Boolean constraints, selected marginal witness probability took
**293 vs classical 289**, while *unselected, evaluated only after
freeze* conditional information-value proxy took 267.

**Across all 80 new cases, the CV-selected router took 382 questions,
while conventional residual greedy took 375.** It was **seven questions
worse**, not better. This is an observed small-sample *method-selection
generalization failure*, even though its CV score on each domain was
better. Selection based on only two math training worlds can overfit
the synthetic generator and does not identify an unconditionally
superior mathematical information theory.

The experiment's posthoc diagnostic now records the observed
per-domain question regret, strongest future candidate and the
resulting **next relevant research question**: whether genuinely
distinct training environments and a distribution-shift-aware guard
can predict when to trust a new information-value criterion.

**The posthoc winner is never promoted into this evaluation.** That
would leak the future results. It is retained as a *hypothesis for a
later preregistered experiment*, not retroactively claimed as an
adaptation success.

The key mathematical lesson is not simply to maximize entropy.
It is to separate **descriptive observation variety** from
**instrumental value toward a verifiable objective**, while
recognizing that even a value-aligned training metric can generalize
poorly. Posterior heuristics also have nonzero computational overhead,
so fewer questions need not mean lower total compute or engineering
cost.

## Boundaries of the claim

Even a successful heldout result would demonstrate only an
engineer-authored **goal-aligned information-routing experiment** on
small, constrained tasks. A failure is equally informative:
an empirically sophisticated information-entropy method could lose
to ordinary classical witness-gain planning. No historical
mathematical novelty, autonomous invention of a mathematically
general algorithm, recursively compounding improvement, or
human-labor cost advantage is claimed.

`RESEARCH_HOLD_NO_GENERAL_INFORMATION_GEOMETRY_DISCOVERY`
