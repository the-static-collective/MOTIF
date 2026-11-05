"""MOTIF-012 evaluator — break correlation before claiming consequence.

ONLY this evaluator imports oracle.py. cartographer.py has no access to
hidden world families, simulator mechanisms, independent local review
outcomes, or held-out causal test outcomes.

30+ synthetic worlds, same source/validation evidence, 2 query budget and
independent review/test suite for each strategy. Competing classical fixed
diagnostic and random baselines receive the same inquiry budget.

Results distinguish provisional *model identity* from an independently
accepted synthetic predictive cartridge. The method is classical
intervention/version-space elimination, not new causal mathematics.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from random import Random
from statistics import mean
import json

from oracle import (FAMILIES,SEEDS,PAIRS,new_world,natural,
                    intervene,independent_suite,declared_policy)
from cartographer import (HOLD,opening_model_space,choose,revise,
                          independent_review,LocalCausalBay,
                          retained_contradictions,_residual,feature_present)

VERSION="cartographer-interventions-v1"
METHODS=("cartographer","fixed_diagnostic","random")
BUDGET=2


def random_order(family,seed):
    rng=Random(int.from_bytes(sha256(
        f"motif012:random:{family}:{seed}".encode()).digest()[:8],"big"))
    return tuple(rng.sample(PAIRS,BUDGET))


def evaluate(family:str,seed:int,method:str) -> dict:
    if method not in METHODS:
        raise ValueError("Unknown inquiry baseline")
    spec=new_world(family,seed)
    training=natural(spec,"train")
    validation=natural(spec,"validation")
    state=opening_model_space(training,validation,spec.controls)
    assert len(state.models)==4
    # Original graph evidence is immutable. The simulator creates new worlds.
    original=tuple(x.before for x in training)
    agenda={
        "fixed_diagnostic":((False,True),(True,False)),
        "random":random_order(family,seed),
    }.get(method)
    budget=BUDGET
    tested=[]
    events=[]
    for step in range(BUDGET):
        if method=="cartographer":
            proposal=choose(state,remaining_budget=budget,used=tested)
            if proposal.status!="PROPOSE_SYNTHETIC_ONLY":
                events.append({"step":step+1,"status":proposal.status,
                               "simulator_called":False})
                break
            setting=proposal.settings
            gain=proposal.expected_gain_bits
            predicted=list(proposal.predictions)
        else:
            setting=agenda[step]
            gain=None
            predicted=None
        # Fresh intervention is created ONLY after the query is finalized.
        observed=intervene(spec,*setting,sequence=1000+step,
                           context=False)
        before=len(state.models)
        state=revise(state,observed,spec.controls)
        budget-=1
        tested.append(setting)
        events.append({
            "step":step+1,
            "settings":list(setting),
            "model_count_before":before,
            "model_count_after":len(state.models),
            "predicted_residual_votes_before_observation":predicted,
            "hypothesized_information_gain_bits":gain,
            "independently_observed_residual":_residual(observed,spec.controls),
            "intervention_source":observed.provenance,
            "simulator_called":True,
            "real_world_action":False,
        })

    # An independent local reviewer tests candidate on a factorial, freshly
    # generated group with the candidate and proxy decoupled from context.
    local=independent_suite(spec,"local_review")
    review=independent_review(state,local,spec.controls)
    bay=LocalCausalBay()
    receipt=None
    ticket=None
    held_before_review=None
    if len(state.models)==1:
        ticket=bay.offer(state.models[0],review)
        held_before_review=ticket not in bay.admitted
        if review.status=="ELIGIBLE_PREDICT_ONLY_PENDING_LOCAL_DECISION":
            # This is an EXPLICIT evaluator-fixture decision. It represents
            # no verified person or real-world authorization.
            receipt=bay.decide(ticket,"ADMIT_PREDICT_ONLY",
                               "LOCAL_SYNTHETIC_STEWARD")
    admitted=ticket in bay.admitted if ticket is not None else False

    # A distinct independently generated held-out evaluator-only suite is
    # NEVER inspected during model selection or local review.
    tests=independent_suite(spec,"test")
    if admitted:
        predicts=[bay.predict(ticket,x,spec.controls) for x in tests]
    else:
        predicts=[None for _ in tests]
    actual=[_residual(x,spec.controls) for x in tests]
    covered=sum(x is not None for x in predicts)
    wrong=sum(x is not None and x!=y for x,y in zip(predicts,actual))

    # Naive observational-only model: choose the first candidate as a cause,
    # never interrogate the proxy, and always predict. This is an intentionally
    # WEAK comparator, not a noise-aware Bayesian or modern causal learner.
    naive=opening_model_space(training,validation,spec.controls).models[0]
    naive_errors=sum(naive.predict(x,spec.controls)!=y
                     for x,y in zip(tests,actual))
    return {
        "family":family,"seed":seed,"method":method,
        "natural_train":len(training),"natural_validation":len(validation),
        "starting_hypotheses":4,"max_inquiry_budget":BUDGET,
        "inquiries_used":len(tested),
        "independent_local_review_examples":len(local),
        "independent_heldout_examples":len(tests),
        "provisional_hypotheses_remaining":len(state.models),
        "provisional_model_label":
            state.models[0].label if len(state.models)==1 else None,
        "provisional_model_id":
            state.models[0].tree.id if len(state.models)==1 else None,
        "query_history":events,
        "model_status_after_inquiries":state.status,
        "independent_review_status":review.status,
        "local_review_rejected_observations":len(review.contradictions),
        "local_review_scars":[
            {"settings":list(x.setting),"predicted":list(x.predicted),
             "observed":x.observed,"source":x.source}
            for x in review.contradictions],
        "held_before_explicit_fixture_decision":held_before_review,
        "explicit_local_fixture_decision":receipt,
        "independently_admitted":admitted,
        "heldout_prediction_coverage":round(covered/len(tests),4),
        "wrong_when_covered":wrong,
        "naive_observational_wrong":naive_errors,
        "natural_world_unchanged":
            original==tuple(x.before for x in training),
        "external_actions":0,
    }


def safe_scope_proof():
    spec=new_world("cause_c",SEEDS[0])
    state=opening_model_space(natural(spec,"train"),
                              natural(spec,"validation"),spec.controls)
    policy=declared_policy()
    refused=choose(state,allowed=policy["allowed"],costs=policy["costs"],
                   remaining_budget=policy["budget"])
    unaffordable=choose(state,allowed=PAIRS,
                        costs={pair:4 for pair in PAIRS},remaining_budget=1)
    available=choose(state,allowed=PAIRS,
                     costs={pair:(1 if pair==(False,True) else 2)
                            for pair in PAIRS},remaining_budget=2)
    return {
        "unsafe_request":refused.status,
        "unaffordable_request":unaffordable.status,
        "permitted_request":available.status,
        "permitted_settings":list(available.settings)
                             if available.settings else None,
        "permitted_cost":available.cost,
        "simulator_operations_dispatched":0,
        "real_world_authority":False,
    }


def aggregate(rows):
    grouped={}
    for method in METHODS:
        cases=[x for x in rows if x["method"]==method]
        grouped[method]={
            "worlds":len(cases),
            "provisional_unique_models":sum(
                x["provisional_hypotheses_remaining"]==1 for x in cases),
            "independently_admitted_worlds":sum(
                x["independently_admitted"] for x in cases),
            "total_review_falsification_scars":sum(
                x["local_review_rejected_observations"] for x in cases),
            "mean_heldout_coverage":round(mean(
                x["heldout_prediction_coverage"] for x in cases),4),
            "heldout_wrong_where_covered":sum(
                x["wrong_when_covered"] for x in cases),
            "query_budget_respected":all(
                x["inquiries_used"]<=BUDGET for x in cases),
            "mean_naive_observational_error_count":round(mean(
                x["naive_observational_wrong"] for x in cases),4),
        }
    families={}
    for family in FAMILIES:
        local=[x for x in rows if x["family"]==family and
               x["method"]=="cartographer"]
        families[family]={
            "worlds":len(local),
            "admitted":sum(x["independently_admitted"] for x in local),
            "review_statuses":dict(sorted(Counter(
                x["independent_review_status"] for x in local).items())),
            "total_heldout_wrong_where_covered":sum(
                x["wrong_when_covered"] for x in local)
        }
    return {
        "version":VERSION,
        "scope":"INDEPENDENT_SYNTHETIC_CAUSAL_COUNTERFACTUALS",
        "families":list(FAMILIES),
        "seeds":list(SEEDS),
        "worlds_per_method":len(FAMILIES)*len(SEEDS),
        "natural_train_each":16,
        "natural_validation_each":16,
        "queries_budget_each":BUDGET,
        "independent_local_review_each":16,
        "independent_heldout_each":16,
        "fresh_environment_for_each_query":True,
        "learned_causal_hypothesis_family_is_handcrafted":True,
        "known_two_port_baseline_is_declared_prior":True,
        "noise_is_procedural_not_calibrated":True,
        "true_source_mechanism_visible_to_cartographer":False,
        "heldout_oracle_labels_visible_during_selection":False,
        "methods":grouped,
        "by_family":families,
        "real_world_actions":0,
    }


def benchmark():
    rows=[evaluate(family,seed,method)
          for family in FAMILIES for seed in SEEDS for method in METHODS]
    return {
        "experiment":"MOTIF-012",
        "summary":aggregate(rows),
        "safety_scope":safe_scope_proof(),
        "worlds":rows,
    }


def demo():
    sample=[]
    for family in FAMILIES:
        row=evaluate(family,SEEDS[0],"cartographer")
        sample.append({
            "family":family,
            "observational_candidate_count":row["starting_hypotheses"],
            "interventions":row["query_history"],
            "provisional":row["provisional_model_label"],
            "review":row["independent_review_status"],
            "contradictions":row["local_review_rejected_observations"],
            "heldout_coverage":row["heldout_prediction_coverage"],
            "heldout_wrong":row["wrong_when_covered"],
        })
    return {
        "experiment":"MOTIF-012",
        "scope":"PURELY_SYNTHETIC",
        "cases":sample,
        "safety":safe_scope_proof(),
        "external_actions":0
    }


if __name__=="__main__":
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
