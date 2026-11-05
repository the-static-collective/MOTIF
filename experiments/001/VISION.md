# MOTIF — Model Of Transformations In Fields

**Experiment 001 — 4 November 2026**  
A deliberately independent thought experiment and executable toy. Not integrated with JAR;VIS, reLATTE or GHoT; no real community data, users, dispatch, authentication, or authority.

## The wager

Instead of making words the primitive of intelligence, make **consequential change to a typed relational world** the primitive. Language and perception are adapters. The native representation is a field of particular entities, relations, opportunities, permissions, and *distinctly identified observations versus hypotheses*.

The state is *not just the world*. It has four layers:

1. **Observed field** — local facts with provenance, confidence, temporal scope and source-owned custody. Different observers can disagree; neither a receipt nor a signature alone proves truth.
2. **Possible field** — counterfactual forks containing projected graph rewrites, including explicitly unresolved dependencies.
3. **Capability field** — what the current configuration permits or affords, including things no one has yet attempted.
4. **History of crossings** — accepted/refused/held attempts, and later observations independent of forecasts.

The testable premise: a model which learns *changes to affordances* can recognize more reusable and regenerative cooperation than a model trained to produce fluent replies alone.

## Speculative native architecture: field → transformations → reachable worlds

```text
perception / language adapter (swappable, not source of truth)
                     |
          OBSERVATION QUARANTINE
                     |
          typed relational hypergraph
     ┌───────────────┼───────────────────┐
     |               |                   |
  Motif learner   Reality ledger    Affordance generator
 (learn verbs)    (what happened)    (what's possible)
     |               |                   |
     └───────────────┼───────────────────┘
                     |
           Counterfactual compiler
      Fork imagined futures, never rewrite facts
                     |
          Frontier / leverage estimator
      Which small change opens useful futures?
                     |
             Stewardship barrier
     Permission, budget, harm, reversible trial,
     source authority. HOLD is a valid answer.
                     |
             proposed intervention
                     |
         independent post-event witness
                     |
     Surprise / misprediction / scar learning
```

### Unconventional research hypotheses

**H1: The model should learn verbs, not just nouns.** The atomic learned item is an operator on a *particular relationship*, such as `(broken, bike) → (usable, bike)` with requirements derived from examples. Operators can later be invented by composing previously learned ones and verified against novel observations. This toy learns two operator schemas from manually labeled demonstrations, not new unnamed verbs.

**H2: Train on *newly opened options*.** Given state `S`, define `R_h(S)` as bounded, reachable consent-valid world configurations within `h` interventions. A catalytic action increases the weighted quality/diversity of `R_h(S')` compared with `R_h(S)`. Use several objective dimensions rather than a single universal welfare score; explicitly avoid treating network expansion as inherently good.

**H3: Two kinds of time.** Reality evolves only upon separately witnessed events; counterfactual time can fork without limit (within a compute budget). A model must never promote its own forecast into observation.

**H4: Surprise is training data, not failure to conceal.** Track when outcomes differ from predictions. Preserve refutations and failed attempts to refine the operator rather than training only on successful demonstrations.

**H5: No single shared world.** Different parties keep distinct observed fields. Shared models exchange carefully scoped, consented, non-identifying motifs rather than automatically aggregating sensitive personal histories.

**H6: The model learns its own *representation*.** At a speculative future phase, let the model propose new useful relation types and primitives, but admit them only if their definitions are inspectable, their predictive value is demonstrated on held-out worlds, and they do not bypass stewardship.

## The executable 001 proof

The `motif.py` interpreter needs only Python's standard library. Six **invented** demonstrations (three repair, three teach) become two action-relative graph rewrite motifs via anti-unification/intersection. The system sees a new graph with previously unseen named entities. Its search finds a three-step counterfactual plan:

1. Mira repairs Jo's bike1 (permission, tool, ownership, broken state and repair skill were supplied in the invented graph).
2. Mira teaches Jo repair (permission supplied).
3. Jo repairs bike2, without Mira's participation, using a tool and self-permission supplied in the graph.

