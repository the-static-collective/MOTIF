"""LLM-001 synthetic *native MOTIF-003* comparison through actual original source.

No external effect or LLM. This adapter deliberately translates an authored
finite action graph into the original MOTIF-003 observer's rewrite ABI.
State reachability is hypothetical; the typed worlds are not physical truths.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
NATIVE=ROOT/"experiments"/"003"/"affordance.py"
sys.path.insert(0,str(NATIVE.parent))
from affordance import actions, analyze_first_moves, select_first_move

def run(case:dict):
    if case.get("schema")!="motif.llm001.world.v0":
        raise ValueError("BAD_FIXTURE")
    moves=case["moves"]
    if len(moves)>100 or any(m["kind"] not in ("probe","simulate","external") for m in moves):
        raise ValueError("BAD_MOVES")
    by_id={m["id"]:m for m in moves}
    if len(by_id)!=len(moves):
        raise ValueError("DUPLICATE_MOVES")
    initial=frozenset(("fact",x) for x in case["facts"])
    def possibilities(world,_verbs):
        facts={x[1] for x in world if x[0]=="fact"}
        done={x[1] for x in world if x[0]=="done"}
        for m in moves:
            if m["kind"]=="external" or m["id"] in done or not set(m["requires"])<=facts:
                continue
            future=world|{("done",m["id"])}|{("fact",f) for f in m["may_grant"]}
            yield m["id"],(),frozenset(future)
    def utility(world,_initial):
        return sum(by_id[x[1]]["immediate"] for x in world if x[0]=="done")
    rows=analyze_first_moves(initial,{},possibilities,utility,horizon=2,max_worlds=500)
    chosen=select_first_move(rows,priority="new-choices")
    return {"native":"experiments/003/affordance.py",
            "source_sha256":hashlib.sha256(NATIVE.read_bytes()).hexdigest(),
            "preferred":chosen["operator"] if chosen else None,
            "ranked":sorted([{"move":r["operator"],
                             "new_choices":len(r["new_affordances"])}
                             for r in rows],key=lambda x:x["move"]),
            "scope":"AUTHOR_BUILT_SYNTHETIC_WORLD_ONLY"}

if __name__=="__main__":
    case=json.load(sys.stdin)
    print(json.dumps(run(case),sort_keys=True))
