# META-006 — Branching inverse grammar with a polynomial coverage guarantee

**User-approved next frontier:** META-005 produced an infinite, positive,
transition-closed family with a strict algebraic rank, but its member count
was only O(log(X)^2 * loglog(X)), hence density zero. Can a new, still
exactly source-verifiable inverse-operation grammar prove STRICTLY GREATER
asymptotic coverage while refusing to admit unsupported positive integers?

**Executed result (research only): YES, within an engineered grammar.**
Our construction gives an explicit infinite subset with
Ω(X^α) distinct positive members below X, α=ln(2)/ln(8192/3)
≈ 0.08760374, asymptotically stronger than META-005's polylog
upper bound. This does not imply positive natural density and does not
prove the Collatz conjecture.

The underlying inverse-tree logic and modular arithmetic are classical;
this is not a claim of historically novel mathematics.

## 1. The changed question language: branch after even segments

META-005's odd predecessors were an uninterrupted initial run into a
power of two. Its certificate language held only a special sparse
subfamily of the genuine inverse Collatz tree.

META-006 gives the investigator a NEW recursive macro operation that
allows an odd inverse operation, followed in the forward direction by
an even block, followed by another already-certified odd state.

Start with seed y=5, known exactly to reach 1 in 4 accelerated steps.

For any odd positive y≡2 (mod 3), define

    B_e(y) = (2^(2e+1)*y - 1) / 3.

The verifier derives an exponent from y modulo 9:

    y mod 9 = 2  => e0=1
    y mod 9 = 5  => e0=2
    y mod 9 = 8  => e0=3.

These choices satisfy exactly

    2^(2e0+1)*y == 7 (mod 9).

Choose an independent branch bit t∈{0,1}, and set e=e0+3t.
Because multiplying the exponent by an additional 6 does not change
2^(2e+1) (mod 9), every child B_e(y) is an ODD POSITIVE INTEGER
congruent to 2 (mod 3). It can branch again indefinitely.

And crucially the EXACT forward transition is

    T(B_e(y)) = 2^(2e)*y.

This is followed by 2e ordinary even halves, returning to y.

Thus, for each finite bit-word t1,...,td, a unique new odd positive
integer is constructible, and its *rank is known symbolically*:

    R(5) = 4;
    R(B_e(y)) = R(y) + 2e+1;
    R(2^h*y) = h+R(y).

Include the even lifts of every generated odd node, all powers of two
and terminal 1. This produces an INFINITE, positive, transition-closed
family with exactly one rank decrement on every nonterminal
accelerated Collatz step. The rank is computed by inverse-code
decoding, not by first tracing an entire orbit.

The reverse code can be recovered uniquely:
for generated x, T(x)=2^(2e)*y with y odd, so
e=v2(T(x))/2 and y=T(x)/2^(2e). The strict inverse expansion
B_e(y)>y prevents cycles and preserves word uniqueness.

Example new members OUTSIDE META-005's former grammar:

    seed 5
      bit 0 -> 53
      bit 0 -> 2,261
      bit 0 -> 6,029

Their forward orbits include even blocks and the already-verified seed,
so they do not have META-005's simpler unbroken odd prefix to a power
of two. The code independently asks the old META-005 recognizer whether
each new member was already certified, with explicit HOLD for nonmembers.

## 2. The quantitative asymptotic advantage (algebra, not graph fitting)

For every branch y->B_e(y), e<=6. Therefore

    B_e(y) < (2^13/3)*y = (8192/3)*y.

A code of depth d produces a positive number below
5*(8192/3)^d. Every depth-d binary word is unique, and there
are exactly 2^d such words. Consequently

    |S intersect [1,X]|
       >= 2^floor(log_(8192/3)(X/5))

for all sufficiently large X, with conservative boundary conventions.

Thus,

    |S intersect [1,X]| = Ω(X^(ln2/ln(8192/3))).

This is a mathematically PROVED polynomial lower bound from a fixed
two-branch reversible arithmetic construction; it is not an empirical
extrapolation. It eventually exceeds the O(log^2 X loglog X)
upper bound already proved for META-005's restricted family.

