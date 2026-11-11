# FIRE-002 — preregistered synthetic comparison

**Registered before the first CI benchmark run for FIRE-002.** This fixes the intended questions, training/test seeds, objective, comparators, and negative-result rule. Tests are engineer-generated deterministic synthetic worlds, not external blind validation.

## Claim under test

Does a governor that evaluates expected **independently verified value per remaining reasoning/observation cost**, then updates its source-reliability and downstream-yield estimates exclusively from verification receipts, beat FIRE-001's opportunity-weighted governor and a strong straightforward value-per-cost scheduler?

More future questions is a secondary measurement, not proof of cognitive progress.

## Train and freeze

- The source graph uses the actual FIRE-001 fixture with eight generated questions and initial roots, source quorums of 1/3/5, a separate synthetic certifying owner, and a fixed **24-operation** budget.
- Tune only one predeclared spark coefficient among **0, 0.5, 1, 2, 4** on 80 steady worlds, seeds **6100–6179**. The selected coefficient is frozen for all other tests.
- Frozen evaluation: **200 independent seeds 42000–42199**, *per regime*. Regimes: **steady** (independent synthetic reports with fidelity .82), **drift** (root fidelity .88; child fidelity .56), and **correlated** (all reports on one question copy a single hidden source, despite distinct apparent IDs; source agreement does not establish independence).
- Genuine external sources and a common shared independent-origin verifier are *absent*.
- Comparators: simple maximum immediate value, classical greedy **value / remaining cost**, naive source-disagreement information priority, FIRE-001's tuned governor, a frozen prior-only version of FIRE-002, and FIRE-002 with online updates.
- All systems see the same generated worlds, cost budgets, and stage ordering. The exact same majority-vote verifier adjudicates answer truth for all; source learning affects prioritization, not any policy's truth oracle or source availability.

## Reporting and falsification

**Primary:** mean independently certified question-value points per world. Report *paired differences against classical greedy and FIRE-001*, with approximate 95% normal confidence intervals across matched worlds.

**Secondary:** number of independently certified questions, verification failures, new questions unlocked, operations consumed, and number of online updates. Do not claim learning improvement from unlocked question count alone. Analyze each regime separately; report if the learning policy loses.

**Important limits:** Parameter tuning is bounded grid search, not autonomous architecture invention. Learning is limited to a two-count Beta-style evidence-reliability estimator, an analogous child-verification estimator, and deterministic finite lookahead. A certification answer is made available only at the verification gate of a toy task with a binary outcome. Source IDs are not authenticated and the correlated-regime generator intentionally lies by omission about ancestry. The full problem generator and test regimes are engineer-authored, not preregistered by a third party, and cannot demonstrate general open-world intelligence.

A credible positive result needs a primary-metric advantage against value/cost greedy, no severe corruption under drift/correlation, and repeatability on new independent real-world or public benchmark data. Otherwise keep the proposed method in research HOLD.
