# META-007 — Break the frame: optimize MOTIF's mathematical question language

**Research-only stacked DRAFT** on META-006 #265, then #263, #259 and prior
unmerged branches. Collatz remains an accepted unsolved mathematical problem.

## Experiment and genuine representation change

META-006 used 2 recursive odd inverse operations per node and certified
a restricted infinite convergent family with
|S∩[1,X]| = Ω(X^0.08760374...) using a uniform worst-case branch multiplier.

Instead of simply allowing more operations, META-007 asks:

> How many DISTINCT, SOURCE-VERIFIABLE positive-integer inverse words fit
> within a bound on their actual construction cost?

The resulting representation is a **weighted language of proof-carrying
Collatz predecessor operations**, not a depth-only search tree.

### Original executable inverse operator

For odd y>=5, y≡2 (mod3), the existing META-006 modular rule chooses
e0(y mod9) from {2:1,5:2,8:3}. A new alphabet of K choices has

    t in {0,...,K-1}
    e=e0+3*t
    B_t(y) = (2**(2e+1)*y-1)/3.

The equation T(B_t(y))=2**(2e)*y, followed by 2e even halves, is
checked against exact integer source arithmetic. Every node is an actual
positive odd integer ≡2 mod3, allowing indefinite new branches.
The inverse word is uniquely decoded from v2(T(child)) and its parent;
finite ambiguity is NOT assumed away.

The strict well-founded rank is the old META-006 rank:
R(5)=4, R(B_t(y))=R(y)+2e+1, and R(2**h*y)=h+R(y).
Each true nonterminal Collatz transition drops the rank by exactly one.
The complete domain also includes powers of two and terminal1.

## 1. Automatic proof-bound self-critique: the source divisor matters

The first bound used in META-006 simply replaced the actual arithmetic
factor with a power of two:

    B_t(y) < 2**(7+6t)*y.

But that threw away the EXACT divisor 3 in the original source formula.
The new experiment systematically derives the **smallest INTEGER
growth-cost bound w_t** satisfying

    3*2**w_t > 2**(7+6t).

This is decided by ordinary BIG-INTEGER inequalities, not logarithm
estimation. The resulting cost is provably and optimally tighter:

    w_t = 6+6t.

The optimizer produces a source-bound *self-critique receipt* showing
the original 7+6t cost, the newly minimal 6+6t cost, the exact
inequalities certifying both minimality and safety, and the reason
for the missed slack. All subsequent source-family proofs recompute
the improved cost.

**This is not a mathematically novel observation.** It is a measured
internal improvement to the program's evidence/measurement representation.

## 2. Exact weighted word counting instead of worst-case depth

For a K-symbol inverse grammar, let C(L) be the number of distinct
inverse-operation WORDS whose sum of weights w_t is at most L.

The exact source-independent recurrence is

    C(L)=1+sum_(t:w_t<=L) C(L-w_t),   for L>=0
    C(L<0)=0.

The empty word accounts for +1. Injective inverse decoding proves each
word denotes a DIFFERENT positive integer, not just a different string.

For rational α=p/q, if

    Σ_t 2**(-α*w_t) > 1,

and W=max_t w_t, then strong induction proves:

    C(L) >= 2**(α*(L-W))  for EVERY L>=0.

Base: L<W implies C(L)>=1>=2^(α(L-W)).
Inductive step: for L>=W each L-w_t>=0, and the recurrence bounds
C(L) below by the previous statement times the verified sum (>1).

Every word of cost ≤L represents n<5*2**L. Hence for sufficiently large X,

    |S∩[1,X]| = Ω(X**α).

This is an **infinite-family mathematical guarantee**, not a fitted
regression on enumerated integers.

## 3. The optimizer actually chooses the improved grammar

The executable finite search considers ALL K=2,...,12 and a grid of
rational exponents α=p/1000, 80<=p<=180.

