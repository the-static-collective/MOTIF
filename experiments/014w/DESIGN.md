# MOTIF-014W — THE WITNESS OF WITNESSES
## When the credibility of an adjudicator is itself uncertain

**Parallel branch note:** A separate active MOTIF-014 **Organ Gardener** experiment occupies `experiments/014` in another branch. This independent probabilistic-witness research is therefore isolated under `experiments/014w` to avoid overwriting that work. Its internal synthetic experiment identifier remains `MOTIF-014` from the original experiment protocol; the repository index calls this research **014W**.

**Question:** If an apparent independent auditor can be wrong, and a report that an intervention occurred can also be wrong, can MOTIF propagate uncertainty about *those witnesses of evidence* through the causal-model hypotheses instead of mistaking adjudications for ground truth?

**Implemented:** **Exact Bayesian enumeration on a small, explicitly specified discrete parameter grid**, using observed synthetic graph-state requests, stochastic upstream claims, meta-auditor reports, and a noise- and compliance-aware likelihood. The experiment uses *classical Bayesian inference*, not a newly invented algorithm or actual authenticated evidence.

**Important:** This remains entirely **seeded simulated testimony** with made-up control settings. There is no external network, physical experimentation, verified reviewer identity, proven reliable auditor, trained neural network, or permission for an outside-world action.

## 1. The recursive evidence problem

MOTIF-013 estimated witness reliability using a separate batch of **adjudicated reports**, implicitly treating the adjudicator's verdict as ground truth. It then substituted posterior-mean witness and actuator reliabilities into a tree-model posterior.

That architecture has a gap:

> What if the person or instrument determining whether a witness was correct is itself unreliable?

MOTIF-014 does not answer this by declaring another referee infallible.

Instead it represents:

