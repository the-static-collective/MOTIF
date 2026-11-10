"""QC-013: ACTUAL out-of-dataset Crafter intervention inspired by human traces.

Deliberately narrow falsifier:
  Baseline = unchanged QC-012 local-tile controller.
  Candidate = same sensor and baseline, plus a *hand-coded* resource/hostile
  priority adapted from observed expert affordances.
  Fairness: both use the identical privileged radius-7 local-tile sensor,
  game seed, action budget, and environment code. They are NOT learned ML.
  Provenance: episode counts from 100 human runs license the hypotheses,
  not the algorithm's validity or safety in the physical world.
"""
from __future__ import annotations
import collections
import json
import os
from pathlib import Path
import sys

import crafter
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"quantumcode012"))
from play_crafter import Controller,run,DIRS,WALK
DATA=json.loads((HERE/"observed_100_episodes.json").read_text())
N=DATA["episodes"]
HITS=DATA["achievements_in_episode"]


def evidence_gate():
    if (N!=100 or
        DATA["source_archive_sha256"]!="7dc2589de4a246035f2fefb151bd8afac85d68d62c90311bc3afe9cca2b053e2"):
        raise ValueError("Human lesson has unknown evidence receipt")
    # Some candidate priorities are intentionally manually chosen after
    # reading achievement frequencies. Counts do NOT prove causality.
    return {
        "seek_cow_food":HITS["eat_cow"]>=75,
        "seek_water":HITS["collect_drink"]>=75,
        "watch_hostile":HITS["defeat_zombie"]>=75,
        "construction_not_the_only_goal":HITS["place_furnace"]<HITS["eat_cow"],
    }


ORIGINAL_ACT=Controller.act


def pursue_object(actor,env,cls):
    pos=actor.pos(env)
    goals=[]
    for dx in range(-7,8):
        for dy in range(-7,8):
            if abs(dx)+abs(dy)>7:continue
            p=(pos[0]+dx,pos[1]+dy)
            tile=actor.tile(env,p)
            if tile and isinstance(tile[1],cls):
                goals.append(p)
    if not goals:return None
    # Breadth-first search within the *same radius* as the baseline.
    queue=collections.deque((pos,))
    prev={pos:None}
    while queue:
        p=queue.popleft()
        for a,d in DIRS.items():
            q=(p[0]+d[0],p[1]+d[1])
            if q in prev:continue
            cell=actor.tile(env,q,pos)
            if not cell or cell[0] not in WALK or cell[1] is not None:
                continue
            prev[q]=p
            queue.append(q)
    paths=[]
    for target in goals:
        for d in DIRS.values():
            stand=(target[0]+d[0],target[1]+d[1])
            if stand not in prev:continue
            path=[]
            p=stand
            while prev[p] is not None:
                path.append(p);p=prev[p]
            path.reverse()
            paths.append((len(path),target,path))
    if not paths:return None
    _,target,path=min(paths,key=lambda x:(x[0],x[1]))
    if path:
        vector=(path[0][0]-pos[0],path[0][1]-pos[1])
        return next(a for a,d in DIRS.items() if d==vector),"seek_living_food"
    delta=(target[0]-pos[0],target[1]-pos[1])
    if tuple(env._player.facing)!=delta:
        return next(a for a,d in DIRS.items() if d==delta),"face_living_food"
    return "do","acquire_living_food"


def nearby_enemies(actor,env,radius=4):
    pos=actor.pos(env)
    hostiles=[]
    for dx in range(-radius,radius+1):
        for dy in range(-radius,radius+1):
            if abs(dx)+abs(dy)>radius:continue
            p=(pos[0]+dx,pos[1]+dy)
            tile=actor.tile(env,p)
            if tile and isinstance(tile[1],(crafter.objects.Zombie,
                                            crafter.objects.Skeleton)):
                hostiles.append(p)
    return hostiles


