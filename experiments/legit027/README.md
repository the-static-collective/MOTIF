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

Five complete, same-grammar question policies are compared:

| Policy | Training uses target domain? | Rule |
| --- | --- | --- |
| `LEGIT026_GRAPH_SCORER_TRANSFERRED` | Yes | Frozen graph-selected COUNT_DIVERSITY / STATIC recipe |
| `TARGET_CLASSICAL_STATIC_GAIN` | Yes | Order by number of training cases distinguished |
| `TARGET_CLASSICAL_RESIDUAL_GREEDY` | Yes | Recompute gain after removing solved training cases |
| `TARGET_DOMAIN_HEURISTIC` | No | Predefined conventional first questions |
| `CANONICAL_FIXED` | No | Full original question order |
| `NO_ESCAPE_OLD_TWO_QUESTIONS` | No | Intentionally weaker two-question baseline |

Each of the first five has the same 35 (polynomial) or 36 (constraint)
candidate questions and same independent oracle. All five have equal
expressive power and must resolve every fixture; poor query ordering
is measured, not silently dismissed.

The old two-question control is expected to abstain on all cases.

We hash both target-domain method orders before accessing future seeds.
All candidate and negative observations are archived; independent
verification is performed on every attempted observation. The
predeclared future-world seed list is open, not a cryptographically
blinded test.

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
