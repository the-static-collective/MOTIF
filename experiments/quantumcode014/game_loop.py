"""QC-014: real Crafter anti-stagnation intervention with genuine game actions.

Two falsifiers:
  1. Inject an explicitly artificial, reproducible game state where a crafting
     table is 3+ steps away and the controller endlessly retries a craft.
     The guarded version MUST detect failure, inspect recipe prerequisites,
     travel to the table in the *actual Crafter engine*, and craft a tool.
  2. Run baseline QC-013 expert-informed policy vs same policy plus watchdog
     on ordinary seeded worlds. Compare failures/side effects, not just score.

This is a local simulated-game tool, not an autonomous MOTIF or human survival
policy; the controller already reads privileged current game tiles.
"""
from __future__ import annotations

from collections import deque
import json
import os
from pathlib import Path
import sys

import crafter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"quantumcode012"))
sys.path.insert(0,str(ROOT/"quantumcode013"))
sys.path.insert(0,str(ROOT/"quantumcode011"))
from play_crafter import Controller,ACTS,DIRS,WALK,snapshot,encode_state
from expert_intervention import expert_informed_act
from game_replay import Episode,Replay,relatte_preview
from insanity import (
    Snapshot,Observation,StagnationGuard,diagnose_craft,PROGRESS
)


def moment(env,step):
    a=env._player
    return Snapshot(
        tuple(sorted((str(k),int(v)) for k,v in a.inventory.items())),
        tuple(sorted("achievement:"+k for k,v in a.achievements.items()
                     if v>0)),
        tuple(int(v) for v in a.pos),
        tuple(int(v) for v in a.facing),
        step,
    )


def add_known_missing_table_fixture(env):
    """Controlled *game-state injection* for an isolated failed precondition.

    No claim that a human naturally placed this table or found that wood.
    We choose a reachable table tile from actual currently local grass/path
    cells, set game state before both compared policies, and keep that
    intervention visible in provenance.
    """
    p=tuple(int(v) for v in env._player.pos)
    queue=deque([(p,0)])
    seen={p}
    targets=[]
    while queue:
        current,depth=queue.popleft()
        if 3<=depth<=5:
            tile=env._world[current]
            if tile[0] in WALK and tile[1] is None:
                targets.append((depth,current))
        if depth>=5:continue
        for dx,dy in DIRS.values():
            q=(current[0]+dx,current[1]+dy)
            if q in seen:continue
            seen.add(q)
            tile=env._world[q]
            if tile[0] in WALK and tile[1] is None:
                queue.append((q,depth+1))
    if not targets:
        raise ValueError("No reachable game tile for controlled scenario")
    distance,loc=min(targets,key=lambda x:(x[0],x[1]))
    env._world[loc]="table"
    env._player.inventory["wood"]=1
    env._player.inventory["wood_pickaxe"]=0
    env._player.achievements["place_table"]=1
    return {"injected_table_position":loc,
            "distance_in_walkable_tiles":distance,
            "injected_inventory":{"wood":1,"wood_pickaxe":0},
            "injected_achievement":"place_table",
            "scenario_is_naturally_observed":False}


def inspect_requirements(action,env):
    if not action.startswith("make_"):
        return None
    recipe=crafter.constants.make.get(action[len("make_"):])
    if not recipe:return None
    near,_=env._world.nearby(env._player.pos,1)
    present=set(near)
    visible={k:(k in present) for k in recipe["nearby"]}
    return diagnose_craft(action,env._player.inventory,visible,recipe,
                          rule_source="ACTUAL_CRAFTER_GAME_CONSTANTS")


