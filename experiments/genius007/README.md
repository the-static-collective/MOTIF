# MOTIF-GENIUS-007 — THE QUESTION FOUNDRY

**Research HOLD.** Executable, local, synthetic proof of concept. Stacked on GENIUS-006 draft; not merged or connected to live MOTIF, Trench, MCP, JAR;VIS, a laboratory, or any person's accounts.

## Frontier

GENIUS-006 could **select questions from an engineer-supplied menu**, and proved an important limit: a two-step affordance planner cannot reliably discover a four-step delayed reward.

This experiment asks a different question:

> Can MOTIF **construct a useful intermediate research question from a goal's prerequisite relationships**, within a typed, source-declared measurement grammar, then test the new question and attach an independently checked downstream capability receipt?

The operation is **compositional query synthesis**, not the invention of an unknown physical sensor, scientific theory or novel mathematical algorithm.

## Relevant classical work

- **Membership-query synthesis** is an established active-learning idea. Schumann & Rehbein (2019), *Active Learning via Membership Query Synthesis for Semi-Supervised Sentence Classification*, CoNLL, DOI https://doi.org/10.18653/v1/K19-1044. Here the questions concern a small Boolean measurement world, not NLP classification.
- **Adaptive/group testing** has long examined useful composite measurement actions. Dorfman-style pooled screening is classical; a useful modern discussion of instrument costs and practical limits appears in *Considerations for Group Testing: A Practical Approach for the Clinical Laboratory*, https://pmc.ncbi.nlm.nih.gov/articles/PMC7731934/ . The code is NOT a medically meaningful test and DOES NOT implement a real pooled assay.
- **Value of information / exact finite Bellman planning** provide the full-action-space optimal baseline. Our experiment neither defeats nor changes that theorem; all agents see the same declared priors, goal contracts and admissible sensor semantics.

## Crucial cost/feasibility boundary

The simulator declares a purely hypothetical instrument with two operations:

**DIRECT(value of one binary sensor)** — fixed cost **2** units. Reveals the sensor's value.

**PAIR_MATCH(first sensor = specified value AND second sensor = specified value)** — fixed cost **3** units *only if the declared instrument says that two-channel co-assay is supported*. Returns a single Boolean, **not** both individual sensor values. Two independent direct measurements would cost 4 units.

The two-channel operation is an **explicit public simulator assumption** and is independently checked for declared availability, exact cost and operator provenance before it can run. The algorithm cannot create a real assay merely by writing a compound question. In a control where the paired instrument is absent, or costs **5** units, query synthesis cannot claim a cheaper new measurement.

This distinction is fundamental: any simulated dividend from composition reflects the availability of the combined sensor operation at the declared price and the planner's ability to formulate/use it. It is **not** an independently demonstrated technological breakthrough.

## What is actually generated?

No menu of named compound questions is supplied. The task supplies only:

- Goal capabilities, each depending on typed literals such as condition A = 1 and condition B = 0.
- A publicly declared instrument with named sensors, whether it can perform a paired match and the instrument cost/source reference.
- A bounded measurement budget, normally 3–6 units.

The foundry constructs two-literal question expressions for pairs of prerequisites that participate in the same capability. Example, not hard-coded into the engine:

~~~text
Goal: safe water depends on cobalt_mill=0 AND windrow=1.
Source instrument: paired two-channel match supported, cost=3.
Synthesized question: p:cobalt_mill=0&windrow=1
Question provenance: capability water_is_ready + instrument contract.
Predicted outcome: held as an unobserved hypothetical branch.
Measurement: called only after selected, returns 0 or 1.
Evidence: source pointer + actual reply + updated candidate worlds.
Certificate: only if ALL remaining consistent worlds satisfy the goal.
Independent check: simulator's separately called direct-world verifier.
~~~

The question string was **not on the source question menu**. A new task may rename sensors to unfamiliar symbols and change the prerequisite polarity; the generator composes the typed question from the new constraints.

All hypothetical answers are evaluated through finite partitions **without reading the actual world** until after the next question has been chosen.

Candidate expressions are regenerated/filtered as evidence narrows the consistent worlds. Source and cost constraints are checked on every actual measurement.

### Strong comparisons — never hide the full oracle

