"""QC-016: goal-relevant escape from a cycle OF cycles in the real Crafter engine.

This is a **deliberately fault-injected miniature task**, not a naturally
emergent survival benchmark, trained MOTIF policy or human welfare model.

A character cycles A=(right,left), B=(up,down); repeat AB. A verified game
water resource is placed two game tiles north, behind a traversable tile.
An intentionally defective comparator continues AB; the experimental policy
observes [A,B]*2 after warming up the visibility field, then executes a
pre-authored, source-checked water-access sequence if QC-016's objective-aware
selector finds it relevant. Every move is executed by independent Crafter,
and results are evaluated only from returned game telemetry.
"""
from __future__ import annotations

from pathlib import Path
import json,os,sys
import crafter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"quantumcode012"))
sys.path.insert(0,str(ROOT/"quantumcode015"))
sys.path.insert(0,str(ROOT/"quantumcode011"))
from play_crafter import Controller,ACTS,snapshot,encode_state
from game_cycles import LocalKnowledge,game_state
from game_replay import Episode,Replay,relatte_preview
from cycle_field import FieldStep
from meta_cycles import NestedMonitor
from goal_probe import Goal,Probe,YES,UNKNOWN,select,evaluate,reenter


ACTIONS=("move_right","move_left","move_up","move_down")
RECEIPT="controlled_game_sensor_water_two_cells_north"


def controlled_scene(env):
    p=tuple(int(x) for x in env._player.pos)
    if not 4<p[0]<59 or not 4<p[1]<59:
        raise ValueError("Unexpected controlled game start")
    altered=[]
    for name,(dx,dy),material in (
        ("east_neighbor",(1,0),"grass"),
        ("north_neighbor",(0,-1),"grass"),
        ("water_objective",(0,-2),"water")):
        coord=(p[0]+dx,p[1]+dy)
        previous,obj=env._world[coord]
        if obj is not None:
            env._world.remove(obj)
        env._world[coord]=material
        altered.append({
            "role":name,"position":coord,"previous_material":str(previous),
            "previous_object":obj is not None,"current_material":material})
    env._player.inventory["drink"]=3
    return {
        "anchor":p,
        "injected_tiles":altered,
        "injected_initial_drink":3,
        "source":"INTENTIONALLY_EDITED_GAME_INITIAL_WORLD",
        "natural_game_observation":False,
    }


def probe_fiber(env,actor,seed):
    p=actor.pos(env)
    north=(p[0],p[1]-1)
    water=(p[0],p[1]-2)
    south=(p[0],p[1]+1)
    north_tile=actor.tile(env,north)
    water_tile=actor.tile(env,water)
    south_tile=actor.tile(env,south)
    observed_north=bool(north_tile and north_tile[0]=="grass"
                        and north_tile[1] is None)
    observed_water=bool(water_tile and water_tile[0]=="water")
    observed_south=bool(south_tile and
                        south_tile[0] in ("grass","sand","path")
                        and south_tile[1] is None)
    g=Goal(
        "obtain_virtual_drink",("game_drink_obtained",),(),3,
        f"crafter:seed={seed}:player_inventory_drink=3")
    probes=(
        Probe(
            "toward_confirmed_water","move_up_then_water_interaction",
            ("game_drink_obtained",),(),3,0,"LOW",YES,
            YES if observed_north and observed_water else UNKNOWN,
            YES if observed_north and observed_water else UNKNOWN,
            "ACTUAL_GAME_SENSOR",
            f"crafter:seed{seed}:current_local_tile_water={water}"),
        Probe(
            "novel_but_irrelevant_neighbor","move_south_for_terrain",
            ("new_terrain_cell",),(),1,0,"LOW",YES,
            YES if observed_south else UNKNOWN,
            YES if observed_south else UNKNOWN,
            "ACTUAL_GAME_SENSOR",f"crafter:seed{seed}:south={south}"),
        Probe(
            "unverified_shortcut","move_into_hidden_cells",
            ("game_drink_obtained",),(),1,0,"HIGH",
            YES,UNKNOWN,UNKNOWN,"PROVISIONAL_MODEL",
            f"crafter:seed{seed}:untested"),
    )
    return g,probes,select(g,probes)


