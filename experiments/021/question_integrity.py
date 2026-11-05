#!/usr/bin/env python3
"""MOTIF-021 — repair the *question encoding*, not the river or an LLM.

Our first "no fresh sources" physical result was falsified after checking
the REQUEST itself: dates rounded its intended end instant to midnight.
A corrected full-UTC request discovered recent agency readings, and a third
independent run actually stopped after the first usable public answer.

This instrument checks three separate source-owned receipts, keeps every
measurement in its true units and asks which method/assumption to inspect
next. It does not make any network requests or autonomously mutate code.
"""
from __future__ import annotations
from hashlib import sha1,sha256
from pathlib import Path
import json
import math
import argparse
import sys

SCHEMA="motif.question-integrity-and-physical-work/v1"
G_COMMIT="1517d2ac822ed1e6cfa30320a0f1e4574b6b0e55"
FILES={
 "initial":("002-first-misencoded-2026-11-05.json","e70629bc8540cd237b0e9a9fcb9b7626d5a44238"),
 "corrected":("002-corrected-2026-11-05.json","c49bf2f99325773673a55249ceafbae5129c2fb7"),
 "conditional":("003-real-stopping-2026-11-05.json","2289794fdce13e58efa271a205c480b074215ca0")
}
EVIDENCE=Path(__file__).resolve().parent/"evidence"
GHOT_002="ghot.public-network-inquiry/v1"
GHOT_003="ghot.actual-conditional-inquiry/v1"

class HOLD(ValueError):pass

def require(ok,code):
 if not ok:raise HOLD(code)

def digest(raw):
 return sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()

def load():
 out={}
 for key,(filename,expected) in FILES.items():
  source=EVIDENCE/filename
  require(source.is_file() and not source.is_symlink() and
          0<source.stat().st_size<30000,"UNAVAILABLE_PINNED_GHOT_EVIDENCE")
  data=source.read_bytes()
  require(digest(data)==expected,"CHANGED_GHOT_GIT_BLOB")
  try:out[key]=json.loads(data)
  except (ValueError,UnicodeError) as exc:
   raise HOLD("INVALID_GHOT_RECEIPT_JSON") from exc
 return out

def number(v):
 require(type(v) in (int,float) and math.isfinite(v) and v>=0,
         "UNKNOWN_OR_FALSE_MEASURED_RESOURCE")
 return v

