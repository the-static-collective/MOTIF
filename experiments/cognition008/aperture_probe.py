"""Source-native public observation/action aperture, development-only diagnostics.

No output from private world internals except evaluator goal and action success.
The policy will not receive novelty mechanism code or state.on_fire.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()))
from gym_novel_gridworlds2.envs.sequential import NovelGridWorldSequentialEnv
from gym_novel_gridworlds2.utils.json_parser import load_json
from utils.pddl_utils import generate_obj_types,get_entities
from utils.diarc_json_utils import generate_diarc_json_from_state

def make(novelty,seed):
    paths=["config/polycraft_gym_rl_single.yaml"]
    # Only the TEST HARNESS sees these original source-owned config paths.
    # None of the adaptive action-proposer functions receives this mapping.
    variants={
        "none":None,
        "fire":"novelties/evaluation1/fire/fire_crafting_table.yaml",
        "axe":"novelties/evaluation1/axe_to_break/axe_to_break.yaml",
        "fence":"novelties/evaluation1/fence/fence_easy.yaml",
        "chest":"novelties/evaluation1/chest_shortcut/chest_shortcut.yaml",
        "dist_trade":"novelties/evaluation1/dist_trade/dist_trade.yaml",
    }
    if novelty not in variants:
        raise ValueError("UNREGISTERED_ORIGINAL_NOVELGYM_VARIANT")
    if variants[novelty]:
        paths.append(variants[novelty])
    cfg=load_json(config_json={"extends":paths},verbose=False)
    env=NovelGridWorldSequentialEnv(config_dict=cfg,render_mode=None,
                                   run_name="cog008-probe",max_time_step=700,seed=seed)
    env.reset(seed=seed,options={"episode":0})
    env.dynamic.all_objects=generate_obj_types(env.config_dict)
    env.dynamic.all_entities=get_entities(env.config_dict)
    return env

def public_observe(env,failed_action=None):
    return generate_diarc_json_from_state(
        player_id=0,state=env.internal_state,dynamic=env.dynamic,
        failed_action=failed_action,success=False)

def main_actions(env):
    return [x[0] for x in env.agent_manager.agents["agent_0"].action_set.actions]

def native_to_main(env,action_name):
    if env.agent_selection!="agent_0":
        raise RuntimeError("NOT_AGENT_TURN")
    aset=env.agent_manager.agents["agent_0"].action_set
    if action_name not in aset.action_index:
        return {"action":action_name,"not_available":True}
    action=aset.action_index[action_name]
    env.step(action,{})
    result={"action":action_name,
            "success":bool(env.infos.get("agent_0",{}).get("success",False)),
            "message":str(env.infos.get("agent_0",{}).get("message",""))[:160]}
    for _ in range(8):
        if env.agent_selection=="agent_0":break
        if env.terminations.get(env.agent_selection) or env.truncations.get(env.agent_selection):
            break
        other=env.agent_selection
        obs,*_=env.last()
        candidate=env.agent_manager.agents[other].agent.policy(obs)
        if isinstance(candidate,tuple):act,ex=candidate
        else:act,ex=candidate,{}
        env.step(act,ex)
    result["returned_to_main"]=env.agent_selection=="agent_0"
    return result

def original_prefix(env,limit=30):
    main=env.agent_manager.agents["agent_0"].agent
    events=[]
    main._reset()
    for i in range(limit*3):
        if env.agent_selection!="agent_0":
            other=env.agent_selection
            obs,*_=env.last()
            action=env.agent_manager.agents[other].agent.policy(obs)
            env.step(*action) if isinstance(action,tuple) else env.step(action,{})
            continue
        obs,*_=env.last()
        action=main.policy(obs)
        if isinstance(action,tuple):act,extra=action
        else:act,extra=action,{}
        name=env.agent_manager.agents["agent_0"].action_set.actions[act][0]
        env.step(act,extra)
        success=bool(env.infos.get("agent_0",{}).get("success",False))
        events.append({"action":name,"success":success,
                       "message":str(env.infos.get("agent_0",{}).get("message",""))[:160]})
        if not success:main.set_stuck();break
        if env.internal_state._goal_achieved:break
    return events

def demo():
    base=make("none",1)
    normal_actions=set(main_actions(base))
    base.close()
    env=make("fire",1)
    try:
        current=main_actions(env)
        observations=[]
        actions=original_prefix(env)
        if actions[-1]["success"]:
            raise RuntimeError("EXPECTED_DEVELOPMENT_FIRE_NOVELTY_NOT_REACHED")
        failed=actions[-1]["action"]
        observations.append({"moment":"after-original-failure",
                             "public_observation":public_observe(env,failed),
                             "action_names":current,
                             "new_action_names":sorted(set(current)-normal_actions),
                             "failed_action":actions[-1]})
        return {"development_seed":1,"original_prefix":actions,
                "native_public_aperture":observations,"policy_actions_taken":0,
                "nonadaptive_only":True}
    finally:
        env.close()

if __name__=="__main__":
    print(json.dumps(demo(),sort_keys=True,indent=2,default=str))
