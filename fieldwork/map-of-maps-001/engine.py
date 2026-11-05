#!/usr/bin/env python3
"""MOTIF MAP-OF-MAPS 001: source-pinned, public-only, tiered evidence inquiry.

This is a bounded deterministic MOTIF research organ, NOT a language model,
unrestricted GitHub crawler, canon selector, adapter inventor or autonomous
agent. It reads fixed files from separately pinned Git checkouts, checks exact
Git blob bytes and prints a human-review-only next-question packet.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
SCHEMA="motif.map-of-maps/v1"
SHA40=re.compile(r"[a-f0-9]{40}\Z")
SAFE_PATH=re.compile(r"(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\Z")
EXPECTED=("atlas-families","atlas-relations","atlas-visibility",
          "atlas-inventory-summary","planz-attention",
          "graft-donor-registry","cannon-question-field")
OWNERS={
 "atlas":"the-static-collective/What-is-the-static-collective-",
 "planz":"the-static-collective/planZ",
 "graft":"the-static-collective/GRAFT",
 "cannon":"the-static-collective/CANNON",
}

def must(ok,reason):
 if not ok:
  raise ValueError(reason)

def git_blob(data):
 return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\x00"+data).hexdigest()

def lock_read(path=HERE/"sources.lock.json"):
 manifest=json.loads(Path(path).read_text(encoding="utf8"))
 must(manifest["schema"]=="motif.map-sources-lock/v1" and
      manifest["policy"]["public_sources_only"] is True and
      manifest["policy"]["automatic_promotion"] is False,
      "UNTRUSTED_SOURCE_LOCK")
 sources=manifest["sources"]
 must(tuple(x["id"] for x in sources)==EXPECTED,"SOURCE_ALLOWLIST_CHANGED")
 for s in sources:
  must(s["tier"] in (1,2,3) and
       s["repo"]==OWNERS.get(s["checkout"]) and
       bool(SHA40.fullmatch(s["blob"])) and
       bool(SHA40.fullmatch(s["commit"])) and
       bool(SAFE_PATH.fullmatch(s["path"])) and
       s["max_bytes"]<=25000 and s["max_bytes"]>0 and
       s["kind"] in ("json","markdown"),"BAD_SOURCE_PIN")
 return manifest

def read_sources(manifest,root,tier):
 must(tier in (1,2,3),"INVALID_TIER")
 root=Path(root)
 observed={}
 records={}
 for s in manifest["sources"]:
  if s["tier"]>tier:continue
  file=root/s["checkout"]/s["path"]
  must(file.is_file() and not file.is_symlink(),
       "MISSING_OR_SYMLINK:"+s["id"])
  raw=file.read_bytes()
  must(0<len(raw)<=s["max_bytes"],"SOURCE_TOO_LARGE:"+s["id"])
  must(git_blob(raw)==s["blob"],"SOURCE_BLOB_MISMATCH:"+s["id"])
  try:
   contents=raw.decode("utf8",errors="strict")
   observed[s["id"]]=json.loads(contents) if s["kind"]=="json" else contents
  except (UnicodeError,json.JSONDecodeError) as err:
   raise ValueError("UNREADABLE_SOURCE:"+s["id"]) from err
  records[s["id"]]={
   "repo":s["repo"],"commit":s["commit"],"path":s["path"],
   "git_blob":s["blob"],"bytes":len(raw),"tier":s["tier"],
   "url":"https://github.com/"+s["repo"]+"/blob/"+
         s["commit"]+"/"+s["path"]
  }
 return records,observed

def question(id,issue,why,sources,probe):
 return {
  "id":id,"disposition":"PROPOSED_RESEARCH_ONLY",
  "why":why,"question":issue,"sources":sources,
  "smallest_falsifiable_probe":probe,
  "action_authorized":False,
  "automatic_adapter_invention":False,
  "external_contact":False,
  "canon_selection":False
 }

def derive(data,receipts,tier):
 atlas=data["atlas-families"]
 rel=data["atlas-relations"]
 visibility=data["atlas-visibility"]
 summary=data["atlas-inventory-summary"]
 must(atlas["owner"]=="the-static-collective" and
      rel["schema"]=="static-git-atlas/relations-v1" and
      visibility["schema"]=="static-git-atlas/visibility-policy-v1" and
      visibility["restricted_default_projection"]=="omit",
      "ATLAS_PUBLIC_AUTHORITY_BOUNDARY")
 families=atlas["constellations"]
 links=rel["relations"]
 must(isinstance(families,list) and isinstance(links,list) and
      all(x.get("authority_owner") and x.get("source_url") and
          x.get("status") in ("declared","observed","inferred") for x in links),
      "UNATTRIBUTED_ATLAS_EDGE")
 repo_names=set()
 for shelf in families:
  for name in shelf["repositories"]:
   must(isinstance(name,str) and 0<len(name)<=120,
        "INVALID_PUBLIC_REPO_NAME")
   repo_names.add(name)
 capture=re.search(
  r"Captured: \*\*([^*]+)\*\*.*?\*\*(\d+) public repositories\*\*.*?"
  r"\*\*(\d+) branch refs\*\*.*?\*\*(\d+) open PRs\*\*",
  summary,re.S)
 must(capture is not None,"PUBLIC_SNAPSHOT_UNRECOGNIZED")
 timestamp,repos,branches,prs=capture.groups()
 url=lambda key:receipts[key]["url"]
 questions=[question(
  "ATLAS-QUESTION",
  "Which exact source-owner contract should be inspected before a map edge is called a working integration?",
  "Public branch inventory is far broader than human-curated source-linked relations.",
  [url("atlas-families"),url("atlas-relations")],
  "Choose one declared edge, retrieve its owner's cited source and test what it actually asserts."
 )]
 out={
  "schema":SCHEMA,"tier":tier,
  "disposition":"READ_ONLY_RESEARCH_PROPOSAL",
  "source_receipts":receipts,
  "source_count":len(receipts),
  "source_bytes":sum(x["bytes"] for x in receipts.values()),
  "atlas":{
   "captured_at":timestamp,
   "reported_public_repositories":int(repos),
   "reported_branch_refs":int(branches),
   "reported_open_pull_requests":int(prs),
   "editorial_shelves":len(families),
   "unique_names_in_editorial_shelves":len(repo_names),
   "human_curated_source_linked_relations":len(links),
   "atlas_is_canon":False,
   "relations_prove_runtime_compatibility":False,
   "restricted_sources_in_public_packet":False,
  },
  "questions":questions,
  "authority":"NONE","network_requests_from_reasoner":0,
  "public_only":True,"private_sources_read":False,
  "donor_source_code_executed":False,
  "external_actions":False,"auto_source_writes":False,
  "automatic_canon_promotion":False,
  "joules_measured":None,"next_tier":tier+1 if tier<3 else None
 }
 if tier>=2:
  plans=data["planz-attention"]
  must(plans["schema"]=="planz/public-attention-v1" and
       plans["authority"]=="INDEX_ONLY" and
       isinstance(plans["entries"],list),"PLANZ_NOT_INDEX_ONLY")
  entries=plans["entries"]
  must(all(x.get("executionAllowed") is False and
           x.get("fieldOutcome")=="NOT_VERIFIED" and
           x.get("thirdPartyApproval")=="NOT_ESTABLISHED"
           for x in entries),"PLANZ_UNAUTHORIZED_PROMOTION")
  target=next((x for x in entries if x.get("id")=="ATLAS-BRIDGE-002"),None)
  must(target is not None,"NO_SELECTED_ATLAS_BRIDGE_PLAN")
  out["plan_attention"]={
   "editorial_edition":plans["edition"],
   "reviewed_on":plans["reviewedOn"],
   "selected_open_entries":len(entries),
   "authorized_to_execute":0,
   "verified_field_outcomes":0,
   "focus":{
    "id":target["id"],"disposition":target["disposition"],
    "source":target["source"],
    "next_human_gate":target["nextGate"],
    "blockers":target["blockedBy"]
   },
   "index_is_a_complete_live_plan_census":False
  }
  questions.append(question(
   "PLANZ-QUESTION",
   "Which owner will choose one exact public source cut for a negative-control integration test?",
   "The plan owner lists source pinning, donor compatibility, capability permission and independent verification as missing gates.",
   [url("planz-attention"),target["source"]],
   "Pin just one source and define both pass and HOLD outcomes before any cross-repository action."
  ))
 if tier>=3:
  graft=data["graft-donor-registry"]
  cannon=data["cannon-question-field"]
  must(graft["schema"]=="graft.donor-code-registry/v1" and
       graft["policy"]["raw_witness_data_imported"] is False and
       cannon["schema"]=="cannon.interface-field-source-lock/v1" and
       cannon["authority"]=="NONE" and
       cannon["policies"]["autoBridge"] is False,
       "CROSSING_AUTHORITY_OR_WITNESS_FAILURE")
  possible=cannon["edges"]
  native=[x for x in possible if x["knownNative"]]
  held=[x for x in possible if not x["knownNative"]]
  must(native and held and
       all(x["evidenceClass"]=="speculation" and
           x["support"]=="unsupported" for x in held),
       "UNVERIFIED_BRIDGE_PROMOTED")
  target=next((x for x in held if x["id"]=="PLZ_TO_PLAYDECK"),held[0])
  out["technical_evidence"]={
   "graft_original_source_subsets":len(graft["candidates"]),
   "graft_registered_adapters":len(graft["adapters"]),
   "cannon_candidate_crossings":len(possible),
   "previously_executed_bounded_native_routes":len(native),
   "held_cross_owner_candidates":len(held),
   "selected_unproven_edge":{
    "id":target["id"],"claim":target["claim"],
    "from_type":target["fromType"],"to_type":target["toType"],
    "source_status":target["sourceCase"],
    "is_runtime_compatible":False
   }
  }
  questions.append(question(
   "CONTRACT-QUESTION",
   "Can a proposed planZ plan actually satisfy the original PlayDeck performance-receipt contract?",
   "CANNON records this exact crossing as unverified; GRAFT can inspect the donor's original source without running it.",
   [url("cannon-question-field"),url("graft-donor-registry")],
   "A proposed-only plan must HOLD; only a truly witnessed typed performance receipt could satisfy a separately reviewed positive test."
  ))
  out["motif_first_next_experiment"]={
   "name":"ONE_SOURCE_PINNED_ADAPTER_NEGATIVE_CONTROL",
   "why":"A missing typed receipt is an inspectable claim, unlike asserting thousands of branches automatically compose.",
   "first_step":"Use owner-original public source files to construct an independently runnable planZ-to-PlayDeck typed negative fixture.",
   "required_refusal":"PROPOSED_UNVERIFIED plan must NOT be interpreted as a completed performance receipt.",
   "possible_positive":"Only independent source-owner-reviewed witnessed receipt may justify a positive adapter test.",
   "result_status":"PROPOSED_NOT_EXECUTED",
   "approval":"HUMAN_SOURCE_OWNER_REVIEW_REQUIRED"
  }
 return out

def run(root,tier,manifest_path=HERE/"sources.lock.json"):
 manifest=lock_read(manifest_path)
 receipts,data=read_sources(manifest,root,tier)
 return derive(data,receipts,tier)

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--source-root",required=True,type=Path)
 p.add_argument("--tier",required=True,type=int,choices=(1,2,3))
 args=p.parse_args()
 try:
  print(json.dumps(run(args.source_root,args.tier),indent=2,sort_keys=True))
  return 0
 except (ValueError,KeyError,TypeError) as ex:
  print(json.dumps({"schema":SCHEMA,"disposition":"HOLD_INVALID_SOURCE_OR_AUTHORITY",
    "reason":str(ex)[:150],"external_actions":False},sort_keys=True))
  return 2

if __name__=="__main__":
 raise SystemExit(main())