| Comparator | Action space | Method |
| --- | --- | --- |
| DIRECT_ENTROPY | Direct sensors only | Max Shannon information per measurement cost |
| DIRECT_OPTIMAL | Direct sensors only | Exact classical Bellman DP |
| FOUNDRY_ENTROPY | Direct + generated supported paired probes | Max Shannon information per measurement cost |
| FOUNDRY_GREEDY | Direct + paired | Max immediate certified capability value |
| FOUNDRY_LOOKAHEAD2 | Direct + paired | Two-question finite classical lookahead |
| FOUNDRY_OPTIMAL | Direct + paired | **Full-horizon exact classical Bellman DP**, strongest fair same-action-space upper bound |
| TRAINING_SELECTED | Select among generated entropy/greedy/2-lookahead | Fixed, validation-only policy selection |

All strategies share the same 32 equally likely binary target worlds, true sensor semantics, costs, budget and goal weights. Full exact planning explores more possible future question trees than shallow methods; it is the **exact optimality reference**, not a matched-compute competitor.

Capability certification requires that **every remaining possible world** meets each literal. A separate direct-world verifier raises an error for any false certificate. There are no real-world actions.

## Families and disconfirming controls

Seven task families are constructed with new names, goal polarities and weights on separate, predeclared random seeds:

1. **PAIRABLE:** one two-literal capability; budget 3. Direct-only exact cannot finish both 2-cost tests; one supported 3-cost combined question may succeed.
2. **TRIPLE:** one three-literal capability; budget 5. A 3-cost pair match plus a 2-cost direct measurement can certify it. Immediate greedy reward can miss the opportunity.
3. **MIXED_POLARITY:** a goal requires a zero-valued condition AND a one-valued condition, forcing proof that the generated expression handles negation.
4. **MULTIGOAL:** two distinct two-literal capabilities; budget 6. Two paired assays may be more productive than three direct tests.
5. **NO_PAIR:** a paired assay is not supported; the foundry's action set must collapse to direct-only.
6. **EXPENSIVE_PAIR:** paired assay is hypothetically supported but costs 5, above its 4-unit inquiry budget. It must not magically become cheap.
7. **DISTRACTOR:** many non-goal sensors can yield information without advancing the stated capability. This probes entropy-only selection versus goal-related synthesized questions.

**Validation:** two synthetic tasks per family (seeds 70701/70702), exhaustively checking all 32 target worlds for each task. Select one of three foundry policies on the validation tasks only. Freeze selection and task/evaluation contracts with SHA-256 before generating future-task constraints.

**Future tasks:** three different seeded tasks per family (70731/70732/70733), new variable suffixes, requirement signs and reward weights, **all 32 possible worlds per task**. This removes finite *world-sample* uncertainty within the model but does not create independently authored task families or genuine distributional transfer.

Metrics: verified weighted capability reward, independently checked certificate count, actual measurement cost, number of episodes using at least one synthesized paired question, generated-candidate count, classical full-prior optimum and Bellman memo states. All measured differences are computed for matching task/target pairs.

A result in which generated methods beat direct-only exact **must not** be reported as beating classical planning on equal instrumentation: the generated methods have access to the additional publicly supported pair assay. They should be compared primarily against **FOUNDRY_OPTIMAL**, which uses the same action set.

## Run and inspect

From the repository root:

~~~sh
python -m unittest discover -s experiments/genius007 -p 'test_*.py' -v
python experiments/genius007/benchmark.py > /tmp/motif-genius007.json
python -m json.tool /tmp/motif-genius007.json >/dev/null
~~~

CI archives complete synthetic task, policy, cost and proof packets, including generated source-owned questions. Tests reject unsupported instruments, forged cost/provenance, contradictory goals, out-of-model truths and unverified certificates.

## Honest frontier boundaries

- This is a **real executable capability to compose candidate question expressions** from a public goal, using conventional enumeration of pairs. It is not autonomous discovery of a general question-invention language.
- The sensor grammar, discount, goals, verification semantics and entire simulator are supplied by the same engineer. An unsupported physical question must return HOLD.
- An initially useful compound query may be worthless for a different instrument or objective. The exact classical DP on the **same action space** should perform at least as well in expectation.
- Validation/test samples come from **one synthetic generator**. Different variable names do not establish deep transfer.
- No real people, private data, external APIs, Trench network, hardware or MCP endpoint are contacted.
- No mathematical novelty or recursive self-improvement is established.

**Next objective:** independent authors must supply a real test-instrument capability description and an unfamiliar goal. MOTIF should invent candidate *typed* experiments that a separate evaluator can actually execute, verify the evidence transport and compare to a well-engineered classical planner under identical tool, question and compute budgets. The highest-value original research problem remains inventing **new causal intermediate variables and legitimate measurement methods**, not merely composing known ones.

**Invariant:** a speculative question can be proposed freely; a measurement requires a supported instrument; a capability claim requires a proof carrying actual evidence.
