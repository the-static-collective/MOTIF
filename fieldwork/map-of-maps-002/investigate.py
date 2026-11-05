#!/usr/bin/env python3
"""MOTIF map-of-maps 002: real owner-native ALEX/planZ/Dogram/GRAFT research.

An investigation of ONE candidate cross-repository contract, chosen by the
actual MOTIF field-map-001 logic. It executes only bounded LOCAL read-only
operations of four source-owner tools. The original planZ proposal and PlayDeck
TS types are inspected, not cast or automatically run as an adapter.

Source discovery != evidence support; graph reachability != compatibility;
classical plan != execution; GRAFT source scout != canonical adoption.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"map-of-maps-001"
SCHEMA="motif.map-of-maps-native-court/v1"
SHA40=re.compile(r"[0-9a-f]{40}\Z")
ALLOWED_REPOS={
 "alex":"the-static-collective/ALEX.2",
 "planz-native":"the-static-collective/planZ",
 "planz-proposal":"the-static-collective/planZ",
 "dogram":"the-static-collective/Dogram",
 "graft-native":"the-static-collective/GRAFT",
 "playdeck":"the-static-collective/playdeck",
}

def require(ok,code):
 if not ok:raise ValueError(code)

def blob(raw):
 return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()

def get_lock():
 lock=json.loads((HERE/"source-pins.json").read_text(encoding="utf8"))
 require(lock["schema"]=="motif.native-investigation-source-lock/v1"
         and lock["permission"]=="LOCAL_PUBLIC_SNAPSHOT_ANALYSIS_ONLY",
         "HOLD_INVALID_NATIVE_SOURCE_LOCK")
 require(set(x["id"] for x in lock["source_owners"])==set(ALLOWED_REPOS)
         and len(lock["source_owners"])==len(ALLOWED_REPOS),
         "HOLD_UNALLOWLISTED_NATIVE_OWNER")
 return lock

def verify_native(root,lock):
 root=Path(root)
 records=[]
 for owner in lock["source_owners"]:
  name=owner["id"]
  require(owner["repo"]==ALLOWED_REPOS[name]
          and bool(SHA40.fullmatch(owner["commit"])),
          "HOLD_SOURCE_OWNER_OR_COMMIT_MISMATCH")
  folder=root/name
  require(folder.is_dir() and not folder.is_symlink(),
          "HOLD_MISSING_NATIVE_SOURCE:"+name)
  observed=subprocess.run(["git","-C",str(folder),"rev-parse","HEAD"],
   capture_output=True,text=True,timeout=8,check=True).stdout.strip()
  require(observed==owner["commit"],"HOLD_STALE_SOURCE_HEAD:"+name)
  for file in owner["files"]:
   rel=file["path"]
   require(bool(re.fullmatch(r"(?:[a-zA-Z0-9_.-]+/)*[a-zA-Z0-9_.-]+",rel))
           and all(p not in (".","..") for p in rel.split("/"))
           and bool(SHA40.fullmatch(file["blob"])),
           "HOLD_UNTRUSTED_FILE_PIN")
   f=folder/rel
   require(f.is_file() and not f.is_symlink(),
           "HOLD_MISSING_NATIVE_FILE:"+name)
   content=f.read_bytes()
   require(len(content)<100000 and blob(content)==file["blob"],
           "HOLD_CHANGED_NATIVE_BYTES:"+name+"/"+rel)
   records.append({
    "repo":owner["repo"],"commit":owner["commit"],
    "path":rel,"git_blob":file["blob"],"bytes":len(content),
    "url":"https://github.com/"+owner["repo"]+"/blob/"+
          owner["commit"]+"/"+rel
   })
 return records

def run_native(command,root):
 env={"PATH":os.environ.get("PATH",""),"PYTHONDONTWRITEBYTECODE":"1"}
 p=subprocess.run(["node",str(HERE/command),str(root.resolve())],
   capture_output=True,text=True,timeout=15,env=env,check=True)
 require(len(p.stdout)<30000 and len(p.stderr)<20000,
         "HOLD_NATIVE_TOOL_TOO_MUCH_OUTPUT")
 return json.loads(p.stdout)

def original_type_probe(root,edge):
 require(edge["id"]=="PLZ_TO_PLAYDECK" and edge["knownNative"] is False
         and edge["support"]=="unsupported"
         and edge["fromType"]=="static-collective/planz-recursive-reactor/v1/proposal"
         and edge["toType"]=="playdeck.PerformanceReceipt/v0.1",
         "HOLD_MAP_SELECTED_UNVERIFIED_EDGE_CHANGED")
 plan=(root/"planz-proposal"/"reactor"/"recursive.mjs").read_text()
 definitions=(root/"playdeck"/"packages/core/src/PerformanceReceipt.ts").read_text()
 checker=(root/"playdeck"/"packages/receipts/src/validateReceipt.ts").read_text()
 seal=(root/"playdeck"/"packages/receipts/src/sealReceipt.ts").read_text()
 require(all(x in plan for x in (
    "export function compileRecursion",'"PROPOSED_UNVERIFIED"',
    "executed: false","admitted: false")),
    "HOLD_PLANZ_OWNER_PROPOSAL_STATE_CHANGED")
 require(all(x in definitions for x in (
    "export type PerformanceReceipt", "phase: ReceiptPhase",
    "events: ReceiptEvent[]","evidence?: PerformanceEvidence[]",
    'scope: "full-performance" | "checkpoint"')),
    "HOLD_PLAYDECK_RECEIPT_TYPE_CHANGED")
 require(all(x in checker for x in (
    "export const validateReceipt","canInheritReceipt",
    "rendered receipt lacks full-performance evidence")),
    "HOLD_PLAYDECK_RUNTIME_VALIDATOR_CHANGED")
 require(all(x in seal for x in (
    "export const canInheritReceipt",
    'receipt.phase === "rendered"',
    'item.scope === "full-performance"')),
    "HOLD_PLAYDECK_SEALING_RULE_CHANGED")
 return {
  "observation":"INCOMPATIBLE_SOURCE_CONTRACTS_WITHOUT_ADAPTER_EVIDENCE",
  "planz_source_status":"PROPOSED_UNVERIFIED",
  "planz_execution_asserted":False,
  "playdeck_receipt_requires_rendered_phase_and_full_performance_evidence":True,
  "source_owned_runtime_seal_module_inspected":True,
  "actual_playdeck_validator_executed":False,
  "real_rendered_performance_observed":False,
  "conversion_authorized":False,
  "owner_review":True,
  "status":"HOLD_NO_EXECUTABLE_CAST"
 }

def alex_native(root):
 # ALEX's original actual evaluator distinguishes attention to a claim from
 # an attributable support path. The case is a controlled fixture drawn from
 # source-observed contracts, NOT a factual accusation against either owner.
 sys.path.insert(0,str(root/"alex"))
 for key in tuple(sys.modules):
  if key=="alex_runtime" or key.startswith("alex_runtime."):
   del sys.modules[key]
 module=importlib.import_module("alex_runtime")
 from alex_runtime.derivation import evaluate_relation_case
 case={
  "operation_type":"relation_derivation",
  "rule_profile":module.DERIVATION_M0_PROFILE,
  "given":{
   "records":[
    {"id":"planz-proposal","kind":"breadcrumb"},
    {"id":"scout-search","kind":"search"},
    {"id":"playdeck-source-observation","kind":"evidence"},
    {"id":"verified-performance-claim","kind":"claim"}],
   "relations":[
    {"subject_id":"scout-search","predicate":"caused_by",
     "object_id":"planz-proposal"},
    {"subject_id":"playdeck-source-observation","predicate":"acquired_from",
     "object_id":"scout-search"}],
   "evidence_paths":[]},
  "attempt":{
   "evaluation_id":"MAP-002-ALEX-ATTENTION-NOT-SUPPORT",
   "relation_proposal":{
    "id":"hypothetical-plan-satisfies-playdeck",
    "subject_id":"planz-proposal",
    "predicate":"SUPPORTS",
    "object_id":"verified-performance-claim",
    "scope":"frozen-public-source-contract-only",
    "basis_ids":["planz-proposal","scout-search",
                 "playdeck-source-observation"]},
   "conclusion_assertion_id":"must-not-issue-a-false-performance"}
 }
 out=evaluate_relation_case(case)
 result=out["evaluation"]
 require(result["disposition"]=="REFUSE" and
         result["reason_code"]=="ATTENTION_NOT_SUPPORT" and
         out["conclusion_assertion"] is None,
         "HOLD_ALEX_EVIDENCE_LAUNDERING")
 # Cross-check a simpler missing-path control: no attention relationship
 # has been recorded, so the answer is INSUFFICIENT rather than acceptance.
 case["given"]["relations"]=[]
 no_path=evaluate_relation_case(case)["evaluation"]
 require(no_path["disposition"]=="INSUFFICIENT_TO_TEST" and
         no_path["reason_code"]=="NO_ATTRIBUTABLE_SUPPORT_PATH",
         "HOLD_ALEX_MISSING_PATH_MISCLASSIFIED")
 return {
  "original_org":"the-static-collective/ALEX.2",
  "source_owner_evaluator_executed":True,
  "attention_only_disposition":result["disposition"],
  "attention_only_reason":result["reason_code"],
  "missing_path_disposition":no_path["disposition"],
  "missing_path_reason":no_path["reason_code"],
  "source_search_is_evidence_of_working_adapter":False,
  "actual_witness_support_path_supplied":False,
  "claim_admitted":False
 }

def dogram_native(root):
 sys.path.insert(0,str(root/"dogram"))
 for key in tuple(sys.modules):
  if key=="dogram" or key.startswith("dogram."):
   del sys.modules[key]
 from dogram.engine import evaluate_specimen
 # A declared CANDIDATE edge is only a *counterfactual graph* — not a real
 # bridge. This tests the consequence of inventing the missing edge.
 specimen={
  "schema":"dogram.specimen/v0",
  "specimen_id":"MAP-002-CANDIDATE-EDGE-WOULD-CHANGE-REACHABILITY",
  "operator":"reach","operator_version":1,
  "inputs":{
   "graph":{
    "nodes":["planz_proposed_plan","hypothetical_adapter",
             "playdeck_verified_receipt"],
    "edges":[["planz_proposed_plan","hypothetical_adapter"]]},
   "mutation":{
    "op":"ADD_EDGE","source":"hypothetical_adapter",
    "target":"playdeck_verified_receipt"},
   "queries":[["planz_proposed_plan","playdeck_verified_receipt"],
              ["playdeck_verified_receipt","planz_proposed_plan"]]},
  "assumptions":["All graph edges here are hypothetical modeling aids.",
                 "Reachability is not type compatibility or real history."],
  "metadata":{"source":"CANNON PLZ_TO_PLAYDECK unresolved edge",
              "public_only":True}
 }
 receipt=evaluate_specimen(specimen)
 require(receipt["schema"]=="dogram.receipt/v0" and
         receipt["status"]=="OK" and receipt["operator"]=="reach",
         "HOLD_DOGRAM_NATIVE_OPERATOR")
 forward,reverse=receipt["result"]["queries"]
 require(forward["reachable_before"] is False and
         forward["reachable_after"] is True and
         reverse["reachable_after"] is False,
         "HOLD_DOGRAM_UNEXPECTED_GRAPH")
 return {
  "original_org":"the-static-collective/Dogram",
  "original_operator_executed":True,
  "operator":"reach@1",
  "receipt_input_digest":receipt["input_digest"],
  "forward_reachable_before":False,
  "forward_reachable_after_counterfactual_edge":True,
  "backward_reachable_after_counterfactual_edge":False,
  "graph_mutation_was_physical_or_code_action":False,
  "model_topology_only_not_adapter_compatibility":True,
  "status":"OK_COUNTERFACTUAL_GRAPH_ONLY"
 }

def investigate(root):
 root=Path(root).resolve()
 # Run exact earlier Map-001 actually; do not pretend to inherit an arbitrary
 # screenshot, detached JSON, or an unverified earlier conclusion.
 sys.path.insert(0,str(OLD))
 import engine as map001
 original=map001.run(root,3)
 require(original["schema"]=="motif.map-of-maps/v1"
         and original["source_count"]==7
         and original["technical_evidence"]["held_cross_owner_candidates"]==5,
         "HOLD_MOTIF_MAP_001_CHANGED")
 question=next(x for x in original["questions"] if x["id"]=="CONTRACT-QUESTION")
 edge=original["technical_evidence"]["selected_unproven_edge"]
 require(edge["id"]=="PLZ_TO_PLAYDECK" and
         question["action_authorized"] is False,
         "HOLD_NO_APPROVED_RESEARCH_QUESTION")
 pinned=verify_native(root,get_lock())
 start=time.process_time_ns()
 typ=original_type_probe(root,{
  "id":edge["id"],"knownNative":False,
  "support":"unsupported",
  "fromType":edge["from_type"],"toType":edge["to_type"]})
 plan=run_native("native_plan.mjs",root)
 require(plan["schema"]=="motif.map-002-native-planz-plan/v1"
         and plan["external_actions"]==0 and
         plan["actions"][-1]=="RETURN_REVIEW_PACKET",
         "HOLD_NATIVE_PLANNER_ANSWER")
 scout=run_native("native_graft_scout.mjs",root)
 require(scout["schema"]=="motif.map-002-native-graft-scour/v1"
         and scout["actual_network_gets"]==0
         and len(scout["observed_docs"])==2,
         "HOLD_NATIVE_GRAFT_SCOUT")
 alex=alex_native(root)
 dogram=dogram_native(root)
 return {
  "schema":SCHEMA,"status":"EXECUTED_NATIVE_READ_ONLY_RESEARCH_HELD",
  "source_map_001":{"source_count":original["source_count"],
    "source_bytes":original["source_bytes"],
    "source_types":list(original["source_receipts"]),
    "selected_question":question["question"],
    "selected_unverified_edge":edge},
  "original_source_owner_pins":pinned,
  "native_organs":{"planZ":plan,"GRAFT":scout,
                   "ALEX":alex,"Dogram":dogram},
  "original_playdeck_contract_inspection":typ,
  "next_experiment":{
    "status":"PROPOSED_FOR_SOURCE_OWNER_REVIEW",
    "question":"Can an original, witnessed PlayDeck performance receipt be generated from an independently authorized source-owned activity, rather than silently casting a proposed plan?",
    "smallest_negative_control":"A planZ PROPOSED_UNVERIFIED output is held, not accepted as a rendered PlayDeck receipt.",
    "smallest_positive_control":"Run original PlayDeck validation on a genuine rendered full-performance receipt with resolved descendants; no such witness is available in this case.",
    "what_next":"Inspect one actual original PlayDeck fixture and its native validation/runner; obtain explicit independent owner review before writing a converter.",
    "adapter_invented":False,"real_positive_witness_found":False,
    "owner_permission":False,
    "human_review_required":True
  },
  "observed_process_cpu_ns_for_orchestrator":time.process_time_ns()-start,
  "observed_cpu_ns_excludes_child_processes":True,
  "actual_energy_joules":None,"real_scout_network_reads":0,
  "private_records_accessed":False,"source_owner_code_modified":False,
  "external_actions_performed":False,
  "automatic_execution_or_canon":False,
  "actual_adapter_compatibility_proved":False
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source-root",type=Path,required=True)
 args=p.parse_args()
 try:
  print(json.dumps(investigate(args.source_root),indent=2,sort_keys=True))
  return 0
 except (ValueError,TypeError,KeyError,subprocess.CalledProcessError,
         subprocess.TimeoutExpired,ImportError) as err:
  print(json.dumps({"schema":SCHEMA,"status":"HOLD_SOURCE_OR_TOOL",
    "reason":str(err)[:240],"authority":"NONE",
    "external_actions_performed":False},sort_keys=True))
  return 2

if __name__=="__main__":
 raise SystemExit(main())
