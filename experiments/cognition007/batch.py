"""COGNITION-007 — 20 preregistered *external* NovelGym environments, static policy.

Does not add MOTIF, change game engine, or use native owner result to pick
actions. Retains every seed even if a particular episode can't complete.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys
import time
import traceback

sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"cognition006"))
from native_smoke import smoke_case,checksum,NOVELGYM_SHA,WORLD_SHA

SEEDS=tuple(20001+13*i for i in range(20))
PAIRS=("none","fire")


def run_batch():
    rows=[]
    errors=[]
    for seed in SEEDS:
        for novelty in PAIRS:
            try:
                row=smoke_case(novelty,seed)
            except Exception as exc:
                row={"seed":seed,"novelty":novelty,
                     "status":"BLOCKED_ENVIRONMENT_EXECUTION",
                     "exception_type":type(exc).__name__,
                     "error":str(exc)[:400],
                     "stack":traceback.format_exc(limit=6)[-1800:],
                     "native_owner_goal_achieved":None}
                errors.append({"seed":seed,"novelty":novelty,"error":str(exc)[:400]})
            rows.append(row)
        current=rows[-2:]
        print(f"native seed {seed}: none={current[0].get('native_owner_goal_achieved')}"
              f" / fire={current[1].get('native_owner_goal_achieved')}",flush=True)
    byseed={seed:{r["novelty"]:r for r in rows if r["seed"]==seed} for seed in SEEDS}
    pairs=[]
    for seed in SEEDS:
        pre=byseed[seed]["none"]
        novelty=byseed[seed]["fire"]
        if any(r.get("native_owner_goal_achieved") is None for r in (pre,novelty)):
            pairs.append({"seed":seed,"status":"UNSCORABLE_RUNTIME_ERROR"})
        else:
            pairs.append({
                "seed":seed,
                "pre_success":pre["native_owner_goal_achieved"],
                "fire_success":novelty["native_owner_goal_achieved"],
                "paired_success_difference":int(pre["native_owner_goal_achieved"])-int(novelty["native_owner_goal_achieved"]),
                "same_initial_actions_before_novelty":(
                    [r["native_action"] for r in pre["native_action_receipts"][:14]]
                    ==[r["native_action"] for r in novelty["native_action_receipts"][:14]])
            })
    scored=[x for x in pairs if x["status"]!="UNSCORABLE_RUNTIME_ERROR"] if False else [
        x for x in pairs if x.get("status")!="UNSCORABLE_RUNTIME_ERROR"]
    summary={"n_fixed_seeds":len(SEEDS),"n_world_episodes":len(rows),
             "n_scored_pairs":len(scored),"runtime_errors":len(errors),
             "owner_pre_goal_victories":sum(r["native_owner_goal_achieved"] is True for r in rows if r["novelty"]=="none"),
             "owner_fire_goal_victories":sum(r["native_owner_goal_achieved"] is True for r in rows if r["novelty"]=="fire"),
             "paired_pre_success_fire_fail":sum(x["paired_success_difference"]==1 for x in scored),
             "same_fourteen_action_prefix":sum(x["same_initial_actions_before_novelty"] for x in scored),
             "original_policy":"BasePlanningAgent+Metric-FF, nonadaptive",
             "motif_policy_executed":False,
             "strong_adaptive_baseline_executed":False}
    report={"experiment":"COGNITION-007","phase":"REAL_NATIVE_NOVELGYM_NONADAPTIVE_GAP_PREVALENCE",
            "novelgym_source_sha":NOVELGYM_SHA,"world_source_sha":WORLD_SHA,
            "python": "3.10","metric_ff_compile":"UPSTREAM_C_SOURCE -O0 -ansi -fno-strict-aliasing -g",
            "seeds":SEEDS,"summary":summary,"pairs":pairs,
            "cases":rows,"runtime_errors":errors}
    report["sha256"]=checksum(report)
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    outcome=run_batch()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(outcome,indent=2,sort_keys=True)+"\n")
    if outcome["runtime_errors"]:
        raise SystemExit(f"Native execution errors in {len(outcome['runtime_errors'])} seeds")
