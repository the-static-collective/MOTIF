"""RING-013: executable decision value of asking, inspecting, or smashing ON.

This is a model-based bounded planner operating over a small authored world,
NOT an unreviewed real-world agent. "SMASH" means executing only a local
simulator of a reversible dry-run. External effects are categorically denied.

A candidate next move is evaluated for:
  * immediate expected gain minus time / attention costs;
  * expected future action value after a new observation;
  * source-conditional entropy reduction (bounded curiosity value);
  * new affordance options discovered if a reversible trial succeeds;
  * downside risk when a model is mistaken;
  * budget and time limits / opportunity cost.

No forced resolution of uncertainty: "OTHER" always has nonzero prior
mass, and candidate methods do not authenticate the source-language claims.
"""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
import itertools
import json
import math

import scenario

SCHEMA="motif.ring013.value-of-next-reversible-move.v1"
POLICY_SCHEMA="motif.ring013.frozen-next-move-research-policy.v1"
EPS=1e-8
ALLOWED=("INSPECT","SMASH_A","SMASH_B","ASK_USER")
FORBIDDEN="EXTERNAL_COMMIT"


def digest(x):
    return scenario.digest(x)


def entropy(belief):
    return -sum(v*math.log(v,2) for v in belief.values() if v>0)


def normalize(b):
    z=sum(b.values())
    if z<=0:
        raise ValueError("No source-supported viability probability")
    return {w:b[w]/z for w in scenario.WORLDS}


def future_signal_probs(action,belief):
    outcomes=set(y for w in scenario.WORLDS
                 for y in action["signal_distribution"][w])
    return {signal:sum(belief[w]*
                       action["signal_distribution"][w].get(signal,0.0)
                       for w in scenario.WORLDS)
            for signal in sorted(outcomes)}


def update(belief,action,signal):
    p=future_signal_probs(action,belief).get(signal,0.0)
    if p<=0:
        raise ValueError("Observed signal was not supported by model")
    return normalize({
        w:belief[w]*action["signal_distribution"][w].get(signal,0.0)
        for w in scenario.WORLDS})


def policy_parameters(params):
    if (not isinstance(params,dict) or set(params)!={
            "information_weight","affordance_weight","risk_weight",
            "ambiguity_sensitivity"}
            or params["information_weight"] not in (0.0,0.7)
            or params["affordance_weight"] not in (0.0,0.5,1.0)
            or params["risk_weight"] not in (0.0,0.7)
            or params["ambiguity_sensitivity"] not in (0.0,0.4)):
        raise ValueError("Unreviewed value model / authority")
    return params


def epistemic_belief(public,lattice_result,params):
    """Public prior + source uncertainty, WITHOUT claiming language truth."""
    policy_parameters(params)
    scenario.verify_public(public)
    counts=len(lattice_result["supported_worlds"])
    unknown=lattice_result["status"]=="UNRESOLVED_SOURCE"
    # THIS IS AN AUTHOR-DESIGNED PRIOR-WIDENING HEURISTIC, not a learned
    # causal mapping from semantics to task viability. It is calibrated
    # only for synthetic examples by comparing candidate decision policies.
    mix=min(0.75,params["ambiguity_sensitivity"]*
            min(1.0,counts/24.0)+
            (0.30 if unknown else 0.0))
    prior=public["proposed_prior"]
    result={
        "USEFUL":prior["USEFUL"]*(1-mix),
        "UNHELPFUL":prior["UNHELPFUL"]*(1-mix),
        "SURPRISE":prior["SURPRISE"]*(1-mix)+mix,
    }
    return normalize(result)


def immediate(action,belief,params):
    raw=sum(belief[w]*
            (action["rewards"][w]+params["affordance_weight"]*
             action["affordances"][w])
            for w in scenario.WORLDS)
    downside=sum(belief[w]*max(0.0,-action["rewards"][w])
                 for w in scenario.WORLDS)
    return (raw-action["cost"]-action["attention_cost"]
            -params["risk_weight"]*downside)


