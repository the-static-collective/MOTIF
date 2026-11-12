"""Locked COGNITION-008 grammar on untouched native NovelGym novelty mechanisms.

No policy tweaks or manual goal description. All cases retained, including
runtime errors and failure-to-adapt. This is NOT a strong classical SOTA contest.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import argparse
import json
import sys
import traceback

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"cognition008"))
from adapt import run_policy,POLICIES
from native_smoke import checksum

NOVELTIES=("fence","axe","chest","dist_trade")
SEEDS=(31001,31021,31041)


def run_all():
    rows=[]
    for novelty in NOVELTIES:
        for seed in SEEDS:
            for policy in POLICIES:
                try:
                    trial=run_policy(policy,seed,novelty)
                    trial["status"]="EXECUTED_IN_ORIGINAL_WORLD"
                except Exception as exc:
                    trial={"policy":policy,"novelty":novelty,"seed":seed,
                           "status":"BLOCKED_NATIVE_OR_ADAPTER_RUNTIME",
                           "verified_owner_success":None,
                           "recovery_owner_success":None,
                           "original_planner_owner_success":None,
                           "exception_type":type(exc).__name__,
                           "error":str(exc)[:800],
                           "traceback":traceback.format_exc(limit=7)[-2000:]}
                rows.append(trial)
            current=rows[-2:]
            print(f"{novelty}/{seed}: "+
                  ", ".join(f"{r['policy']}={r['verified_owner_success']} [{r['status']}]"
                            for r in current),flush=True)
    summary={}
    for novelty in NOVELTIES:
        summary[novelty]={}
        for policy in POLICIES:
            segment=[r for r in rows if r["novelty"]==novelty and r["policy"]==policy]
            summary[novelty][policy]={
                "original_cases":len(segment),
                "native_engine_runtime_errors":sum(x["verified_owner_success"] is None for x in segment),
                "original_planner_solved_without_recovery":sum(x.get("original_planner_owner_success") is True for x in segment),
                "owner_verified_recovery_successes":sum(x.get("recovery_owner_success") is True for x in segment),
                "owner_verified_all_goal_successes":sum(x.get("verified_owner_success") is True for x in segment),
                "recovery_actions":sum(x.get("observed_recovery_actions",0) for x in segment),
                "attempts_used":sum(x.get("attempts_used",0) for x in segment)}
    paired=[]
    for novelty in NOVELTIES:
        for seed in SEEDS:
            m=next(x for x in rows if x["novelty"]==novelty and x["seed"]==seed and
                   x["policy"]=="motif_adaptive")
            c=next(x for x in rows if x["novelty"]==novelty and x["seed"]==seed and
                   x["policy"]=="classical_adaptive")
            paired.append({"novelty":novelty,"seed":seed,
                           "motif_owner_success":m["verified_owner_success"],
                           "classical_owner_success":c["verified_owner_success"],
                           "motif_minus_classical_recovery":(
                               int(m["recovery_owner_success"])-
                               int(c["recovery_owner_success"])
                               if m["recovery_owner_success"] is not None and
                                  c["recovery_owner_success"] is not None else None)})
    report={"experiment":"COGNITION-009","status":"LOCKED_GRAMMAR_UNSEEN_NOVELTIES_NOT_SOTA",
            "real_native_external_environment":True,
            "original_novelgym_sha":"0ad2cbb656177f76ff29f86793269b14879d9b89",
            "original_world_sha":"f5d06d4f5166ca985ca420c809129a79700d904e",
            "novelties":NOVELTIES,"seeds":SEEDS,"policies":POLICIES,
            "n":len(rows),"summary":summary,"paired":paired,"rows":rows,
            "policies_locked_from_commit":"76f797e920aee74bfab065744b051eb5fd34084a",
            "motif_not_claimed_to_beat_strong_model_learning":True}
    report["sha256"]=checksum(report)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    out=run_all()
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2,default=str)+"\n")
    print(json.dumps(out["summary"],sort_keys=True,indent=2))
    if any(r["verified_owner_success"] is None for r in out["rows"]):
        raise SystemExit("Original native world runtime or adapter errors; full receipts archived.")
