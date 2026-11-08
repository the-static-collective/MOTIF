"""RING-013 measured hyperedges: VALUE of inquiry, action, and further action.

The evidentiary record must make optimistic losses, wasted curiosity,
opportunity gained, simulated human-attention costs and STOP explicit.

No language interpretation, prospective modeled payoff or source-author
label is upgraded to an independently verified real-world fact or an
authorization to execute external work.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import scenario,value,trial

SCHEMA="motif.ring013.option-value-evidence-hypergraph.v1"

class HOLD(ValueError):
    pass


def digest(x):
    return value.digest(x)


def verify(frozen,report):
    trial.verify_frozen(frozen)
    if (not isinstance(report,dict) or report.get("schema")!=trial.SCHEMA
            or report.get("status")!=
            "REAL_SAFE_SIMULATOR_EXECUTED_WITH_AMBIGUITY_AWARE_ACTION_SEARCH"
            or report.get("receipt_sha256")!=digest({
                k:v for k,v in report.items() if k!="receipt_sha256"})
            or report.get("frozen_policy_sha256")!=frozen["receipt_sha256"]
            or report.get("source_ring012_ambiguity_policy_sha256")!=frozen[
                "source_ring012_lattice_policy_sha256"]
            or report.get("retains_ambiguity_instead_of_forcing_decision_truth") is not True
            or report.get("source_test_outcomes_author_constructed_not_real_user_preference") is not True
            or report.get("external_effectful_option_never_reaches_executor") is not True
            or report.get("external_actions_executed")!=0
            or report.get("new_real_world_tools_installed")!=0
            or report.get("authority")!="NONE"):
        raise HOLD("Non-source-backed or externally empowered action plan")
    packets=report.get("test_packets")
    if (not isinstance(packets,list) or len(packets)!=3
            or {p.get("family") for p in packets}!={
                "NOVEL_LANGUAGE","MISLEADING_OPPORTUNITIES",
                "NO_VALUE_BUT_CURIOSITY"}):
        raise HOLD("Three source-shift falsifiers are required")
    seen=set()
    recomputed={}
    for packet in packets:
        source=packet.get("public_source_ids_sha256")
        rows=packet.get("case_witnesses")
        if (type(source) is not str or len(source)!=64 or source in seen
                or packet.get("case_count")!=20
                or not isinstance(rows,list) or len(rows)!=20
                or packet.get("trial_uses_author_hidden_viability_only_in_simulator") is not True
                or packet.get("no_external_actions_or_user_questions_executed") is not True
                or packet.get("novel_templates_not_used_in_selection") is not True
                or packet.get("same_author_constructed_all_examples") is not True):
            raise HOLD("Duplicated or overclaimed synthetic world")
        seen.add(source)
        for strategy in trial.STRATEGIES:
            outputs=[]
            for record in rows:
                if (record.get("hidden_true_viability_not_given_to_planner") is not True
                        or record.get("remaining_unknown_always_possible") is not True
                        or record.get("external_authority")!="NONE"):
                    raise HOLD("Source world hidden outcome or ambiguity incorrectly promoted")
                if strategy=="FRONTIER":
                    r=record["value_trace"]
                    if (r["steps"] and record["planned_first_move"]!=r[
                            "steps"][0]["action"]
                            or not r["steps"] and record["planned_first_move"]!="STOP"):
                        raise HOLD("Planner transcript first move contradicts its receipt")
                else:
                    r=record.get("control_action_traces",{}).get(strategy)
                if not isinstance(r,dict):
                    raise HOLD("Missing source-matched method trajectory")
                if (r.get("strategy")!=strategy
                        or r.get("source_case_id")!=record.get("source_case_id")
                        or r.get("human_interruption_count")!=0
                        or r.get("all_actions_safe_simulated_only") is not True
                        or r.get("no_real_effects") is not True
                        or r.get("authority")!="NONE"
                        or r.get("budget_units_remaining",0)<0
                        or r.get("action_count")!=len(r.get("steps",[]))
                        or r.get("action_count",0)>3):
                    raise HOLD("Mismatched action trajectory or permission claim")
                used=set()
                for step in r["steps"]:
                    name=step.get("action")
                    if (name not in value.ALLOWED or name in used
                            or step.get("permission") not in (
                                "INTERNAL_READONLY","INTERNAL_REVERSIBLE",
                                "HUMAN_ATTENTION_SIMULATED_ONLY")
                            or step.get("internal_simulator_executed") is not True
                            or step.get("external_effect_executed") is not False
                            or step.get("hidden_world_never_supplied_to_planner") is not True):
                        raise HOLD("Unapproved or repeated action in measured transcript")
                    used.add(name)
                if r.get("internal_smash_count")!=sum(
                        x["action"] in ("SMASH_A","SMASH_B")
                        for x in r["steps"]):
                    raise HOLD("Smash count laundered")
                if (abs(r["realized_utility"]-sum(
                        x["realized_utility"] for x in r["steps"]))>0.00002
                        or r.get("simulated_user_question_count")!=sum(
                            x["action"]=="ASK_USER" for x in r["steps"])):
                    raise HOLD("Fabricated realized value or attention count")
                outputs.append(r)
            totals={
                "cases":len(outputs),
                "sum_realized_utility":round(sum(x["realized_utility"]
                                                  for x in outputs),6),
                "sum_internal_smashes":sum(x["internal_smash_count"]
                                           for x in outputs),
                "sum_internal_actions":sum(x["action_count"]
                                           for x in outputs),
                "negative_utility_cases":sum(x["realized_utility"]<0
                                             for x in outputs),
                "sum_new_affordances":sum(x["realized_new_affordance_count"]
                                         for x in outputs),
                "simulated_user_questions":sum(
                    x["simulated_user_question_count"] for x in outputs),
                "real_user_interruptions":sum(
                    x["human_interruption_count"] for x in outputs),
                "effectful_actions_executed":0,
                "start_entropy_sum":round(sum(x["initial_entropy_bits"]
                                               for x in outputs),6),
                "end_entropy_sum":round(sum(x["final_entropy_bits"]
                                             for x in outputs),6),
                "all_cases_retained_unmodeled_possible":True,
                "all_actions_reversible_simulation":True,
            }
            totals["mean_realized_utility"]=round(
                totals["sum_realized_utility"]/len(outputs),6)
            if totals!=packet.get("metrics",{}).get(strategy):
                raise HOLD("Action value aggregate differs from individual source traces")
            combined=recomputed.setdefault(strategy,{k:0 for k in totals
                                                      if k not in (
                                                          "mean_realized_utility",
                                                          "all_cases_retained_unmodeled_possible",
                                                          "all_actions_reversible_simulation")})
            for key in combined:
                combined[key]+=totals[key]
    for name,r in recomputed.items():
        for key in ("sum_realized_utility","start_entropy_sum","end_entropy_sum"):
            r[key]=round(r[key],6)
        r["mean_realized_utility"]=round(
            r["sum_realized_utility"]/r["cases"],6)
        r["all_cases_retained_unmodeled_possible"]=True
        r["all_actions_reversible_simulation"]=True
    if recomputed!=report.get("combined"):
        raise HOLD("Combined strategies do not reconcile with individual outcomes")
    return packets


def build(frozen,report):
    packs=verify(frozen,report)
    policy="policy:"+frozen["receipt_sha256"]
    source="source:"+frozen["source_ring012_lattice_policy_sha256"]
    belief="task-prior:"+frozen["source_train_source_sha256"]
    selection="selection:"+frozen["source_dev_source_sha256"]
    nodes=[
        {"id":source,"kind":"RING012_CORRELATED_OPEN_WORLD_LANGUAGE_SOURCE"},
        {"id":belief,"kind":"AUTHOR_PRIOR_SYNTHETIC_ACTION_VALUE_SOURCE"},
        {"id":selection,"kind":"AUTHOR_TRAINED_OPTION_VALUE_PREFERENCE"},
        {"id":policy,"kind":"FROZEN_FINITE_SAFE_ACTION_POLICY",
         "new_external_permission":False},
    ]
    ref=[]
    for packet in packs:
        point="test:"+packet["public_source_ids_sha256"]
        ref.append(point)
        nodes.append({
            "id":point,
            "kind":"AUTHOR_CREATED_HIDDEN_SIMULATION_OUTCOME",
            "family":packet["family"],
            "case_count":packet["case_count"],
            "real_person_value_preferences_verified":False,
        })
    frontier=report["combined"]["FRONTIER"]
    stop=report["combined"]["ALWAYS_STOP"]
    ask=report["combined"]["ASK_FIRST"]
    smash=report["combined"]["ALWAYS_SMASH"]
    greedy=report["combined"]["GREEDY"]
    edges=[
        {
            "id":"constructed:incomplete-knowledge-to-safe-reversible-action",
            "kind":"SOURCE_BASED_BOUNDED_VALUE_OF_INFORMATION_AND_ACTION",
            "tails":[source,belief,selection],
            "heads":[policy,
                     "option:reversible-trial-with-positive-modeled-value",
                     "option:read-only-evidence-gathering",
                     "option:leave-ambiguity-unresolved",
                     "option:stop-negative-interest-research"],
            "training_selection_candidates":frozen["candidate_policies_executed"],
            "source_classification_is_not_executable_permission":True,
            "future_options_are_author_assigned_proxy_rewards":True,
        },
        {
            "id":"measured:action-value-interest-and-opportunity-costs",
            "kind":"UNSEEN_TO_SELECTION_SYNTHETIC_SEQUENTIAL_DECISION_TRIAL",
            "tails":[policy,source,belief,selection,*ref],
            "heads":["benefit:realized_sandbox_trial_value",
                     "benefit:new_synthetic_affordance_options",
                     "risk:negative_value_reversible_smashes",
                     "cost:user_attention_if_question_chosen_in_simulation",
                     "frontier:empirical_value_of_action_without_known_truth"],
            "total_cases":frontier["cases"],
            "frontier_policy":frontier,
            "always_stop_control":stop,
            "always_smash_control":smash,
            "greedy_one_step_control":greedy,
            "ask_before_act_control":ask,
            "perfect_info_oracle_is_unattainable_simulated_bound":report[
                "simulated_perfect_information_upper_bound"],
            "negative_value_cases_not_suppressed":frontier[
                "negative_utility_cases"],
            "real_user_actions_executed":0,
            "outcomes_are_synthetic_not_proven_general_ability":True,
        },
    ]
    result={
        "schema":SCHEMA,
        "source_policy_sha256":frozen["receipt_sha256"],
        "source_trial_sha256":report["receipt_sha256"],
        "vertices":nodes,"hyperedges":edges,
        "positive_action_value_can_proceed_without_ambiguity_resolution":True,
        "interest_alone_can_be_outweighed_by_time_and_risk":True,
        "no_action_without_authorized_internal_permission":True,
        "truthful_negative_results_preserved":True,
        "independent_human_outcome_validation":False,
        "real_world_autonomous_execution_demonstrated":False,
        "new_external_tool_permissions":0,
        "external_actions_executed":False,"authority":"NONE",
    }
    result["receipt_sha256"]=value.digest(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",required=True,type=Path)
    p.add_argument("--trial",required=True,type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        result=build(json.loads(args.frozen.read_text()),
                     json.loads(args.trial.read_text()))
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
        obs=result["hyperedges"][1]
        print(json.dumps({
            "schema":result["schema"],
            "cases":obs["total_cases"],
            "frontier_realized_utility":obs["frontier_policy"]["sum_realized_utility"],
            "frontier_simulated_smashes":obs["frontier_policy"]["sum_internal_smashes"],
            "frontier_negative_cases":obs["frontier_policy"]["negative_utility_cases"],
            "always_smash_realized_utility":obs["always_smash_control"]["sum_realized_utility"],
            "receipt":result["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
