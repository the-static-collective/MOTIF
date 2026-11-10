# META-002 — Variable-time ranking, and the invariants that fail

**Unmerged stacked research DRAFT**, based on META-001 #250 and the
COLLECTIVE-005 source/evidence experiments. No external source actions,
no production merge, no new claim that Collatz has been solved.

## User-approved experimental question

Can MOTIF use the failure of a fixed-horizon proof method to invent a
*variable-horizon proof strategy*, test proposed well-founded ranking
functions, discover rigorous counterexamples when they cannot work, and
carry accurate positive and negative evidence into the next question?

Yes, in a bounded **human-authored arithmetic grammar**. It does not
generate unrestricted new mathematical axioms or independent theorem
novelty. The problem remains open.

## Three strategies and their exact outcomes

### A. Fixed-horizon strict descent — algebraically blocked

From META-001: for every fixed k, an infinite family n=2**k*t-1
(n>1) obeys T**k(n)=3**k*t-1>n under the accelerated Collatz map T.
The exact induction proof blocks *universal same-k strict descent*.
It does not block eventual or variable-horizon descent.

### B. Finite-state positive affine potential — another no-go

The system tests the candidate rank function

    P(n) = w[n mod m]*n + b[n mod m]

for a fixed finite modulus m, arbitrary **positive** bounded coefficients
w, and arbitrary finite offsets b.

A general all-odd-prefix diagonal shows this family cannot be
strictly decreasing at EVERY accelerated Collatz step, regardless of
which weights and offsets are selected.

Let w_min>0, w_max and B=max|b|. Pick k so that

    w_min*3**k > w_max*2**k.

Then choose integer t sufficiently large that for
n=2**k*t-1, N=T**k(n)=3**k*t-1,

    P(N) >= w_min*N - B > w_max*n + B >= P(n).

If P decreased on every intermediate step, necessarily P(N)<P(n),
contradiction. This proof does NOT exclude a variable-horizon,
nonlinear, unbounded-memory, or more expressive ranking method.

The implementation constructs concrete independently replayable witness
orbits for five sample coefficient sets, including mixed and negative
offsets, and verifies the lower/upper bound and the *first actual
nondecreasing P step*. The general inequality is mathematical, not
a sample-based extrapolation. This is elementary no-go reasoning, not
claimed as a historically novel theorem.

### C. Variable-time *residue-class first descent* — partial success

For each residue r mod 2**K, enumerate exact k-step affine expressions
from META-001 at ALL shorter horizons 1..K. Choose the *earliest* j such
that T**j(n)<n holds for every positive n>1 in that parent residue class.

This is mathematically sound: the parity path is fixed across the
larger parent class for every j<=K, the affine slope is <1, and the
strict inequality is checked at the smallest member n>1. If true there,
it remains true for all larger members of the same progression.

Compare:
- A restricted fixed-endpoint policy that checks only T**K(n)<n.
- The adaptive symbolic proof generator using the earlier proof cards.
- An independently implemented **classical exact Fraction first-descent
  solver** with identical candidate horizon budget and information.

**Verified target level K=9:**

| Metric | Exact class count |
| --- | ---: |
| All classes mod 512 | 512 |
| Uniform descent at exactly 9 steps | **382** |
| Uniform descent at SOME j<=9 (adaptive) | **474** |
| Strong exact classical adaptive baseline | **474** |
| Additional infinite residue classes proven vs fixed-only | **92** |
| Still unproved at horizons <=9 | **38** |

A transfer test at K=12 uses the same rules, no changed grammar:

- Fixed endpoint only: **3,301 / 4,096** classes.
- Variable-time: **3,870 / 4,096** classes.
- Strong classical adaptive: **3,870 / 4,096** classes.
- **226** classes still HOLD; includes the all-odd 4095 residue.

These are **infinite arithmetic progression** proof certificates: each
covered residue has infinitely many members. Incomplete coverage means
there is **no** global stopping-time proof. The adaptive method is
standard classical stopping-time reasoning, not mathematically novel.
The comparison to FIXED ONLY shows gains from question-language
expressiveness; the fair adaptive classical comparator ties.

### D. Honest unresolved evidence

The saved packet includes complete K=9 residue cards (the earliest
certified step and exact supporting source proof, or HOLD), a per-level
summary, five complete finite source-owner traces of representative
numbers from HOLD classes, and exact counterexamples to the weighted
one-step potential family.

**Finite examples that eventually descend do not certify their infinite
residue class.** Nothing authorizes publishing an open-problem solution.

## What counts as a solution?

By standard strong induction, Collatz is equivalent to: **for every n>1,
some accelerated iterate T**j(n) is strictly less than n**. We cannot
derive a finite universally complete such assignment of variable j
from the tested residue classes. Each fixed K has an all-odd exceptional
class; varying K without a quantified bound on individual n proves
nothing global.

The next meaningful question is whether a genuinely new **nonlinear,
stateful, or unbounded-memory ranking certificate**, with explicit
well-founded semantics, can handle the remaining 2-adic frontier
without probabilistic parity assumptions.

## Source research

- Eric Weisstein, "Collatz Stopping Time", MathWorld, reference to
  Lagarias 1985 (source on first-drop equivalence):
  https://mathworld.wolfram.com/CollatzStoppingTime.html
- Lagarias, J. C. (1985), *The 3x+1 Problem and Its Generalizations*,
  DOI 10.1080/00029890.1985.11971528.
- Terras/Everett classic stopping-time density-one results.
- Tao (2022) almost-everywhere orbit theorem and Barina (2025/26)
  computer verification, as documented by META-001.

The distinction between **almost all** and **every** integer is
critical. No historical mathematical originality claim is justified.

## Reproduce

Run Python 3.11+ standard library, from project root:

    python -m unittest discover -s experiments/meta002 -p 'test_*.py' -v
    python experiments/meta002/variable_horizon.py --k 9 > meta002-research.json

The dedicated GitHub Actions workflow runs META-001 regressions and
META-002, plus K=12 exact transfer and publishes the complete JSON
proof-carrying record as an artifact.

## Research hold

- No general autonomous method or primitive invention.
- No improvement over the full-featured fair classical solver.
- No new unreviewed open-problem theorem or counterexample.
- No independent scientific source identity; source oracle is local.
- No global ranking function with decreasing potential.
- No deployment, no plugin installation or external-world action.
