#!/usr/bin/env python3
"""MOTIF-026 — a HUMAN-APPROVED definition of done can author a LOCAL work packet.

The contract is recomputed by the exact 025 kernel, not trusted from an
arbitrary request. A second, explicit PREPARE_LOCAL_PACKET_ONLY permission
authorizes a limited *in-memory* work-pack spec, not contact, network, posting,
third-party sign-in, field execution, automatic model rewrite, or persistence.
The renderer lives in JAR;VIS and must independently verify the result.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"025"))
import example_composer as composer

SCHEMA="motif.goal-to-work-spec/v1"
ACTION="PREPARE_LOCAL_PACKET_ONLY"
KINDS=("checklist","csv_tracker","unsent_message","html_workpage")
DOMAINS=("coffee_donation","volunteer_shift","community_event",
         "grocery_network","website","research","generic","river_reports")
FIELDS={
 "coffee_donation":["donor_or_source","contact_status","event_date",
  "quantity_confirmed","handoff_method","evidence_of_commitment"],
 "volunteer_shift":["volunteer_name","role","shift_date","contact_status",
  "commitment_status","evidence"],
 "community_event":["event_date","location","host","permission",
  "invitation_status","evidence"],
 "grocery_network":["offer_or_need","participant","permission_status",
  "handoff_time","handoff_status","evidence"],
 "website":["page_or_flow","requested_task","test_status","access_url",
  "reviewer","evidence"],
 "research":["hypothesis_or_question","source","source_checked",
  "competing_explanation","confidence_or_limitation","next_test"],
 "generic":["task","owner_or_helper","permission","next_action",
  "evidence","completion_status"],
 "river_reports":["site","report_timestamp","reported_value","verification",
  "limits","observation_status"],
}
CHECKS={
 "coffee_donation":[
  "Specify the event date and estimated servings (not assumed).",
  "Identify a possible donor and request permission to contact them.",
  "Prepare a short unsent ask with quantity and pickup needs.",
  "Record the donor's explicit acceptance or decline, if obtained.",
  "Verify quantity, contact, and pickup/delivery arrangements.",
  "Compare the result with the person's confirmed definition of enough."],
 "volunteer_shift":[
  "Specify roles, dates, and responsible coordinator.",
  "Prepare an unsent invitation for each role.",
  "Record the person's voluntary yes/no response only after it happens.",
  "Confirm handoff and arrival details.",
  "Check every named shift against the accepted goal."],
 "community_event":[
  "Specify event date, location, host and permission to use space.",
  "Prepare an invitation draft; do not send automatically.",
  "Identify what can be offered without assuming commitments.",
  "Record actual confirmed people, not hypothetical ones.",
  "Verify the accepted event outcome was genuinely achieved."],
 "grocery_network":[
  "Write the offer or need without revealing private participant data.",
  "Find a willing steward and confirm permission before publication.",
  "Do not imply a match has been verified before a voluntary yes.",
  "Arrange a safe practical handoff only through consenting people.",
  "Witness the actual handoff and check the goal contract."],
 "website":[
  "Write the visitor task in testable terms.",
  "Select the existing local tool or project repo with explicit permission.",
  "Produce a minimal test case before claiming a working feature.",
  "Run the test and capture actual results rather than inventing them.",
  "Ask the human to verify the result against the approved contract."],
 "research":[
  "Write the question and what evidence would count as sufficient.",
  "Collect only allowed sources in a separately authorized research step.",
  "Record source and date, including missing or contradictory evidence.",
  "Compare alternatives and disclose remaining uncertainty.",
  "Check the answer against the person's agreed standard."],
 "generic":[
  "Review the person's exact wording; it has not been semantically verified.",
  "Identify the next smallest permitted action and responsible person.",
  "Do not infer contacts, identities, signatures or external permissions.",
  "Record actual evidence only after work has been performed.",
  "Ask the person whether the original requirement has been satisfied."],
 "river_reports":[
  "Confirm the specific river gauges and UTC freshness cutoff.",
  "Check the request's UTC window before making any public query.",
  "This local packet does not contact USGS or issue flood warnings.",
  "Record source timestamps and provisional-data limits if later obtained.",
  "Never use a flow observation alone as proof of bridge or water safety."],
}
MAIL={
 "coffee_donation":("Coffee for a community gathering",
  "Hello,\n\nWe're organizing a community gathering and looking for donated coffee. "
  "Would you consider helping with an amount and pickup arrangement that work for you? "
  "We can share the event date, approximate servings and a point of contact after confirming details.\n\n"
  "There is no commitment unless you explicitly agree. Thank you for considering it."),
 "volunteer_shift":("Voluntary shift invitation",
  "Hello,\n\nWe're looking for help with a community activity. Would you be open to "
  "hearing the specific role, date and expected time commitment? It's completely optional."),
 "community_event":("Invitation draft for a gathering",
  "You're invited to a community gathering. Event details, host, location and schedule "
  "must be confirmed by the organizer before this draft is shared."),
 "grocery_network":("Optional food exchange inquiry",
  "Hello,\n\nWould you be interested in discussing a voluntary local food handoff? "
  "Nothing has been matched or committed. We would confirm permissions and details first."),
 "website":("Request for a focused feature review",
  "Could you review whether the proposed user task and evidence of completion match "
  "the requested website outcome? No deployment or source change has been made."),
 "research":("Source and evidence request draft",
  "Could you point us toward a source relevant to the stated research question? "
  "We will check provenance and competing explanations before making a conclusion."),
 "generic":("Optional collaboration request draft",
  "Hello,\n\nI'm exploring a possible project outcome. Could I send you the details "
  "to see whether you're interested? This is only an invitation, not a commitment."),
 "river_reports":("Research request draft — unsent",
  "This is a draft only. No river gauge was contacted and no environmental safety "
  "inference was made. A separate authorized instrument is required to retrieve source data.")
}

def check_args(inp):
 if type(inp) is not dict or set(inp)-{
    "text","choice","own_example","freshness_hours",
    "expected_contract_id","consent","action"}:
  raise ValueError("UNLISTED_ACTION_INPUT")
 if inp.get("action")!=ACTION or inp.get("consent") is not True:
  return False
 return True

def prepare(inp):
 if not check_args(inp):
  return {"schema":SCHEMA,"status":"HOLD_NO_SEPARATE_LOCAL_WORK_PERMISSION",
    "work_spec":None,"generated":False,"external_effect":False,
    "authority":False,"user_data_stored":False}
 # The source kernel checks the digest against a recomputed contract,
 # rather than believing a hand-supplied "confirmed": true flag.
 r=composer.compose(inp.get("text"),inp.get("choice"),
     inp.get("own_example"),freshness_hours=inp.get("freshness_hours"),
     confirmed=True,expected_contract_id=inp.get("expected_contract_id"))
 if r.get("status")!="READY_HELD_NO_EXECUTION":
  return {"schema":SCHEMA,"status":"HOLD_UNCONFIRMED_OR_CHANGED_GOAL",
    "work_spec":None,"generated":False,"external_effect":False,
    "authority":False,"user_data_stored":False}
 domain=r.get("domain")
 if domain not in DOMAINS:
  raise ValueError("UNLISTED_SOURCE_DOMAIN")
 goal=r["draft_contract"]
 if type(goal) is not dict or goal.get("schema") not in (
     "motif.human-completion-contract/v1",
     "motif.human-evidence-contract/v1"):
  raise ValueError("UNKNOWN_GOAL_CONTRACT")
 # No simulated answer, no actual external task completion, no witness!
 return {
  "schema":SCHEMA,
  "status":"LOCAL_WORK_SPEC_PREPARED_NOT_EXECUTED",
  "work_spec":{
   "schema":"motif.local-work-spec/v1",
   "goal_contract_id":r["contract_id"],
   "goal_contract":goal,
   "domain":domain,
   "allowed_outputs":list(KINDS),
   "tracking_fields":list(FIELDS[domain]),
   "checklist_items":list(CHECKS[domain]),
   "message_subject":MAIL[domain][0],
   "message_draft":MAIL[domain][1],
   "user_content_is_unverified":True,
   "external_delivery_permitted":False,
   "external_contact_verified":False,
   "remote_execution_permitted":False,
   "execution_claim":False,
   "separate_human_permission_scope":ACTION,
  },
  "generated":True,
  "external_effect":False,
  "user_data_stored":False,
  "hosted_tokens_used":0,"actual_energy_joules":None,
  "authority":False,
  "source_code_modified":False,
  "model_trained":False,
  "note":"A local-only packet recipe has been derived; rendering and download require separate user action. No real-world outcome verified."
 }

def main():
 p=argparse.ArgumentParser();p.add_argument("--input",type=Path)
 args=p.parse_args()
 try:
  raw=args.input.read_text(encoding="utf8") if args.input else sys.stdin.read(4096)
  if len(raw)>=4096:raise ValueError("BOUNDARY_INPUT_TOO_LARGE")
  packet=prepare(json.loads(raw))
  print(json.dumps(packet,ensure_ascii=True,sort_keys=True,separators=(",",":")))
  return 0
 except (ValueError,TypeError,KeyError,OSError) as e:
  print(json.dumps({"schema":SCHEMA,"status":"HOLD_INVALID_INPUT",
      "message":str(e)[:140],"generated":False,
      "external_effect":False,"authority":False,"user_data_stored":False}))
  return 2

if __name__=="__main__":raise SystemExit(main())
