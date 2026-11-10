# MOTIF-GENIUS-005 — EVIDENCE BEFORE REVISION

**Research HOLD — local experiment on an unmerged stacked draft, not a deployed Trench/MCP system.**

## Why the crater matters

GENIUS-004's "humility" operator, despite intuitively sensible REVISE/REFRAME/RELEASE labels, **lost against the strongest conventional prediction method on every tested synthetic scenario**. It also flagged hundreds of ordinary stationary fluctuations as apparent changes. The correct next question is not "can we give it more cognitive mode names?" but rather:

> **What amount of evidence warrants revising a model, and how do we distinguish genuine persistent change from chance variation?**

The immediate technical result is a new independently checkable observation protocol, not a claim that MOTIF has developed human insight or invented a novel inference algorithm.

## Shoulders of giants

- **Fisher's exact conditional two-sample test**: for fixed sample sizes, compare reference/future binary-response tables using the exact hypergeometric distribution conditional on table margins, without assuming a known population Bernoulli rate. Implemented directly with Python integer combinatorics. This is an existing classical test.
- **Bonferroni / family-wise multiple-testing correction**: up to **12 predetermined tests** per stream, each at 0.05/12, bound the probability of **one or more** false alarms under the specified IID Bernoulli no-change null by <=0.05. Tests can overlap or be correlated; the union bound still applies. But the null must be correct and test times/patterns fixed independently of the values. This is **per stream**, not a global guarantee across arbitrary populations.
- **Classical CUSUM**: two-sided log-likelihood accumulation for proposed upward/downward changes, with a baseline probability estimated from 40 reference labels. Its estimated baseline and selected threshold **do not** grant exact false-alarm control.
- **Established online adaptation**: cumulative empirical Bernoulli, short fixed windows, exponential weighted moving average (EWMA), and standard Hedge/exponentially weighted expert predictions.
- **2026 benchmark-design warning**: Cerqueira, Gomes, Heyden, Pfahringer & Bifet, *A Framework for Evaluating and Benchmarking Concept Drift Detection Methods*, KDD 2026, https://doi.org/10.1145/3770855.3819070. Independent datasets, comparable false-alarm/delay metrics and explicit hyperparameter-selection isolation are important. This project adopts only a small part of that discipline; it is **not** a reproduction of their benchmark or real-world validation.

## Executable methods and control arms

The module **detectors.py** includes:

- An exact two-sided hypergeometric p-value calculation, with alternative tables and edge cases tested.
- Exactly 40 reference public binary outcomes, a 24-public-report moving comparison window, and 12 fixed checkpoints (public report indices 24,32,...,112).
- A conservative Fisher/Bonferroni alarm (EXACT), an uncorrected rolling-gap alarm (NAIVE), and a two-sided Bernoulli CUSUM.
- Source-bound alarm receipts. The controller receives only already shared binary reports plus source IDs; it **cannot** see the evaluator's true shift time or generator probabilities.

The module **benchmark.py** evaluates **prequential** forecasting (predictions recorded *before* each shareable outcome is observed), across eight decision arms:

1. FROZEN: baseline frequency stays at initial 40 reports.
2. CUMULATIVE: every previous public label updates the estimate.
3. WINDOW8: fixed recent eight shared observations.
4. WINDOW24: fixed recent 24 shared observations.
5. EWMA: exponential recency weighting.
6. HEDGE: conventional exponentially weighted experts combining the preceding online estimators.
7. EXACT_SWITCH: cumulative until EXACT fires; then use WINDOW8.
8. CUSUM_SWITCH: cumulative until tuned CUSUM fires; then use WINDOW8.

The switches are simple **classical model-selection rules**, not newly discovered mathematics. Each method sees the same previous information and future public observations; private/withheld labels are never scored, learned or published. No one is contacted, no messages are generated, and nothing is deployed.

## Strict sequential order / freeze

Validation uses seeds **50501/50502** across five engineer-authored scenario families. The CUSUM threshold is chosen from a predeclared small grid (4.5, 6.0, 8.0) using only validation alarms, misses, and delay. Freeze CUSUM threshold, fixed Fisher schedule, comparison arms, heldout seed list and all evaluation settings with SHA-256.

**Only after the frozen plan** are future worlds created from separate seeds **50541/50542/50543**. Each regime has 12 synthetic streams per seed. Every stream has 40 reference labels and 120 future opportunities; predictable non-outcome-based withholding removes some reports.

