# MOTIF-016 / THE LIVING WATERSHED

**Experimental stage:** environmental reasoning has physical-world constraints. No public flood alerts, deployment, operational weather services, agent capabilities, or autonomous self-improvement.

## Physical topology we deliberately do *not* assert as a perfect equation

Real USGS continuous sensors:
- Blue Earth River near Rapidan: `USGS-05320000`
- Le Sueur River near Rapidan: `USGS-05320500`
- Minnesota River at Mankato: `USGS-05325000`

These are *associated with* the southern Minnesota hydrologic area, but **downstream Mankato includes many other flows**; no data-only correlation proves upstream causality. Same agency, distinct sensor locations. The source is the **modernized** USGS OGC `continuous` endpoint, *not the legacy WaterServices scheduled for retirement* (https://api.waterdata.usgs.gov/docs/ogcapi/migration/). Each exact public site code is checked against returned data. Streamflow is in cubic feet per second, parameter `00060`.

Optional environmental context: hourly **Open-Meteo historical gridded precipitation estimates**, not a rain-gauge observation. Used only as a candidate feature in a retrospective benchmark; it may not have been available at the prediction origin. No false claim that a precipitation estimate was physically observed at a sensor.

## The real question

At least six hours before the end of an hourly observation window, can we estimate future Mankato river discharge better than simple persistence?

Compare FOUR predeclared strategies:
1. **Persistence**: last completed Mankato hour; no fit or tuning.
2. **Local trend**: Mankato's previous six-hour change.
3. **Cross gauge**: local trend plus changes in Blue Earth and Le Sueur.
4. **Rain context**: the above plus historical gridded rain in the previous six hours (only when supplied completely).

This is intentionally *classical* reasoning as the hurdle for MOTIF/JAR;VIS. The cross-gauge model uses standard ridge regression (no model weights outside this short experiment). No claim MOTIF invented, learned or autonomously chose any improvement.

## Time discipline

At target hour `t`, available sensor features are computed from hours `t-7` and earlier. The complete last-known hourly window ends before any hypothetical six-hour prediction lead; actual report transmission latency is **not** modeled. A chronological 55% training / 20% validation / 25% sealed test split prevents fitting on the test labels. Selection uses validation *only*. Every candidate's test score is shown. No best-on-test rewriting.

Minimum 78 complete joined hours or HOLD. Partial or conflicting sensor reports, wrong units, paging, bad UTC, and missing archives HOLD or suppress a missing auxiliary weather lane. The evaluation explicitly distinguishes:
- sensor measurements or derived flow estimates
- gridded historical precipitation estimate
- hypothetical earlier information
- held-out retrospective evaluation outcome
- human authorization, which is always absent.

Metric: mean absolute discharge error (cubic feet/second) and rising-flow subset error. **No flood-stage labels, flood alert calibrations, evacuation decisions or actions.**

## Hard new frontier: the diagnostic can lose

The experiment may select persistence. It may select a method that wins on validation but loses on test. It may see no flow-rise episodes. All are legitimate negative results; **no automatic promotion**.

For a worthwhile `HELD_FOR_NEW_PERIOD_REPLICATION`, the selected alternative must improve on test by at least 10% relative to persistence *and* see at least three test rises. Even so, seasonal and multi-event replication, sensitivity to missingness, freeze-era vs rain-era tests, report-availability review and independent evaluator checks are necessary. Avoid the trap that merely having more possible next steps makes something better.

The `motif.reality-iron-watershed/v1` JSON result contains explicit source-response hashes, validation-based choice, train/validation/test counts, model scores, source types, disconfirming notes, and a `self_diagnostic` about blind spots. Both peers can inspect it as an inert, read-only improvement cartridge candidate after source validation.

## Reproduction (Python 3.10+ stdlib)

```sh
python3 -m unittest discover -s experiments/016 -p "test_watershed.py" -v
python3 experiments/016/watershed.py --live --out watershed-result.json
# Off-line (previously captured and authenticated source envelope):
python3 experiments/016/watershed.py --sources collected-data.json --out result.json
```

Live mode makes **3** bounded, fixed-site USGS OGC requests plus **1** optional Open-Meteo historical precipitation request. No arbitrary user URLs, authentication, sensitive addresses, remote writes or external effects. A forecast receipt from MOTIF-015 may be attached *as parallel evidence*, not plugged into the hydrologic fit. The public source providers can rate-limit, delay, revise or refuse; HOLD is valid.

## Other environmental frontier probes

- NOAA NWS measured weather observations vs archived forecasts — MOTIF-015.
- USGS stage and discharge gauges over season transitions.
- Real rainfall sensor networks vs gridded reanalyses (separate rain measurement category).
- River response and missing signal question-value selection.
- Compare forecast method errors in different water regimes against stronger physical hydrology models.

The experiment **must not** imply official agency affiliation, flood-warning ability, weather/personal risk advice or permissions to contact anyone.

## Sources

- https://api.waterdata.usgs.gov/docs/ogcapi/migration/
- https://waterdata.usgs.gov/monitoring-location/USGS-05320000/
- https://waterdata.usgs.gov/monitoring-location/USGS-05320500/
- https://waterdata.usgs.gov/monitoring-location/USGS-05325000/
- https://open-meteo.com/en/docs/historical-weather-api
- https://open-meteo.com/en/terms (free hosted service is noncommercial; retain attribution)
