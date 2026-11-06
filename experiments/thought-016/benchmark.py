"""Produce operator-reviewable code/diff and experiment receipts (local only)."""
from pathlib import Path
import json
import sys
from lab import run_lab

def main(destination=None):
    report,old,new,diff=run_lab()
    if destination is not None:
        p=Path(destination);p.mkdir(parents=True,exist_ok=True)
        for name,data in [('reference_solver.py',old),('candidate_solver.py',new),('candidate.diff',diff),
                          ('experiment-results.json',json.dumps(report,sort_keys=True,indent=2)+'\n')]:
            (p/name).write_text(data,encoding='utf-8')
    return report
if __name__=='__main__':
    result=main(Path(__file__).resolve().parent if len(sys.argv)==1 else Path(sys.argv[1]))
    print(json.dumps({key:result[key] for key in ('status','model_kind','development','audit','stress','safety',
         'installed_fragments','model_test_result','receipt_digest')},indent=2))
    if result['status']!='PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED':sys.exit(1)
