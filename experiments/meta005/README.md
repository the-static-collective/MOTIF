# META-005 — An explicit infinite closed positive-integer domain with a real rank

**User-approved next breach:** META-004 constructed an exact terminating rank
on a finite verified graph. Does a genuinely **INFINITE**, transition-closed
family of positive Collatz states admit an explicit, verified, noncircular
well-founded ranking?

**Answer in a restricted domain: YES.** We construct an explicit
*parameterized infinite subset* of the positive integers, with infinitely
many odd members and arbitrarily long initial runs of odd accelerated
Collatz steps. Every member has an algebraically predicted termination
rank, with proofs of transition closure and strict rank decrease.

**This is established-style inverse Collatz arithmetic, not a solution
of the Collatz conjecture and not historically novel mathematics.**

## Actual new executable research

For the accelerated Collatz map

    T(n) = n/2           if n is even
         = (3*n+1)/2    if n is odd,

first derive the PREIMAGE grammar by solving its actual branch equations.

- EVEN preimage of y: 2*y, always.
- ODD preimage of y: (2*y-1)/3, an odd integer if and only if
  y≡2 mod3. Exclude the terminal 1 as a new ranked odd predecessor
  of y=2, to avoid misrepresenting the ordinary 1↔2 terminal cycle.

Iterate the ODD inverse j times from an even power of two 2**m.
The mathematical obstacle is whether every inverse is a positive integer.
Rather than check samples, construct a parameterized integrality
certificate using the established p=3 lifting-the-exponent lemma (LTE).

For any j>=1 and t>=0, define

    m = 3**(j-1)*(2*t+1).
    A = 2**m+1.
    n_i = 2**i*(A/3**i)-1   for 0<=i<=j.

Because m is odd, LTE proves exactly

    v_3(2**m+1) = 1+v_3(m) >= j.

Thus every division A/3**i is exact. For i>0, each n_i is
positive and odd except the explicitly excluded degenerate
j=1,t=0,i=1 case (n_i=1, already the terminal). For i=0,
n_0=2**m.

Direct substitution into the accelerated Collatz rule proves

    T(n_i) = n_(i-1)   for i>0.
    T(2**m) = 2**(m-1).

Add arbitrary EVEN inverse prefixes: 2**h*n_i for h>=0.
It is still an exact positive integer and

    T(2**h*n_i) = 2**(h-1)*n_i  for h>0.

The newly defined infinite domain is:

    S = {1} ∪ {2**e: e>=1}
        ∪ {2**h*n_i : j>=1,t>=0, 1<=i<=j,h>=0,
                      m=3**(j-1)*(2*t+1),
                      (j,t,i)!=(1,0,1)}

Then a genuine **strictly decreasing, well-founded rank** over all S is:

    R(1)=0;
    R(2**e)=e;
    R(2**h*n_i)=h+i+m   for i>=1.

The function is defined from the *generating parameters*, not by
tracing the future trajectory first. All nonterminal accelerated
successors are in S and their ranks decrease **exactly by one**.
This proves finite convergence on S, an infinite parameterized
domain, without asserting anything about positive integers outside S.

The generating representation can be redundant (e.g. n=5 can be
generated using j=1 or j=2), but the rank agrees on duplicate states,
because their actual strict odd-prefix/terminal-power signature is
the same. The test suite checks these duplicate witnesses.

### Arbitrarily many initial odd steps

For each j>=2 choose t=0, m=3**(j-1). The n_j(m) so constructed
starts with **j consecutive odd accelerated steps**, then reaches
2**m, whose m halvings reach 1. Since j is unrestricted in the
symbolic proof, this family has arbitrarily long initial odd blocks,
although materialized tests are bounded.

Concrete examples:

| j | m | n_j | exact accelerated rank |
| --- | ---: | ---: | ---: |
| 1 | 3 | 5 | 4 |
| 2 | 3 | 3 | 5 |
| 3 | 9 | 151 | 12 |

The positive family is demonstrably infinite: it includes every
power of two and infinitely many odd predecessors.

### Actual independent checks

- All tested exact LTE valuations match an independent repeated
  division-by-3 reference, including hundreds of odd m not authored
  as special cases.
- All materialized j<=7,t<=5 inverse chains and their rank lengths
  agree with a separately implemented direct Collatz forward oracle.
- Parameterized successor transitions, including even lifts, are
  rechecked against two independent Collatz step implementations.
- A separately built CLASSICAL inverse-preimage tree, its source
  closures and direct orbit depths is the equal-information baseline.
  The standard classical method is **NOT beaten**.
- False family universality is caught: n=7 is known by exact direct
  computation to reach 1 but is NOT a member of this restricted
  family (its initial odd block leads to even 26, not a power of 2).
  Failing membership is an honest HOLD, not a declaration of
  nonconvergence.

## Why this doesn't prove Collatz

The Collatz conjecture asserts EVERY positive integer enters the
1↔2 cycle. Showing explicit infinite subsets do does not cover
all positive integers. The full *backward-reachable set* from 1 is
indeed the set of convergent integers, and proving it equals all
positive integers would be **equivalent to solving Collatz**.

META-005 does not assume that equality. It constructs one
explicitly parameterized (restricted) subset instead.

The finite checks independently replay proofs, but the unbounded
induction proof is **human-reviewable mathematics, NOT a Lean-checked
formalization**. The underlying inverse-tree and LTE facts are
classical and independently documented.

## Provenance

- Jeffrey Lagarias, *Lower Bounds for the Total Stopping Time of
  3x+1 Iterates*, section "3x+1 trees":
  https://websites.umich.edu/~lagarias/doc/3x%2B1bound.pdf
- Lifting-the-Exponent lemma, p=3: see the UCLA Math Circles
  LTE handout https://circles.math.ucla.edu/circles/lib/data/Handout-2227-1977.pdf
- Related inverse tree literature: Bell & Lagarias, *3x+1 inverse
  orbit generating functions almost always have natural boundaries*,
  Acta Arithmetica 170 (2015).

## Next genuinely unknown mathematical question

Can an expanded proof-producing grammar establish **a new quantitative
coverage bound** for an infinite positive transition-closed inverse family
that isn't already implied by classical inverse-tree constructions?
More ambitiously, can it cover *every* positive integer without assuming
that conclusion as its defining axiom?

Any proposed global proof must first survive exact scope checking,
independent classical baselines and expert or formal proof review.

## Implementation and verification

This is an **unmerged stacked research DRAFT** on META-004 #259
(and #257, #255, #250 and earlier COLLECTIVE branches).

Run using Python 3.11 standard library:

    python -m unittest discover -s experiments/meta005 -p 'test_*.py' -v
    python experiments/meta005/infinite_inverse_rank.py > meta005-infinite-rank-evidence.json

GitHub Actions executes the new tests plus inherited META-004/003/002/001
regressions and archives the complete ranked-family evidence packet.
No plugin or service is installed. No independent source agent or
production merge.
