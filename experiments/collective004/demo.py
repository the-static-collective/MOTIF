"""Run bounded grammar invention from a pinned native National Treasure question."""
import argparse
import json
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"collective003"))
from national_treasure_frontier import build_node,verify_node
from question_inventor import run

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--case-root",required=True)
    parser.add_argument("--box-root",required=True)
    args=parser.parse_args()
    q=build_node("same-state-different-world",args.case_root,args.box_root)
    verify_node(q,args.case_root,args.box_root)
    outcome=run(q)
    print(json.dumps(outcome,indent=2,sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
