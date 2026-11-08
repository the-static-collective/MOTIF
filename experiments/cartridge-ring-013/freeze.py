"""RING-013 precommit: select value-of-next-action policy on previous data ONLY.

This selection is supervised on authored synthetic realized utilities. It
has no access to RING-013 novel.py, which is imported only after freeze
verification by trial.py. Source-language ambiguity comes from actual
RING-012 methods; *viability* priors and realized economic rewards are
separate author-defined task estimates, not inferred human preferences.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-012"))
import lattice,calibration
import scenario,value

SCHEMA=value.POLICY_SCHEMA
PARAMS=("information_weight","affordance_weight","risk_weight",
        "ambiguity_sensitivity")


def source_methods():
    prior_uncertainty=calibration.calibrate()
    previous=calibration.search.run()
    train,program=calibration.benchmark.verify_frozen(previous)
    sources=lattice.Sources(train,program)
    if (sources.train_sha256!=prior_uncertainty["source_train_sha256"]
            or sources.program_sha256!=prior_uncertainty["derived_program_sha256"]):
        raise ValueError("Mismatch between RING-012 source and candidate method lineage")
    return sources,prior_uncertainty


def prepare_worlds(sources,policy12,rows):
    prepared=[]
    for case in rows:
        public=case["public"]
        scenario.verify_public(public)
        lattice_result=lattice.combine(
            public["source_utterance"],public["source_event"],
            public["source_carrier"],sources,policy12)
        if (lattice_result["authority"]!="NONE"
                or lattice_result["external_action_executed"] is not False
                or lattice_result["other_unmodeled_readings_remain_possible"] is not True):
            raise ValueError("RING-012 model illegally collapsed ambiguity")
        prepared.append((public,case["hidden"],lattice_result))
    return prepared


def measure(prepared,params,*,strategy="FRONTIER"):
    totals={
        "cases":0,"sum_realized_utility":0.0,
        "sum_internal_smashes":0,"sum_internal_actions":0,
        "negative_utility_cases":0,"sum_new_affordances":0,
        "simulated_user_questions":0,
        "real_user_interruptions":0,
        "effectful_actions_executed":0,
        "start_entropy_sum":0.0,"end_entropy_sum":0.0,
        "all_cases_retained_unmodeled_possible":True,
        "all_actions_reversible_simulation":True,
    }
    receipts=[]
    for public,hidden,lattice_result in prepared:
        outcome=value.simulate(public,hidden,lattice_result,params,
                               strategy=strategy)
        totals["cases"]+=1
        totals["sum_realized_utility"]+=outcome["realized_utility"]
        totals["sum_internal_smashes"]+=outcome["internal_smash_count"]
        totals["sum_internal_actions"]+=outcome["action_count"]
        totals["negative_utility_cases"]+=int(outcome["realized_utility"]<0)
        totals["sum_new_affordances"]+=outcome["realized_new_affordance_count"]
        totals["simulated_user_questions"]+=outcome["simulated_user_question_count"]
        totals["real_user_interruptions"]+=outcome["human_interruption_count"]
        totals["start_entropy_sum"]+=outcome["initial_entropy_bits"]
        totals["end_entropy_sum"]+=outcome["final_entropy_bits"]
        totals["all_cases_retained_unmodeled_possible"] &= (
            lattice_result["other_unmodeled_readings_remain_possible"])
        totals["all_actions_reversible_simulation"] &= (
            outcome["all_actions_safe_simulated_only"])
        receipts.append(outcome)
    for k in ("sum_realized_utility","start_entropy_sum","end_entropy_sum"):
        totals[k]=round(totals[k],6)
    totals["mean_realized_utility"]=round(
        totals["sum_realized_utility"]/max(1,totals["cases"]),6)
    return totals,receipts


def search():
    sources,prior12=source_methods()
    train=scenario.make_cases(split="train",seed=2026111301,n=24)
    dev=scenario.make_cases(split="dev",seed=2026111302,n=24)
    train_prepared=prepare_worlds(sources,prior12,train)
    dev_prepared=prepare_worlds(sources,prior12,dev)
    attempts=[]
    for info,option,risk,ambiguity in itertools.product(
        (0.0,0.7),(0.0,0.5,1.0),(0.0,0.7),(0.0,0.4)):
        params={
            "information_weight":info,
            "affordance_weight":option,
            "risk_weight":risk,
            "ambiguity_sensitivity":ambiguity,
        }
        # The entire 48 source training/development episodes are selection
        # data. Hidden outcomes are only read AFTER each policy decision.
        tr,_=measure(train_prepared,params)
        dev_result,_=measure(dev_prepared,params)
        attempts.append({
            "params":params,"train_metrics":tr,"dev_metrics":dev_result,
            "program_receipt_sha256":value.digest(params),
        })
    # The author explicitly values expansion of possible future actions
    # and real payoff, but not unproductive "curiosity" for its own sake.
    # Rank on combined measured utility and downside losses. The 24
    # potential configurations ARE model-selection attempts, not test.
    best=max(attempts,key=lambda a:(
        a["train_metrics"]["sum_realized_utility"]+
        a["dev_metrics"]["sum_realized_utility"]
        -0.4*(a["train_metrics"]["negative_utility_cases"]+
              a["dev_metrics"]["negative_utility_cases"]),
        a["dev_metrics"]["sum_realized_utility"],
        -a["dev_metrics"]["simulated_user_questions"],
        -a["dev_metrics"]["sum_internal_actions"],
        -a["params"]["information_weight"],
        a["program_receipt_sha256"],
    ))
    result={
        "schema":SCHEMA,
        "status":"AUTHOR_SYNTHETIC_OPTION_VALUE_POLICY_FROZEN",
        "policy_params":best["params"],
        "source_ring012_lattice_policy_sha256":prior12["receipt_sha256"],
        "source_ring011_binder_sha256":sources.program_sha256,
        "source_train_source_sha256":value.digest([
            x["public"]["id"] for x in train]),
        "source_dev_source_sha256":value.digest([
            x["public"]["id"] for x in dev]),
        "source_train_cases":len(train),
        "source_dev_cases":len(dev),
        "candidate_policies_executed":len(attempts),
        "train_selection_metrics":best["train_metrics"],
        "dev_selection_metrics":best["dev_metrics"],
        "selection_trials":attempts,
        "future_unknown_test_module_imported_during_selection":False,
        "heldout_outcomes_influenced_action_valuation":False,
        "all_reward_priors_and_payoffs_are_author_assumptions":True,
        "decisions_do_not_follow_from_linguistic_truth":True,
        "only_internal_simulated_experimentation_autonomous":True,
        "automatic_unauthorized_effects":0,
        "new_real_world_agent_authority":"NONE",
    }
    result["receipt_sha256"]=value.digest(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    frozen=search()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(frozen,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "status":frozen["status"],
        "selected":frozen["policy_params"],
        "candidate_policies":frozen["candidate_policies_executed"],
        "dev_selection":frozen["dev_selection_metrics"],
        "source_policy":frozen["source_ring012_lattice_policy_sha256"],
        "receipt_sha256":frozen["receipt_sha256"],
    },sort_keys=True))


if __name__=="__main__":
    main()
