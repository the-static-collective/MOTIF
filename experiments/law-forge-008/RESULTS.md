# LAW-FORGE-008 — Measured Unknown World trial

**Date:** November 5, 2026.  
**Verified code commit:** `73b790f22870f8fa4bf2f1a81ae5ac8816f96d69`.  
**Successful dedicated Actions run:** [LAW-FORGE-008 Unknown World](https://github.com/the-static-collective/MOTIF/actions/runs/42096643840).

The run passed **139 automated tests**, comprising 118 inherited LAW-FORGE-001..007 checks (14+18+16+16+18+17+19) and **21 new 008 adversarial tests**. It produced the full benchmark JSON and a real, bounded **proposal-only** Question Machine JSON packet (not executed by a live third party). A workflow artifact stores both for independent inspection.

## First genuine incomplete-domain evaluation

A twelve-channel binary input has **4,096 configurations**. Initial source observations: **four**. Each method could inspect only a 160-question source-owned query catalog and spend at most **24 declared inquiry-cost units**. Across all worlds no model witnessed more than 28 source configurations, meaning **less than 0.7% of the 4,096-setting domain**.

The source owns separate **160 potential inquiry configurations, 192 independent-review configurations and 320 heldout-test configurations**, with strict non-overlap; no learner can access independent labels before the corresponding gates. The source is still researcher-authored and seeded from eleven known family types, not an independently sourced outside world.

The learner reuses the actual source-vector checking logic from LAW-FORGE-007 and stores exact witnessed classical lookup first. For previously unseen configurations, it may report a model value only when all surviving members of the **650-rule classical hypothesis set agree**. Because a limited model class may exclude the truth, independent review must approve at least 16 covered predictions and reject **any** covered contradiction. Unknown settings remain unknown to lookup-only; *version-space consensus is not calibrated probability or an absolute guarantee*.

## Frozen development — eleven synthetic families × two seeds = 22 worlds

| Method | Review eligible | HELD | Query cost units | Heldout predictions covered | Declared-weight coverage | Wrong covered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Consequence-weighted active** | **12** | 10 | 154 | **3,840** | **7,608** | 0 |
| **Strong classical entropy active** | **12** | 10 | **153** | **3,840** | **7,608** | 0 |
| Fixed catalog + same hypotheses | 12 | 10 | 528 | 3,522 | 7,006 | 0 |
| Classical greedy-Gini decision tree | 6 | 16 | 528 | 1,869 | 3,737 | 0 |
| Exact lookup of witnessed settings only | 0 | 22 | 528 | 0 | 0 | 0 |

## Separate frozen evaluation — eleven families × five unseen seeds = 55 worlds

| Method | Review eligible | HELD | Query cost units | Heldout predictions covered | Declared-weight coverage | Wrong covered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Consequence-weighted active** | **30** | 25 | **398** | **9,600** | **19,872** | 0 |
| **Strong classical entropy active** | **30** | 25 | **347** | **9,600** | **19,872** | 0 |
| Fixed catalog + same hypotheses | 30 | 25 | 1,320 | 8,814 | 18,170 | 0 |
| Classical greedy-Gini decision tree | 24 | 31 | 1,320 | 7,178 | 14,842 | 0 |
| Exact lookup of witnessed settings only | 0 | 55 | 1,320 | 0 | 0 | 0 |

### Measured method selection: NO_METHOD_PROMOTION

The **classical entropy active learner tied or beat our consequence-weighted policy on every predeclared development decision criterion**. Both accepted 12 of 22 development worlds and covered 3,840 test cases with the same declared consequence-weighted coverage; the consequence policy consumed **154** rather than **153** units.

On separately frozen evaluation the same pattern persisted: **equal accuracy, equal covered predictions and equal consequence-weighted coverage**, but the consequence heuristic cost **398** source units compared with classical entropy's **347**.

**We found no evidence that the new consequence weighting is better.** This negative result matters: a semantically attractive cost-of-inaction idea does not automatically improve active inquiry. In these synthetic families, ordinary entropy selection reaches a sufficient representation with fewer source costs. The method was **not promoted**.

A classical active question policy **did** outperform the predeclared fixed-order catalog: 9,600 vs 8,814 covered test predictions with only 347 vs 1,320 source cost units. That advantage belongs to **classical active learning**, not a novel mathematical breakthrough in MOTIF's heuristic.

The classical greedy-Gini tree control covered 7,178 approved test predictions, and the lookup-only policy, preserving only actual witnessed cells, covered none because all test controls were disjoint from training. That is correct conservative lookup behavior, **not an error on unseen labels**.

### Honest scope of the zero-error report

Among the six in-grammar synthetic source families (single channel, AND/OR/XOR of a pair, AND/OR of a triple), the classical version-space model passed review and covered unseen configurations.

Five out-of-grammar/unstable families were held: majority of a triple, triple XOR, twelve-input parity, review-phase changed law, and hidden context change. Those **25 held evaluation worlds made no approved heldout predictions**. No claim of 100% accurate classification over every world is warranted; the measured zero error applies **only to approved covered predictions**.

The heldout inputs are genuinely disjoint from training and review, but their target laws share hand-authored mechanism classes with development. This is a synthetic within-family transfer test, not independent open-world truth.

## Executable Question Machine doorway

The `desk.py` JSON-stdio tool accepts source-owned input contracts and observations to:

- `propose`: emit one strict typed experiment packet carrying source-declared question cost, consequence weight and **owner_must_execute=true**.
- `predict`: return actual witnessed source lookup, hypothesis-conditional consensus on an unobserved setting, or explicit HOLD if the candidate set disagrees or the source revision changes.

The CI workflow emitted and archived a concrete query proposal, but did **not** execute it on any external system or network. The source-owned evaluator alone performed test membership queries in the offline experiment. This is a MOTIF-authored interface, not an integration into a separate live Question Machine, ALEX, GRAFT, Dogram, reLATTE or CANNON runtime.

## Known limitations and next precise challenge

The cost and consequences are **artificial 1/2 and 1/5 labels** based on input bits. These values do not measure real human harm, financial loss, effort or latency. The learner's 650-rule library was pre-supplied, the source input arity and hidden families hand-designed, and no probability calibration, out-of-family coverage guarantee, dynamic sensor construction or external source authentication was established.

**Next:** freeze the learner; introduce a genuinely independent source with unfamiliar mechanism classes and its own measured query-cost contract. Compare against stronger cost-sensitive classical active learning (including tree/Bayesian protocols) and require an explicit selective-prediction risk ledger under distribution shift. If ordinary classical entropy remains better, keep it as the preferred skill rather than overriding data with a favored heuristic.
