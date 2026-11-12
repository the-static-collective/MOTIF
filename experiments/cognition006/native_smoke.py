"""Noninteractive, bounded replay in the original NovelGym / NovelGridWorldsV2.

No game logic copied, no reward fabricated. This runner intentionally
implements NO MOTIF adapter and claims NO strong-baseline comparison.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import time
import traceback

NOVELGYM_SHA="0ad2cbb656177f76ff29f86793269b14879d9b89"
WORLD_SHA="f5d06d4f5166ca985ca420c809129a79700d904e"
MAX_MAIN=160
MAX_TOTAL=600
SEED=1


def checksum(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()


def smoke_case(novelty, seed=SEED):
    if novelty not in ("none","fire") or seed!=SEED:
        raise ValueError("SMOKE_UNREGISTERED_TASK")
    # run with CWD = pinned original NovelGym root.
    root=Path.cwd()
    if not (root/"config"/"polycraft_gym_rl_single.yaml").is_file():
        raise RuntimeError("ORIGINAL_NOVELGYM_CWD_REQUIRED")
    # Upstream YAML refers to top-level "agents" and "novelties" packages.
    # Python invoked on a script outside the upstream checkout omits cwd from
    # sys.path, so expose the pinned checkout explicitly (no code copying).
    if str(root) not in sys.path:
        sys.path.insert(0,str(root))
    from gym_novel_gridworlds2.envs.sequential import NovelGridWorldSequentialEnv
    from gym_novel_gridworlds2.utils.json_parser import load_json
    config_paths=["config/polycraft_gym_rl_single.yaml"]
    if novelty=="fire":
        config_paths.append("novelties/evaluation1/fire/fire_crafting_table.yaml")
    config=load_json(config_json={"extends": config_paths}, verbose=False)
    env=NovelGridWorldSequentialEnv(config_dict=config, render_mode=None,
                                    run_name="motif_cognition006_probe",
                                    max_time_step=MAX_MAIN+100, seed=seed)
    main_actions=0
    total_actions=0
    planner_failed=False
    attempted=[]
    end_reason="NOT_STARTED"
    start=time.monotonic()
    try:
        env.reset(seed=seed,options={"episode":0})
        for i in range(MAX_TOTAL):
            if bool(env.internal_state._goal_achieved):
                end_reason="ORIGINAL_OWNER_GOAL_ACHIEVED"
                break
            if bool(env.internal_state._given_up):
                end_reason="ORIGINAL_OWNER_GIVEN_UP"
                break
            if main_actions>=MAX_MAIN:
                end_reason="MAIN_ACTION_CAP"
                break
            selected=env.agent_selection
            if env.terminations.get(selected,False) or env.truncations.get(selected,False):
                end_reason="OWNER_EPISODE_TERMINATED_OR_TRUNCATED"
                break
            agent_obj=env.agent_manager.agents[selected].agent
            action_set=env.agent_manager.agents[selected].action_set
            obs,_,terminated,truncated,info=env.last()
            response=agent_obj.policy(obs)
            extra={}
            if isinstance(response,tuple):
                action,extra=response
            else:
                action=response
            if isinstance(action, str):
                action=action_set.action_index[action]
            if not isinstance(action,int):
                action=int(action)
            if action<0 or action>=len(action_set.actions):
                raise RuntimeError("NATIVE_AGENT_INVALID_ACTION_INDEX")
            action_name=action_set.actions[action][0]
            env.step(action,extra)
            native_info=env.infos.get(selected,{})
            success=bool(native_info.get("success",False))
            total_actions+=1
            if selected=="agent_0":
                main_actions+=1
                attempted.append({
                    "step":main_actions,
                    "native_action":action_name,
                    "native_action_success":success,
                    "native_message":str(native_info.get("message",""))[:220],
                    "owner_goal_after":bool(env.internal_state._goal_achieved),
                    "owner_given_up_after":bool(env.internal_state._given_up),
                })
                if not success:
                    if hasattr(agent_obj,"set_stuck"):
                        agent_obj.set_stuck()
                    planner_failed=True
                    end_reason="ORIGINAL_PLAN_ACTION_FAILED"
                    break
                if getattr(agent_obj,"stuck",False):
                    planner_failed=True
                    end_reason="ORIGINAL_PLANNER_STUCK"
                    break
            # Do not read internal target state to choose a policy action; here
            # only the original NPCs and original BasePlanningAgent act.
        else:
            end_reason="TOTAL_ACTION_CAP"
        if bool(env.internal_state._goal_achieved):
            end_reason="ORIGINAL_OWNER_GOAL_ACHIEVED"
        elif end_reason=="NOT_STARTED":
            end_reason="LOOP_STOPPED_UNCLASSIFIED"
        state=env.internal_state
        return {
            "phase":"NATIVE_EXTERNAL_WORLD_SMOKE_NOT_MOTIF_EVALUATION",
            "novelty":novelty,"seed":seed,"config_paths":config_paths,
            "novelgym_pin":NOVELGYM_SHA,"native_world_pin":WORLD_SHA,
            "native_owner_goal_achieved":bool(state._goal_achieved),
            "native_owner_given_up":bool(state._given_up),
            "planner_failed":planner_failed,
            "end_reason":end_reason,
            "main_actions":main_actions,"total_actions":total_actions,
            "elapsed_wall_seconds":round(time.monotonic()-start,3),
            "native_action_receipts":attempted,
            "real_external_actions":0,"motif_policy_loaded":False,
            "owner_reward_not_recomputed":True,
            "model_adaptation_not_tested":True,
        }
    finally:
        env.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    report={"experiment":"COGNITION-006",
            "source":"UNMODIFIED_NOVELGYM_AND_NOVELGRIDWORLD_NATIVE_CODE",
            "novelgym_sha":NOVELGYM_SHA,
            "novelgridworld_sha":WORLD_SHA,
            "seed":SEED,"status":"INTEGRATION_SMOKE_NOT_BENCHMARK",
            "cases":[]}
    failure=False
    for name in ("none","fire"):
        try:
            result=smoke_case(name)
        except Exception as exc:
            result={
                "novelty":name,"status":"BLOCKED_NATIVE_ENVIRONMENT_OR_ADAPTER_ERROR",
                "exception_type":type(exc).__name__,
                "error":str(exc)[:600],
                "stack":traceback.format_exc(limit=9)[-2500:],
                "native_owner_goal_achieved":None,
            }
            failure=True
        report["cases"].append(result)
        print(f"{name}: {result.get('end_reason',result.get('status'))}, goal={result.get('native_owner_goal_achieved')}",flush=True)
    report["status"]=("BLOCKED_NATIVE_INTEGRATION" if failure else
                      "NATIVE_WORLD_EXECUTED_BASELINE_NOT_PROVEN")
    report["sha256"]=checksum(report)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"
")
    if failure:
        raise SystemExit("Native upstream execution had errors; see saved report.")


if __name__=="__main__":
    main()
