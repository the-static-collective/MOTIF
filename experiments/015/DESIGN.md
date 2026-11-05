# MOTIF-015 — REALITY IRON: THE WEATHER WITNESS

**Research proposal with an executable instrument, not a discovered environmental intelligence.**

## The important crossing

MOTIF-001–014w mostly operate on invented graphs and synthetic evidence. The JAR;VIS ↔ MOTIF Reciprocal Reasoning 001 bridge currently measures *synthetic route-sequence affordances*. It has not established improvements in actual task outcomes.

This experiment introduces a **source-attributed physical-world prediction test**. A forecast issued for a particular UTC hour must be judged against an observed sensor report for that hour. It is a disciplined way to expose overconfidence, missing evidence, wrong units, time-travel leakage, model drift and poor improvement proposals.

**Pilot place:** Mankato Regional Airport station KMKT, southern Minnesota (public environmental station, not user's address). Provider grid query anchored at latitude 44.22, longitude -93.92. A fixed-location pilot is not a geolocation service.

## Real sources

1. **Forecast** — Open-Meteo Previous Model Runs `temperature_2m_previous_day1` (~24h lead) at the stated public coordinates. This is an archived forecast from an earlier model run, not a retrospective reanalysis mislabeled as a forecast. Docs: https://open-meteo.com/en/docs/previous-runs-api
2. **Physical measurement report** — National Weather Service station observations from `/stations/KMKT/observations`. Reports carry timestamp and Celsius value and can be missing or flawed. Docs: https://www.weather.gov/documentation/services-web-api
3. **Evaluation** — deterministic, bounded UTC matching within 25 minutes; record forecast/observation source fingerprints; compute holdout absolute errors and freezing-event misses/false alarms; no external writes.

Open-Meteo's free service is **non-commercial only**, at most 10,000 requests/day, with CC BY 4.0 attribution. Keep provider attribution when displaying measured values. See https://open-meteo.com/en/terms. Commercial or broader automated use requires a separate plan or a directly licensed feed.

NWS's public real-time station API keeps only **seven days** of station observations, making collection time-sensitive. It requires a recognizable User-Agent. This experiment requests only five days back and does not spider arbitrary locations.

## Execute

```sh
python3 -m unittest discover -s experiments/015 -p "test_weather_verifier.py" -v
python3 experiments/015/weather_verifier.py --live
# or use previously captured JSON for fully offline reproducibility:
python3 experiments/015/weather_verifier.py --forecast-file forecast.json --station-file station.json
```

Live mode makes at most two public read-only HTTPS GETs. A nonzero exit / `HOLD` is a legitimate result if the sources refuse service, a station has no recent reports, or the samples cannot be matched. The source responses aren't committed, and raw user questions aren't involved.

## Why this is actual iron, but not a free claim of proof

The published output is an observational **retrospective benchmark** with an explicit chronological train/test split, comparing a 24-hour prior forecast to (a) a mean-bias correction fit on earlier examples and (b) a constant train-mean control. If the adjustment wins on test, the proposal is still **HELD_FOR_INDEPENDENT_VALIDATION**. Further unseen periods, fixed forecast model/source version, geographic baselines and independently captured issue-time records are necessary.

The archived forecast is not proof of what an operator *actually had available* at its alleged issue time; archives may be revised. NWS station measurements are physical sensor testimony, not infallible ground truth. The forecast grid and airport sensor differ spatially. Station reports can be late, corrected or absent. Open-Meteo Best Match changes underlying models over time. Ordinary weather forecast accuracy is not evidence MOTIF has learned.

**Dangerous failure:** if JAR;VIS/MOTIF classifies a synthetic route as smarter because it has more future steps, an environmental benchmark can reveal that no reduction in decision error occurred. The falsifier should be allowed to *beat the diagnostic*.

## Next three source-owned instruments

- USGS Water Data APIs: streamflow, gauge height, daily and continuous sensor series. Independent physical processes and delayed response to rainfall. https://api.waterdata.usgs.gov/
- NWS alerts: warnings issued before a period and independent station records showing what happened (but warning quality requires event-specific verification, not temperature alone).
- NOAA NCEI daily summaries: persistent station measurement archives for longer holdouts, with different update latency and QC properties. https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation

**Proposed JAR;VIS crossing:** feed a read-only, pinned `motif.reality-iron-weather/v1` evidence card to the reciprocal evaluation. Ask the paired systems for bounded hypotheses about forecast error or information value, compare against out-of-sample holdouts and classical controls, and *reject* changes that do not improve scores. Do not silently grant weather-derived recommendations dispatch authority.

## Evidence/authority boundaries

Archived forecast != observed weather; station report != unquestionable truth; retrospective data != information available in real time; an improved fit != generalizable reasoning improvement; a HOLD != failure of the research protocol; a comparison != permission to send alerts or make safety-critical decisions.
