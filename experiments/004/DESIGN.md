# MOTIF-004 — The First Scar

**Question:** Can a graph-native model preserve the fact that an eligible, intentionally attempted transformation did *not* occur, infer a missing contextual discriminator, and retract that inference when contradicted?

**Status:** Working standard-library symbolic experiment with deliberately generated synthetic fixtures, **not** causal identification, physical observation, human authorization, or a trainable neural architecture.

## The test

MOTIF-002 learns a "broken bike → usable bike" graph rewrite from three action-name-free before/after demonstrations. That model sees a skill, tool and a fictional \`permits\` fact and predicts a successful rewrite.

MOTIF-004 introduces an *explicitly separate attempted-action record* with an observed-after graph. Some synthetic repair attempts work; others exhibit **no observed change**. The original learned rule predicts success on both.

Training uses eight synthetic records: four successful graph rewrites and four no-effect records. Each contains varied, role-relative nuisance properties. In this hand-designed fixture, a previously unmodeled \`part(bike, brake_kit)\` graph relation is present in every success and absent in every no-effect case.

A conservative rule-revision pass:

1. Archives the attempted action, original world, simulated prediction and independently *supplied fixture* observation without overwriting either.
2. Calculates missing predicted facts and unexpected observed facts.
3. Distinguishes full effect, no observed change, and divergent/partial outcome.
4. Extracts local role-relative contextual facts not already in the original operator's requirements.
5. Selects a **provisional correlation** only when at least three successes and three failures exist and **exactly one** additional feature appears in every success and no failure.
6. **ABSTAINS** if the evidence is sparse, contradictory, divergent, or equally compatible with several proposed missing features.
7. Evaluates a holdout with *new entity identities but the same fixture-generating mechanism*.

## Reproduce

Python 3.10+, no third-party packages or API credentials:

\`\`\`sh
cd experiments/004
python scar.py
python -m unittest -v test_scar.py
\`\`\`

Expected controlled output:

| Metric | Naive MOTIF-002 graph rule | MOTIF-004 contrast revision |
|---|---:|---:|
| Training attempts | 8 | 8 |
| Negative/no-effect observations preserved | no | 4 |
| Held-out synthetic attempts | 4 | 4 |
| Correct holdout outcome classifications | 2 | 4 |

The holdout is intentionally narrow (fresh identities, same generator). This does **not** establish statistical generalization, reliable causal inference, or improved real-world performance. The numbers are not independent empirical measurements.

## The scar is not the truth

Every stored record contains \`SYNTHETIC_WITNESS\` provenance. That is a **fixture label**, not a verified witness or a cryptographic signature. The in-memory journal does not provide durable append-only storage, encryption, attestation, external fact checking, or authenticated identity.

A predicted transition remains imagined. An observed transition is supplied by the experiment separately. A mismatch remains visible; it is not silently rewritten as success.

The synthetic \`permits\` fact is a guard for the demonstration, **not** human consent. Missing permissions prevent accepting the attempted transition into the learning journal. No external action can be taken by this code.

## Why abstention matters

The learner can mistake correlation for causation. If every success also has blue paint, blue paint and brake parts are indistinguishable to this toy learner. **It abstains instead of selecting a convenient answer.**

Introduce one synthetic success without the brake-part relation, and the inferred separator disappears; the model abstains again.

Introduce a divergent/partial observation and it abstains until a richer outcome model exists.

This is the first "scar": uncertainty can become a durable, testable consequence of surprise, rather than a story explaining surprise away.

## Falsification and next steps

The current revision rule assumes a single, positive, sufficient discriminator, complete local before/after graphs, exact operator grounding, and correct observation labels. A stronger MOTIF-005 study should:

- Use partially observed worlds, several genuinely relevant prerequisites, and *counterfactually altered* inputs.
- Randomize nuisance features and include confounders that defeat single-feature explanation.
- Pre-register held-out intervention tests that break spurious correlations.
- Quantify coverage, calibration, precision, recall, and abstention—not accuracy alone.
- Compare with simple statistical classifiers, decision trees, graph rewrite learners, and Bayesian / causal alternatives under identical sample budgets.
- Learn and revise *types or ontological predicates*, with explicit approval before admission into any source-owned runtime.
- Keep legal authorization, stewardship and external execution outside the learned model.

See [THE OUTERMOST CIRCLE](../../docs/THE-OUTERMOST-CIRCLE.md) for the broader research program.

## Boundary worth keeping

**Hypothesis ≠ observation ≠ authority.**

The point of a scar is not that the machine has found the cause. It is that the machine remembers exactly how its world model was wrong—and has a disciplined way to become less certain.