def inspect(data):
 require(type(data) is dict and set(data)==set(FILES),
         "REQUIRE_ALL_THREE_INDEPENDENT_EXPERIMENTS")
 initial,corrected,conditional=(
  data["initial"],data["corrected"],data["conditional"])
 for name,s in (("initial",initial),("corrected",corrected)):
  require(type(s) is dict and s.get("schema")==GHOT_002 and
          s.get("external_action") is False and
          s.get("automatic_body_assignment") is False and
          s.get("automatic_model_promotion") is False and
          s.get("electrical_energy_measured") is False and
          s.get("research_only_not_flood_warning") is True and
          s.get("source_reporting_is_not_ground_truth") is True,
          "NOT_AUTHORIZED_PUBLIC_EVIDENCE_"+name)
  c=s.get("actual_network_activity",{})
  require(c.get("requests_sent")==3 and
          c.get("actual_on_wire_network_bytes") is None and
          c.get("energy_joules_attributable_to_requests") is None and
          type(s.get("per_request_receipts")) is list and
          len(s["per_request_receipts"])==3 and
          [x.get("site") for x in s["per_request_receipts"]]==
           ["blue","sueur","mankato"],
          "EXPERIMENT_002_SOURCE_COVERAGE_INVALID")
  for r in s["per_request_receipts"]:
   require(r.get("valid_source_response") is True and
           r.get("http_status")==200 and
           type(r.get("observation")) is dict and
           type(r["observation"].get("fresh_source_witness")) is bool and
           r.get("wire_network_bytes_total") is None,
           "INCORRECT_OR_UNTRUSTED_SOURCE_RECEIPT")
   number(r.get("latency_wall_ns"))
   number(r.get("local_cpu_ns"))
   number(r.get("body_bytes_received"))
  require(c.get("received_body_payload_bytes")==sum(
           r["body_bytes_received"] for r in s["per_request_receipts"]) and
          c.get("sum_individually_observed_http_elapsed_ns")==sum(
           r["latency_wall_ns"] for r in s["per_request_receipts"]),
           "SOURCE_SIZE_TIME_SUMS_CHANGED")
 require(initial.get("disposition")=="HOLD_NO_FRESH_SOURCE_WITNESS_OBSERVED" and
         initial["actual_network_activity"]["fresh_public_source_count"]==0 and
         all(r["observation"]["latest_observation_utc"]=="2026-11-05T00:00:00Z"
             for r in initial["per_request_receipts"]),
         "FIRST_RESULT_IS_NOT_FALSE_STALE_COUNTEREXAMPLE")
 require(corrected.get("disposition")=="HELD_FOR_PROSPECTIVE_CONDITIONAL_QUERY_TEST" and
         corrected["actual_network_activity"]["fresh_public_source_count"]==3 and
         all(r["observation"]["fresh_source_witness"] is True and
             r["observation"]["latest_observation_utc"]=="2026-11-05T13:45:00Z"
             for r in corrected["per_request_receipts"]),
         "FULL_UTC_CORRECTION_NOT_FRESH")
 c=conditional
 require(type(c) is dict and c.get("schema")==GHOT_003 and
         c.get("status")=="HELD_SINGLE_CURRENT_SOURCE_WITNESS_OBTAINED" and
         c.get("authority") is False and
         c.get("automatic_model_promotion") is False and
         c.get("physical_action") is False and
         c.get("credit_cost_used") is False and
         c.get("GHOT_willingness")=="normal" and
         c.get("requests_sent")==1 and
         c.get("actually_executed_sites")==["blue"] and
         c.get("skipped_sites")==["sueur","mankato"] and
         c.get("stopped_early") is True and
         c.get("source_witness_found") is True and
         len(c.get("per_request_receipts",[]))==1 and
         c.get("actual_on_wire_bytes") is None and
         c.get("electrical_energy_joules") is None and
         c.get("new_requests_avoided_vs_previous_run")=="NOT_MEASURED_AS_PARALLEL_CONTROL",
         "ACTUAL_CONDITIONAL_GHOT_RESULT_NOT_SAME")
 witness=c.get("witness")
 require(type(witness) is dict and witness.get("site")=="blue" and
         witness.get("observation_utc")=="2026-11-05T14:00:00Z" and
         witness.get("not_a_hazard_prediction") is True and
         number(witness.get("reported_discharge_cfs"))==2580,
         "COND_GHOT_MEASUREMENT_INVALID")
 require(c["body_payload_bytes_received"]==sum(
          r["body_bytes_received"] for r in c["per_request_receipts"]) and
         c["actual_request_elapsed_ns_sum"]==sum(
          r["latency_wall_ns"] for r in c["per_request_receipts"]),
         "ACTUAL_CONDITIONAL_RESOURCE_SUM_MISMATCH")
 time_a=number(initial["actual_network_activity"]["sum_individually_observed_http_elapsed_ns"])
 time_b=number(corrected["actual_network_activity"]["sum_individually_observed_http_elapsed_ns"])
 time_c=number(c["actual_request_elapsed_ns_sum"])
 bytes_a=number(initial["actual_network_activity"]["received_body_payload_bytes"])
 bytes_b=number(corrected["actual_network_activity"]["received_body_payload_bytes"])
 bytes_c=number(c["body_payload_bytes_received"])
 # Diagnostic must not rewrite "3-source vs 1-source" across different
 # executions into a matched counterfactual savings proof.
 results={
   "schema":SCHEMA,
   "question":"How can an intelligence detect that its physical evidence was distorted by how it encoded the question?",
   "source_commit_GHOT":G_COMMIT,
   "observations":{
      "first_date_only_interval":{
        "requests_actually_sent":3,"public_body_bytes":bytes_a,
        "wall_ns_sum":time_a,
        "reported_latest_utc":"2026-11-05T00:00:00Z",
        "qualified_fresh_source_count":0,
        "invalid_inference":"THE_AGENCY_SENSORS_ARE_STALE",
        "diagnosed_protocol_error":"END_OF_DATE_ONLY_INTERVAL_IS_MIDNIGHT",
        "request_url_not_embedded_in_receipt":True
      },
      "corrected_full_UTC_interval":{
        "requests_actually_sent":3,"public_body_bytes":bytes_b,
        "wall_ns_sum":time_b,
        "reported_latest_utc":"2026-11-05T13:45:00Z",
        "qualified_fresh_source_count":3,
        "source_code_repair":"FULL_UTC_TIMESTAMP_INTERVAL_AND_NEGATIVE_TEST"
      },
      "actual_stop_when_first_fresh":{
        "requests_actually_sent":1,"public_body_bytes":bytes_c,
        "wall_ns_sum":time_c,
        "source_observation_utc":witness["observation_utc"],
        "reported_discharge_cfs":witness["reported_discharge_cfs"],
        "other_fixed_queries_actually_executed":False,
        "fresh_reported_observation_obtained":True
      }
   },
   "learning":{
      "protocol_error_detected":True,
      "diagnostic_that_blames_sensor_on_buggy_query_is_refuted":True,
      "source_code_was_changed_BY_HUMAN_APPROVED_COMMIT":True,
      "autonomous_model_weight_update":False,
      "new_physical_world_interaction_kind":"MEASURED_QUESTION_FETCH_AND_STOP",
      "newly_proved_minimal_task":"ONE_PUBLIC_SOURCE_REPORTED_TIMELY_READING",
      "improved_operator_outcome_beyond_this_question_NOT_PROVED":True,
      "next_best_question":"Can MOTIF check the fidelity of its question's URL, timestamps and freshness window BEFORE spending network resources or blaming a sensor?",
      "next_hypothesis":"A source-request contract validator can prevent a false environmental diagnosis without executing any network request.",
      "next_falsification":"Freeze the URL/request-window validator and compare actual conditional source inquiry on another independently scheduled period, with captured exact request URLs and response-status timing."
   },
   "measured_resource_units":{
      "GHOT002_corrected_actual_request_count":3,
      "GHOT003_actual_request_count":1,
      "resource_comparison_is_NONCONTEMPORANEOUS":True,
      "causal_network_cost_savings_PROVED":False,
      "electrical_energy_joules":None,
      "body_payload_bytes_not_total_network_wire_bytes":True,
      "arbitrary_credits":False
   },
   "source_limits":[
      "The original date-only bug is known from the source code and regression tests, not reconstructible from the old receipts alone; raw requested URL is not archived.",
      "Source reports were read in separate executions, so the before/after difference is not a controlled experiment.",
      "The conditional strategy meets an intentionally narrow information goal, not a flood forecasting or human-benefit benchmark.",
      "No original physical gauge calibration or USGS issue-time provenance independently authenticated.",
      "The GHOT power field reported willingness, not attributable Joules or watts.",
      "Actual request count and HTTP response bytes are measured, but claimed saved bytes are not causally identified."
   ],
   "disposition":"HELD_QUESTION_PROTOCOL_VALIDATOR_AND_FRESH_REPLICATION",
   "automatic_promotion":False,"electrical_energy_measured":False,
   "authority":False,"environmental_warning":False,
 }
 return results

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",type=Path)
 a=p.parse_args()
 try:
  data=inspect(load())
  s=json.dumps(data,sort_keys=True,indent=2)+"\n"
  if a.out:a.out.write_text(s,encoding="utf8")
  print(s)
  return 0
 except (HOLD,OSError,ValueError,TypeError,KeyError) as e:
  print("HOLD: "+str(e)[:180],file=sys.stderr)
  return 2

if __name__=="__main__":raise SystemExit(main())