class RecoveryController:
    def __init__(self,seed,threshold=3):
        self.actor=Controller(seed)
        self.watch=StagnationGuard(threshold=threshold)
        self.active=None
        self.repair_steps=0
        self.max_repair_steps=18
        self.diagnoses=[]
        self.events=[]
        self.total_blocked_retries=0
        self.terminal_hold=False
        self.completed_repairs=0

    def plan(self,env,base_action,base_reason):
        action=base_action
        # Avoid repeating actions already identified as ineffective.
        if not self.watch.should_hold(action):
            return action,base_reason
        self.total_blocked_retries+=1
        self.repair_steps+=1
        if self.repair_steps>self.max_repair_steps:
            self.terminal_hold=True
            return "noop","HOLD_REPAIR_BUDGET_EXHAUSTED"
        if action.startswith("make_"):
            diagnosis=inspect_requirements(action,env)
            if diagnosis is None:
                self.terminal_hold=True
                return "noop","HOLD_UNRECOGNIZED_RECIPE"
            if len(self.diagnoses)<50:
                self.diagnoses.append({
                    "step":len(self.events)+1,
                    "action":action,
                    "explanation":diagnosis.explanation,
                    "missing_resources":diagnosis.missing_resources,
                    "missing_utilities":diagnosis.missing_utilities,
                    "source":diagnosis.rule_source,
                })
            if diagnosis.missing_resources:
                key=diagnosis.missing_resources[0][0]
                # A generic source-dependent mapping, not a claim all missing
                # resources are always safely obtainable.
                known={"wood":"tree","stone":"stone"}
                if key not in known:
                    self.terminal_hold=True
                    return "noop","HOLD_NO_VERIFIED_RESOURCE_PROBE"
                proposed=self.actor.approach(env,known[key])
                if proposed:
                    return proposed[0],"PROBE_MISSING_RESOURCE_"+key
                return self.actor.explore(env)[0],"PROBE_SEARCH_FOR_"+key
            if diagnosis.missing_utilities:
                key=diagnosis.missing_utilities[0]
                proposed=self.actor.approach(env,key)
                if proposed:
                    return proposed[0],"PROBE_RESTORE_UTILITY_"+key
                return self.actor.explore(env)[0],"PROBE_SEARCH_FOR_UTILITY_"+key
            if diagnosis.unknown_utilities:
                self.terminal_hold=True
                return "noop","HOLD_UTILITY_NOT_OBSERVABLE"
            # The actual game has verified all recorded prerequisites. We
            # allow one sourced reassessment, not a blind recursive retry.
            self.watch.release_after_new_evidence(
                action,"live_game_verified_recipe_conditions")
            self.repair_steps=0
            self.completed_repairs+=1
            return action,"RETRY_AFTER_VERIFIED_STATE_CHANGE"
        if action.startswith("move_"):
            candidate=self.actor.explore(env)
            if candidate[0]!=action:
                return candidate[0],"PROBE_ALTERNATIVE_ACCESS"
        self.terminal_hold=True
        return "noop","HOLD_NO_SUPPORTED_REPAIR"

    def observe(self,before,action,after,evidence):
        alert=self.watch.observe(Observation(action,before,after,evidence))
        if alert is not None:
            self.active=alert.action
            self.repair_steps=0
        return alert


