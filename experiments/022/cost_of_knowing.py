#!/usr/bin/env python3
"""MOTIF-022 — THE COST OF KNOWING, in actual units and explicit goals.

A source-pinned, read-only interrogation of GHoT-004's four ACTUALLY
EXECUTED USGS inquiry arms. No fictitious credits or inferred electricity.
It discovers when another inquiry can STILL complete a defined evidence
contract, and refuses to call over-questioning useful or valueless universally.
"""
from __future__ import annotations
from datetime import datetime, timezone,timedelta
from hashlib import sha1,sha256
import argparse
import json
import math
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
import sys

SCHEMA="motif.cost-of-knowing/v1"
SOURCE_SCHEMA="ghot.goal-aware-inquiry/v1"
GHOT_COMMIT="f6a36f5c9d8b567a69ead04ccf7641cba338a7f3"
GHOT_GIT_BLOB="ee545add1b71f97eb3fae2e5151398f81814a89b"
FIXED_SOURCE=Path(__file__).resolve().parent/"evidence"/"ghot-004-actual-2026-11-05.json"
GOALS={
 "any_fresh":{"kind":"any_of","required":["blue","sueur","mankato"],
              "plan":["blue","sueur","mankato"]},
 "two_named_fresh":{"kind":"all_of","required":["blue","sueur"],
                    "plan":["blue","sueur"]},
}
CONTROL=["blue","sueur","mankato"]
TRIAL_ORDER=[("any_fresh","goal_aware"),("any_fresh","exhaustive"),
             ("two_named_fresh","exhaustive"),("two_named_fresh","goal_aware")]
STATIONS={"blue":"USGS-05320000","sueur":"USGS-05320500","mankato":"USGS-05325000"}
BASE_URL="https://api.waterdata.usgs.gov/ogcapi/v1/collections/continuous/items"
MAX_AGE_SECONDS=12*3600
FIELDS=("actual_get_requests","http_response_body_bytes","sum_request_wall_ns",
        "sum_request_local_cpu_ns")

class HOLD(ValueError):pass
def require(ok,code):
 if not ok:raise HOLD(code)
def iso(s):
 require(isinstance(s,str) and len(s)<80,"INVALID_UTC_CLOCK")
 try:d=datetime.fromisoformat(s.replace("Z","+00:00"))
 except ValueError as ex:raise HOLD("INVALID_UTC_CLOCK") from ex
 require(d.tzinfo is not None,"NAIVE_CLOCK")
 return d.astimezone(timezone.utc)
def number(x):
 require(type(x) in (int,float) and math.isfinite(x) and x>=0,
         "UNVERIFIED_OR_NEGATIVE_RESOURCE_MEASUREMENT")
 return x
def gitblob(x):
 return sha1(b"blob "+str(len(x)).encode()+bytes([0])+x).hexdigest()

def load(source=FIXED_SOURCE):
 require(isinstance(source,Path) and source.is_file() and
         not source.is_symlink() and 0<source.stat().st_size<80000,
         "UNKNOWN_OWNER_SOURCE")
 raw=source.read_bytes()
 require(gitblob(raw)==GHOT_GIT_BLOB,"SOURCE_OWNED_GHOT_BLOB_CHANGED")
 try:return json.loads(raw)
 except (UnicodeError,ValueError) as ex:raise HOLD("GHOT_SOURCE_NOT_JSON") from ex

def validate_source_url(url,site):
 require(isinstance(url,str) and len(url)<800,"NON_PUBLIC_SOURCE_REQUEST")
 p=urlsplit(url)
 require(p.scheme=="https" and p.netloc=="api.waterdata.usgs.gov" and
         p.path=="/ogcapi/v1/collections/continuous/items" and
         not p.fragment and not p.username and not p.password,
         "UNAPPROVED_QUERY_DESTINATION")
 q=parse_qs(p.query,strict_parsing=True)
 require(set(q)=={"monitoring_location_id","parameter_code","datetime","limit","f"} and
         all(len(v)==1 for v in q.values()) and
         q["monitoring_location_id"]==[STATIONS[site]] and
         q["parameter_code"]==["00060"] and q["limit"]==["700"] and
         q["f"]==["json"],"WRONG_STATION_OR_PARAMETER")
 parts=q["datetime"][0].split("/")
 require(len(parts)==2 and all("T" in x and x.endswith("Z") for x in parts),
         "QUESTION_LOST_TIME_WINDOW_AGAIN")
 require(0<(iso(parts[1])-iso(parts[0])).total_seconds()<=96*3600,
         "INVALID_SOURCE_TIME_RANGE")
 return q["datetime"][0]

def available(r):
 if r.get("valid_source_response") is not True:return False
 o=r.get("observation")
 return type(o) is dict and o.get("fresh_source_witness") is True

