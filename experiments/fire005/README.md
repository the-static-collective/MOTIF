# FIRE-005 — The Discernment Frontier

**Research HOLD — executable, reproducible negative overall result.**

This fifth experiment is stacked on unmerged FIRE-004 → FIRE-003 → FIRE-002 → FIRE-001 research branches. It tests whether a reasoning system can distinguish a genuine failure of its own research method from transient surprise, and reverse a bad methodological correction without rewriting historical evidence. It has no authority to act outside the simulator or modify its own code.

## What is actually implemented

- A new **standard Beta–Bernoulli Bayesian online changepoint (BOCPD) filter**, one posterior for each *attested* source origin. It updates run-length hypotheses only after separate synthetic verification. Prespecified hazard 0.025, segment Beta(2,1) prior, and a maximum of 40 posterior components. The finite cap is an approximation, not unconstrained exact inference.
- Real original FIRE-004 **Hedge (without alarm)** and **Hedge (with alarm)** are imported and run using identical observations.
- A full-support classical **two-expert multiplicative-weights controller** (`HEDGE-2`) updates the relative contributions of Hedge and BOCPD on prequential losses. Unlike a binary switch, it can weight both methods continuously.
- **FIRE-005** makes a reversible binary method change when both the latest 12 verified paired forecasts support BOCPD and a separate six-step changepoint posterior monitor offers two change signals. A BOCPD method choice can be rolled back after sufficient verified underperformance; explicit `PENCIL_REVERSIBLE_METHOD_EDIT` receipts preserve when and why the policy changed.
- The `REGRET-ONLY` ablation applies the same reversible switch logic *without* requiring the changepoint detector, isolating the detector's incremental value.
- No policy receives actual answers, true source ancestry, or hidden reliability before making its prediction. The generator includes a **dishonest lineage auditor** that can still deceive BOCPD.

Run from repository root (Python 3.11, standard library only):

```sh
python -m unittest discover -s experiments/fire005 -p 'test_*.py' -v
python experiments/fire005/benchmark.py
```

All **50 tests across FIRE-001..005 passed** in GitHub Actions. `PREREGISTRATION.md` was committed before scoring, and `results.json` preserves the completed new-seed study.

## Primary result — negative on overall verified forecasting accuracy

New, prespecified study: **960 engineered synthetic worlds**, 160 seeds in each of six regimes and 96 prequential forecasts per world (**92,160 decisions**). Brier scores include all forecasts, including low-confidence/HOLD forecasts. **Lower is better.**

| Evidence regime | Classical HEDGE | Classical HEDGE-2 | FIRE-004 | BOCPD | **FIRE-005** |
| --- | ---: | ---: | ---: | ---: | ---: |
| Steady independent evidence | 0.063163 | 0.064795 | 0.066644 | 0.069374 | **0.063170** |
| Abrupt reliability reversal | 0.061859 | **0.060530** | 0.058348 | 0.063430 | **0.061738** |
| Gradual deterioration | 0.128024 | **0.120346** | 0.124148 | 0.118624 | **0.128143** |
| Copied source roots, honest provenance | 0.120228 | 0.122046 | 0.126445 | 0.127428 | **0.120249** |
| Copied roots, compromised provenance | 0.180544 | **0.174096** | 0.184546 | 0.172559 | **0.180467** |
| Two-step transient anomaly | 0.088190 | 0.088652 | 0.093264 | 0.091721 | **0.088204** |
| **Macro mean, six regimes** | 0.107001 | **0.105077** | 0.108899 | 0.107189 | **0.106995** |

The strongest eligible macro comparator is **HEDGE-2**, the conventional adaptive mixture of the **exact same two underlying methods** used by FIRE-005. FIRE-005's macro Brier is **+0.00191778 worse**, not better.

A privileged generator-aware oracle had macro Brier 0.076962, but is ineligible as a real predictor. The mixed static model and other controls are recorded in `results.json`, not omitted from evaluation.

### How the guard behaved

FIRE-005 was cautious about changing models: only **0.0125 method entries per steady world** and **0.0375 per transient world**. Its change requirement reduced some harmful changes compared with REGRET-ONLY, and FIRE-005 beat the older FIRE-004 in the steady, duplicated, compromised, and transient scenarios.

However, it **usually missed real change**: only **3.75% of abrupt-change worlds** switched to BOCPD within steps 48–64, and **0% of gradual-change worlds** switched in that window. It delivered a lower Brier than HEDGE-2 in the *early* 16-step window after abrupt reversal (paired difference −0.00314586, interval [−0.00543262, −0.00085910]), but **worse** Brier in the later recovery window (+0.00514897, interval [+0.00332054, +0.00697740]).

In gradual drift it lost to HEDGE-2 by **+0.00779665** over all 96 steps (paired world-level descriptive 95% interval [+0.00706405, +0.00852924]). In compromised-auditor worlds it lost to HEDGE-2 by **+0.00637086**. In honest copied-source worlds its conservative method switching did help relative to HEDGE-2 (−0.00179652).

**The effect is a genuine trade-off, not an overall win:** waiting for repeated confirmation avoids overreacting to noise, but can delay warranted correction. An online continuous combination can preserve the benefits of multiple models without making a brittle binary choice.

## Important epistemic and implementation limits

1. Method changes are **bounded choice of an existing forecaster**, not invention of a new reasoning method, arbitrary self-modification, autonomous recursive improvement, or demonstrated general intelligence.
2. A BOCPD posterior is only as reliable as its model assumptions and declared source grouping. The compromised lineage attestation remains an unresolved hard failure; report agreement is not proof of true independence.
3. The generator, auditors, labels and regimes are engineered synthetic fixtures; successful reproduction is not independent real-world field validation.
4. Many old FIRE-004 tests were retained, but previously seen 70000-series scores cannot be repurposed as fresh FIRE-005 testing. The **new 81000-series** was registered before seeing results.
5. Changing thresholds using these 960 evaluation worlds would contaminate their held-out status. Any new variant requires a **new** preregistration and future test seeds.

## Next frontier — not a victory lap

A sixth experiment should challenge the binary-switch formulation itself. Use *calibrated model posterior weights* with an explicit no-change/noise alternative, prospective decision-cost and rollback budget, and better uncertainty about the source auditor, then compare against a strengthened classical Bayesian model averaging benchmark. Require an independently authored public sequence or new frozen seeds, with actual incremental advantage over HEDGE-2 as the advancement criterion.

**The question isn't merely whether MOTIF can reconsider a method; it's whether the evidence warrants paying the cost of abandoning a currently useful one.**
