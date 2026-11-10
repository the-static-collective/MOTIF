# META-007 — Break the frame: Optimize the *language of mathematical discovery*

**Status:** research DRAFT stacked on META-006 PR #265 and its unmerged
predecessors. Collatz is still OPEN. No externally validated new mathematics.

## User-approved task

Instead of simply adding another example, make MOTIF analyze *the family of
operations it uses to generate mathematical objects*. Can an optimizer
design a stronger, proof-carrying inverse Collatz grammar, rigorously derive
the resulting infinite-family coverage, and measure the gain against the
previous real implementation and an equally informed classical solver?

## The actual representation change

META-006 used a binary choice t=0 or1 at each inverse-tree node.
It guaranteed two children at each depth d, but upper-bounded every
branch by the SINGLE worst possible multiplier (8192/3), obtaining the
relatively weak lower exponent

    alpha_old = ln(2)/ln(8192/3) ≈ 0.08760374.

That mixes together two different questions:

- how many mathematically VALID child operations exist?
- how EXPENSIVE is each child, in increasing source-integer magnitude?

**META-007 stops treating unlike branches as equivalent.**

### Exact generalized branch grammar

For any certified odd y>=5 congruent to 2 modulo 3, compute e0 from
the exact y modulo 9:

    y mod9 :    2   5   8
    e0     :    1   2   3.

For a branch symbol t∈{0,...,K-1} choose

    e = e0 + 3*t,
    B_t(y) = (2**(2e+1)*y-1)/3.

The source checks EXACT divisibility and ordinary positive-integer
closure, and requires

    T(B_t(y))=2**(2e)*y.

All generated children remain certified odd integers congruent 2 mod3
and so can branch again indefinitely. Every binary/greater-arity
code is reversibly decoded from v2(T(child)) and its smaller parent.
All even intermediate states are admitted and rank = prior rank+2e+1,
decreasing exactly by 1 on every real accelerated transition.

Now assign a **conservative individual growth cost**

    w_t = 7+6t.

Because e0<=3, every macro child satisfies

    B_t(y) < 2**w_t * y.

This avoids the worst-single-branch bound that was needlessly applied
to every cheap operation in META-006.

## The new question type: weighted combinatorial coding

Let C(L) be the number of DISTINCT inverse-branch words with total
cost at most L. These are actual positive integers, not untrusted
string proposals, because the inverse grammar is injective.

An exact source-independent combinatorial recurrence is

    C(L)=1+sum_{t : w_t<=L} C(L-w_t),  L>=0,
    C(L<0)=0.

The +1 is the empty word. Distinct words decode to distinct actual
positive Collatz predecessors.

Suppose for rational alpha=p/q,

    sum_t 2**(-alpha*w_t) > 1.

Let W=max_t w_t. For 0<=L<W, the base bound

    C(L)>=1>=2**(alpha*(L-W))

holds. For L>=W, substitution into the recurrence and induction
using the stated supercritical weight sum proves

    C(L)>=2**(alpha*(L-W)).

Every cost-L inverse word encodes a positive integer n<5*2**L.
For X sufficiently large, L=floor(log2(X/5)) therefore yields

    |S∩[1,X]| = Omega(X**alpha).

This is a mathematical theorem about the RESTRICTED explicit inverse
family, not a conjectural fit to small enumeration.

## The optimizer ACTUALLY runs

A finite search considers EVERY grammar size K from 2 through 12,
and a prescribed rational exponent grid p/1000, 80<=p<=160.
For each K, it binary-searches the largest mathematically certified p.

**Crucial:** the inequality is NOT trusted to floating-point estimates.

Each candidate power 2**(-p*w/1000) is bracketed by rational integers
z/10**12 and (z+1)/10**12. To certify the bracket, the Python engine
checks both exact enormous-integer inequalities:

    z**1000 * 2**(p*w) <= (10**12)**1000
    (z+1)**1000 * 2**(p*w) > (10**12)**1000.

For the chosen K, SUM of the exact lower bounds exceeds 1.
For the next greater p, the SUM of the exact upper bounds stays below 1.
The optimizer and the classical independent high-precision geometric-sum
checker agree on all grammar candidates.

**The winning constrained synthesis is K=11, p=154/1000.**

Not hand-picked: the exact source receipts preserve every binary-search
decision and the first forbidden higher exponent for each K.
A K=12 grammar also reaches 0.154 but uses more branch operations, so
the predeclared tie-break chooses K=11.

The new **rigorously certified lower bound** is therefore

    |S∩[1,X]| = Omega(X**0.154).

Compare META-006's proved ~0.0876 exponent under its less expressive
grammar/measurement. This is an approximately **1.76-fold increase in
the guaranteed growth exponent**, NOT a 76% increase in all Collatz
convergence or an improvement over known mathematical literature.

The optimizer is optimal ONLY inside this restricted alphabet/cost/grid
search—not over arbitrary inverse-tree algorithms or all Collatz methods.

## Finite independent-source experiments

MOTIF materializes every inverse code of lengths 0..3 in the selected
11-branch grammar:

| Depth | Distinct, source-checked positive integers |
| --- | ---: |
| 0 | 1 |
| 1 | 11 |
| 2 | 121 |
| 3 | 1,331 |
| **Total** | **1,464** |

It calls the **actual META-006 binary decoder** on every constructed
integer. Exactly **1,449** of these generated nodes are new relative to
the previous binary grammar; 15 come from words containing only 0/1.

Every node is also independently checked against the actual accelerated
Collatz forward trajectory and verifies its rank and real macro-path.
The program rejects branch collision, unsupported integer, unjustified
rank, or any off-domain 2-adic ghost.

## Scientific controls

The 2003 Krasikov–Lagarias journal result already established a
lower-bound exponent around 0.84 for the FULL predecessor set of 1.
That is much stronger than our restricted family's ~0.154.
Journal DOI: https://doi.org/10.4064/aa109-3-4 .

A separately implemented classical high-precision geometric-sum
calculation, given the SAME branch-cost grammar and search grid,
produces the SAME winning rational exponents. No performance or
novelty advantage over classic combinatorial optimization is claimed.

There is no general learned operator creation, LLM autonomous mathematical
invention, verified new theorem, positive natural density, global Collatz
proof, source-human authentication, or unrestricted formal verification.

This experiment *does* demonstrate a meaningful machine-executed method
evolution: from counting nodes by depth to counting them by verified
individual construction costs, then designing a family of operations
under an exact proof criterion.

## Reproduce

Python 3.11 standard library, GitHub Actions source pin is the branch:

    python -m unittest discover -s experiments/meta007 -p 'test_*.py' -v
    python experiments/meta007/weighted_grammar.py > meta007-weighted-proof.json

Dedicated CI also reruns META-001 through META-006 regression suites,
full source re-entry, original-history reference and packet upload.

## Next genuine frontier

The current certificate treats all source nodes as though they have the
worst possible e0=3, even though their actual 9-residue states differ.

The next change should replace one uniform cost list with a
**multi-type finite-state source graph and a source-certified spectral
growth inequality** that rigorously transports residue information
through each inverse edge. That will require deeper mod-3^k state
tracking, not merely adjusting the same coefficients. A strong
classical weighted automaton or difference-inequality solver must be
our fair comparator.

Whether this helps beyond known Krasikov–Lagarias bounds is unproved.