def play(seed,mode,outdir,horizon=80,scenario="controlled"):
    env=crafter.Env(seed=seed,length=horizon,view=(9,9),size=(64,64))
    env.reset()
    injection=(add_known_missing_table_fixture(env)
               if scenario=="controlled" else None)
    actor=Controller(seed)
    watcher=RecoveryController(seed)
    episodes=[]
    facts=[]
    b=snapshot(0,env._player.inventory,
               env._player.achievements,env._player.pos)
    done=False
    target_achieved=False
    for t in range(horizon):
        before=moment(env,t)
        if scenario=="controlled":
            intended,reason="make_wood_pickaxe","deliberate_bad_retry"
        else:
            intended,reason=expert_informed_act(
                watcher.actor if mode=="guarded" else actor,env)
        if mode=="guarded":
            action,why=watcher.plan(env,intended,reason)
        else:
            action,why=intended,reason
        if watcher.terminal_hold:break
        obs,reward,done,info=env.step(ACTS.index(action))
        after=moment(env,t+1)
        g=snapshot(t+1,info["inventory"],info["achievements"],
                   info["player_pos"])
        episode=Episode(
            f"qc014-seed{seed}-{mode}-{scenario}-{t+1}",
            "OTHER_GAME","GAME_TELEMETRY",
            f"crafter:game-engine:seed{seed}:tick{t+1}",
            "OWNER_PROVIDED",t,t+1,action,b,g,
            "SUCCESS" if ("achievement:make_wood_pickaxe" in
                          set(g.capabilities)-set(b.capabilities))
                      else "INCONCLUSIVE",
            "Actual Crafter 1.8.3 game execution; chosen by "+why+
            "; controlled fixture explicitly edits initial state, not footage.",
            "OBSERVED",("OBSERVED_GAME",))
        episode.validate()
        episodes.append(episode)
        alert=watcher.observe(
            before,action,after,episode.pin)
        if alert is not None or t<10 or (t+1)%20==0:
            facts.append({
                "step":t+1,"action":action,
                "policy_reason":why,"observed_progress":watcher.watch.recent[-1][1],
                "trigger":alert.reason if alert else None,
                "game_wood_pickaxe":after.count("wood_pickaxe"),
                "position":after.position,
            })
        b=g
        if (scenario=="controlled" and
            after.count("wood_pickaxe")>0):
            target_achieved=True
            break
        if done:break
    replay=Replay(
        "OTHER_GAME",tuple(episodes),
        f"REAL_CRAFTER_ENGINE;seed={seed};policy={mode};"
        f"scenario={scenario};controlled_injection={bool(injection)};"
        "debug_local_tile_radius=7;recipe_lookup=canonical_engine"
        if mode=="guarded" else
        f"REAL_CRAFTER_ENGINE;seed={seed};policy={mode};"
        f"scenario={scenario};controlled_injection={bool(injection)};"
        "debug_local_tile_radius=7",
        True)
    replay.validate()
    packet=relatte_preview(replay)
    outdir.mkdir(parents=True,exist_ok=True)
    data={
        "schema":"motif.annotated-gameplay/v0",
        "game":replay.game,"provenance":replay.provenance,
        "consent_for_derived_research":True,
        "episodes":[{
            **{k:v for k,v in ep.__dict__.items()
               if k not in ("before","after","tags")},
            "before":encode_state(ep.before),
            "after":encode_state(ep.after),
            "tags":list(ep.tags)} for ep in replay.episodes],
    }
    (outdir/"annotated_gameplay.json").write_text(
        json.dumps(data,sort_keys=True,indent=2)+"\n")
    summary={
        "seed":seed,"mode":mode,"scenario":scenario,
        "injected_initial_state":injection,
        "steps_executed":len(episodes),
        "target_tool_acquired":target_achieved or
            env._player.inventory["wood_pickaxe"]>0,
        "end_game_health":env._player.inventory["health"],
        "in_game_died":done and env._player.inventory["health"]<=0,
        "alerts":[{"action":a.action,"at_step":a.step,
                   "failure_count":a.failures,
                   "causal_explanation_confirmed":a.actual_cause_confirmed}
                  for a in watcher.watch.alerts],
        "prevented_retries":watcher.total_blocked_retries,
        "repaired_preconditions":watcher.completed_repairs,
        "repair_diagnoses":watcher.diagnoses,
        "terminal_hold":watcher.terminal_hold,
        "events_preview":facts,
        "replay_pin":replay.pin,
        "relatte_status":packet["status"],
        "real_world_actions":0,
        "MOTIF_neural_agent":False,
    }
    (outdir/"summary.json").write_text(json.dumps(summary,indent=2,
                                                   sort_keys=True)+"\n")
    print("QC014_EPISODE_SUMMARY="+json.dumps(
        {k:v for k,v in summary.items() if k not in
         ("events_preview","repair_diagnoses")},sort_keys=True),flush=True)
    return summary


def benchmark():
    root=Path(os.environ.get("QC014_OUTPUT_DIR","runs/crafter-qc014"))
    root.mkdir(parents=True,exist_ok=True)
    pairs=[]
    for seed in (1042,2026,3199,8765):
        raw=play(seed,"blind",root/f"{seed}-blind",30,"controlled")
        fixed=play(seed,"guarded",root/f"{seed}-guarded",30,"controlled")
        pairs.append({
            "seed":seed,
            "blind_steps":raw["steps_executed"],
            "guarded_steps":fixed["steps_executed"],
            "blind_tool":raw["target_tool_acquired"],
            "guarded_tool":fixed["target_tool_acquired"],
            "alerts":len(fixed["alerts"]),
            "guarded_held":fixed["terminal_hold"],
            "repaired":fixed["repaired_preconditions"],
        })
    normal=[]
    for seed in (1042,2026,3199,8765):
        base=play(seed,"blind",root/f"{seed}-natural-baseline",220,"natural")
        tested=play(seed,"guarded",root/f"{seed}-natural-guarded",220,"natural")
        normal.append({
            "seed":seed,
            "baseline_steps":base["steps_executed"],
            "guarded_steps":tested["steps_executed"],
            "baseline_health":base["end_game_health"],
            "guarded_health":tested["end_game_health"],
            "baseline_tool":base["target_tool_acquired"],
            "guarded_tool":tested["target_tool_acquired"],
            "guarded_alerts":len(tested["alerts"]),
        })
    result={
        "experiment":"QC-014-INSANITY-PREVENTION",
        "controlled_injection_pairs":pairs,
        "ordinary_game_pairs":normal,
        "actual_external_game_engine":True,
        "game_engine":"crafter==1.8.3",
        "identical_current_local_tile_sensor":True,
        "guard_extra_game_recipe_metadata":True,
        "autonomous_machine_learning":False,
        "real_world_actions":0,
    }
    (root/"comparison.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("QC014_RESULTS="+json.dumps(result,sort_keys=True),flush=True)


if __name__=="__main__":
    benchmark()
