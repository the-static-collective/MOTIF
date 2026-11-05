# MOTIF-017 — Learning from the losing watershed model

## Falsifiable learning, not a success story

MOTIF-016's three-gauge validation winner **lost** to untrained persistence on later 2026 low-flow data. The next consequential question is whether a more cautious, *pre-registered* policy can learn to distrust apparent validation success, rather than simply adding more parameters.

This experiment makes a specific evidence-derived change to the **evaluation method**: before seeing the locked event test, compare the old choice rule (lowest validation MAE) against a new cautious rule that requires:
1. A 20% improvement over persistence on full validation.
2. A 10% improvement in **both** pre-event validation halves.
3. Median downstream flow regime reasonably similar to earlier training (0.5× to 2×).
4. At a hypothetical issue-time, fall back to persistence if the last-known downstream flow is outside 0.5×/1.5× of the training range.

These values are *declared design choices*, not learned scientifically. The cautious rule can be worse than the old one; that is counted as a negative. No model is adjusted after observing test labels.

## Predeclared historical event

The June 2024 southern Minnesota flood was documented by NOAA/NWS; it is an especially severe test, including the Rapidan Dam crisis. NOAA/NWS documentation: https://www.weather.gov/mpx/RecordFloodingJune2024 . USGS reported on June 24, 2024 that the Rapidan gauge structure was secure but its power was lost: https://water.usgs.gov/alerts/item_2024-06-24_17%3A20%3A54.html . **Sensor availability is part of the experiment**, not something to interpolate away or pass as environmental truth.

Three non-overlapping, hard-coded observational windows:
- **Training:** 2023-05-04 through 2023-05-13 (historic, earlier year).
- **Validation:** 2024-06-01 through 2024-06-10.
- **Sealed, unqueried until policy is frozen:** 2024-06-18 through 2024-06-28 (published flood).

Selection of the event is retrospective. This is *not a prospective prediction made in 2024*, nor independent proof of generalization. The older 2023 window precedes the 2024 validation and flood.

Only USGS public `00060` discharge streamflow data for these three fixed stations is used:
Blue Earth River near Rapidan `05320000`, Le Sueur River near Rapidan `05320500`, Minnesota River at Mankato `05325000`.

**No gridded rainfall in 017**, explicitly removing a retrospective-information avenue that performed poorly in 016. Each 6+ hour prediction uses streamflow features up through t-7 hours. Actual telemetry availability and post-hoc rating-curve revisions are *not* reconstructed. Hourly mean flows are retrospective aggregation.

## Two-stage source separation

Run locally from repo root (Python 3.10+ stdlib only):

```sh
python3 -m unittest discover -s experiments/017 -p "test_event_learner.py" -v
python3 experiments/017/event_learner.py prepare --out-dir /tmp/motif017
# Inspect saved frozen-plan.json and its SHA-256 BEFORE opening event data.
python3 experiments/017/event_learner.py evaluate --out-dir /tmp/motif017
```

The GitHub workflow also invokes those commands in this exact order and uploads the full public-source responses and result as a private-to-run artifact for audit (not directly committed). For replays without live network:
```sh
python3 experiments/017/event_learner.py prepare --offline --out-dir /tmp/motif017
python3 experiments/017/event_learner.py evaluate --offline --out-dir /tmp/motif017
```
Offline mode requires pre-captured `train-raw.json`, `validation-raw.json`, and `event-raw.json`. It refuses overwriting the sealed plan or result. Plans are SHA-256 checksummed (**content integrity, not a source-authority signature**); a malicious person who can rewrite all files can still create a different plan.

The actual `event-raw.json` is **not opened or fetched** by the prepare command. The evaluate command re-verifies the complete frozen plan, then gets only the 2024 event source and scores both policies on the same observations. It explicitly reports source fingerprints, missing matched-hour coverage, event rises, old-policy loss, cautious-policy loss, and whether caution helped or harmed. Both models remain HELD even on a positive event.

## Adversarial questions

- Did the evaluation method change its model selection **before** seeing event labels?
- Are missing Blue Earth measurements during the Rapidan Dam failure causing biased event coverage?
- Did the policy just default to persistence? If so, did that help *on this event*, or not?
- Does the policy generalize to another hydrologic event we have not already identified?
- Are gains only caused by post-hoc discharge rating estimates, rather than contemporaneously available readings?
- Does high-water skill differ from mean MAE, and are there at least three rising-flow test cases?

**No flood/stage warning, evacuation, emergency classification, dispatch, real-time operational advice or fully autonomous self-modification is authorized here.** USGS data are public and often provisional; source agency approval status is preserved in raw responses for audit. Use stronger physical modeling, archived originally issued forecasts and independent gauge data before any safety-relevant use.

Source: https://api.waterdata.usgs.gov/docs/ogcapi/migration/ . This experiment is an isolated, source-owned research branch stacked on MOTIF-016 and 015.
