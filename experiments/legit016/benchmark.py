"""Run LEGIT-016 retrospective + new source-anchored measured episode.

This is a new *measurement* of real generated code, not another source
rewrite or an independently blinded trial. Its result is a hard HOLD
until a separate external benchmark and source-custody witness exist.
"""
from __future__ import annotations
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from evidence import archive,summarize
from measurement import measure
from decision import compare

def execute():
    new_episode=measure()
    decision=compare(new_episode)
    if decision["promotion_decision"]!="HOLD_NOT_ENOUGH_INDEPENDENT_EVIDENCE":
        raise AssertionError("No external-validation authority exists")
    if decision["observed_compounding_rate"]!="NOT_ESTIMABLE":
        raise AssertionError("Researcher-generated task timings are not compounding calibration")
    return decision

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("Usage: python experiments/legit016/benchmark.py [--emit]")
    report=execute()
    if sys.argv[1:]:
        target=Path("/tmp/motif-legit016-empirical-witness.json")
        target.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",
                          encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