def satisfied(goal,seen):
 g=GOALS[goal]
 fresh={r["site"] for r in seen if available(r)}
 if g["kind"]=="any_of":return bool(fresh&set(g["required"]))
 return set(g["required"])<=fresh

def future_useful(goal,seen,remaining):
 if satisfied(goal,seen):return False
 g=GOALS[goal]
 fresh={r["site"] for r in seen if available(r)}
 if g["kind"]=="any_of":return bool(set(remaining)&set(g["required"]))
 return set(g["required"])<=(fresh|set(remaining))

def check_trial(t,goal,policy):
 g=GOALS[goal]
 require(type(t) is dict and t.get("schema")=="ghot.goal-trial/v1" and
         t.get("goal")==goal and t.get("policy")==policy and
         t.get("contract_kind")==g["kind"] and
         t.get("required_public_stations")==g["required"] and
         t.get("no_monetary_or_api_credit_costs") is True and
         t.get("no_emergency_action") is True and
         t.get("authority") is False,
         "GHOT_OWNER_CONTRACT_MISMATCH")
 plan=g["plan"] if policy=="goal_aware" else CONTROL
 require(t.get("predeclared_route")==plan,"QUESTIONS_NOT_PREDECLARED")
 received=t.get("per_request_receipts")
 steps=t.get("actual_steps")
 require(type(received) is list and type(steps) is list and
         len(received)==len(steps) and 1<=len(received)<=len(plan),
         "INCOMPLETE_OR_EXTRA_PHYSICAL_REQUESTS")
 requested=[r.get("site") for r in received]
 require(requested==plan[:len(received)] and
         t.get("actually_queried_public_sites")==requested and
         t.get("skipped_public_sites")==[s for s in CONTROL if s not in requested],
         "SOURCE_TASK_ROUTE_CHANGED")
 trace=[]
 for i,(r,step) in enumerate(zip(received,steps)):
  site=requested[i]
  require(type(r) is dict and r.get("kind")=="ghot.source-probe/v1" and
          type(r.get("valid_source_response")) is bool and
          r.get("wire_network_bytes_total") is None and
          step.get("schema")=="ghot.goal-step/v1" and
          step.get("step")==i and
          step.get("actual_site_requested")==site,
          "RECEIPT_NOT_PHYSICAL_HTTP_SOURCE")
  number(r.get("latency_wall_ns"))
  number(r.get("local_cpu_ns"))
  number(r.get("body_bytes_received"))
  require(r.get("body_bytes_received")<=1500000 and
          r.get("latency_wall_ns")<=20000000000 and
          r.get("http_status") in (None,200,400,403,404,408,429,500,502,503,504),
          "UNBOUNDED_PUBLIC_QUERY")
  url=step.get("public_request_url")
  validate_source_url(url,site)
  require(step.get("request_url_sha256")==sha256(url.encode()).hexdigest(),
          "TAMPERED_PUBLIC_REQUEST_ENCODING")
  require(iso(r["request_start_utc"])<=iso(r["response_end_utc"])+timedelta(seconds=1),
          "IMPOSSIBLE_HTTP_TIME_ORDER")
  if available(r):
   o=r["observation"]
   require(o.get("station")==site and
           type(o.get("latest_flow_cfs")) in (int,float) and
           0<=o["latest_flow_cfs"]<10000000 and
           type(o.get("latest_observation_utc")) is str and
           -300<=(iso(r["response_end_utc"])-iso(o["latest_observation_utc"])).total_seconds()<=MAX_AGE_SECONDS+300,
           "UNREALISTIC_REPORTED_DATA_FRESHNESS")
  elif r["valid_source_response"]:
   require(type(r.get("observation")) is dict and
           r["observation"].get("fresh_source_witness") is False,
           "HIDDEN_REPORT_MISSING_OR_WRONG")
  prefix=received[:i+1]
  ok=satisfied(goal,prefix)
  rest=plan[i+1:]
  can= future_useful(goal,prefix,rest)
  if policy=="goal_aware":
   intended=("STOP_GOAL_MET" if ok else
      "HOLD_GOAL_UNREACHABLE_WITH_ALLOWED_SOURCES" if not can else
      "ASK_NEXT_POSSIBLY_USEFUL_SOURCE")
  else:intended=("FINISH_CONTROL_AFTER_ALL_SOURCES" if not rest else
                 "CONTROL_ASK_EXTRA_EVEN_IF_GOAL_MET")
  require(step.get("original_goal_satisfied_after_this_step") is ok and
          step.get("decision")==intended and
          step.get("still_possible_to_finish")==can and
          step.get("this_source_was_fresh")==available(r) and
          step.get("received_http_body_bytes")==r["body_bytes_received"] and
          step.get("measured_wall_ns")==r["latency_wall_ns"],
          "RESEARCH_STEP_DECISION_NOT_EXPLAINED")
  trace.append({
   "public_source":site,"goal_was_satisfied":ok,
   "is_another_question_capable_of_completing_original_goal":can,
   "next_decision":intended,
   "actual_http_payload_bytes":r["body_bytes_received"],
   "actual_http_request_wall_ns":r["latency_wall_ns"],
  })
  if policy=="goal_aware" and intended!="ASK_NEXT_POSSIBLY_USEFUL_SOURCE":
   require(i==len(received)-1,"QUERIED_AFTER_DECLARED_STOP")
  if policy=="goal_aware" and intended=="ASK_NEXT_POSSIBLY_USEFUL_SOURCE":
   require(i<len(received)-1,"FAILED_TO_ASK_NECESSARY_NEXT_SOURCE")
 require(len(received)==len(CONTROL) if policy=="exhaustive" else
         trace[-1]["next_decision"]!="ASK_NEXT_POSSIBLY_USEFUL_SOURCE",
         "INCOMPLETE_EXHAUSTIVE_OR_GOAL_ROUTE")
 unit=t.get("actual_resource_units")
 require(type(unit) is dict and
         unit.get("wire_bytes") is None and
         unit.get("attributable_joules") is None and
         unit.get("actual_get_requests")==len(received) and
         unit.get("http_response_body_bytes")==sum(r["body_bytes_received"] for r in received) and
         unit.get("sum_request_wall_ns")==sum(r["latency_wall_ns"] for r in received) and
         unit.get("sum_request_local_cpu_ns")==sum(r["local_cpu_ns"] for r in received) and
         t.get("task_contract_completed") is satisfied(goal,received),
         "INVENTED_RESOURCE_SAVINGS_OR_FALSE_TASK_COMPLETION")
 require(t.get("stop_reason")==(
         trace[-1]["next_decision"] if policy=="goal_aware" else "CONTROL_ALL_THREE_COMPLETED"),
         "MISLABELED_REASON_FOR_STOPPING")
 return trace

