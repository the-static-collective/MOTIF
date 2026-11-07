# MOTIF LEGIT-022 — THE ATLAS APERTURE DIVIDEND

**Status: RESEARCH HOLD.** We tested two ambitious claims: whether the
system can discover historically original mathematics, and whether
previously invented mathematical perspectives causally increase its
later research productivity. The observed data support bounded reuse
and known mathematical conjecture validation, **not either stronger
claim**.

## Stronger external-origin test

Unlike the internally created graph scenarios of LEGIT-021, this
experiment uses independently originated carriers from Ronald C. Read
and Robin J. Wilson's *An Atlas of Graphs* (1998), as distributed by
pinned NetworkX 3.4.2. The dataset has 1,253 unique graph types and
1,044 types with seven vertices. The actual external compressed
atlas.dat.gz source bytes are pinned by SHA-256:

    73fc416df0164923607751cb759f4ae81deb5f6550bf25be59c86de3b747e41d

All challenges come from **42 selected pairs** with identical degree
multisets, sampled from 402 eligible Atlas pairs. The first 14 are
training; the next 28 are held out. Pair selection and the shuffle
seed (22022) are fixed before any probe-homomorphism outcome is read.

**Independence caveat:** Original mathematical graph data were created
outside this project. The pairing protocol, task objectives,
algorithms and test operation were authored here. The test is not
externally blinded or independently adjudicated.

## Mathematical conjecture trial

A source-graph grammar enumerates all **18** nonisomorphic undirected
simple graph patterns with up to four vertices. Ten are connected and
eight disconnected. A small symbolic search tries four ways to
combine component homomorphism counts:

    PRODUCT, SUM, MAX, MIN

On the preregistered Atlas training graphs, only PRODUCT survived.
SUM, MAX, MIN each produced actual counterexamples.

The surviving relationship is:

    hom(F1 disjoint_union F2, G) = hom(F1,G) * hom(F2,G)

The program checked every disconnected source with an independently
implemented exhaustive vertex-assignment enumerator, and recorded a
general mathematical explanation: homomorphisms on disjoint source
components restrict/glue uniquely, so their cardinalities multiply.

**This is established classical graph mathematics.** The general
combinatorial reasoning was supplied by the program author; it was
not generated as a new formal historical proof by MOTIF.

A more ambitious conjecture was deliberately challenged:

    "Same degree sequence implies every tree-homomorphism count agrees."

The independently originated Atlas graphs **G897 and G898** refute it:
they have identical degree multisets

    [1, 3, 3, 3, 4, 4, 6]

but their four-vertex path-homomorphism counts are **362 versus 360**.
That falsifier is genuinely computed, not a synthetic assertion.
This result, too, is known mathematical behavior, not a newly
discovered theorem.

Lovasz's graph-homomorphism characterization (1967) predates all
these experiments and gives broader existing results.

## Matched prior-improvement trial on 28 external-source pairs

We loaded the actual LEGIT-021 source receipts for three previously
generated observations: triangle, three-leaf star and four-cycle.
The source program matches and original mathematical counts were
replayed, rather than trusting an unverified label.

Four variants received **the same heldout pair tasks**:

| Variant | Total questions | Actual hom calls | Uncached median CPU, 3 runs |
| --- | ---: | ---: | ---: |
| All 18 patterns, including disconnected | 283 | 566 | 131.82 ms |
| Canonical connected-only ordering | 139 | 278 | 56.52 ms |
| **Prior LEGIT-021 questions before fallback** | **60** | **120** | **50.38 ms** |
| **Strong conventional training-optimized priority** | **56** | **112** | **38.23 ms** |

All **28/28** pairs were distinguished by each arm; successful
observations were independently checked. Query counts include
unsuccessful probes, not just winning ones. The CPU figures were
actually executed with no global cached-answer benefit, three runs
per arm with rotated execution order. The complete experiment also
records raw CPU/wall samples and a consistent 7^k assignment budget.

The results cut both ways:

* **There is real transfer** of existing mathematical questions onto
  external-origin mathematical objects. Previously generated probes
  reduced query count from 139 to 60 relative to canonical ordering.
* The **strong classical planner wins** under matched source grammars
  and training conditions: 56 questions, lower uncached CPU.
* The known product law removes redundant disconnected source probes,
  but the stronger classical control already uses that optimization.
  The 18-source comparison is deliberately an inefficient ablation.

We separately measure current theorem-mining and finite-checking
compute, but the human engineering costs, original LEGIT-021
discovery costs, maintenance and rollback costs remain unavailable.
An end-to-end compounding rate cannot legitimately be calculated.

## Program and reproduction

Python 3.11 with pinned NetworkX 3.4.2:

    python -m pip install --only-binary=:all: networkx==3.4.2
    python -m unittest discover -s experiments/legit022 -p 'test_*.py' -v
    python experiments/legit022/trial.py --emit

Files:

- atlas.py — original external data provenance and SHA-256 pin;
  degree-matched 14/28 independent-carrier source cohort.
- theorems.py — mined product conjecture, concrete false alternatives,
  independently enumerated finite source checks, and degree/tree
  over-generalization counterexample.
- trial.py — actual LEGIT-021 source revalidation, training-only
  cost-sensitive policy selection, four matched heldout arms, per-probe
  evidence and uncached CPU/wall timings.
- test_atlas_dividend.py — adversarial data, theorem, source-provenance,
  semantic and performance checks.
- generated/atlas_dividend_witness.json — frozen GitHub Actions
  measurement with aggregate source/task receipts.
- .github/workflows/legit022.yml — pinned external graph package,
  complete executable trial, tests and archived full raw receipts.

All benchmark probes are graph-homomorphism questions over finite,
publicly reproducible graphs. This is not a general natural-language
or open-world research agent.

## Scientific verdict

**New theorem claim:** NOT established. One true well-known
factorization identity was rediscovered in a finite grammar and
a false over-generalization was independently refuted.

**Independently verified recursive self-improvement:** NOT established.
Inherited probes had a useful effect against a fixed ordering,
but they were slower and less economical than an optimized classical
learned policy. There is only one matched downstream experiment,
authored by the research team, without independent task
administration or full earlier engineering costs.

    RESEARCH_HOLD_NO_VERIFIED_HISTORICAL_NOVELTY_OR_RECURSIVE_COMPOUNDING

This is useful evidence rather than a rhetorical claim of
self-improvement. A credible next test needs independent mathematical
challenge authors, preregistered unknown tasks, audited sequential
adoption, full discovery and verification labor costs, and comparison
against contemporary tuned mathematical-search methods.
