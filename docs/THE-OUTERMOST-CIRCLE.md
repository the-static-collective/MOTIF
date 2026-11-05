# MOTIF — THE OUTERMOST CIRCLE
## A research program for native intelligence built from consequential change

Status: **speculative architecture** with six bounded, standard-library, synthetic experiments (001–006). No claim of artificial general intelligence, causal discovery, learned ethics, or verified real-world agency.

### The fundamental wager

Language is not the mandatory internal substrate of intelligence. MOTIF's native unit is a typed, attributable *change in relationships*, and its core problem is predicting how that change modifies the space of further feasible changes.

Its first primitive is not a token. It is an event proposal:
`(observed_field, proposed_transformation, possible_next_field, uncertainty, prerequisites)`.

Its second primitive is **a frontier**: the set of actions that a particular field makes available.

Its third primitive is **a gap**: the difference between imagined and independently observed outcomes.

The long-term question: *Can a learner invent useful transformation programs by compressing histories of state changes, then improve its predictive power by actively seeking falsifying evidence rather than more fluent descriptions?*

## The whole circle

```text
                  INDEPENDENT HUMAN / SENSOR INPUT
                             |
                   QUARANTINE + PROVENANCE
                             |
                   LOCAL TYPED HYPERGRAPH
                 /            |             \
           observations   contradictions   permissions
                 \            |             /
                  CHANGE INDUCTION / GRAMMAR
                       |        |
                 rules of     uncertain
                 change       missing links
                       \        /
                 COUNTERFACTUAL COMPILER
                      (fork only)
                            |
                  AFFORDANCE FRONTIER
             "what becomes possible after this?"
                            |
                    MINIMAL INTERVENTION
                 /          |           \
            smallest      greatest     evidence needed
            next step     reach        to choose
                 \          |           /
                 AUTHORIZATION / REVIEW GATE
                 (external, never learned away)
                            |
                     PROPOSED ACTION
                      (not execution)
                            |
                  SEPARATE ACTUATOR + RECEIPT
                            |
                  INDEPENDENT WORLD WITNESS
                            |
                      SURPRISE TRACE
                            |
             retain / refine / reject hypotheses
                            |
                       INHERITANCE
              share verified motif abstractions,
               not unconsented personal histories
```

## Formal objects

Let `G` be a locally scoped observed graph. It is not a universal truth graph. Every observation must have source, time, custody, scope and conflict metadata in a production system.

Let `m` be a candidate typed graph rewrite program, `θ` a role binding, and `T(G,m,θ)` a **simulated** transition.

The bounded synthetic affordance field is:

`A(G) = {(m, θ) | preconditions(m, θ) ⊆ G and the simulation gate admits it}`

The newly enabled choices from a simulated move `a` are:

`Δ⁺A(G,a) = A(T(G,a)) \ A(G)`

A bounded possibility horizon is:

`R_h(G) = {G' | G' is reachable in ≤ h simulated transitions}`

These sets are *epistemic constructs*, not proof that an action will work in reality.

### Three independent clocks

1. **Observation time:** when a source reported a condition.
2. **Counterfactual time:** the hypothetical sequence in a fork.
3. **Crossing time:** when independently admitted real-world effects occurred.

A forecast can never advance the observation clock or crossing clock.

## MOTIF-003: The newly opened door

The experiment runs the two unnamed rewrite operators induced in MOTIF-002. In the synthetic world, Jo owns two broken bikes; Mira can repair them; the relevant permission facts are present.

Two *first actions* are available:

- Repair one bicycle: immediate toy utility +10, **zero** newly enabled grounded rewrite opportunities.
- Teach Jo repair: immediate toy utility +4, **one** newly enabled grounded rewrite opportunity (Jo can now repair the second bike).

A myopic first-step policy favors the first. A declared *new-choices-first* policy favors the second. Both are plausible, neither is a universal moral rule. The result reveals a measurable decision difference between solving a need now and opening the ability to solve further needs. The teaching result is an assumed synthetic graph rewrite—not proof of real-world education.

MOTIF-003 also counts remaining reachable simulated states (bounded, with truncation reported) and separates predicted from independently supplied observations. It does not change either world or grant consent.

## Seven shells to fill

