# MOTIF-015 — first real-world witness (2026-11-05)

**Source:** [GitHub Actions live read-only run 42028055188](https://github.com/the-static-collective/MOTIF/actions/runs/42028055188), job `real-station-witness`, at approximately 2026-11-05T12:33:07Z.

**What crossed:** Open-Meteo previous-day1 archived 24-hour weather forecast for the fixed Mankato public research point (44.22, -93.92) was checked against timestamped NWS KMKT station sensor reports. This was a genuine network-backed evaluation on publicly reported weather data, not synthetic observations. The underlying sources are independent *products*, but are **not established to be statistically independent** or perfectly accurate.

## Observed result

| Held-out measure | Measured value |
| --- | ---: |
| Matched hourly forecast/sensor pairs | 88 |
| Earlier chronological training records | 58 |
| Later held-out test records | 30 |
| First / last forecast valid hour (UTC) | 2026-11-01 15:00 / 2026-11-05 06:00 |
| Mean bias fitted on the earlier 58 records | +0.0190 °C |
| Unadjusted archived forecast MAE, test | **1.6000 °C** |
| Bias-adjusted forecast MAE, test | **1.6126 °C** |
| Train-only constant baseline MAE, test | 6.5692 °C |
| Raw minus adjusted MAE | **−0.0126 °C** |
| Below-freezing test cases | 0 |
| Independent human/field decisions performed | 0 |

**Disposition: `HOLD_NO_MEASURED_IMPROVEMENT`.** The attempted bias correction did not help on this test. The unmodified forecast is slightly better on this slice. This is important: the research apparatus returned a negative result rather than flattering the new model. No rules, forecasts or decision-maker actions were altered.

The zero below-freezing test events mean we **cannot** claim any evidence about freezing-alert false negatives from this run, despite numeric zero miss counters.

## Source receipts

- Open-Meteo response's canonical JSON SHA-256: `ae72ee53a82dbc6348a39ca149cdf3c103ff0c5033cb7aab22fdf3f3e21c0dc5`
- NWS station response's canonical JSON SHA-256: `55f7d57aff749ce53f8880d5b4223d73ec3ef24c04df4bc74cdf849aa89971c2`
- JSON result artifact: [reality-iron-015-mankato-public-weather](https://github.com/the-static-collective/MOTIF/actions/runs/42028055188/artifacts/13414448263) (workflow retention: 14 days).

The source responses themselves are **not included** in that artifact; the hashes preserve their identity if later independently captured, not their bytes or verifiability. Provider archives and station reports can be revised.

## Why the modest result matters

This is a calibration of **our research discipline**, not evidence of MOTIF's higher intelligence. The instrument evaluates an ordinary bias-adjustment hypothesis; its next task is to use *existing MOTIF and JAR;VIS methods* to propose alternatives, then compare those alternatives against independent, held-out human-relevant decisions. No recursive improvement was demonstrated in this run.

The first live attempt was honestly held on a large NWS GeoJSON response. A bounded response-limit adjustment on the branch let the subsequent read-only run complete. Offline synthetic tests are separate and passed.

## Licenses, methods and limits

Open-Meteo Previous Runs: https://open-meteo.com/en/docs/previous-runs-api ; noncommercial API and CC BY 4.0 attribution: https://open-meteo.com/en/terms. NOAA NWS station API: https://www.weather.gov/documentation/services-web-api. The sensor measures near an airport; the archived gridded forecast is not necessarily at exactly the same elevation or sensor location. The test uses a short, retrospective dataset and an adaptive model-provider "Best Match", so neither forecast model stability nor operational issue-time reconstruction is independently proven.
