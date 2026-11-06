# MOTIF GEOM-010 — Self-Revising Reasoning Laboratory

**Status:** isolated Python-stdlib synthetic experiment, built on the **unmerged** GEOM-009 branch. No production integration. This is not a self-authorizing agent, general intelligence, or independent discovery of new mathematics.

## The challenge inherited from GEOM-009

GEOM-009's first rule inventor induces `bud → branch` using labeled demonstrations. It produces 20 false positives on the previous synthetic heldout set because relevant context is absent from its vocabulary. More graph-growth computation by itself cannot fix an omitted variable. GEOM-010 adds a testable **Critic → Inventor → Explorer → Critic** closed laboratory cycle for **conditional** symbolic rewrites.

## Three cooperating roles, one controlled loop

**Explorer** generates hypothetical paths in a finite in-memory graph from the existing GEOM-009 grammar, with or without a proposed context-guarded operator. It reports `PATH`, `SATURATED_NO_TARGET`, `HOLD_RESOURCE_INCOMPLETE` or `HOLD_UNKNOWN_CONTEXT` and never mutates the historical GEOM-008/009 `LivingGraph` grammar. No forced geometry, fixed node count or preferred physical layout is imposed. Each invocation has a finite operation budget. The context is fixed per scratch-graph exploration and does not evolve as a rewrite effect.

**Critic** checks a candidate rewrite against attributed `SituatedCase`s, recording true/false positives, false negatives, missing facts, and **identical visible inputs with opposing labels**. That latter condition is an elementary impossibility certificate *under the available features*. Critic must HOLD rather than invent a sensor reading or silently privilege one witness. Claimed source roots remain unverified strings.

**Inventor** enumerates conjunction guards from the shared positive **development** facts; a candidate must explain *every* positive and negative development example with no abstentions. Search order is by number of guard conditions then lexicographic order, permitting an exact shortest guard **within this grammar**. It uses a finite per-call candidate/time budget and deterministic source/dataset-bound continuation cursors; incomplete search cannot return a purported best rule. The cursor cannot skip an already successful shorter candidate. This is classical decision-rule learning; it is not synthesis of arbitrary operators, negation, time-varying state, disjunctions, recursive programs, or natural-language concepts.

All rules are `PENCIL_ONLY` and `authority: NONE`. Missing required conditions cause **unknown/hold**, not an invented fact. A known mismatching condition legitimately makes the rule inapplicable.

## Two successive revisions

1. The prior GEOM-009 engine proposes the unconditional symbolic rule from separately labeled synthetic demonstrations (`oak`, `pine`, `birch`).
2. First development feedback includes `warm/wet/good` positives, `cold/wet/good` and `warm/dry/good` negatives. The Critic detects 28 false positives. The Inventor produces `moisture=wet AND season=warm` (46/46 development cases).
3. Further synthetic feedback introduces `warm/wet/poor` negatives. The Critic now evaluates the **current two-condition rule** and detects 14 additional false positives. The Inventor recomputes against all development evidence and produces `moisture=wet AND nutrient=good AND season=warm` (74/74 combined development cases).
4. Only **after** choosing the second rule do we instantiate 260 frozen developer-generated cases: 60 positives; 180 complete-feature negatives; 20 incomplete-feature negatives missing the `nutrient` fact. The final rule scores **240 correct, 0 wrong, 20 explicit abstentions**. The unconditional initial rule gets 60 correct, 200 wrong; an always-false predictor gets 200 correct; an independent classical minimal-conjunction learner **ties the revised rule** exactly. These data are synthetic and constructed with the same condition grammar, not independent generalization evidence.
5. Graph exploration reaches `oak branch` from `oak seed` with the conditioned rule in the permitted synthetic context; the rule refuses the same path under the forbidden context and holds when a required fact is missing. This is a local hypothetical graph, not an external action.

## Actual epistemic limits

- **Conditional vocabulary is supplied:** the Inventor never originates a new fact, decides whether features are real, authenticates sources, or reaches into other connected apps. The categories `season`, `moisture` and `nutrient` were explicitly given by the synthetic task.
- Source root labels are not independently verified. Contradictory labels on the same visible input remain unresolved. Some real systems would require a new feature, not another conjunction; the Critic reports this as a blind spot, not a solved challenge.
- All condition operators depend on scope/observer/time/decoder strings being **exactly equal**. This is not an implementation of 3rdi's real authority or access model.
- No autonomous continuous operation or external execution; the loop is explicitly invoked and finite. It does not change a live grammar or GitHub repository on its own.
- Archives of proposed cartridges use GEOM-008's SQLite `LivingGraph` as a PENCIL-only n-ary attribution trace, recomputing exact proposal scores before writing; no THOUGHT-006 PEN promotion.
- No trained T5/LLM observer, unconstrained natural-language symbolic discovery, or authenticated real-world learning. LOADOUT, ALEX and Free Graph integration remains future review work.
- Stronger future falsifiers should include *frozen external data*, covariate shifts, correlated provenance, missing variables, disjunctive conditions, and plain classical decision-tree / SAT / CSP baselines. If geometry adds nothing, use **NONE**.

## Reproduce

```sh
cd experiments/geometry-010
python3 -m unittest -v test_reason_lab.py
python3 demo.py
python3 benchmark.py
python3 interface.py example-input.json
```

All code is Python 3.11+ stdlib. `interface.py` accepts only a local JSON file of at most 2 MB, with exact `parent_grammar`, `initial_rule`, `development`, `work_budget`, optional `seconds`/`cursor`; no network, shell or external side effects. The dedicated GitHub Actions workflow runs the small tests and deterministic examples only. It does **not** repeat GEOM-009's large resource stress experiment.

**Branch stacking:** GEOM-010 → GEOM-009 (#129) → GEOM-008 (#126) → GEOM-007 (#121) → GEOM-006 (#116) → GEOM-005 (#110) and earlier geometric predecessors. None is merged automatically into `main`.