\`\`\`text
                          UNSEEN CALIBRATION TRUTH
                                 /          |        \
                                /           |         \
                 WITNESS A says X   WITNESS B says Y   AUDITOR says Z
                       |                  |                 |
                  UNKNOWN r0         UNKNOWN r1        UNKNOWN q
                       \                  |                 /
                        \                 |                /
                         JOINT POSTERIOR, NONE IS GOLD TRUTH
                                       |
                     +-----------------+------------------+
                     |                                    |
           REQUESTED CONTROL                         OUTCOME CLAIMS
                     |                                    |
              UNKNOWN COMPLIANCE c                 WITNESS A / B
                     |                                    |
             UNOBSERVED APPLIED SETTING ---- UNKNOWN ACTUAL OUTCOME
                     |                        |
             FALLIBLE AUDITOR REPORT ---------+
                     |
                    MODEL H   FOUR 009 DECISION TREES + OTHER
                     |
                     +--------- FORECAST --------------+
                                |
                     PROBABILITY + EPISTEMIC RANGE
                                |
                    INDEPENDENT VALIDATION WARNING
                                |
                      PREDICT OR HOLD PROPOSAL
\`\`\`

Neither the calibration event's **actual outcome** nor the training intervention's **actually applied control** is passed to the learner. The hidden data exists on the evaluator side solely for constructing synthetic data and testing forecasts. The learner sees public attributed claims, a fallible audit claim, the requested action, and a role-relative graph of the **requested** settings—not the actual applied settings.

Forwarded reports retain the original source key and are counted once. Contradictory reports claiming the same upstream origin cause HOLD. Missing auditor reports are **marginalized**, not discarded and not reclassified as verified applied controls.

### The synthetic world is deliberately imperfect

[oracle.py](oracle.py) uses separate deterministic random seeds to sample **genuine Bernoulli variation inside each generated world**. The hidden source correctness probabilities are drawn approximately as:
- upstream source 0: **0.84–0.94**
- upstream source 1: **0.17–0.33**, systematically more often wrong than right
- meta-auditor: **0.75–0.90** on the training regime
- actuator compliance: **0.72–0.90** on the training regime

The audit channel performs two kinds of testimony: it estimates the outcome of *calibration events* and attests whether the **first of two commanded ports** was actually applied. We deliberately assume the *same* quality parameter for those two kinds of attestation. That is an experimental modeling assumption, not a proven fact about real witnesses.

Some calibration and intervention reports are missing, and source 0's original report may be forwarded verbatim. All values are programmable synthetic fixtures, not estimates of real people's honesty.

The resulting world families are \`FIRST\`, \`SECOND\`, \`AND\`, \`XOR\` (an outcome mechanism unavailable in MOTIF's four named trees), \`SOURCE_SHIFT\` (source 0 changes from reliable to below chance), \`AUDIT_SHIFT\` (auditor falls to 28% correctness), and \`COMPLIANCE_SHIFT\` (first actuator compliance drops to 28%). The changes take effect **after training**, during validation/test. These are hard-coded distribution shifts, not emergent novel physics.

## 2. Exact joint Bayes, with an important qualifier

The posterior explicitly ranges over:

\`P(H, r0, r1, q, c | calibration reports, intervention reports)\`

where:
- \`H\` is the causal-tree hypothesis,
- \`r0, r1\` are independent upstream source correctness rates,
- \`q\` is **meta-auditor correctness**,
- \`c\` is **actuator compliance**.

For calibration reports, the learner sums over *both possible hidden truths*. For training interventions, it also sums over *both possible applied first-port settings* and the *unobserved Bernoulli outcome*:

\`\`\`text
P(source0, source1, audit | requested, H, r0, r1, q, c)
   = sum_applied P(applied | requested, c)
       P(audit | applied, q)
       sum_outcome P(outcome | applied, H)
           P(source0 | outcome, r0)
           P(source1 | outcome, r1)
\`\`\`

Absent source/audit claims simply contribute likelihood 1 for the missing channel. This is **not** a rule that says missing evidence never matters; it is an assumption that missingness is ignorable for this carefully created simulator. Real selection bias and malicious withholding are unmodeled.

The full posterior is evaluated over **960 discrete combinations for the MOTIF tree family**, as specified in [joint.py](joint.py):

- \`r0, r1\` grids: \`{.20, .45, .70, .90}\`
- \`q\` grid: \`{.58, .72, .84, .95}\`
- \`c\` grid: \`{.55, .76, .92}\`
- tree hypotheses: \`FIRST, SECOND, AND, OR, OTHER\`.

The \`OTHER\` hypothesis has a fixed 50% success probability, not a learned arbitrary cause. Every named model uses prescribed 12%/88% conditional outcome probabilities. The prior favors an above-chance auditor, and the source-0 prior favors a reliable reporter. **This prior orientation helps resolve an otherwise non-identifiable truth-label symmetry.** The system does not independently establish truth merely because sources agree with one another.

**"Exact" means exact posterior weights on these 960 handcrafted discrete states—not exact inference over unrestricted real-valued reliability, unknown source dependence, arbitrary graph mechanisms or physical reality.** Likewise, the interval reported for an event's *success probability* is a finite-grid epistemic posterior interval, not a frequentist 90% guarantee that future individual Bernoulli outcomes lie in it.

### Decision-tree cartridges really participate

The ensemble bundles **four actual MOTIF-009 two-question decision-tree cartridges**, each exported and structurally validated using the existing 009 schema. They represent different hypothetical Boolean transformation programs. The fifth OTHER probability mass is retained separately, never forged as a deterministic tree.

The upstream leaf counts in this 009-compatible package are explicitly labeled **unadjudicated source-reported outcomes at requested control settings**. They must **not** be interpreted as verified truths or actual applied-control counts. The joint Bayesian model, not 009's uncalibrated leaf proportions, supplies the probabilistic forecast.

The whole ensemble defaults to \`HOLD_PROPOSAL_ONLY\`. Content checksums can detect modifications, **not prove who created the artifact or whether the reports were real**.

## 3. A stronger classical comparison

The independent [benchmark.py](benchmark.py) evaluates two implementations of the same classical Bayesian latent-witness calculus on **identical public data**, including uncertain auditor and applied-control reports:

| Approach | Hypothesis grammar | Number of finite grid states |
|---|---|---:|
| MOTIF-014 joint Bayesian decision-tree ensemble | FIRST, SECOND, AND, OR + OTHER | 960 |
| Classical full-Boolean joint Bayes | **All 16 possible two-input Boolean tables + OTHER** | 3,264 |

Both integrate witness, auditor, actuator and hypothesis uncertainty over their finite grids. Both receive identical training source claims, audit statements and commanded actions, with the same likelihood and priors over reliability/compliance. The classical baseline has a **broader model grammar**; its prior spreads the same named-model mass over all 16 tables. That extra flexibility is part of the comparison and is reported rather than hidden.

Also reported is a **privileged true-simulator oracle** (not attainable by the learner) that knows the hidden generating mechanism and actual regime parameters. It is only a reference for scoring.

### The frozen synthetic benchmark

- **7 mechanism families × 4 deterministic seeds = 28 worlds**
- **40 fallible-auditor calibration cases, 48 training interventions, 24 independent validation interventions, 96 held-out probabilistic test outcomes per world**.
- All **2,688** held-out outcomes receive forecasts for scoring, **including withheld/abstained predictions**.
- No calibration case's actual outcome is ever passed into inference.
- No training/test trial's actual applied first-port setting or true outcome enters the learner.
- Brier score and log loss use the held-out true Bernoulli outcomes; five fixed forecast bins report empirical calibration.
- The warning threshold \`log_evidence_ratio_vs_ignorance < -4.5\` on an independent validation batch is a **development heuristic**, not a calibrated drift significance test.

### What actually happened

Results recorded directly from the successful GitHub Actions run:

| Mean held-out score across 2,688 outcomes | MOTIF four-tree joint Bayes | Classical 16-tree joint Bayes |
|---|---:|---:|
| **Brier score ↓** | **0.202442** | **0.197640** |
| **Log loss ↓** | **0.592631** | **0.581080** |

Privileged simulator-oracle Brier: **0.175628**.

**The broader classical Bayesian model wins overall**. The four-tree MOTIF grammar performs well on several familiar mechanisms, but is confidently too restrictive for XOR and can suffer badly when compliance changes. This is a negative result for claiming architectural superiority—not for the value of representing recursive uncertainty.

| World family | MOTIF Brier ↓ | Full-Boolean Bayes Brier ↓ | Validation shift warnings |
|---|---:|---:|---:|
| FIRST | 0.180801 | 0.194728 | 0/4 |
| SECOND | 0.111395 | 0.111549 | 0/4 |
| AND | 0.160785 | 0.177203 | 0/4 |
| XOR (outside MOTIF grammar) | **0.266846** | **0.216514** | 0/4 |
| SOURCE_SHIFT | 0.198439 | 0.203818 | **2/4** |
| AUDIT_SHIFT | 0.189581 | 0.190022 | **3/4** |
| COMPLIANCE_SHIFT | **0.309248** | **0.289648** | **1/4** |

The failure is instructive: the system can estimate q for the *old* auditor regime but often cannot tell that q or compliance has changed. This means **well-calculated posterior probability can still become miscalibrated under distribution shift**. It can detect some out-of-regime evidence but does not recover a changed auditor's new reliability from thin air.

### A second negative result: credibility intervals do not cover true reliability

We also evaluated whether the reported **nominal 90% finite-grid parameter intervals** actually contain the simulator's hidden, continuous reliability parameters. These results were calculated directly from all 28 archived world receipts, **without refitting or looking at test truths during training**:

| Source parameter | Worlds where interval contains hidden training parameter | Empirical coverage | Intervals collapsed to one grid point |
|---|---:|---:|---:|
| Upstream source 0 reliability `r0` | **10/28** | **35.71%** | **14/28** |
| Upstream source 1 reliability `r1` | **7/28** | **25.00%** | **21/28** |
| Fallible auditor reliability `q` | **27/28** | **96.43%** | 0/28 |
| Actuator compliance `c` | **24/28** | **85.71%** | 0/28 |

**This is a serious failure of the source-reliability uncertainty representation.** For example, the model only permits source 0 rates of `.20, .45, .70, .90` even though the simulator can generate values *above* `.90`. A concentrated discrete posterior can therefore exclude the true continuous parameter **by construction**. In the example cartridge, source 0's interval is `[.90,.90]` while its hidden training reliability is `.841`; source 1's interval is `[.20,.20]` while its hidden reliability is `.2606`.

These numbers **must not** be advertised as externally calibrated 90% intervals. This is a falsifier for the next generation: use denser/continuous priors and measure coverage under *independently generated, out-of-grid truths*, not just whether a posterior interval is narrow. The q and c figures also come from only 28 related synthetic worlds, not a validation of real-world coverage.

The experiment's heuristic prediction gate issues probabilities on **57.14%** of held-out cases and holds the rest. It still makes **362 wrong thresholded decisions** among those issued because actual outcomes are stochastic. We do not hide the internal probability scores for abstained cases: all contribute to Brier and log loss.

The code deduplicated **1,359 forwarded copies** and *integrated rather than discarded* **279 missing auditor control-attestation reports**. These are measured toy counters, not operational business telemetry.

## 4. A question that measures its own evidence

[propose_inquiry](joint.py) chooses between two categories of **synthetic, not executed** questions:

- \`CALIBRATION\`: ask for additional reports about an *unseen calibration truth* to learn source and auditor credibility.
- \`INTERVENTION\`: propose a two-port synthetic intervention intended to distinguish causal and compliance hypotheses.

It estimates classical **mutual information over the full joint state** \`(H,r0,r1,q,c)\`, not merely agreement among trees. It assumes all three reporting channels respond to the hypothetical next inquiry, an intentionally optimistic assumption that is separately marked.

Every proposal is evaluated against **explicit permitted inquiry types and positive integer costs** before selection, returning \`HOLD_UNSAFE\` or \`HOLD_BUDGET\` when appropriate. A proposal never dispatches a real actuator.

Thus a scientific instrument can explicitly ask whether the better next step is *to test the world* or *to test the reliability of the evidence being used to interpret it*.

This is classical Bayesian optimal experimental design on a toy model, not proof of independent consciousness or general epistemic intelligence.

## 5. Literal witness-of-witnesses cartridge

[example-joint-credibility.json](example-joint-credibility.json) is generated by the GitHub Actions experiment itself. It includes:

- A **real, portable set of 009 decision-tree cartridges** with joint Bayesian marginal weights and explicit OTHER mass;
- Actual synthetic reports from conflicting upstream witnesses and a fallible meta-auditor;
- Posterior **discrete 90% intervals** for both reporters, the auditor, and intervention compliance;
- An actual probability forecast made before the test outcome is exposed to the evaluator;
- A budgeted synthetic inquiry about calibration versus intervention;
- A **held unsafe question** and an **unaffordable question**;
- Separate successful and missed cases of source drift, auditor drift, and compliance drift.

It is deliberately an inspectable scientific receipt rather than a web application. No live JAR;VIS integration or external action is claimed.

## 6. Reproduce

Python 3.10+, standard library, no paid API:

\`\`\`sh
cd experiments/014w
python benchmark.py
python demo.py
python -m unittest -v test_joint.py
\`\`\`

The CI suite also executes MOTIF-001–013. The 014 tests assert exact reproduction of checked-in result/cartridge files, source-truth separation, checksum-validated 009 tree components, duplicate-source suppression, rejection of internally contradictory testimony, real stochastic outcomes, fallible auditor reports, noncompliance marginalization, all 16 classical Boolean alternatives, and safe proposal holds.

## 7. What must actually become harder

1. **Identifiability:** Agreement between fallible observers cannot produce absolute ground truth without anchoring assumptions, external calibration or verifiable interventions. Test alternative priors and adversarial mixtures; quantify sensitivity of inferred truth to prior trust in the auditor.
2. **Temporal reliability:** Treat q, c and source credibilities as time-varying state rather than constant parameters; use online filtering and prequential calibration instead of one posterior frozen at training.
3. **Correlated sources:** Model collusion, evidence copying with falsified provenance, source dependence and source-of-source chains; source IDs are currently synthetic labels with no authentication.
4. **Genuine partial intervention compliance:** Model unobserved confounders and failures of both actuators, not just the first; compare intention-to-treat and per-protocol causal claims in separately held-out domains.
5. **More flexible scientific hypotheses:** Evaluate more than two controls, continuous outcomes, effect-size uncertainty and new structural relation discovery; the 16-table baseline already reveals the cost of restricting the hypothesis grammar.
6. **Calibration of abstention:** Benchmark selective risk/coverage and false-warning rates against calibrated Bayesian and conformal baselines with a fixed protocol.
7. **Practical provenance architecture:** Any integration into reLATTE or JAR;VIS must require real source custody, signed claims where appropriate, explicit local human review, and strong boundaries between recommendations and permissions.

**The actual demonstrated principle:** Treating the auditor as another uncertain witness is mathematically workable. But this does not establish who speaks truth; model assumptions, priors and new regimes remain consequential. A stronger classical Bayesian model still predicts the synthetic test outcomes better overall.