def information_gain(action,belief):
    prior=entropy(belief)
    after=sum(p*entropy(update(belief,action,signal))
              for signal,p in future_signal_probs(action,belief).items()
              if p>EPS)
    return max(0.0,prior-after)


def choose(public,belief,params,used=(),budget=None,horizon=None,
           *,strategy="FRONTIER"):
    """Finite Bellman search over *safe* hypothetical actions only.

    Includes STOP at zero utility; never makes progress just to look busy.
    Returns the recommended local simulation action and its option-value
    decomposition. 'FRONTIER' uses up to the available three-step horizon.
    """
    scenario.verify_public(public)
    policy_parameters(params)
    if strategy not in ("FRONTIER","GREEDY","ALWAYS_STOP",
                        "ALWAYS_SMASH","ASK_FIRST"):
        raise ValueError("Unreviewed decision policy")
    if budget is None:budget=public["budget_units"]
    if horizon is None:horizon=public["horizon"]
    used=tuple(used)
    if horizon<=0 or budget<=0 or strategy=="ALWAYS_STOP":
        return {"action":"STOP","expected_net":0.0,"ranked":[]}
    horizon=1 if strategy=="GREEDY" else horizon
    if strategy=="ALWAYS_SMASH":
        option=["SMASH_A"] if "SMASH_A" not in used else []
    elif strategy=="ASK_FIRST" and "ASK_USER" not in used:
        option=["ASK_USER"]
    else:
        option=list(ALLOWED)
    ranks=[]
    for name in option:
        if name in used:continue
        action=public["actions"][name]
        if (action["permission"] not in (
                "INTERNAL_READONLY","INTERNAL_REVERSIBLE",
                "HUMAN_ATTENTION_SIMULATED_ONLY")
                or action["budget_units"]>budget):
            continue
        reward=immediate(action,belief,params)
        info=information_gain(action,belief)
        future=0.0
        if horizon>1 and strategy not in ("ALWAYS_SMASH",):
            # Real option value is explicitly conditional on what the
            # simulated probe would observe next, not a fixed novelty bonus.
            for signal,p in future_signal_probs(action,belief).items():
                if p<=EPS:continue
                after=update(belief,action,signal)
                later=choose(public,after,params,
                             used=used+(name,),
                             budget=budget-action["budget_units"],
                             horizon=horizon-1,
                             strategy=("FRONTIER" if strategy=="ASK_FIRST"
                                       else strategy))
                future+=p*later["expected_net"]
        intrinsic=params["information_weight"]*info
        ranks.append({
            "action":name,
            "expected_immediate":round(reward,6),
            "expected_information_gain_bits":round(info,6),
            "intrinsic_interest_value":round(intrinsic,6),
            "expected_future_option_value":round(future,6),
            "total_expected_value":round(reward+intrinsic+future,6),
            "permission":action["permission"],
            "source_world_model_is_authored_not_real":True,
        })
    ranks.sort(key=lambda x:(-x["total_expected_value"],x["action"]))
    if not ranks or ranks[0]["total_expected_value"]<=EPS:
        return {"action":"STOP","expected_net":0.0,
                "ranked":ranks}
    return {"action":ranks[0]["action"],
            "expected_net":ranks[0]["total_expected_value"],
            "ranked":ranks}


def public_decision(public,lattice_result,params,*,strategy="FRONTIER"):
    belief=epistemic_belief(public,lattice_result,params)
    first=choose(public,belief,params,strategy=strategy)
    return {
        "schema":SCHEMA,
        "input_source_sha256":digest(public),
        "source_perspective_lattice_sha256":digest(lattice_result),
        "source_perspective_count":len(lattice_result["supported_worlds"]),
        "unmodeled_readings_still_possible":lattice_result[
            "other_unmodeled_readings_remain_possible"],
        "belief_is_estimate_not_event_truth":belief,
        "conditional_invariants":lattice_result.get(
            "conditional_invariants_within_modeled_worlds",{}),
        "optional_ambiguity_discriminator":lattice_result.get(
            "optional_discriminator_question_kind"),
        "best_first_action":first["action"],
        "ranked_next_moves":first["ranked"],
        "never_act_on_semantics_as_external_authority":True,
        "if_interest_is_positive_may_run_internal_simulation":True,
        "no_real_user_question_asked":True,
        "externally_effectful_action_blocked":True,
        "external_action_executed":False,
        "authority":"NONE",
    }


