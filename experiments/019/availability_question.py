#!/usr/bin/env python3
"""MOTIF-019 — Is asking whether a source can answer worth its cost?

Bounded self-revision: introduce a *new kind of question* (sensor health),
score it against graceful direct querying, freeze on older published records,
then open a distinct later-year holdout. All actions are retrospective
simulations using public USGS data. No real issue-time availability assertion.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timedelta,timezone
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
from statistics import mean
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"016"))
sys.path.insert(0,str(ROOT/"018"))
import watershed as water
import question_loop as q18

SCHEMA="motif.question-about-questions/v1"
PLAN_SCHEMA="motif.question-kind-policy/v1"
RESULT_SCHEMA="motif.question-kind-physical-test/v1"
WINDOWS={
    "train":("2023-05-04","2023-05-13"),
    "develop":("2025-09-12","2025-09-22"),  # previously inspected during MOTIF-018
    "holdout":("2026-03-01","2026-03-14"), # source-locked BEFORE first test fetch
}
SITES=dict(water.SITES)
HORIZON=7
HISTORY=6
MIN_DOWNSTREAM=72
MAX_ROWS=600
MAX_FEATURES=1800
PROBE_CREDIT=0.2 # cheaper, but NOT free
REQUEST_CREDIT=1.0
COST_FRACTION_OF_TRAIN_BASELINE=0.08
# These are hypotheses about research utility. Not economic/safety valuations.
RULES=(
 ("Q0","Does the extra information improve MAE when questions are free?",
  ("downstream","sueur_only","both_graceful"),(0.,0.,0.,0.)),
 ("Q1","Should every requested source consume an observation credit?",
  ("downstream","sueur_only","both_graceful"),(1.,0.,0.,0.)),
 ("Q2","Should asking a silent sensor incur a further cost?",
  ("downstream","sueur_only","both_graceful"),(1.,2.,0.,0.)),
 ("Q3","Is querying on demand better when the local river actually changes?",
  ("downstream","sueur_only","both_graceful","trend_gate_2pct"),(1.,2.,0.20,0.)),
 ("Q4","Could prior station health be itself a cheap question?",
  ("downstream","sueur_only","both_graceful","trend_gate_2pct",
   "health_last1","health_last3","health_last6"),(1.,2.,0.20,0.)),
 ("Q5","Could a health signal be misleading despite being cheaper to ask?",
  ("downstream","sueur_only","both_graceful","trend_gate_2pct",
   "health_last1","health_last3","health_last6"),(1.,2.,0.20,1.)),
)
POSSIBLE_POLICIES=("downstream","sueur_only","both_graceful",
                   "trend_gate_2pct","health_last1","health_last3","health_last6")
HEALTH_LENGTH={"health_last1":(1,1),"health_last3":(3,2),"health_last6":(6,3)}

class HOLD(water.HOLD):pass

def require(ok,code):
    if not ok:raise HOLD(code)

def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                            ensure_ascii=True).encode("utf8")).hexdigest()

def collect(name):
    require(name in WINDOWS,"NO_ARBITRARY_DATE_WINDOW")
    start,end=WINDOWS[name]
    result={}
    for sensor,site in SITES.items():
        qs=urlencode({"monitoring_location_id":site,"parameter_code":"00060",
                      "datetime":start+"/"+end,"f":"json","limit":str(MAX_FEATURES)})
        result[sensor]=water.request_json(water.USGS+"?"+qs)
    return result

def make_rows(raw,name):
    require(name in WINDOWS and type(raw) is dict and set(raw)==set(SITES),
            "BAD_SOURCE_ENVELOPE")
    # Original Mankato gauge must have genuine target, origin and past rows.
    d={"mankato":water.gauges(raw["mankato"],"mankato")}
    # Missing upstream is NOT missing downstream. Keep the full denominator.
    d["sueur"]=q18.optional_upstream_gauge(raw["sueur"],"sueur")
    d["blue"]=q18.optional_upstream_gauge(raw["blue"],"blue")
    start=datetime.fromisoformat(WINDOWS[name][0]).replace(tzinfo=timezone.utc)
    end=datetime.fromisoformat(WINDOWS[name][1]).replace(tzinfo=timezone.utc)+timedelta(days=1)
    result=[]
    for target in sorted(d["mankato"]):
        origin=target-timedelta(hours=HORIZON)
        prev=origin-timedelta(hours=HISTORY)
        if not(start<=target<end and origin in d["mankato"] and prev in d["mankato"]):
            continue
        row={
            "target_utc":target.isoformat().replace("+00:00","Z"),
            "y":d["mankato"][target],
            "known":d["mankato"][origin],
            "local_delta":d["mankato"][origin]-d["mankato"][prev],
        }
        for sensor in ("sueur","blue"):
            row[sensor+"_delta"]=(
                d[sensor][origin]-d[sensor][prev]
                if origin in d[sensor] and prev in d[sensor] else None)
        # Presence is a historical timestamp-completeness PROXY, not what the
        # station would have reported in real time.
        for n in (1,3,6):
            row["blue_historic_present_last"+str(n)]=sum(
                origin-timedelta(hours=i) in d["blue"] for i in range(1,n+1))
        result.append(row)
    require(MIN_DOWNSTREAM<=len(result)<=MAX_ROWS,
            "INSUFFICIENT_OR_OVERSIZED_DOWNSTREAM_CASES")
    return result,{
        "complete_downstream_hours":len(result),
        "upstream_present_feature_hours":{
            "blue":sum(x["blue_delta"] is not None for x in result),
            "sueur":sum(x["sueur_delta"] is not None for x in result),
        },
        "complete_both_hours":sum(
            x["blue_delta"] is not None and x["sueur_delta"] is not None
            for x in result),
        "period_start_utc":result[0]["target_utc"],
        "period_end_utc":result[-1]["target_utc"],
    }

def fit(train):
    bank={"downstream":None}
    specs={
      "sueur":("local_delta","sueur_delta"),
      "blue":("local_delta","blue_delta"),
      "both":("local_delta","sueur_delta","blue_delta")
    }
    for name,cols in specs.items():
        eligible=[r for r in train if all(r[k] is not None for k in cols)]
        require(len(eligible)>=45, "INSUFFICIENT_MODEL_TRAINING_"+name.upper())
        bank[name]=water.fit_ridge(eligible,cols)
    return bank

def step_action(row,policy):
    """Return request decisions without ever inspecting future target y."""
    if policy=="downstream":
        return False,False,0.,False
    if policy=="sueur_only":
        return True,False,0.,False
    if policy=="both_graceful":
        return True,True,0.,False
    if policy=="trend_gate_2pct":
        request_blue=abs(row["local_delta"])/max(1,row["known"])>=.02
        return True,request_blue,0.,False
    if policy in HEALTH_LENGTH:
        n,threshold=HEALTH_LENGTH[policy]
        # History only earlier than origin, never the target or origin itself.
        # Health can be stale; its historic availability != real-time reported.
        prediction=row["blue_historic_present_last"+str(n)]>=threshold
        return True,prediction,PROBE_CREDIT, prediction and row["blue_delta"] is None
    raise HOLD("UNDEFINED_RESEARCH_QUESTION")

def simulate_one(row,policy,bank):
    ask_sueur,ask_blue,probe,false_health=step_action(row,policy)
    sueur_found=ask_sueur and row["sueur_delta"] is not None
    blue_found=ask_blue and row["blue_delta"] is not None
    if sueur_found and blue_found:
        model=bank["both"]
    elif sueur_found:
        model=bank["sueur"]
    elif blue_found:
        model=bank["blue"]
    else:
        model=bank["downstream"]
    pred=water.predict(row,model)
    request_count=int(ask_sueur)+int(ask_blue)
    silent=int(ask_sueur and not sueur_found)+int(ask_blue and not blue_found)
    return {"error":abs(row["y"]-pred),
            "requests":request_count,"silent":silent,
            "probe_credit":probe,"false_health":int(false_health),
            "uses_model":(
               "both" if sueur_found and blue_found else
               "sueur" if sueur_found else "blue" if blue_found else "downstream"
            )}

def metric(rows,policy,bank,unit,weights):
    outcomes=[simulate_one(r,policy,bank) for r in rows]
    n=len(rows)
    a,b=outcomes[:n//2],outcomes[n//2:]
    error=mean(o["error"] for o in outcomes)
    half1=mean(o["error"] for o in a)
    half2=mean(o["error"] for o in b)
    requests=sum(o["requests"] for o in outcomes)
    silent=sum(o["silent"] for o in outcomes)
    probes=sum(o["probe_credit"] for o in outcomes)
    wrong_health=sum(o["false_health"] for o in outcomes)
    inquiry_price=weights[0]*unit*(requests+probes)/n
    unanswered_penalty=weights[1]*unit*silent/n
    instability_penalty=weights[2]*abs(half1-half2)
    stale_health_penalty=weights[3]*unit*wrong_health/n
    return {
        "absolute_error_mae_cfs":round(error,4),
        "inquiry_credits_per_hour":round((requests+probes)/n,5),
        "unanswered_queries":silent,
        "probe_credits_total":round(probes,5),
        "false_positive_health_probes":wrong_health,
        "first_half_mae_cfs":round(half1,4),
        "second_half_mae_cfs":round(half2,4),
        "temporal_instability_cfs":round(abs(half1-half2),4),
        "weighted_objective_cfs_equivalent":round(
            error+inquiry_price+unanswered_penalty+
            instability_penalty+stale_health_penalty,4),
        "count":n,
        "request_count":requests,
        "effective_model_counts":{
            k:sum(o["uses_model"]==k for o in outcomes)
            for k in ("downstream","sueur","blue","both")
        }
    }

def develop(train_raw,dev_raw):
    training,train_coverage=make_rows(train_raw,"train")
    development,dev_coverage=make_rows(dev_raw,"develop")
    bank=fit(training)
    training_base=mean(abs(x["y"]-x["known"]) for x in training)
    price=training_base*COST_FRACTION_OF_TRAIN_BASELINE
    require(price>0,"ZERO_TRAIN_PRICE")
    previous=None
    steps=[]
    for i,(stage,question,options,weights) in enumerate(RULES):
        scores={name:metric(development,name,bank,price,weights)
                for name in options}
        # On equal scored objective, prefer fewer probes and fewer sensors.
        choice=min(options,key=lambda name:(
            scores[name]["weighted_objective_cfs_equivalent"],
            scores[name]["inquiry_credits_per_hour"],
            POSSIBLE_POLICIES.index(name)))
        base=scores["downstream"]["weighted_objective_cfs_equivalent"]
        steps.append({
            "iteration":i,"stage":stage,
            "question_reformulation":question,
            "new_question_kind_introduced":("source_health" if stage=="Q4" else
               "false_health_cost" if stage=="Q5" else
               "conditional_measurement" if stage=="Q3" else None),
            "predeclared_utility_weights":{
                "request":weights[0],"missing":weights[1],
                "temporal_instability":weights[2],
                "false_health":weights[3]
            },
            "candidate_question_scores":scores,
            "selected_question_policy":choice,
            "changed_policy":previous is not None and previous!=choice,
            "same_objective_difference_vs_baseline":round(
                base-scores[choice]["weighted_objective_cfs_equivalent"],4),
            "holdout_labels_seen":False,
            "code_mutated_during_execution":False,
            "next_discriminating_question":(
               "Does this question rule still outperform the same baseline "
               "on the unrevealed March 2026 physical observations?")
        })
        previous=choice
    data={
        "schema":PLAN_SCHEMA,
        "protocol":SCHEMA,
        "research_problem":"Is a cheap source-availability question worth its observation and delay costs?",
        "windows":WINDOWS,
        "fixed_source_sites":SITES,
        "training_sha256":digest(train_raw),
        "development_sha256":digest(dev_raw),
        "training_coverage":train_coverage,
        "development_coverage":dev_coverage,
        "train_baseline_mae_cfs":round(training_base,6),
        "observation_credit_unit_cfs_equivalent":round(price,6),
        "probe_credit_fraction_of_request":PROBE_CREDIT,
        "probe_meaning":"HISTORICAL_GAUGE_TIMESTAMP_PRESENCE_PROXY_NOT_ISSUED_TIME_HEALTH",
        "bank":bank,
        "stages":steps,
        "selected_policy":previous,
        "allowed_policies":list(POSSIBLE_POLICIES),
        "holdout_was_not_read":True,
        "auto_modify_source":False,"auto_promote_model":False,
        "external_action":False,
    }
    return dict(data,plan_sha256=digest(data))

def verify(plan):
    require(type(plan) is dict and plan.get("schema")==PLAN_SCHEMA,
            "BAD_POLICY_PLAN_SCHEMA")
    seal=plan.get("plan_sha256")
    require(type(seal) is str and seal==digest(
        {k:v for k,v in plan.items() if k!="plan_sha256"}),"FAILED_POLICY_SEAL")
    expected={k:list(v) for k,v in WINDOWS.items()}
    require(plan.get("windows")==expected or plan.get("windows")==WINDOWS,
            "UNLISTED_SOURCE_WINDOWS")
    require(plan.get("fixed_source_sites")==SITES,"CHANGED_SOURCE_IDENTITIES")
    require(plan.get("allowed_policies")==list(POSSIBLE_POLICIES),
            "RULE_GRAMMAR_CHANGED")
    require(plan.get("holdout_was_not_read") is True and
            plan.get("auto_modify_source") is False and
            plan.get("auto_promote_model") is False and
            plan.get("external_action") is False,
            "CHANGED_BOUNDARY_PERMISSIONS")
    steps=plan.get("stages")
    require(type(steps) is list and len(steps)==len(RULES),"WRONG_LOOP_SIZE")
    for i,(step,template) in enumerate(zip(steps,RULES)):
        stage,question,options,weights=template
        require(type(step) is dict and step.get("iteration")==i and
                step.get("stage")==stage and
                step.get("question_reformulation")==question and
                step.get("holdout_labels_seen") is False and
                step.get("code_mutated_during_execution") is False and
                step.get("predeclared_utility_weights")=={
                    "request":weights[0],"missing":weights[1],
                    "temporal_instability":weights[2],
                    "false_health":weights[3]} and
                set(step.get("candidate_question_scores",{}))==set(options) and
                step.get("selected_question_policy") in options,
                "FROZEN_REVISION_CONTRACT_CHANGED")
        # Even a re-signed plan cannot change declared selection after reading
        # target labels: candidate scores were calculated in old-data stage.
        ranks=step["candidate_question_scores"]
        require(all(type(value) is dict and
                    math.isfinite(value.get("weighted_objective_cfs_equivalent",float("nan")))
                    and math.isfinite(value.get("inquiry_credits_per_hour",float("nan")))
                    for value in ranks.values()),"BAD_DEVELOPMENT_METRICS")
        check=min(options,key=lambda name:(
            ranks[name]["weighted_objective_cfs_equivalent"],
            ranks[name]["inquiry_credits_per_hour"],
            POSSIBLE_POLICIES.index(name)))
        require(check==step["selected_question_policy"],"SELECTED_BEHIND_METRICS")
    require(plan.get("selected_policy")==steps[-1]["selected_question_policy"],
            "POLICY_CHANGED_AFTER_FREEZE")
    require(type(plan.get("observation_credit_unit_cfs_equivalent")) in (int,float)
            and math.isfinite(plan["observation_credit_unit_cfs_equivalent"])
            and plan["observation_credit_unit_cfs_equivalent"]>0,
            "UNSAFE_COST_SCHEME")
    bank=plan.get("bank")
    expected_models={
        "downstream":None,"sueur":("local_delta","sueur_delta"),
        "blue":("local_delta","blue_delta"),
        "both":("local_delta","sueur_delta","blue_delta")}
    require(type(bank) is dict and set(bank)==set(expected_models)
            and bank["downstream"] is None,"BAD_FROZEN_MODELS")
    for name,columns in expected_models.items():
        if name=="downstream":continue
        model=bank[name]
        require(type(model) is dict and
                set(model)=={"names","mean","scale","weights"} and
                model.get("names")==list(columns) and
                all(type(model.get(k)) is list for k in ("mean","scale","weights")) and
                len(model["mean"])==len(columns) and
                len(model["scale"])==len(columns) and
                len(model["weights"])==len(columns)+1 and
                all(type(v) in (float,int) and math.isfinite(v)
                    for k in ("mean","scale","weights") for v in model[k]) and
                all(v>0 for v in model["scale"]),
                "UNSAFE_STORED_MODEL")
    return True

def test_frozen(plan,unseen_raw):
    verify(plan)
    cases,coverage=make_rows(unseen_raw,"holdout")
    bank=plan["bank"]
    weights=tuple(RULES[-1][-1])
    unit=plan["observation_credit_unit_cfs_equivalent"]
    # Report all post-test alternatives; they may inform an entirely NEW
    # hypothesis but are not authorized to replace the frozen selected policy.
    results={policy:metric(cases,policy,bank,unit,weights)
             for policy in POSSIBLE_POLICIES}
    selected=plan["selected_policy"]
    base=results["downstream"]
    chosen=results[selected]
    by_objective=min(POSSIBLE_POLICIES,key=lambda name:(
        results[name]["weighted_objective_cfs_equivalent"],
        results[name]["inquiry_credits_per_hour"],
        POSSIBLE_POLICIES.index(name)))
    savings=round(base["weighted_objective_cfs_equivalent"]-
                  chosen["weighted_objective_cfs_equivalent"],4)
    raw_gain=round(base["absolute_error_mae_cfs"]-
                   chosen["absolute_error_mae_cfs"],4)
    saw_probes=selected in HEALTH_LENGTH
    if savings<=0 or raw_gain<=0:
        verdict="HOLD_NO_INDEPENDENT_QUESTION_VALUE"
    elif chosen["unanswered_queries"]>max(1,chosen["request_count"]*.2):
        verdict="HOLD_HIGH_UNANSWERED_QUERY_RATE"
    else:
        verdict="HELD_REPLICATE_BEFORE_ADMISSION"
    if by_objective!=selected:
        next_question=(
            "What changed between 2025 and 2026 that made "+
            by_objective+" more valuable than the frozen "+selected+
            " question, and can we predict that change without seeing target labels?")
    elif saw_probes:
        next_question=(
            "Does the historical last-hours gauge-presence signal actually "
            "predict real issue-time response availability, delay, and cost?")
    else:
        next_question=(
            "Is checking a source's health itself worth its credit "
            "compared with graceful fallback when the source is silent?")
    return {
        "schema":RESULT_SCHEMA,
        "source_type":"USGS_MODERN_OGC_HISTORICAL_REPORTED_DISCHARGE",
        "status":"PUBLIC_SENSOR_RETROSPECTIVE_COMPARISON_NO_ACTUAL_FORECAST_ISSUED",
        "fixed_frozen_plan_sha256":plan["plan_sha256"],
        "holdout_source_response_sha256":digest(unseen_raw),
        "test_window":WINDOWS["holdout"],
        "downstream_complete_case_population":coverage,
        "frozen_selection":selected,
        "baseline_mae_cfs":base["absolute_error_mae_cfs"],
        "frozen_policy_mae_cfs":chosen["absolute_error_mae_cfs"],
        "frozen_policy_raw_mae_improvement_cfs":raw_gain,
        "frozen_policy_utility_improvement_cfs_equivalent":savings,
        "all_declared_policy_results_POSTHOC_DO_NOT_SELECT":results,
        "posthoc_best_from_opened_holdout_NOT_ADMITTED":by_objective,
        "whether_historical_health_probe_selected":saw_probes,
        "proposed_next_question":next_question,
        "hypothesis_state":verdict,
        "reciprocal_critique":{
          "MOTIF_to_JARVIS":"An answer's value includes whether the measuring instrument answered, at what apparent cost, and whether the question stays predictive across regimes.",
          "JARVIS_to_MOTIF":"A historical timestamp found today is not proof that the agency answered at the original hypothetical query time. The availability question itself could be wrong.",
          "self_doubt":"Were research credit prices or historical response completeness better predictors of the selected question than physically measured forecast error?",
          "next_method":"Use actual time-of-issue request/response metadata, event-block holdouts, and health-probe cost measured in seconds or money."
        },
        "limits":[
          "The 2025 development source was previously inspected by 018; no pretense of untouched development data.",
          "The 2026 March test window was fixed in source before its live source query.",
          "Probed source health is derived from hindsight historical time stamps, not true live-availability receipts.",
          "No evidence that reported discharge estimates, later revised ratings, or missing sensor records equal contemporaneous physical truth.",
          "No real monetary costs, real network delay, flood decisions or operational alerts; credits are declared research proxies.",
          "All posthoc policy comparisons are diagnostic only; selecting the posthoc best would invalidate the 2026 holdout."
        ],
        "observed_future_labels_used_to_modify_policy":False,
        "sensor_health_really_queried_at_issue_time":False,
        "actual_2026_forecasts_issued":False,
        "autonomous_code_modification":False,
        "automatic_admission":False,"real_world_action":False,
        "authority":False
    }

def write(path,value):
    path.write_text(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True)+"\n",encoding="utf8")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("phase",choices=("evolve","confront"))
    parser.add_argument("--out-dir",type=Path,default=Path("question019-evidence"))
    parser.add_argument("--offline",action="store_true")
    args=parser.parse_args()
    out=args.out_dir
    try:
        if args.phase=="evolve":
            require(not (out/"frozen-plan.json").exists(),"REFUSE_OVERWRITE_FROZEN")
            if not args.offline:out.mkdir(parents=True,exist_ok=True)
            train=(json.loads((out/"train-raw.json").read_text()) if args.offline
                   else collect("train"))
            dev=(json.loads((out/"develop-raw.json").read_text()) if args.offline
                 else collect("develop"))
            proposal=develop(train,dev)
            if not args.offline:
                write(out/"train-raw.json",train)
                write(out/"develop-raw.json",dev)
            write(out/"frozen-plan.json",proposal)
            print(json.dumps({
                "phase":"EVOLVED_RESEARCH_QUESTIONS_BEFORE_HELDOUT",
                "plan_sha256":proposal["plan_sha256"],
                "selected":proposal["selected_policy"],
                "stages":[{
                    "stage":s["stage"],
                    "new_kind":s["new_question_kind_introduced"],
                    "selected":s["selected_question_policy"],
                    "policy_changed":s["changed_policy"],
                    "difference_vs_same_baseline":s["same_objective_difference_vs_baseline"]
                }for s in proposal["stages"]],
                "holdout_seen":False
            },indent=2))
        else:
            frozen=json.loads((out/"frozen-plan.json").read_text())
            verify(frozen)
            require(not (out/"result.json").exists(),"REFUSE_OVERWRITE_RESULT")
            test=(json.loads((out/"holdout-raw.json").read_text()) if args.offline
                  else collect("holdout"))
            report=test_frozen(frozen,test)
            if not args.offline:write(out/"holdout-raw.json",test)
            write(out/"result.json",report)
            print(json.dumps(report,indent=2,sort_keys=True))
        return 0
    except (ValueError,TypeError,KeyError,OSError,ZeroDivisionError) as exc:
        print("HOLD: "+str(exc)[:170],file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
