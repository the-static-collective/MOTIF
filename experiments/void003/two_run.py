"""VOID-003: actual two-episode Crafter memory-transfer experiment.

First round scouts using original VOID-002 policies; second round deliberately
uses the SAME conventional controller for both memory treatments. Game resets
between rounds; remembered map is a hypothesis, not an observable game state.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import importlib.metadata
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/"void002"))
from frontier import choose
from memory import EpisodicMap,seal,waypoint_action,signature

SOURCE_PIN="7e35ab7157755c83c6353e939a2ae1b018d70667"
PINNED=ROOT/"sources"/"qc017"/"experiments"
DEV_SEEDS=(1042,2026,3199,8765)
TEST_SEEDS=(27011,27013,27017,27019,27023,27029)
MAX_ACTIONS=70
GOALS=("game_wood_obtained","game_drink_obtained")
SCOUTS=("classical_2ply","motif003")
FOLLOWUPS=("no_memory","classical_memory","motif_memory")


def source_modules():
    for p in (PINNED/"quantumcode017",PINNED/"quantumcode012"):
        if str(p) not in sys.path:
            sys.path.insert(0,str(p))
    from plan import observe,traverse,check_goals
    from play_crafter import ACTS,Controller
    return observe,traverse,check_goals,ACTS,Controller


def game_episode(seed,scout_policy=None,followup_memory=None,stage="scout"):
    """Return verified action evidence and optional historical observation map."""
    if seed not in DEV_SEEDS+TEST_SEEDS or stage not in ("scout","followup"):
        raise ValueError("UNREGISTERED_SEED_OR_STAGE")
    if stage=="scout" and scout_policy not in SCOUTS:
        raise ValueError("UNREGISTERED_SCOUT_POLICY")
    if stage=="followup" and scout_policy is not None:
        raise ValueError("FOLLOWUP_POLICY_MUST_BE_IDENTICAL")
    import crafter
    if importlib.metadata.version("crafter")!="1.8.3":
        raise RuntimeError("GAME_VERSION_MISMATCH")
    observe,traverse,check_goals,ACTS,Controller=source_modules()
    env=crafter.Env(seed=seed,length=MAX_ACTIONS,view=(9,9),size=(64,64))
    env.reset()
    if env._player not in env._world.objects:
        raise RuntimeError("PLAYER_OBJECT_NOT_ACTIVE")
    actor=Controller(seed)
    seen=set();visited=Counter();actions=[];num_no_effect=0
    attained={g:False for g in GOALS}
    history=EpisodicMap(seed) if stage=="scout" else None
    admitted=None
    hints=0;used_exploration_mem=0
    termination="ACTION_BUDGET_EXHAUSTED"
    for tick in range(MAX_ACTIONS):
        if all(attained.values()):
            termination="BOTH_GOALS_WITNESSED";break
        goal=next(g for g in GOALS if not attained[g])
        belief=observe(env,actor,f"crafter:1.8.3:seed{seed}:stage{stage}:turn{tick}:r7")
        if tick==0:
            # All packet admissions occur before any second-round action.
            if stage=="scout":
                history.first_signature=signature(belief)
                history.start=tuple(belief.start)
            elif followup_memory is not None:
                admitted=EpisodicMap.admit(followup_memory,seed,belief)
        if history is not None:
            history.remember(belief)
        visible={c.xy for c in belief.cells}
        seen.update(visible)
        visited[belief.start]+=1
        planned=traverse(belief,goal)
        memory_hint=None
        if planned.status=="PLAN_CANDIDATE":
            action=planned.actions[0]
            reason="COMMON_LIVE_OBSERVED_TARGET_BFS"
        else:
            if stage=="followup" and admitted:
                memory_hint=waypoint_action(belief,admitted,goal)
            if memory_hint:
                action=memory_hint["action"]
                reason="HISTORICAL_WAYPOINT_NEXT_STEP_CURRENTLY_VERIFIED"
                hints+=1
            else:
                # Both follow-up memory arms use *the same* classical method.
                relevant_seen=seen | (admitted.coordinates if admitted else frozenset())
                action=choose(belief,relevant_seen,visited,
                              scout_policy if stage=="scout" else "classical_2ply")
                reason="COMMON_CLASSICAL_FRONTIER" if stage=="followup" else f"SCOUT_{scout_policy}"
                if stage=="followup" and admitted:
                    used_exploration_mem+=1
        if action is None:
            termination="HOLD_NO_WITNESSED_NEXT_ACTION";break
        if action not in ACTS:
            raise RuntimeError("UNREVIEWED_GAME_ACTION")
        inv_before=dict(env._player.inventory)
        ach_before=dict(env._player.achievements)
        pos_before=tuple(int(x) for x in env._player.pos)
        face_before=tuple(int(x) for x in env._player.facing)
        _,rew,done,info=env.step(ACTS.index(action))
        inv_after=dict(info["inventory"])
        ach_after=dict(info["achievements"])
        pos_after=tuple(int(v) for v in env._player.pos)
        face_after=tuple(int(v) for v in env._player.facing)
        witness=check_goals(inv_before,inv_after,ach_before,ach_after,goal)
        if witness!="GOAL_NOT_YET_WITNESSED":
            attained[goal]=True
        changed=(pos_after!=pos_before or face_after!=face_before or
                 inv_after!=inv_before or ach_after!=ach_before)
        num_no_effect+=int(not changed)
        row={"tick":tick+1,"goal":goal,"action":action,"reason":reason,
             "currently_seen_count":len(visible),"sensor_pin":belief.pin,
             "plan_status":planned.status,"before_pos":pos_before,"after_pos":pos_after,
             "before_facing":face_before,"after_facing":face_after,
             "before_target_resource":int(inv_before.get("wood" if "wood" in goal else "drink",0)),
             "after_target_resource":int(inv_after.get("wood" if "wood" in goal else "drink",0)),
             "verified_goal_outcome":witness,"changed_in_engine":changed,
             "game_reward":float(rew),"terminal":bool(done),
             "historical_hint_was_only_conditional":bool(memory_hint),
             "source_is_synthetic":False}
        row["seal"]=seal(row)
        actions.append(row)
        if done:
            termination="ENGINE_TERMINATED";break
    else:
        termination="ACTION_BUDGET_EXHAUSTED"
    if all(attained.values()):
        termination="BOTH_GOALS_WITNESSED"
    result={"seed":seed,"stage":stage,"policy":scout_policy if stage=="scout" else "common_classical_2ply",
            "verified_goals":attained,"goal_count":sum(attained.values()),
            "actions":len(actions),"no_effect":num_no_effect,
            "seen_coordinate_count":len(seen),
            "saw_historical_memory":stage=="followup" and admitted is not None,
            "used_historical_waypoint_steps":hints,
            "used_memory_adjusted_frontier_steps":used_exploration_mem,
            "termination":termination,"engine":"UNMODIFIED_CRAFTER_1_8_3",
            "privileged_source_sensor":True,"real_world_actions":0,
            "game_world_modified_by_researcher":False,
            "source_code_ref":SOURCE_PIN,"action_receipts":actions}
    if stage=="scout":
        packet=history.export()
        result["map_memory_packet"]=packet
        result["historical_resource_cells"]={m:sum(x[0]==m for x in history.cells.values())
                                             for m in ("tree","water")}
    result["seal"]=seal(result)
    return result


def net(scout,followup):
    return round(followup["goal_count"]-.1*(scout["actions"]+followup["actions"])/(2*MAX_ACTIONS)
                 -.05*(scout["no_effect"]+followup["no_effect"])/(2*MAX_ACTIONS),9)


def mean(xs):
    return round(sum(xs)/len(xs),9) if xs else None


def benchmark():
    cases=[]
    for seed in DEV_SEEDS+TEST_SEEDS:
        scouts={p:game_episode(seed,p,stage="scout") for p in SCOUTS}
        followups={"no_memory":game_episode(seed,stage="followup")}
        for policy in SCOUTS:
            key=("motif_memory" if policy=="motif003" else "classical_memory")
            followups[key]=game_episode(seed,followup_memory=scouts[policy]["map_memory_packet"],stage="followup")
        m=scouts["motif003"]["map_memory_packet"]["historical_cells"]
        c=scouts["classical_2ply"]["map_memory_packet"]["historical_cells"]
        km={tuple(t[0]) for t in m};kc={tuple(t[0]) for t in c}
        resource_m={tuple(t[0]) for t in m if t[1] in ("tree","water")}
        resource_c={tuple(t[0]) for t in c if t[1] in ("tree","water")}
        cases.append({"seed":seed,"split":"development" if seed in DEV_SEEDS else "heldout",
                      "scouts":scouts,"followups":followups,
                      "motif_only_coordinates":len(km-kc),
                      "classical_only_coordinates":len(kc-km),
                      "motif_only_resource_coordinates":len(resource_m-resource_c),
                      "classical_only_resource_coordinates":len(resource_c-resource_m),
                      "paired_net":{
                          "motif_memory":net(scouts["motif003"],followups["motif_memory"]),
                          "classical_memory":net(scouts["classical_2ply"],followups["classical_memory"]),
                          "motif_no_memory":net(scouts["motif003"],followups["no_memory"]),
                          "classical_no_memory":net(scouts["classical_2ply"],followups["no_memory"]),
                      }})
    groups={}
    for split in ("development","heldout"):
        sub=[c for c in cases if c["split"]==split]
        measures={name:mean([c["paired_net"][name] for c in sub])
                  for name in ("motif_memory","classical_memory","motif_no_memory","classical_no_memory")}
        groups[split]={"episodes":len(sub),"mean_two_run_net":measures,
                       "primary_deltas":{
                           "motif_memory_minus_classical_memory":round(measures["motif_memory"]-measures["classical_memory"],9),
                           "motif_memory_minus_motif_no_memory":round(measures["motif_memory"]-measures["motif_no_memory"],9),
                           "classical_memory_minus_classical_no_memory":round(measures["classical_memory"]-measures["classical_no_memory"],9),
                       },
                       "followup_verified_goals":{
                           p:sum(c["followups"][p]["goal_count"] for c in sub)
                           for p in FOLLOWUPS},
                       "mean_initial_seen":{
                           p:mean([c["scouts"][p]["seen_coordinate_count"] for c in sub])
                           for p in SCOUTS},
                       "mean_exclusive_map_positions":{
                           k:mean([c[k] for c in sub])
                           for k in ("motif_only_coordinates","classical_only_coordinates",
                                     "motif_only_resource_coordinates","classical_only_resource_coordinates")}}
    output={"experiment":"VOID-003","status":"RESEARCH_HOLD_TWO_REAL_GAME_EPISODES",
            "source_dependency_sha":SOURCE_PIN,"game_version":"1.8.3",
            "game_world_reset_each_episode":True,
            "only_historical_information_transfers":True,
            "primary":"SECOND_ROUND_VERIFIED_GOALS_MINUS_TWO_ROUND_ACTION_COSTS",
            "model_calls":0,"paid_services":0,
            "source_code_untouched":True,"real_world_actions":0,
            "case_count":len(cases),"episode_count":5*len(cases),
            "total_game_steps":sum(sum(r["actions"] for r in c["scouts"].values())+
                                    sum(r["actions"] for r in c["followups"].values()) for c in cases),
            "results":groups,"cases":cases,
            "limits":["no blind third-party task administration",
                      "second round uses same seed game reset, not continuous same-world play",
                      "recalled tile data is historical and may be stale",
                      "all policies share privileged game-internal radius-seven sensor",
                      "second-run controller is classical and identical across arms",
                      "not proof of autonomous multi-run planning or general intelligence",
                      "different action trajectories may encounter divergent stochastic events"]}
    output["seal"]=seal(output)
    return output


if __name__=="__main__":
    output=benchmark()
    output_file=ROOT/"void003-two-run-crafter-audit.json"
    output_file.write_text(json.dumps(output,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in output.items() if k!="cases"},sort_keys=True,indent=2))
