# LEGIT-027 — CROSS-DOMAIN QUESTION TRANSFER

**RESEARCH HOLD.** No generalized research intelligence or autonomous
scientific discovery claim. Stacked draft on LEGIT-026, not merged.

## Can a graph-learned rule help different mathematics?

LEGIT-026 adopted the graph question-selection rule
`LEAF_FIRST + COUNT_DIVERSITY + STATIC` through engineer-designed
bounded policy mutation and graph-world training. It matched classical
optimized graph-ordering controls. This trial asks whether the
`COUNT_DIVERSITY` **evaluation principle** works outside graphs.

**Translation boundary matters.** The graph-only `LEAF_FIRST` gate is not
portable to polynomials or constraint systems. The actual transfer is:
collect candidate question outputs on target-domain training examples,
rank each candidate by the number of distinct observed values, and freeze
a nonadaptive order. This is *not* a zero-shot transfer of graph-source
questions. Target-domain training data are used to instantiate rankings.

The prior source artifact is mechanically validated at
`experiments/legit026/generated/selected_meta_cartridge.json` including
the original frozen SHA-256, so the rule cannot silently change between
experiments.

## Two different mathematical question types

### A. Exact integer-polynomial **nonidentity witnesses**

Inputs are pairs of integer-coefficient polynomials in one variable.
Questions take the form `(integer x, prime modulus p)` with `x` in
{-3,-2,-1,0,1,2,3} and `p` in {2,3,5,7,11}.

Each question observes both exact polynomial values modulo p. If the
residues differ, that is a mathematically valid counterexample to
polynomial identity. Matching residues are **not** a proof of equality.
A separate direct-coefficient comparator verifies the existence of
different polynomials, and an independently implemented direct-power
polynomial evaluator verifies every attempted question.

The synthetic fixture generator produces degree-three polynomial
differences with roots at zero and one and a varying third root and
factor. Both initial cheap probes `(0,2)`, `(1,2)` are guaranteed
inconclusive. There are **35** eligible questions.

### B. Bounded integer linear-constraint **countermodels**

Inputs are pairs of conjunctions of two linear integer inequalities
`a*x + b*y <= t` with `x,y` in `0..5`. One bound differs
between two formulas. An assignment `(x,y)` is a question: evaluate
both formulas and check for a differing truth value. A differing value
is an exact **nonequivalence countermodel**; agreement at a few
assignments never proves equivalence.

A separate independent constraint evaluator checks every attempted
assignment. There are **36** eligible questions. Initial corner
assignments `(0,0)`, `(5,5)` are guaranteed inconclusive.

This is deliberately hard on the graph-learned `COUNT_DIVERSITY`
rule: unlike graph-homomorphism counts, Boolean satisfiability
observations have only two possible values. If diversity degenerates
or underperforms, the result should be retained as counterevidence
against easy generalization.

## Fair matched comparison

For **each** domain, training uses fixed predeclared seeds 27011 and
27012 (16 cases each). New task families use 27013 and 27014 (16
cases each) *after* ranking is frozen. All cases have verified finite
counterexamples and are conditioned on the two old cheap questions
failing. This is engineer-authored, selected, not externally blind.
Challenge construction checks witness **existence**, but does not use
future-case measurements to choose the rank order.

Six complete, same-grammar question policies are compared, including a training-validated guard:

| Policy | Training uses target domain? | Rule |
| --- | --- | --- |
| `LEGIT026_GRAPH_SCORER_TRANSFERRED` | Yes | Frozen graph-selected COUNT_DIVERSITY / STATIC recipe |
| `TARGET_CLASSICAL_STATIC_GAIN` | Yes | Order by number of training cases distinguished |
| `TARGET_CLASSICAL_RESIDUAL_GREEDY` | Yes | Recompute gain after removing solved training cases |
| `TARGET_DOMAIN_HEURISTIC` | No | Predefined conventional first questions |
| `CANONICAL_FIXED` | No | Full original question order |
| `TRAINING_CV_GUARDED_TRANSFER` | Training-seed CV only | Retain transfer only if it beats target conventional residual-greedy on held-out-within-training problems; otherwise reuse classical method |
| `NO_ESCAPE_OLD_TWO_QUESTIONS` | No | Intentionally weaker two-question baseline |

