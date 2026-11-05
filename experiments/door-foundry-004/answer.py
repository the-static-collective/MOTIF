"""MOTIF-004: Receive a held GRAFT answer only after MOTIF poses its own question."""
import argparse
from pathlib import Path
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"experiments"/"door-foundry-003"))
import graft_backloop as graft
import question as inquiry

class HOLD(ValueError): pass

def document(path):
    path=Path(path)
    if not path.is_file() or path.stat().st_size>120000:
        raise HOLD("Missing or oversized evidence")
    obj=json.loads(path.read_text())
    if not isinstance(obj,dict):
        raise HOLD("Evidence must be an object")
    return obj

def evaluate(query_file,packet_file,graft_source,motif_original,build,report):
    q=document(query_file)
    p=document(packet_file)
    original_question_sha=inquiry.verify_question(q,motif_original)
    held_receipt_sha=graft.check_receipt(p)
    gap=q["missing_capability_contract"]
    operator=p["selected_operator"]
    if (gap["kind"]!="NUMERIC_OBSERVATION_FROM_BOUNDED_JSON" or
        gap["target_path"] is not None or
        gap["target_path_known_to_questioner"] is not False or
        gap["minimum_independent_final_cases"]!=4 or
        p["independent_final_check"]["generated_correct"]!=4 or
        operator["network_authority"]!="NONE"):
        raise HOLD("Candidate does not satisfy the source-independent question")
    graft.build(packet_file,graft_source,motif_original,build)
    result=subprocess.run([sys.executable,"run.py"],cwd=build,text=True,
                          capture_output=True,timeout=25)
    if result.returncode or len(result.stdout)>40000:
        raise HOLD("Built organ failed local execution")
    measured=json.loads(result.stdout)
    if (measured.get("schema")!="motif.graft-born-sensor-result.v0" or
        measured.get("status")!="EXECUTED_NEW_LOCAL_SENSOR_WITH_ORIGINAL_MOTIF_POLICY" or
        measured.get("network_requests")!=0 or
        measured.get("external_actions")!=0 or
        measured.get("operator_admitted") is not False or
        measured.get("fair_classical_selector_would_tie") is not True):
        raise HOLD("Unsupported synthetic conclusion")
    rows=measured.get("observations",[])
    if len(rows)!=4: raise HOLD("Four blind synthetic cases required")
    threshold=gap["decision_rule"]["threshold"]
    unmeasured=0
    changes=0
    for row in rows:
        n=row["generated_sensor_value"]
        if type(n) is not int or not 0<=n<=10:
            raise HOLD("Invalid numeric result")
        desired="new-choices" if n>=threshold else "immediate"
        if row["selected_original_003_policy"]!=desired:
            raise HOLD("Generated sensor cannot resolve proposed gap")
        unmeasured += desired=="immediate"
        changes += desired!="immediate"
    if unmeasured!=2 or changes!=2:
        raise HOLD("No reproducible change in original MOTIF policy")
    manifest=document(Path(build)/"manifest.json")
    body={
      "schema":"motif.self-question-answer.v0",
      "status":"SYNTHETIC_GAP_ADDRESSED_IN_HELD_BUILD",
      "question_asked_before_candidate":True,
      "original_question_sha256":original_question_sha,
      "cannon_held_receipt_sha256":held_receipt_sha,
      "new_generated_operator_sha256":operator["source_sha256"],
      "new_build_manifest_sha256":manifest["content_sha256"],
      "source_owner":"the-static-collective/GRAFT",
      "review_owner":"the-static-collective/CANNON",
      "decision_owner":"the-static-collective/MOTIF",
      "case_count":4,
      "fixed_immediate_no_sensor_matches":unmeasured,
      "new_sensor_matches":4,
      "fair_classical_same_evidence_matches":4,
      "recommendations_changed":changes,
      "next_question":"Can the new measurement generalize to an unknown observation schema?",
      "next_question_submitted":False,
      "real_world_actions":0,
      "automatic_source_changes":0,
      "claimed_classical_superiority":False,
      "real_human_outcomes":False,
      "admitted":False
    }
    body["content_sha256"]=inquiry.digest(body)
    if Path(report).exists():raise HOLD("Existing output must not be overwritten")
    Path(report).write_text(json.dumps(body,indent=2)+"\n")
    return body

def main():
    parser=argparse.ArgumentParser()
    for k in ("question","cannon-receipt","graft-source","motif-original","build","report"):
        parser.add_argument("--"+k,required=True,type=Path)
    x=parser.parse_args()
    try:
        result=evaluate(x.question,x.cannon_receipt,x.graft_source,
                        x.motif_original,x.build,x.report)
        print(json.dumps(result,indent=2))
    except (HOLD,inquiry.HOLD,graft.HOLD) as exc:
        print(json.dumps({"stage":"HOLD","reason":str(exc)}))
        raise SystemExit(1)
if __name__=="__main__":main()
