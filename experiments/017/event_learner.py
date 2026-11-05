#!/usr/bin/env python3
"""MOTIF-017: learn from failed river-model selection without test-label leakage.

Prepare fits and seals two rival policies using PRE-EVENT windows only.
Evaluate opens the sealed plan and retrieves the *previously unqueried* public
June 2024 flood record. Historical retrospective; not a forecast that was
actually issued, no automated learning, alarm, or physical action.

All source windows and thresholds were fixed in source before the event fetch.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from statistics import median, mean
from urllib.parse import urlencode
import hashlib
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "016"))
import watershed as water

SCHEMA = "motif.reality-iron-event-learning/v1"
PLAN_SCHEMA = "motif.event-frozen-plan/v1"
# Predeclared before event read. The final window was chosen because NOAA/NWS
# publicly documented the June 2024 flood; this is event selection in hindsight.
WINDOWS = {
    "train": ("2023-05-04", "2023-05-13"),
    "validation": ("2024-06-01", "2024-06-10"),
    "event": ("2024-06-18", "2024-06-28"),
}
SITES = dict(water.SITES)
METHODS = ("persistence", "local_trend", "cross_gauges")
MIN_CASES = {"train": 70, "validation": 70, "event": 48}
MAX_DAYS = 12
MIN_VALIDATION_RELATIVE_ADVANTAGE = 0.20
MIN_HALF_ADVANTAGE = 0.10
MAX_FLOW_REGIME_MULTIPLIER = 2.0
OOD_LOW_MULTIPLIER = 0.5
OOD_HIGH_MULTIPLIER = 1.5
RISING_RELATIVE = 0.05
RISING_ABSOLUTE_CFS = 20
MAX_READ_BYTES = 6_000_000
HISTORIC_EVENT_SOURCE = "https://www.weather.gov/mpx/RecordFloodingJune2024"


def require(test, reason):
    if not test:
        raise water.HOLD(reason)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)


def fingerprint(obj):
    return hashlib.sha256(canonical(obj).encode("utf8")).hexdigest()


def _period(name):
    start, end = WINDOWS[name]
    return datetime.fromisoformat(start).replace(tzinfo=timezone.utc), (
        datetime.fromisoformat(end).replace(tzinfo=timezone.utc) + timedelta(days=1)
    )


def download_window(name):
    """Three fixed public USGS queries; no test records in preparation mode."""
    require(name in WINDOWS, "UNLISTED_WINDOW")
    start,end = WINDOWS[name]
    raw={"rain":None}
    for station,site in SITES.items():
        params=urlencode({"monitoring_location_id":site,
                          "parameter_code":"00060",
                          "datetime":start+"/"+end,"limit":"1800","f":"json"})
        # Source network primitive is reused from 016 and separately allowlisted.
        raw[station]=water.request_json(water.USGS+"?"+params)
    return raw


def rows_from(raw,name):
    """Checked USGS features; separate windows cannot overlap or blend."""
    require(name in WINDOWS and type(raw) is dict,"UNLISTED_WINDOW")
    parsed, rain=water.frame(raw)
    require(not rain, "RAIN_CONTEXT_MUST_NOT_ENTER_THIS_EXPERIMENT")
    lo,hi=_period(name)
    parsed=[x for x in parsed if lo<=water.utc(x["target_utc"])<hi]
    require(len(parsed)>=MIN_CASES[name],"INSUFFICIENT_MATCHED_EVENT_HOURS")
    require(all(lo<=water.utc(x["target_utc"])<hi for x in parsed),
            "CROSS_WINDOW_LEAK")
    # Source can be incomplete; quantify coverage rather than zero-fill.
    hours=int((hi-lo).total_seconds()/3600)
    return parsed,{"available_complete_hours":len(parsed),
                   "total_calendar_hours":hours,
                   "complete_hour_coverage":round(len(parsed)/hours,4)}


def score(rows,model):
    return mean(abs(x["y"] - water.predict(x,model)) for x in rows)


def score_policy(rows,selection,models,thresholds,*,context):
    """Predictions use only origin-known features; no y data in routing."""
    total=0.0
    fallbacks=0
    count=0
    for row in rows:
        use=selection
        if context=="cautious" and selection!="persistence":
            # Training-only extrema determine extrapolation guard.
            if row["known"]<thresholds["low_cfs"] or row["known"]>thresholds["high_cfs"]:
                use="persistence"
                fallbacks+=1
        yhat=water.predict(row, models[use])
        total+=abs(row["y"]-yhat)
        count+=1
    return {"mae_cfs":round(total/count,4),
            "origin_only_fallbacks":fallbacks,
            "count":count}


def freeze(train_raw,validation_raw):
    """No event/source/target can enter this function, by API construction."""
    train,train_coverage=rows_from(train_raw,"train")
    val,val_coverage=rows_from(validation_raw,"validation")
    model={"persistence":None}
    for name in METHODS[1:]:
        model[name]=water.fit_ridge(train,water.FEATURES[name])
    metrics={name:round(score(val,model[name]),4) for name in METHODS}
    halves=[val[:len(val)//2],val[len(val)//2:]]
    half_mae=[{name:round(score(part,model[name]),4) for name in METHODS}
              for part in halves]
    legacy=min(METHODS,key=lambda name:(metrics[name],METHODS.index(name)))
    selected="persistence"
    reasons=[]
    train_median=median(x["known"] for x in train)
    val_median=median(x["known"] for x in val)
    ratio=val_median/max(train_median,1)
    if not 1/MAX_FLOW_REGIME_MULTIPLIER<=ratio<=MAX_FLOW_REGIME_MULTIPLIER:
        reasons.append("REGIME_SHIFT_IN_PRE_EVENT_VALIDATION")
    else:
        options=[]
        base=metrics["persistence"]
        for name in METHODS[1:]:
            advantage=(base-metrics[name])/max(base,1e-9)
            if advantage<MIN_VALIDATION_RELATIVE_ADVANTAGE:
                continue
            if not all(
                (half["persistence"]-half[name])/max(half["persistence"],1e-9)
                >=MIN_HALF_ADVANTAGE for half in half_mae
            ):
                continue
            options.append(name)
        if options:
            selected=min(options,key=lambda n:(metrics[n],METHODS.index(n)))
        else:
            reasons.append("NO_STABLE_TWO_HALF_VALIDATION_ADVANTAGE")
    thresholds={
        "low_cfs": round(min(x["known"] for x in train)*OOD_LOW_MULTIPLIER,4),
        "high_cfs": round(max(x["known"] for x in train)*OOD_HIGH_MULTIPLIER,4)
    }
    proposal={
        "schema":PLAN_SCHEMA,
        "method_source":"MOTIF-016 ridge + fixed 017 gate",
        "algorithm":"TRAIN_FIT_VALIDATION_CHOICE_EVENT_SEALED",
        "windows":{"train":WINDOWS["train"],"validation":WINDOWS["validation"],
                   "event":WINDOWS["event"]},
        "predeclared_event":HISTORIC_EVENT_SOURCE,
        "source_response_sha256":{"train":fingerprint(train_raw),
                                  "validation":fingerprint(validation_raw)},
        "sizes":{"train":len(train),"validation":len(val)},
        "coverage":{"train":train_coverage,"validation":val_coverage},
        "training_flow_median_cfs":round(train_median,4),
        "validation_flow_median_cfs":round(val_median,4),
        "validation_to_train_flow_ratio":round(ratio,4),
        "models":model,
        "validation_mae_cfs":metrics,
        "validation_half_mae_cfs":half_mae,
        "legacy_choice":legacy,
        "cautious_choice":selected,
        "reasons_for_caution":reasons,
        "training_only_out_of_distribution_guard":thresholds,
        "gate_thresholds":{
            "validation_relative_advantage":MIN_VALIDATION_RELATIVE_ADVANTAGE,
            "per_half_advantage":MIN_HALF_ADVANTAGE,
            "allowed_median_flow_ratio":[1/MAX_FLOW_REGIME_MULTIPLIER,MAX_FLOW_REGIME_MULTIPLIER],
            "origin_ood_low_multiplier":OOD_LOW_MULTIPLIER,
            "origin_ood_high_multiplier":OOD_HIGH_MULTIPLIER
        },
        "operator_invention_origin":"Post-MOTIF-016 holdout failure led to predeclared conservative counterpolicy. Not a learned neural model.",
        "source_authentication":"SOURCE_FINGERPRINT_ONLY_NOT_SIGNED",
        "external_effect":False,"automatic_promotion":False,
    }
    return dict(proposal, plan_sha256=fingerprint(proposal))


def validate_frozen(plan):
    require(type(plan) is dict and plan.get("schema")==PLAN_SCHEMA,
            "UNKNOWN_FROZEN_SCHEMA")
    key=plan.get("plan_sha256")
    require(type(key) is str and len(key)==64
            and key==fingerprint({k:v for k,v in plan.items() if k!="plan_sha256"}),
            "FROZEN_PLAN_INTEGRITY_FAIL")
    require(plan.get("windows")=={"train":list(WINDOWS["train"]),
                                  "validation":list(WINDOWS["validation"]),
                                  "event":list(WINDOWS["event"])} or
            plan.get("windows")==WINDOWS, "EVENT_WINDOW_NOT_PREDECLARED")
    require(set(plan.get("models",{}))==set(METHODS) and
            plan["models"]["persistence"] is None, "UNEXPECTED_MODEL_SET")
    require(plan.get("legacy_choice") in METHODS and
            plan.get("cautious_choice") in METHODS, "UNKNOWN_POLICY")
    require(plan.get("gate_thresholds",{}).get("per_half_advantage")==MIN_HALF_ADVANTAGE,
            "MODIFIED_GATE_THRESHOLDS")
    require(plan.get("gate_thresholds",{}).get("validation_relative_advantage")
            ==MIN_VALIDATION_RELATIVE_ADVANTAGE,"MODIFIED_GATE_THRESHOLDS")
    require(plan.get("gate_thresholds",{}).get("origin_ood_low_multiplier")
            ==OOD_LOW_MULTIPLIER,"MODIFIED_GATE_THRESHOLDS")
    require(plan.get("gate_thresholds",{}).get("origin_ood_high_multiplier")
            ==OOD_HIGH_MULTIPLIER,"MODIFIED_GATE_THRESHOLDS")
    require(plan.get("gate_thresholds",{}).get("allowed_median_flow_ratio")
            ==[1/MAX_FLOW_REGIME_MULTIPLIER,MAX_FLOW_REGIME_MULTIPLIER],
            "MODIFIED_GATE_THRESHOLDS")
    require(plan.get("source_response_sha256",{}).keys()=={"train","validation"},
            "SOURCE_PROVENANCE_MISSING")
    require(all(isinstance(v,str) and len(v)==64 and
                all(c in "0123456789abcdef" for c in v)
                for v in plan["source_response_sha256"].values()), "SOURCE_PROVENANCE_MISSING")
    thresholds=plan.get("training_only_out_of_distribution_guard")
    require(type(thresholds) is dict and
            set(thresholds)=={"low_cfs","high_cfs"} and
            0<=thresholds["low_cfs"]<=thresholds["high_cfs"]<10_000_000,
            "INVALID_GUARD_RANGE")
    # Never permit imported objects to cause Python object execution.
    for name in METHODS[1:]:
        model=plan["models"][name]
        fields={"names","mean","scale","weights"}
        require(type(model) is dict and set(model)==fields and
                model["names"]==list(water.FEATURES[name]),
                "MALFORMED_FROZEN_MODEL")
        n=len(model["names"])
        require(all(type(model[k]) is list for k in ("mean","scale","weights"))
                and len(model["mean"])==n and len(model["scale"])==n
                and len(model["weights"])==n+1,
                "MALFORMED_FROZEN_MODEL")
        require(all(type(v) in (int,float) and math.isfinite(v)
                    for k in ("mean","scale","weights") for v in model[k]) and
                all(v>0 for v in model["scale"]), "NONFINITE_FROZEN_MODEL")


def evaluate_frozen(plan,event_raw):
    validate_frozen(plan)
    test,coverage=rows_from(event_raw,"event")
    models=plan["models"]
    t = plan["training_only_out_of_distribution_guard"]
    methods={name:score_policy(test,name,models,t,context="legacy") for name in METHODS}
    legacy=score_policy(test,plan["legacy_choice"],models,t,context="legacy")
    cautious=score_policy(test,plan["cautious_choice"],models,t,context="cautious")
    base=methods["persistence"]
    rises=[x for x in test if x["y"]>=x["known"]*(1+RISING_RELATIVE)
           and x["y"]-x["known"]>=RISING_ABSOLUTE_CFS]
    rise_result=(
        {"count":len(rises),
         "persistence_mae_cfs":score_policy(rises,"persistence",models,t,context="legacy")["mae_cfs"],
         "legacy_mae_cfs":score_policy(rises,plan["legacy_choice"],models,t,context="legacy")["mae_cfs"],
         "cautious_mae_cfs":score_policy(rises,plan["cautious_choice"],models,t,context="cautious")["mae_cfs"]
        } if rises else {"count":0,"persistence_mae_cfs":None,
                          "legacy_mae_cfs":None,"cautious_mae_cfs":None}
    )
    regret=round(legacy["mae_cfs"]-cautious["mae_cfs"],4)
    baseline_improvement=round(base["mae_cfs"]-cautious["mae_cfs"],4)
    # A single selected historical event cannot promote an operator.
    if coverage["complete_hour_coverage"]<.45:
        disposition="HOLD_INSUFFICIENT_EVENT_COVERAGE"
    elif rise_result["count"]<3:
        disposition="HOLD_INSUFFICIENT_RISE_CASES"
    elif regret<=0:
        disposition="HOLD_NO_LEARNING_BENEFIT"
    else:
        disposition="HELD_FOR_DISTINCT_EVENT_REPLICATION"
    event_run={
        "schema":SCHEMA,
        "experiment":"MOTIF-017_LIVING_WATERSHED_EVENT_LEARNING",
        "period":"2024_JUNE_FLOOD_HISTORICAL",
        "fixed_event_source":HISTORIC_EVENT_SOURCE,
        "status":"RETROSPECTIVE_SOURCE_BACKED_REPLAY_NOT_ACTUAL_ISSUED_FORECAST",
        "frozen_plan_sha256":plan["plan_sha256"],
        "plan_frozen_before_event_fetch":"VERIFIED_BY_WORKFLOW_ORDER_NOT_CRYPTOGRAPHIC_TIME_AUTHORITY",
        "event_window":WINDOWS["event"],
        "event_source_snapshot_sha256":fingerprint(event_raw),
        "stations":SITES,
        "complete_hour_coverage":coverage,
        "matched_test_hours":len(test),
        "rising_flow_test":{"definition":{
            "relative_increase":RISING_RELATIVE,
            "minimum_absolute_cfs":RISING_ABSOLUTE_CFS},
            **rise_result},
        "policies_frozen":{
            "legacy_validation_winner":plan["legacy_choice"],
            "cautious_regime_aware":plan["cautious_choice"],
            "cautious_reasons":plan["reasons_for_caution"]
        },
        "all_method_event_mae_cfs":{name:data["mae_cfs"] for name,data in methods.items()},
        "candidate_event_mae_cfs":{
            "persistence":base["mae_cfs"],
            "old_selection":legacy["mae_cfs"],
            "cautious_selection":cautious["mae_cfs"]},
        "origin_ood_fallback_count":cautious["origin_only_fallbacks"],
        "cautious_vs_old_error_reduction_cfs":regret,
        "cautious_vs_persistence_error_reduction_cfs":baseline_improvement,
        "disposition":disposition,
        "peer_research_diagnostics":{
            "MOTIF_to_JARVIS":"A method that wins on one validation block can fail under different physical conditions. Respect sealed event error and sensor availability.",
            "JARVIS_to_MOTIF":"More sensors, routes or code are not proof of better field outcomes. Preserve the transparent persistence control and an ability to abstain.",
            "self_critique":"This preselected 2024 flood is a single historical event. Missing upstream sensors, report-time hindsight, later ratings and a conservative rule invented after 016 failure undermine generalization.",
            "next_experiment":"Choose an entirely different future or independently archived flood event and freeze this policy unchanged before access to target labels."
        },
        "source_limitations":[
            "2024 flood was selected retrospectively from documented historical events; not sampled randomly.",
            "The 2024 Rapidan dam event temporarily disrupted gauge power; missingness is informative and can bias results.",
            "Raw USGS API source captures in run artifact can change if re-fetched after later station revisions.",
            "No original time-of-issue telemetry snapshots, rating curves or independent verification of physical outcomes.",
            "Models calibrated on 2023/early-2024 history, not modern official flood forecast tools.",
            "No stage thresholds, warnings, contacts, evacuation, safety advice or real-world decisions.",
            "A win over a weak historical policy is not proof of generally improved intelligence."
        ],
        "raw_responses_in_ci_artifact":True,
        "source_measurements_are_estimates_not_infallible":True,
        "model_was_trained_on_event":False,
        "test_labels_selected_policy":False,
        "automatic_admission":False,
        "external_action":False,
        "authority":False
    }
    return event_run


def write_json(path,obj):
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=True)+"\n",
                    encoding="utf8")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("phase",choices=("prepare","evaluate"))
    ap.add_argument("--out-dir",type=Path,default=Path("watershed-017-run"))
    ap.add_argument("--offline",action="store_true",help="use existing raw-source JSON captures, no network")
    args=ap.parse_args()
    out=args.out_dir
    try:
        if args.phase=="prepare":
            require(not (out/"frozen-plan.json").exists(),"FROZEN_PLAN_ALREADY_EXISTS")
            if not args.offline:
                out.mkdir(parents=True,exist_ok=True)
            train=(json.loads((out/"train-raw.json").read_text()) if args.offline
                   else download_window("train"))
            val=(json.loads((out/"validation-raw.json").read_text()) if args.offline
                 else download_window("validation"))
            plan=freeze(train,val)
            if not args.offline:
                write_json(out/"train-raw.json",train)
                write_json(out/"validation-raw.json",val)
            write_json(out/"frozen-plan.json",plan)
            print(json.dumps({
                "phase":"PREPARED_NO_EVENT_READ",
                "frozen_plan_sha256":plan["plan_sha256"],
                "legacy_choice":plan["legacy_choice"],
                "cautious_choice":plan["cautious_choice"],
                "validation_mae_cfs":plan["validation_mae_cfs"],
                "caution":plan["reasons_for_caution"]
            },indent=2))
        else:
            plan=json.loads((out/"frozen-plan.json").read_text())
            validate_frozen(plan)
            require(not (out/"result.json").exists(),"RESULT_ALREADY_EXISTS")
            event=(json.loads((out/"event-raw.json").read_text()) if args.offline
                   else download_window("event"))
            result=evaluate_frozen(plan,event)
            if not args.offline:
                write_json(out/"event-raw.json",event)
            write_json(out/"result.json",result)
            print(json.dumps(result,sort_keys=True,indent=2))
        return 0
    except (water.HOLD,ValueError,OSError,TypeError,KeyError,ZeroDivisionError) as exc:
        print("HOLD: "+str(exc)[:170],file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