| Shell | Native question | Minimal proof | Critical falsifier |
|---|---|---|---|
| 001 — Relations | What changed? | role-relative edit induction from synthetic events | wrong edit on held-out IDs |
| 002 — Unnamed verbs | What recurring transition exists? | cluster unlabeled graph deltas; infer roles | alias-sensitive or spurious operator |
| 003 — Affordances | What *new* action became possible? | compare A(G) before/after a fork | gains vanish on controlled recombination |
| 004 — Causal scars | Why did a prediction fail? | retain contradictory/no-op attempts; abstain or revise | fails under intervention |
| 005 — New ontology | Which missing relational *type* improves predictions? | propose typed predicates, measure held-out compression | no improvement over simpler vocabulary |
| 006 — Recursive capability | Can the system propose a new testable tool or composite operator? | **Composite macro induction and source-checked deterministic replay implemented**; true new executable tools remain future research | missing primitive guards, source tampering or claimed new external authority |
| 007 — Federated inheritance | Can one world transfer useful motifs to another *without transferring its private states*? | scoped signed schema exchange, independently admissible | leakage, attribution loss, authority confusion |

Further horizons: continuous quantities, physical uncertainty, multiagent preferences, uncertain event duration, energy budgets, local processors, and transferable multimodal perception. None is implemented merely by documenting it.

## Key mathematical temptation to reject

`max |R_h(G)|` is **not** a universal definition of goodness. An expanding number of future choices can be worthless, unsafe, unwanted, or merely duplicate pathways.

Instead evaluate a vector of explicit, human-declared objectives:

`(validated need met, time/cost, new useful capability, reversibility, confidence, dignity/consent constraints, robustness)`.

Pareto comparisons and human selection should remain visible. A scalar ranking is permitted only as a transparent, task-specific *policy* and never mistaken for a natural law.

## What truly new model architecture would require

The present artifacts are symbolic program induction and search. A candidate **trainable** architecture would require:

1. A typed, sparse graph encoder with identity separated from feature roles.
2. A learned distribution `p(ΔG, failure | G, intervention, context)` over possible edit programs, not next words.
3. A latent motif library with minimum-description-length or Bayesian structural penalties, plus uncertainty estimates.
4. An explicit counterexample-driven update mechanism; observed no-change must not be thrown away.
5. A horizon module predicting *changes in grounded affordances*, not only immediate graph deltas.
6. Calibrated abstention under domain shift and missing authority.
7. A non-neural gate for authority, custody, source provenance, and irreversible acts.
8. An audit of novel predicate proposals: improve out-of-sample predictions before admission.

Controlled comparisons must include: handcrafted rewrite rules; object-centric GNN/world-model baselines; causal planners; and small LLM+tool-planning baselines with **identical evidence, budgets, and no privileged hints**.

**Kill condition:** if the custom architecture does not improve calibrated prediction, decision utility, cost, transfer or interpretability on held-out worlds, retire the complication.

## ReLATTE / JAR;VIS / GHoT seam (future, not live)

- **JAR;VIS:** interprets a voluntary human question into bounded goals and constraints; presents proposals in human language.
- **MOTIF:** estimates possible transformations and their uncertain consequences; has no authorization or dispatch authority.
- **reLATTE:** verifies source-owned crossing envelopes, admission, custody and receipts; does not equate signing with truth.
- **GHoT:** offers measured compute capabilities on local nodes, including a tiny optional inference service; a processor never becomes an authority.
- **STATIC OS:** eventually hosts the locally owned runtime, recovery and audit surface; its existing repository is not yet a verified bootable OS.

The boundaries must remain explicit: *planning does not dispatch; a signature does not prove an event; witnessing does not imply endorsement; an abstraction does not inherit its originating person's authority.*

## Experiment discipline

- Fixtures are marked **synthetic** and carry no real identities.
- A model's imagined world is immutable relative to observations.
- Every reported result includes the baseline, objective definition, horizon, compute cap, and holdout split.
- Negative/no-op observations stay in the record; contradictions are never silently averaged away.
- No independent cross-world sharing without explicit bounded permission and provenance.
- Open research questions are recorded as open, not marketed as achievements.

The large circle is the research contract. We fill it with reproducible falsifiable increments—not by pretending that an unfinished system already exists.
