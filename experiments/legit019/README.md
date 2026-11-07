# MOTIF LEGIT-019 — THE TWO-FRONTIER FALSIFICATION

**Status: RESEARCH HOLD. Actual experiments implemented and executed. No new historical mathematics or independently verified recursive compounding claimed.**

We accepted the challenge:

> Can MOTIF autonomously discover genuinely original mathematical truths,
> and can an earlier generation of self-produced discoveries measurably
> increase its ability to make further discoveries on independently
> constructed problems?

This experiment makes both propositions **falsifiable**, and its first
observed answers are mixed and mostly negative.

## Frontier I — mathematical conjecture discovery

The program in algebra.py creates 436 legal symbolic 64-bit bitvector
expressions from a small grammar (variables, constants, Boolean bitwise
ops, addition, logical shifts, complement). These expressions are NOT
hand-written identities.

An unsupervised miner evaluates them on a few initial probes (0,1),
groups expressions that appear equal, and automatically proposes
equations from those coincidences. For each conjectured equation, it
asks **a real, independently maintained Z3 SMT solver** whether any
64-bit input can refute it. If SAT, the actual model is recorded as a
counterexample and used as a new probe. If UNSAT, the equality is proved
within the encoded 64-bit bitvector theory; the program also checks
all 256 eight-bit values as a separate finite regression.

**Observed in the saved passing run:**

- **11 automatically proposed equations verified** by external Z3.
- **1 false conjecture refuted** by a real SAT model and integrated
  into the probe set.
- **3 nonconstant cross-operator equalities** discovered, not merely
  equations with 0 or 1.

Examples of those Z3-verified identities:

    x + x == x << 1              (mod 2^64)
    ~x == (2^64 - 1) XOR x
    x OR x == x AND x

These are standard bitvector algebra, **not historically new
mathematics**. Finding and verifying them via executable conjecture
search is still a legitimate demonstration of automated theorem
discovery *within the chosen grammar*. Historical novelty would
require literature and independent expert review. There is no basis
for proclaiming an undiscovered law from this exercise.

The proof is universal only for fixed-width operations in the modeled
SMT semantics. It says nothing about unrestricted integers, floating
point, or arbitrary software programs.

The solver's exact mathematical formula ASTs, proof statuses, SAT
counterexamples and typed rewriting library are preserved in the
generated receipt. Unproved equalities cannot enter the rewrite
library: every saved equation is re-proven when loaded.

## Frontier II — externally authored 2017 SyGuS challenge

Unlike previous MOTIF task distributions, **the mathematical input
problems here were authored and publicly released by the SyGuS
competition years before MOTIF existed**.

Four selected 2017 bitvector program-synthesis tasks are checked in:

    SyGuS-Org/benchmarks, commit
    13c8deb68a873635879c9a69bc78caebd340f646
    comp/2017/PBE_BV_Track:
      101_10.sl / 101_100.sl
      112_10.sl / 112_100.sl
      100_10.sl / 100_100.sl
      103_10.sl / 103_100.sl

All original source bytes are preserved, and original Git blob SHA-1
hashes are **recomputed locally** to guard against source substitution.
The competition examples are PUBLIC, and these four tasks were chosen
by the experiment's author after seeing some of their small training
sets. They were not secretly sealed, blinded or independently
adjudicated on our behalf.

Two otherwise matched synthesis engines use the SAME enumerative
expression grammar, training examples, maximum candidate count,
observational equivalence deduplication and search algorithm.

- UNASSISTED receives no mathematical identity library.
- WITH_SELF_PROVED_LEMMAS receives the previously generated,
  externally Z3-proved equalities, which it may use to canonicalize
  candidate source expressions. Proof construction and reproving costs
  are measured and charged to this treatment.

For each task, the system sees ten independently published input/output
training pairs and searches for a satisfying expression. It then
**freezes the chosen source** before checking the corresponding
100-example publication. The latter separation is enforced in the
code's data-access sequence, although the files themselves are
already public and accessible, so this is NOT cryptographic blinding.

The control already has strong semantic-signature deduplication. The
math library must beat that baseline to demonstrate a useful
additional research capability, rather than beating a deliberately
weak strawman.

### Actual results

| Public SyGuS-Comp 2017 task | Without previous math proofs | With previous math proofs |
| --- | ---: | ---: |
| 100 | 0/100 | 0/100 |
| 101 | 0/100 | 0/100 |
| 103 | 0/100 | 0/100 |
| **112** | **100/100** | **100/100** |

For task 112, both engines synthesized the same expression:

    NOT(SHL1(NOT(x)))