Each of the six full-grammar methods has the same 35 (polynomial) or 36 (constraint)
candidate questions and same independent oracle. All six have equal
expressive power and must resolve every fixture; poor query ordering
is measured, not silently dismissed.

The old two-question control is expected to abstain on all cases.

We hash both target-domain method orders before accessing future seeds.
All candidate and negative observations are archived; independent
verification is performed on every attempted observation. The
predeclared future-world seed list is open, not a cryptographically
blinded test.

## Measured result — transfer fails against strong domain comparators

**Original GREEN CI trial #42748075671:** 12 adversarial tests passed.
The source graph-selected `COUNT_DIVERSITY` scorer was executed on
two new non-graph goal contracts. It did *not* match the target-domain
classical residual-greedy order on either future problem family:

| Method | Polynomial nonidentity (32/32) | Integer-constraint countermodel (32/32) |
| --- | ---: | ---: |
| Fixed canonical complete questions | 483 | 435 |
| Transferred graph `COUNT_DIVERSITY` score | **117** | **435** |
| Target static classical gain | 70 | 255 |
| Target residual classical greedy | **62** | **234** |
| Prespecified target heuristic | 112 | 295 |
| **Training-CV guarded selector** | **62** | **234** |
| Old two-question limit | 0/32 solved | 0/32 solved |

Numbers are **individual questions actually asked**, not CPU
milliseconds. Each full-grammar method found 32 independently checked
counterexamples in each domain. The old control abstained on every task.

On modular polynomials, the transferred rule beat naive fixed ordering,
but required **117 versus 62** questions for the strong classical
planner. On Boolean constraint observations, the diversity score
degenerates: it required **435**, identical to fixed canonical ordering,
versus **234** for the target-trained classical method.

### Automatic refusal of a weak transfer

We added a conservative **training-only domain gate**: leave one of the
two training-seed worlds out, fit each method on the other world, and
compare its average source questions on the left-out world. Prefer
the conventional classical method on a tie.

| Training-world CV (avg questions per case) | Transferred graph scorer | Target classical residual greedy |
| --- | ---: | ---: |
| Polynomial modular nonidentity | 5.34375 | **2.96875** |
| Integer constraint countermodels | 15.71875 | **15.28125** |

**The gate rejected the transferred rule in both domains before future
evaluation cases were opened.** It automatically reused an established
classical planner, and matched that planner's 62 and 234 questions in
the separately seeded future worlds.

This is an informative *negative result* for cross-domain generalization
of observation diversity and a verified demonstration of refusing a
poorly supported transferred method. It is not algorithm invention:
the fallback was an existing conventional method, and the train/eval
world generators, candidate grammars and selection gate were written
by the engineer.

### Preserved negative-result cartridge

`generated/transfer_failure_and_guard.json` records the source
graph-frozen policy, exact source SHA-256, training-world CV scores,
rejection decisions, future scored results and green CI evidence. A
test verifies its training-derived fields against the executable
research code, so the failed transfer is part of MOTIF's durable
knowledge rather than a forgotten discarded experiment.

The source CI run includes an artifact containing all attempted
questions, positive and negative exact witnesses and all final
training-frozen source orders. Final follow-on validation should be
consulted for the added artifact-integrity test.

## What the result can and cannot mean

If count diversity matches or improves domain-specific classical
controls, it is narrow evidence of transfer for two small engineer-
generated math families. If it loses, it identifies a real
cross-domain limitation. Neither outcome proves recursive
self-improvement, new theorem discovery, novel algorithms, or
cross-domain mathematical generality.

In particular, a polynomial-equivalence or constraint-equivalence
statement cannot be established from observing finitely many matching
question outputs. This trial tests finding **counterexamples**, not
certifying equivalence.

The computational cost recorded is CPU including exact independent
checks, **not** end-to-end human engineering cost. No externally
independent challenge, statistical multi-seed robust superiority
claim, or formal Lean certificate is attempted.

## Reproduce

```sh
python -m unittest discover -s experiments/legit027 -p 'test_*.py' -v
python experiments/legit027/transfer.py --emit > /tmp/motif-legit027-transfer.json
```

No additional Python packages beyond the standard library are used
for the new experiment; it loads its predecessor's committed JSON
cartridge but does not execute predecessor graphs or math engines.
