# GENIUS-005 first heldout results: evidence ≠ automatic accuracy

**Source:** GitHub Actions #42845639907, run on the first frozen protocol at commit 239f02a932678f711f37651f6425b8f797466463. Original plan SHA-256:
be251c6c1d72fd477be9832bbd2c49c5f3132c677f25a3dceba67f6eed438635.

**Status:** First test suite passed (10 tests). All generator worlds are engineer-authored binary streams, not human subjects, externally sourced records, or independent research replications.

Each regime contains 36 streams, of 120 future rounds, with 4,065 public reports scored and 255 withheld (i.e., not learned from and not included in predictions). The CUSUM threshold was validation-selected as **8.0** before testing future seeds 50541–50543.

## Detection results, where a real synthetic change was deliberately inserted

| Scenario | Detector | Correct detections / changed streams | First-alarm false positives (across all streams) | Mean delay from start (rounds) |
| --- | --- | --- | --- | ---: |
| ABRUPT | Exact Fisher/Bonferroni | **36/36** | **0** | 18.19 |
| ABRUPT | CUSUM | 35/36 | 1 | **13.83** |
| ABRUPT | Naive gap | 24/36 | 12 | **4.17** (survivors only) |
| LOCAL | Exact Fisher/Bonferroni | **12/12** | **0** | 17.00 |
| LOCAL | CUSUM | 12/12 | 1 (unchanged stream) | **11.92** |
| LOCAL | Naive gap | 7/12 | 20 (including unchanged streams) | **4.00** (survivors only) |
| GRADUAL | Exact Fisher/Bonferroni | **35/36** | **0** | 39.29 |
| GRADUAL | CUSUM | 35/36 | 1 | **34.94** |
| GRADUAL | Naive gap | 24/36 | 12 | **15.50** (survivors only) |

These are not directly comparable delays for detectors with different missed-detection/early-false-alarm frequencies; fast averages among surviving detections can hide many failures. Gradual drift has no single natural ground-truth instant; 40 denotes its engineer-defined beginning.

## False alarms when nothing actually changed

| Detector | STABLE (36 streams) | NOISY_STABLE (36 streams) | Combined |
| --- | ---: | ---: | ---: |
| **Exact Fisher/Bonferroni** | **0/36** | **1/36** | **1/72 (1.39%)** |
| Classical tuned CUSUM | 0/36 | 4/36 | 4/72 (5.56%) |
| Naive rolling gap | 25/36 | 35/36 | 60/72 (83.33%) |

The exact method controlled apparent changes on these finite synthetic examples far better than the naive threshold. Its *formal* <=5% family-wise false-alarm bound is **per stream under stationary IID Bernoulli observations and a predetermined checkpoint schedule**. The measured 1/72 is not proof that the empirical risk is always 1.39%, nor evidence that the bound applies to human behavior.

## Does this actually produce better predictions?

Not necessarily. All methods made a prediction before receiving each public future label.

| Regime | EXACT_SWITCH costed Brier | Best conventional online predictor | Best Brier |
| --- | ---: | --- | ---: |
| STABLE | 0.147652 | CUMULATIVE (tie) | **0.147652** |
| NOISY_STABLE | 0.253160 | CUMULATIVE | **0.252771** |
| ABRUPT | 0.198864 | HEDGE | **0.168102** |
| LOCAL | 0.165508 | HEDGE | **0.156097** |
| GRADUAL | 0.212417 | HEDGE | **0.192791** |

**Crucial negative result:** Being more careful about declaring structural changes did not turn the simple conditional switch into the strongest forecaster. Strong classical online averaging remained more accurate in changed worlds.

The demonstrable outcome is a safer *diagnostic evidence certificate* on narrowly controlled streams, not an improvement in general predictive intelligence.

## Evidence-carrying adapter added afterward

Following the first heldout measurements, a standalone preview module **evidence_gate.py** was added. It creates a conditional, source-owned receipt: reference evidence IDs, exact p-value and threshold at first alarm, fixed comparison windows, no raw private notes, and a next useful question. Its dispositions include:

- PROPOSE_REVISION_CONDITIONALLY: evidence against the stationary IID null, **not** authority to change a real-world state or speak on behalf of another person.
- RETAIN_PROVISIONALLY_NO_REJECTED_NULL: insufficient evidence to reject a fixed null is **not proof of no change**.
- HOLD_NOT_ENOUGH_MONITORING, HOLD_UNVERIFIED_SAMPLING_PLAN, HOLD_DUPLICATE_FUTURE_EVIDENCE, HOLD_FOREIGN_SOURCE and other refusal cases.

This interface is added **after inspecting the original benchmark**; it was not an originally frozen benchmark arm and may not be presented as though it independently won the old holdouts. It is a local experimental interface only, not a live Trench device or MCP service. The sampling-plan attestation is a claim made by the caller, not cryptographically verified authorization or scientific proof.

## Next meaningful question

Can a truthful, exact change-evidence packet help a planner choose **better subsequent research questions and externally verified actions**, instead of merely producing more labels for when it thinks a model should change? Compare with an identical evidence and compute budget classical planner. Use independently authored, blinded and non-IID challenge families before claiming transfer.
