"""MOTIF-012 — an inspectable synthetic causal-map and refusal transcript.

Run:
    cd experiments/012
    python demo.py

The output is a human-readable experimental receipt containing *real 009
tree cartridges* and two independently witnessed synthetic interventions.
A separate latent-confounder case is explicitly refused after local review.
No real-world action or author authentication is possible.
"""
from __future__ import annotations
import json
from oracle import new_world,natural,intervene,independent_suite
from benchmark import safe_scope_proof
from cartographer import (opening_model_space,choose,revise,
                          independent_review,LocalCausalBay,_residual)
from cartridge import export_cartridge


def walk(family,seed=11):
    world=new_world(family,seed)
    train=natural(world,"train")
    val=natural(world,"validation")
    space=opening_model_space(train,val,world.controls)
    initial_cards=[{
        "abstract_hypothesis":model.label,
        "tree":json.loads(export_cartridge(model.tree))
    } for model in space.models]
    trace=[]
    used=[]
    for i in range(2):
        proposed=choose(space,used=used)
        if proposed.status!="PROPOSE_SYNTHETIC_ONLY":
            raise AssertionError("This controlled fixture requires two questions")
        before=len(space.models)
        intervention=intervene(world,*proposed.settings,sequence=1000+i,
                               context=False)
        space=revise(space,intervention,world.controls)
        used.append(proposed.settings)
        trace.append({
            "step":i+1,
            "controlled_candidate_values":list(proposed.settings),
            "expected_information_gain_bits":proposed.expected_gain_bits,
            "votes_before_observation":list(proposed.predictions),
            "independent_synthetic_result":_residual(intervention,world.controls),
            "candidate_count_before":before,
            "candidate_count_after":len(space.models),
            "real_world_authority":False,
        })
    reviewer=independent_review(
        space,independent_suite(world,"local_review"),world.controls)
    final=(json.loads(export_cartridge(space.models[0].tree))
           if len(space.models)==1 else None)
    bay=LocalCausalBay()
    ticket=bay.offer(space.models[0],reviewer) if len(space.models)==1 else None
    held_before_explicit_decision=(ticket not in bay.admitted
                                   if ticket else None)
    decision=(bay.decide(ticket,"ADMIT_PREDICT_ONLY","LOCAL_SYNTHETIC_REVIEWER")
              if ticket and reviewer.status==
              "ELIGIBLE_PREDICT_ONLY_PENDING_LOCAL_DECISION" else None)
    return {
        "source_description":"OPAQUE_TWO_CANDIDATE_OBSERVATIONAL_PROXIES",
        "source_training_observations":len(train),
        "initial_hypotheses":initial_cards,
        "interventions":trace,
        "provisional_cartridge":final,
        "held_before_explicit_local_decision":held_before_explicit_decision,
        "local_fixture_admission":decision,
        "local_review":{
            "status":reviewer.status,
            "separate_intervention_evidence":reviewer.independently_checked,
            "contradiction_count":len(reviewer.contradictions),
            "scars":[{
                "setting":list(s.setting),
                "expected":list(s.predicted),
                "observed":s.observed,
                "source":s.source,
            } for s in reviewer.contradictions],
            "no_real_world_authority":True,
        },
        "graph_source_modified":False,
    }


def demonstrate():
    supported=walk("cause_p")
    latent=walk("latent")
    noisy=walk("noisy_c")
    if (supported["local_review"]["status"]!=
            "ELIGIBLE_PREDICT_ONLY_PENDING_LOCAL_DECISION" or
            supported["local_fixture_admission"] is None):
        raise AssertionError("Synthetic visible cause did not transfer to review")
    for rejected in (latent,noisy):
        if rejected["local_review"]["status"]!="HOLD_INDEPENDENT_FALSIFIER":
            raise AssertionError("Underspecified/noisy cause incorrectly admitted")
    return {
        "experiment":"MOTIF-012",
        "artifact":"CAUSAL_CARTOGRAPHER_SYNTHETIC_CARTRIDGE_TRANSCRIPT",
        "supported_causal_candidate":supported,
        "latent_source_refused":latent,
        "noisy_source_refused":noisy,
        "safety_and_cost":safe_scope_proof(),
        "independently_authenticated_source":False,
        "causal_validity_outside_programmed_simulator":False,
        "real_world_actions":0,
    }


if __name__=="__main__":
    print(json.dumps(demonstrate(),indent=2,sort_keys=True))
