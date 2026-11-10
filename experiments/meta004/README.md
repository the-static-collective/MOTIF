# META-004 — The 2-Adic Ghost Boundary & Proof-Carrying Nonlocal Rank

**User-approved frontier:** instead of increasing the finite proof horizon
indefinitely, change representation. Ask whether an infinitely extending
unresolved parity history corresponds to an *ordinary positive integer* or to
something that exists only in the larger 2-adic state space.

**This is an unmerged research DRAFT** stacked on META-003 #257, META-002
#255, META-001 #250, and COLLECTIVE-001..005. Not a Collatz proof.

## The real problem, still OPEN

Does every positive integer eventually reach 1 under Collatz?

In META-003, 226 unresolved residue classes modulo 4096 each allowed
adversarial continuation of the parity sequence to *any preselected*
finite length, even though every finite cylinder contains infinitely many
positive integers. That does NOT demonstrate that *one positive integer*
has an infinite nonconvergent orbit. The quantifiers are different.

Our new research question:

> What is the 2-adic limit point of an indefinitely unresolved parity
> branch? Does it actually belong to the positive natural numbers?

This is a distinct, nonlocal **topological/domain-admission question**
that finite Collatz stopping-time simulations cannot decide.

## 1. Actually synthesize and test the 2-adic periodic points

Represent any parity word of length k by its exact affine composition:

    T^k(x) = (3^o*x + b) / 2^k,

where o is its count of odd steps. Set the expression equal to x:

    x = b / (2^k - 3^o).

The denominator is always odd. This is an EXACT rational 2-adic integer.
The program checks every parity bit and replays the entire rational cycle
with independent exact fractions. No mystical pattern or guessed history.

Enumerate **ALL 510 parity words** of length 1..8:

| Exact point classification | Source parity programs |
| --- | ---: |
| Noninteger rational 2-adic periodic points | **480** |
| Negative ordinary integer cycles | **14** |
| Positive ordinary integer cycles (trivial 1,2) | **8** |
| Zero, outside positive domain | **8** |
| **Total** | **510** |

These are *parity programs*, not 510 distinct cycles; words can encode
rotations or repetitions of the same orbit. Classification counts are
therefore NOT independent mathematical discoveries.

Exact exemplar orbits:
- Parity word O: x=-1, a negative fixed point.
- Parity word OOE: x=-5 -> -7 -> -10 -> -5.
- Parity word OOOOEOOOEEE (length 11): x=-17, a known negative cycle.
- Parity word EEO: x=4/5, a rational 2-adic cycle that is **not an
  ordinary integer**, even though the rational denominator is odd.
- Parity word OE: x=1 ->2 ->1, the positive terminal cycle.

For every specified finite precision K in {8,12,16,20,24}, produce an
actual POSITIVE integer n congruent to one of these 2-adic points
modulo 2^K, then check the first K parity bits exactly against the
original rational 2-adic orbit. These are mathematically
indistinguishable by their finite parity prefix.

The sample positive shadows all returned to 1 in exact finite arithmetic,
including n=2^24-1 as a lookalike to -1. A finite computed return does
not prove all positive integers converge.

## 2. THE QUANTIFIER BREACH: nonempty finite cylinders ≠ common positive point

For every K>=1, the congruence class

    n ≡ -1 (mod 2^K)

contains infinitely many positive integers.

But the intersection of all these nested classes in the **2-adic
integers** is exactly x=-1. The same intersection with the
ordinary POSITIVE integers is empty.

Thus the naive inference

    "an unresolved cylinder exists at every finite depth"
      => "a positive integer exists that never descends"

IS FALSE. The positive integers are dense in the 2-adic integers but
are not closed. An inverse-limit proof of a permanent odd-parity path
cannot automatically give a positive-integer counterexample.

**The test cross-checks** -1, -5 and -17 against META-003's own exact
8/12/16-bit HOLD cylinders. Those unresolved source cylinders are
compatible with negative infinite 2-adic paths. This demonstrates the
representation-level boundary; it does not prove all unresolved paths
are ghosts. Some might still concern a positive integer. That is the
genuinely unknown global problem.

This matters because even a perfectly valid infinite 2-adic parity
argument could be irrelevant to Collatz on the natural numbers.

## 3. A different kind of nonlocal rank: exact finite terminal basin

Separate from the 2-adic boundary investigation, the engine constructs
a source-verified finite directed transition graph from starts 2..128,
then tests and extends it on heldout starts 129..512.

It does not require a fixed step count; each state n has a **nonlocal
potential** equal to its EXACT minimum remaining number of accelerated
steps before the terminal state 1, calculated by full source trace and
reverse proof propagation.

This is a genuine well-founded ranking on the **finite graph of
actually verified nodes**. Every successor of a nonterminal graph node
is also in the verified graph, and every edge decreases the rank by 1.

| Finite proof memory measurement | Value |
| --- | ---: |
| Starts checked through | 512 |
| Unique transition-closed basin nodes, including terminal | **800** |
| Source transition computations (memoized) | **799** |
| Full independently simulated unreused transitions | **18,043** |
| Redundant source transitions avoided versus naive replay | **17,244** |
| Strong classical memoized graph-traversal baseline | **Exact tie** |

The source trace can travel with its proof, and a new starting point can
reuse an existing verified suffix. This is a working demonstration of
**nonlocal, history-dependent proof reuse** for the finite observed state
graph, not a novel global ranking formula.

Why it isn't a Collatz proof: this ranking is discovered only AFTER a
trajectory has been verified. There is no algorithm that has been shown
to produce such a finite certificate for EVERY starting integer.

## 4. How the two investigations join

The 2-adic frontier keeps an unresolved distinction between
*nonordinary infinite limit paths* and *ordinary positive integers*.

The finite rank engine shows exactly what a genuine, source-verifiable
well-founded termination certificate would look like on a closed domain.

The missing bridge is:

> Can MOTIF construct a nonlocal, well-founded measure on an INFINITE
> positive-integer domain that is verified closed under its transitions
> and cannot be defeated by the 2-adic ghost boundary?

That would require real mathematical innovation or a powerful
new synthesis method. We have not achieved it.

## Integrity, limits and literature

- No Collatz proof, real counterexample or historically novel theorem.
- The parity-word affine grammar and inverse-limit mathematics are known.
- Python source oracles are local; no externally authenticated agent.
- Finite state/rank proofs do not extend to all integers.
- The 2-adic finite-word enumeration is bounded (up to period 8);
  the -17 negative cycle is a separately tested period-11 specimen.
- The naive unmemoized query baseline is intentionally weaker than a
  fair classical memoized baseline; the latter **ties**.
- The code checks real mathematical identities, rejects forged/rehashed
  packet claims, preserves the exact source warnings and next unknown.

Context and independent known mathematics:
- Nicholas Polson & Vadim Sokolov (2026), *On the Collatz Conjecture:
  Martingales, Momentum and Continued Fractions*, Proposition 15.1:
  https://vsokolov.org/books/collatz/results.html
  (an author-maintained, not independently refereed mathematics book).
- Eric Weisstein, *Collatz Problem*, Wolfram MathWorld:
  https://mathworld.wolfram.com/CollatzProblem.html
- Lagarias (1985), classic 3x+1 survey.

## Reproduce (standard Python only)

    python -m unittest discover -s experiments/meta004 -p 'test_*.py' -v
    python experiments/meta004/two_adic_boundary.py > meta004-evidence.json

Dedicated GitHub Actions also verifies inherited META-003/002/001
tests and archives the complete finite nonlocal rank and 2-adic evidence.
