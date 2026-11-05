#!/usr/bin/env python3
"""MOTIF-004: ask original, source-owned Free Graph which research gap next.

This is a bounded actual use of the existing generic selector, NOT a model
that acquires repos or executes tools. An operator provides the task cut.
A previous lookup is historical evidence of attention, not a fresh source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
LOCK_FILE=HERE/"source-lock.json"
SCHEMA="motif.map-004-source-native-investigation-selection/v1"

class Hold(ValueError):pass

def require(ok,why):
 if not ok:raise Hold("HOLD_"+why)

def blob(raw:bytes):
 return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()

def checked_sources(fgroot:Path):
 config=json.loads(LOCK_FILE.read_text(encoding="utf8"))
 require(config.get("schema")=="motif.freegraph-inquiry-source-lock/v1"
         and config.get("freegraph_repo")=="the-static-collective/free-graph"
         and config["external_lsd_code_executed"] is False
         and all(v is False for v in config["rights"].values())
         and config["native_receipt"]["path"]==
            "fieldwork/map-of-maps-002/evidence/first-actual-native-court-2026-11-05.json",
         "PERMISSION_OR_REPORT_LOCK_CHANGED")
 directory=fgroot.resolve()
 require(directory.is_dir() and not fgroot.is_symlink(),"NATIVE_FREEGRAPH_MISSING")
 try:
  r=subprocess.run(["git","-C",str(directory),"rev-parse","HEAD"],
       capture_output=True,text=True,check=True,timeout=5)
 except (subprocess.CalledProcessError,subprocess.TimeoutExpired,OSError) as e:
  raise Hold("HOLD_NATIVE_FREEGRAPH_IDENTITY") from e
 require(r.stdout.strip()==config["freegraph_commit"],
         "FREEGRAPH_NOT_SOURCE_OWNER_COMMIT")
 require(len(config["files"])==7,"SOURCE_FILE_ALLOWLIST_CHANGED")
 receipts=[]
 for relative,sha in sorted(config["files"].items()):
  require(relative in {
   "scripts/fg_core.py","scripts/fg_ops.py","scripts/reason_space.py",
   "scripts/motif_reason_bridge.py","scripts/inquiry_selector.py",
   "scripts/select_motif_next.py","research/reason-space-002/instruments.json"
  },"UNLISTED_SOURCE_FILE")
  file=directory/relative
  require(file.is_file() and not file.is_symlink(),"SOURCE_FILE_MISSING_OR_SYMLINK")
  raw=file.read_bytes()
  require(0<len(raw)<=18000 and blob(raw)==sha,
          "SOURCE_BLOB_CHANGED")
  receipts.append({"path":relative,"blob":sha,"bytes":len(raw)})
 report=ROOT/config["native_receipt"]["path"]
 require(report.is_file() and not report.is_symlink()
         and blob(report.read_bytes())==config["native_receipt"]["blob"],
         "MOTIF_NATIVE_RECEIPT_NOT_EXACT")
 return config,receipts,report,directory

def investigate(fgroot:Path,*,new_source:bool=False,
                original_positive_specimen:bool=False,ideation:bool=False,
                decline:bool=False):
 config,receipts,report,directory=checked_sources(fgroot)
 if str(directory) not in sys.path:sys.path.insert(0,str(directory))
 from scripts.motif_reason_bridge import build
 from scripts.inquiry_selector import select,task_cut
 p=build(report.read_bytes(),"all")
 cut=task_cut(p,requested_profiles=[
  "playdeck-validator","graft-source","alex-evidence","dogram-graph",
  "planz-plan","lsd-divergence"],
  source_scope_changed=new_source,
  original_positive_specimen_available=original_positive_specimen,
  ideation_requested=ideation,
  mode="not_required" if decline else "human_research_only")
 result=select(p,cut)
 require(result["schema"]=="free-graph.inquiry-selection/v0"
         and result["source_packet_id"]==p["packet_id"]
         and result["no_external_actions"] is True
         and result["no_automatic_tool_invocations"] is True
         and result["no_owner_canon_or_authority"] is True,
         "SOURCE_SELECTOR_CLAIMS_POWER")
 return {
  "schema":SCHEMA,
  "status":"REAL_NATIVE_FREEGRAPH_SELECTOR_COMPLETED_NO_ACTIONS",
  "source_owner":"the-static-collective/free-graph",
  "verified_commit":config["freegraph_commit"],
  "verified_source_blobs":receipts,
  "native_historical_receipt":config["native_receipt"],
  "selection":result,
  "external_effects":False,
  "original_tool_called_by_selector":False,
  "lsd_github_executable_connected":False,
  "unverified_source_promoted_to_truth":False,
  "model_weights_updated":False,
  "measured_joules":None
 }

def main():
 a=argparse.ArgumentParser()
 a.add_argument("--freegraph-root",type=Path,required=True)
 a.add_argument("--new-source",action="store_true")
 a.add_argument("--positive-specimen",action="store_true")
 a.add_argument("--lsd-ideation",action="store_true")
 a.add_argument("--decline",action="store_true")
 a.add_argument("--output",type=Path)
 args=a.parse_args()
 try:
  o=investigate(args.freegraph_root,new_source=args.new_source,
    original_positive_specimen=args.positive_specimen,
    ideation=args.lsd_ideation,decline=args.decline)
  result=json.dumps(o,indent=2,sort_keys=True)+"\n"
  if args.output:args.output.write_text(result,encoding="utf8")
  else:sys.stdout.write(result)
  return 0
 except (ValueError,KeyError,TypeError,OSError,ImportError) as e:
  sys.stderr.write("HOLD_NATIVE_INQUIRY:"+str(e)[:160]+"\n")
  return 2
if __name__=="__main__":raise SystemExit(main())