def escape_if_needed(actor,env):
    pos=actor.pos(env)
    hostiles=nearby_enemies(actor,env)
    if not hostiles:return None
    def worst(p):
        return min(abs(p[0]-h[0])+abs(p[1]-h[1]) for h in hostiles)
    now=worst(pos)
    if now>3:return None
    moves=[]
    for a,d in DIRS.items():
        q=(pos[0]+d[0],pos[1]+d[1])
        cell=actor.tile(env,q)
        if not cell or cell[0] not in WALK or cell[1] is not None:continue
        moves.append((worst(q),-actor.visited[q],actor.rng.random(),a))
    if moves:
        best=max(moves)
        if best[0]>now:
            return best[-1],"retreat_from_observed_game_hostile"
    # If no retreat improves distance, preserve baseline choice. This is
    # a hypothesis, NOT proven tactical safety.
    return None


def expert_informed_act(actor,env):
    gates=evidence_gate()
    inv=env._player.inventory
    # Prioritize *observed* urgent in-game resource needs over maximizing
    # structures. The numerical trigger is hand authored, not learned.
    if gates["watch_hostile"]:
        escape=escape_if_needed(actor,env)
        if escape:return escape
    if gates["seek_water"] and inv["drink"]<=5:
        water=actor.approach(env,"water")
        if water:return water[0],"human_motivated_"+water[1]
    if gates["seek_cow_food"] and inv["food"]<=6:
        hunt=pursue_object(actor,env,crafter.objects.Cow)
        if hunt:return hunt
    if inv["energy"]<=3 and inv["food"]>2 and inv["drink"]>2:
        # Crafter's actual source applies severe damage during sleep when
        # enemies strike: scan the same 7-tile exposed debug radius.
        if not nearby_enemies(actor,env,radius=7):
            return "sleep","recover_game_energy"
    # Reenter from failed affordance: the *original* controller repeatedly
    # tried crafting a tool after the table had become inaccessible.
    # Here the missing physical precondition, not another "make" command,
    # becomes the next subgoal. This is a hand-coded field-correction rule.
    if (inv["wood"]>=1 and env._player.achievements["place_table"]>0
        and inv["wood_pickaxe"]==0):
        near, _ = env._world.nearby(env._player.pos,1)
        if "table" not in near:
            back=actor.approach(env,"table")
            if back:
                return back[0],"restore_missing_table_precondition"
            return actor.explore(env)[0],"search_for_lost_crafting_table"
    return ORIGINAL_ACT(actor,env)


def bench():
    root=Path(os.environ.get("QC013_OUTPUT_DIR","runs/crafter-qc013"))
    root.mkdir(parents=True,exist_ok=True)
    specs=(1042,2026,3199,8765)
    results=[]
    for seed in specs:
        print("QC013_SEED="+str(seed),flush=True)
        # Separate game initializations with identical seed. The sensors
        # and game version are the same, though different actions lead to
        # different generated encounters.
        before=run(seed,220,"local_debug",root/f"{seed}-baseline")
        Controller.act=expert_informed_act
        try:
            after=run(seed,220,"human_informed",root/f"{seed}-human_informed")
        finally:
            Controller.act=ORIGINAL_ACT
        results.append({
            "seed":seed,
            "baseline_steps":before["real_engine_steps"],
            "candidate_steps":after["real_engine_steps"],
            "baseline_achievements":len(before["achievements"]),
            "candidate_achievements":len(after["achievements"]),
            "baseline_final_health":before["final_inventory"]["health"],
            "candidate_final_health":after["final_inventory"]["health"],
            "baseline_food":before["final_inventory"]["food"],
            "candidate_food":after["final_inventory"]["food"],
        })
    record={
        "experiment":"QC013-HUMAN-INFORMED-INTERVENTION",
        "evidence_source_sha256":DATA["source_archive_sha256"],
        "controller":"HAND_WRITTEN_TRANSLATION_OF_100_EPISODE_HYPOTHESES",
        "same_privileged_local_tile_sensor":True,
        "matched_seed_count":len(specs),
        "paired_results":results,
        "human_demo_train_or_test_seed_match_known":False,
        "policy_is_fitted_neural_model":False,
        "policy_is_independently_human_validated":False,
        "causal_improvement_proven":False,
        "real_world_actions":0,
    }
    (root/"paired_results.json").write_text(
        json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("QC013_PAIR_RESULTS="+json.dumps(record,sort_keys=True),
          flush=True)


if __name__=="__main__":
    bench()
