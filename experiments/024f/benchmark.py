"""024F: actual 77M model vs SAME native-only and classical baselines.

Two real T5 ranked decisions per invented test case (original vs reversed
candidate display). The source is independently calibrated before model
ranking. Hidden post-review drift and all outcome scoring remain in a separate
synthetic oracle. No model is trained, and no human or field tool is called.

This is SHADOW ranking: a T5 suggestion NEVER changes the native plan,
permissions, or evidence; the alternative is run inside separate simulation.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
import random
import time

from heldout import CASES
from native import native_shortlist, independent_run
from rerank import lexical_rule, rerank_with_real_model


def evaluate():
    import torch
    from chorus import LocalFlanT5Small
    torch.set_num_threads(2)
    start=time.monotonic()
    model=LocalFlanT5Small()
    load_start=time.monotonic()
    model._prepare()
    model_load=round(time.monotonic()-load_start,4)
    rng=random.Random(20261105)
    records=[]
    for index, case in enumerate(CASES):
        shortlist=native_shortlist(case)
        if len(shortlist.eligible_ids)!=2:
            raise RuntimeError("HOLD_NATIVE_SHORTLIST_DID_NOT_GENERATE_TWO_ADMISSIBLE_TESTS:"+case.id)
        # Both source reviews and 016 planner agree they offer identical
        # expected benefit. No hidden drift labels passed to these methods.
        model_ranking=rerank_with_real_model(
            model,case,shortlist,reverse=bool(index%2))
        reversed_ranking=rerank_with_real_model(
            model,case,shortlist,reverse=not bool(index%2))
        picks={
            "NATIVE_ONLY":shortlist.native_choice,
            "CLASSICAL_LEXICAL_SAME_NOTES":lexical_rule(case),
            "RANDOM_SEEDED":rng.choice(shortlist.eligible_ids),
            "REAL_T5_SHADOW":model_ranking["selected"],
            "REAL_T5_REVERSED_DISPLAY_ORDER":reversed_ranking["selected"],
            # This oracle is NEVER a practical policy; only a known ceiling.
            "HINDSIGHT_ORACLE_CEILING":next(
                (x for x in shortlist.eligible_ids
                 if x!=case.drifted_source),shortlist.native_choice),
        }
        observed={
            method:independent_run(case,choice)
            for method,choice in picks.items()
        }
        records.append({
            "case":case.id,
            "regime":case.regime,
            "native_proposed_question_shortlist":asdict(shortlist),
            "source_descriptions_shown_to_all_language_aware_methods":{
                "PROBE_ALPHA":case.alpha_note,
                "PROBE_BETA":case.beta_note,
            },
            "submitted_source_notes_are_unverified":True,
            "advisory_real_t5":model_ranking,
            "advisory_real_t5_swapped_order":reversed_ranking,
            "chosen_by_method":picks,
            "independent_synthetic_run":observed,
            "no_external_actions":True,
        })
    names=list(records[0]["chosen_by_method"])
    comparisons={}
    for method in names:
        correct=sum(x["independent_synthetic_run"][method]["correct"]
                    for x in records)
        shifted=[x for x in records if x["regime"]!="NO_DRIFT"]
        correct_shift=sum(x["independent_synthetic_run"][method]["correct"]
                          for x in shifted)
        comparisons[method]={
            "correct_heldout_synthetic_predictions":correct,
            "total_cases":len(records),
            "accuracy":round(correct/len(records),4),
            "correct_on_shifting_sources":correct_shift,
            "shifting_source_cases":len(shifted),
        }
    flip_count=sum(
        x["advisory_real_t5"]["selected"] !=
        x["advisory_real_t5_swapped_order"]["selected"]
        for x in records
    )
    total_model_seconds=round(
        sum(
            x["advisory_real_t5"]["latency_seconds"] +
            x["advisory_real_t5_swapped_order"]["latency_seconds"]
            for x in records
        ),4)
    return {
        "schema":"motif024f.native-vs-small-model-shadow-ranking/v0",
        "actual_model_weights_loaded":model._model is not None,
        "model_id":"google/flan-t5-small",
        "actual_model_token_logits_used":True,
        "model_never_granted_field_authority":True,
        "model_was_only_offered_native_eligible_instruments":True,
        "all_outcomes_independent_synthetic_runs":True,
        "model_load_seconds":model_load,
        "real_model_inference_seconds_total_40_calls":total_model_seconds,
        "total_wall_seconds":round(time.monotonic()-start,4),
        "number_of_heldout_cases":len(records),
        "number_of_actual_model_ranking_calls":2*len(records),
        "same_question_selected_after_display_order_reversed":len(records)-flip_count,
        "different_question_selected_after_display_order_reversed":flip_count,
        "comparison":comparisons,
        "cases":records,
        "limitations":{
            "sample_is_hand_constructed_and_small":True,
            "notes_are_synthetic_unverified_risk_cues":True,
            "model_received_facts_cues_equal_to_classical_lexical_control":True,
            "all_two_question_shortlists_came_from_actual_016_022f_logic":True,
            "source_candidates_supplied_from_bounded_operator_catalog":True,
            "model_invented_no_new_external_sensors":True,
            "native_source_evidence_has_no_verified_post_review_reliability":True,
            "no_field_permission_or_event_success_claimed":True,
            "real_cpu_latency_is_not_user_laptop_benchmark":True,
            "future_welfare_and_delay_not_quantified":True,
            "no_model_training_or_fine_tuning":True,
        },
    }


if __name__=="__main__":
    print(json.dumps(evaluate(),indent=2,sort_keys=True))
