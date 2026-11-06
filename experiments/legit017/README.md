# MOTIF-LEGIT-017 — THE RESEARCH PRODUCTIVITY ENGINE

**Status: DRAFT RESEARCH HOLD. Main untouched.**

## Question, implementation and limits

Can MOTIF allocate a limited research-tool budget, generate executable
candidate tools, prove their answers within bounded cases, reuse the
tools on previously unseen problem instances, and measure whether
improving the *verification process itself* makes later testing cheaper?

**Yes for a bounded, assistant-authored program grammar.** The resulting
algorithms are classical; there is no independent evidence yet of
compounding autonomous discovery or superiority to optimized classical
algorithm families.

Three distinct engineering task domains are implemented:

- GRAPH: directed graph reachability using precomputed source-to-node
  traversal indexes.
- SUBSET: subset-sum feasibility with either a bitset or a set-based
  dynamic program.
- TEXT: literal substring search or a precomputed substring index.

A finite hand-written grammar emits TWO executable Python implementations
per domain. Tools are compiled and executed only after byte-identical
source-template checks. This is NOT a general Python security sandbox.
Each tool passes independent reference checks across every training
question, every heldout question, and small exhaustive bounded tests:
576 three-node graph cases, 832 subset-sum cases, or 384 short-text
cases per implementation, depending on the family. These finite tests
are regression evidence, not general mathematical certification.

## What MOTIF actually did

The planner evaluated six real executable tools on 18 training
instances (six per family), measuring Python compilation, verification,
and seven repeated execution times. Under a budget of two tool
families and a visibly hypothetical horizon of 64 future batches,
an ordinary exact combinatorial allocator selected precomputed
reachability (GRAPH_STACK) and bitset subset-sum (SUBSET_BITSET).

**The source selection was frozen before the heldout workload.** The
study then generated 36 new-seed input instances containing 2,592
queries and checked every answer from ALL SIX generated algorithms
against separate classical reference implementations. Zero mismatches
were observed.

In a passing CI trial, the median wall-clock time across the same
36-task heldout batch (11 repetitions per implementation) was:

| Implementation | Median batch time |
| --- | ---: |
| Recompute direct reference per question | 83.540 ms |
| **Frozen generated portfolio** | **1.508 ms** |
| Strong optimized classical indexed portfolio | 1.574 ms |

The generated approach is much faster than repeatedly recomputing
unindexed answers but effectively tied with standard classical indexed
methods. The tiny observed difference from the classical indexed
comparator is not independently replicated or statistically
established. Up-front source compilation and independent checks are
recorded separately. Human authoring, deployment and maintenance
costs are not measured.

## The second-order research tool: verification itself

The same experiment generates a **reusable cross-domain witness cache**.
Rather than solving a graph or set problem, the cache reduces the cost
of *verifying the next proposed algorithm* against already computed
independent reference answers.

We tested four processes on the same newly generated tasks and all six
candidate strategies:

- RECHECK: recompute the independent reference for every candidate.
- CACHE: compute independent reference results once, then reuse them
  through generated cache source.
- IMPROVED_CACHE: prime the same generated cache from an independently
  crosschecked **strong conventional reference**.
- STRONG: a separately implemented classical optimized truth builder
  with ordinary Python dictionary caching.

The first naive cache was not competitive with classical preprocessing.
A revised *training-only* decision therefore measured both source-tool
priming strategies, selected the faster one, and froze that choice
before testing the new 36 cases. In the passing study, the selected
mode was IMPROVED_CACHE.

**Every one of 5,184 candidate/query checks was still performed.**
Reusable witness computation reduced expected-answer construction from
5,184 to 2,592 calls across the full six-tool portfolio.

One passing seven-repeat heldout trial measured:

| Method | Median full verification time |
| --- | ---: |
| RECHECK | 174.534 ms |
| Original generated CACHE | 94.044 ms |
| **Revised generated IMPROVED_CACHE** | **10.352 ms** |
| Strong separately implemented classical cache | **9.294 ms** |

That is real measured reduction in redundant experimental verification
work on these cases, and the generated tool can transfer its interface
across graph, subset and text algorithms. It is still marginally
slower than the strong classical reference method. It demonstrates
reusable infrastructure, not a new mathematical law or verified
autonomous research compounding.

## Evidence provenance and strict HOLD

The code reads the actual committed LEGIT-016 source-anchored
empirical witness, requiring its previous negative result to remain
intact:

    observed_compounding_rate = NOT_ESTIMABLE
    promotion_decision = HOLD_NOT_ENOUGH_INDEPENDENT_EVIDENCE

A better benchmark in LEGIT-017 does not retroactively convert a
rejected LEGIT-014 code change into a successful realized dividend.

The current experiment's research decision remains:

    HOLD_RESEARCH_ONLY_INDEPENDENT_COMPOUNDING_NOT_DEMONSTRATED

There is no proof that an earlier adopted improvement caused the later
discovery of a genuinely new algorithm at lower cost. We have not
obtained independently authored challenge tasks, authenticated external
source custody, or measured total research and integration labor.

## Reproduce and inspect

From the repo root, Python 3.11 standard library only:

    python -m unittest discover -s experiments/legit017 -p 'test_*.py' -v
    python experiments/legit017/benchmark.py --emit

The second command emits full measured data and generated source in:

    /tmp/motif-legit017-research-trial.json
    /tmp/motif-legit017-generated-tools.json

The dedicated GitHub Actions job archives and exposes the original
source/result packets. Committed frozen artifacts are:

- generated/research_productivity_report.json — the original real
  training-and-heldout benchmark, raw CPU/wall data and ablation.
- generated/executable_research_tools.json — actual emitted Python
  source, SHA-256 commitments and training-frozen selection.
- tasks.py — three registered task generators, independent per-query
  exact references and tuned classical comparators.
- toolsmith.py — six static source templates, compilation gate, bounded
  exhaustive independent checks.
- metatool.py — one generated cross-domain verifier cache and direct,
  older-cache, improved-cache and strong-classical ablations.
- benchmark.py — actual two-tool budget, freeze-before-heldout decision
  and complete performance accounting.
- test_productivity.py — adversarial source and semantic tests.

**What the tests do NOT establish:** independently sourced task
distributions (all are research-authored), general proof beyond the
small exhaustive domains, performance on multiple machines,
accounting for human software development or maintenance, or a causal
series of improvements which themselves speed future discovery.

The next serious frontier is an independently preregistered challenge
and a multi-episode randomized or matched study in which a tool
created during one episode actually changes the measured difficulty
or discovery cost of a later *different* research problem. Compare
with tuned conventional toolchains and include full engineering,
proof, rollback and opportunity costs.

**A witnessed shortcut in verification is useful; a demonstrated
recursive improvement in discovery is a harder claim. LEGIT-017 makes
that difference executable and inspectable.**
