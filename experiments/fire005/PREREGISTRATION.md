# FIRE-005 — THE DISCERNMENT FRONTIER: preregistration

**Registered on the branch before implementation, tests, or numeric evaluation.** FIRE-005 is a synthetic research extension of stacked FIRE-004, FIRE-003, FIRE-002 and FIRE-001 draft PRs. It does not add real-world authority.

## Motivating hypothesis

FIRE-004's short-term surprise alarm improved abrupt/gradual source change but damaged steady, copied, corrupted-auditor, and transient regimes. Can a cognitive governor distinguish *sustained evidence of improvement by an alternative method* from a temporary surprise, perform a **reversible, proof-carrying policy switch**, and outperform a strong classical online mixture of the same forecasters?

An alarm is a question, not proof. A method change is provisional and reversible. All evaluation is prequential: forecast before independent label arrives.

## Fixed data and no-leak protocol

Use the *unchanged source* `experiments/fire004/flame.py` `make_world` generator, public `view` and verification receipt `verify`, with six already defined regimes: steady, abrupt switch at t=48, gradual drift, copied sources with honestly attested common ancestry, copied sources with dishonest distinct-root attestation, and two-step transient disruption at t=48-49. All 96 steps for each world, five claims each, fixed external simulator label revealed only **after** all predictions.

**New evaluation seeds: 81000–81159 (160 worlds per regime, 960 worlds / 92,160 questions).** These are not used for threshold tuning or debugging. Separate deterministic development-only seeds are 91000–91019 (implementation checks, not performance claims). No fitting controller parameters on held-out scores.

## Prespecified forecasters / comparators

1. **FIRE-003**: existing fixed lineage-aware model.
2. **FIRE-004**: existing self-triggering surprise-alarm Hedge ensemble.
3. **HEDGE**: exact same four-expert classical online ensemble from FIRE-004, *without* the alarm.
4. **BOCPD**: standard Beta–Bernoulli Bayesian online changepoint filtering **per attested origin** over correctness outcomes from verified labels only. Per-root run-length posterior, segment prior Beta(2,1), hazard .025, at most 40 posterior states retained by probability, no hidden labels or regime names. It models source reliability changes explicitly and accepts neither audit metadata nor source IDs as physical authenticity.
5. **MIX-50**: unchanging 50/50 arithmetic mixture of HEDGE and BOCPD.
6. **HEDGE-2**: a conventional online multiplicative-weights mixture of HEDGE and BOCPD with forgetting exponent .97 and Brier-loss learning rate 2.0, after each verified label. **This is the principal matched-expert classical comparator.** It uses the same two expensive models as FIRE-005.
7. **REGRET-ONLY** ablation: same two forecasters, same regret windows, same reversible switching, but no changepoint posterior guard.
8. **FIRE-005**: same two forecasters, but switches *only* after both a sustained prequential improvement by BOCPD and an independent BOCPD changepoint indicator; reverses when verified evidence no longer supports the selected method.

### FIRE-005 reversible rule (fixed)

Base mode HEDGE. Track the latest 12 per-step signed Brier losses: `r_t = (HEDGE_t - y_t)^2 - (BOCPD_t - y_t)^2`. Track the latest six `BOCPD` change indicators: at least two rounds with mean per-source changepoint posterior > .035, computed only **after verification** of those rounds.

Switch to BOCPD for subsequent predictions if: >=12 verified paired scores, 12-round mean regret >= .012, >=8 positive regret samples, >=2 recent changepoint indicators, and minimum 12-step cooldown. REGRET-ONLY uses same rule without the last condition. Stay in BOCPD for at least eight subsequent observations. Roll back to HEDGE if the most recent 8-step mean signed regret <= -.007. Log decisions as `PENCIL` proposals with source-step receipts, not altered old evidence. Re-entry allowed only after cooldown. A null alarm is not treated as ground truth.

### Monitoring and test metrics

**Primary:** mean all-96-step prequential Brier, across all regimes (unweighted macro mean) and per regime. Paired world-level 95%-normal-approx descriptive intervals for FIRE-005 minus HEDGE-2, BOCPD, HEDGE, FIRE-004, REGRET-ONLY. Lower is better.

**Secondary:** mean prequential log loss, 16-step post-abrupt Brier (48–63) and late (80–95), HOLD at confidence <0.70 (still scores Brier on those forecasts), overconfident failures, inferred changed vs stable moments, new method-switches, reversals, false alarms in steady and transient regimes, audit provenance deficiencies. The unchanged FIRE-004 privileged oracle is reported as a non-deployable ceiling, never used in policy selection.

**Decision rule:** If FIRE-005's macro Brier fails to beat strong classical HEDGE-2, it does *not* demonstrate improved general self-correction. If it reduces harmful alarms in steady worlds but misses genuine drift, report that tradeoff explicitly. If forged audit remains indistinguishable, report it. A lower number of alarms without improved prediction doesn't imply successful discernment.

## Boundaries

Source lineages remain idealized and synthetic; a compromised synthetic auditor can lie. BOCPD and Hedge are well-established statistical methods, not novel math or unbounded recursive self-improvement. The reversible governor does not edit code, overwrite history, issue external commands, or establish authorization. The unit of research evidence is the independently checked, source-scoped prediction receipt.
