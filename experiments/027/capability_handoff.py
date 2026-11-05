#!/usr/bin/env python3
"""MOTIF-027 — THE LAST INCH: source-owned, opt-in capability crossing.

A user-confirmed contract plus separate MOTIF-026 permission can reveal
local, actual capabilities. A *third* explicit approval allows producing a
mailto: handoff URI for a specific HUMAN-ENTERED recipient and exact preview.
No SMTP, no third-party login, no sending, no claimed delivery, no storage.
A LOCAL_WORKSHOP route allows only a local page handoff, never auto-execution.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from urllib.parse import quote, urlencode
import argparse
import json
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"026"))
import prepare_work as owner

SCHEMA="motif.capability-handoff/v1"
DISCOVER="DISCOVER_LOCAL_CAPABILITIES"
PREVIEW="PREVIEW_MAIL_APP_HANDOFF"
OPEN="AUTHORIZE_MAIL_APP_OPEN"
PERMISSION="OPEN_LOCAL_MAIL_COMPOSER_ONLY"
ALLOWED_FIELDS={
 "text","choice","own_example","freshness_hours","expected_contract_id",
 "stage","recipient","subject","message","preview_id",
 "open_permission","open_consent"
}
DIGEST=re.compile(r"^[0-9a-f]{64}$")
# Single, conventional ASCII mailbox. No lists, encoded separators or Unicode
# domains. IDN/quoted addresses remain unsupported rather than half-accepted.
RECIPIENT=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._%+\-]{0,63}@[A-Za-z0-9][A-Za-z0-9\-]{0,61}(?:\.[A-Za-z0-9][A-Za-z0-9\-]{0,61})+$")
BAD=re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
MAIL_DOMAINS={"coffee_donation","volunteer_shift","community_event",
              "grocery_network"}
WORKSHOP_DOMAINS={"website","research","community_event","grocery_network",
                  "coffee_donation","volunteer_shift","generic"}
MAX_SUBJECT=130
MAX_MESSAGE=1300
MAX_RECIPIENT=150
MAX_MAILTO=3400

def require(x,err):
 if not x:raise ValueError(err)

def canonical(x):
 return json.dumps(x,ensure_ascii=True,sort_keys=True,separators=(",",":"))

def digest(x):
 return sha256(("MOTIF-027|"+canonical(x)).encode("utf8")).hexdigest()

def fail(status,reason):
 return {
  "schema":SCHEMA,"status":status,"message":reason,
  "capabilities":None,"preview_id":None,
  "mailto_uri":None,"recipient":None,
  "actual_message_sent":False,"external_delivery":False,
  "remote_execution":False,"public_network_gets":0,
  "journal_events_created":0,"api_credits_spent":0,
  "actual_energy_joules":None,"authority":False,
  "model_updated":False,
 }

def check(data):
 require(type(data) is dict and set(data)<=ALLOWED_FIELDS,
         "HOLD_UNLISTED_INPUT_FIELDS")
 require(data.get("stage") in (DISCOVER,PREVIEW,OPEN),
         "HOLD_INVALID_STAGE")
 require(type(data.get("expected_contract_id")) is str and
         DIGEST.fullmatch(data["expected_contract_id"]),
         "HOLD_UNBOUND_CONTRACT")
 if data["stage"]==DISCOVER:
  require(not any(k in data for k in (
    "recipient","subject","message","preview_id",
    "open_consent","open_permission")),
    "HOLD_CONTACT_WITHOUT_SELECTION")
 if data["stage"]==PREVIEW:
  require(not any(k in data for k in (
    "preview_id","open_consent","open_permission")),
    "HOLD_PREMATURE_COMPOSER_PERMISSION")
 if data["stage"]==OPEN:
  require(data.get("open_consent") is True and
          data.get("open_permission")==PERMISSION and
          type(data.get("preview_id")) is str and
          DIGEST.fullmatch(data["preview_id"]),
          "HOLD_SEPARATE_MAIL_APP_PERMISSION_MISSING")

def validated_person_mail(data):
 recipient=data.get("recipient")
 subject=data.get("subject")
 message=data.get("message")
 require(type(recipient) is str and
         5<=len(recipient)<=MAX_RECIPIENT and
         RECIPIENT.fullmatch(recipient) and
         not BAD.search(recipient),"HOLD_INVALID_SINGLE_MAIL_RECIPIENT")
 require(type(subject) is str and
         1<=len(subject.strip())<=MAX_SUBJECT and
         "\n" not in subject and "\r" not in subject and
         not BAD.search(subject),"HOLD_INVALID_SUBJECT")
 require(type(message) is str and
         1<=len(message.strip())<=MAX_MESSAGE and
         not BAD.search(message.replace("\r\n","\n").replace("\n","")),
         "HOLD_INVALID_MESSAGE")
 require(not ("\r" in message and "\r\n" not in message),
         "HOLD_UNEXPECTED_CR")
 return recipient,subject,message

def verify_owner(data):
 # This exact owner-side gate recomputes human-defined success under the
 # MOTIF-025 grammar; a caller-supplied contract object cannot override it.
 fields=("text","choice","own_example","freshness_hours",
         "expected_contract_id")
 msg={k:data[k] for k in fields if k in data}
 msg["action"]=owner.ACTION
 msg["consent"]=True
 out=owner.prepare(msg)
 require(out.get("status")=="LOCAL_WORK_SPEC_PREPARED_NOT_EXECUTED"
         and out.get("work_spec",{}).get("goal_contract_id")==
              data["expected_contract_id"] and
         out["external_effect"] is False and
         out["authority"] is False,
         "HOLD_UNCONFIRMED_OR_MODIFIED_ORIGINAL_GOAL")
 return out["work_spec"]

def route(data):
 check(data)
 spec=verify_owner(data)
 domain=spec["domain"]
 identifier=spec["goal_contract_id"]
 capabilities=[{
  "id":"local_workkit",
  "label":"Prepare local checklists, CSV, an unsent letter and printable page",
  "effect":"BROWSER_DOWNLOAD_ONLY",
  "requires_permission":"PREPARE_LOCAL_PACKET_ONLY",
  "available":True
 }]
 if domain in WORKSHOP_DOMAINS:
  capabilities.append({
   "id":"local_workshop",
   "label":"Bring the confirmed question into the local Static OS workshop",
   "effect":"LOCAL_PREFILL_ONLY_NO_AUTO_RUN",
   "requires_permission":"EXPLICIT_OPEN_LOCAL_WORKSHOP",
   "available":True,"route":"/workshop"
  })
 if domain in MAIL_DOMAINS:
  capabilities.append({
   "id":"local_email_composer",
   "label":"Open the person's own mail app with a reviewed outreach draft",
   "effect":"MAILTO_URI_ONLY_NO_SEND",
   "requires_permission":PERMISSION,
   "available":True,"recipient_must_be_entered_by_person":True,
   "contact_exists_or_is_donor_verified":False
  })
 if data["stage"]==DISCOVER:
  return {
   **fail("LOCAL_CAPABILITIES_AVAILABLE_NOT_EXECUTED",
         "Choose a local capability. No external work has occurred."),
   "goal_contract_id":identifier,"domain":domain,
   "capabilities":capabilities,
   "source_owner_verified":True,
   "mail_app_supported":domain in MAIL_DOMAINS,
   "workshop_supported":domain in WORKSHOP_DOMAINS,
   "message_template_subject":spec["message_subject"] if domain in MAIL_DOMAINS else None,
   "message_template_body":spec["message_draft"] if domain in MAIL_DOMAINS else None,
   "template_sent":False,
  }
 # Narrow to manual recipient handoff; never convert unsupported domain
 # or river research into an email to an imaginary donor.
 if domain not in MAIL_DOMAINS:
  return fail("HOLD_MAIL_HANDOFF_NOT_SUPPORTED_FOR_THIS_GOAL",
              "This research domain has no approved contact capability.")
 recipient,subject,message=validated_person_mail(data)
 contents={
  "goal_contract_id":identifier,"recipient":recipient,
  "subject":subject,"message":message,
  "effect":"MAILTO_URI_ONLY_NO_SEND"
 }
 stamp=digest(contents)
 if data["stage"]==PREVIEW:
  return {
   **fail("LOCAL_MAIL_COMPOSER_PREVIEW_NOT_SENT",
          "Review the exact recipient and text, then separately choose to open your mail app."),
   "goal_contract_id":identifier,
   "preview_id":stamp,
   "recipient":recipient,"subject":subject,"message":message,
   "contact_is_human_supplied_unverified":True,
   "opening_a_mail_app_does_not_prove_sending":True,
  }
 require(data["preview_id"]==stamp,
         "HOLD_CHANGED_MAIL_RECIPIENT_OR_MESSAGE_REVIEW_AGAIN")
 mailto="mailto:"+quote(recipient,safe="@._+-") + "?" + urlencode(
    {"subject":subject,"body":message},quote_via=quote)
 require(len(mailto)<=MAX_MAILTO and mailto.startswith("mailto:") and
         not any(c in mailto for c in "\r\n"),"HOLD_UNSAFE_MAILTO_LENGTH")
 return {
  **fail("LOCAL_MAIL_APP_HANDOFF_READY_NOT_SENT",
         "Only a mailto URL was prepared. User action in their mail app is required to send."),
  "goal_contract_id":identifier,
  "preview_id":stamp,"recipient":recipient,
  "subject":subject,"message":message,
  "mailto_uri":mailto,
  "open_permission_applied":PERMISSION,
  "no_smtp_request":True,"no_delivery_receipt":True,
  "contact_is_human_supplied_unverified":True,
  "opening_a_mail_app_does_not_prove_sending":True,
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input",type=Path)
 args=p.parse_args()
 try:
  raw=args.input.read_text(encoding="utf8") if args.input else sys.stdin.read(4096)
  require(len(raw)<4096,"HOLD_OVERSIZE_INPUT")
  obj=json.loads(raw)
  print(canonical(route(obj)))
  return 0
 except (ValueError,TypeError,KeyError,OSError) as ex:
  print(canonical(fail("HOLD_INVALID_OR_UNVERIFIED_HANDOFF",str(ex)[:130])))
  return 2

if __name__=="__main__":raise SystemExit(main())
