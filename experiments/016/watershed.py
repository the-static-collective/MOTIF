#!/usr/bin/env python3
"""MOTIF-016 — LIVING WATERSHED: real hydrologic witness vs held-out controls.

Three fixed public USGS streamflow sensors form a hypothesis, NOT a declared
causal flow model. Optional Open-Meteo historical gridded precipitation adds
retrospective context (not an independent rain-gauge measurement).
Read-only HTTPS; no actuator, alerts, persons, or automatic promotion.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import mean
import sys
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SCHEMA = "motif.reality-iron-watershed/v1"
USGS = "https://api.waterdata.usgs.gov/ogcapi/v1/collections/continuous/items"
RAIN = "https://archive-api.open-meteo.com/v1/archive"
# Named public upstream tributary sensors and downstream RECEIVER; presence of
# upstream gauges does NOT make the downstream target a mass-balance sum.
SITES = {"blue": "USGS-05320000", "sueur": "USGS-05320500", "mankato": "USGS-05325000"}
LAT, LON = 44.17, -94.00
PARAMETER = "00060"  # Discharge in cubic feet per second
MAX_BYTES = 5_000_000
MAX_FEATURES = 1800
HORIZON_HOURS = 7   # Completed hourly window at t-7; >6h non-lookahead
DIFF_HOURS = 6
MIN_ROWS = 78
MAX_ROWS = 600
CANDIDATES = ("persistence", "local_trend", "cross_gauges", "rain_context")
FEATURES = {
    "local_trend": ("local_delta",),
    "cross_gauges": ("local_delta", "blue_delta", "sueur_delta"),
    "rain_context": ("local_delta", "blue_delta", "sueur_delta", "rain6"),
}


class HOLD(ValueError):
    pass


def ensure(condition, reason):
    if not condition:
        raise HOLD(reason)


def utc(s):
    ensure(isinstance(s, str) and len(s) < 64, "BAD_TIMESTAMP")
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HOLD("BAD_TIMESTAMP") from exc
    ensure(d.tzinfo is not None, "MISSING_UTC_OFFSET")
    return d.astimezone(timezone.utc)


def number(x, *, nonnegative=True):
    try:
        v = float(x)
    except (ValueError, TypeError) as exc:
        raise HOLD("BAD_NUMERIC_SENSOR") from exc
    ensure(math.isfinite(v) and (not nonnegative or v >= 0) and v < 10_000_000,
           "OUTSIDE_NUMERIC_SENSOR_ENVELOPE")
    return v


def digest(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True).encode()).hexdigest()


def gauges(data: dict, site: str):
    """Reject wrong site, unit, parameter, duplicate/conflict and pagination."""
    ensure(site in SITES, "UNKNOWN_FIXED_SENSOR")
    ensure(type(data) is dict and data.get("type") == "FeatureCollection"
           and isinstance(data.get("features"), list), "INVALID_USGS_GEOJSON")
    feats = data["features"]
    ensure(len(feats) <= MAX_FEATURES and len(feats) > 0, "USGS_COLLECTION_BUDGET_OR_EMPTY")
    if any(link.get("rel") == "next" for link in data.get("links", [])
           if isinstance(link, dict)):
        raise HOLD("USGS_PAGINATED_NO_SILENT_SAMPLE")
    samples = {}
    for entry in feats:
        ensure(type(entry) is dict and type(entry.get("properties")) is dict,
               "INVALID_SENSOR_FEATURE")
        p = entry["properties"]
        ensure(p.get("monitoring_location_id") == SITES[site] and
               p.get("parameter_code") == PARAMETER, "MIXED_USGS_SENSOR_OR_VARIABLE")
        unit = p.get("unit_of_measure")
        ensure(unit in ("ft3/s", "ft^3/s", "ft³/s", "ft3 s-1"), "UNEXPECTED_FLOW_UNIT")
        q = number(p.get("value"))
        t = utc(p.get("time"))
        ensure(t not in samples or samples[t] == q, "CONFLICTING_SAME_TIME_SENSOR")
        samples[t] = q
    byhour = defaultdict(list)
    for t, v in samples.items():
        hour = t.replace(minute=0, second=0, microsecond=0)
        byhour[hour].append(v)
    ensure(len(byhour) >= 50, "INSUFFICIENT_USGS_HOURLY_MEASUREMENTS")
    return {hour: mean(values) for hour, values in byhour.items()}


def rainfall(data):
    """Grid-estimated retrospective precipitation; NOT a physical rain sensor."""
    ensure(type(data) is dict and data.get("timezone") in ("GMT", "UTC"),
           "RAIN_TIMEZONE_MISMATCH")
    ensure(data.get("hourly_units", {}).get("precipitation") == "mm",
           "RAIN_UNITS_MISMATCH")
    h = data.get("hourly", {})
    times, values = h.get("time"), h.get("precipitation")
    ensure(isinstance(times, list) and isinstance(values, list)
           and len(times) == len(values) and len(times) <= 1000, "BAD_RAIN_SERIES")
    out = {}
    for t, val in zip(times, values):
        dt = utc(t + "Z" if len(t) == 16 and t[10] == "T" else t)
        if val is None:
            continue
        ensure(dt not in out, "DUPLICATE_RAIN_HOUR")
        out[dt] = number(val)
    return out


def frame(data, *, now=None):
    ensure(isinstance(data, dict) and set(data) == {"blue", "sueur", "mankato", "rain"},
           "INVALID_WATERSHED_ENVELOPE")
    fs = {key: gauges(data[key], key) for key in SITES}
    weather = rainfall(data["rain"]) if data["rain"] is not None else {}
    rain_available = data["rain"] is not None
    times = sorted(set.intersection(*(set(rows) for rows in fs.values())))
    rows = []
    for target in times:
        origin = target - timedelta(hours=HORIZON_HOURS)
        past = origin - timedelta(hours=DIFF_HOURS)
        if any(origin not in fs[k] or past not in fs[k] for k in SITES):
            continue
        if now is not None and target > now - timedelta(hours=2):
            continue  # report latency; no future/near-current claim
        known = fs["mankato"][origin]
        row = {
            "target_utc": target.isoformat().replace("+00:00", "Z"),
            "y": fs["mankato"][target],
            "known": known,
            "local_delta": known - fs["mankato"][past],
            "blue_delta": fs["blue"][origin] - fs["blue"][past],
            "sueur_delta": fs["sueur"][origin] - fs["sueur"][past],
        }
        # Missing weather is missing, not zero rainfall.
        hours = [origin - timedelta(hours=i) for i in range(6)]
        row["rain6"] = sum(weather[t] for t in hours) if all(t in weather for t in hours) else None
        rows.append(row)
    ensure(MIN_ROWS <= len(rows) <= MAX_ROWS, "INSUFFICIENT_OR_OVERSIZED_COMPLETE_HOURLY_CASES")
    return rows, rain_available


def fit_ridge(train, names, penalty=2.0):
    """Train-only regularized linear adjustment; scale features on train only."""
    k = len(names)
    means = [mean(row[name] for row in train) for name in names]
    scales = [(mean((row[name] - means[i])**2 for row in train)**0.5) or 1.0
              for i, name in enumerate(names)]
    mat = [[0.0] * (k+1) for _ in range(k+1)]
    vec = [0.0] * (k+1)
    for row in train:
        x = [1.0] + [(row[name] - means[i])/scales[i] for i,name in enumerate(names)]
        y = row["y"] - row["known"]
        for i in range(k+1):
            vec[i] += x[i] * y
            for j in range(k+1):
                mat[i][j] += x[i] * x[j]
    for i in range(1,k+1):
        mat[i][i] += penalty
    # Deterministic Gauss-Jordan elimination on small strictly-ridged system.
    for i in range(k+1):
        swap = max(range(i,k+1), key=lambda j: abs(mat[j][i]))
        ensure(abs(mat[swap][i]) > 1e-10, "NONIDENTIFIABLE_TRAINING_SYSTEM")
        mat[i], mat[swap] = mat[swap], mat[i]
        vec[i], vec[swap] = vec[swap], vec[i]
        scale = mat[i][i]
        for j in range(i,k+1):
            mat[i][j] /= scale
        vec[i] /= scale
        for j in range(k+1):
            if j == i:
                continue
            factor = mat[j][i]
            for h in range(i,k+1):
                mat[j][h] -= factor * mat[i][h]
            vec[j] -= factor * vec[i]
    return {"names": list(names), "mean": means, "scale": scales, "weights": vec}


def predict(row, model):
    if model is None:
        return row["known"]
    x = [1] + [(row[n] - model["mean"][i]) / model["scale"][i]
                 for i,n in enumerate(model["names"])]
    return row["known"] + sum(a*b for a,b in zip(x, model["weights"]))


def mae(rows, model):
    return round(mean(abs(row["y"] - predict(row, model)) for row in rows), 4)


def score_rises(rows, model):
    rising = [row for row in rows if row["y"] >= row["known"] * 1.05 and
              row["y"] - row["known"] >= 20]
    return {"rising_count": len(rising),
            "mae_cfs": mae(rising, model) if rising else None}


def evaluate(raw, *, now=None, weather_witness=None):
    records, rainy = frame(raw, now=now)
    # Three chronological partitions; no future values in feature construction.
    n = len(records)
    n_train, n_val = int(n * .55), int(n * .20)
    train, validation, test = (records[:n_train],
                               records[n_train:n_train+n_val],
                               records[n_train+n_val:])
    ensure(len(train)>=38 and len(validation)>=15 and len(test)>=18,
           "SMALL_TEMPORAL_SPLIT")
    available = ["persistence", "local_trend", "cross_gauges"]
    if rainy and all(row["rain6"] is not None for row in records):
        available.append("rain_context")
    else:
        # Absence of precipitation context does not mean absence of rain.
        rainy = False
    models = {"persistence": None}
    for name in available[1:]:
        models[name] = fit_ridge(train, FEATURES[name])
    val_scores = {name:mae(validation, models[name]) for name in available}
    # Fixed tie-break by increasing model simplicity, selection on validation only.
    selected = min(available,key=lambda name:(val_scores[name],available.index(name)))
    test_scores = {name:mae(test, models[name]) for name in available}
    base = test_scores["persistence"]
    chosen = test_scores[selected]
    abs_improvement = round(base-chosen,4)
    rel_improvement = round(100 * abs_improvement/max(base,1e-9),3)
    rising = {name:score_rises(test, models[name]) for name in available}
    sufficient_rises = rising["persistence"]["rising_count"] >= 3
    if selected=="persistence" or abs_improvement<=0:
        status = "HOLD_NO_IMPROVEMENT"
    elif not sufficient_rises:
        status = "HOLD_INSUFFICIENT_RISING_EVENTS"
    elif rel_improvement < 10:
        status = "HOLD_WEAK_IMPROVEMENT"
    else:
        status = "HELD_FOR_NEW_PERIOD_REPLICATION"
    provenance = {
        "source_urls": {
            "USGS_modern_continuous": USGS,
            "precipitation_context": RAIN if rainy else None
        },
        "USGS_public_site_ids": SITES, "flow_parameter":"00060",
        "source_json_sha256":{k:digest(raw[k]) if raw[k] is not None else None
                              for k in sorted(raw)},
        "rain_type":"OPEN_METEO_GRIDDED_HISTORICAL_ESTIMATE_NOT_RAIN_GAUGE" if rainy else "UNAVAILABLE",
        "public_context_coordinate":[LAT,LON],
        "observation_units":"cubic_feet_per_second",
        "forecast_horizon_minimum_hours": 6,
        "known_hour_offset": HORIZON_HOURS,
        "time_split":"chronological_55_20_25",
    }
    forecast_note = None
    if weather_witness is not None:
        ensure(type(weather_witness) is dict and
               weather_witness.get("schema")=="motif.reality-iron-weather/v1" and
               weather_witness.get("status")=="RETROSPECTIVE_OBSERVATIONAL_COMPARISON" and
               weather_witness.get("station")=="KMKT" and
               weather_witness.get("real_world_effect") is False and
               isinstance(weather_witness.get("provenance"),dict) and
               isinstance(weather_witness["provenance"].get("source_snapshots_sha256"),dict),
               "INVALID_PRIOR_WEATHER_WITNESS")
        forecast_note = {
            "source_schema": "motif.reality-iron-weather/v1",
            "input_card_sha256": digest(weather_witness),
            "weather_015_disposition": weather_witness.get("improvement_disposition"),
            "relation":"PARALLEL_EVIDENCE_NOT_A_PREDICTOR_OR_GROUND_TRUTH",
        }
    return {
        "schema":SCHEMA,
        "scope":"RETROSPECTIVE_REAL_SENSOR_TEST_NOT_DEPLOYED_FORECAST",
        "matched_complete_hours":n,
        "partitions":{"train":len(train),"validation":len(validation),"test":len(test)},
        "period_start_utc":records[0]["target_utc"],
        "period_end_utc":records[-1]["target_utc"],
        "heldout_start_utc":test[0]["target_utc"],
        "validation_mae_cfs":val_scores,
        "holdout_mae_cfs":test_scores,
        "selected_on_validation":selected,
        "holdout_improvement_vs_persistence_cfs":abs_improvement,
        "holdout_improvement_vs_persistence_percent":rel_improvement,
        "rising_event_test_scores":rising,
        "disposition":status,
        "hypothesis_test":"Do measured tributary-flow changes (and retrospective gridded rain, if available) help predict Mankato streamflow relative to persistence?",
        "next_discriminating_question":(
            "Would the selected method beat persistence on an untouched future river regime with multiple rise events?"
            if sufficient_rises else
            "Can we observe at least three independent rising-flow test hours before claiming flood/rise skill?"
        ),
        "peer_diagnostic":{
            "MOTIF_to_JARVIS":"Treat model selection on earlier validation as a held experiment; compare later physical test error before claiming a useful next action.",
            "JARVIS_to_MOTIF":"Three gauges belong to coupled rivers. Shared weather, delayed reporting, and retrospective rainfall may create spurious causal-looking gains.",
            "self_diagnostic":"This test may fail under a seasonal regime shift. The scorer can improve: use block-holdout by hydrologic event and fit a rainfall-free control."
        },
        "prior_weather_015":forecast_note,
        "provenance":provenance,
        "limitations":[
            "USGS stage/discharge estimates can be provisional or revised; sensors are not independent draws.",
            "Mankato flow includes upstream Minnesota basin, not just the two measured tributaries.",
            "Hourly averages are computed retrospectively; gauge telemetry latency is not modeled.",
            "Open-Meteo historical precipitation is gridded model/reanalysis context, not rain-gauge truth or guaranteed available at issue time.",
            "Past-6h context is calculated using hours fully prior to target; report availability may lag.",
            "Single watershed and short retrospective window; no flood thresholds or safety alert calibration.",
            "Choosing a method on validation does not prove generalization across events, seasons or basins."
        ],
        "independent_outcome_verified":False,
        "automatic_promotion":False,"real_world_effect":False,"authority":False
    }


def request_json(url):
    host=urlparse(url).netloc
    ensure(urlparse(url).scheme=="https" and host in
           ("api.waterdata.usgs.gov","archive-api.open-meteo.com"),"OUTSIDE_FIXED_HOSTS")
    req=Request(url,headers={"User-Agent":"MOTIF-016 Watershed Research (github.com/the-static-collective/MOTIF)",
                             "Accept":"application/geo+json,application/json"},method="GET")
    try:
        with urlopen(req,timeout=18) as r:
            ensure(r.status==200, "REMOTE_HTTP_FAILURE")
            final=urlparse(r.geturl())
            ensure(final.scheme=="https" and final.netloc==host,"SOURCE_REDIRECT_OUTSIDE_ALLOWLIST")
            content=r.read(MAX_BYTES+1)
    except (HTTPError,URLError,TimeoutError,OSError) as exc:
        raise HOLD("REMOTE_SOURCE_UNAVAILABLE") from exc
    ensure(len(content)<=MAX_BYTES,"REMOTE_JSON_OVERSIZE")
    try:
        return json.loads(content)
    except (UnicodeError,ValueError) as exc:
        raise HOLD("MALFORMED_REMOTE_JSON") from exc


def get_live(now):
    # End 6 days ago to accommodate public gridded historical archive latency.
    end=(now-timedelta(days=6)).date()
    start=end-timedelta(days=14)
    interval=start.isoformat()+"/"+end.isoformat()
    raw={}
    for name,site in SITES.items():
        q=urlencode({"monitoring_location_id":site,"parameter_code":PARAMETER,
                     "datetime":interval,"f":"json","limit":1800})
        raw[name]=request_json(USGS+"?"+q)
    rain_q=urlencode({"latitude":LAT,"longitude":LON,"start_date":start.isoformat(),
                      "end_date":end.isoformat(),"hourly":"precipitation",
                      "timezone":"GMT"})
    try:
        raw["rain"]=request_json(RAIN+"?"+rain_q)
    except HOLD:
        raw["rain"]=None # No precipitation = unavailable, not dry.
    return raw


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--live",action="store_true",help="read-only fixed public USGS+Open-Meteo APIs")
    ap.add_argument("--sources",type=Path,help="pre-captured four-source JSON envelope")
    ap.add_argument("--weather-witness",type=Path,help="optional 015 witness card (parallel evidence)")
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    try:
        ensure(args.live != bool(args.sources),"SELECT_LIVE_XOR_SOURCE_FILE")
        raw=get_live(datetime.now(timezone.utc)) if args.live else json.loads(args.sources.read_text())
        weather=json.loads(args.weather_witness.read_text()) if args.weather_witness else None
        result=evaluate(raw,now=datetime.now(timezone.utc),weather_witness=weather)
        s=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=True)+"\n"
        if args.out:
            args.out.write_text(s,encoding="utf8")
        print(s)
        return 0
    except (HOLD,ValueError,TypeError,OSError) as exc:
        print("HOLD: "+str(exc)[:180],file=sys.stderr)
        return 2


if __name__=="__main__":
    sys.exit(main())
