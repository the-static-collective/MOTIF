# FIRE-004 — The Witness of the Flame

**Experimental research — HOLD.** This is a proposed fourth stage of the cognitive-fire metaphor: can a reasoning system identify errors in **the way it learns**, not merely errors in the conclusions it reaches?

The experiment uses real implementations of the existing FIRE-003 `smoke.forecast` source-lineage check, a conventional global Beta credibility learner, a per-source exponentially discounted Beta learner, two **exact two-state Bayesian HMM reliability filters**, a standard Hedge expert mixture, and a matching Hedge mixture with an extra self-monitoring surprise alarm.

All eight predictors use the same five synthetic witness claims at each time step; the correct outcome is supplied by a **separate synthetic verification oracle only after forecasts**. Source ancestry is attested in the honest-source cases; a falsified auditor is an explicit adversarial condition. No system is authorized to act in the outside world.

## Reproduce

Python 3.11, standard library:

```sh
python -m unittest discover -s experiments/fire004 -p 'test_*.py' -v
python experiments/fire004/benchmark.py
```

Tests include prediction-before-feedback, stale/untrusted label rejection, no access to future source reliability or hidden truth through public observations, bounded alert behavior, duplicated/compromised provenance, and deterministic replay. Full frozen evidence is in `results.json`; a dedicated GitHub Actions workflow reproduces and checks it.

## Primary study: 1,440 engineer-authored synthetic worlds

A complete 96-step sequence per world, with 240 new numeric seeds in each of six prespecified evidence regimes. **Mean prequential Brier score on every question**, not only answered questions. Lower is better.

| Evidence regime | FIRE-003 fixed | Discounted Beta | HMM slow | Classical Hedge, no alarm | **FIRE-004 alarm** | Privileged oracle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Steady independent sources | **0.0612675** | 0.0714925 | 0.0766089 | 0.0652753 | 0.0690940 | 0.0611249 |
| Abrupt source reversals at step 48 | 0.3420993 | 0.0974282 | 0.0594974 | 0.0614049 | **0.0580946** | 0.0282675 |
| Gradual reliability deterioration | 0.2766808 | 0.1295958 | 0.1330659 | 0.1287177 | **0.1249362** | 0.0882752 |
| Three roots behind five claims; honest audit | **0.1152689** | 0.1245921 | 0.1371178 | 0.1197053 | 0.1257716 | 0.1142718 |
| Same copied roots; auditor lies | 0.1890204 | **0.1798856** | 0.2155841 | 0.1822606 | 0.1862532 | 0.1138176 |
| Two-step transient failure | **0.0762159** | 0.0844332 | 0.0933785 | 0.0831142 | 0.0879136 | 0.0567668 |
| **Unweighted six-regime mean** | 0.1767588 | 0.1145712 | 0.1192088 | **0.1067463** | 0.1086772 | 0.0770873 |

The privileged oracle sees true generator reliability and ancestry, so **is not a deployable method**. HMM fast and pooled Beta are also fully reported in `results.json`, not hidden.

### Important positive AND negative results

**Positive, narrowly scoped:** FIRE-004's post-verification change alarm improves the matched-compute, matched-expert, no-alarm Hedge by **−0.0033103 Brier** in the abrupt-shift regime (world-paired descriptive 95% interval **[−0.0037521, −0.0028686]**) and **−0.0037815** in gradual drift (interval **[−0.0045045, −0.0030585]**). For abrupt reversals, its Brier in the 16 steps immediately after the true switch is **0.0264392 lower** than Hedge (descriptive interval **[−0.029206, −0.0236724]**). These are genuine synthetic benefits on the prespecified primary scoring rule.

**Negative, decisive:** The same alarm **harms calibration in all four other regimes** and has **worse average Brier across all six regimes**: **0.1086772 vs 0.1067463** for the matched-compute classical Hedge. A steady world triggers **3.675 alarms on average**, *more* than the abrupt-change regime's **3.0125 alarms per world**. **62.5% of steady worlds generated an alarm in the arbitrary 48–64 window**, despite no true change. In the copied-source regime the alarm worsens Brier by **+0.0060663** versus the no-alarm Hedge (interval **[+0.0057045, +0.0064281]**). Under a compromised provenance auditor, it also loses to Hedge. Transient noise often provokes an unjustified method switch.

**Interpretation:** We constructed a *functional, receipt-gated self-monitoring and corrective-switch mechanism*, not an effective generally reliable change detector. A method can be beneficial precisely when reality shifts yet harmful because its **alarm policy cannot reliably distinguish genuine change from ordinary surprise**. The ability to revise cognition does not establish the wisdom of the revision.

### The unresolved frontier

We should next test a `FIRE-005` independent *change vs noise adjudicator*: calibrated changepoint posterior and delayed evidence requirements before altering the reasoning policy, with explicit reversal/rollback after false alarms. Require source-identity consistency across time, account for bogus lineage attestations, and benchmark against a properly specified Bayesian online changepoint detector and strong non-alarm ensemble on **new external task streams or genuinely fresh seeds**, without retroactively claiming this study succeeded overall.

Do **not** retune FIRE-004 thresholds after reading these scores and continue calling the same 70,000-series seeds a clean test. The code and current negative study are preserved as a reconstructible research trace.

**A successful self-correction needs evidence that a correction was warranted, not merely evidence that the system changed its mind.**
