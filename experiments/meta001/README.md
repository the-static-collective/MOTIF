# META-001 — The first genuinely unanswered mathematical question

**Experiment:** Ask MOTIF an established open mathematical conjecture, let the
bounded question/primitive generator try new lawful inquiries, and distinguish
what can actually be *proved* from what remains out of reach.

**Status:** stacked research DRAFT on COLLECTIVE-005 #247 and its unmerged
parents. No production merge, model service, internet browsing agent or MCP
installation. This is deterministic program execution, NOT autonomous LLM
reasoning.

## The question asked

> Does every positive integer eventually reach 1 by repeatedly applying
> 3n+1 when n is odd and n/2 when n is even?

This is the **Collatz conjecture**, a genuinely open problem in mathematics
as checked against published and maintained sources in November 2026.
A rigorous proof or genuine counterexample would be a major result.

This experiment does NOT prove or refute it. More than 2**71 starting
values have *already* been computationally checked by David Barina's
independent project; repeating a few thousand small inputs is NOT new
frontier computation.

## External research context

1. David Barina, "Improved verification limit for the convergence of the
   Collatz conjecture", The Journal of Supercomputing 81:810, 2025,
   https://doi.org/10.1007/s11227-025-07337-0
   — published computational verification below 2**71.
2. Barina's maintained project, https://pcbarina.fit.vut.cz/
   — has continued beyond that historical published limit.
3. Terence Tao, "Almost all orbits of the Collatz map attain almost bounded
   values", https://arxiv.org/abs/1909.03562 — an almost-everywhere
   theorem, not a proof for every positive integer.

These are provenance pointers and independent research. Local Python source
oracles do not access the authors' source servers or replicate large-scale
published computations. No source authentication is implied by a citation.

## Real steps taken by the experimental investigation

1. **Ask the original open conjecture.** Store OPEN/HOLD, not a fabricated
   global answer or derived theorem.
2. Generate a tempting but overstrong local claim:
   "The accelerated map always decreases for n>1."
3. **Falsify that claim** with an exact counterexample: accelerated T(3)=5>3.
   This does NOT refute Collatz; it refutes only the naive monotonicity idea.
4. Change the question *type*. Instead of asking for a global monotonic
   step, construct exact residue-conditioned k-step affine forms for
   integers n mod 2**k. Derive each branch from elementary
   parity, multiplication, addition, exact halving, modular refinement,
   and exact affine comparison.
5. **Prove the symbolic identity for every integer in each residue class**
   (not just a sample): for T^k(n) = (a*n+b)/2**k, parity is fixed
   through the first k steps on n congruent to r mod 2**k.
   Exact induction checks this condition at every step and yields a valid
   rational-affine expression on the entire infinite progression.
   A separate Fraction-based classical recurrence and ordinary
   unaccelerated step implementation crosscheck the algebra.
6. Derive a narrow, *known* universal descent lemma from these primitives:
   if n>1 and n ≡ 1 (mod 4), then T(T(n))=(3n+1)/4<n.
   This proves strict descent within an infinite arithmetic progression
   at that fixed depth. It does NOT imply full Collatz convergence.
7. Exhaustively examine every residue class for each k=1...9, classifying
   those with provable local descent beyond an exact threshold versus
   those still undescended at that *particular depth*. A HOLD is
   deliberately not an assertion that an orbit never descends.
8. Make a local finite source-owner survey and attach complete receipts.
   Reopen the proof packet by recomputing all source evidence, primitive
   derivations and the classification hierarchy.
9. Keep the original problem OPEN. The next relevant research question is:
   **Can every remaining residue class be assigned a finite descent
   certificate without incorrectly treating parity bits as random?**

## A second discovery: why every fixed-step global descent attempt must fail

The program systematically found an ALL-ODD parity residue among the
remaining unsolved classes at **every tested depth**. That pattern admits a
simple general algebraic induction, not merely a numerical observation:

For any integer k>=1 and t>=1, write n=2**k*t-1. Then for 0<=j<=k,

    T**j(n) = 3**j * 2**(k-j) * t - 1.

For j<k the value is odd, so the induction legitimately applies the
odd accelerated step. In particular:

    T**k(n) = 3**k*t - 1 > 2**k*t - 1 = n.

For every chosen common finite horizon k, there exist infinitely many
starting values that are STRICTLY LARGER after exactly k accelerated steps.

This is a rigorous elementary mathematical obstruction to a particular
*proof strategy*: no universal claim that ALL n>1 decrease after the
SAME fixed number k of accelerated steps can be correct.

It is **not** a Collatz counterexample. Those values may, and for sampled
ones do, decrease later. The statement is a known-style elementary
arithmetic identity, not a claim of historic novelty.

This obstruction changes the generated next research question:

> Since no common fixed-step descent argument can work, what
> **variable-time**, well-founded ranking certificate could force all
> orbits eventually below their starts?

That is a sharper unexplored path than simply increasing the same k
forever. The trial explicitly records the failed global proof approach,
the symbolic all-odd family and the next open aperture in its output.

## What this experiment calls 'primitive invention'

The *new* measurement question is **universal descent in a residue class**.
This type of question offers rigorously proved information that finite
orbit sampling alone cannot provide. It is generated by composing the
available arithmetic/parity primitives.

The arithmetic primitives, mod-2**k partition strategy, affine
representation and search depth were **engineer-supplied**. Thus this is
an authored meta-research harness and a composed question grammar,
NOT independently invented mathematics or a general machine that
invents arbitrary axioms. There is no hidden global-answer oracle.

## Strong controls

- Reference operator C(n) is implemented separately from accelerated T(n)
  and checks the exact relation for all tested starts.
- An independent Fraction arithmetic engine must derive the same
  k-step formula for every residue class.
- Universal proof cards are backed by modular parity-induction
  invariants, not extrapolated from finite examples.
- Deliberately false local monotonicity is rejected with n=3.
- Degenerate n=1 and n=2 exceptions stay visible.
- Source-owner fabricated/rehashed step receipts and revision drift fail.
- An altered/rehashed claimed infinite-family lemma fails replay.
- A global Collatz proof is never claimed or inferred from any
  finite source survey.
- Honest HOLD/no result is permitted and required.

## Reproduction

Standard-library Python 3.11+ from MOTIF repo root:

    python -m unittest discover -s experiments/meta001 -p 'test_*.py' -v
    python experiments/meta001/collatz_frontier.py > meta001-collatz-evidence.json

Dedicated GitHub Actions uploads the complete proof-carrying
research-only packet.

## What would genuinely count as advancing the open problem?

A new correct lemma not already known, an independent simplification
of a published proof, a verified infinite-family statement not previously
known, a proven global invariant eliminating every nontrivial orbit, or
a real counterexample with independently checkable source and arithmetic.

Finding one more large number returning to 1 is not a proof.
An aesthetically convincing digit or number pattern is not a proof.
A density result for *almost all* integers is not a universal proof.
Our finite residue certificates are not a global proof.

A credible next stage would bring the original operator-invention
code together with actual theorem checking (e.g., Lean), self-generated
counterexamples, independent standard number-theory baselines, and an
unseen problem family. Every claimed historically novel result would
need independent external scholarly review.
