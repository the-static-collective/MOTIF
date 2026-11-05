#!/usr/bin/env python3
"""MOTIF-023 / Human Goal Handshake.
Before trying to economize *questions to the world*, ask the person what
would actually count as an answer. Bounded stdlib, no network or LLM calls,
no text persistence, no implicit user consent, no source execution.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"022"))
import cost_of_knowing as ghot022

SCHEMA="motif.human-goal-handshake/v1"
CONTRACT="motif.human-evidence-contract/v1"
AGES=(1,6,12,24)
GOALS=("any_fresh","two_named_fresh")
STATIONS={"blue":"USGS-05320000","sueur":"USGS-05320500",
          "mankato":"USGS-05325000"}
HAZARD=re.compile(r"\b(evacuat\w*|flood\s+risk|flood\s+warning|"
 r"safe\s+to\s+(cross|drive|drink|swim|travel)|safe\s+(bridge|route|road|water)|"
 r"bridge\s+(safe|closed)|should\s+i\s+(cross|drive|evacuate))\b",re.I)
RIVER=re.compile(r"\b(river|streamflow|discharge|gauge|gage|usgs|"
 r"water\s+reading|water\s+level)\b",re.I)
COMMUNITY=re.compile(r"\b(coffee|donat\w*|fellowship|event|volunteer|"
 r"grocery|church|soup\s+kitchen)\b",re.I)
BLUE=re.compile(r"\bblue\s+earth\b",re.I)
SUEUR=re.compile(r"\ble\s+sueur\b",re.I)
MANKATO=re.compile(r"\bmankato\b",re.I)
ANY=re.compile(r"\b(any|one|a\s+single|at\s+least\s+one)\b",re.I)
BOTH=re.compile(r"\b(both|two|each)\b",re.I)
HOURS=re.compile(r"\b(?:within|last|past|under|no\s+older\s+than)\s+"
 r"(\d{1,3})\s*(?:hours?|h)\b",re.I)
SCOPE_QUESTION={
 "id":"evidence_scope",
 "question":"Would ONE recent public river report be enough, or do you need BOTH named Blue Earth and Le Sueur reports?",
 "options":[{"value":"any_fresh","label":"One reported reading is enough"},
            {"value":"two_named_fresh","label":"Readings from both named rivers"}]
}
AGE_QUESTION={
 "id":"freshness_hours",
 "question":"How old can the reported measurement be and still count as useful?",
 "options":[{"value":n,"label":f"Within {n} hour"+("" if n==1 else "s")}
            for n in AGES]
}

class HOLD(ValueError):pass
def require(ok,why):
 if not ok:raise HOLD(why)
def canonical(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def sha(x):return sha256(canonical(x).encode()).hexdigest()

def physical_witness():
 """Independently verify GHoT-004 via the source-owned MOTIF-022 verifier."""
 source=ghot022.load()
 card=ghot022.inspect(source)
 require(card["schema"]=="motif.cost-of-knowing/v1" and
         card["automatic_promotion"] is False and
         card["measured_electrical_energy_joules"] is None,
         "SOURCE_WITNESS_UNVERIFIED")
 cost={}
 for goal in GOALS:
  outcome=card["goal_aware_vs_exhaustive_actual_resources"][goal]
  trial=next(t for t in source["actually_executed_trials"]
             if t["goal"]==goal and t["policy"]=="goal_aware")
  require(outcome["contract_completed_in_both_actual_trials"] is True,
          "SOURCE_WITNESS_DID_NOT_SATISFY_GOAL")
  cost[goal]={
   "historical_actual_request_count":outcome["optimized_real_requests"],
   "historical_actual_http_body_bytes":
       trial["actual_resource_units"]["http_response_body_bytes"],
   "not_a_future_cost_prediction":True,
  }
 require(cost["any_fresh"]["historical_actual_request_count"]==1 and
         cost["two_named_fresh"]["historical_actual_request_count"]==2,
         "SOURCE_GOAL_CONTRAST_NOT_MEASURED")
 return cost

def detect(text):
 require(type(text) is str and 0<len(text.strip())<=320 and
         "\x00" not in text,"INVALID_HUMAN_TEXT")
 t=" ".join(text.casefold().split())
 if HAZARD.search(t):return "SAFETY",None
 if not RIVER.search(t):
  return "OUTSIDE",None
 a,b,c=bool(BLUE.search(t)),bool(SUEUR.search(t)),bool(MANKATO.search(t))
 if a and b and not re.search(r"\b(or|either)\b",t):
  return "SUPPORTED","two_named_fresh"
 if (a or b or c):
  return "UNSUPPORTED_NAMED",None
 if BOTH.search(t):return "AMBIGUOUS",None
 if ANY.search(t):return "SUPPORTED","any_fresh"
 return "AMBIGUOUS",None

def age_in_text(text):
 m=HOURS.search(text)
 return int(m.group(1)) if m else None

def hold(status,message,*,question=None,goal=None,age=None,history=None):
 return {"schema":SCHEMA,"status":status,"message":message,
         "next_question":question,"draft_contract":None,
         "selected_goal":goal,"freshness_hours":age,
         "historical_resource_examples":history,
         "human_confirmed":False,"source_requests_sent":0,
         "llm_calls":0,"credits_used":0,"actual_energy_joules":None,
         "personal_question_stored":False,"physical_action":False,
         "authority":False,"automatic_promotion":False}

def evaluate(text,answers=None,*,confirmed=False,expected_contract_id=None,
             prior=None):
 """Only clarifies and proposes a plan; NEVER executes the plan."""
 require(type(confirmed) is bool and
         (expected_contract_id is None or
          (type(expected_contract_id) is str and
           re.fullmatch(r"[a-f0-9]{64}",expected_contract_id))),
         "UNSAFE_CONSENT_ARGUMENTS")
 require(answers is None or
         (type(answers) is dict and set(answers)<=
          {"evidence_scope","freshness_hours"}),"INVALID_CLARIFICATION_KEYS")
 answers=answers or {}
 kind,stated_goal=detect(text)
 if kind=="SAFETY":
  return hold("HOLD_HIGH_STAKES",
   "Public river reports cannot determine whether a bridge, road, evacuation or drinking water is safe.")
 if kind=="OUTSIDE":
  return hold("HOLD_OUTSIDE_RESEARCH_SCOPE",
   "This finite research instrument cannot infer an evidence contract for a non-river human goal.")
 if kind=="UNSUPPORTED_NAMED":
  return hold("HOLD_UNSUPPORTED_SOURCE_SPECIFICATION",
   "A specifically named source cannot be silently replaced by an arbitrary source.")
 answer_scope=answers.get("evidence_scope")
 require(answer_scope is None or
         (type(answer_scope) is str and answer_scope in GOALS),
         "UNLISTED_GOAL")
 if (stated_goal is not None and answer_scope is not None and
     stated_goal!=answer_scope):
  return hold("HOLD_CONFLICTING_HUMAN_INTENT",
    "Your selected source requirement conflicts with the explicit original request.")
 goal=answer_scope or stated_goal
 history=physical_witness() if prior is None else prior
 require(type(history) is dict and set(history)==set(GOALS) and
         history["any_fresh"]["historical_actual_request_count"]==1 and
         history["two_named_fresh"]["historical_actual_request_count"]==2,
         "INVALID_PHYSICAL_CONSEQUENCE_WITNESS")
 if goal is None:
  out=hold("ASK_ONE_DECISIVE_QUESTION",
    "The answer would be different depending on what you count as enough.",
    question=SCOPE_QUESTION,history=history)
  out["why_this_question"]=(
    "GHoT-004 physically required 1 GET for an any-source task and 2 "
    "GETs for the both-named task. Historical examples, not a forecast.")
  return out
 stated_age=age_in_text(text)
 provided_age=answers.get("freshness_hours")
 require(provided_age is None or type(provided_age) is int,
         "INVALID_AGE_ANSWER")
 if (provided_age is not None and stated_age is not None and
     provided_age!=stated_age):
  return hold("HOLD_CONFLICTING_HUMAN_INTENT",
    "The proposed freshness limit conflicts with the original request.",
    goal=goal,age=stated_age,history=history)
 age=provided_age if provided_age is not None else stated_age
 if age is None:
  return hold("ASK_ONE_DECISIVE_QUESTION",
    "No evidence can be evaluated as recent without a cutoff.",
    question=AGE_QUESTION,goal=goal,history=history)
 if age not in AGES:
  return hold("HOLD_UNSUPPORTED_FRESHNESS",
    "The current experiment only supports 1, 6, 12, or 24-hour cutoffs.",
    goal=goal,age=age,history=history)
 route=["blue","sueur","mankato"] if goal=="any_fresh" else ["blue","sueur"]
 spec={
  "schema":CONTRACT,
  "goal":goal,"freshness_hours":age,
  "completion_rule":("ANY_ONE_REPORTED_SOURCE" if goal=="any_fresh" else
                     "BOTH_NAMED_REPORTED_SOURCES"),
  "read_only_public_gauge_ids":[STATIONS[s] for s in route],
  "predeclared_order":route,
  "full_utc_window_required":True,"no_flood_safety_authority":True,
  "needs_separate_execution_consent":True,
  "actual_same_goal_age_studied_at_GHOT_004":age==12,
 }
 ident=sha(spec)
 if confirmed and expected_contract_id!=ident:
  return hold("HOLD_CONFLICTING_HUMAN_INTENT",
    "Contract changed or was never presented: confirmation refused.",
    goal=goal,age=age,history=history)
 return {
  "schema":SCHEMA,"status":(
    "READY_HELD_NO_EXECUTION" if confirmed else "CONFIRM_REQUIRED"),
  "message":("The person's specification is acknowledged, but no source contacted."
             if confirmed else "Confirm the exact information contract before any work."),
  "selected_goal":goal,"freshness_hours":age,
  "draft_contract":spec,"contract_id":ident,"next_question":None,
  "historical_resource_examples":history,
  "earlier_matching_12h_example":history[goal] if age==12 else None,
  "estimated_actual_future_requests":None,
  "human_confirmed":confirmed,"source_requests_sent":0,
  "llm_calls":0,"credits_used":0,"actual_energy_joules":None,
  "personal_question_stored":False,"physical_action":False,
  "authority":False,"automatic_promotion":False
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input",type=Path)
 args=p.parse_args()
 try:
  raw=(args.input.read_text() if args.input else sys.stdin.read(4096))
  require(len(raw)<4096,"REQUEST_TOO_LARGE")
  data=json.loads(raw)
  require(type(data) is dict and set(data)<={
     "text","answers","confirmed","expected_contract_id"},
     "UNKNOWN_DIALOG_FIELDS")
  out=evaluate(data.get("text"),data.get("answers"),
    confirmed=data.get("confirmed",False),
    expected_contract_id=data.get("expected_contract_id"))
  print(json.dumps(out,sort_keys=True,separators=(",",":")))
  return 0
 except (ValueError,TypeError,OSError,KeyError) as e:
  print(json.dumps({"schema":SCHEMA,"status":"HOLD_INVALID_INPUT",
   "message":str(e)[:120],"source_requests_sent":0,
   "personal_question_stored":False,"authority":False},sort_keys=True))
  return 2

if __name__=="__main__":raise SystemExit(main())
