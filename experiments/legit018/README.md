# MOTIF LEGIT-018 — Compositional Capability Discovery

**Status: DRAFT, RESEARCH HOLD. No production merge or deployment.**

## Central experiment

LEGIT-017 generated and tested real graph-reachability and subset-sum
tools. LEGIT-018 asks whether a constrained research agent can **reuse
those actually verified source programs** to tackle a NEW composite
problem, then adapt a verified program when a second new constraint
arrives.

Unlike the earlier source-template selection work, the new research
programs are assembled from several *typed fragments* (inherited
prefilters, graph-specific search, exact weighted-path DP). They are not
free-form autonomous code invention. They implement standard classical
algorithms. Every source is still admitted only if it exactly matches
the declared finite assembly procedure.

This is a two-episode study, with direct and strong conventional
comparators and a deliberately false initial composition.

## Episode A — combine previously distinct capabilities

**Problem:** In a positively weighted directed acyclic graph, does
there exist a route from node S to node T whose weights sum to exactly
K? Simple reachability and global subset-sum do not answer this
question separately.

The source loader first reads the exact real generated LEGIT-017
GRAPH_STACK and SUBSET_BITSET Python source from the prior frozen
artifact, verifies every source SHA-256 and checks each against the
old fixed generator. A forged ancestral source prefix cannot authorize
a new program.

The initial tempting synthesis is mathematically WRONG:

    "a path from S to T exists"
        AND
    "some subset of ALL edge weights sums to K"

The second condition loses path adjacency and therefore has false
positives. The actual candidate engine proposed it, and an
independent exhaustive path enumerator gave a concrete counterexample
(e.g. the tested case S=T=8 and K=11, where the zero-edge path costs 0
and a global edge subset can still sum to 11).

That false program was rejected before it could be selected.

The typed search then evaluated an exact per-query depth-first solver
and a **newly assembled path-cost bitset dynamic program**, in which
weight masks propagate only along valid edges. This is the mathematically
correct way to combine the two kinds of previously available structure.

Five candidate programs were explored; four passed the independent
training checks and a complete small-domain finite falsifier. The
training-only planner selected the exact-weight bitset DP source and
froze its identity before HELDOUT problems were generated.

### Actual Episode A measurements

The heldout cohort contained **12 newly seeded weighted graphs and
576 exact-cost queries**. All answers matched an independent exhaustive
oracle and an optimized conventional DAG index.

Median batch wall time on one GitHub Actions runner (11 repeats):

| Comparator, same 576 queries | Median wall time |
| --- | ---: |
| Independent per-query path enumeration | **1.965 ms** |
| **MOTIF's generated bitset path source** | **0.163 ms** |
| Strong classical indexed DP (only required sources indexed) | **0.158 ms** |

The generated program is much more efficient than per-query
enumeration. It is **essentially tied with the optimized conventional
DP**, which computes the same known bitset recurrence. No superiority
over classical algorithms is established.

## Episode B — adapt the verified source to a new constraint

**New problem:** Can such an exact-weight path be found **while
excluding a specified vertex**?

The source assembly adds an excluded-vertex axis to the Episode A
bitset recurrence. The emitted Python now differs from the earlier
verified source. The candidate is admitted only if the exact earlier
source is available and verified, and all altered answer semantics
pass both independent reference checks and the complete small finite
domain.

This makes real source transfer and extension inspectable, rather
than merely copying a symbolic label.

A matched ablation asks the same Episode B training questions with
and without access to the earlier verified exact-weight path source.

Under the deliberately bounded no-ancestry grammar, the agent can
still construct a **correct per-query DFS**. Under the inherited grammar,
it can also build a precomputed excluded-vertex bitset DP. The latter
is correct, but has substantial setup cost.

**What actually happened:** the training-only selector chose **DFS**
in BOTH conditions.

Heldout: 12 distinct new graphs and 576 queries, all correct:

| Matched new problem | Median wall time |
| --- | ---: |
| Repeated exact reference enumeration | 1.601–1.611 ms |
| No-ancestry selected DFS | **0.241 ms** |
| With-ancestry selected DFS | **0.242 ms** |
| Independently optimized conventional index | 0.345 ms |

This is a negative result for the intended hypothesis on the
declared baseline task volume. The earlier capability was available
and successfully adapted into a verified candidate, but the learner
**correctly declined to select it**, because its preprocessing costs
were not justified by so few queries.

No evidence of additional discovery productivity under these matched
conditions should be claimed.

## Exploratory amortization frontier (POST HOC)