def inspect(d):
 require(type(d) is dict and d.get("schema")==SOURCE_SCHEMA and
         d.get("source_host")=="api.waterdata.usgs.gov" and
         d.get("actual_energy_joules") is None and
         d.get("actual_wire_bytes") is None and
         d.get("no_paid_credits_needed") is True and
         d.get("outcome_research_hold")=="NO_CROSS_RUN_CAUSAL_ENERGY_CLAIM" and
         d.get("external_side_effects_other_than_readonly_public_GET") is False and
         d.get("source_code_autonomously_modified") is False and
         d.get("automatic_model_promotion") is False and
         d.get("authority") is False,
         "PHYSICAL_RESEARCH_DID_NOT_KEEP_BOUNDARIES")
 trials=d.get("actually_executed_trials")
 require(type(trials) is list and len(trials)==len(TRIAL_ORDER) and
         d.get("run_order")==[list(x) for x in TRIAL_ORDER],
         "TRIALS_NOT_PREDECLARED_OR_MUTATED")
 require(d.get("power_willingness") in ("abundant","normal","conserve","critical"),
         "POWER_CONTEXT_NOT_REPORTED")
 traces={}
 for t,(goal,policy) in zip(trials,TRIAL_ORDER):
  traces[goal+"/"+policy]=check_trial(t,goal,policy)
 require(d["actual_network_requests_sent"]==sum(
             t["actual_resource_units"]["actual_get_requests"] for t in trials) and
         d["actual_http_response_body_bytes"]==sum(
             t["actual_resource_units"]["http_response_body_bytes"] for t in trials) and
         d["actual_request_wall_time_ns_sum"]==sum(
             t["actual_resource_units"]["sum_request_wall_ns"] for t in trials),
         "GRAND_RESOURCE_TOTALS_CANNOT_BE_REPRODUCED")
 comparisons={}
 for goal in GOALS:
  aware=next(t for t in trials if t["goal"]==goal and t["policy"]=="goal_aware")
  baseline=next(t for t in trials if t["goal"]==goal and t["policy"]=="exhaustive")
  a,b=aware["actual_resource_units"],baseline["actual_resource_units"]
  outcome=d.get("two_goal_comparisons",{}).get(goal,{})
  require(outcome.get("optimized_goal_satisfied") is aware["task_contract_completed"] and
          outcome.get("control_goal_satisfied") is baseline["task_contract_completed"] and
          outcome.get("actual_optimized_get_count")==a["actual_get_requests"] and
          outcome.get("actual_control_get_count")==b["actual_get_requests"] and
          outcome.get("actual_optimized_body_bytes")==a["http_response_body_bytes"] and
          outcome.get("actual_control_body_bytes")==b["http_response_body_bytes"] and
          outcome.get("comparison_can_prove_general_causal_savings") is False and
          outcome.get("comparison_can_prove_electrical_savings") is False,
          "PAIRED_GOAL_UNRELIABLE")
  both_finished=aware["task_contract_completed"] and baseline["task_contract_completed"]
  # Multiple independent physical resource dimensions: never combine into
  # a scalar fictional credit price or call measured CPU nanoseconds Joules.
  resource_differences={
   "number_of_real_requests":b["actual_get_requests"]-a["actual_get_requests"],
   "http_body_bytes":b["http_response_body_bytes"]-a["http_response_body_bytes"],
   "request_wall_nanoseconds":b["sum_request_wall_ns"]-a["sum_request_wall_ns"],
   "local_request_cpu_nanoseconds":b["sum_request_local_cpu_ns"]-a["sum_request_local_cpu_ns"]
  }
  dominated=both_finished and all(x>=0 for x in resource_differences.values()) and any(
               x>0 for x in resource_differences.values())
  comparisons[goal]={
   "contract_completed_in_both_actual_trials":both_finished,
   "optimized_real_requests":a["actual_get_requests"],
   "exhaustive_real_requests":b["actual_get_requests"],
   "observed_resource_differences_exhaustive_minus_goal_aware":resource_differences,
   "goal_aware_observed_non_worse_on_all_measured_dimensions":dominated,
   "measured_energy_joules":None,
   "matched_contemporaneous_randomized_trial":False,
   "causal_performance_gain_demonstrated":False,
   "human_usefulness_beyond_declared_binary_goal":False,
  }
 return {
  "schema":SCHEMA,
  "owner_source":{
   "repository":"the-static-collective/GHoT",
   "commit":GHOT_COMMIT,"git_blob":GHOT_GIT_BLOB,
   "run":"https://github.com/the-static-collective/GHoT/actions/runs/42057823934",
   "source_response_types":"USGS_REPORTED_PUBLIC_FLOW_NOT_INDEPENDENTLY_CALIBRATED"
  },
  "exact_test_scope":"TWO_EXPLICIT_EVIDENCE_CONTRACTS_FOUR_REAL_NETWORK_TRIALS",
  "inquiry_steps_composed_from_source_receipts":traces,
  "goal_aware_vs_exhaustive_actual_resources":comparisons,
  "total_actual_public_gets":d["actual_network_requests_sent"],
  "total_actual_http_body_bytes":d["actual_http_response_body_bytes"],
  "total_actual_request_wall_ns":d["actual_request_wall_time_ns_sum"],
  "measured_electrical_energy_joules":None,
  "resource_units_are_not_fictional_credit_prices":True,
  "hypothesis_disposition":(
     "HELD_REAL_NARROW_GOAL_COMPLETION_WITH_LESS_OBSERVED_RESOURCE_WORK"
     if all(x["goal_aware_observed_non_worse_on_all_measured_dimensions"] for x in comparisons.values())
     else "HOLD_NO_UNAMBIGUOUS_RESOURCE_BENEFIT"
  ),
  "next_question":"Can an assistant establish the person's actual evidence need and prove which extra question might change its satisfaction before spending energy and attention?",
  "counterhypothesis":"A shorter investigative path can be less useful if the declared answer contract omits a quality, safety, provenance or timeliness requirement the human actually needed.",
  "falsification_plan":"Freeze the human-confirmed goal before starting; prospectively log actual usefulness, all requests, unavailable responses, latency and separately metered Joules across devices and new task types.",
  "limits":[
    "Two goal contracts intentionally simple; binary source-report satisfaction is not human utility.",
    "The two strategies were executed at different times, not randomly/independently controlled.",
    "Comparative measured differences are observed, not causal savings estimates or universal performance guarantees.",
    "HTTP body bytes exclude transport-layer overhead; process CPU and elapsed time do not measure energy.",
    "No physical hazards, flood warnings or personal data were evaluated. No autonomous source rewriting."
  ],
  "no_autonomous_code_revision":True,
  "automatic_promotion":False,"authority":False,"dispatch":False,
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path)
 a=p.parse_args()
 try:
  j=json.dumps(inspect(load()),sort_keys=True,indent=2)+"\n"
  if a.out:a.out.write_text(j,encoding="utf8")
  print(j)
  return 0
 except (HOLD,OSError,ValueError,TypeError,KeyError) as ex:
  print("HOLD: "+str(ex)[:160],file=sys.stderr)
  return 2

if __name__=="__main__":raise SystemExit(main())
