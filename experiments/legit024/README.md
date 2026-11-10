# MOTIF LEGIT-024 — RESEARCH METHOD ECOLOGY

## The shoulders of giants become selectable tools

**RESEARCH HOLD.** LEGIT-022 established that a tuned classical planner
beat MOTIF's inherited perspectives on a narrow graph-hom question.
LEGIT-023 gave MOTIF a genuine classical graph repertoire. This experiment
connects symbolic algebra, integer-programming solvers, graph invariants and
graph-homomorphism witnesses under **typed question, method, evidence and
verification contracts**.

MOTIF should start with the best established method appropriate to the
question, then inspect what remains unresolved; a positive "new theorem"
claim is deliberately **not** an output of this trial.

## The executable crossing

A request is an explicit JSON-compatible task in one of four bounded
mathematical languages:

| Task | Executable candidate methods | Required evidence |
| --- | --- | --- |
| Univariate integer-polynomial identity | SymPy exact polynomial expansion; separate native coefficient ring; MOTIF-style sample-then-escalate | Exact coefficient equality, or integer substitution counterexample. Both native and SymPy cross-check the conclusion. |
| Bounded integer linear optimization | Z3 Optimize, Google OR-Tools CP-SAT, exhaustive enumerator | Full exhaustive finite search cross-checks feasibility, an actual satisfying assignment and global optimum. Native exhaustive method also requires independent Z3 agreement. |
| Graph isomorphism/nonisomorphism | exact 1-WL invariant (may abstain), NetworkX VF2++ | Independent permutation enumeration on at most 7 vertices. 1-WL inconclusiveness is **never** "isomorphic." |
| Find graph-homomorphism source witness | inherited LEGIT-021 probe ordering; LEGIT-023 training-DP ordered probes | Concrete source graph F with unequal exact hom(F,G1) and hom(F,G2), cross-checked against LEGIT-021's separate exact enumerator. |

**Never substitute an answer to one contract for another.** In
particular, graph nonisomorphism from VF2++ does not by itself supply a
finite homomorphism-count source witness.

The languages are bounded and contain no evaluation of arbitrary user
code. Z3 and CP-SAT calls have internal time budgets. Model outputs,
nonoptimal incumbent solutions, false statements and proof-obligation
failures are not promoted. Unknown cases are HOLD/ABSTAIN. Planned
Lean/mathlib, cvc5 SyGuS, nauty/Traces and open-ended theorem synthesis
are explicitly NOT INTEGRATED.

## An executable training and next-question loop

1. Run *every eligible tool* against training problems, checking
   numerical/proof obligations and recording real CPU time.
2. Order methods within each task contract by verified training coverage,
   then training CPU time. Hash and freeze all method orders **before**
   heldout solver answers are requested.
3. Run the original fixed method order versus this learned order on
   heldout tasks, on exactly the same cases with the same acceptance
   contract. A method that abstains can trigger fallback.
4. Preserve all receipts: methods actually called, exact answers and
   witnesses, verification route, CPU time, and explicit refusals.
5. Admit what cannot be measured: no full integration/development labor
   cost, no independent hidden benchmark, no real multi-generation
   improvement proof.

This learning is limited to *choosing among existing tools* based on a
single training episode. The "next question" is about **which method is
most useful for the current mathematical goal**, not autonomous theorem
discovery or independent invention of new solver algorithms.

## Research provenance and scope

- Graph carrier objects: Read/Wilson (1998) Graph Atlas via pinned
  NetworkX 3.4.2, with LEGIT-022's original cryptographic source pin,
  14 training matched pairs and 28 evaluation matched pairs. Graph
  pairing and the experimental design are project-authored.
- Polynomial and integer-optimization fixtures: **engineer-authored**
  standard algebraic and synthetic bounded-integer tasks with separate
  training and heldout instances. Not independent mathematics.
- Actual exact solver packages: Python 3.11; NetworkX 3.4.2,
  SymPy 1.14.0, z3-solver 4.16.0.0 and OR-Tools 9.15.6755.
- All raw research evidence is written as a GitHub Actions artifact and
  printed aggregate metrics can be inspected in the job log. Timing is
  a tiny-runner measurement with training and verification overhead; do
  not interpret it as a statistical speedup claim.

### Reproduce in a branch with LEGIT-021/022/023 ancestry

```sh
python -m pip install --only-binary=:all: networkx==3.4.2 sympy==1.14.0 z3-solver==4.16.0.0 ortools==9.15.6755
python -m unittest discover -s experiments/legit024 -p 'test_*.py' -v
python experiments/legit024/trial.py --emit > /tmp/motif-legit024-ecology.json
```

## Known limits and honest science

We now have a small **general-purpose research-method selection pattern**
covering *four* exact, tightly constrained goal families. That is not a
universal mathematics assistant. It does not search arbitrary scholarly
literature, synthesize unbounded programs, emit Lean proofs, or discover
new theorems. The "MOTIF sample then certify" probe was engineer-authored
and is useful as an illustration of avoiding premature proof promotion.

A promising follow-up is controlled multi-episode training on truly new,
independently administered tasks, with formal certificates and total
engineering/research cost accounted. Until then:

RESEARCH_HOLD_NO_NOVEL_MATH_OR_RECURSIVE_IMPROVEMENT

## Relevant established methods

- SymPy: https://docs.sympy.org/
- Z3: https://microsoft.github.io/z3guide/
- Google OR-Tools: https://developers.google.com/optimization/cp/cp_solver
- Graph Atlas: https://networkx.org/documentation/stable/reference/generated/networkx.generators.atlas.graph_atlas_g.html
- VF2++: https://networkx.org/documentation/stable/reference/algorithms/isomorphism.html
- Lean 4/mathlib: https://lean-lang.org/learn/
