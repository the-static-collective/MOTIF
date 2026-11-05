#!/usr/bin/env python3
"""MOTIF-024 — the right to be wrong: two examples or the person's own.

Exactly two concrete examples of what "enough" could mean, plus custom
example / explicit correction. Human correction redefines only THIS
session's proposed contract. No global learning, no LLM, no network, no
logs, no executable authority, no assumption that arbitrary text was parsed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"023"))
import human_goal as human

SCHEMA="motif.goal-example-correction/v1"
MAX_CUSTOM=320
EXAMPLES=(
 {
  "id":"one",
  "heading":"Example A — one answer would do",
  "would_this_be_enough":(
   "One USGS river discharge report, from any one of the three named "
   "public stations, timestamped within the last 12 hours, would be enough."
  ),
  "scope":"any_fresh","freshness_hours":12,
  "is_example_not_fact":True,
 },
 {
  "id":"both",
  "heading":"Example B — I need two specific answers",
  "would_this_be_enough":(
   "I need a discharge report from Blue Earth AND a separate report "
   "from Le Sueur, each timestamped within the last 12 hours."
  ),
  "scope":"two_named_fresh","freshness_hours":12,
  "is_example_not_fact":True,
 },
)
CONFIRM_STATUSES={"CONFIRM_REQUIRED","READY_HELD_NO_EXECUTION"}
NO_GUESS=re.compile(
 r"\b(not\s+one|not\s+both|don't\s+need|do\s+not\s+need|"
 r"instead\s+of|except|unless|rather\s+than)\b",re.I)
CONTROL=re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
ID=re.compile(r"^[0-9a-f]{64}$")

class HOLD(ValueError): pass

def require(ok,code):
 if not ok:raise HOLD(code)

def common(status,message,**kwargs):
 return {
  "schema":SCHEMA,
  "status":status,
  "message":message,
  "examples":[dict(x) for x in EXAMPLES] if status=="SHOW_TWO_EXAMPLES" else None,
  "write_your_own_option":{
   "id":"custom",
   "label":"Or describe your own example of what would be enough",
   "placeholder":"It would be enough if I had ... within the last ... hours.",
   "is_permitted":True
  } if status=="SHOW_TWO_EXAMPLES" else None,
  "next_question":None,
  "draft_contract":None,
  "contract_id":None,
  "selected_example":None,
  "human_confirmed":False,
  "correction_reviewed_only_in_this_request":False,
  "prior_contract_replaced":False,
  "source_requests_sent":0,
  "llm_calls":0,"credits_used":0,
  "actual_energy_joules":None,
  "personal_question_stored":False,
  "automatic_model_promotion":False,
  "physical_action":False,
  "authority":False,
  **kwargs
 }

def evaluate(text,choice=None,own_example=None,*,freshness_hours=None,
             confirmed=False,expected_contract_id=None,
             correction_of_id=None,prior=None):
 """No state, persistence, external effects, or silent acceptance of examples."""
 require(type(text) is str and 0<len(text.strip())<=320 and
         not CONTROL.search(text),"INVALID_PERSON_QUESTION")
 require(choice is None or choice in ("one","both","custom"),"INVALID_EXAMPLE_CHOICE")
 require(type(confirmed) is bool,"INVALID_CONFIRMATION")
 for digest in (expected_contract_id,correction_of_id):
  require(digest is None or (type(digest) is str and ID.fullmatch(digest)),
          "INVALID_CONTRACT_DIGEST")
 require(freshness_hours is None or type(freshness_hours) is int,
         "INVALID_FRESHNESS")
 require(own_example is None or (
    type(own_example) is str and len(own_example)<=MAX_CUSTOM and
    not CONTROL.search(own_example)
 ),"INVALID_CUSTOM_EXAMPLE")
 if choice!="custom":
  require(own_example is None,"CUSTOM_TEXT_WITHOUT_CUSTOM_CHOICE")
 elif not own_example or not own_example.strip():
  return common("HOLD_CUSTOM_EXAMPLE_REQUIRED",
    "Write what a finished answer would look like. The system will not choose for you.")
 kind,explicit=human.detect(text)
 if kind=="SAFETY":
  return common("HOLD_HIGH_STAKES",
   "River reports cannot determine whether a bridge, road, drinking water or evacuation is safe.")
 if kind=="OUTSIDE":
  return common("HOLD_OUTSIDE_RESEARCH_SCOPE",
   "This experiment only interprets specified public river-report goals; your other goal requires a different capability.")
 if kind=="UNSUPPORTED_NAMED":
  return common("HOLD_UNSUPPORTED_SOURCE_SPECIFICATION",
   "The existing research contracts cannot replace your specifically named gauge.")
 if choice is None:
  require(not confirmed and expected_contract_id is None,
          "CANNOT_CONFIRM_UNSHOWN_EXAMPLE")
  return common("SHOW_TWO_EXAMPLES",
   "Would either of these concrete finished answers be enough? Or write your own example.",
   original_intent_explicit=explicit is not None,
   prior_physical_example=prior if prior is not None else human.physical_witness(),
   no_option_has_been_accepted=True)
 # A prewritten example deliberately proposes a 12h cutoff; selecting it
 # expresses this preference, but never overrides the person's original
 # explicit constraint.
 if choice in ("one","both"):
  chosen=next(x for x in EXAMPLES if x["id"]==choice)
  scope=chosen["scope"]
  age=chosen["freshness_hours"]
  if freshness_hours is not None and freshness_hours!=age:
   return common("HOLD_CONFLICTING_HUMAN_INTENT",
    "This example explicitly says 12 hours. Rewrite your own example for a different cutoff.",
    selected_example=choice)
 else:
  # An arbitrary sentence cannot be declared semantically understood.
  # Permit only the exact, transparent finite research grammar.
  c=own_example.strip()
  if NO_GUESS.search(c) or human.HAZARD.search(c):
   return common("HOLD_CUSTOM_EXAMPLE_NEEDS_REVIEW",
    "This example has a negation, exception or safety implication the finite parser cannot reliably interpret. Please state a positive, exact completion condition.",
    selected_example="custom")
  # The original question carries the river domain; the person's proposed
  # custom example may say only "one report" or "both named reports".
  kind_custom,scope=human.detect("river "+c)
  if kind_custom!="SUPPORTED":
   return common("HOLD_CUSTOM_EXAMPLE_NEEDS_REVIEW",
    "The custom example did not clearly state 'one report' or 'both Blue Earth and Le Sueur'. Revise it; nothing is inferred.",
    selected_example="custom")
  age=human.age_in_text(c)
 if explicit is not None and scope!=explicit:
  return common("HOLD_CONFLICTING_HUMAN_INTENT",
   "The example contradicts your original explicit source requirement. Rewrite the original goal if you intend to change it.",
   selected_example=choice)
 original_age=human.age_in_text(text)
 if original_age is not None and age is not None and original_age!=age:
  return common("HOLD_CONFLICTING_HUMAN_INTENT",
    "The example's freshness cutoff conflicts with the one in your original request.",
    selected_example=choice)
 if freshness_hours is not None:
  if age is not None and freshness_hours!=age:
   return common("HOLD_CONFLICTING_HUMAN_INTENT",
    "The freshness setting contradicts your own typed example.",
    selected_example=choice)
  age=freshness_hours
 if age is None:
  # Ask a consequential follow-up rather than silently assuming 12h.
  return common("ASK_ONE_DECISIVE_QUESTION",
   "How recent would a report need to be for your example to count as enough?",
   selected_example=choice,next_question=human.AGE_QUESTION)
 # Use 023's existing formal contract, source-verifier and exact digest.
 answers={"evidence_scope":scope,"freshness_hours":age}
 result=human.evaluate(text,answers,
    confirmed=confirmed,expected_contract_id=expected_contract_id,prior=prior)
 if result["status"] not in CONFIRM_STATUSES:
  return common(result["status"],result["message"],selected_example=choice,
    next_question=result.get("next_question"))
 contract_id=result["contract_id"]
 # Caller-supplied prior ID is evidence of a correction *request*, not
 # authenticated memory of the old agreement; never train a global rule.
 differs=correction_of_id is not None and correction_of_id!=contract_id
 return common(result["status"],result["message"],
   selected_example=choice,draft_contract=result["draft_contract"],
   contract_id=contract_id,human_confirmed=result["human_confirmed"],
   prior_physical_example=result["earlier_matching_12h_example"],
   correction_reviewed_only_in_this_request=correction_of_id is not None,
   prior_contract_replaced=differs,
   correction_not_a_global_policy_update=True,
   needs_fresh_confirmation_after_correction=differs and not confirmed)

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--input",type=Path)
 args=parser.parse_args()
 try:
  raw=args.input.read_text(encoding="utf8") if args.input else sys.stdin.read(4096)
  require(len(raw)<4096,"REQUEST_TOO_LARGE")
  data=json.loads(raw)
  require(type(data) is dict and set(data)<={
    "text","choice","own_example","freshness_hours",
    "confirmed","expected_contract_id","correction_of_id"
  },"UNEXPECTED_INPUT_FIELDS")
  out=evaluate(data.get("text"),data.get("choice"),data.get("own_example"),
      freshness_hours=data.get("freshness_hours"),
      confirmed=data.get("confirmed",False),
      expected_contract_id=data.get("expected_contract_id"),
      correction_of_id=data.get("correction_of_id"))
  print(json.dumps(out,sort_keys=True,separators=(",",":"),ensure_ascii=True))
  return 0
 except (ValueError,TypeError,OSError,KeyError) as e:
  print(json.dumps(common("HOLD_INVALID_INPUT",
       "Invalid bounded goal-example input: "+str(e)[:90]),sort_keys=True))
  return 2

if __name__=="__main__":
 raise SystemExit(main())