Each candidate t's real irrational term 2**(-p*w_t/1000) is bracketed
by rationals z/10**12 and (z+1)/10**12, with rigor certified using
**pure integer power comparisons**:

    z**1000 * 2**(p*w_t) <= (10**12)**1000
    (z+1)**1000 * 2**(p*w_t) > (10**12)**1000.

The program proves each selected alphabet's weight sum >1 from
integer lower bounds, and rejects its next p from integer upper bounds.
Monotonicity in p makes binary search COMPLETE over this declared grid.
An independent, high-precision classical closed-form geometric-sum
method reproduces all selected candidate scores.

### Selected result

**K=8 possible inverse operations per node, α=166/1000=0.166.**

K=9,10,11,12 attain the same maximal grid exponent but use more
operation choices, so the predeclared tie break selects the smallest K.

The optimized restricted family therefore satisfies

    |S∩[1,X]| = Ω(X**0.166).

This rigorously improves the exponent over META-006's more constrained
0.08760374... lower bound by **about 1.895-fold**.

It is NOT an improvement over all known Collatz mathematics.
Krasikov and Lagarias (2003) proved a much larger bound ~X^0.84 for
the FULL predecessor set of 1, using difference inequalities:
https://doi.org/10.4064/aa109-3-4 .
They remain a much stronger independent historical benchmark.

The 0.166 exponent is optimal only over the stated K and rational p
grid, with THIS source-verified uniform cost grammar. It does not imply
positive density, completeness or a global Collatz solution.

## 4. Real-world mathematical source checks

The selected K=8 grammar generates ALL words through depth3:

| Depth | Different true positive Collatz predecessors |
| ---: | ---: |
| 0 | 1 |
| 1 | 8 |
| 2 | 64 |
| 3 | 512 |
| **Total** | **585** |

Every generated integer is separately checked using direct forward
Collatz simulation to 1, full inverse-code decoding, exact macro
transitions, rank and weighted size bound.

The **actual prior META-006 binary grammar decoder** recognizes
only 15 of these nodes. The expanded language certifies **570 new
nodes outside META-006's available operation alphabet**.

These 570 are genuinely new relative to the *previous restricted
grammar*, not unverified historical mathematical discoveries. The
arithmetic source is deterministic and local, not a live remote scientist.

The word-count recurrence is independently matched to exhaustive
classical word enumeration at small cost budgets. All full future proofs
carry original source version, exact inequality witnesses, rejected
parameter attempts, positive-integer domain checks and global OPEN label.

## 5. Scientific boundaries

- The Collatz conjecture is still **OPEN**.
- The proof is about one proper infinite subset of the natural numbers.
- The grammar and optimizer's decision space are engineer-authored.
- The algebraic induction has been written out and checked on finite
  representatives, but has NOT been formalized in Lean/Coq or reviewed
  externally as a new mathematical theorem.
- Existing classical inversions and counting arguments are not novel.
- Equal-information classical weighted-code optimization **ties** MOTIF.
- The score does not prove a positive natural density or improve the
  published X^.84 full-predecessor lower bound.
- A SHA digest is not source authentication or authority to publish.
- No service deployment, MCP installation or production merge.

## Reproduction

Python 3.11+ standard library:

    python -m unittest discover -s experiments/meta007 -p 'test_*.py' -v
    python experiments/meta007/weighted_grammar.py > meta007-weighted-proof.json

The dedicated workflow reruns inherited META-001 through META-006 source
tests, generates full inspectable proof artifacts and re-enters the evidence
without new external investigative questions.

## Next frontier

The present cost grammar pessimistically assumes e0=3 for **every**
source y, even though e0 depends on y modulo 9.

A mathematically meaningful new primitive would transport deeper
mod-3^k residue states through each inverse branch and build a
**multitype, rigorously verified weighted transition operator**.

Then compute a spectral growth inequality with exact rational lower
certificates, using the strongest available classical residue automaton
and difference-inequality methods as controls.

That is the next opportunity to improve the REPRESENTATION of the
research process rather than simply spend more computation.
