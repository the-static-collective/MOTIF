"""Produce review packet; no install, no repo writes or arbitrary model code."""
from pathlib import Path
from program import CHAT_MODEL_PROPOSAL,MONOTONE_BASELINE,generate_source
from lab import run_experiment
import json

def main(dest=None,candidate=CHAT_MODEL_PROPOSAL):
    dest=Path(dest or Path(__file__).resolve().parent)
    dest.mkdir(parents=True,exist_ok=True)
    result,source,diff=run_experiment(candidate)
    (dest/'experiment-results.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    (dest/'monotone_reference.py').write_text(generate_source(MONOTONE_BASELINE))
    (dest/'candidate_solver.py').write_text(source)
    (dest/'candidate.diff').write_text(diff)
    return result

if __name__=='__main__':
    r=main();print(json.dumps({k:r[k] for k in ('status','truth_table','development','safety','developer_probes','frozen_audit','stress','installed')},indent=2));
    if r['status']!='PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED':raise SystemExit(1)
