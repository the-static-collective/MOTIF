# MOTIF RING-003 — The Cartridge Hypergraph

**Stage:** isolated draft, stacked on the live RING-002 branch. Synthetic utility optimization and reviewed source-only provenance; **not** demonstrated scientific improvement or permission for external operations.

## Why a hypergraph and not one cartridge → one job?

A cartridge is not a single-purpose tool. One real, pinned research method can have more than one potential application. Conversely, a useful capability might require two or three different cartridges together. A normal pairwise connection is the wrong shape for that.

This experiment represents a typed **directed hypergraph**. Each hyperedge relates a **set of inputs** to a **set of outputs**:

```text
  {language-cartridge, proof-cartridge}
             \                 /
              \               /
                 [HYPEREDGE]
                  /        \
                 v          v
      interpretation-    language-evidence-
      objection-bridge   skepticism
```

- An edge may have one method and multiple output affordances: **one cartridge serves several jobs**.
- An edge may have several jointly required methods and several output affordances: **a composition serves several jobs**.
- The same affordance may be produced by different edges: **one claimed use has alternative approaches**.
- A `TENSION` hyperedge can model a deliberately hypothesized conflict or negative transfer penalty for certain combinations. It is a **concern to test**, not established harm.
- A GitHub branch source is a different node type from an executable method. The source may support multiple *possible-use* hypotheses by inspectable file/line occurrences, but a line containing `proof` does not prove it checks proofs.

RING-003 does **not** infer a relationship from geometric closeness on a display. The hypergraph is an auditable typed incidence structure; a future visualization can render it without becoming authority for a new edge.

## Implementations

**`hypergraph.py` — admitted native methods, hypothetical uses, exact routing**

Uses only these source-pinned RING-002 native methods: GEOM-013, THOUGHT-014, and REASON-006. It declares several plausible *hypothetical* affordances of each and proposed 2-way / 3-way composition edges. The local exact solver enumerates bounded method subsets (up to 12 method identities / 4,096 configurations) and evaluates explicit task-goal value, method cost, and penalties. Every number is designer-assigned. The solver returns an empty method set when no eligible method can justifiably reach a goal. It never treats a simulated "covered" goal as actual task success.

It compares the same declared utility against a myopic greedy single-method-addition baseline and an always-all baseline. On intentionally constructed complementary tasks, neither isolated method gives immediate credit, so myopic selection can miss a valuable pair. This is a **synthetic mathematical counterexample**, not evidence of superiority to strong general planning or empirical cross-method reasoning.

**`candidate_lens.py` — future branch possible-use hyperedges**

For any newly indexed public branch with a locally present exact Git commit, it searches a bounded operator-defined vocabulary through the RING-002 source reader. A branch mentioning `graph`, `question`, `counterexample`, `instrument`, etc., may emit a **many-head, unverified source-word-match** proposal with line-level provenance. No fetched source instructions are obeyed, no branch code is executed, and absence of a term is *not* absence of an actual capability. Each proposal remains `SOURCE_WORD_MATCH_ONLY`, `verified_use: false`, `admitted_for_execution: false`.

**`receipt_bridge.py` — independently executed native methods as separate evidence**

Re-checks the existing RING-002 triad sandbox receipt, original pinned source commits, explicit no-external-action and independent synthetic-world constraints. Each source-native trial is an evidence vertex connected to its method vertex. This does **not** make jointly hypothesized use edges real; no new executable admission or shared-world success is inferred.

**`living_ring.py` — new optional typed hypergraph use**

Live GitHub discovery still precedes any method planning. The caller can provide typed goals and values, receive a many-to-many route, and optionally request an explicit `--native --execute-hyper-selected` RING-002 sandbox run for the selected already-installed methods. The outputs are native **individual** research demos, not a shared-problem result. Only explicitly reviewed pinned triad adapters can execute, never arbitrary newly indexed branches.

## Reproduce

```sh
# Unit controls, adversarial tests and prior-ring regressions
python -m unittest discover -s experiments/cartridge-ring-001 -p 'test_*.py' -v
python -m unittest discover -s experiments/cartridge-ring-003 -p 'test_*.py' -v

# Produce the typed multi-use graph, inspect generated edge tails / heads
python experiments/cartridge-ring-003/hypergraph.py

# Compare declared values/cost against naive one-step and always-all policies
python experiments/cartridge-ring-003/benchmark.py

# Join live branch census to on-demand hypothetical route, no native execution
python experiments/cartridge-ring-001/living_ring.py \
  --hyper-goal interpretation-objection-bridge:12 --hyper-budget 4

# Source-only look at possible additional uses for the exact pinned GEOM-013
python experiments/cartridge-ring-001/discovery.py --offline-frozen --output /tmp/garden.json
python experiments/cartridge-ring-003/candidate_lens.py \
  --catalog /tmp/garden.json \
  --ref experiment/geometry-013-self-redesigning-instrument \
  --prefix experiments/geometry-013 \
  --terms instrument counterexample question

# Native benchmark receipts in Docker only, with ALL external network disabled
docker pull python:3.11-slim
python experiments/cartridge-ring-001/triad.py --output /tmp/triad.json
python experiments/cartridge-ring-003/receipt_bridge.py \
  --triad-receipt /tmp/triad.json --goal interpretation-objection-bridge --budget 4

# Execute only the selected native methods (separate synthetic experiments)
python experiments/cartridge-ring-001/living_ring.py \
  --hyper-goal interpretation-objection-bridge:12 --hyper-budget 4 \
  --native --execute-hyper-selected
```

The native Docker step requires full pinned Git commit objects in the checkout and a usable Docker daemon. The source-only branch scan requires GitHub access, or explicitly `--offline-frozen` for historic data.

## Proven vs hypothetical (do not collapse)

| Statement | Current evidential status |
| --- | --- |
| A method may have several *declared* affordance uses | Implemented typed graph and tests |
| Two or more methods can be selected together | Implemented exact declared-utility subset search |
| One source-only future branch may suggest several uses | Implemented bounded static text lens, inspectable line witnesses |
| Existing three native experiment sources run in isolated Docker | Source-native CI smoke test |
| Those three methods reason effectively about the same source world | **Not demonstrated** |
| A generated candidate-use mapping actually improves real task outcomes | **Not demonstrated** |
| 155 indexed branches are compatible executable methods | **False**: indexed source pointers are not runnable admissions |
| A source checksum grants method or outside-world authority | **False** |

## Next experiment — shared evidence, genuine possible gain

The most important unresolved measurement is **cross-method marginal contribution on the same held-out problem**. It needs a frozen common source-owned task/evidence packet, verified adapters with compatible types, truly unseen outcomes, calibrated uncertainty, independent baseline planners, contradictory-source handling, and measured runtime/negative transfer. Only then can the hypergraph start to update its edge weights from *observed value* rather than mere design assumptions.

The live watcher on `main` continues collecting source-only branch pointers independently of this experimental branch. A new branch can be analyzed without reauthoring the roster. No new branch is automatically executed, merged, or granted permission.
