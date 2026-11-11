# FIRE-004 preregistration — The Witness of the Flame

**Frozen before first implementation benchmark.** This is an engineer-authored, deterministic synthetic learning study, not an independently administered blind benchmark. Stacked on FIRE-003 / FIRE-002 / FIRE-001 draft branches.

## Question
Can MOTIF detect when **its own evidence-evaluation method** is becoming unreliable and adapt its reasoning policy before epistemic errors compound? Distinguish the gain of a real feedback-triggered governor from standard classical online statistical models and a no-alarm ensemble.

## Experimental environment, fixed in advance
- 96 sequential binary questions per world, **five reported witnesses every time step**; independent synthetic oracle releases the correct label **after all policies forecast and decide whether to HOLD**. All algorithms receive exactly the same five claims and delayed-after-prediction label. No policy receives the generator's hidden truth, reliability curve, future labels, or true lineage.
- 240 held-out numeric seeds **70000..70239 per regime**; six independently declared regimes:
  1. `steady`: independent sources, accuracy 0.78 throughout.
  2. `abrupt`: three sources change from accuracy 0.88 to 0.12 at time step 48, remaining two stay 0.72.
  3. `gradual`: three sources decline from 0.90 to 0.15 over steps 24..80, others remain 0.68.
  4. `copied`: five apparent witnesses representing three actual parents (multiplicity 3+1+1), truthful source ancestry attested; each root fidelity 0.76.
  5. `compromised`: same copied-source generator, but synthetic auditor falsely certifies five independent origins with plausible metadata.
  6. `transient`: independent sources, generally 0.78 accuracy, but a two-step localized reliability collapse around step 48 (false-alarm pressure).
- Common time steps and data across policies. A claim ID is not a source pedigree; when an honest auditor attests an origin, use one vote per root. If a corrupt auditor attests five fictitious roots, no method should be credited with detecting an otherwise observationally identical lie.
- The synthetic verification result is a **separate trusted simulator truth gate**, deliberately idealized. The model cannot use it before forecasting.

## Fixed policies (no test-set fitting)
1. **FIRE-003** existing fixed `smoke.forecast` with attested lineage and source correctness prior 0.80.
2. **Pooled beta** classical Bayesian learning of a global report-fidelity parameter (Beta prior 4/1), using verified task labels and verified origin deduplication.
3. **Discounted beta** per-source online credibility with pseudocounts and forgetting factor 0.92.
4. **Bayesian HMM slow** per-source two-reliability-state Bayesian filter, known emission probabilities 0.90 / 0.10 and switching hazard 0.005.
5. **Bayesian HMM fast** same exact two-state model, switching hazard 0.08.
6. **Classical hedge ensemble** of fixed FIRE-003, slow/fast HMM, and discounted beta with multiplicative online prequential expert-loss updates and weight discount; **no change alarm**.
7. **FIRE-004** same four experts, same data and compute, and the same hedge updates, plus a prespecified sequential surprise monitor which can activate a bounded fast-expert intervention. Its detection trigger and cool-down must be deterministic and not use hidden regime labels.

The first five are lower-compute baselines. The hedge ensemble is the **matched-model, matched-compute ablation**: it differs from FIRE-004 only by absence of a self-evaluation alarm. The true-latent-reliability `oracle` is an explicitly privileged evaluation ceiling, not an eligible method.

## Metrics and decision criteria
- **Primary**: mean *prequential* Brier across every one of all 96 time steps, **including forecasts that would HOLD**. Lower is better; report per regime and macro average. Report paired FIRE-004 minus HEDGE, Bayesian HMM fast, and FIRE-003, with world-paired descriptive normal-approx 95% intervals.
- **Secondary**: prequential log-loss, calibration, abstention coverage if confidence < 0.70, accuracy on answered rounds, high-confidence wrong forecasts >=0.95, detector alarms per world and estimated detection delay after step 48, and comparison to privileged oracle. Show any adverse regimes and extra cost of abstention.
- **Critical falsifier**: if FIRE-004 cannot outperform the no-alarm ensemble in Brier, do **not** claim self-correction improves learning. Strong Bayesian controls may win. If the guard overreacts to transient errors, report it. If copied evidence with a compromised auditor fools it, report that failure. Any measured gain remains synthetic and does not establish open-world epistemic immunity or autonomous architecture self-modification.
- No permissions or actions outside this repo. No paid infrastructure. Parameter values are frozen before evaluation; changing them after inspecting held-out scores creates a new exploratory version with new future evaluation seeds.

## Guardrail
Observation != independent source; learner prediction != verified event; an internal alarm != proof of change; theoretical knowledge of hidden generator parameters != deployable model; code execution != real-world authorization.
