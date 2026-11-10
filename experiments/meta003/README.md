# META-003 — Nonlinear/stateful ranking: adversaries, CEGIS and 2-adic decision trees

**User-approved follow-up to the genuine unsolved Collatz experiment.** Stacked
unmerged research DRAFT above META-002 #255, META-001 #250 and the COLLECTIVE
source/question papers. No production merge or broad autonomy.

## What was genuinely attempted

The question is still:

> Does every positive integer eventually reach 1 under Collatz?

We deliberately change the kind of measurement away from the linear
residue-affine rank proposals that failed in META-002:

1. **Counterexample-guided nonlinear rank synthesis (CEGIS).**
   Fit the stateful polynomial potential
   \(V(n)=n^p+b_{n \bmod 16}\) with p=1, 2 and 3, where integer offsets
   are actually found by a Bellman-Ford difference-constraints solver,
   not hand-picked. Fit to the first thirteen starts (2..14).
   It really does strictly decrease on every training transition.
   Then evaluate out-of-sample; both n=15 and n=17 force refinements;
   the example eventually becomes infeasible. Preserve every candidate
   and its falsifying source observation.

2. **General mathematical obstruction to any finite-residue positive
   monotone-size rank.** For any modulus m, and t>=1, take

       n = 2*m*t - 1,
       T(n) = 3*m*t - 1.

   Then T(n)>n, but both integers are congruent to -1 modulo m.
   Consequently for any strictly increasing f, positive class weights
   w_r, and fixed real class offsets b_r, the potential

       V(n) = w_(n mod m)*f(n) + b_(n mod m)

   cannot strictly decrease on *every* accelerated Collatz step:
   the state label does not change while the size increases. This
   includes logarithmic, quadratic, cubic and similar monotone-size
   state corrections. It does NOT reject a nonlinear/nonmonotone rank,
   a variable-time proof, or arbitrarily large/nonlocal state.

   This self-loop-type argument is elementary and related to the known
   literature on Collatz 2-adic parity and weighted residue graphs.
   **No historically original theorem is claimed.**

3. **A genuinely different stateful proof object: finite 2-adic
   decision tree over mathematical possibilities.** META-002 left
   226/4096 residue classes unresolved at K=12. Rather than extending
   EVERY already-certified class to K=16, carry the original proof
   for each covered parent to all 16 descendants, and divide only
   the 226 unresolved parents into 16 candidate subclasses each.

   Results at precision K=16:

   | Exact classes mod 65,536 | Count |
   | --- | ---: |
   | Previously proved by a K=12 ancestor | 61,920 |
   | Previously unresolved, **now certified** by deeper exact descent | **1,502** |
   | Still unresolved | **2,114** |
   | Total independently verified certified infinite families | **63,422** |
   | **Total** | **65,536** |

   The narrow frontier executes 226*16=3,616 new modular-class
   inquiries, not 65,536, because source-owned ancestor proofs are
   reusable. This beats brute-force recomputing already-covered families
   but **does not beat** an equally informed classical branch-pruning
   method; the independent direct-orbit/odd-count classical comparator
   agrees on every new class.

   Each successful certificate is an EXACT affine identity plus a
   strict inequality valid for every member n>1 of that infinite
   arithmetic progression; it is not merely a finite experimental
   trajectory. Refinement from 12->13 produces 85 new certified child
   classes; 12->15 produces 513. All failures are kept.

4. **Adversarial 2-adic continuation defeats EVERY fixed-depth cover
   of these 226 unresolved parent classes.** At base K=12, the 226
   held parent classes have no decreasing affine slope during their
   first 12 accelerated steps. For every subsequent j, the two
   residue lifts r and r+2**j have opposite parity at T**j, because
   their T**j values differ by odd factor 3**(number of prior odd steps).
   The adversary therefore picks the lift whose next parity is ODD.
   It can repeat this construction to any prescribed finite depth K.

   The original 12 steps have affine slope >=1 and nonnegative offset,
   so no integer in that cylinder drops below its start during the
   prefix. Every newly selected odd step grows the iterate and its
   affine slope (multiply by 3/2). Thus for **any fixed K** there is
   a descendant *infinite arithmetic progression* inside each
   unresolved parent that still has no first descent by that depth.

   **No finite-depth tree that attempts to prove strict first-descent
   within its maximum depth can completely cover such a parent.**

   This is a negative result about the available local-descent proof
   method, not a proof that individual integers diverge, not a solution
   to Collatz, and not a no-go for fundamentally different invariants.

## New next question from the failure

> Can a truly well-founded nonlocal or unbounded-memory progress
> certificate cope with the adversarial continuation of parity bits
> without assuming stochastic independence or monotone size?

This is the next useful change in question type. Merely searching more
residue bits or adding another strictly increasing finite-state size
correction cannot supply a universal guarantee.

## Proof and verification

- The stateful rank *fit* is checked on all finite training constraints,
  and CEGIS records actual failing heldout transitions and eventual
  constraint infeasibility.
- The expanding same-residue Collatz self-loop is derived algebraically
  and crosschecked on independent integer inputs and moduli.
- Every *new* residue-class proof is crosschecked against a second
  independent direct-iteration parity-product method and checked on
  several different integers within the infinite class.
- Each of the 226 hold parents has a concrete adversarial descendant
  with a preserved proof of nondrop for EVERY number in that descendant.
- Re-entry regenerates and rechecks the source facts, hard failures and
  proof tree from its parameters; checksum-only changes do not pass.
- The archived result is **research-only** and not admitted automatically.

## Scientific limits

The Collatz conjecture remains OPEN. The original exact parity-vector
and finite-stopping-time methods are classical. No new mathematical
theorem, general autonomous primitive invention, live external source,
or superiority over a strong same-information classical solver has
been demonstrated. Modest local arithmetic budget, engineered examples
and publicly reconstructible source data.

Context:
- Eric Weisstein, Collatz Problem / Stopping Time, MathWorld.
- Known 2-adic parity vector correspondence (Terras; Bernstein–Lagarias).
- Polson & Sokolov (2026), *On the Collatz Conjecture: Martingales,
  Momentum and Continued Fractions*, reports related finite-residue
  logarithmic-potential cycle barriers; an external manuscript,
  not independent verification of this code.

## Reproduce

Standard library Python 3.11+:

    python -m unittest discover -s experiments/meta003 -p 'test_*.py' -v
    python experiments/meta003/invariant_stress.py > meta003-stateful-ranking-evidence.json

The dedicated GitHub Action also runs inherited META-002/META-001
regressions and archives an audit of the full stateful subtree.
