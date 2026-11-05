"""MOTIF-027F: controlled three-specialist T5 'thinking' experiment.

Three specialized READ-ONLY encoder roles share ONE real pinned FLAN-T5-small
checkpoint. Their votes are correlated; consensus is not independent truth.
All methods receive the same notes. The native relevance witness is applied
identically BEFORE the original 022F Question Machine and original 016 Forest.

The decision rubric is precommitted, including no-model and lexical controls.
Nothing from T5 can invent sources, access personal records, publish claims,
change human permission or bypass a native HOLD.
"""
from __future__ import annotations
from collections import Counter
import json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in ("016","021f","022f","025f","026f","027f"):
    folder=str(ROOT/p)
    if folder not in sys.path:sys.path.append(folder)
from frozen_cases import CASES,digest
from chorus import LocalFlanT5Small
from native_careers import native_rule,NATIVE_JOB
from semantic_router import CachedT5GateClassifier,ClassicalGateClassifier,operator_projection
from nodes import ThreeSpecialistEncoder,combine_opinions
from pipeline import relevance_first_relay,source_only
from relevance import anchored_native_guess

METHODS=(
    "NO_MODEL_NATIVE",
    "SOURCE_ANCHOR_ONLY",
    "CLASSICAL_TFIDF_ANCHORED",
    "SINGLE_T5_ANCHORED",
    "THREE_T5_2_OF_3",
    "THREE_T5_3_OF_3",
)

def choose_deployment_and_new_question(result:dict)->dict:
    """Asked after the prospective score; no model gets to hire itself.

    Paired differences are synthetic and deliberately too small to provide
    transfer guarantees. Use actual model time and explicit no-model.
    """
    scored=result["scores"]
    strongest=max(
        ("NO_MODEL_NATIVE","SOURCE_ANCHOR_ONLY","CLASSICAL_TFIDF_ANCHORED"),
        key=lambda m:(scored[m]["toy_utility_before_compute"],-scored[m]["wrong_held_offers"]),
    )
    model_names=("SINGLE_T5_ANCHORED","THREE_T5_2_OF_3","THREE_T5_3_OF_3")
    best_t5=max(model_names,key=lambda m:scored[m]["toy_utility_after_compute"])
    increment=scored[best_t5]["toy_utility_after_compute"]-scored[strongest]["toy_utility_before_compute"]
    # Two or more source-unrelated review offers in only 50 synthetic cases
    # is an explicit stop; neither a quorum nor source similarity is a witness.
    violations=scored[best_t5]["wrong_held_offers"]
    if increment>0 and violations==0:
        provisional="SHADOW_RESEARCH_CANDIDATE_"+best_t5
    else:
        provisional="NO_T5"
    rows=result["cases"]
    false=[
        r["id"] for r in rows
        if r["methods"]["THREE_T5_2_OF_3"]["held_review_question"]
        and r["methods"]["THREE_T5_2_OF_3"]["chosen_gate"]!=r["gold"]
    ]
    missed=[
        r["id"] for r in rows
        if r["gold"]!="NONE" and
        not r["methods"]["THREE_T5_2_OF_3"]["held_review_question"]
    ]
    return {
        "question":"Can three differently specialized tiny T5 encoder nodes improve MOTIF's thinking compared with one node, no model, and strong classical relevance checks?",
        "same_checkpoint_three_independent_witnesses":False,
        "roles":(
            "SCOUT nearest known unresolved gate",
            "SKEPTIC task-framed 3-neighbor relevance/none contrast",
            "CARTRIDGE_FINDER registered-question exemplars",
        ),
        "comparison_best_non_llm":strongest,
        "best_t5_policy_by_predeclared_toy_utility":best_t5,
        "toy_utility_gain_over_best_classical":round(increment,5),
        "misleading_held_review_offers":violations,
        "provisional_research_appointment":provisional,
        "automated_system_assignment":"NO_T5",
        "real_world_authority":"NONE",
        "external_actions":0,
        "review_false_cases":false,
        "unresolved_review_cases":missed,
        "proposed_next_falsification_question":(
            "Do independent, source-specific relevance witnesses and a "
            "genuinely held-out multi-domain corpus distinguish complementary "
            "semantic clues from correlated three-head agreement well enough "
            "to justify three encoder calls instead of one or zero?"
        ),
        "compute_delay_and_human_welfare":"NOT_CALIBRATED",
        "native_question_and_source_gate_not_overridden":True,
    }


