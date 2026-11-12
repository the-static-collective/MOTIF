#!/usr/bin/env python3
"""MOTIF-015: compare archived 24h weather forecasts against station measurements.

This is an observational retrospective benchmark, NOT a weather model or
an independently verified calibration of MOTIF. No external writes, actions,
identities, authorization or inference from people are involved.

Live mode performs exactly two read-only HTTPS GET requests (fixed hosts).
Offline scoring can operate on pre-collected JSON under independent review.
Python 3.10+ standard library only.
"""
from __future__ import annotations

import argparse
from bisect import bisect_left
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import mean
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SCHEMA = "motif.reality-iron-weather/v1"
STATION = "KMKT"                    # Mankato Regional Airport; a public sensor
LATITUDE, LONGITUDE = 44.22, -93.92  # Explicit PUBLIC research point, NOT user location
ARCHIVE_HOST = "https://previous-runs-api.open-meteo.com/v1/forecast"
OBS_HOST = "https://api.weather.gov/stations/KMKT/observations"
USER_AGENT = "MOTIF-Reality-Iron-015 (https://github.com/the-static-collective/MOTIF)"
MAX_RESPONSE_BYTES = 8_000_000
MAX_AGE_DAYS = 7
ALIGNMENT_MINUTES = 25
MIN_MATCHED = 24
MIN_TEST = 8


class HOLD(ValueError):
    """Cannot infer a measured outcome from unsuitable data."""


