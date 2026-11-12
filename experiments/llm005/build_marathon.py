"""Create all 879+ step marathon source-ledger artifacts and interactive offline HTML."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from marathon import GROUPS,POLICIES,Marathon,experiment
from viewer_marathon import render

def create(study=None):
    study=study or experiment()
    if study.get("schema")!="motif.odyssey-marathon.study/v0":
        raise ValueError("STUDY_NOT_COMPATIBLE")
    cases={}
    for policy in POLICIES:
        runner=Marathon(GROUPS[0],policy)
        runner.execute()
        cases[policy]=runner.public_record()
    return {"schema":"motif.odyssey-marathon.viewer/v0",
       "scope":"PUBLIC_AUTHOR_SYNTHETIC_ONLY",
       "group":list(GROUPS[0]),"selection":"FIRST_REGISTERED_GROUP_NOT_SELECTED_FOR_OUTCOME",
       "study":study,"records":cases,"external_actions":False,"real_model":False}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="/tmp/odyssey240")
    a.add_argument("--study-file")
    args=a.parse_args()
    path=Path(args.out);path.mkdir(parents=True,exist_ok=True)
    if args.study_file:
        study=json.loads(Path(args.study_file).read_text())
    else:study=experiment()
    data=create(study)
    (path/"marathon-dossier.json").write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    (path/"marathon.html").write_text(render(data))
    compact={"registered_group":data["group"],"required_minimum_actions":879,
       "required_verified_decisions":384,
       "author_synthetic_only":True,
       "policies":{p:r["summary"] for p,r in data["records"].items()}}
    (path/"marathon-display-summary.json").write_text(json.dumps(compact,sort_keys=True,indent=2)+"\n")
    print("MARATHON_RECORDS",{p:r["summary"]["actual_serial_actions"] for p,r in data["records"].items()})
    print("MARATHON_VIEWER_BYTES",(path/"marathon.html").stat().st_size)
if __name__=="__main__":main()
