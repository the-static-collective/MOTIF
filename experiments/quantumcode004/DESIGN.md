# QC-004 — THE GRAMMAR GARDENER

**Status:** tested synthetic / classical graph-query program synthesis / local research-only, not merged, installed or dispatched.

## Why this experiment exists

The user's **Quantum Code / IT WRITES ITSELF** thread, traced in [National Treasure's glyph-circuit](https://github.com/the-static-collective/national-treasure/blob/main/cases/quantum-code-glyph-circuit/README.md) and [Daily Slice's decompressor discussion](https://github.com/the-static-collective/the-daily-slice/blob/main/slices/2026/08/2026-08-26/grow-a-world-that-knows-how-to-read-the-seed.md), suggests a careful engineering hypothesis: a system that notices a representation gap may need to grow its *language of possible observations*, not merely choose a better answer in its existing language.

In [QC-003 (PR #188)](https://github.com/the-static-collective/MOTIF/pull/188), when local descriptors failed, the researcher gave the learner exactly **one** new allowable query: whether the ends of a cut edge remain reachable. That works but says little about **selecting among different possible new questions**.

QC-004 replaces that single prescribed query with a generic, typed, bounded relational expression grammar. It also tests the narrower idea of **reusing a learned question as a building block for another**.

Do not confuse this with an historically novel mathematical theory: typed relational algebra, transitive closure, graph grammar search and program synthesis are established classical techniques. The related [LEGIT-021 aperture inventor](https://github.com/the-static-collective/MOTIF/pull/183) already generates *graph-source homomorphism questions* in a different representation; QC-004's contribution is a **composable edge-query AST**, not the first time MOTIF formed mathematical questions.

## Typed domain

The only underlying domain is *undirected simple graphs*, not quantum states or actual written-language glyphs.

Allowed terms (all of type **binary relation over graph vertices**):

| AST constructor | Meaning | Size cost |
|---|---|---|
| E | Original graph edges (both directions) | 1 |
| CUT | Original edges with this candidate anchor edge removed | 1 |
| ID | Identity relation | 1 |
| TC(R) | Directed transitive closure of R (fixed-point reachability) | 1 + cost(R) |
| JOIN(R,S) | Relational composition | 1 + costs |
| UNION(R,S) | Set union of relation pairs | 1 + costs |
| INTER(R,S) | Intersection | 1 + costs |
| DIFF(R,S) | Relative difference | 1 + costs |

The *question* is the Boolean expression: **Does the relation represented by the synthesized term connect these two endpoints?** The cap is five AST nodes. The learner has **no capability to modify the operator set, generate Python to execute, use arbitrary network access or promote outside authority**.

The generator enumerates actual expression trees bottom-up by size; it does **not** choose between three named task-specific code snippets. It may reject trivially equivalent ASTs (e.g. duplicate commutative children) by syntactic identities. The candidate that first separates TRAIN labels is frozen before independent VALIDATE.

## Data and effects

There are **three distinct structural learning questions**, with independently authored evaluator functions:

1. **Alternate path:** is the source edge non-bridging? The mathematical query involves an arbitrary-length alternate path after cutting the edge.
2. **Triangle membership:** does the source edge belong to a triangle? It requires a length-2 alternate route.
3. **Square membership:** does the source edge belong to a four-cycle? It requires a length-3 alternate route after cutting the source edge, not mere reachability.

For each task: 6 synthetic TRAIN, 4 synthetic VALIDATE and 8 synthetic TEST before/after graph episodes. The learner's records **do not contain a named action, an explicit anchor or a rule label**. Source graph and after graph let it infer the changed boundary and canonicalize a two-new-node local transformation. There are two contrasting effects per task. The evaluator's output conventions map an affirmative structural property to removal of an old edge while introducing a fresh two-node route; negative properties retain the old edge while adding such a route. The learner is not directly given that mapping or the evaluator function.

Every pair of source records in a split shares the exact same input graph and different anchor edges. VALIDATE and TEST graph sizes and perturbations differ from TRAIN. TEST effects are never used in search or review, though all task fixtures are authored in this same repository and visible to the human reviewer; this is **not an external blind benchmark**.

All candidate programs must fit all TRAIN receipts, have independent VALIDATE support for both effects, and remain review-only. On test graphs the evaluator uses held-out after-graphs to identify which edge to score, whereas the learner at inference enumerates counterfactual effects for any chosen edge. It does **not** infer which action a real-world actor would take.

## Exact observed outcomes

The GitHub Actions test suite and runtime report provide the actual evidence; the claims below apply ONLY to the fixed synthetic fixture.

| Question | Chosen AST | AST cost | Train ASTs examined | TEST coverage |
|---|---|---:|---:|---:|
| Alternate path | TC(CUT) | 2 | 4 | 8/8 |
| Triangle | JOIN(CUT,CUT) | 3 | 16 | 8/8 |
| Square | JOIN(CUT,JOIN(CUT,CUT)) | 5 | 310 | 8/8 |

- **24/24** covered held-out episode predictions correct across all three tasks.
- All eligible edges on four larger, perturbed TEST graphs per question agree with the **independent classical source-owner evaluator**: alternate path 244/244, triangle 134/134, square 148/148 (**526/526** in total). This control *ties* the system, not loses to it.
- **Cost ablation**: smaller-than-selected grammars cannot fit each task's paired TRAIN observations. In particular cost 4 cannot fit square (in this generator and fixture).
- The search actually synthesizes different expressions from the same generic grammar, rather than receiving one prescribed feature.
- A **Garden** stores three independently validated local question cartridges. At admission it reconstructs TRAIN and VALIDATE review from the supplied receipts; it rejects status-only forged records, duplicate keys and unsupported proposals.
- **Source-pinned question graft:** from previously reviewed triangle expression JOIN(CUT,CUT), generic source-plus-atom composition generates the validated square expression JOIN(CUT,JOIN(CUT,CUT)). The graft's TRAIN-only selection inspects **14** candidate expressions before choosing; the cold, general-purpose search inspects **310**. Its frozen 8/8 TEST predictions agree, and donor-rule pin revocation disables its use.

### About that 14 vs 310 number

This is a *favorable, deliberately constructed sequential task ordering* and two **different search spaces**, not a like-for-like compute comparison or evidence of general, independently compounding research improvement. The cost of the original triangle discovery, quality of the given library and task prior are not normalized. A single reused subexpression happened to cover a later task. Other tasks may not. The graft is a **separate review-only local experiment**, not a proof that the main discovery planner autonomously improves.

## Falsification and negative controls

Adversarial unit tests include: candidate AST forgery, source receipt forgery, wrong split, repeated evidence, mixed TRAIN/VALIDATE evidence, contradictory validation **on the same inferred edge**, unauthorized status, invalid relation AST shape, missing donor, revoked donor pin, altered expected graph, inadmissible unreviewed programs and fixed-cost underfit. Source pins are local hashes and not signatures of real-world witnesses.

**What would invalidate claims:** any test-label use in search, promoting a candidate after contradictory validation, tampered-source replay, a lower-cost AST proving that a declared representation gap was illusory, hidden-action selection disguised as observed agency, or an OOD graph producing systematic mistakes while retaining the same graph semantics.

**What is NOT established:** quantum mechanics, new mathematical laws, real software self-rewriting, actual causal discovery without before/after pairing, full natural-language grounding, external data generalization, an advantage over standard relational program synthesis, general transfer to unmodeled domains or net economic/compute benefits.

## Reproduction

Python 3.10+ and standard library only, stacked on QC-003 and QC-002:

    cd experiments/quantumcode004
    python -m unittest -v test_gardener.py
    python gardener.py

The dedicated workflow is .github/workflows/quantum-code-004.yml. Results should be reported from an actually completed green CI run and unaltered runner logs.

## Next independent falsifier

Give an **outside party** the sealed grammar search, withhold the task logic and code-generated graph distributions, have the outside party author mixed-domain target predictions (e.g. symbolic circuit connectivity, visual diagram relations or causal graph updates), and compare to a separately implemented classical inductive logic programming/SyGuS/graph learner **at identical training examples and compute budgets**. Ask the learner to HOLD whenever no AST in the declared grammar can fit. Randomly permute symbols and introduce noise and unresolved contradictions. Evaluate whether the library genuinely improves results after accounting for prior learning cost. Until then the correct status remains **synthetic, bounded, inspectable**.
