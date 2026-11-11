# FIRE-006 — The Price of Revision

**Research HOLD.** Executable synthetic trial and honest negative result, stacked on FIRE-005 (and FIRE-004/003/002/001) draft PRs. The three older expert modules are imported; this is not a rewrite of them or an autonomous production system.

## The question

Can MOTIF maintain **several live, provisional reasoning approaches**, and revise their influence only when the expected *independently verified value of revision* exceeds its cost? And can an evidence-driven counterfactual rollback improve on a revision without rolling it back?

The fire metaphor: fuel is unresolved investigation; oxygen is genuinely independent evidence; heat is finite reasoning capacity. FIRE-006 adds a **price of moving a working method** while keeping alternative explanations alive. A saved alternative is a *PENCIL hypothesis*, not independently verified truth.

## Implemented

- Three simultaneously running, actual prior research forecasters: `FIRE-003` fixed source-lineage model, original `FIRE-004` Hedge-without-alarm, and `FIRE-005` BOCPD source-change predictor. Every strategy uses their **identical current predictions**, and they all receive the same synthetic independent verification *after* the prediction. No policy gets its test regime, actual source origins, hidden future, or reference answers before predicting.
- Six competing portfolio policies over the same three models: equal-weight preservation, classical exponential expert weighting (EXP3), classical fixed-share expert weighting, a receding-horizon **convex projected-gradient portfolio optimizer** (PROXIMAL3), FIRE-006 gated changes without rollback, and FIRE-006 with **8-round independently verified counterfactual rollback**.
- All pay the **same fixed price** `0.03 × total variation of method weights`. FIRE-006 holds current weights unless the previous verified 16-round evidence predicts enough net improvement over eight future rounds. A rejected revision preserves existing weights and appends a `PRESERVE_PENCIL` receipt; an authorized revision appends a provisional receipt; a regression found on *future verified labels* appends a `ROLLBACK` receipt. Nothing overwrites older observations or predicts a future label by asking the toy oracle.
- Every system reports *all-round forecast Brier*, accumulated revision cost, total verified loss+price, selective coverage, overconfident failures, effective number of retained hypotheses, switches/rejections/rollbacks, and exact receipts. `PREREGISTRATION.md` froze constants and new numeric test seeds before running the experiment.

### Reproduce

Python 3.11 standard library from the repository root:

```sh
python -m unittest discover -s experiments/fire006 -p 'test_*.py' -v
python experiments/fire006/benchmark.py
```

The CI job also executes all earlier FIRE research test suites. The exact committed `results.json` is compared with a fresh independent GitHub Actions rerun; this is CI reproducibility, **not** independent external experimental validation.

## Prespecified experiment — 960 synthetic worlds

New synthetic seeds **106000–106159** in each of six fixed regimes, 96 verified prequential predictions per world (92,160 questions per policy). All-round **Brier + charged revision-price per prediction** is the primary score; **lower is better**.

| Evidence regime | EXP3 classical | FIXED_SHARE3 classical | PROXIMAL3 classical | FIRE-006 no rollback | **FIRE-006** |
| --- | ---: | ---: | ---: | ---: | ---: |
| Steady | 0.065586 | 0.065869 | 0.065790 | 0.065403 | **0.065397** |
| Abrupt source change | **0.064487** | 0.064140 | 0.068940 | 0.068739 | **0.069650** |
| Gradual source drift | 0.122209 | **0.122112** | 0.123702 | 0.125340 | **0.126291** |
| Copied evidence, honest lineage | 0.120322 | 0.120526 | 0.120157 | 0.119526 | **0.119440** |
| Compromised source auditor | 0.175338 | 0.175457 | **0.175207** | 0.175292 | **0.175391** |
| Two-round transient disruption | 0.079500 | 0.079824 | 0.079545 | **0.079019** | 0.079042 |
| **Six-regime macro average** | **0.104574** | 0.104655 | 0.105557 | 0.105553 | **0.105868** |

The **strongest eligible overall comparator is the classical EXP3**, scoring **0.104574**, compared with **0.105868** for FIRE-006. **The prespecified claim of a better total error+revision-cost policy is NOT established.** Ordinary probabilistic reweighting helps enough during drift that its small revision price pays for itself under this synthetic cost assumption.

For transparency: the corresponding macro **raw Brier without revision price** is **0.104079** for EXP3 and **0.105727** for FIRE-006. FIRE-006's macro loss is also **0.000315 worse** than the same method with rollback turned off. This means adding a theoretically appealing safety mechanism can reduce performance in some environments.

### What *did* improve?

FIRE-006 reduces method changes dramatically, preserving a larger live set of alternatives instead of constantly moving all model weights:
- Steady worlds: about **2.74 revisions** per 96-round world, compared with **95 for EXP3** and about **68.95 for PROXIMAL3**.
- Copied-source worlds: about **3.44 revisions** and **0.23 rollbacks** per world, compared with 95 and about 65.6 revisions for those classical comparators. FIRE-006 achieved the best scored total loss in the honest copied-source regime.
- A larger average **effective number of live hypotheses** remains across most worlds (roughly 2.5–2.8 versus 1.8–2.4 for adaptive rivals). This is a measure of retained diversity, **not** independent knowledge or verified novelty.

The cost is predictable: when reality genuinely changes, the conservative gate delays beneficial weight adjustments. FIRE-006 loses notably to conventional exponential weighting in both sudden and gradual shift regimes.

The rollback system is **real and proof-bound within this toy**: it compares the old and new portfolios on subsequent independently verified labels and can revert when the new choice loses. But it **does not outperform the no-rollback ablation overall**. It helps modestly in some copied-source conditions, while hurting more in drift.

## Cautions and next challenge

All world regimes, source audits, truth, and task rewards are engineer-authored. A compromised auditor can still certify forged roots and deceive every live forecaster. The explicit revision price of 0.03 per unit total variation is an **assumed utility unit**, not a discovered universal value; different user goals will require a different objective. The alternative models and counterfactual rollback are bounded and preprogrammed, not discovered autonomously by MOTIF.

The next rigorous question is **how to estimate the actual *opportunity cost* of a revision and the cost of *failing to revise***, rather than assuming a globally fixed price. A suitable future experiment would compare calibrated cost-sensitive online convex optimization with explicit tool/evidence costs against the best classical expert algorithms, using newly declared seeds and a truly independently authored external task stream.

**FIRE-006's achievement is an inspectable experimental decision-and-rollback ledger. It has not beaten established online learning overall.**
