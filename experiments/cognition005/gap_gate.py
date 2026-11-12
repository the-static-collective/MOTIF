"""COGNITION-005 audit gate: never advertise a 'classical failure' without fair arms.

This does NOT run NovelGym, access the internet, invoke MOTIF or verify real
third-party results. The official owners and their environment adapters must
supply observed receipts. Local fixture seals are *not* authentication.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import argparse
import json

ROOT=Path(__file__).resolve().parent
REQUIRED=("static_pddl","strong_adaptive_classical",
          "upstream_hybrid_rapidlearn","motif_cognition")
PRIMARY="novelgym/fire"
SCHEMA="motif.gap-hunt-evaluation/v0"

def audit(envelope):
    """Fail closed: require matched independent external task evidence."""
    if not isinstance(envelope,dict) or envelope.get("schema")!=SCHEMA:
        return {"status":"HOLD_BAD_SCHEMA"}
    rows=envelope.get("rows")
    if not isinstance(rows,list) or not rows:
        return {"status":"HOLD_NO_EXTERNAL_TRIALS",
                "motif_outperformed_strong_classical":None}
    if envelope.get("source")!="EXTERNALLY_EXECUTED_NOVELGYM":
        return {"status":"HOLD_NOT_EXTERNAL_ENVIRONMENT"}
    if envelope.get("predeclared_task")!=PRIMARY:
        return {"status":"HOLD_UNREGISTERED_PRIMARY_TASK"}
    if envelope.get("protocol_frozen") is not True or envelope.get("source_pin")!="0ad2cbb656177f76ff29f86793269b14879d9b89":
        return {"status":"HOLD_UNVERIFIED_PROTOCOL_OR_PIN"}
    obs={}
    seeds=set()
    for r in rows:
        if not isinstance(r,dict):
            return {"status":"HOLD_UNSTRUCTURED_ROW"}
        required={"seed","policy","novelty","pre_solved","immediate_post_solved",
                  "post_solved_by_budget","actions_used","cpu_seconds",
                  "owner_receipt","environment_sha","action_budget"}
        if not required.issubset(r):
            return {"status":"HOLD_MISSING_OUTCOME_OR_OWNER_RECEIPT"}
        if not isinstance(r["seed"],int) or r["policy"] not in REQUIRED or r["novelty"]!="fire":
            return {"status":"HOLD_BAD_CASE_SCOPE"}
        if not all(type(r[k]) is bool for k in ("pre_solved","immediate_post_solved","post_solved_by_budget")):
            return {"status":"HOLD_NOT_BOOLEAN_TASK_OUTCOME"}
        if not isinstance(r["owner_receipt"],dict) or r["owner_receipt"].get("independent_environment_owner") is not True:
            return {"status":"HOLD_NO_OWNER_VERIFICATION"}
        if not isinstance(r["actions_used"],int) or r["actions_used"]<0:
            return {"status":"HOLD_BAD_ACTION_ACCOUNTING"}
        if not isinstance(r["cpu_seconds"],(int,float)) or r["cpu_seconds"]<0:
            return {"status":"HOLD_BAD_CPU_ACCOUNTING"}
        if not isinstance(r["action_budget"],int) or r["action_budget"]<1:
            return {"status":"HOLD_BAD_ACTION_BUDGET"}
        if r["environment_sha"]!="0ad2cbb656177f76ff29f86793269b14879d9b89":
            return {"status":"HOLD_WRONG_ENVIRONMENT_SOURCE"}
        key=(r["seed"],r["policy"])
        if key in obs:
            return {"status":"HOLD_DUPLICATE_CASE","case":list(key)}
        obs[key]=r
        seeds.add(r["seed"])
    matched=[]
    for seed in sorted(seeds):
        if any((seed,p) not in obs for p in REQUIRED):
            return {"status":"HOLD_UNMATCHED_ARMS","seed":seed}
        g=[obs[(seed,p)] for p in REQUIRED]
        if len({x["action_budget"] for x in g})!=1:
            return {"status":"HOLD_UNMATCHED_ACTION_BUDGET","seed":seed}
        if len({x["environment_sha"] for x in g})!=1:
            return {"status":"HOLD_UNMATCHED_ENVIRONMENT","seed":seed}
        if any(r["actions_used"]>r["action_budget"] for r in g):
            return {"status":"HOLD_OVER_BUDGET","seed":seed}
        matched.append((seed,{p:obs[(seed,p)] for p in REQUIRED}))
    if len(matched)<20:
        return {"status":"HOLD_TOO_FEW_MATCHED_SEEDS",
                "matched":len(matched),"minimum":20}
    counts={p:sum(row[p]["post_solved_by_budget"] for _,row in matched)
            for p in REQUIRED}
    direct=[(int(row["motif_cognition"]["post_solved_by_budget"])
             -int(row["strong_adaptive_classical"]["post_solved_by_budget"]))
            for _,row in matched]
    wins=sum(x==1 for x in direct)
    losses=sum(x==-1 for x in direct)
    ties=sum(x==0 for x in direct)
    # A directional descriptive difference alone is NOT a statistical claim.
    return {"status":"SCORABLE_DESCRIPTIVE_ONLY",
            "matched_seeds":len(matched),"wins":counts,
            "motif_minus_adaptive_pairwise":{"wins":wins,"losses":losses,"ties":ties},
            "motif_outperformed_strong_classical":None,
            "inferential_statistics":"NOT_YET_CALCULATED_OR_REVIEWED",
            "warning":"Local receipt claim is not independent authenticity proof; inspect owner logs manually before scientific claim.",
            "static_planner_failure_not_sufficient_for_novelty_claim":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--results",type=Path,help="Externally executed, independently verified JSON envelope; absent => HOLD")
    opts=p.parse_args()
    data=json.loads(opts.results.read_text()) if opts.results else {"schema":SCHEMA,"rows":[]}
    print(json.dumps(audit(data),indent=2,sort_keys=True))
if __name__=="__main__":
    main()
