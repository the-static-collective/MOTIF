# REALITY-017: First sealed flood replay and the failed caution hypothesis

**Experiment executed November 5, 2026.** Public June 2024 flood observations, with a previously frozen model-selection and routing plan. This is a retrospective event replay, **not an actual 2024 issued prediction**.

## Predeclared questions

MOTIF-016 found that a three-gauge linear model won the early validation window but subsequently lost to persistence in its October 2026 low-flow holdout. Does a newly proposed conservative policy—requiring stable pre-event advantage and reverting to persistence outside its training flow range—help on a documented, genuinely different historical water regime?

**Real public-source event:** NOAA/NWS documented record flooding in June 2024 (https://www.weather.gov/mpx/RecordFloodingJune2024). USGS confirmed the Rapidan dam episode disrupted streamgage power on June 24, 2024 (https://water.usgs.gov/alerts/item_2024-06-24_17%3A20%3A54.html). The latter is a major *source-availability limitation*, not an inferred cause of all missing observations.

## Evidence timeline

1. PREPARE: Read only earlier training (May 4–13, 2023) and validation (June 1–10, 2024) records for three named USGS stations. Fit ridge models on train data; select two frozen rival policies using validation data. **No June 18–28 flood source was fetched during preparation.**
2. SEAL: The selected old and cautious policies were both `cross_gauges`; the cautious policy added an origin-only out-of-training-range fallback to persistence. SHA-256 of pre-event plan: `196fa6be6703c5470b017d3db0ab4da6e5ffb3a4dd74abbe4a098e53c610750a`.
3. EVALUATE: Only afterward fetched June 18–28, 2024 flood records. Scored identical complete-case measurement hours with all three options.
4. DIAGNOSE: A second, fallible meta-diagnostic compared this event with the previous October 2026 low-flow witness and generated three HELD lessons and proposed next tests. No weights or rules were automatically promoted.

[Actual source-backed workflow, tests, source response artifact](https://github.com/the-static-collective/MOTIF/actions/runs/42034382151). The run artifact contains the complete raw public USGS JSON responses plus frozen plan and event result, retained for 30 days. The selected source report and fallible lesson card are committed as `evidence/first-real-event-2026-11-05.json` and `evidence/first-lessons-2026-11-05.json`.

## Actual scored results — NOT generalized model performance

| Frozen test policy | Mean absolute discharge error |
|---|---:|
| Previous validation winner (cross-gauge fit) | **1,293.0220 cfs** |
| Newly proposed origin-aware conservative fallback | **1,966.8894 cfs** |
| Persistence baseline (last previously completed downstream hour) | 2,027.3504 cfs |

**The cautious proposal LOST by 673.8674 cfs against the unchanged selected model on this historical event subset.** It fell back to persistence for **74** of the 117 scored hours. The unchanged cross-gauge model also beat raw persistence by 734.3284 cfs *on these same test hours*. This does not prove general cross-gauge superiority across other seasons or flows.

**Coverage was only 117/264 = 44.32% of calendar hours**. Only observations jointly available at all three gauges were scored. There were 32 qualifying rising-flow observations *within that selective complete-case subset*. Because the source set is incomplete, the research disposition was `HOLD_INSUFFICIENT_EVENT_COVERAGE`, not 'the new method works' or 'the old method is globally better'.

## What the machine actually learned to ask

It did **not learn a better weather or hydrology model**. Its source-owned metadiagnostic extracted three falsifiable research constraints:

**L-001: No universal complexity hierarchy.** In the October 2026 low-flow slice, persistence beat the cross-gauge strategy. In this June 2024 event's available measured hours, cross-gauge beat persistence. River conditions and evaluation populations differ, so a model's complexity alone cannot rank its value.

**L-002: Caution itself has a cost.** A method called 'conservative' can destroy useful signal. The 74 origin-only fallback decisions were part of the new proposal; on the available event cases, total error grew. That is not a universal argument against cautious operation; it is evidence against this particular fallback policy on this sample.

**L-003: A diagnostic that only sees functioning sensors may be measuring selection bias.** Nearly 56% of possible hours lacked complete observations across all three sites. Missingness and changed reporting practices may alter the conclusions. The diagnostic must be able to find its own blind spot.

The diagnostic explicitly challenges itself:

> Is the current test measuring model skill or simply selecting the hours when broken sensors happened to report?

## The strongest next experiment

**Freeze these policies again, intact, and test a genuinely different not-yet-scored river event**, with independently archived input-availability evidence and proper accounting for hours with missing gauges. No changing the rules after examining the event outcome. Evaluate *both* prediction loss and the cost of abstaining.

A further quality improvement is to score the downstream gauge even when upstream gauges are absent, reporting both (a) baseline coverage over all downstream hours and (b) paired model coverage. Compare accuracy on the common support separately from *actionable opportunity lost* to source outages. This addition is a proposal for a new experiment, not a retroactive recomputation of 017.

**No automatic code promotion, flood warnings, human dispatch, claim of independent sensor authentication, or operational river forecast.**
