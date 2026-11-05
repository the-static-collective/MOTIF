# MOTIF-013 — THE PROBABILISTIC WITNESS
## What if the witness is wrong, the intervention fails, and the outcome is genuinely random?

**Research question:** Can a relational scientist retain uncertain, contradictory, partially witnessed evidence; estimate the credibility of distinct upstream reporters from *separate adjudicated observations*; account for failed or unverified interventions; make probability forecasts rather than force binary certainty; and know when to abstain?

**Status:** Executable standard-library Python with a **seeded pseudorandom stochastic simulator** and actual probabilistic likelihood calculations. This is a better uncertainty experiment than the deliberately deterministic MOTIF-001–012 worlds, but it is still **entirely invented evidence**. It is NOT real-world source authentication, genuine external sensor data, physical causal discovery, an LLM, or autonomous action.

## The architecture: uncertainty is part of the world model

MOTIF-012's intervention outcomes were mostly exact programmed functions. The new independent simulator [oracle.py](oracle.py) draws every underlying outcome from a **Bernoulli distribution** conditional on the *actually applied* controls—not the requested ones. It separately draws whether each actuator complies and whether each witness reports the right outcome.

An observation now has several distinct truths:

\`\`\`text
    PROPOSED INTERVENTION
             |
    actuator may FAIL to comply
             |
     ACTUAL CONTROL SETTING  ---- a verified crossing receipt may be MISSING
             |
     TRUE SIMULATED OUTCOME  ---- NEVER given to inference on train/test
             |
       UPSTREAM SOURCES
        /      |      \
      reliable weak  contrarian
        \      |      /
      independently reported claims (some missing)
           |
      forwarded COPY of a report ---- same origin, NOT a second witness
           |
        SOURCE-CHECKED GRAPH + CLAIMS
           |
     CALIBRATED BAYESIAN LIKELIHOOD
           |
      WEIGHTED 009 TREE CARTRIDGES
              + OTHER
           |
   PROBABILITY + UNCERTAINTY + HOLD
\`\`\`

The simulator has **three independent upstream witness channels** with different, world-hidden probabilities of telling the truth (approximately **0.86–0.96**, **0.59–0.76**, and **0.12–0.31**). The third source is **systematically misleading**: calibrated reporting accuracy can be below 50%, and a false report may actually *increase* the probability that the true outcome was success.

An additional "forwarded" reporter republishes the first source's exact claim with the same source-origin identifier. The learner **deduplicates** these reports instead of treating them as two independent confirmations. If two reports claiming the *same* upstream origin conflict, the record is **HOLD**, not twice counted.

Each report can be missing; each actuator can fail to apply its intended setting. Most training attempts have an independently marked synthetic applied-control receipt, but a fraction do not. **Without a receipt of what was actually applied, the learner conservatively refuses causal attribution from that event**. It does not equate an instruction with its observed consequence.

### What information the learner actually receives

The evaluator creates a secret \`SecretTrial(public, realized_controls, true_outcome)\`. Only the \`PublicTrial\` is supplied to [witness_model.py](witness_model.py): a role-relative graph of the commanded controls, the public intended control pair, possibly a synthetic audited applied pair, and noisy attributed witness reports. The public object does **not contain** the true outcome, hidden generating mechanism, true reliability probabilities, or private world state.

A **different calibration batch** supplies only *aggregate* adjudicated counts—60 for each of three source origins and 80 for each of two actuators, per world. These are deliberately independent from the model-training and final test events. Nothing about the oracle's rule family is supplied by calibration.

The source simulator is allowed to know hidden truth; the learner isn't. This separation is tested.

## The actual probability calculation

Each source correctness probability has an independent Beta prior \`Beta(2,2)\`; the calibration updates it to:

\`reliability_source ~ Beta(2 + correct, 2 + incorrect)\`

Each actuator compliance probability has the same type of prior and update, independently.

The learner's four structural hypotheses—FIRST, SECOND, AND, OR—are represented by **real portable MOTIF-009 two-question decision-tree cartridges**. A fifth \`OTHER\` model retains explicit mass for an unrepresented explanation; it is **not** turned into a fake deterministic tree.

The tree hypotheses and probability-of-outcome templates are *declared*, not learned from nothing: an in-grammar hypothesis predicts a success probability **0.85** if its Boolean rule is true and **0.15** if false. OTHER predicts **0.50** for every intervention. Initial weights are 0.85/4 per known tree and 0.15 for OTHER.

For a given verified applied setting, a model's witness-evidence likelihood marginalizes the *unobserved true outcome*:

\`\`\`text
P(reports | tree)
 = P(success | tree) × Π_origin P(report_origin | success)
 + P(failure | tree) × Π_origin P(report_origin | failure)
\`\`\`

The product contains **one report per independently declared upstream origin**, not copies of the same rumor. As new records arrive, the model adds log-likelihoods to the prior log weights and normalizes the resulting probability masses.

For a *future commanded* intervention, the forecast also sums over the four possible actually applied control settings, weighting each by separately calibrated compliance. That gives a numerical probability of success, not an assertion of guaranteed success.

**Scope qualification:** This is an **approximate plug-in Bayesian model**, not a full hierarchical Bayes model. It substitutes the source and compliance Beta posterior *means* during fit, instead of integrating uncertainty about those parameters across all observations. Its displayed 90% Monte Carlo probability interval samples model choice and compliance but not the source-likelihood posterior; it must **not** be called a fully calibrated credible interval.

Separate 90% source reliability intervals *are* sampled from each source's actual adjudicated Beta posterior. Their meaning is source correctness under the simulator's calibration regime, not proof of human honesty or authenticated identity.

### Prediction decisions are distinct from internal forecasts

Every held-out instance receives an **internal** probability estimate so that no failures disappear from Brier-score or log-loss evaluation.

A separate decision gate may decline to **issue** a prediction to a hypothetical user:
- \`HOLD_OUTSIDE_MODEL_FAMILY\` when OTHER has at least 40% posterior weight.
- \`HOLD_MODEL_UNCERTAINTY\` when no named tree has at least 70% weight.
- \`HOLD_PREDICTIVE_SHIFT\` when an independent validation witness batch gives substantially worse predictive likelihood than the declared OTHER reference.
- \`PREDICT_PROBABILITY_ONLY\` otherwise.

The validation threshold is a *development heuristic*, **not a calibrated drift-test false-positive rate**. A time-shift that occurs only after validation would remain undetectable before the change happens.

## Matched benchmark: a stronger classical Bayesian competitor

The independent evaluator [benchmark.py](benchmark.py) compares the structural cartridge posterior with a real, flexible Bayesian alternative.

**Classical Bayesian four-cell baseline:** Rather than assume one of the four Boolean programs, fit an *independent success probability for each of the four verified control configurations*, with \`Beta(2,2)\` priors and a 121-point numerical posterior grid. Crucially, it receives the **same independent calibration, same verified training controls, same deduplicated witness reports and same test commands**, and marginalizes the noisy underlying outcome through the identical witness likelihood. It does not use hidden true labels or the oracle's intervention mechanism.

This is a substantive comparison, not a random or deliberately weak majority baseline. Like the structural model, it uses plug-in source reliability estimates.

An additional deliberately weak source-blind baseline counts reports as equal votes; a privileged oracle-based model exposes the **unattainable performance reference** available only to the evaluator, not the learner.

### Frozen synthetic protocol

- **6 families × 5 seeds = 30 stochastic simulated worlds.**
- **80 training trials, 32 independent validation trials, 120 held-out test trials each**: 2,400 training, 960 validation and **3,600 held-out probabilistic outcomes**.
- **Independent calibration:** 60 adjudicated samples × 3 sources plus 80 verified compliance samples × 2 actuator channels per world.
- Model families: FIRST, SECOND, AND, OR, out-of-grammar XOR and regime SHIFT (training FIRST; validation/test SECOND).
- Trial outcomes, witness correctness, dropout and intervention compliance are drawn using \`random.Random\` Bernoulli sampling and **independent hashed phase/seed streams**. This is statistical simulation with reproducible pseudorandom draws, not deterministic Boolean outcome labels or cryptographic unpredictability.
- Model selection never sees held-out true outcomes; final test scoring evaluates every internal probability, even ones marked HOLD.

### Actual independently reproduced results

The [full 30-world, per-family result receipt](experiment-results.json) includes all families and negative results.

| Held-out metric, 3,600 outcomes | MOTIF probabilistic tree ensemble | Classical Bayesian four-cell |
|---|---:|---:|
| Mean Brier score (lower is better) | **0.228364** | **0.224069** |
| Mean log loss (lower is better) | **0.651315** | **0.641032** |

The source-blind weak baseline scores **0.242385 Brier**, and the unattainable true-world oracle reference scores **0.199130 Brier**.

**The classical Bayesian baseline BEATS MOTIF overall.** The probabilistic tree grammar does better on several supported in-grammar world families, but is penalized for being confidently wrong when the mechanism lies outside that family or changes over time. We must not describe this as superiority or a discovery of new Bayesian mathematics.

| Synthetic family | MOTIF Brier ↓ | Classical Bayesian Brier ↓ |
|---|---:|---:|
| FIRST | 0.202544 | 0.209510 |
| SECOND | 0.198106 | 0.210294 |
| AND | 0.190731 | 0.199201 |
| OR | 0.203160 | 0.206997 |
| **XOR (out of grammar)** | **0.264903** | **0.229541** |
| **SHIFT (changed regime)** | **0.310739** | **0.288870** |

The model abstained from issuing predictions in five of 30 worlds, for **83.33% issued prediction coverage**: it caught **two of five XOR cases** and **three of five SHIFT cases**. It **missed** the other three out-of-grammar XOR worlds and two shifted worlds. These failure cases remain in [the actual witness dossier](example-probabilistic-witness.json); we did not select only the successful demonstration.

Across all worlds, **2,039 forwarded duplicate witness reports** were recognized rather than counted as independent sources; **365 training trials** lacking independently verified applied controls were withheld from causal learning. These are real counters from this synthetic benchmark, not fabricated examples.

The model's issued thresholded predictions still make mistakes—**943 across the issued cases**—because the realized outcome is stochastic. Even a correct rule can assign an event an 80% chance and still be wrong in that event. This is why Brier and log loss matter more here than demanding 100% individual accuracy.

The Brier score is calculated for all 3,600 outcomes, including abstained cases. The reported "zero outside-world authority" is a software boundary for this prototype, not a verified general safety guarantee.

### An inspectable uncertainty cartridge

[example-probabilistic-witness.json](example-probabilistic-witness.json) contains an actual CI-reproduced, locally generated object with:

- Four **real, checksum-validated MOTIF-009 tree cartridges**.
- Their posterior weights and a separately labeled non-tree OTHER probability mass.
- Verified-correctness Beta posterior means and 90% Monte Carlo intervals for three source origins, including an anti-reliable witness.
- Estimated actuator compliance, withheld unverifiable attempts and deduplicated forwarded witness claims.
- An example of two witnesses actually disagreeing about a synthetic outcome.
- A predicted probability *before* the evaluator reveals an independent synthetic truth.
- Cases where the model recognizes an unknown rule or shift—and cases where it **doesn't**.
- A permitted read-only **synthetic question proposal** plus blocked unsafe/over-budget ones.

A tree cartridge's leaf evidence counts here refer explicitly to **unadjudicated reported witness claims**, **not observed ground-truth outcomes**. The deterministic tree's leaves are hypotheses, not probabilistic outcome truths. The weighted ensemble contains more information than any individual 009 tree and defaults to \`HOLD_PROPOSAL_ONLY\`.

The packet's hash detects changes, **does not verify who authored it**, and cannot grant any real-world power. Proposals do not execute operations.

### What "real uncertain" means in this experiment

This study has genuine **aleatoric uncertainty inside its simulator**: outcomes are Bernoulli draws rather than guaranteed rewrites. It also carries **epistemic uncertainty**: separate uncertain witness reliabilities, compliance rates, and competing hypothesis weights.

But it does **not** have real human witness data. The three reporter identities are local synthetic source keys, not authenticated people. The reliability estimates depend on independent *synthetic adjudications*. There are no externally witnessed facts, physical causality, real-world consent or ability to act. Source correctness, inconsistent accounts, unknown causes and temporal shift may be observationally indistinguishable from limited evidence.

There are additional honest limits:

1. The source-origin metadata is trusted as a synthetic fixture. A malicious participant could misattribute, forge or coordinate origins in a real system.
2. True source reliabilities are constant within each generated world; real reporting standards can drift, depend on topic or be adversarial.
3. The model skips training trials with unaudited applied controls instead of using a more efficient full uncertainty-in-controls likelihood.
4. The estimated 90% predictive interval is conditional and not guaranteed frequentist coverage; reliability uncertainty is not jointly integrated with model weights.
5. The OTHER model is a constant 0.5 reference, **not** an open-world concept learner. Three of five unsupported XOR worlds remain unrecognized.
6. The SHIFT detector misses two of five simulated regime changes and cannot distinguish their underlying causes.
7. The Bayesian comparator's four-cell model is deliberately flexible but not an unrestricted state-of-the-art temporal/hierarchical causal model.

## Reproduce

Python 3.10+, standard library only, no paid API or model downloads:

\`\`\`sh
cd experiments/013
python benchmark.py
python demo.py
python -m unittest -v test_witness.py
\`\`\`

GitHub Actions also runs every MOTIF-001–012 suite. Tests reproduce both saved 013 JSON artifacts **exactly** from the seeded stochastic process, assert that secret outcomes never enter fitting, that correlated forwarded reports are counted once, and that negative results remain visible.

## Next falsifiers

- Implement full hierarchical joint Bayes over uncertain reliability, source dependence, actuation compliance and world model; compare with classical Bayesian gold-standard posterior, not a weaker majority model.
- Learn channel reliability without assuming adjudication is always correct; propagate adjudication uncertainty, custody and source dependence explicitly.
- Freeze held-out **new mechanism families** where probabilities and source reliabilities change over time, and assess prequential (online) Brier, calibration, interval coverage and concept drift detection.
- Measure explicit *selective prediction* risk versus coverage, with comparison to calibrated conformal and Bayesian abstention policies; don't advertise unconditional calibration from a single positive curve.
- Incorporate imperfect intervention compliance into the updating likelihood rather than simply withholding unaudited crossings.
- Keep the latest 009–012 tree cartridges and methods interchangeable, but require strict local ontology compatibility and independently reviewed prediction-only import across worlds.

**Actual finding:** Probabilistic graph evidence is usable without treating every report as truth, every command as an applied action or every model as certain. But a flexible classical Bayesian alternative currently predicts this simulator better overall. MOTIF-013 advances the integration and exposes failures that a deterministic experiment could conceal.
