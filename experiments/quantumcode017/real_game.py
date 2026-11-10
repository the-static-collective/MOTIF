"""QC-017: actual third-party Crafter executed-world probe-planner benchmark.

The game world is deliberately edited for controlled tests. This module never
claims to have solved unmodified open-world survival, discovered unknown
physics, or produced real-life advice. Both planners read the same *privileged*
radius-seven local engine tiles. One uses shortest-path BFS over observed
(position,facing) states; the comparator uses a simple Manhattan heuristic
that may repeat an ineffective blocked move. The latter is NOT a strong
planning baseline; BFS itself IS classical planning.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import crafter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"quantumcode012"))
sys.path.insert(0,str(ROOT/"quantumcode011"))

from play_crafter import ACTS,Controller,snapshot,encode_state
from game_replay import Episode,Replay,relatte_preview
from plan import observe,traverse,check_goals,GOAL_RULES

SEEDS=(1042,2026,3199,8765)
SCENARIOS={
    "north_water": {"offset":(0,-3),"material":"water","walls":()},
    "east_detour": {"offset":(3,0),"material":"water","walls":((1,0),(2,0))},
    "south_water": {"offset":(0,3),"material":"water","walls":()},
    "west_detour": {"offset":(-3,0),"material":"water","walls":((-1,0),(-2,0))},
    "surprise_wall": {"offset":(0,-4),"material":"water","walls":(),
                      "surprise":(0,-2)},
    "tree_acquisition":{"offset":(3,-1),"material":"tree","walls":()},
    "hidden_resource":{"offset":(0,-8),"material":"water","walls":(),
                       "not_in_sensor":True},
}


def setup(env,name):
    """Fully enumerated, controlled game-only changes, not natural gameplay."""
    desc=SCENARIOS[name]
    p=tuple(int(x) for x in env._player.pos)
    if not (10<=p[0]<=53 and 10<=p[1]<=53):
        raise ValueError("Cannot safely initialize bounded synthetic game region")
    changed=0
    # Remove all initial game hazards and unknown materials in *current* local
    # sensing aperture. This is a controlled geometry benchmark, not survival.
    for dx in range(-7,8):
        for dy in range(-7,8):
            if abs(dx)+abs(dy)>7:
                continue
            cell=(p[0]+dx,p[1]+dy)
            old,obj=env._world[cell]
            if obj is not None:
                env._world.remove(obj)
            env._world[cell]="grass"
            changed+=1
    for dx,dy in desc["walls"]:
        env._world[(p[0]+dx,p[1]+dy)]="stone"
    dest=tuple(p[i]+desc["offset"][i] for i in (0,1))
    outside=False
    if desc.get("not_in_sensor"):
        outside=True
        old,obj=env._world[dest]
        if obj is not None:env._world.remove(obj)
    env._world[dest]=desc["material"]
    env._player.inventory["drink"]=3
    env._player.inventory["food"]=9
    env._player.inventory["health"]=9
    env._player.inventory["energy"]=9
    env._player.inventory["wood"]=0
    return {
        "type":"EXPLICITLY_MODIFIED_CRAFTER_START",
        "scenario":name,
        "sensor_radius":7,
        "origin":p,"resource_position":dest,
        "resource_material":desc["material"],
        "resource_outside_current_sensor":outside,
        "cleared_local_cells":changed,
        "obstacle_offsets":desc["walls"],
        "simulator_seed":env._seed if hasattr(env,"_seed") else None,
        "real_world_authority":False,
    }


def greedy_step(belief,goal):
    """Independent weak heuristic; intentionally lacks obstacle planning."""
    material,_=GOAL_RULES[goal]
    targets=sorted((c.xy for c in belief.cells if c.material==material and
                    not c.object_present),
                   key=lambda v:(abs(v[0]-belief.start[0])+
                                 abs(v[1]-belief.start[1]),v))
    if not targets:
        return None
    target=targets[0]
    dx=target[0]-belief.start[0]
    dy=target[1]-belief.start[1]
    if abs(dx)+abs(dy)==1:
        needed=((dx,dy))
        if belief.facing==needed:
            return "do"
    if abs(dx)>=abs(dy) and dx:
        return "move_right" if dx>0 else "move_left"
    if dy:
        return "move_down" if dy>0 else "move_up"
    return None


def run(seed,scenario,mode,outdir,limit=19):
    if mode not in ("bfs","greedy"):
        raise ValueError("Unknown policy")
    env=crafter.Env(seed=seed,length=limit,view=(9,9),size=(64,64))
    env.reset()
    injected=setup(env,scenario)
    actor=Controller(seed)
    goal=("game_wood_obtained" if SCENARIOS[scenario]["material"]=="tree"
          else "game_drink_obtained")
    events=[]
    history=[]
    before=snapshot(0,env._player.inventory,
                    env._player.achievements,env._player.pos)
    initial_inv=dict(env._player.inventory)
    initial_ach=dict(env._player.achievements)
    status="NOT_STARTED"
    goal_witness=None
    blocked_attempts=0
    previous_stationary=None
    surprise=False
    new_plan_after_surprise=None
    before_surprise=None
    issued_actions=[]
    for tick in range(limit):
        belief=observe(env,actor,
                       f"crafter:seed{seed}:scenario{scenario}:step{tick}")
        p=traverse(belief,goal)
        action=(p.actions[0] if mode=="bfs" and
                p.status=="PLAN_CANDIDATE" else
                greedy_step(belief,goal) if mode=="greedy" else None)
        if action is None:
            status="HOLD_NO_WITNESSED_GOAL_ACCESS"
            history.append({
                "time":tick,"action":"HOLD",
                "reason":p.status if mode=="bfs" else
                         "GREEDY_NO_WITNESSED_TARGET",
                "witnessed_input_pin":belief.pin,"game_execution":False})
            break
        if surprise and new_plan_after_surprise is None:
            new_plan_after_surprise={
                "action_after_obstacle_observed":action,
                "plan_actions":p.actions,
                "sensor_pin":belief.pin,
                "route_changed_from_previous_plan":
                    bool(before_surprise and
                         p.actions != tuple(before_surprise[1:])),
            }
        oldpos=tuple(int(x) for x in env._player.pos)
        oldface=tuple(int(x) for x in env._player.facing)
        prior_inv=dict(env._player.inventory)
        prior_ach=dict(env._player.achievements)
        observation,reward,done,info=env.step(ACTS.index(action))
        after=snapshot(tick+1,info["inventory"],
                       info["achievements"],info["player_pos"])
        newface=tuple(int(x) for x in env._player.facing)
        newpos=tuple(int(x) for x in env._player.pos)
        reward_actual=check_goals(
            prior_inv,info["inventory"],prior_ach,info["achievements"],goal)
        attained=reward_actual!="GOAL_NOT_YET_WITNESSED"
        e=Episode(
            f"qc017:{seed}:{scenario}:{mode}:{tick+1}",
            "OTHER_GAME","GAME_TELEMETRY",
            f"crafter:1.8.3:seed{seed}:scenario{scenario}:step{tick+1}",
            "OWNER_PROVIDED",tick,tick+1,action,before,after,
            "SUCCESS" if attained or after.location!=before.location
                         else "INCONCLUSIVE",
            f"Actual engine execution; selector={mode}; "
            f"planned actions={p.actions}; input_pin={belief.pin}; "
            "controller reads privileged local current game tiles; "
            "initial world was deliberately modified; "
            "timestamps represent game ticks not video seconds.",
            "OBSERVED",("OBSERVED_GAME",))
        e.validate()
        events.append(e)
        issued_actions.append(action)
        history.append({
            "time":tick+1,
            "observed_belief_pin":belief.pin,
            "planned_actions":p.actions if mode=="bfs" else (),
            "planned_model_state_expansions":p.expanded_states,
            "chosen_action":action,"before_position":oldpos,
            "after_position":newpos,
            "before_facing":oldface,
            "after_facing":newface,
            "real_game_goal_result":reward_actual,
            "source_episode_pin":e.pin,
        })
        before=after
        if attained:
            goal_witness={
                "step":tick+1,
                "observed_game_outcome":reward_actual,
                "before":prior_inv[GOAL_RULES[goal][1]],
                "after":info["inventory"][GOAL_RULES[goal][1]],
                "source_pin":e.pin,
            }
            status="GAME_GOAL_WITNESSED"
            break
        if newpos==oldpos and newface==oldface:
            blocked_attempts+=1
            if previous_stationary==(oldpos,oldface,action) and mode=="bfs":
                status="HOLD_REPEATED_FAILED_ACTION"
                break
            previous_stationary=(oldpos,oldface,action)
        else:
            previous_stationary=None
        if scenario=="surprise_wall" and tick==0:
            # AFTER a real game action and BEFORE the next sensor read,
            # create a new obstacle on the original predicted route.
            # Its position derives from a named stress condition, not from
            # any hidden route supplied to the BFS.
            offset=SCENARIOS[scenario]["surprise"]
            anchor=injected["origin"]
            cell=tuple(anchor[i]+offset[i] for i in (0,1))
            if cell==newpos or cell==injected["resource_position"]:
                raise ValueError("Obstacle must not replace player or goal")
            old,obj=env._world[cell]
            if obj is not None:env._world.remove(obj)
            env._world[cell]="stone"
            surprise=True
            before_surprise=p.actions
            history.append({
                "time":tick+1,
                "EXPLICIT_INTERVENTION":"SUDDEN_BLOCKED_GAME_TILE",
                "position":cell,
                "previous_material":str(old),
                "new_material":"stone",
                "status":"WILL_REPLAN_FROM_NEXT_REAL_SENSOR_READING",
            })
        if done:
            status="GAME_TERMINATED"
            break
    if status=="NOT_STARTED":status="ACTION_BUDGET_EXHAUSTED"
    if not events:
        # The absence of a path is still an important outcome, but no
        # artificial action should be added merely to satisfy a replay type.
        packet_status="NOT_CREATED_NO_GAME_ACTIONS"
        replay_pin=None
    else:
        replay=Replay(
            "OTHER_GAME",tuple(events),
            f"ACTUAL_CRAFTER_ENGINE;seed={seed};scenario={scenario};"
            f"mode={mode};controlled_world_edited=True;"
            "local_tile_sensor_privileged=True",True)
        replay.validate()
        packet_status=relatte_preview(replay)["status"]
        replay_pin=replay.pin
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    if events:
        serial={
            "schema":"motif.annotated-gameplay/v0",
            "game":"OTHER_GAME",
            "provenance":replay.provenance,
            "consent_for_derived_research":True,
            "episodes":[{
                **{k:v for k,v in e.__dict__.items()
                   if k not in ("before","after","tags")},
                "before":encode_state(e.before),
                "after":encode_state(e.after),
                "tags":list(e.tags),
            } for e in replay.episodes],
        }
        (outdir/"annotated_gameplay.json").write_text(
            json.dumps(serial,sort_keys=True,indent=2)+"\n")
    (outdir/"decision_log.json").write_text(
        json.dumps(history,sort_keys=True,indent=2)+"\n")
    outcome={
        "seed":seed,"scenario":scenario,"selector":mode,
        "goal":goal,
        "controlled_environment":injected,
        "game_actions_executed":len(events),
        "game_actions":issued_actions,
        "game_goal_witness":goal_witness,
        "goal_witnessed":goal_witness is not None,
        "end_game_resource":int(
            env._player.inventory[GOAL_RULES[goal][1]]),
        "initial_game_resource":int(initial_inv[GOAL_RULES[goal][1]]),
        "status":status,
        "blocked_or_stationary_attempts":blocked_attempts,
        "surprise_injected":surprise,
        "first_replan_after_surprise":new_plan_after_surprise,
        "source_replay_pin":replay_pin,
        "relatte_preview":packet_status,
        "actual_real_world_effects":0,
        "planner_is_classical_BFS":mode=="bfs",
        "learned_policy":False,
    }
    (outdir/"outcome.json").write_text(json.dumps(outcome,sort_keys=True,
                                                  indent=2)+"\n")
    print("QC017_GAME="+json.dumps({
        k:v for k,v in outcome.items() if k not in
        ("controlled_environment","game_actions")},
        sort_keys=True),flush=True)
    return outcome


def benchmark():
    root=Path(os.environ.get("QC017_OUTPUT_DIR","runs/crafter-qc017"))
    root.mkdir(parents=True,exist_ok=True)
    comparisons=[]
    for seed in SEEDS:
        for scenario in SCENARIOS:
            greedy=run(seed,scenario,"greedy",
                       root/f"seed{seed}-{scenario}-greedy")
            bfs=run(seed,scenario,"bfs",
                    root/f"seed{seed}-{scenario}-bfs")
            comparisons.append({
                "seed":seed,"scenario":scenario,
                "greedy_succeeded":greedy["goal_witnessed"],
                "bfs_succeeded":bfs["goal_witnessed"],
                "greedy_steps":greedy["game_actions_executed"],
                "bfs_steps":bfs["game_actions_executed"],
                "greedy_final_game_resource":greedy["end_game_resource"],
                "bfs_final_game_resource":bfs["end_game_resource"],
                "bfs_status":bfs["status"],
                "bfs_replanned_after_changed_map":
                    bool((bfs["first_replan_after_surprise"] or {})
                         .get("route_changed_from_previous_plan")),
            })
    result={
        "experiment":"MOTIF-QC017",
        "comparator":"MANHATTAN_GREEDY__NOT_STRONG_PLANNING_BASELINE",
        "planner":"CLASSICAL_BFS_OVER_CURRENT_OBSERVED_GAME_TILES",
        "no_hidden_map_access":True,
        "sensor_limitation":"PRIVILEGED_CURRENT_RADIUS_7_ENGINE_TILES",
        "run_count":len(comparisons)*2,
        "game_actions":sum(x["greedy_steps"]+x["bfs_steps"]
                           for x in comparisons),
        "BFS_goal_successes":sum(x["bfs_succeeded"] for x in comparisons),
        "greedy_goal_successes":sum(x["greedy_succeeded"] for x in comparisons),
        "pairs":comparisons,
        "trained_MOTIF_policy":False,
        "human_survival_claim":False,
        "production_deploy":False,
    }
    (root/"comparison.json").write_text(json.dumps(result,indent=2,
                                                    sort_keys=True)+"\n")
    print("QC017_COMPARISON="+json.dumps(result,sort_keys=True),flush=True)
    return result


if __name__=="__main__":
    benchmark()
