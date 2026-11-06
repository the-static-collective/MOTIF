"""Reproducible local test harness, output receipts and review-only patch artifacts."""
from __future__ import annotations
import json
from pathlib import Path
from lab import run_experiment
from solver_factory import Config, generate_source

def main(out=None):
    result, source, diff=run_experiment()
    if out is not None:
        p=Path(out);p.mkdir(parents=True,exist_ok=True)
        (p/"reference_solver.py").write_text(generate_source(Config()))
        (p/"candidate_solver.py").write_text(source)
        (p/"candidate.diff").write_text(diff)
        (p/"experiment-results.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result

if __name__=="__main__":
    p=Path(__file__).resolve().parent
    r=main(p)
    print(json.dumps(r,indent=2,sort_keys=True))
    if r["status"]!="PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED":raise SystemExit(1)
