"""COGNITION-008 — Two equal-information native NovelGym recovery controllers.

Original simulation owns state/actions and success. Action proposals are built
only from public NovelGym action names, public DIARC observation, and the
historical pre-novelty action-name list; never from novelty implementation code.
No strings containing an engine-specific novelty solution appear in the policy.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys
import time
import traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"cognition001"))
sys.path.insert(0,str(HERE.parent/"cognition003"))
from aperture_probe import make,public_observe,main_actions,native_to_main,original_prefix
from circuit import native_affordance
from resurface import _native_graph

MAX_ATTEMPTS=10
MAX_RECOVERY=80
POLICIES=("classical_adaptive","motif_adaptive")


def safe_inventory(public_observation):
    slots=public_observation.get("inventory",{}).get("slots",[])
    return {r["item"]:int(r["count"]) for r in slots if isinstance(r,dict)
            and isinstance(r.get("item"),str) and isinstance(r.get("count"),(float,int))}


def proposer(actions,old_actions,observation,history):
    """Grammar of generic new tool actions, no novelty- or goal-specific names.

    Source-conditioned: a native failed action, publicly reported inventory,
    original available action repertoire and history of actual native actions.
    """
    names=set(actions)
    prior=set(old_actions)
    newcomer=sorted(names-prior)
    available=safe_inventory(observation)
    failed=observation.get("failedAction")
    if isinstance(failed,tuple):
        failed=failed[0]
    if not isinstance(failed,str) or failed not in names:
        return []
    prior_approach=next((r["action"] for r in reversed(history)
                         if r["action"].startswith("approach_") and
                         r["success"]),None)
    # A remembered visit to a workstation or target becomes a return route;
    # a failed craft alone never authorizes action toward a hidden target.
    new_selects=[a for a in newcomer
                 if a.startswith("select_") and
                 available.get(a[len("select_"):],0)>0]
    approaches=[a for a in newcomer if a.startswith("approach_")]
    candidates=[]
    for tool in new_selects:
        # The generic productive test is: equip an encountered unfamiliar
        # object, try normal contact at the failed site, retry the original step.
        for interaction in ("collect","use","place","interact_103"):
            if interaction in names:
                candidates.append({
                    "hypothesis":f"new-tool-contact:{tool}:{interaction}",
                    "actions":[tool, interaction, failed],
                    "support":["native-inventory","native-novel-actions",
                               "historical-failed-action"],
                    "status":"PENCIL_UNTESTED",
                })
    for approach in approaches:
        suffix=approach[len("approach_"):]
        select="select_"+suffix
        # An object may be visible in native action vocabulary but not yet in
        # inventory. Sample collection rather than assuming its effects.
        template=[approach]
        if "collect" in names:template.append("collect")
        if select in names:template.append(select)
        if prior_approach in names:template.append(prior_approach)
        for interaction in ("collect","use","place"):
            if interaction in names:
                candidates.append({
                    "hypothesis":f"unfamiliar-object-sequence:{suffix}:{interaction}",
                    "actions":template+[interaction,failed],
                    "support":["native-novel-actions","historical-location"],
                    "status":"PENCIL_UNTESTED",
                })
    # Sort on action count, then fixed lexical action order. This conventional
    # search order is shared with the MOTIF-instrumented arm.
    unique={}
    for c in candidates:
        a=tuple(c["actions"])
        if a not in unique:unique[a]=c
    return sorted(unique.values(),key=lambda c:(len(c["actions"]),tuple(c["actions"])))


def native_motif_hypothetical_programs(programs):
    """Actual MOTIF-003 affordance API; owner action outcome is NOT supplied."""
    native=native_affordance()
    before=frozenset({("status","unverified")})
    offered=tuple(programs)
    def successor(world,unused):
        for idx,c in enumerate(offered):
            option=("skill",f"propose-test-program-{idx}")
            if option not in world:
                yield (f"investigate-{idx}",(c["hypothesis"],),
                       world|frozenset({option}))
    evaluated=native.analyze_first_moves(
        before,(),successor,lambda after,prior:len(after-prior),
        horizon=1,max_worlds=64)
    if len(evaluated)!=len(offered):
        raise RuntimeError("MOTIF_003_AFFORDANCE_MISMATCH")
    return len(evaluated)


def public_free_graph_hypothesis(prefix,observation,program):
    """Source-bound real FG proposal, not admitted owner truth."""
    rec_id,pkt_id,validate,neighbors=_native_graph()
    sources=[]
    for idx,record in enumerate((prefix,observation)):
        source={
            "source_class":"unresolved-receipt",
            "locator":{"system":"NovelGym native public-observation experiment",
                       "coordinate":f"cog008:development:input-{idx}",
                       "revision":"source-sha-fixed",
                       "resolution":"observed nonprivileged action history"},
            "observed_at":"2026-11-12",
            "acquisition":"native NovelGym nonprivileged view",
            "digest":"sha256:"+sha256(json.dumps(record,sort_keys=True,
                    default=str).encode()).hexdigest(),
            "excerpt":"Native observable earlier action and inventory, not hidden owner model",
            "access":"public","export":"portable","authority":"none",
        }
        source["id"]=rec_id("source",source)
        sources.append(source)
    nodes=[]
    for label in ("Old action failed","Unfamiliar tool candidate",
                  "Test original goal again"):
        n={"kind":"question","label":label,"status":"unresolved",
           "source_ids":[s["id"] for s in sources]}
        n["id"]=rec_id("node",n)
        nodes.append(n)
    links=[]
    for i,j in ((0,1),(1,2)):
        l={"from":nodes[i]["id"],"to":nodes[j]["id"],
           "verb":"connects","status":"unresolved",
           "qualifier":"conditional-test-not-established-effect",
           "source_ids":[s["id"] for s in sources],"authority":"none"}
        l["id"]=rec_id("link",l)
        links.append(l)
    packet={
        "schema":"free-graph.packet/v0",
        "purpose":"Native failed-plan investigation, speculative provenance",
        "modes":["re-enter","seed"],
        "scope":{"task":"Investigate original unmodeled failed action",
                 "worlds":["NovelGym public engine"],
                 "as_of":"2026-11-12","resolution":"PENCIL not verified"},
        "task_world_cut":{"status":"unresolved",
             "selected_ids":[s["id"] for s in sources]+
                            [n["id"] for n in nodes]+[l["id"] for l in links],
             "owner_head_source_ids":[],
             "omitted":[{"door":"private MEMENTO owner memory",
                         "reason":"not part of external public environment trial"}],
             "rationale":"Similarity between unfamiliar action and prior failure only warrants a test"},
        "sources":sources,"nodes":nodes,"links":links,
        "residual_fog":["An available action name does not establish a causal remedy.",
                        "No model's owner state used as proposal input."],
        "non_imports":["No native game hidden operator or novel fire predicate read."],
        "extensions":{"hypothesis_status":"PENCIL_UNTESTED",
                      "program_length":len(program["actions"]),
                      "synthetic_research":True},
    }
    packet["packet_id"]=pkt_id(packet)
    if validate(packet):
        raise RuntimeError("FREE_GRAPH_NATIVE_PACKET_INVALID")
    local=neighbors(packet,nodes[1]["id"],depth=1)
    if validate(local):
        raise RuntimeError("FREE_GRAPH_NATIVE_NEIGHBORS_INVALID")
    return {"native_validated":True,"packet_id":packet["packet_id"],
            "unresolved_links":len(links),"native_traversal_nodes":len(local["nodes"]),
            "owner_admission":False}


def advance_npcs(env):
    for _ in range(20):
        if env.agent_selection=="agent_0":
            return True
        name=env.agent_selection
        if env.terminations.get(name,False) or env.truncations.get(name,False):
            return False
        other=env.agent_manager.agents[name].agent
        obs,*_=env.last()
        action=other.policy(obs)
        if isinstance(action,tuple):a,extra=action
        else:a,extra=action,{}
        env.step(a,extra)
    return False


def action_owner_receipt(env,name,step,attempt):
    """All policy decisions happen before owner success check."""
    if not advance_npcs(env):
        raise RuntimeError("ENGINE_NEVER_RETURNED_TO_AGENT")
    before=public_observe(env)
    native=native_to_main(env,name)
    after=public_observe(env)
    first=safe_inventory(before)
    second=safe_inventory(after)
    changed={k:second.get(k,0)-first.get(k,0)
             for k in sorted(set(first)|set(second))
             if second.get(k,0)!=first.get(k,0)}
    receipt={"attempt":attempt,"recovery_step":step,
             "action":name,"native_action_success":native.get("success",False),
             "native_failure_message":native.get("message","")[:180],
             "visible_inventory_delta":changed,
             "selected_item_before":before["inventory"]["selectedItem"],
             "selected_item_after":after["inventory"]["selectedItem"],
             "public_position_after":after["player"]["pos"],
             # Owner outcome only for evaluator reporting; neither proposer
             # nor ranking function has access to these fields.
             "evaluator_goal_after":bool(env.internal_state._goal_achieved),
             "evaluator_given_up_after":bool(env.internal_state._given_up)}
    return receipt


def run_policy(policy,seed=1,novelty="fire"):
    if policy not in POLICIES or not ((novelty=="fire" and seed==1) or
            (novelty in ("fence","axe","chest","dist_trade") and
             seed in (31001,31021,31041))):
        raise ValueError("UNREGISTERED_NOVELGYM_EVALUATION_CASE")
    start_cpu=time.process_time()
    old=make("none",seed)
    old_actions=main_actions(old)
    old.close()
    history=[]
    source_programs=[]
    attempted=[]
    all_attempts=[]
    native_options=0
    native_graph=None
    success=False
    for attempt in range(1,MAX_ATTEMPTS+1):
        env=make(novelty,seed)
        try:
            native=main_actions(env)
            prefix=original_prefix(env)
            last=prefix[-1]
            if last["success"] or bool(env.internal_state._goal_achieved):
                all_attempts.append({"attempt":attempt,"baseline_finished":True,
                                      "owner_goal":bool(env.internal_state._goal_achieved)})
                success=bool(env.internal_state._goal_achieved)
                break
            public=public_observe(env,last["action"])
            if not source_programs:
                source_programs=proposer(native,old_actions,public,prefix)
                if policy=="motif_adaptive":
                    native_options=native_motif_hypothetical_programs(source_programs)
                    if source_programs:
                        native_graph=public_free_graph_hypothesis(prefix,public,source_programs[0])
            if not source_programs:
                all_attempts.append({"attempt":attempt,"status":"HOLD_NO_OBSERVABLE_PROPOSALS",
                                      "owner_goal":False,"original_prefix":prefix})
                break
            # Both policies receive the same explicit candidate scripts,
            # the same status and outcome receipts, and the same reorder rules.
            remaining=[p for p in source_programs
                       if p["hypothesis"] not in attempted]
            if not remaining:
                break
            program=remaining[0]
            attempted.append(program["hypothesis"])
            actions=[]
            for index,name in enumerate(program["actions"][:MAX_RECOVERY],1):
                if name not in native:
                    actions.append({"action":name,"status":"NOT_NATIVE_ACTION"})
                    break
                step=action_owner_receipt(env,name,index,attempt)
                actions.append(step)
                history.append({"attempt":attempt,"program":program["hypothesis"],
                                "step":step})
                # Owner goal only determines benchmark episode termination,
                # never which action will be attempted next.
                if step["evaluator_goal_after"] or step["evaluator_given_up_after"]:
                    break
            success=bool(env.internal_state._goal_achieved)
            all_attempts.append({"attempt":attempt,"program":program,
                                  "native_owner_goal":success,
                                  "original_prefix":prefix,
                                  "observed_recovery":actions})
            if success:
                break
        finally:
            env.close()
    return {"policy":policy,"seed":seed,"novelty":novelty,
            "task":"original NovelGym "+novelty,
            "source":"ORIGINAL_NOVELGYM_NATIVE_OWNER",
            "verified_owner_success":success,
            "original_planner_owner_success":bool(all_attempts and all_attempts[0].get("baseline_finished") and success),
            "recovery_owner_success":bool(success and all_attempts and not all_attempts[0].get("baseline_finished")),
            "recovery_attempted":bool(attempted),
            "first_successful_attempt":(len(all_attempts) if success else None),
            "attempts_used":len(all_attempts),
            "novel_action_candidates":len(source_programs),
            "native_motif003_options":native_options,
            "native_free_graph":native_graph,
            "source_bound_hypotheses":len(attempted),
            "observed_recovery_actions":len(history),
            "negative_native_receipts":sum(not x["step"]["native_action_success"]
                                           for x in history),
            "cpu_seconds":round(time.process_time()-start_cpu,5),
            "original_owner_history":all_attempts,
            "private_understory_imported":False,
            "model_trained":False,
            "app_deployed":False,"real_world_external_actions":0}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    rows=[run_policy(p) for p in POLICIES]
    out={"experiment":"COGNITION-008","phase":"DEVELOPMENT_ONE_SEED",
         "original_game_source_sha":"0ad2cbb656177f76ff29f86793269b14879d9b89",
         "original_engine_source_sha":"f5d06d4f5166ca985ca420c809129a79700d904e",
         "protocol_seed":1,"max_attempts":MAX_ATTEMPTS,
         "matched_policy_candidates":True,
         "strong_classical_is_adaptive_grammar":True,
         "original_owner_outcomes_not_synthetic":True,
         "proof_of_generalization":False,"rows":rows}
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True,default=str)+"\n")
    print(json.dumps([{k:v for k,v in r.items()
                       if k not in ("original_owner_history",)}
                      for r in rows],indent=2,default=str))


if __name__=="__main__":
    main()