The source engine exhaustively checks binary proof codes through depth
10: 1,024 distinct positive odd states at depth 10 and 2,047
in the classical breadth-first inverse-tree through depth 10.

A fully equal-information classical inverse-tree enumerator gets
the SAME exact results. We do not claim to beat classical math.

## 3. Concrete comparative coverage from the actual older source verifier

Finite checks compare every generated odd/even-lift member against the
**actual META-005 recognizer**, rather than assigning new labels by
hand. Verified old counts and strictly newly certified extras:

| Positive integers <=X | Old META-005 | NEW outside old | Guaranteed union |
| --- | ---: | ---: | ---: |
| 64 | 18 | 1 | **19** |
| 512 | 38 | 4 | **42** |
| 4,096 | 64 | 9 | **73** |
| 16,384 | 85 | 18 | **103** |

**Every one of the extras** receives a symbolic rank and is independently
rechecked by a completely separate direct forward Collatz implementation.

These raw fractions remain tiny. Polynomial LOW growth is not a
positive density proof and does not settle Collatz.

## 4. Adversarial and provenance controls

- Modulo-9 branch divisibility is checked before admitting a number.
- Every binary code is decoded from the actual forward source transition;
  forged or colliding words are rejected.
- All generated finite even and odd transitions decrease rank exactly 1.
- The induced closure includes intermediate even states; no hidden
  skip over unverified source transitions.
- Original META-005 recognizer independently refuses every claimed
  NEW member until the expanded grammar supplies a real certificate.
- A known-convergent nonmember n=7 remains explicitly HOLD.
- Rehashed false claims of universal Collatz or positive natural
  density are refused by rebuilding the proof packet.
- Classical breadth-first inverse graph, with the exact SAME two
  branch choices and depth budget, matches the synthesized words.
- The GENERAL unbounded proof is a human-reviewable elementary
  induction, NOT Lean formal verification.
- No production merge, genuine autonomous axiom invention, or
  source-owner human identity authentication.

## 5. What's still genuinely unknown?

We have proved a strictly more expressive and quantitatively faster
growing positive-integer family, without assuming global convergence.

But Ω(X^0.0876) is still a very weak lower bound, and nothing here
establishes a positive proportion of all positive integers, much less
all positive integers. Classical inverse-tree theory contains many
stronger results; the growth argument is not claimed historically new.

**Next frontier:** can the model discover and justify a new inverse
grammar or a stronger combinatorial coding argument with a quantitatively
better exponent, using equal-budget classical baselines and genuinely
independent historical results?

## Published mathematical context and comparison ceiling

The polynomial lower bound obtained here, exponent ≈0.0876, is only a
**relative improvement over META-005's highly restricted family**. It
is NOT close to the best known results for the entire predecessor set
of 1. Krasikov and Lagarias proved in *Acta Arithmetica* 109 (2003),
237–258, that for all sufficiently large X, **at least X^0.84 positive
integers ≤X reach 1** (more generally the predecessor count of any
fixed positive a not divisible by 3). DOI:
https://doi.org/10.4064/aa109-3-4
Official journal page:
https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/109/33/81918/bounds-for-the-3x-1-problem-using-difference-inequalities

That established theorem is MUCH stronger numerically than this
elementary binary subtree bound, but applies to the full convergent
basin rather than our explicit reversible-word subfamily. Therefore
neither a new world-record exponent nor new published mathematics is
claimed here. The value of the experiment is source-checkable
generation of a richer INFINITE proof-carrying family, strict closed
rank and a valid comparative asymptotic certificate.

A genuinely competitive next experiment would reconstruct published
difference-inequality bounds and a strong classic inverse-tree
baseline before testing any new weighted branch grammar.

## Reproduce

Stacked draft on META-005 #263 / META-004 #259, no merge.

    python -m unittest discover -s experiments/meta006 -p 'test_*.py' -v
    python experiments/meta006/branching_inverse.py > meta006-branching-inverse-evidence.json

CI also runs all 72 inherited META-005/004/003/002/001 tests.
Complete evidence JSON contains actual source rankings, code-word witness
checks, algebraic growth proof, coverage comparisons and all open limits.