def deterministic_signal(hidden,action_name,step,distribution):
    """Only the simulator, NEVER the agent, receives a hidden viability."""
    w=hidden["true_world"]
    key=f"{hidden['measurement_seed']}:{action_name}:{step}:{w}"
    fraction=int(sha256(key.encode()).hexdigest()[:14],16)/float(16**14)
    running=0.0
    for signal,p in sorted(distribution[w].items()):
        running+=p
        if fraction<running: return signal
    return sorted(distribution[w])[-1]


def simulate(public,hidden,lattice_result,params,*,strategy="FRONTIER"):
    """Real code execution inside TEST SIMULATION; no external effect."""
    scenario.verify_public(public)
    if hidden.get("true_world") not in scenario.WORLDS:
        raise ValueError("Hidden synthetic viability unsupported")
    belief=epistemic_belief(public,lattice_result,params)
    trace=[]
    budget=public["budget_units"]
    used=[]
    total_realized=0.0
    total_options=0
    start_belief=dict(belief)
    for step in range(public["horizon"]):
        choice=choose(public,belief,params,used=used,budget=budget,
                      horizon=public["horizon"]-step,
                      strategy=strategy)
        name=choice["action"]
        if name=="STOP":break
        if name=="EXTERNAL_COMMIT" or name not in ALLOWED:
            raise ValueError("External effect prohibited regardless of expected gain")
        action=public["actions"][name]
        if action["permission"] not in (
                "INTERNAL_READONLY","INTERNAL_REVERSIBLE",
                "HUMAN_ATTENTION_SIMULATED_ONLY"):
            raise ValueError("Effectful action cannot pass permission wall")
        signal=deterministic_signal(hidden,name,step,
                                    action["signal_distribution"])
        realized=(action["rewards"][hidden["true_world"]]
                  +params["affordance_weight"]*action[
                      "affordances"][hidden["true_world"]]
                  -action["cost"]-action["attention_cost"])
        next_belief=update(belief,action,signal)
        trace.append({
            "action":name,
            "permission":action["permission"],
            "internal_simulator_executed":True,
            "external_effect_executed":False,
            "observed_synthetic_signal":signal,
            "realized_utility":round(realized,6),
            "realized_affordance_count":action[
                "affordances"][hidden["true_world"]],
            "belief_before":{k:round(v,7) for k,v in belief.items()},
            "belief_after":{k:round(v,7) for k,v in next_belief.items()},
            "entropy_reduction_bits":round(
                entropy(belief)-entropy(next_belief),6),
            "expected_action_value_before_observation":choice["expected_net"],
            "hidden_world_never_supplied_to_planner":True,
        })
        total_realized+=realized
        total_options+=action["affordances"][hidden["true_world"]]
        budget-=action["budget_units"]
        used.append(name)
        belief=next_belief
    return {
        "source_case_id":public["id"],
        "strategy":strategy,
        "steps":trace,
        "action_count":len(trace),
        "internal_smash_count":sum(x["action"].startswith("SMASH")
                                   for x in trace),
        "human_interruption_count":0,
        "simulated_user_question_count":sum(
            x["action"]=="ASK_USER" for x in trace),
        "budget_units_remaining":budget,
        "realized_utility":round(total_realized,6),
        "realized_new_affordance_count":total_options,
        "initial_entropy_bits":round(entropy(start_belief),6),
        "final_entropy_bits":round(entropy(belief),6),
        "final_belief":{w:round(belief[w],7) for w in scenario.WORLDS},
        "open_world_surprise_retained":belief["SURPRISE"]>0.0,
        "all_actions_safe_simulated_only":True,
        "no_real_effects":True,
        "authority":"NONE",
    }