def parse_utc(value: str, *, assume_utc: bool = False) -> datetime:
    if not isinstance(value, str) or len(value) > 35:
        raise HOLD("invalid timestamp")
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as err:
        raise HOLD("invalid timestamp") from err
    if dt.tzinfo is None:
        if not assume_utc:
            raise HOLD("observation without timezone")
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def celsius(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise HOLD("nonfinite or nonscalar temperature")
    if not -95 <= value <= 65:
        raise HOLD("impossible temperature outside instrument envelope")
    return float(value)


def forecasts(payload: object) -> dict[datetime, float]:
    if not isinstance(payload, dict) or payload.get("hourly_units", {}).get(
        "temperature_2m_previous_day1") not in ("°C", "C"):
        raise HOLD("unexpected archive units")
    if payload.get("timezone") not in ("GMT", "UTC"):
        raise HOLD("unexpected forecast timezone")
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise HOLD("missing archive hourly series")
    times = hourly.get("time")
    vals = hourly.get("temperature_2m_previous_day1")
    if not isinstance(times, list) or not isinstance(vals, list) or len(times) != len(vals):
        raise HOLD("archive arrays do not align")
    if len(times) > 1000:
        raise HOLD("archive sample budget exceeded")
    pairs = {}
    for stamp, val in zip(times, vals):
        dt = parse_utc(stamp, assume_utc=True)
        temp = celsius(val)
        if temp is None:
            continue
        if dt in pairs:
            raise HOLD("duplicate archived forecast valid time")
        pairs[dt] = temp
    return pairs


def observations(payload: object) -> list[tuple[datetime, float]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("features"), list):
        raise HOLD("missing NOAA station observations")
    features = payload["features"]
    if len(features) > 800:
        raise HOLD("observation budget exceeded")
    out = {}
    for f in features:
        if not isinstance(f, dict) or not isinstance(f.get("properties"), dict):
            raise HOLD("invalid station feature")
        p = f["properties"]
        temp = p.get("temperature")
        if not isinstance(temp, dict):
            continue
        if temp.get("unitCode") != "wmoUnit:degC":
            raise HOLD("unexpected NOAA temperature unit")
        val = celsius(temp.get("value"))
        if val is None:
            continue
        dt = parse_utc(p.get("timestamp"))
        # Multiple reports for the same timestamp cannot be separate witnesses.
        if dt in out and out[dt] != val:
            raise HOLD("conflicting observation with same timestamp")
        out[dt] = val
    return sorted(out.items())


def match_samples(f: dict[datetime, float],
                  o: list[tuple[datetime, float]],
                  now: datetime) -> list[dict]:
    now = now.astimezone(timezone.utc)
    obs_times = [row[0] for row in o]
    matched = []
    used = set()
    for when, predicted in sorted(f.items()):
        if when >= now - timedelta(hours=6) or when < now - timedelta(days=MAX_AGE_DAYS):
            continue
        pos = bisect_left(obs_times, when)
        nearby = []
        for idx in (pos - 1, pos):
            if 0 <= idx < len(o) and idx not in used:
                delta = abs((o[idx][0] - when).total_seconds())
                if delta <= ALIGNMENT_MINUTES * 60:
                    nearby.append((delta, idx))
        if not nearby:
            continue
        _, closest = min(nearby)
        used.add(closest)
        observed_at, observed = o[closest]
        matched.append({
            "valid_utc": when.isoformat().replace("+00:00", "Z"),
            "observed_utc": observed_at.isoformat().replace("+00:00", "Z"),
            "forecast_c": predicted, "observed_c": observed,
            "alignment_minutes": round(abs((when - observed_at).total_seconds()) / 60, 2)
        })
    return matched


def mae(rows, predict) -> float:
    return round(mean(abs(float(predict(row)) - row["observed_c"]) for row in rows), 4)


def freezing_counts(rows, predict) -> dict:
    truth = lambda x: x["observed_c"] <= 0
    guess = lambda x: float(predict(x)) <= 0
    return {
        "events": sum(truth(x) for x in rows),
        "misses": sum(truth(x) and not guess(x) for x in rows),
        "false_alarms": sum(not truth(x) and guess(x) for x in rows)
    }


def evaluate(forecast_payload: object, obs_payload: object,
             now: datetime | None = None) -> dict:
    """Train/test split by VALID TIME; a corrected forecast must beat controls.

    We do NOT claim this establishes forecast issuances, sensor independence,
    physical causality, or real-time availability. Model archives and NOAA
    observations can be revised, and the forecast grid is not the station.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise HOLD("UTC observation time required")
    records = match_samples(forecasts(forecast_payload), observations(obs_payload), now)
    if len(records) < MIN_MATCHED:
        raise HOLD(f"insufficient matched observations: {len(records)} (<{MIN_MATCHED})")
    split = int(len(records) * 2 / 3)
    train, test = records[:split], records[split:]
    if len(test) < MIN_TEST or len(train) < 16:
        raise HOLD("chronological split too small")
    bias = mean(x["observed_c"] - x["forecast_c"] for x in train)
    baseline_mean = mean(x["observed_c"] for x in train)
    raw = mae(test, lambda x: x["forecast_c"])
    corrected = mae(test, lambda x: x["forecast_c"] + bias)
    constant = mae(test, lambda x: baseline_mean)
    improvement = round(raw - corrected, 4)
    # Never silently label a retrospective fit as a real-time deployed upgrade.
    proposal = ("HELD_FOR_INDEPENDENT_VALIDATION" if improvement >= 0.1
                else "HOLD_NO_MEASURED_IMPROVEMENT")
    provenance = {
        "forecast_provider": "Open-Meteo Previous Runs 24h lead (Best Match)",
        "forecast_url": ARCHIVE_HOST,
        "station_provider": "NWS reported station observation KMKT",
        "observation_url": OBS_HOST,
        "source_snapshots_sha256": {
            "forecast": sha256(json.dumps(forecast_payload, sort_keys=True).encode()).hexdigest(),
            "observations": sha256(json.dumps(obs_payload, sort_keys=True).encode()).hexdigest()
        },
        "public_research_coordinate": [LATITUDE, LONGITUDE],
        "lead_hours": 24, "reference_temperature_unit": "Celsius",
        "alignment_max_minutes": ALIGNMENT_MINUTES,
    }
    return {
        "schema": SCHEMA, "status": "RETROSPECTIVE_OBSERVATIONAL_COMPARISON",
        "station": STATION, "matched_count": len(records),
        "train_count": len(train), "test_count": len(test),
        "train_end_utc": train[-1]["valid_utc"], "test_begin_utc": test[0]["valid_utc"],
        "period_start_utc": records[0]["valid_utc"], "period_end_utc": records[-1]["valid_utc"],
        "temperature_bias_train_c": round(bias, 4),
        "holdout_mae_c": {"raw_previous_day1": raw,
                          "train_bias_adjusted": corrected,
                          "train_only_constant": constant},
        "holdout_freezing_c": {
            "raw_previous_day1": freezing_counts(test, lambda x: x["forecast_c"]),
            "train_bias_adjusted": freezing_counts(test, lambda x: x["forecast_c"] + bias)
        },
        "difference_raw_minus_adjusted_mae_c": improvement,
        "improvement_disposition": proposal,
        "provenance": provenance,
        "source_independence": "FORECAST_PRODUCT_AND_REPORTED_STATION_SENSOR; NOT PROVEN FULLY INDEPENDENT",
        "limitations": [
            "Archived forecasts are retrospectively accessed, not independently captured at issue time.",
            "Open-Meteo Best Match model selection may vary; the research needs fixed-model runs.",
            "NWS station values may be missing, delayed, revised or differ from the forecast grid.",
            "24-hour lead definition is provider documented, not independently verified here.",
            "Short chronological holdout is insufficient to establish robust calibration.",
            "A fitted bias correction is a held proposal, not an automatic operational change."
        ],
        "real_world_effect": False, "authority": False, "automatic_promotion": False
    }


def get_json(url: str, *, nws: bool = False) -> dict:
    if not url.startswith(OBS_HOST + "?") and not url.startswith(ARCHIVE_HOST + "?"):
        raise HOLD("source outside fixed allowlist")
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json" if nws else "application/json"}
    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=18) as response:
            if response.status != 200:
                raise HOLD("source unavailable")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as err:
        raise HOLD("source unavailable or rate limited") from err
    if len(raw) > MAX_RESPONSE_BYTES:
        raise HOLD("source response too large")
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeError) as err:
        raise HOLD("source did not return JSON") from err
    if not isinstance(value, dict):
        raise HOLD("source JSON not an object")
    return value


def fetch_pair(now: datetime):
    # No geolocation. One fixed, public municipal airport station.
    forecast_qs = urlencode({
        "latitude": LATITUDE, "longitude": LONGITUDE,
        "hourly": "temperature_2m_previous_day1",
        "temperature_unit": "celsius", "timezone": "UTC",
        "past_days": 5, "forecast_days": 1
    })
    first = now - timedelta(days=5)
    end = now - timedelta(hours=6)
    station_qs = urlencode({
        "start": first.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "end": end.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "limit": 500
    })
    return get_json(ARCHIVE_HOST + "?" + forecast_qs), get_json(OBS_HOST + "?" + station_qs, nws=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="two read-only public HTTPS GETs")
    ap.add_argument("--forecast-file", type=Path)
    ap.add_argument("--station-file", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    try:
        if args.live:
            if args.forecast_file or args.station_file:
                raise HOLD("choose live or explicitly supplied files")
            pair = fetch_pair(datetime.now(timezone.utc))
        else:
            if not args.forecast_file or not args.station_file:
                raise HOLD("provide two source JSON files or --live")
            pair = (json.loads(args.forecast_file.read_text()),
                    json.loads(args.station_file.read_text()))
        out = evaluate(*pair)
        encoded = json.dumps(out, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf8")
        print(encoded)
        return 0
    except (HOLD, ValueError, OSError, TypeError, json.JSONDecodeError) as err:
        # No fake data, no retries to hide a failed read.
        print("HOLD: " + str(err)[:180], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