The model's rules are **induced from transition examples**; the action names/role arguments and search objective are supplied by its designer. No neural weights, no NLP and no real actions. This demonstrates rudimentary structural transfer and planning from changed capability; **it does not establish a novel model family, real-world accuracy, or emergent autonomy**.

Counterfactual when all `permits(...)` facts are removed: *no plan*. Explicit absence of authority is not filled in by imagination.

### Run

```bash
python motif.py
python -m unittest -v test_motif.py
```

The result JSON is saved as `experiment-results.json`.

## Design of a *genuinely learnable* next engine

A future graph-native architecture could learn a distribution over graph rewrite programs:

- Input: typed graph with event time, uncertainty, causal evidence, and source permissions; candidate intervention.
- Latent: compositional **event motifs**, not a sequence of text tokens. A motif has role slots, preconditions, expected state edits, possible failures, resource costs and evidence requirements.
- Dynamics: `pθ(ΔG, observation, failure | G, intervention)`. Use sparse local graph operations and sampled rewrite distributions; keep hard invariants and authority checks outside neural weights.
- Explorer: expand hypothetical edit sequences; favor actions that achieve declared goals, preserve scarce resources, and create independently reusable capabilities.
- Learning: predictive next-edit loss, counterfactual held-out tests, calibration, minimum-description-length pressure on redundant operators, explicit penalties for impossible transitions, abstention under missing evidence.
- Identity: independently scoped histories; transfer learned motif *schemas* across worlds only with rights preserved.

This is a proposed architecture, **not yet implemented** in the included code. It may be better to learn a library of graph-transformation programs than to learn a massive end-to-end neural network.

## Major unsolved problems

- Inducing causal preconditions from mere before/after correlations (this toy does **not** do that).
- Capturing continuous physics, quantities, deadlines, scarcity, irreversible damage and social preference diversity.
- Learning action types/role assignments without human labels.
- Generalizing across unseen *relations* and intentions, not only unseen entity IDs.
- Calibrating uncertainty from failures and incomplete, biased records.
- Avoiding optimizing for opportunities that no one actually wants.
- Achieving federated training without extracting private data.
- Controlling exponential world-fork exploration and bad recursive capability invention.

## Falsifiable milestones

**F1 — Hidden names:** Hold out new people and assets; learn motifs on unrelated names; measure state-delta precision/recall and refusal under missing permission.

**F2 — Hidden compositions:** Hold out *chains* of actions (e.g. teach → repair); train only on one-step episodes; measure whether planning discovers the chain.

**F3 — Hidden failures:** Add no-op and failed attempts (broken tools, missing permissions, expired resources) and learn calibrated abstention instead of blindly reusing success motifs.

**F4 — Frontier value:** Compare a one-step reward planner with a bounded multi-step planner; measure useful, validated capabilities created, not just action count or claimed impact.

**F5 — Competing baselines:** Compare against deterministic typed rule systems, graph neural networks, and a conventional LLM+planner with **the same input evidence and evaluation budget**. Retire any custom complication that cannot win a relevant metric.

**F6 — Real field trial:** Only after opt-in and independent validation: small, reversible public-community tasks with explicit separation of proposals, consent, execution and outcomes.

## Adjacent research, not claims of originality

- Graph World Models: Concepts, Taxonomy, and Future Directions (Liu et al., 2026), https://arxiv.org/abs/2604.27895
- Learning Interactive World Model for Object-Centric Reinforcement Learning (Feng et al., NeurIPS 2025), https://proceedings.nips.cc/paper_files/paper/2025/hash/8187faaf6759ef6d4e93293339bc656e-Abstract-Conference.html
- Learning possibilistic dynamic systems from state transitions (Hu et al., 2025), https://www.sciencedirect.com/science/article/abs/pii/S0165011424004056

MOTIF's synthesis is hypothetical. Related mechanisms exist in relational dynamics, inductive logic programming, world models, program induction and causal planning. Novelty would need formal comparison and empirical proof.