def evaluate():
    import torch
    torch.set_num_threads(2)
    began=time.monotonic()
    ckpt=os.environ.get("MOTIF_FLAN_MODEL_DIR","google/flan-t5-small")
    model=LocalFlanT5Small(ckpt)
    t=time.monotonic()
    model._prepare()
    loaded=round(time.monotonic()-t,4)
    single=CachedT5GateClassifier(model)
    triple=ThreeSpecialistEncoder(model)
    classical=ClassicalGateClassifier()
    data=[]
    for i,case in enumerate(CASES):
        operator_projection(case.note)
        native=native_rule(NATIVE_JOB,case.note)
        if native=="NONE":
            one=single.classify(case.note)[0]
            three=triple.opinions(case.note)
            two=combine_opinions(three,quorum=2)
            all3=combine_opinions(three,quorum=3)
            classical_suggestion=classical.classify(case.note)[0]
            decisions={
                "NO_MODEL_NATIVE":None,
                "SOURCE_ANCHOR_ONLY":source_only(case.note),
                "CLASSICAL_TFIDF_ANCHORED":classical_suggestion,
                "SINGLE_T5_ANCHORED":one,
                "THREE_T5_2_OF_3":two["candidate"],
                "THREE_T5_3_OF_3":all3["candidate"],
            }
        else:
            three=()
            two={"status":"NATIVE_BYPASS","candidate":native}
            all3=two
            decisions={
                "NO_MODEL_NATIVE":native,
                "SOURCE_ANCHOR_ONLY":source_only(case.note),
                "CLASSICAL_TFIDF_ANCHORED":native,
                "SINGLE_T5_ANCHORED":native,
                "THREE_T5_2_OF_3":native,
                "THREE_T5_3_OF_3":native,
            }
        world=("00","01","10","11")[i%4]
        results={}
        for name,candidate in decisions.items():
            x=relevance_first_relay(
                case.note,candidate,mode=name,hidden_world=world
            )
            offered=x["source_quote"] is not None
            passnative=x["status"]=="ELIGIBLE_SYNTHETIC_REPLAN_ONLY"
            results[name]={
                "chosen_gate":candidate,
                "held_review_question":offered,
                "grounding_status":x["status"],
                "literal_grounding_span":x["source_quote"],
                "reviewed_synthetic_question":passnative,
                "synthetic_correct_question":passnative and case.gold=="FOOD",
                "synthetic_irrelevant_question":passnative and case.gold!="FOOD",
                "real_execution":False,
            }
            assert x["field_actions"]==0
            assert x["permission_granted"] is False
            assert x["model_outcome_promoted_to_fact"] is False
        data.append({
            "id":case.id,"synthetic_note":case.note,"gold":case.gold,
            "native_initial_gate":native,
            "source_anchored_gates":anchored_native_guess(case.note),
            "specialist_nodes":tuple({
                "role":n.role,"label":n.label,"similarity":n.similarity,
                "seconds":n.elapsed_seconds
            } for n in three),
            "quorum_two":two,
            "quorum_three":all3,
            "methods":results,
            "model_never_received_gold":True,
            "synthetic_only":True,
        })
    scores={}
    for method in METHODS:
        n=Counter()
        for row in data:
            x=row["methods"][method]
            gold=row["gold"]
            gate=x["chosen_gate"]
            offered=x["held_review_question"]
            n["correct_raw_gate"]+=(gate==gold or (gate is None and gold=="NONE"))
            n["correct_held_offers"]+=(offered and gate==gold)
            n["wrong_held_offers"]+=(offered and gate!=gold)
            n["missed_real_gates"]+=(gold!="NONE" and (not offered or gate!=gold))
            n["false_held_gate_on_none"]+=(gold=="NONE" and offered)
            n["native_accepted_synthetic_question"]+=x["reviewed_synthetic_question"]
            n["native_accepted_relevant_synthetic_question"]+=x["synthetic_correct_question"]
            n["native_accepted_irrelevant_synthetic_question"]+=x["synthetic_irrelevant_question"]
        for field in ("correct_raw_gate","correct_held_offers","wrong_held_offers",
                      "missed_real_gates","false_held_gate_on_none",
                      "native_accepted_synthetic_question",
                      "native_accepted_relevant_synthetic_question",
                      "native_accepted_irrelevant_synthetic_question"):
            n.setdefault(field,0)
        # An openly arbitrary research score, NOT social welfare:
        # +2 for correct note-grounded human review suggestion,
        # -4 for irrelevant offer, -1 for each missed actual gate.
        utility=2*n["correct_held_offers"] - 4*n["wrong_held_offers"] - n["missed_real_gates"]
        if method.startswith("THREE_T5"):
            seconds=triple.inference_seconds
        elif method=="SINGLE_T5_ANCHORED":
            seconds=single.total_query_seconds+single.build_seconds
        else:
            seconds=0.
        n["toy_utility_before_compute"]=utility
        n["measured_model_seconds"]=round(seconds,5)
        n["toy_utility_after_compute"]=round(utility - .1*seconds,5)
        n["cases"]=len(CASES)
        scores[method]=dict(n)
    result={
        "schema":"motif027f.three-specialized-correlated-encoders/v0",
        "model":"google/flan-t5-small",
        "model_source_revision":os.environ.get("MOTIF_FLAN_REVISION","UNPINNED_LOCAL_CACHE"),
        "actual_model_weights_loaded":model._model is not None,
        "actual_encoder_model_calls":single.total_queries+triple.calls,
        "actual_decoder_calls":0,
        "one_loaded_model_three_different_roles":True,
        "three_roles_are_independent_models":False,
        "source_relevance_guard":"LITERAL_NOTE_SPAN_AND_DECLARED_LEXICON_NOT_FIELD_AUTHENTICATION",
        "precommitted_synthetic_cases_digest":digest(),
        "sample_size":len(CASES),
        "model_load_seconds":loaded,
        "single_encoder_seconds":round(single.build_seconds+single.total_query_seconds,5),
        "triple_encoder_seconds":round(triple.inference_seconds+
            triple.scout.build_seconds+triple.skeptic_build_seconds+
            triple.finder_build_seconds,5),
        "total_wall_seconds":round(time.monotonic()-began,4),
        "scores":scores,
        "cases":data,
        "external_actions":0,
        "real_source_authentication":False,
        "human_permission_inferred":False,
        "native_planner_overwritten":False,
        "comparison_inputs_all_author_written_synthetic":True,
        "classical_relevance_lexicon_was_frozen_before_model_run":True,
    }
    result["motif_asks_again_about_three_t5_nodes"]=choose_deployment_and_new_question(result)
    return result

if __name__=="__main__":
    print(json.dumps(evaluate(),sort_keys=True,indent=2))
