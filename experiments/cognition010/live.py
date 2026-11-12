"""COGNITION-010: LIVE feedback-driven recovery in original NovelGym.

The user requirement is operational: NO failure decision while legal sandbox
actions and approved attempts remain. Every native step yields source evidence;
after a recovered subgoal the original plan must resume in that SAME world.
There is a finite 10x80 action budget, so no unbounded loops or physical acts.

Both policies use the identical transition-model learner. MOTIF additionally
runs its genuine source-owned hypothetical affordance and Free Graph observer;
those observations cannot see the hidden owner goal or force a "win".
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json
import sys
import time
import traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/"cognition008"))
from adapt import (make, public_observe, main_actions, native_to_main,
                   original_prefix, safe_inventory,
                   native_motif_hypothetical_programs,
                   public_free_graph_hypothesis)
from aperture_probe import native_to_main as native_step

POLICIES=("classical_live","motif_live")
DEV_NOVELTIES=("axe","fence","dist_trade")
DEVELOPMENT_SEED=31001
MAX_ATTEMPTS=10
MAX_RECOVERY=80
MAX_PROGRAM_STEPS=6
MAX_MAIN_TOTAL=160
NAVIGATION=("move_forward","move_backward","move_left","move_right",
            "rotate_left","rotate_right")
INTERACTIONS=("break_block","collect","interact_103","use","place")
ENGINE_ERROR_STOP="NATIVE_TERMINATED"


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,default=str,
                             separators=(",",":")).encode()).hexdigest()


def public_signature(view,blocked_action):
    # The policy knows the active target action, visible selected tool, and
    # visible inventory. It NEVER receives native world owner-goal truth.
    return (blocked_action,
            str(view.get("inventory",{}).get("selectedItem")),
            tuple(sorted((k,v) for k,v in safe_inventory(view).items() if v>0)))


def safe_actions(native_names):
    return set(native_names)-{"give_up","nop"}


def programs_for_failure(allowed,old_names,view,failed_action,prior):
    """Generic *evolving* action-model hypotheses from public source only.

    None of these branches contains the NovelGym solution noun. All moves
    must be in the actual native action set. A successful tested action
    reopens the original task plan.
    """
    names=safe_actions(allowed)
    if failed_action not in names:
        # An original PDDL translation can be absent after novelty; explore
        # non-destructive native names but never fabricate one.
        failed_action=next((x for x in allowed if x.startswith("approach_")),None)
    if not failed_action:
        return []
    own=safe_inventory(view)
    recent=prior[-10:]
    novel=sorted(names-set(old_names))
    local_selects=sorted(x for x in names if
                         x.startswith("select_") and
                         own.get(x[len("select_"):],0)>0)
    novel_selects=[x for x in local_selects if x in novel]
    novel_approaches=[x for x in novel if x.startswith("approach_")]
    prior_near=next((x["action"] for x in reversed(recent)
                     if x.get("native_action_success") and
                        x["action"].startswith("approach_")),None)
    strategies=[]
    def add(label,sequence,priority):
        sequence=[x for x in sequence if x in names]
        if len(sequence)<2 or sequence[-1]!=failed_action:
            return
        strategies.append({"kind":label,"actions":sequence,
                           "status":"PENCIL_UNVERIFIED","priority":priority})
    # First, try changed preconditions by selecting any available new or old
    # inventory tool. A selected item is never proof that it meets a precondition.
    for chosen in novel_selects + [x for x in local_selects if x not in novel_selects]:
        add("selection-tests-old-action",[chosen,failed_action],0 if chosen in novel else 4)
        for behavior in ("collect","break_block","interact_103","use"):
            if behavior in names and behavior!=failed_action:
                add("tool-probe-and-retry",[chosen,behavior,failed_action],
                    2 if chosen in novel else 7)
    # Obstructed old reachability: approach an unfamiliar object and test
    # breaking/removing it, then retry the previous blocked action.
    for approach in novel_approaches:
        for behavior in ("break_block","collect","interact_103","place"):
            if behavior in names:
                add("new-obstacle-probe",[approach,behavior,failed_action],1)
        add("new-object-return",[approach,failed_action],6)
    # Changed preconditions can occur with NO new action names. Try motion and
    # previously successful sites before retrying the SAME familiar action.
    for move in NAVIGATION:
        if move in names:
            add("positional-retest",[move,failed_action],3)
            if prior_near and prior_near in names:
                add("historical-position-and-retest",[prior_near,move,failed_action],5)
    for action in sorted(x for x in names if x.startswith("approach_")):
        if action!=failed_action:
            add("reapproach-and-retry",[action,failed_action],9)
    for behavior in INTERACTIONS:
        if behavior in names and behavior!=failed_action:
            add("existing-tool-action-test",[behavior,failed_action],10)
    # Our original fixed COGNITION-009 policy stopped when this list ended.
    # Instead we systematically grow a safe bounded movement/search frontier.
    navigable=[n for n in NAVIGATION if n in names]
    if navigable:
        for depth in (2,3):
            for path in product(navigable,repeat=depth):
                add("expanded-novel-motion-sequence",[*path,failed_action],
                    30+depth)
    result=[]
    unique=set()
    for p in sorted(strategies,key=lambda x:(x["priority"],
                     len(x["actions"]),tuple(x["actions"]))):
        key=tuple(p["actions"])
        if key in unique:continue
        unique.add(key)
        result.append(p)
    return result


class TransitionMemory:
    def __init__(self):
        self.actions=[]
        self.attempted=set()
        self.by_transition={}
        self.positive_repairs={}
        self.failure_contexts=Counter()
    def observe(self,receipt,failed_action):
        visible={k:v for k,v in receipt.items()
                 if k not in ("owner_goal","owner_given_up")}
        row={"failed_subgoal":failed_action,**visible}
        row["source_hash"]="sha256:"+digest(row)
        self.actions.append(row)
        key=(failed_action,receipt["action"],str(receipt["selected_item_before"]))
        entry=self.by_transition.setdefault(key,{"passes":0,"fails":0,
                       "inventory_effects":Counter(),"last_source_ids":[]})
        entry["passes" if receipt["native_action_success"] else "fails"]+=1
        for item,n in receipt["visible_inventory_delta"].items():
            entry["inventory_effects"][item]+=n
        entry["last_source_ids"].append(row["source_hash"])
        entry["last_source_ids"]=entry["last_source_ids"][-4:]
    def tried(self,failed,program):
        self.attempted.add((failed,tuple(program["actions"])))
    def untried(self,failed,program):
        return (failed,tuple(program["actions"])) not in self.attempted
    def summary(self):
        return {"source_bound_receipts":len(self.actions),
                "unique_source_transition_models":len(self.by_transition),
                "tested_programs":len(self.attempted),
                "verified_locally_recovered_subgoals":dict(self.positive_repairs),
                "failure_families":dict(self.failure_contexts)}


def execute_native_step(env,chosen,mode,iteration,attempt,memory,failed):
    """Native owner is read by outer evaluator ONLY after the policy action."""
    if chosen not in safe_actions(main_actions(env)):
        raise ValueError("NOT_A_PERMITTED_ACTION")
    if env.agent_selection!="agent_0":
        raise RuntimeError("ENGINE_MAIN_TURN_NOT_ACTIVE")
    before=public_observe(env)
    status=native_step(env,chosen)
    after=public_observe(env)
    prior=safe_inventory(before)
    posterior=safe_inventory(after)
    changes={k:posterior.get(k,0)-prior.get(k,0)
             for k in sorted(set(prior)|set(posterior))
             if posterior.get(k,0)!=prior.get(k,0)}
    receipt={
        "attempt":attempt,"step":iteration,"phase":mode,
        "action":chosen,"native_action_success":bool(status.get("success")),
        "native_message":status.get("message",""),
        "visible_inventory_delta":changes,
        "selected_item_before":before.get("inventory",{}).get("selectedItem"),
        "selected_item_after":after.get("inventory",{}).get("selectedItem"),
        "public_position_after":after.get("player",{}).get("pos"),
        "observation_digest":"sha256:"+digest(after),
    }
    memory.observe(receipt,failed)
    # This goal flag is copied only to the EVALUATION transcript, never passed
    # into proposer, TransitionMemory, or MOTIF hypothetical ranking.
    owner_goal=bool(env.internal_state._goal_achieved)
    owner_given_up=bool(env.internal_state._given_up)
    return receipt,after,owner_goal,owner_given_up


def original_plan_step(env,memory,attempt,stepno,failed):
    main=env.agent_manager.agents["agent_0"].agent
    if env.agent_selection!="agent_0":
        raise RuntimeError("ORIGINAL_PLAN_NPC_TURN_NOT_AVAILABLE")
    # Existing upstream action_buffer was *not cleared on failure*; resuming
    # it is how a local repair returns to the original task.
    main.stuck=False
    obs,*_=env.last()
    response=main.policy(obs)
    action=response[0] if isinstance(response,tuple) else response
    native=main_actions(env)
    chosen=native[int(action)]
    if chosen=="nop" and getattr(main,"stuck",False):
        return None,None,False,False
    receipt,view,goal,given=execute_native_step(
        env,chosen,"ORIGINAL_PLAN_RESUME",stepno,attempt,memory,failed)
    if not receipt["native_action_success"]:
        main.set_stuck()
    return receipt,view,goal,given


def run_case(novelty,policy,seed=DEVELOPMENT_SEED):
    if novelty not in DEV_NOVELTIES or policy not in POLICIES or seed!=DEVELOPMENT_SEED:
        raise ValueError("NOT_PREDECLARED_DEVELOPMENT_CASE")
    start=time.process_time()
    normal=make("none",seed)
    old_names=main_actions(normal)
    normal.close()
    memory=TransitionMemory()
    results=[]
    goal=False
    stop=None
    total_recovery=0
    native_motif_calls=0
    graph_receipts=[]
    subgoal_recovered=0
    resume_events=0
    independent_failure_families=set()
    for attempt in range(1,MAX_ATTEMPTS+1):
        env=make(novelty,seed)
        attempt_receipts=[]
        local_events=[]
        used=0
        try:
            # Original baseline followed normally until first surprising failure.
            prefix=original_prefix(env,limit=MAX_MAIN_TOTAL)
            if env.internal_state._goal_achieved:
                goal=True;stop="ORIGINAL_PLAN_SUCCEEDED"
                results.append({"attempt":attempt,"prefix":prefix,
                                "post_failure_actions":0,"owner_goal":True,
                                "stop":"ORIGINAL_PLAN_SUCCEEDED"})
                break
            if not prefix:
                blocked="cannotplan"
                failure_message="original planner produced no action"
            else:
                failed=next((r for r in reversed(prefix) if not r["success"]),None)
                blocked=failed["action"] if failed else "cannotplan"
                failure_message=failed["message"] if failed else "planned actions ended"
            historical=[{"action":r["action"],"native_action_success":r["success"]}
                        for r in prefix]
            local_events.append({"event":"ORIGINAL_PLAN_FAILED",
                                 "action":blocked,"message":failure_message[:140]})
            last_view=public_observe(env,blocked)
            current_program=None
            next_index=0
            in_resume=False
            while used<MAX_RECOVERY:
                if env.terminations.get("agent_0",False) or env.truncations.get("agent_0",False):
                    stop=ENGINE_ERROR_STOP
                    break
                if bool(env.internal_state._goal_achieved):
                    goal=True
                    stop="ORIGINAL_OWNER_GOAL"
                    break
                if in_resume:
                    # One original plan action at a time; any surprising failure
                    # immediately returns control to the model learner.
                    used+=1
                    rec,view,owner_goal,owner_end=original_plan_step(
                        env,memory,attempt,used,blocked)
                    if rec is None:
                        used-=1
                        in_resume=False
                        local_events.append({"event":"ORIGINAL_PLAN_NO_REPLAN",
                                             "blocked":blocked})
                        continue
                    total_recovery+=1
                    attempt_receipts.append(rec)
                    historical.append(rec)
                    last_view=view
                    if owner_goal:
                        goal=True;stop="ORIGINAL_OWNER_GOAL"
                        break
                    if owner_end:
                        stop="ORIGINAL_OWNER_GAVE_UP"
                        break
                    if not rec["native_action_success"]:
                        blocked=rec["action"]
                        failure_message=rec["native_message"]
                        in_resume=False
                        current_program=None
                        next_index=0
                        memory.failure_contexts[blocked]+=1
                        local_events.append({"event":"NEW_UNEXPECTED_FAILURE",
                                             "failed_action":blocked,
                                             "source":"sha256:"+digest(rec)})
                    continue
                # Reconsider candidates after every observed native outcome
                # when no currently admitted microplan remains.
                if current_program is None or next_index>=len(current_program["actions"]):
                    view=public_observe(env,blocked)
                    options=programs_for_failure(
                        main_actions(env),old_names,view,blocked,historical)
                    remaining=[p for p in options if memory.untried(blocked,p)]
                    if not remaining:
                        # This is NOT acceptable as a terminal failure: widen
                        # bounded exploration, revisit movement sequences under
                        # a different orientation or retry post-observation.
                        navigable=[x for x in NAVIGATION if x in safe_actions(main_actions(env))]
                        if navigable:
                            for length in (4,5):
                                for path in product(navigable,repeat=length):
                                    if blocked not in safe_actions(main_actions(env)):
                                        continue
                                    candidate={"kind":"DEEPENED_BOUNDED_EXPLORATION",
                                               "actions":[*path,blocked],
                                               "status":"PENCIL_UNVERIFIED"}
                                    if memory.untried(blocked,candidate):
                                        remaining=[candidate];break
                                if remaining:break
                    if not remaining:
                        # If all proposed short scripts have been tried, force
                        # active reassessment using legal native movement. No
                        # early exit. This fallback cannot constitute a repair.
                        nav=[x for x in NAVIGATION if x in safe_actions(main_actions(env))]
                        if not nav:
                            stop="NO_NATIVE_RECOVERY_ACTIONS"
                            break
                        remaining=[{"kind":"ACTIVE_REASSESSMENT",
                                    "actions":[nav[(attempt+used)%len(nav)],blocked]
                                    if blocked in safe_actions(main_actions(env))
                                    else [nav[(attempt+used)%len(nav)],nav[(attempt+used+1)%len(nav)]],
                                    "status":"PENCIL_UNVERIFIED"}]
                    current_program=remaining[0]
                    next_index=0
                    memory.tried(blocked,current_program)
                    local_events.append({"event":"NEW_HYPOTHESIS_AFTER_OBSERVATION",
                                         "kind":current_program["kind"],
                                         "actions":current_program["actions"],
                                         "attempt":attempt,"at_step":used})
                    if policy=="motif_live" and native_motif_calls<24:
                        # Native MOTIF-003 evaluates hypothetical test options;
                        # it gets NO hidden source truth. No extra game actions.
                        from adapt import native_motif_hypothetical_programs,public_free_graph_hypothesis
                        limited=remaining[:8]
                        try:
                            native_motif_calls+=native_motif_hypothetical_programs(limited)
                            if len(graph_receipts)<3:
                                graph_receipts.append(public_free_graph_hypothesis(
                                    historical,view,current_program))
                        except Exception as err:
                            local_events.append({"event":"NATIVE_ORGAN_DIAGNOSTIC_HOLD",
                                                 "error_type":type(err).__name__})
                chosen=current_program["actions"][next_index]
                next_index+=1
                if chosen not in safe_actions(main_actions(env)):
                    local_events.append({"event":"NOT_A_NATIVE_ALLOWED_ACTION",
                                         "action":chosen})
                    current_program=None
                    continue
                used+=1
                receipt,after,owner_goal,owner_end=execute_native_step(
                    env,chosen,"LIVE_INVESTIGATION",used,attempt,memory,blocked)
                total_recovery+=1
                attempt_receipts.append(receipt)
                historical.append(receipt)
                last_view=after
                if owner_goal:
                    goal=True;stop="ORIGINAL_OWNER_GOAL"
                    break
                if owner_end:
                    stop="ORIGINAL_OWNER_GAVE_UP"
                    break
                if not receipt["native_action_success"]:
                    # Never execute the rest of a failed plan blindly.
                    local_events.append({"event":"TEST_FAILED_REVISE",
                                         "action":chosen,"kind":current_program["kind"],
                                         "source":"sha256:"+digest(receipt)})
                    current_program=None
                    next_index=0
                    continue
                if chosen==blocked:
                    # A once-failed native action now succeeded under a changed
                    # state. This is a verified local result, NOT task completion.
                    subgoal_recovered+=1
                    memory.positive_repairs[blocked]=memory.positive_repairs.get(blocked,0)+1
                    local_events.append({"event":"SUBGOAL_RECOVERED",
                                         "action":blocked,"source":"sha256:"+digest(receipt)})
                    in_resume=True
                    resume_events+=1
                    current_program=None
                    next_index=0
                    continue
                # If the observed effect changes material inventory, immediately
                # retry the obstructed old action rather than following an
                # unrelated precomputed program.
                if receipt["visible_inventory_delta"] and blocked in safe_actions(main_actions(env)):
                    current_program={"kind":"IMMEDIATE_STATE_DELTA_RETEST",
                                     "actions":[blocked],"status":"PENCIL_UNVERIFIED"}
                    next_index=0
                    local_events.append({"event":"REPLAN_ON_NATIVE_DELTA",
                                         "visible_change":receipt["visible_inventory_delta"]})
                # Otherwise, carry on the current tentative microplan; the next
                # action always follows an actual observation, not a blind batch.
            if not goal and stop not in ("NO_NATIVE_RECOVERY_ACTIONS",ENGINE_ERROR_STOP,"ORIGINAL_OWNER_GAVE_UP"):
                stop="ATTEMPT_RECOVERY_BUDGET_EXHAUSTED" if used>=MAX_RECOVERY else "ATTEMPT_UNRESOLVED"
            results.append({"attempt":attempt,"original_prefix":prefix,
                            "post_failure_actions":used,"verified_owner_goal":goal,
                            "ending":stop,"source_receipts":attempt_receipts,
                            "cognitive_events":local_events})
            if goal:break
            # Do not silently accept a temporary planning failure while the
            # remaining attempt budget exists. World reset, retained learning.
            stop=None
        finally:
            env.close()
    return {"experiment":"COGNITION-010",
            "policy":policy,"novelty":novelty,"seed":seed,
            "native_owner_goal":goal,
            "successful_attempt":results[-1]["attempt"] if goal else None,
            "attempts_used":len(results),
            "max_attempts":MAX_ATTEMPTS,
            "all_remaining_attempts_spent_if_unsolved":goal or len(results)==MAX_ATTEMPTS,
            "total_post_failure_actions":total_recovery,
            "source_bound_model":memory.summary(),
            "subgoals_locally_recovered":subgoal_recovered,
            "original_plan_resumes":resume_events,
            "genuine_motif003_hypothetical_options":native_motif_calls,
            "native_free_graph_proposals":graph_receipts,
            "cpu_seconds":round(time.process_time()-start,4),
            "owner_source":"ORIGINAL_UNMODIFIED_NOVELGYM",
            "no_automatic_app_deployment":True,
            "no_private_understory":True,
            "success_only_from_original_owner":True,
            "real_world_actions":0,
            "stop_reason":(results[-1].get("ending") or results[-1].get("stop")) if results else "NO_RUN",
            "attempts":results}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--novelties",nargs="+",choices=DEV_NOVELTIES,default=list(DEV_NOVELTIES))
    parser.add_argument("--policies",nargs="+",choices=POLICIES,default=list(POLICIES))
    args=parser.parse_args()
    cases=[]
    for novelty in args.novelties:
        for policy in args.policies:
            try:
                row=run_case(novelty,policy)
                row["integration_status"]="NATIVE_WORLD_EXECUTED"
            except Exception as exc:
                row={"novelty":novelty,"policy":policy,
                     "integration_status":"BLOCKED_ADAPTER_RUNTIME",
                     "exception_type":type(exc).__name__,
                     "error":str(exc)[:400],
                     "stack":traceback.format_exc(limit=8)[-2200:],
                     "native_owner_goal":None}
            cases.append(row)
            print(f"{novelty} {policy}: {row.get('native_owner_goal')} "
                  f"attempts={row.get('attempts_used','BLOCKED')}",flush=True)
    output={"experiment":"COGNITION-010","stage":"INSPECTED_DEVELOPMENT_VARIANTS",
            "source_sha":"0ad2cbb656177f76ff29f86793269b14879d9b89",
            "world_sha":"f5d06d4f5166ca985ca420c809129a79700d904e",
            "cases":cases,"no_premature_give_up":all(x.get(
              "all_remaining_attempts_spent_if_unsolved",False)
                for x in cases if x["native_owner_goal"] is not None),
            "experimental_generalization_not_established":True}
    output["sha256"]=digest(output)
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True,default=str)+"\n")
    if any(x["native_owner_goal"] is None for x in cases):
        raise SystemExit("Original owner or adapter error, see archived receipts")


if __name__=="__main__":
    main()