| Family | Ground-truth construction | What could go wrong |
| --- | --- | --- |
| STABLE | Four distinct fixed Bernoulli rates | Repeated observations falsely interpreted as structural change |
| NOISY_STABLE | Fixed near-50/50 Bernoulli rates | Chance produces large swings despite no underlying drift |
| ABRUPT | All streams reverse their probability after future round 40 | The detector misses or reacts too late |
| LOCAL | Only one-third of streams reverse | Overgeneralizing an exceptional stream to the group |
| GRADUAL | Rates interpolate toward their opposites over 48 rounds | No obvious instantaneous boundary; slow drift obscured |

Score **per-stream null false-alarm rate, changed-stream detection rate, delay from defined start**, and **mean prequential Brier** for every forecast arm. Detection and forecasting are different objectives; lower false alarms may trade against slower recognition. For gradual drift, time from its defined beginning is only an operational delay proxy.

### Scope of the exact mathematical guarantee

Under the narrowly defined null, one stream's 40 reference responses and each predetermined window of 24 future shared responses are IID draws from the *same unknown constant Bernoulli probability*. Fisher's exact two-sided test is finite-sample valid unconditionally, and summing 12 per-test errors by the union bound controls that stream's probability of at least one false alarm at <=0.05.

**Not guaranteed** under reporting dependent on the hidden outcome, time-correlated choices, shifts in who is sampled, repeated outcomes from one latent event, adaptive checkpoint selection, strategic behavior, or evolving preferences. There is no verified inference about actual humans. The strong bound is *an implementation of pre-existing mathematics under restrictive assumptions*, not new mathematics.

For the adaptive CUSUM, the 40-sample estimated baseline is treated as an approximation only. Its threshold is selected on validation data and then frozen; no significance or family-wise guarantee is asserted.

## Reproduce

Run from the MOTIF checkout at this branch:

~~~sh
python -m unittest discover -s experiments/genius005 -p 'test_*.py' -v
python experiments/genius005/benchmark.py > /tmp/motif-genius005-evidence.json
python -m json.tool /tmp/motif-genius005-evidence.json >/dev/null
~~~

The CI workflow tests the inference contracts and archives **synthetic, source-attributed** event-level receipts for inspection. The generator's latent rates and private text are never provided to detectors or public outputs. Inferred metrics and the evaluator's ground-truth start times are marked separately from raw prediction evidence.

## Scientific result status / real frontier

All generator families, datasets, thresholds, and expected concepts are engineer-authored. Even strict separation of different PRNG seeds is not **independent data authorship** or external blinded verification. A success here would demonstrate the classical detector's behavior on these toy conditions, not autonomous human-level reason or generalized Trench intelligence.

Potential next challenges: independent authored multivariate environments, truly voluntary external reports, pre-registered detector settings, calibration under non-IID outcomes, strong River/ADWIN and change-point baselines, explanation cost, and evaluating whether better drift evidence improves **verified joint problem solving** rather than just probability scores.

**Core rule: uncertainty is not contradiction; contradiction is not necessarily change; change is not proof of an explanation.**


## First measured results and optional evidence gate

See [RESULTS.md](RESULTS.md) for the complete initial synthetic results: **exact Fisher/Bonferroni produced 1 false alarm among 72 stationary streams, versus 60/72 for a naïve gap alarm**, and detected 36/36 abrupt, 12/12 localized, and 35/36 gradual synthetic changes. It was usually *slower* than tuned CUSUM. Crucially, its simple post-alarm WINDOW8 forecast switch **did not outperform strong classical HEDGE in any shifted scenario**. Better diagnosis is not automatically better prediction.

An added local-only module [evidence_gate.py](evidence_gate.py) packages the conditional evidence as a **proof-carrying preview proposal**, including source-owned reference IDs, a supporting 24-report window, exact p-value, corrected test threshold, declared sampling assumptions, and next research question. It returns explicit HOLD cases for duplicates, unshareable/foreign reference data, deficient monitoring and unverified sampling plans; it never authorizes automatic revision or any external action.

The adapter and its adversarial tests were developed *after* the initial holdout inspection, so the original holdout cannot establish the adapter's independently predictive performance. No attestation boolean authenticates consent or independently establishes IID sampling.