After the initial heldout results, the experiment ran a separate,
explicitly **post-hoc** query-volume study with *new synthetic seeds*
from the same researcher-authored generator. It does not change,
replace, or retroactively re-register the original heldout results.

It compares the previously verified inherited B bitset DP, the
no-ancestry DFS, and a strong independently coded classical index
on the SAME six fresh graphs within each stated volume.

Median wall times (seven repeats, precomputation included):

| Queries per graph | Inherited B bitset DP | DFS without A | Strong indexed classical |
| --- | ---: | ---: | ---: |
| 36 | 0.367 ms | **0.107 ms** | 0.145 ms |
| 144 | 0.452 ms | **0.400 ms** | 0.395 ms |
| 576 | **0.802 ms** | 1.573 ms | 0.835 ms |

The first tested workload where the inherited approach beats the
restricted DFS occurred at **576 queries per graph**. Its near-tie
with the strong classical indexed method matters more than the
large gain over repeated DFS.

The transfer has a legitimate *conditional* payoff: reusing a
precomputation-heavy capability may make subsequent queries cheaper
if enough use arrives. The crossover was explored AFTER the initial
result and is not an independent confirmation. The trial uses fixed,
researcher-authored generated tasks; its timings are exploratory
rather than a statistically powered performance study.

## Reproduction and provenance

Python 3.11 standard library; from repository root:

    python -m unittest discover -s experiments/legit018 -p 'test_*.py' -v
    python experiments/legit018/trial.py --emit

Files:

- challenge.py — two registered weighted-DAG challenge families,
  independent exhaustive-path oracle, strong *query-aware* classical
  bitset index, and complete three-node constraint cases.
- synth.py — loads and cryptographically checks real LEGIT-017 Python
  sources, assembles typed executable successor programs, independently
  falsifies naïve compositions, guards source integrity and provenance.
- trial.py — sequential training-only source selection, two-source
  ablation, new-seed heldout correctness/timing, and transparently
  post-hoc query-volume scaling.
- test_discovery.py — adversarial source forgery, invalid composition,
  finite semantics, classical baseline, source-archive and negative
  evidence tests.
- generated/capability_discovery_report.json — full actual CI-executed
  candidate record, raw timings, counterexamples and no-promotion gate.
- generated/executable_capability_sources.json — exact generated Python
  for the A winner, the verified reusable A bitset candidate, and
  both B selected solutions; hashes anchored to actual LEGIT-017 tools.
- .github/workflows/legit018.yml — dedicated CI tests and source
  archives.

The small exhaustive checker covers all 27 three-node DAG edge
configurations where an edge is absent or has weight 1/2, with all
source/target/cost queries and applicable excluded-node cases. Its
results are not a universal proof over arbitrary graph sizes.

## Boundaries and why HOLD remains the right verdict

1. All new challenge families, algorithmic fragments, finite source
   grammar, source-selection scoring and test generators were authored
   by this project. They are **not independently authored, blind, or
   unfamiliar** in the scientific sense.
2. The program composer may combine its registered operators but
   cannot invent unrestricted Python source, unknown external APIs or
   arbitrary new mathematical primitives.
3. The altered B program was verified, but on the original workload
   it was NOT chosen; no sequence of independently adopted improvements
   has caused the discovery of a new algorithm in controlled conditions.
4. The with/without-ancestry arms have **different search languages by
   design**. That ablation tests access to a declared library, not
   whether intelligence has spontaneously become better at discovery.
5. The apparently useful post-hoc volume threshold depends on repeated
   queries, workload structure and one CI runner. It is not a
   preregistered test of causal open-ended improvement.
6. Even when the inherited engine is faster than naïve enumeration,
   a strong classical index implements essentially the same algorithm.
   No mathematical novelty or general superiority is claimed.
7. Full human code-authoring, maintenance, rollback and real-world
   execution risks remain unmeasured; template matching is not a
   general-purpose security sandbox.
8. No generated source is deployed, auto-merged, promoted or granted
   external tool execution privileges.

**Final research decision:**

    HOLD_NO_INDEPENDENT_CAUSAL_COMPOUNDING_PROOF

What LEGIT-018 *does* demonstrate is useful: real previous generated
capabilities can be loaded under source checks, composed into working
code for a new relational problem, refuted by genuine counterexamples
when naïve composition is invalid, extended to a later constraint and
tested for whether their future reuse is actually economical.

**Next serious experiment:** preregister genuinely third-party-authored
tasks, independently authenticate their source custody, and run
multiple randomized/matched sequential episodes. Measure the complete
cost of discovering and proving a genuinely new tool with and without
prior inventions, against strong conventional engineering portfolios.
Only such evidence could justify a measured causal compounding rate.
