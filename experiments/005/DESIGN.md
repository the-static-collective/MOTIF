# MOTIF-005 — THE BIRTH OF A CONCEPT

**Research question:** Can a graph-native learner derive a *previously unnamed, composite relation* from contrasted outcomes, without receiving the relation's name or definition, and use it to refine which hypothetical transformations it considers feasible?

**Status:** A small, deterministic, standard-library **symbolic concept-induction experiment** using *constructed synthetic examples*. This does not establish that MOTIF invented a fundamentally new ontology, discovered causality, learned a neural representation, or understood an actual physical world.

## The vertical move

MOTIF-002 induced anonymous transition operators. MOTIF-003 recognized which new grounded actions a transition might enable. MOTIF-004 retained failed predictions and proposed a missing contextual relationship.

MOTIF-005 now asks whether the missing relationship must be **composed** from multiple old relationships:

\`\`\`text
Worker ──carries──► Part ──fits──► Bicycle

       shared intermediate witness
                  ↓
    derived concept-<hash>(Bicycle, Owner, Worker)
                  ↓
       candidate repair permitted
       inside a synthetic future
\`\`\`

The learner is **not supplied this two-edge pattern**. It enumerates simple local candidates from the graphs, tests each against successful/no-effect attempted transitions, and proposes the unique composite pattern if one exists. Its vocabulary *is* supplied: the existing \`carries\` and \`fits\` relations, plus entity roles and the original graph-rewrite operator. The newly proposed predicate is built from them.

This is narrower but more testable than asserting spontaneous concept creation from sensory experience.

## The experiment

The input is a fixture-built set of bicycle-repair attempts with independent \`before\` and \`observed_after\` graphs.

Each observation has fictional repairers, owners, bicycles, and anonymous part IDs. **Both** source predicates (\`carries\`, \`fits\`) occur in successful and unsuccessful worlds. In the failing worlds, the carried part does *not* match the part that fits the bicycle.

Thus, knowing merely that a worker carries *something* and *something* fits the bike is insufficient.

A successful synthetic outcome correlates with a specific joined structure:

\`∃p: carries(worker,p) ∧ fits(p,bike)\`

The engine generates role-relative, anonymous candidate patterns, then retains one as a *proposed* concept only when:

- at least three successful and three no-effect attempts exist;
- the proposed structural pattern matches every success and no failure;
- it contains **two** source edges (single-edge patterns are reported as no new composite concept);
- exactly **one** pattern meets the criterion;
- no divergent/partial outcome is present.

All other cases yield an explicit abstention, including a confounded dataset with an equally perfect spurious feature.

### One synthetic experiment, two models

| Measure | Single-edge model | Composite-join learner |
|---|---:|---:|
| Training fixtures | 18 | 18 |
| Held-out fixtures (new IDs, same generator) | 12 | 12 |
| Can represent shared existential part? | No | Yes |
| Best training balanced accuracy | 0.50 | 1.00 |
| Held-out correct outcome classifications | Not yet measured separately | 12/12 |

The 0.50 result is *the best single-edge feature within this deliberately constructed candidate family*, not a comparison against every statistical learner or neural architecture. The 12/12 holdout shares the same engineered generation mechanism; it is not evidence of general out-of-distribution robustness.

The derived concept is an **ephemeral inferential overlay**, never inserted into the observed world. MOTIF-005 can use it to **filter** existing synthetic rewrite proposals from MOTIF-002; it cannot authorize, create, dispatch or execute an action.

## Files

- [concept.py](concept.py): candidate generation, existential-join matching, contrast learning, inferred concept projection, bounded hypothetical action filter.
- [test_concept.py](test_concept.py): tests covering generalization to fresh IDs, joins with wrong parts, preservation of original observations, synthetic permission boundaries, contradictory and confounded evidence, and abstention.

Run:

\`\`\`sh
cd experiments/005
python concept.py
python -m unittest -v test_concept.py
\`\`\`

Pure Python 3.10+ and standard library. GitHub Actions runs both the experiment and tests without paid API dependencies.

## What this demonstrates, and what it does not

**Demonstrates under constructed assumptions:** a simple learner can discover an unprovided composite graph pattern with a shared witness, assign a stable local symbolic identifier, and use it as a testable condition on hypothetical transitions.

**Does not demonstrate:** the discovery of a new primitive relation from raw experience, self-generated perception, causality, authenticated authorization, open-world competence, calibrated probability, or a novel neural model architecture.

The underlying induction is constrained to one- and two-edge candidates. It intentionally excludes longer paths, negation, quantities, hidden confounders, temporal durations, uncertainty and social claims. The current tests are designed for exact synthetic graphs, and selection on perfect pattern separation is prone to overfitting.

## The important failure

If a gold-colored badge appears **only in successful examples**, that unrelated single-edge fact becomes another perfect explanation. MOTIF-005 **abstains** because the evidence is compatible with both hypotheses.

If identical input graphs produce contradictory outcomes, the proposed separator loses perfect support and it abstains.

This is desirable: the system has not earned the right to elevate a pattern into an asserted truth.

## More demanding next frontier

The next proof must challenge both graph feature engineering and learning itself:

1. Randomly intervene on part assignment to break spurious coincidences.
2. Hold out new *graph structures* and distribution shifts, not just entity names.
3. Track empirical calibration, coverage, false positives, refusals and sample efficiency.
4. Compare a hand-coded two-hop relational detector, decision trees with engineered join features, relational rule induction, and a learned graph model at the same resource budget.
5. Propose candidate **new primitive predicates** only when simpler rewrites fail; test them by held-out predictive compression and independent review.
6. Preserve observed history and the permission boundary when transferring a learned motif to other locally governed worlds.

The wider ambition is in [THE OUTERMOST CIRCLE](../../docs/THE-OUTERMOST-CIRCLE.md).

**A useful idea is not a fact. A derived concept is not a verified condition. A predicted possibility is not permission to act.**
