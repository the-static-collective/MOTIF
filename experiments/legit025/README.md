# MOTIF-LEGIT-025 — APERTURE ESCAPE

**Status: RESEARCH HOLD. Stacked draft, not merged.**

The user-approved question is whether MOTIF can recognize a real failure
of its inherited observational vocabulary, formulate and execute a useful
next mathematical question, construct a new tool combination, verify its
results, and carry that tool to a different future problem.

## Actual executable trial

**1. Find a true failure.** Authenticate the original 1998 Read/Wilson
Graph Atlas data distributed in NetworkX **3.4.2** by the same
SHA-256 pin as LEGIT-022. Exhaustively examine its 1,044 seven-vertex
carrier graphs. For each, compute the complete ten connected
graph-homomorphism counts using source graphs of at most four vertices.
Group by degree signature and the whole count vector. Pairs of
non-isomorphic targets with matching whole vectors are true
*finite-grammar* blind spots. This is not evidence of graph equivalence
or proof of any fundamental obstruction: these are different graphs,
but the existing small question language cannot distinguish them.

This scan selects cases *because the old method fails*. It uses the
old observations over the entire external public dataset, so the
result is a deliberately challenging **engineer-authored diagnostic
cohort**, not a random or cryptographically hidden sample.

**2. Ask the next relevant question.**

> Can a one-vertex extension of a previously known four-vertex source
> distinguish the graphs that all old four-vertex probes failed to separate?

**3. Generate an executable method.** Compose every connected four-node
source with a fifth vertex connected to one, two, three, or four old
vertices; deduplicate up to graph isomorphism, preserve the parent,
operator, neighbor-set recipe and stable source identity. The 21
five-vertex connected patterns are exactly the classical grammar
already supported by LEGIT-021's `grammar(5)`. This is **not** novel
mathematics, and *not* autonomous invention of an algorithm. It
demonstrates making a previously dormant method compositional and
available upon detecting an actual problem.

**4. Select from training only.** Sort ten newly identified hard pairs
deterministically by external Atlas IDs. The first four are training,
remaining six held out. Select one of the five-node sources by exact
training coverage using a restricted leaf-extension search. Compare
against two strong controls given exactly the same full 21-source
grammar: canonical source ordering and fully trained classical greedy
ranking. Freeze and SHA-256 hash the full orders *before* evaluating
any heldout 5-node source answer.

**5. Verify and transfer.** Test each frozen policy on:
- The six originally heldout seven-node Atlas pairs.
- Complements of those six heldout pairs.
- New eight-node graphs obtained by adding a universal vertex to
  each heldout Atlas graph.
- A separately sampled, fixed-seed population of 1,000 labeled
  Erdős–Rényi eight-node random graphs, filtered only by matching complete
  old (<=4 source) observation vectors and verified non-isomorphism.
  Eight candidate collision pairs form an additional heldout challenge
  that does NOT descend from the Atlas examples.

The complement and universal-join groups are **synthetic dependent
transformations** of the same external carriers. The random eight-node
group is sampled from a **distinct engineer-generated** population; it is
not independently authored or externally blind. It is deliberately
conditioned on known limitations of the old method, and no five-node
probe outcomes may be read during selection. Check that the old 4-node grammar remains insufficient
and that candidate five-node probes really distinguish the targets.
Both positive and negative answers to every attempted source-question
must agree with LEGIT-021's separate exhaustive vertex-assignment
enumerator, including on eight-node carriers.

**6. Archive a cartridge.** The report includes the full parent
recipe, chosen new source, its original training witnesses and the
frozen source ordering. CI archives full raw investigation receipts.
A stable version-controlled training-only cartridge can be separately
committed after independently inspecting the green run, rather than
inventing evidence in advance.

## Matched controls and honest comparisons

| Policy | Eligible source questions | Train? | What it tests |
| --- | --- | --- | --- |
| No adaptation | all 10 connected sources through 4 vertices | No | Exact observational inadequacy |
| Full classical 5-node grammar | 21 connected sources of size 5 | No | Existing classical search |
| Classical tuned greedy | same 21 sources | Yes, 4 pairs | Strong conventional method |
| Composed leaf-first | same 21 sources; actual provenance from 4-node parents | Yes, 4 pairs | Compositional reactivation and reuse |

All three 5-node policies have equal eventual source expressivity and
the same training opportunity; no claim that MOTIF has outperformed
the tuned classical method. We keep every failed question and CPU time
including independent verification. The choice of priority depends on
the limited training set; the benchmark is nonblind and small.

We preserve the distinction between:
- constructing an additional mathematical *observation*;
- generating a new source graph using an existing construction rule;
- inventing historically original mathematics or a general-purpose
  algorithm (NOT demonstrated);
- proving independently validated, multi-generation self-improvement
  (NOT demonstrated).

## Reproduce

```sh
python -m pip install --only-binary=:all: networkx==3.4.2
python -m unittest discover -s experiments/legit025 -p 'test_*.py' -v
python experiments/legit025/research.py --emit > /tmp/motif-legit025.json
```

The next rigorous boundary is tool-composition learned from independent
challenges in a different corpus/problem family, with a registered
selection rule and costs that include human setup, verification and
maintenance. That is future work, not this result.
