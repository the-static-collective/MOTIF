# MOTIF-019 / The question that asks whether another question has an answer

## Research question

**When a sensor is sometimes unavailable, is it worth paying for a cheap source-health question before paying for the measurement itself?**

This question was generated after MOTIF-018 found a puzzling contradiction in real September 2025 USGS streamflow: its frozen preferred additional sensor was Le Sueur, but an unselected two-sensor policy appeared better on *already-opened* 2025 test data even with Blue Earth missing for 81 of 228 cases. Those test labels may inform **design of a new independent question**, but they may **not** be reused as a sealed holdout to select the new policy.

## Fixed data periods (before first 2026 March test read)

- **Fit basic hydrology:** 2023-05-04–13 (three public river stations).
- **Iteratively develop question-choice policy:** 2025-09-12–22 (previously inspected in MOTIF-018; now development data).
- **Unopened physical challenge:** 2026-03-01–14. Source dates pinned in code before test. No 2026 March records used in selection.

Stations: Minnesota River Mankato `USGS-05325000` (target), Blue Earth `USGS-05320000`, Le Sueur `USGS-05320500` (potential additional information). Data: USGS modern OGC Continuous `00060` streamflow (cubic feet/second).

## Question grammar and genuine alternatives

Seven policies compete, all evaluating **the same downstream target hours**, whether optional sensor readings are missing or not:

- **downstream**: use the last known Mankato flow (persistence; zero added source questions).
- **sueur_only**: query Le Sueur; fall back to downstream if unavailable.
- **both_graceful**: request Blue Earth and Le Sueur; if either fails, *use the available other source*; if both fail, downstream. This strong comparator prevents a fake health-probe benefit over an arbitrarily weak fallback.
- **trend_gate_2pct**: query Le Sueur and request Blue Earth only when the origin-known six-hour Mankato change exceeds 2% of origin-known flow.
- **health_last1 / health_last3 / health_last6**: pay **a cheap probe cost** every time, then request Le Sueur and Blue Earth only when the *historical presence of earlier timestamp records* suggests Blue Earth can answer. Their thresholds are hardcoded before test.

**Hard limitation:** Historical timestamp presence from a 2026 query does not prove that the observation would actually have arrived by the historical prediction issuance time. This is a test of **source-timestamp completeness as an availability proxy**, NOT a deployed or independently validated live station-health service. No actual health ping was made at historical issuance time.

At each target hour `t`, predictions use only river timestamps at `t-7h` and earlier; health proxies look backward 1–6h from that origin. Errors compare to target observations after this hypothetical lead. Reporting delays and USGS discharge rating revisions are unknown. No river warnings, flood control, safety claims, or alerts.

## Executable self-question revisions

The development phase runs **six bounded revisions of its own JSON decision rubric**. The alternatives and questions remain fixed; the scoring rubric changes:

| Iteration | Concept introduced |
|---|---|
| Q0 | Does measuring more improve error when asking is free? |
| Q1 | Each source question has a research credit price. |
| Q2 | Missing answers receive an additional penalty. |
| Q3 | Asking conditionally plus development time instability. |
| Q4 | New question *kind*: check whether the sensor has been reporting recently. |
| Q5 | New meta-penalty: health probes can falsely promise availability. |

Policy selection in each stage uses only 2025 development observations, deterministic tie-breaking and all-candidate score ledgers. It may stay constant across revisions, change several times, or select the zero-query baseline. **These are criterion revisions, not changed Python source code or autonomous invention of new executable functions.**

Fit ridge regression only on 2023 training records with complete features for each model: `sueur`, `blue`, `both`. At test time, missing optional features lead to the best available corresponding pre-fit model, not dropping the target observation. Missing responses incur research costs. All candidate methods pay a consistent cost according to the rubric and expose per-hour model-use counts.

**Proxy costs:** one source question = 8% of 2023 training persistence MAE, converted to cfs-equivalent utility; a health question costs 0.2 source credits; unanswered source queries incur 2 extra credits, stale-positive health probes 1 extra, and development half-to-half error instability incurs a 20% penalty. These are hypothetical experiment weights, not calibrated economic, safety or hydrologic valuations. Benefit and costs are reported separately.

## Run it

From repository root (Python 3.10+ standard library only):

```sh
python3 -m unittest discover -s experiments/019 -p 'test_*.py' -v
python3 experiments/019/availability_question.py evolve --out-dir /tmp/motif-019
# inspect SHA-256 frozen plan, and verify there is no holdout data
python3 experiments/019/availability_question.py confront --out-dir /tmp/motif-019
```

The GitHub Actions workflow enforces stages and preserves **all three raw API response sets**, the sealed plan, and test output as a downloadable temporary run artifact (30 days), available after the run. Re-run the exact snapshots offline using `--offline`; do **not** silently re-label new API snapshots as original.

## What constitutes learning?

The program can operationally refine the category of question it asks, test value of a new question type against stronger direct-query baselines, and produce a testable question from the resulting contradiction. A new candidate only becomes *held for independent replication* if it improves both heldout raw MAE and the predeclared research utility vs downstream persistence, with sufficiently few unanswered queries.

If a question wins on already-opened test labels but wasn't the frozen selected policy, it remains **POSTHOC / NOT ADMITTED** and can only motivate research in a different untouched window. A source health proxy can improve cost without improving prediction, or improve predictions without offsetting cost; either is informative.

**No autonomous code editing, trained language model, flood prediction service, real sensors queried in 2026 March at issue time, model promotion, or external effects.**

Main source: https://api.waterdata.usgs.gov/docs/ogcapi/migration/ .

## The meta-question: maybe the cost function, not the sensor, was wrong

On the first USGS March 2026 replay, the evolved question policy selected **no extra source query**, after Q1 introduced our invented research credit price. Among 300 downstream targets, Blue Earth was usable in only 35 origin-time histories, Le Sueur in 116. The zero-query method had MAE **185.3333 cfs**, whereas querying Le Sueur produced **155.8044 cfs** raw error and the historical health-probe policy **150.4962 cfs** raw error on exactly the same 300 hours. Despite this, the assumed, uncalibrated query/missing-answer prices made the zero-query policy win the **declared weighted objective**.

**This is not evidence that asking is genuinely too expensive in the real world.** The system can now inspect *its own arbitrary value function*. The post-test diagnostic explicitly calculates, for each policy, the maximum **hypothetical research credit price** at which it would beat downstream persistence under the same time-stability weighting, while keeping the original sealed decision and raw metrics unchanged. The output is `self_diagnostic_on_assumed_cost_of_questions`, strictly **posthoc; not admitted**.

The resulting new question is about **measuring actual question cost**, not another pretense of smarter source selection. A legitimate future experiment would log true source request timestamps, delays, availability at issue time, model error and the measurable cost of indecision across real user tasks. This cannot be reconstructed fully from retrospective water-data snapshots.
