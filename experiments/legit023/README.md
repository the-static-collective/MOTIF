# MOTIF-LEGIT-023 — THE SHOULDERS OF GIANTS REPERTOIRE

**Status: research hold; stacked draft on LEGIT-022, not merged.**

The next experiment takes the best lesson of LEGIT-022 seriously: a
classical cost-sensitive planner was better than the inherited mathematical
aperture. Rather than handicap the comparator, make established methods
available to MOTIF as a **typed, testable, selectable portfolio**.

It is not intellectually legitimate to call something novel because we
neglected a standard method that already solves it.

## Two different mathematical requests

The externally originated 1998 Read/Wilson Graph Atlas is inherited from
LEGIT-022 with the same NetworkX 3.4.2 source-byte fingerprint, fixed
14-training/28-heldout split and original graph objects.

**Task A — graph non-isomorphism.** NetworkX's VF2++ algorithm can answer
this directly. A native joint 1-dimensional Weisfeiler–Lehman refinement
can sometimes *certify* non-isomorphism by distinct exact color histograms;
failure to distinguish **never implies isomorphism**. This task is a
first-class classical baseline that LEGIT-022's narrower scoring excluded.

**Task B — explicit homomorphism-count witness.** Produce an actual source
graph F with hom(F,G1) != hom(F,G2), including both numerical counts.
A VF2++ non-isomorphism verdict, while relevant to Lovasz's classical
characterization, is *not itself* an F and is never allowed to satisfy this
task. Compare five equal-grammar source-order policies:

- canonical connected source order (10 graphs through four vertices);
- inherited LEGIT-021 triangle, three-leaf star, square then fallback;
- LEGIT-022 classical greedy cost-sensitive training priority;
- **exact DP-optimal training unit-question ordering**;
- **exact DP-optimal training assignment-weighted ordering**.

The finite DP minimizes the weighted sum of source-question cost until the
first separating probe for the distinguishable *training* tasks. Any
unselected sources are appended in canonical order for the heldout fallback.
The optimized sequence is frozen and SHA-256 committed in the output
**before any heldout hom-count result is calculated**. This is optimal only
for that tiny nonadaptive training objective, not necessarily for the
external heldout distribution or for mathematical research generally.

All source hom-count answers are calculated using an actual classical
algorithm portfolio: exact forest message-passing/dynamic programming
where applicable, otherwise source-degree-ordered CSP backtracking with
early edge checks. These are checked against LEGIT-021's separate exhaustive
mapping enumerator **at each used heldout probe**. We do not confuse faster
counting with fewer questions, or a non-isomorphism decision with a numerical
homomorphism witness.

## Operating inventory

| Method | Status | Contract |
| --- | --- | --- |
| Tree homomorphism DP | EXECUTABLE | Exact finite counts, independently cross-checked |
| CSP/constraint backtracking | EXECUTABLE | Exact counts, repeat target vertices allowed |
| Exact training-order DP | EXECUTABLE | Optimizes frozen *training* finite objective |
| Joint 1-WL refinement | EXECUTABLE | Unequal histograms certify non-isomorphism |
| NetworkX VF2++ | EXECUTABLE with pinned dependency | Exact graph-isomorphism decision |
| SymPy symbolic algebra | NOT INTEGRATED | Typed adapter and validation pending |
| Z3 SMT | NOT INTEGRATED | Typed adapter and solver/certificate pending |
| cvc5 SyGuS | NOT INTEGRATED | Synthesis grammar and verification pending |
| OR-Tools CP-SAT | NOT INTEGRATED | Integer optimization adapter pending |
| Lean 4 + Mathlib | NOT INTEGRATED | Formal theorem proof-checker pending |
| nauty / Traces | NOT INTEGRATED | Canonical-labeling adapter pending |

**NOT INTEGRATED means unavailable at runtime**, never a simulated tool.
A future adapter must declare input schema, eligible goals, exact/heuristic
status, version, resource limits, failure modes, and independent
verification before becoming selectable. Selecting the cheapest admissible
method should be based on the *question*, not attachment to MOTIF's own
prior invention.

### Reproduce

In a checkout containing LEGIT-021 and LEGIT-022 on its ancestry:

```sh
python -m pip install --only-binary=:all: networkx==3.4.2
python -m unittest discover -s experiments/legit023 -p 'test_*.py' -v
python experiments/legit023/shoulders.py --emit > /tmp/legit023.json
```

No network API, cloud account or model credentials are used by the
experiment beyond dependency installation. The GitHub Actions workflow
writes the full result as an artifact. It does not modify main or
self-promote the findings.

### Research boundary

The Atlas source is independently authored, but benchmark construction,
selection and interpretation remain project-authored and non-blind. This
is one small, fixed graph problem. Exact DP is the best solver for the
*defined finite ordering objective*, not the best general search method.
The source-count time measured in this experiment includes independent
oracle verification, so it **must not** be compared as though it were the
uncached CPU microbenchmark from LEGIT-022. External peer review, formal
proofs, full engineering costs and multi-generation research acceleration
are all still missing.

The best available *general* computational research repertoire is not
one library: it is a typed tool ecology spanning graph algorithms,
optimization, symbolic algebra, synthesis, model checking and independent
proof. Only the first executable slice is shipped here.

## References (official project documentation)

- NetworkX VF2++: https://networkx.org/documentation/stable/reference/algorithms/isomorphism.html
- NetworkX Graph Atlas: https://networkx.org/documentation/stable/reference/generated/networkx.generators.atlas.graph_atlas_g.html
- Google OR-Tools: https://developers.google.com/optimization/cp/cp_solver
- Microsoft Z3 guide: https://microsoft.github.io/z3guide/
- cvc5 synthesis / SMT: https://cvc5.github.io/
- Lean + Mathlib: https://lean-lang.org/learn/
- SymPy: https://docs.sympy.org/
