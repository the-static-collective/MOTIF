# MOTIF-006 — THE COMPOSITE VERB
## When a demonstrated sequence becomes a new proposed operation

**Research question:** Can MOTIF induce a reusable, anonymous *macro-operator* from repeated observed graph-change trajectories, then recursively compose that macro into another macro while preserving the exact prerequisites, possible outcomes, and source identities of every constituent operation?

**Status:** Executable symbolic experiment, not a trained neural architecture, autonomous tool builder, proof of causality, real-world capability, verified human authorization, or independent field observation.

## The conceptual transition

MOTIF-001/002 learn and group single state transitions. MOTIF-003 asks which new transformations they enable. MOTIF-004 records predictions contradicted by observation. MOTIF-005 proposes a new *derived* relational predicate.

**006 changes the unit of planning itself:** a trace made of multiple previously learned transformations can be abstracted into a reusable, source-pinned operation. That new operation can be a constituent of another induced operation.

\`\`\`text
synthetic trace [teach, repair A, repair B]
     |
     +--> macro-A := [teach, repair A]
     |                 (= two existing graph rewrites)
     |
     +--> macro-B := [macro-A, repair B]
                       (= three source graph rewrites)
     |
     +--> new held-out world (different identities)
                       |
                 source-checked replay
                       |
                identical terminal graph
\`\`\`

The names **macro-A** and **macro-B** are explanatory labels. Their actual identifiers are anonymous deterministic hashes of their definitions and dependency pins. The learner does not receive the names or fixed sequence of operator IDs to recognize. The synthetic training traces, however, **do** supply the demonstrated sequence and explicit role assignments from MOTIF-002's planner. MOTIF-006 therefore **compresses demonstrated skills**; it does not spontaneously discover new unseen plans.

## Why this is more than hiding three calls behind a function name

For each repeated trajectory, the compiler:

1. Replays all actions from the original, explicitly synthetic before-state and rejects a trace if its independently supplied after-state disagrees.
2. Tracks entity identities *across* steps, extracting shared typed roles without depending on their literal names.
3. Compiles each source operation into role-relative macro form, including all source prerequisites and aggregate added/removed relations.
4. Separately fingerprints every dependency's **semantics** (role types, preconditions, effects; plus nested macro program and pins), not just its mutable name.
5. Groups identical anonymous programs across at least **two** demonstration traces.
6. Treats any resulting macro as a **candidate-only planning abbreviation**, with a bounded total expanded length.
7. At evaluation, checks the actual source fingerprints, **replays every nested primitive precondition**, and independently checks that the candidate's advertised net graph change matches the replay.

The result has inspectable lineage and no independent authority.

## Controlled demonstration

Three training traces are role-renamed copies of **one** synthetic MOTIF-002 planning example: teaching Jo, repairing bicycle 1, and repairing bicycle 2. This is **not three independent human demonstrations**; the repetition tests stable abstraction under renamed identities, not statistical learning from independent sources.

- First macro: two underlying primitive rewrites.
- Nested macro: first macro plus another rewrite = three underlying primitive transitions.
- Held-out test: a graph with unseen entity names but the same structure.
- Output: a *single macro invocation* computes the identical state reached by three checked primitive calls.
- Objective: matches the previously declared **toy utility of 24**, not a human value measure.
- Remove an intermediate fictional permission relation or an available tool: the composite fails closed.
- Change any source primitive or nested macro semantics after induction: the composite refuses replay.
- Falsify the macro's published effect, create a dependency cycle, exceed limits, or alter the claimed observed outcome: it refuses.
- A complete macro replay never mutates the input observed graph.

### The critical accounting distinction

**One macro call ≠ one physical action.**

A nested macro still requires all three synthetic source transformations. The evaluation does not prove faster physical execution, lower compute cost, automatic tool construction, learned policy optimization, or any new real-world ability.

What is compressed is **the representation of a verified-looking synthetic sequence within the planner**. The "verification" is against toy source definitions and constructed observations, not external reality.

## A compact formalism

For primitive source operators \`a,b\` with role bindings, let \`T_a(G)\` denote the simulated rewrite if all typed prerequisites hold.

A macro \`M=[a,b]\` denotes the function:

\`T_M(G) = T_b(T_a(G))\`

and is **undefined** when either constituent is unavailable.

A nested macro \`N=[M,c]\` denotes:

\`T_N(G) = T_c(T_b(T_a(G)))\`

Thus a novel macro can become a component of a second macro without erasing the decomposition. It is always transparently expandable into the original constituent graph rewrites.

Required properties:

- **Sound replay:** \`T_M(G)\` agrees exactly with constituent replay wherever admitted.
- **Hold:** no constituent guard may be bypassed.
- **Provenance pin:** source semantic changes invalidate previously induced macros.
- **No ontology promotion:** a macro candidate is not a verified ability, a permitted real-world command, or a new causal law.
- **Boundedness:** maximum expanded primitive count and graph-grounding search budget are explicit.

## Evidence

Run with Python 3.10+ and no dependencies:

\`\`\`sh
cd experiments/006
python composition.py
python -m unittest -v test_composition.py
\`\`\`

The GitHub Actions job runs **20 dedicated tests** along with earlier experiments. Reproduction output is archived in [experiment-results.json](experiment-results.json).

The 20 tests include typed role reuse, held-out name transfer, no-op and false observation rejection, source-body tampering, intermediate permission removal, tool removal, cycle rejection, effect forging, expansion budgets and grounding caps.

## What must be investigated next

The observed "recursive growth" is **bounded, symbolic reuse of known demonstrated sequences**. To evaluate genuine capability discovery, we need difficult tests that do not provide a complete known macro trace:

- Discover candidate operator sequences from partial goals and intentionally incomplete demonstrations.
- Search for useful combinations under resource budgets; verify each against an independent simulator with hidden rules rather than the same program used to propose them.
- Compare representation-size and search-cost improvements against classical macro-learning and hierarchical planning baselines, reporting negative results.
- Learn to propose new tools or executable candidates only inside a sandbox; reject proposals not backed by tests and human review.
- Carry MOTIF-005 inferred relation constraints into proposal filters **without converting inferences to real permission**.
- Train on true structural holdouts, unseen graph sizes and diverse domains; stop claiming generalization based solely on renamed entities.
- Measure whether a composed abstraction increases the set of *actually reachable* goals or merely makes existing paths easier to retrieve.

MOTIF-007 is the proposed **federated inheritance** frontier: can typed, independently attributable abstract methods be shared while local source graphs, permissions and custody remain local?

## The law at the seam

\`ABSTRACTION != EXECUTION\`

\`RECURSION != AUTHORITY\`

\`SYNTHETIC WITNESS != REAL OBSERVATION\`

\`COMPRESSED PROGRAM != NEW CAUSAL CAPABILITY\`

A genuinely useful intelligence should be able to build on what it has learned **without pretending that a compressed description has become a new power over the world**.
