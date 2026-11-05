#!/usr/bin/env python3
"""MOTIF MAP-003: use native Free Graph as an abstract reasoning substrate.

This first integration turns one actually run historical multi-organ
investigation into a source-owned, content-addressed reasoning graph. It then
asks the original Free Graph code a *structural* follow-up question. No new
owner gate, automatic tool invocation, source modification, private import,
model inference or live network call is implied.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
LOCK=HERE/"freegraph.lock.json"
FG_COMMIT="a74d018a4ebc7398733e5d98da8f7d389621fb9a"
SOURCE_PINS={
 "scripts/fg_core.py":"bd4e75b55b91bb199de65d26bbd888662a65495d",
 "scripts/fg_ops.py":"cb80e283bb114e97e1769d149a2c52b8f79ae3a3",
 "scripts/reason_space.py":"3c00d1f75e20ab6384fb514f4f30f45ae8650bc2",
 "scripts/motif_reason_bridge.py":"21e9dbc48edaa1118db15fae6ecf46cc7902e495",
}
REPORT_PATH=("fieldwork/map-of-maps-002/evidence/"
             "first-actual-native-court-2026-11-05.json")
REPORT_BLOB="457eaf895cc96cfa9f853b31ab665f38f2f3f0c9"
SCHEMA="motif.map-003-freegraph-reason/v1"

class Hold(ValueError): pass
def require(b,what):
 if not b:raise Hold("HOLD_"+what)
def git_blob(data):
 return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()

def verify(fgroot:Path,report:Path):
 cfg=json.loads(LOCK.read_text(encoding="utf8"))
 require(cfg["schema"]=="motif.freegraph-join/v1"
         and cfg["permission"]=="LOCAL_HISTORICAL_SOURCE_READ_ONLY"
         and cfg["freegraph_source_owner"]["repo"]=="the-static-collective/free-graph"
         and cfg["freegraph_source_owner"]["commit"]==FG_COMMIT
         and cfg["historical_motif_report"]["path"]==REPORT_PATH
         and cfg["historical_motif_report"]["blob"]==REPORT_BLOB
         and cfg["historical_motif_report"]["commit"]==
             "070aba60319cbab3d1c1838ec7481c350e7d86e5"
         and all(cfg["rights"][name] is False for name in (
             "private_content","network","external_execution",
             "branch_discovery","owner_gate","auto_canon")),
         "SOURCE_GRANT_INVALID")
 files=cfg["freegraph_source_owner"]["files"]
 require({f["path"]:f["blob"] for f in files}==SOURCE_PINS
         and len(files)==len(SOURCE_PINS),"SOURCE_FILES_REPLACED")
 fgroot=fgroot.resolve()
 require(fgroot.is_dir() and not fgroot.is_symlink(),
         "FREEGRAPH_CHECKOUT_REQUIRED")
 try:
  head=subprocess.run(["git","-C",str(fgroot),"rev-parse","HEAD"],
       check=True,capture_output=True,text=True,timeout=5).stdout.strip()
 except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
  raise Hold("HOLD_FREEGRAPH_GIT_IDENTITY") from e
 require(head==FG_COMMIT,"FREEGRAPH_HEAD_MISMATCH")
 receipts=[]
 for path,blob in SOURCE_PINS.items():
  f=fgroot/path
  require(f.is_file() and not f.is_symlink(),"FREEGRAPH_SOURCE_MISSING_OR_SYMLINK")
  raw=f.read_bytes()
  require(len(raw)<=50000 and git_blob(raw)==blob,"FREEGRAPH_SOURCE_BYTES_CHANGED")
  receipts.append({"path":path,"blob":blob,"bytes":len(raw)})
 require(report.resolve()==(REPO/REPORT_PATH).resolve() and
         report.is_file() and not report.is_symlink(),
         "MOTIF_REPORT_UNAUTHORIZED_OR_RELOCATED")
 raw=report.read_bytes()
 require(0<len(raw)<30000 and git_blob(raw)==REPORT_BLOB,
         "MOTIF_NATIVE_REPORT_CHANGED")
 return raw,receipts

def investigate(fgroot:Path,report:Path):
 raw,receipts=verify(fgroot,report)
 # The selected Free Graph source is checked at exact bytes and commit *before*
 # import. No new dependency manager, remote install or runtime network read.
 root=str(fgroot.resolve())
 if root not in sys.path:sys.path.insert(0,root)
 from scripts.motif_reason_bridge import build
 from scripts.reason_space import lens, pressure
 from scripts.fg_core import validate_packet

 allp=build(raw,"all")
 evidence=lens(allp,"evidence")
 upcoming=lens(allp,"next")
 for p in (allp,evidence,upcoming):
  require(not validate_packet(p),"FREEGRAPH_PACKET_INVALID")
  require(p["schema"]=="free-graph.packet/v0"
          and p["task_world_cut"]["status"]=="unresolved"
          and p["modes"]==["re-enter"]
          and all(l["authority"]=="none" for l in p["links"])
          and not any(l["verb"]=="constitutes" for l in p["links"]),
          "UNAUTHORIZED_GRAPH_PROMOTION")
 query=pressure(allp)
 require(query["schema"]=="free-graph.reason-pressure/v0"
         and query["source_packet_id"]==allp["packet_id"]
         and query["status"]=="STRUCTURAL_QUESTIONS_NOT_DECISIONS"
         and query["external_actions"] is False
         and query["automatic_authority"]=="NONE",
         "SOURCE_OWNED_PRESSURE_BOUNDARY")
 return {
  "schema":SCHEMA,
  "status":"SOURCE_PINNED_FREEGRAPH_REVIEW_ONLY",
  "source_owner":"the-static-collective/free-graph",
  "source_commit":FG_COMMIT,
  "verified_freegraph_blobs":receipts,
  "historical_motif_receipt_blob":REPORT_BLOB,
  "reasoning_graph":{
   "schema":allp["schema"],
   "packet_ids":{n:p["packet_id"] for n,p in (
    ("all",allp),("evidence",evidence),("next",upcoming))},
   "count":{"sources":len(allp["sources"]),"nodes":len(allp["nodes"]),
            "links":len(allp["links"])},
   "links_have_execution_authority":False,
   "all_projections_preserve_record_identities":True,
   "unchanged_native_source_custody":True,
   "graph_is_a_historical_snapshot":True,
  },
  "source_owned_graph_pressure":query,
  "all_results_unresolved":True,
  "human_approval_required":True,
  "actual_external_actions":0,
  "private_sources_read":False,
  "real_network_requests":0,
  "generic_tool_dispatch_implemented":False,
  "actual_energy_joules":None,
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--freegraph-root",type=Path,required=True)
 p.add_argument("--report",type=Path,default=REPO/REPORT_PATH)
 p.add_argument("--output",type=Path)
 args=p.parse_args()
 try:
  out=investigate(args.freegraph_root,args.report)
  text=json.dumps(out,indent=2,sort_keys=True)+"\n"
  if args.output:args.output.write_text(text,encoding="utf8")
  else:sys.stdout.write(text)
  return 0
 except (ValueError,KeyError,TypeError,OSError) as ex:
  sys.stderr.write("HOLD_FREEGRAPH_REASON_JOIN:"+str(ex)[:180]+"\n")
  return 2

if __name__=="__main__":
 raise SystemExit(main())
