#!/usr/bin/env python3
"""MOTIF-025 — portable definition-of-done examples; still human-authorized.

A finite cartridge registry creates two DIFFERENT concrete completion
criteria for recognized requests, while a deliberately generic fallback
preserves choice for unknown requests. People can author an uninterpreted
third criterion. No network, hosted model, sources, background work, code
editing, consent inheritance, database access, or actual service completion.

River research is delegated to the unchanged source-pinned 024 chain.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"024"))
import goal_examples as river

SCHEMA="motif.composable-goal-examples/v1"
CONTRACT="motif.human-completion-contract/v1"
ID=re.compile(r"^[0-9a-f]{64}$")
BAD=re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
RISK=re.compile(
 r"\b(evacuat\w*|safe\s+to\s+(cross|drive|drink|swim)|"
 r"bridge\s+(safe|closed)|should\s+i\s+evacuate|"
 r"emergency\s+(medical|flood)|suicide|self.harm|"
 r"weapon\s+instructions)\b",re.I)
NEGATION=re.compile(r"\b(not|never|without|unless|except|instead|rather than)\b",re.I)
RECUR=re.compile(r"\b(recurring|regularly|ongoing|every|each week|monthly|"
 r"weekly|biweekly|twice a month|repeatable|standing)\b",re.I)
SINGLE=re.compile(r"\b(only once|one.time|just this time|only (the )?next)\b",re.I)
COFFEE=re.compile(r"\b(coffee|espresso|caffeine)\b",re.I)
DONATE=re.compile(r"\b(donat\w*|sponsor\w*|contribut\w*|free\s+coffee)\b",re.I)
VOL=re.compile(r"\b(volunteer\w*|staff\s+shift|recruit\s+(a\s+)?helper)\b",re.I)
EVENT=re.compile(r"\b(event|gathering|fellowship|festival|potluck|church\s+night)\b",re.I)
GROCERY=re.compile(r"\b(grocery|food\s+shelf|food\s+exchange|produce\s+sharing)\b",re.I)
WEB=re.compile(r"\b(website|webpage|web\s+site|landing\s+page|deploy\s+(an?\s+)?app)\b",re.I)
RESEARCH=re.compile(r"\b(research|investigate|evidence\s+packet|source\s+audit)\b",re.I)
CUSTOM_MAX=320
MAX_GOAL=320

# Source-owned, bounded "outcome lenses". They are proposed examples, not
# factual answers, commitments from third parties or a trained classifier.
CARTRIDGES={
 "coffee_donation":{
  "label":"Coffee donation for an event",
  "differentiator":"One-time confirmed supply versus repeatable donated supply",
  "a":("A named donor confirms coffee for one upcoming gathering, "
       "with quantity, contact person, and pickup or delivery arranged."),
  "b":("A named donor commits coffee for at least two successive gatherings, "
       "with dates, quantity, coordinator and pickup or delivery confirmed."),
  "proof_a":"Donor confirmation, amount and handoff arrangement",
  "proof_b":"Explicit recurring commitment, dates, amounts and responsible contact",
  "mode_a":"one_time","mode_b":"recurring"},
 "volunteer_shift":{
  "label":"Volunteer help",
  "differentiator":"One filled shift versus a repeatable coverage arrangement",
  "a":("One volunteer agrees to cover a specific shift, with the date, "
       "role, location and contact confirmed."),
  "b":("A coordinator has confirmed volunteer coverage for two upcoming "
       "shifts, with named people, dates, roles and handoffs."),
  "proof_a":"Named volunteer and confirmed shift",
  "proof_b":"Named people and commitments for both scheduled shifts",
  "mode_a":"one_time","mode_b":"recurring"},
 "community_event":{
  "label":"Community gathering",
  "differentiator":"One gathering ready to run versus a repeatable series",
  "a":("The next gathering has a confirmed date, space, host, "
       "and a practical invitation to attendees."),
  "b":("Two successive gatherings have confirmed dates, hosts and "
       "a repeatable invitation and volunteer handoff plan."),
  "proof_a":"Confirmed venue/date/host and an invitation",
  "proof_b":"Two confirmed gathering arrangements and repeatable handoff",
  "mode_a":"one_time","mode_b":"recurring"},
 "grocery_network":{
  "label":"Community food exchange",
  "differentiator":"One documented handoff versus an ongoing matching process",
  "a":("One specific food offer or need is matched to a willing participant, "
       "and the pickup and consent details are confirmed."),
  "b":("A reusable offer-and-need board can receive one offer and one need, "
       "show permissions and complete a witnessed handoff."),
  "proof_a":"Consented match and documented handoff",
  "proof_b":"Demonstrated permissioned posting and witnessed handoff",
  "mode_a":"one_time","mode_b":"repeatable"},
 "website":{
  "label":"Website or public app",
  "differentiator":"One usable public page versus a maintainable working flow",
  "a":("A visitor can open a working page and complete one clear task, "
       "with the result demonstrated."),
  "b":("The complete requested user flow works end-to-end, and another "
       "person can repeat its tests and update its content."),
  "proof_a":"Reachable page and a completed visitor task",
  "proof_b":"Reproducible end-to-end tests and maintainer handoff",
  "mode_a":"minimum","mode_b":"repeatable"},
 "research":{
  "label":"Research and evidence",
  "differentiator":"One sourced answer versus an independently inspectable dossier",
  "a":("A clear answer is supported by at least one inspectable source, "
       "with its major uncertainty disclosed."),
  "b":("An evidence packet compares alternative explanations, records "
       "sources and uncertainty, and states what could falsify its conclusion."),
  "proof_a":"Inspectable source, answer and limitation",
  "proof_b":"Evidence ledger, competing hypotheses and falsification test",
  "mode_a":"focused","mode_b":"auditable"},
 "generic":{
  "label":"Unclassified request — human must specify the real outcome",
  "differentiator":"An actionable next step versus a verified completed outcome",
  "a":("A practical next step exists, with an identified responsible person, "
       "needed permissions, and a way to check progress."),
  "b":("The actual requested outcome has occurred, with evidence that "
       "the person asking can inspect to decide whether it is done."),
  "proof_a":"Next step, responsible party, authorization and observable checkpoint",
  "proof_b":"Person-defined verification of the actual achieved outcome",
  "mode_a":"plan_only","mode_b":"completed"}
}

def require(ok,reason):
 if not ok:raise ValueError(reason)

def fingerprint(obj):
 return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                          ensure_ascii=True).encode("utf8")).hexdigest()

def detect_domain(text):
 if river.human.RIVER.search(text):
  return "river_reports","finite-river-024",["physical agency report"]
 candidates=[]
 if COFFEE.search(text) and DONATE.search(text):candidates.append("coffee_donation")
 if VOL.search(text):candidates.append("volunteer_shift")
 if GROCERY.search(text):candidates.append("grocery_network")
 if WEB.search(text):candidates.append("website")
 if RESEARCH.search(text):candidates.append("research")
 if EVENT.search(text) and not candidates:candidates.append("community_event")
 if len(candidates)==1:return candidates[0],"explicit-term-cartridge",[]
 if len(candidates)>1:
  return "generic","multiple-domains-ambiguous",candidates
 return "generic","unknown-domain-fallback",[]

def base(status,message,domain,method,**extra):
 result={
  "schema":SCHEMA,"status":status,"message":message,
  "domain":domain,"selection_basis":method,
  "examples":None,
  "write_your_own_option":None,
  "draft_contract":None,"contract_id":None,
  "next_question":None,
  "selected_example":None,"human_confirmed":False,
  "human_text_persisted":False,
  "llm_calls":0,"credits_used":0,
  "network_requests_sent":0,"actual_energy_joules":None,
  "automatic_model_promotion":False,"authority":False,
  "physical_action":False,"correction_replaces_prior_id":False,
  "general_language_understanding_proven":False,
  **extra
 }
 return result

def examples(domain):
 c=CARTRIDGES[domain]
 return [
  {"id":id,"heading":("A · One concrete result" if id=="a" else
                      "B · More complete or repeatable result"),
   "would_this_be_enough":c[id],
   "evidence_needed":c["proof_"+id],
   "is_illustrative_not_an_achieved_outcome":True}
  for id in ("a","b")]

def inspect_input(text,choice,own_example,confirmed,expected_contract_id,correction_of_id):
 require(type(text) is str and 0<len(text.strip())<=MAX_GOAL and
         not BAD.search(text),"INVALID_PERSON_GOAL")
 require(choice is None or (type(choice) is str and
         choice in ("a","b","custom")),"INVALID_CHOICE")
 require(type(confirmed) is bool,"INVALID_CONFIRMATION")
 for n in (expected_contract_id,correction_of_id):
  require(n is None or (type(n) is str and ID.fullmatch(n)),"INVALID_DIGEST")
 require(own_example is None or (type(own_example) is str and
         len(own_example)<=CUSTOM_MAX and not BAD.search(own_example)),
         "INVALID_OWN_EXAMPLE")
 require(choice=="custom" or own_example is None,
         "CUSTOM_EXAMPLE_WITHOUT_CUSTOM_SELECTION")
 require(not confirmed or (choice is not None and expected_contract_id is not None),
         "NO_CONFIRMATION_WITHOUT_SEEN_CONTRACT")

def compose(text,choice=None,own_example=None,*,confirmed=False,
            expected_contract_id=None,correction_of_id=None,
            river_prior=None):
 inspect_input(text,choice,own_example,confirmed,
               expected_contract_id,correction_of_id)
 domain,method,unresolved=detect_domain(text)
 if RISK.search(text):
  return base("HOLD_HIGH_STAKES",
    "This illustrative goal matcher cannot certify safety or undertake emergency actions.",
    domain,method)
 if domain=="river_reports":
  # No rewriting of validated 024 river semantics: all physics retained.
  selection={"a":"one","b":"both","custom":"custom",None:None}[choice]
  r=river.evaluate(text,selection,own_example,
      confirmed=confirmed,expected_contract_id=expected_contract_id,
      correction_of_id=correction_of_id,prior=river_prior)
  opts=None
  if r["status"]=="SHOW_TWO_EXAMPLES":
   opts=[{"id":"a","heading":"A · One recent public reading",
          "would_this_be_enough":r["examples"][0]["would_this_be_enough"],
          "evidence_needed":"One source-reported timestamp and flow",
          "is_illustrative_not_an_achieved_outcome":True},
         {"id":"b","heading":"B · Both named public readings",
          "would_this_be_enough":r["examples"][1]["would_this_be_enough"],
          "evidence_needed":"Separate source-reported values from both named stations",
          "is_illustrative_not_an_achieved_outcome":True}]
  return base(r["status"],r["message"],domain,method,
    examples=opts,
    write_your_own_option=(
       {"id":"custom","label":"Or type your own example"} if opts else None),
    draft_contract=r.get("draft_contract"),
    contract_id=r.get("contract_id"),
    next_question=r.get("next_question"),
    selected_example=choice,
    human_confirmed=r.get("human_confirmed",False),
    correction_replaces_prior_id=r.get("prior_contract_replaced",False),
    prior_physical_example=r.get("prior_physical_example"),
    human_text_persisted=False)

 c=CARTRIDGES[domain]
 if choice is None:
  return base("SHOW_TWO_EXAMPLES",
    "Do you mean this result, that result, or something different? Show us what done looks like.",
    domain,method,
    examples=examples(domain),
    write_your_own_option={
      "id":"custom","label":"Or describe your own example of enough",
      "placeholder":"I would consider this done when...",
    },
    unresolved_domains=unresolved,
    no_example_auto_selected=True)
 if choice=="custom":
  if not own_example or not own_example.strip():
   return base("HOLD_CUSTOM_EXAMPLE_REQUIRED",
      "Type the actual result you would count as enough.",domain,method)
  # Important: preserve user's wording EXACTLY for their review and do not
  # pretend to have translated arbitrary text into machine success logic.
  completion=own_example.strip()
  criterion_origin="HUMAN_TYPED_UNINTERPRETED"
  proof="HUMAN_MUST_REVIEW_AND_DEFINE_ACCEPTANCE_EVIDENCE"
  scope="human_authored"
  inferred=False
  if RISK.search(completion):
   return base("HOLD_HIGH_STAKES",
     "A high-stakes outcome cannot be confirmed by this finite exemplar system.",
     domain,method)
 else:
  completion=c[choice]
  proof=c["proof_"+choice]
  criterion_origin="CURATED_SUGGESTION_REQUIRES_HUMAN_CONFIRMATION"
  scope=c["mode_"+choice]
  inferred=True
  # Do not let a convenient suggested one-time criterion overrule a
  # person's explicit request for recurring work, or vice versa.
  if RECUR.search(text) and scope=="one_time":
   return base("HOLD_CONFLICTING_HUMAN_INTENT",
     "Your original request calls for a recurring outcome. This example only covers one occasion.",
     domain,method,selected_example=choice)
  if SINGLE.search(text) and scope=="recurring":
   return base("HOLD_CONFLICTING_HUMAN_INTENT",
     "Your original request specifies one occasion. This example assumes a recurring commitment.",
     domain,method,selected_example=choice)
 # No proof that a contact, quote, site, contributor, donor or volunteer
 # actually exists; all criteria are prospective.
 contract={
  "schema":CONTRACT,
  "domain":domain,
  "completion_statement":completion,
  "criterion_origin":criterion_origin,
  "verification_required":proof,
  "declared_mode":scope,
  "semantics_machine_verified":False,
  "requested_outcome_observed":False,
  "needs_human_confirmation":True,
  "needs_separate_execution_authorization":True,
  "no_external_work_authorized":True,
 }
 ident=fingerprint(contract)
 if confirmed and expected_contract_id!=ident:
  return base("HOLD_CONFLICTING_HUMAN_INTENT",
   "That confirmation applies to a different or changed definition of done.",
   domain,method,selected_example=choice)
 return base(
  "READY_HELD_NO_EXECUTION" if confirmed else "CONFIRM_REQUIRED",
  "The definition is held for your approval; no work has been performed.",
  domain,method,
  selected_example=choice,
  draft_contract=contract,contract_id=ident,
  human_confirmed=confirmed,
  criterion_is_proposed_not_fact=True,
  prior_id_seen_but_not_authenticated=correction_of_id is not None,
  correction_replaces_prior_id=(
       correction_of_id is not None and correction_of_id!=ident),
  no_global_preference_update=True,
  human_text_persisted=False,
  completion_criterion_understood_by_machine=inferred,
 )

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--input",type=Path)
 args=parser.parse_args()
 try:
  raw=args.input.read_text(encoding="utf8") if args.input else sys.stdin.read(4096)
  require(len(raw)<4096,"BOUNDARY_INPUT_TOO_LARGE")
  d=json.loads(raw)
  require(type(d) is dict and set(d)<={
   "text","choice","own_example","confirmed",
   "expected_contract_id","correction_of_id"},"UNLISTED_API_INPUT")
  response=compose(d.get("text"),d.get("choice"),d.get("own_example"),
      confirmed=d.get("confirmed",False),
      expected_contract_id=d.get("expected_contract_id"),
      correction_of_id=d.get("correction_of_id"))
  print(json.dumps(response,sort_keys=True,separators=(",",":")))
  return 0
 except (ValueError,KeyError,TypeError,OSError) as ex:
  print(json.dumps(base("HOLD_INVALID_INPUT",
    "Request rejected: "+str(ex)[:100],"none","invalid")))
  return 2

if __name__=="__main__":
 raise SystemExit(main())