def play(seed,mode,outdir,horizon=19):
    env=crafter.Env(seed=seed,length=horizon,view=(9,9),size=(64,64))
    env.reset()
    setup=controlled_scene(env)
    actor=Controller(seed)
    observed=LocalKnowledge()
    observed.scan(env,actor)
    nested=NestedMonitor()
    baseline_actions=()
    status="NO_POLICY_CHANGE"
    first_alert=None
    chosen_probe=None
    outcome=None
    script=()
    episodes=[]
    observed_novelty_by_step=[]
    b=snapshot(0,env._player.inventory,env._player.achievements,
               env._player.pos)
    for t in range(horizon):
        old=game_state(t,env)
        if script:
            action=script[0]
            script=script[1:]
            rationale="GOAL_DEPENDENT_WATER_PROBE"
        else:
            action=ACTIONS[t%4]
            rationale="INTENTIONALLY_REPEATED_AB_GAME_LOOP"
        _,_,done,info=env.step(ACTS.index(action))
        new=game_state(t+1,env)
        novelty=observed.scan(env,actor)
        observed_novelty_by_step.append(novelty)
        g=snapshot(t+1,info["inventory"],info["achievements"],
                   info["player_pos"])
        diff=set(g.capabilities)-set(b.capabilities)
        spent=dict(b.resources)
        gained=dict(g.resources)
        success=bool(diff or any(gained.get(k,0)>spent.get(k,0)
                                 for k in ("drink","food","wood","stone")))
        e=Episode(
            f"qc016:seed{seed}:policy{mode}:step{t+1}",
            "OTHER_GAME","GAME_TELEMETRY",
            f"crafter:1.8.3:seed{seed}:ordinal{t+1}","OWNER_PROVIDED",
            t,t+1,action,b,g,
            "SUCCESS" if success else "INCONCLUSIVE",
            "Actual Crafter environment action; "+rationale+
            "; controlled scenario patches game tiles and drink; "
            "step ordinal not recorded video seconds.",
            "OBSERVED",("OBSERVED_GAME",))
        e.validate()
        episodes.append(e)
        alert=nested.observe(FieldStep(old,action,new,novelty,e.pin))
        if alert is not None and first_alert is None:
            first_alert=alert.detected_step
        if (mode=="goal_dividend" and alert is not None
            and alert.status=="CONFIRMED_NO_NEW_SCENE_FACTS_META_CYCLE"
            and not chosen_probe):
            goal,candidates,decision=probe_fiber(env,actor,seed)
            if "toward_confirmed_water" in decision["pareto_candidate_ids"]:
                chosen_probe=evaluate(goal,candidates[0])
                status="CANDIDATE_PROBE_SELECTED_GAME_ONLY"
                script=("move_up","move_up","do")
            else:
                status="HOLD_NO_GOAL_RELEVANT_CONFIRMED_ACCESS"
        if chosen_probe is not None and action=="do" and not script:
            evidence=tuple(["game_drink_obtained"]
                           if gained.get("drink",0)>spent.get("drink",0)
                           else [])
            outcome=reenter(
                chosen_probe,evidence,
                f"crafter:seed{seed}:game_step={t+1}:"
                f"drink_before={spent.get('drink',0)}:"
                f"drink_after={gained.get('drink',0)}")
            status=("WITNESSED_IN_GAME_PROGRESS" if
                    outcome.success_proven_in_source_world
                    else "GAME_PROBE_FAILED_OR_UNVERIFIED")
            b=g
            break
        b=g
        if done:break
    replay=Replay(
        "OTHER_GAME",tuple(episodes),
        f"REAL_CRAFTER_ENGINE;seed={seed};mode={mode};"
        "controlled_tile_and_drink_injection=True;"
        "privileged_local_terrain_sensor_radius7=True",True)
    replay.validate()
    packet=relatte_preview(replay)
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    raw={
        "schema":"motif.annotated-gameplay/v0",
        "game":replay.game,"provenance":replay.provenance,
        "consent_for_derived_research":True,
        "episodes":[{
            **{k:v for k,v in e.__dict__.items()
               if k not in ("before","after","tags")},
            "before":encode_state(e.before),
            "after":encode_state(e.after),"tags":list(e.tags)}
            for e in replay.episodes]}
    (outdir/"annotated_gameplay.json").write_text(
        json.dumps(raw,indent=2,sort_keys=True)+"\n")
    result={
        "seed":seed,"controller":mode,
        "intentionally_patched_starting_world":setup,
        "actual_game_steps":len(episodes),
        "meta_alert_count":len(nested.alerts),
        "meta_primitive_loops":nested.primitives_seen,
        "meta_visibility_resets":nested.resets_due_to_information,
        "meta_recent_primitive_tokens":tuple(x.token[:12] for x in nested.primitives),
        "observed_new_facts_by_step":tuple(observed_novelty_by_step),
        "first_meta_alert_step":first_alert,
        "detected_period":nested.alerts[0].primitive_motif_length
                          if nested.alerts else None,
        "game_drink_before":3,
        "game_drink_after":int(env._player.inventory["drink"]),
        "new_terrain_facts":observed.new_cells,
        "decision_status":status,
        "chosen_probe":chosen_probe.probe_id if chosen_probe else None,
        "evidence_reentry_success":outcome.success_proven_in_source_world
                                  if outcome else None,
        "replay_sha256":replay.pin,
        "relatte_packet":packet["status"],
        "effectful_real_world_actions":0,
        "autonomous_learned_policy":False,
    }
    (outdir/"summary.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("QC016_REAL_GAME_RUN="+json.dumps(
        {k:v for k,v in result.items()
         if k!="intentionally_patched_starting_world"},sort_keys=True),flush=True)
    return result


def experiment():
    root=Path(os.environ.get("QC016_OUTPUT_DIR","runs/crafter-qc016"))
    root.mkdir(parents=True,exist_ok=True)
    pairs=[]
    for seed in (1042,2026,3199,8765):
        a=play(seed,"blind",root/f"{seed}-blind",19)
        b=play(seed,"goal_dividend",root/f"{seed}-goal",19)
        pairs.append({
            "seed":seed,
            "blind_steps":a["actual_game_steps"],
            "goal_steps":b["actual_game_steps"],
            "blind_game_drink":a["game_drink_after"],
            "goal_game_drink":b["game_drink_after"],
            "first_meta_alert_step":b["first_meta_alert_step"],
            "goal_probe_selected":b["chosen_probe"],
            "goal_reentry_success":b["evidence_reentry_success"],
        })
    d={
        "experiment":"QC016-REAL-GAME-META-TO-GOAL",
        "pairs":pairs,
        "world":"CONTROLLED_INDEPENDENT_CRAFTER_1_8_3",
        "comparator":"INTENTIONALLY_DEFECTIVE_REPEAT_NOT_STRONG_BASELINE",
        "matched_real_world_conditions_claim":False,
        "true_world_effects":0,
        "total_game_actions":sum(x["blind_steps"]+x["goal_steps"]
                                 for x in pairs)}
    (root/"comparison.json").write_text(json.dumps(d,sort_keys=True,
                                                    indent=2)+"\n")
    print("QC016_REAL_GAME_RESULTS="+json.dumps(d,sort_keys=True),flush=True)
    return d


if __name__=="__main__":
    experiment()
