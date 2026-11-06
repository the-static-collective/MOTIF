"""LEGIT-015 executed compounding-capability economy and counterfactuals.

All scenarios here are synthetic and constructed for falsification. These
are NOT estimated future MOTIF improvements and do not automatically
install anything. A bridge to actual LEGIT-014 records makes that
non-calibration explicit. Exact Bellman values are independently matched
against a conventional dynamic-programming implementation; some small
scenarios are additionally checked by brute-force policy-tree recursion.

No generic exponential-growth promise: shortening the horizon, increasing
cost, lowering success probability, or hitting capacity ceilings can
eliminate the value of self-improvement.
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from fractions import Fraction
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from economy import (Economy,Improvement,evaluate,interaction,sensitivity,
                     independent_only,validate,planner,initial,action_values)
from classical_reference import (classical_optimal,tree_optimal,
                                 one_step_action_values,no_reinvestment)
from evidence_bridge import evidence

def scenario_cases():
    # Synthetic resource costs, abstract work/capital units; NOT dollars,
    # not observed CPU milliseconds, and NOT assessed MOTIF probabilities.
    a=Improvement("FASTER_ENGINE",5,2,requires=())
    b=Improvement("NEXT_GENERATOR",8,2,requires=("FASTER_ENGINE",))
    flywheel=Economy(8,5,4,(a,b),64,64)
    independent=Economy(8,12,4,(
        Improvement("INDEX_LIBRARY",4,2),
        Improvement("PROOF_REUSE",4,2)),64,64)
    short=replace(flywheel,horizon=1)
    uncertain=Economy(6,5,4,(
        Improvement("RISKY_REWRITE",5,3,1,2),
        Improvement("DOWNSTREAM",12,2,1,1,("RISKY_REWRITE",))),64,64)
    unlocking=Economy(8,8,4,(
        Improvement("BUILD_VERIFIER",1,1),
        Improvement("COMPOSE_NEW_SOLVER",4,3,1,1,("BUILD_VERIFIER",))),64,64)
    saturated=Economy(8,12,4,(
        Improvement("A_CAP_LIMIT",4,4),
        Improvement("B_CAP_LIMIT",4,4)),64,12)
    guaranteed_bad=Economy(7,12,4,(
        Improvement("CERTAIN_FAILURE",7,4,0,1),),64,64)
    return {
        "CASHFLOW_COMPOUND_AND_UNLOCK":flywheel,
        "MULTIPLICATIVE_INTERACTION":independent,
        "TOO_LATE_TO_PAY_OFF":short,
        "UNCERTAIN_SUCCESS":uncertain,
        "CAPABILITY_GATE_UNLOCKS_NEW_ACTION":unlocking,
        "SATURATION_ENDS_COMPOUNDING":saturated,
        "CERTAIN_FAILURE_SHOULD_BE_REFUSED":guaranteed_bad,
    }

def stringify(result):
    if isinstance(result,Fraction):return str(result)
    if isinstance(result,tuple):return [stringify(x) for x in result]
    if isinstance(result,list):return [stringify(x) for x in result]
    if isinstance(result,dict):return {str(k):stringify(v) for k,v in result.items()}
    return result

def execute():
    empirical=evidence()
    cases=scenario_cases()
    samples={}
    for label,scenario in cases.items():
        candidate=evaluate(scenario)
        conventional=classical_optimal(scenario)
        direct=one_step_action_values(scenario)
        if conventional!=candidate["best_expected_useful_work"]:
            raise AssertionError("MOTIF economy disagrees with exact conventional Bellman")
        if direct!=candidate["action_values"]:
            raise AssertionError("Counterfactual first-action economics wrong")
        if scenario.horizon<=7 and len(scenario.investments)<=3:
            brute,action=tree_optimal(scenario)
            if brute!=conventional or action!=candidate["first_action"]:
                raise AssertionError("An independent exhaustive policy tree refutes planning")
        else:
            brute=None
        samples[label]={
            "best_expected_useful_work":candidate["best_expected_useful_work"],
            "do_no_investment":candidate["baseline_work_only"],
            "model_improvement_over_work_only":candidate["gain_vs_never_invest"],
            "first_action":candidate["first_action"],
            "cost_of_forced_work_first":candidate["cost_of_forcing_work_before_improvement"],
            "first_action_counterfactual_values":candidate["action_values"],
            "independent_classical_dp_exact_agreement":True,
            "independent_full_policy_tree_checked":brute is not None,
            "reachable_dynamic_program_states":candidate["bellman_states_evaluated"],
            "one_all_success_illustrative_path":candidate["success_path_only_not_expected_trajectory"],
        }
    extra={
        "non_additive_synergy":interaction(cases["MULTIPLICATIVE_INTERACTION"],
                                           "INDEX_LIBRARY","PROOF_REUSE"),
        "risk_assumption_sensitivity":sensitivity(cases["UNCERTAIN_SUCCESS"],
                                                   "RISKY_REWRITE"),
    }
    # Semantic falsifiers, not just nice-looking results.
    if samples["CASHFLOW_COMPOUND_AND_UNLOCK"]["first_action"]!="FASTER_ENGINE":
        raise AssertionError("Cashflow self-financing example didn't invest")
    if samples["TOO_LATE_TO_PAY_OFF"]["first_action"]!="WORK":
        raise AssertionError("Late investment wasn't refused")
    if samples["CERTAIN_FAILURE_SHOULD_BE_REFUSED"]["first_action"]!="WORK":
        raise AssertionError("Known failure was treated as growth")
    if extra["non_additive_synergy"]["net_synergy"]<=0:
        raise AssertionError("The intended multiplicative example lacks synergy")
    if samples["SATURATION_ENDS_COMPOUNDING"]["best_expected_useful_work"]>=(
            samples["MULTIPLICATIVE_INTERACTION"]["best_expected_useful_work"]):
        raise AssertionError("Saturation did not bound repeated gains")

    result={
        "experiment":"MOTIF-LEGIT-015",
        "title":"THE_COMPOUNDING_IMPROVEMENT_ECONOMY",
        "formal_model":"FINITE_HORIZON_STOCHASTIC_BELLMAN_EXACT_FRACTIONS",
        "core_concept":"PRODUCTIVE_CAPACITY_INCREASES_FUTURE_WORK_AND_FINANCES_LATER_IMPROVEMENTS",
        "real_prior_trial_boundary":empirical,
        "scenario_assumptions":"SYNTHETIC_NOT_CALIBRATED_FROM_LEGIT014",
        "examples":samples,
        "demonstrations":extra,
        "source_created_by_model":"NONE",
        "third_party_formal_solver_invoked_for_economy":False,
        "exact_independent_classical_DP_compared":True,
        "general_superiority_over_classical":False,
        "discovery_probabilities_real_world_validated":False,
        "unbounded_exponential_growth_claimed":False,
        "negative_cases_tested":True,
        "production_improvement_promotion":False,
        "automated_external_actions":0,
        "state":"RESEARCH_HOLD",
    }
    # Provenance labels, all numerical economics are model-dependent.
    return stringify(result)

def main():
    output=execute()
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("Usage: python benchmark.py [--emit]")
    if sys.argv[1:]:
        Path("/tmp/motif-legit015-improvement-economy.json").write_text(
            json.dumps(output,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
