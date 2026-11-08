"""RING-013 post-freeze evaluation: when is "smash on" worth acting on?

Tests the frozen value policy on three author-created unseen-to-selection
populations. It uses the *actual* RING-012 source-perspective lattice as
uncertainty metadata, but viability priors and utility values are explicit
author estimates rather than inferred real-world intent or ground truth.

Executes local SIMULATED trials only. It cannot send a message, open a
website, modify a repository, or perform an external/world-affecting action.

Scores actual modeled benefit and newly unlocked options vs time costs,
question attention, risk, budget and perfect-information synthetic oracle.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path

import scenario,value,freeze

SCHEMA="motif.ring013.postfreeze-action-vs-ambiguity-trial.v1"
STRATEGIES=("FRONTIER","GREEDY","ALWAYS_STOP",
            "ALWAYS_SMASH","ASK_FIRST")

class HOLD(ValueError):
    pass


def verify_frozen(policy):
    if (not isinstance(policy,dict) or policy.get("schema")!=value.POLICY_SCHEMA
            or policy.get("status")!="AUTHOR_SYNTHETIC_OPTION_VALUE_POLICY_FROZEN"
            or policy.get("receipt_sha256")!=value.digest({
                k:v for k,v in policy.items() if k!="receipt_sha256"})
            or policy.get("future_unknown_test_module_imported_during_selection") is not False
            or policy.get("heldout_outcomes_influenced_action_valuation") is not False
            or policy.get("only_internal_simulated_experimentation_autonomous") is not True
            or policy.get("new_real_world_agent_authority")!="NONE"
            or policy.get("automatic_unauthorized_effects")!=0):
        raise HOLD("Unfrozen, modified or authority-promoting policy")
    value.policy_parameters(policy["policy_params"])
    # Reproduce selection from the earlier original authored source.
    # A changed-but-rehashed selected program is also rejected.
    expected=freeze.search()
    if expected!=policy:
        raise HOLD("Policy not reproducible without hidden test outcomes")
    return policy


def oracle_known_outcome(public,hidden,params):
    """Infeasible, perfect-information safe-trial upper bound only."""
    true=hidden["true_world"]
    eligible=("SMASH_A","SMASH_B")
    max_value=0.0
    selected=()
    for size in (1,2):
        for subset in itertools.combinations(eligible,size):
            if sum(public["actions"][x]["budget_units"] for x in subset)>public[
                    "budget_units"]:
                continue
            score=sum(
                public["actions"][name]["rewards"][true]
                +params["affordance_weight"]*public[
                    "actions"][name]["affordances"][true]
                -public["actions"][name]["cost"]
                for name in subset)
            if score>max_value:
                max_value=score
                selected=subset
    return round(max_value,6),selected


def run_frozen(frozen):
    verify_frozen(frozen)
    # Only NOW import the source author-created novel task world.
    import novel
    sources,policy12=freeze.source_methods()
    if (policy12["receipt_sha256"]!=frozen[
            "source_ring012_lattice_policy_sha256"]
            or sources.program_sha256!=frozen["source_ring011_binder_sha256"]):
        raise HOLD("Original perspective evidence source changed")
    params=frozen["policy_params"]
    trials=[]
    for family,seed in (
        ("NOVEL_LANGUAGE",2026111311),
        ("MISLEADING_OPPORTUNITIES",2026111312),
        ("NO_VALUE_BUT_CURIOSITY",2026111313),
    ):
        raw=novel.generate(family,seed=seed,n=20)
        prepared=freeze.prepare_worlds(sources,policy12,raw)
        measurements={}
        witnesses=[]
        for strategy in STRATEGIES:
            m,receipts=freeze.measure(prepared,params,strategy=strategy)
            measurements[strategy]=m
            for i,receipt in enumerate(receipts):
                if strategy=="FRONTIER":
                    witnesses.append({
                        "source_case_id":raw[i]["public"]["id"],
                        "utterance_sha256":value.digest(
                            raw[i]["public"]["source_utterance"]),
                        "source_lattice_sha256":value.digest(
                            prepared[i][2]),
                        "source_alternatives":len(
                            prepared[i][2]["supported_worlds"]),
                        "remaining_unknown_always_possible":prepared[i][2][
                            "other_unmodeled_readings_remain_possible"],
                        "planned_first_move":value.public_decision(
                            raw[i]["public"],prepared[i][2],params)[
                            "best_first_action"],
                        "value_trace":receipt,
                        "hidden_true_viability_not_given_to_planner":True,
                        "external_authority":"NONE",
                    })
        # A genuinely unwarranted "smash" spends time. The perfect-info
        # benchmark only scores what's possible under authored hidden world,
        # never a claim the planner could actually know that future.
        upper=sum(oracle_known_outcome(p,h,params)[0]
                  for p,h,l in prepared)
        trial={
            "family":family,
            "public_source_ids_sha256":value.digest([
                p["id"] for p,h,l in prepared]),
            "case_count":len(prepared),
            "metrics":measurements,
            "case_witnesses":witnesses,
            "perfect_information_hypothetical_utility_upper_bound":round(upper,6),
            "trial_uses_author_hidden_viability_only_in_simulator":True,
            "no_external_actions_or_user_questions_executed":True,
            "novel_templates_not_used_in_selection":True,
            "same_author_constructed_all_examples":True,
        }
        trials.append(trial)
    combined={}
    for strategy in STRATEGIES:
        example=trials[0]["metrics"][strategy]
        combined[strategy]={}
        for key in example:
            if key=="mean_realized_utility":continue
            if type(example[key]) is bool:
                combined[strategy][key]=all(
                    p["metrics"][strategy][key] for p in trials)
            else:
                combined[strategy][key]=round(sum(
                    p["metrics"][strategy][key] for p in trials),6)
        m=combined[strategy]
        m["mean_realized_utility"]=round(
            m["sum_realized_utility"]/m["cases"],6)
    report={
        "schema":SCHEMA,
        "status":"REAL_SAFE_SIMULATOR_EXECUTED_WITH_AMBIGUITY_AWARE_ACTION_SEARCH",
        "frozen_policy_sha256":frozen["receipt_sha256"],
        "source_ring012_ambiguity_policy_sha256":frozen[
            "source_ring012_lattice_policy_sha256"],
        "source_ring011_binder_sha256":frozen["source_ring011_binder_sha256"],
        "test_packets":trials,
        "combined":combined,
        "simulated_perfect_information_upper_bound":round(sum(
            p["perfect_information_hypothetical_utility_upper_bound"]
            for p in trials),6),
        "value_function_includes_information_future_options_cost_risk":True,
        "retains_ambiguity_instead_of_forcing_decision_truth":True,
        "safe_simulated_action_can_run_when_expected_benefit_positive":True,
        "stops_when_no_allowed_safe_action_has_positive_estimated_value":True,
        "human_clarification_is_only_a_simulated_option":True,
        "source_test_outcomes_author_constructed_not_real_user_preference":True,
        "external_effectful_option_never_reaches_executor":True,
        "source_methods_are_correlated_not_independent":True,
        "external_actions_executed":0,
        "new_real_world_tools_installed":0,
        "authority":"NONE",
    }
    report["receipt_sha256"]=value.digest(report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        report=run_frozen(json.loads(args.frozen.read_text()))
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print(json.dumps({
            "schema":report["schema"],
            "cases":sum(p["case_count"] for p in report["test_packets"]),
            "selected_policy":report["frozen_policy_sha256"],
            "combined":report["combined"],
            "perfect_info_upper":report[
                "simulated_perfect_information_upper_bound"],
            "external_effectful_actions":report["external_actions_executed"],
            "receipt_sha256":report["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