It matched every one of the 100 published test examples. These
examples are finite and public; they do not constitute a universal
functional specification or a formal proof that the synthesized
function equals the benchmark's intended black-box function on every
possible 64-bit input.

The other three tasks were **not solved** within the configured finite
grammar, and their results were not silently repaired by looking at
the published test labels.

### Did the first theorem discovery improve the later research?

**No.** Across the four preregistered public benchmark tasks, the
inherited lemma library produced **zero additional fully correct
solutions** and reduced no evaluated search counts.

It also imposed measurable overhead. In one passing CI run:

| Computation, four tasks | Recorded CPU time |
| --- | ---: |
| Unassisted total median synthesis search | **39.94 ms** |
| Assisted total median synthesis search, excluding proofs | **57.47 ms** |
| Assisted synthesis including source equation mining and Z3 checks | **96.74 ms** |

These are short exploratory timings on one GitHub Actions host. They
do not establish a general slowdown law. They do establish that this
particular first generated theorem library did NOT pay for itself on
these four independently published problems. The baseline and
treatment used exactly the same search space; canonicalizing simple
algebraic identities brought no additional program discovery under
these conditions.

This is a meaningful **negative result** for the *specific tested
compounding hypothesis*. Better prior discoveries or different task
families might matter; that remains untested.

## Why this isn't a proof of original new mathematics

An SMT proof can verify a theorem but cannot certify that no human has
ever proven it. The three substantive laws above are existing textbook
bitvector identities, not scientific firsts.

Satisfying 100 examples is not proving a function on the entire 64-bit
input domain. Only actual Z3-checked identities are labeled proven in
this experiment.

Similarly, having public challenges created by someone else is not
the same as independent test administration. The experimenter chose
the tasks and implemented the evaluator, so empirical independence is
partial and clearly recorded.

## Reproduce

Run from repository root with Python 3.11 and genuine third-party
z3-solver==4.16.0.0:

    python -m pip install z3-solver==4.16.0.0
    python -m unittest discover -s experiments/legit019 -p 'test_*.py' -v
    python experiments/legit019/trial.py --emit

The second command generates a complete evidence packet at:

    /tmp/motif-legit019-two-frontier-receipt.json

Its results preserve the proposed and formally checked equalities,
actual UNSAT proofs and SAT counterexamples, per-arm timing samples,
training-frozen expression sources, source hashes and heldout scores.
They do not archive every intermediate enumerated candidate expression.

The initial passing run with the 11 cross-checked identities, one
counterexample and four published challenge tasks is committed at:

    experiments/legit019/generated/two_frontier_external_challenge_receipt.json

Tests reprove the archived equations and revalidate the external
problem-source fingerprints. Timing samples need not reproduce exactly
on different machines.

## Adversarial controls and boundaries

The full test suite checks actual external Git blob fingerprints,
missing/incorrect source claims, 64-bit Z3 UNSAT proof replay, real SAT
counterexample evaluation, independent 8-bit exhaustive truth tables,
rejection of forged rewrite rules, illegitimate syntax, search budget
fairness, published test label isolation, source-freeze record hashes,
heldout truth, and measured proof/setup overhead.

This is a deliberately finite, conservative experiment. It does
NOT invent unrestricted algorithms, prove historical mathematical
novelty, infer a calibrated probability of future discovery, build an
autonomous system that merges its own source, or establish two
successive independently administered research gains.

No production code is modified; the PR is stacked as a draft on
LEGIT-018, and no generated source is installed in main.

**Verdict:**

    RESEARCH_HOLD_UNVERIFIED_HISTORICAL_NOVELTY_AND_COMPOUNDING

What the system DID demonstrate is real, inspectable and falsifiable:
it can automatically hypothesize mathematical equalities, receive real
counterexamples, formally prove some identities, and test whether that
self-produced mathematical knowledge helps on independently authored
public problems. On the initial matched trial, **it did not**.

## The next possible experiment

Broaden the expression search to handle conditional and arithmetic
operators from the competition grammar, while charging the increased
compute budget fairly. Use more independent heldout benchmark families
and stronger competing synthesis solvers. For theorem novelty, submit
uncommon externally checked candidate statements for a genuine
literature search and independent mathematical review, rather than
assuming a newly generated equation is new to civilization.

For compounding, compare a sequence of adopted tool improvements across
several genuinely separate challenge episodes. Include failed attempts,
historical priors, proofs, discovery setup and human cost, negative
transfer, and properly blinded external administrators.

**The first honest answer to a difficult hypothesis can be NO.**
That answer provides a better foundation for the next attempt.
