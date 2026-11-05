# MOTIF-002 — Birth of an unnamed verb

## Question

Can repeated before/after observations yield **reusable operators without being told action names or action role positions**, and can these operators compose in an unfamiliar world?

## What's implemented

1. Read explicit `person` / `bike` type declarations and sets of relational facts.
2. Compute the difference between before and after graphs.
3. Locate one changed entity and traverse a bounded 2-hop neighborhood of before-state facts.
4. Infer an ordered set of role variables by following relation positions, independent of names.
5. Group equivalent normalized graph edits across demonstrations, intersect contextual preconditions, require at least two matching examples, and assign an **anonymous structural verb ID**.
6. Reject any induced rule lacking a synthetic `permits` prerequisite.
7. Search counterfactual worlds using those learned operators, with a small declared artificial utility and a three-step cap.

**No action names appear in the training episodes.** Predicates such as `broken`, `skill`, and `permits`, the type ontology, the one-changed-entity restriction, and the utility function are still supplied by the programmer. This is symbolic program induction, *not* a novel neural weight architecture, language-free understanding of the physical world, or genuine discovery of causes.

## Demonstration

Three synthetic repair examples and three synthetic teaching examples, with unrelated people and assets, produce two anonymous operators. An unfamiliar world permits a three-step simulation: helper repairs bike 1; helper teaches owner; owner repairs bike 2. Remove permission facts and the planner has no valid action. Remove the wrenches and it has no repair action.

```sh
python motif002.py
python -m unittest -v test_motif002.py
```

## Hard limitations and important falsifiers

- Correlation is not causation; intersected preconditions can be spurious, and missing preconditions can be accidentally dropped.
- Only one changed entity is supported. Different relation schemas and changed-role structures won't generalize yet.
- Lexical sorting of predicates gives stable role ordering for these controlled examples; symmetric and ambiguous graphs need explicit matching/uncertainty.
- A static two-hop neighborhood may include irrelevant facts or miss distant prerequisites.
- No-op observations are ignored rather than learned as informative failures.
- The permission gate uses *fictional asserted graph facts*. Never equate it with actual consent or authorization.
- Baselines against simpler rule learners, causal systems, and neural systems have **not** yet been run.

## Next test

Present labeled only by `before/after` worlds, mix successful and failed attempts (recording failed attempt intent separately from outcome), and evaluate predictive calibration on held-out combinations. Discover whether compressed event motifs outperform a simple hand-coded transition library on tasks with the same inputs and evaluation budget.