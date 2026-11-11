# FIRE-006 — The Price of Revision (preregistered protocol)

**Frozen before the first FIRE-006 benchmark.** Stacked draft research on FIRE-005 (then FIRE-004/003/002/001). This is not production or autonomous real-world action.

## Question

Is it better to preserve several evidence-backed reasoning hypotheses in a revisable portfolio, while explicitly accounting for the *price of changing belief*, than to continuously reweight or abruptly select a single method?

Unlike prior FIRE-005 binary switching, all evaluated portfolio policies can maintain **all three live alternative predictors**. A method revision changes only their weights, never the source record or the original models.

## Shared environment and prequential firewall

Use the **unchanged** FIRE-004 synthetic data generator `make_world` and six regimes: steady, abrupt (time 48), gradual, copied roots with honest audit, copied roots with dishonest audit, transient two-step noise. Every round: five witness claims and public attestation; all models predict; a separate synthetic owner reveals the true binary outcome only afterward; then all learners update. No test labels or regime identifiers are passed into any predictor.

Three shared **real, imported** forecasters per world:

- FIRE-003 fixed lineage-aware predictor;
- FIRE-004 original Hedge-without-alarm;
- FIRE-005 original per-attested-root Beta–Bernoulli Bayesian online changepoint predictor (BOCPD; 40-state approximation).

Everyone receives the same three current expert probabilities and the same past independently verified labels. These models run on the same complete 96-round stream regardless of which portfolio policy selects them. True roots and true reliability remain private in the toy owner. A privileged generator-aware oracle may be reported as a nondeployable ceiling, never for policy selection.

### Competing policies and fixed numbers

- **EQUAL3**: permanently preserve one-third weight in each of the three experts.
- **EXP3**: standard three-expert exponentially weighted average with learning rate **2.0** on each expert's verified per-step squared loss; no future labels.
- **FIXED_SHARE3**: standard three-expert exponential weights plus **0.02 share** toward uniform each verified step; same learning rate **2.0**.
- **PROXIMAL3**: conventional receding-horizon convex mixture optimizer. At each verified step, optimize the last **16** rounds' *joint portfolio* Brier plus quadratic proximity penalty **0.015**, using **12** deterministic projected-gradient iterations (step size **0.35**). Move immediately. This is the main matched-model classical optimization control.
- **FIRE006_NO_ROLLBACK**: same optimized candidate but refuses reweighting unless the last-16-step counterfactual estimate predicts at least **0.012** benefit over the next **8** decisions *after* paying the explicit revision cost and an uncertainty margin `0.012 × stdev(per-round signed loss gain)`. Cooldown between decisions is **8** steps. A rejected proposal holds existing weights in **PENCIL**.
- **FIRE006**: same risk-gated portfolio, plus an **8-round counterfactual trial**: keep the superseded weights as a live shadow (without changing base predictors), compare both using subsequently independently verified scores, and rollback if the trial is worse by more than **0.005 mean Brier**. Rollbacks are recorded, never retroactively revise predictions.

For all policies, at each step the revision price is **0.03 × total-variation distance** between new and old weight vectors, `TV = 0.5 × sum |new_i - old_i|`. Constant weights cost zero; EXP3/FIXED_SHARE/PROXIMAL pay the same price every time they reweight. To compare fairly all methods start at uniform weights, and all base experts run at the same observation/computation cost. For FIRE-006, explicit `revision`, `hold`, `trial`, and `rollback` receipts are append-only.

Neither FIRE-006 portfolio is a new generalized reasoning model: it's a finite governing policy over existing forecasters. A source *claim* remains separate from independent origin evidence; forged attestations are a deliberately unresolved falsifier.

## Fixed validation and test

- Engineering tests: deterministic seeds **95000–95019** only; no performance calibration on held-out worlds.
- **Held-out numeric test**: seeds **106000–106159**, 160 worlds per regime, six regimes = **960 worlds / 92,160 prequential predictions per policy**. There is **no hyperparameter sweep on test worlds**. If this experiment disappoints, preserve it and use newly declared seeds for a future revision.

## Primary and secondary metrics

**Primary:** *verified-loss-plus-revision-price* per decision: `mean_all_step_Brier + sum(0.03 × TV) / 96`. Lower is better. Account for every round (including low-confidence/HOLD forecasts). Show the raw Brier and revision price components separately, macro average across six regimes, paired world-level normal-approx 95% descriptive intervals for FIRE006 minus PROXIMAL3, FIXED_SHARE3, EXP3 and FIRE006_NO_ROLLBACK.

**Secondary:** ordinary Brier and log loss, 16-step early/late post-change Brier windows, confidence coverage (<0.70 is HOLD but still scored), revision count, rejected proposals / preservation, rollback count, observed post-revision counterfactual regret and false positive rollback frequency in steady/transient regimes.

**Falsifier:** a reduction in revisions is not a win unless the *all-step verified-loss-plus-revision-price* improves against the strongest conventional baseline. Preserving alternatives in parallel is not evidence of self-improving intelligence by itself. Rollback only proves the code can undo a policy change after observed loss; it does not prove the original change was intrinsically wrong. If a revised method becomes necessary under drift, the gate may delay useful adaptation. Report negative results and dishonest-auditor failures candidly.

This benchmark is wholly synthetically authored; no field source authentication, external effects or independent real-world validation.
