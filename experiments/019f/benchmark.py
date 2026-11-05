"""MOTIF-019F frozen synthetic classical-method and native-organ research receipt."""
from __future__ import annotations

from dataclasses import asdict
import json

from bridge import verify_sources
from classical import develop_methods, find_plan
from engine import fixture_cases, propose_guard, sample_clue
from online import base_problem, run_online, static_fallback, weighted_problem


def benchmark():
    verified = verify_sources()
    cases = fixture_cases()
    clean_question = propose_guard("open_gate", *cases, sample_clue())
    source_hold = propose_guard("open_gate", *cases,
                               sample_clue(include_source=False))
    weighted = weighted_problem()
    weighted_competitors = {
        name: asdict(find_plan(weighted, name))
        for name in ("BFS", "UCS", "ASTAR_HMAX")
    }
    weighted_methods = develop_methods(weighted)
    normal = run_online("TOKEN", "FOUNDRY")
    classic_same_evidence = run_online("TOKEN", "UCS_ONLY")
    fixed = static_fallback("TOKEN")
    shifted = run_online("SHIFT_BADGE", "FOUNDRY")
    return {
        "schema": "motif019f.native-planner-study/v0",
        "native_original_git_blobs": verified,
        "normal_model_upgrade": {
            "status": clean_question.status,
            "question": clean_question.question,
            "guard_concept": clean_question.feature.name if clean_question.feature else None,
            "guard_fact": clean_question.feature.guard_fact if clean_question.feature else None,
            "disproved_alternative": clean_question.rejected_rivals,
            "question_source_blob": clean_question.native_question_blob,
            "dogram_source_blob": clean_question.native_dogram_blob,
        },
        "missing_source": {
            "status": source_hold.status,
            "question": source_hold.question,
            "dogram_was_called": source_hold.native_dogram_blob is not None,
        },
        "weighted_classical_control": {
            "all_search_results": weighted_competitors,
            "generated_method_proposals": [asdict(x) for x in weighted_methods.candidates],
            "chosen_cartridge": asdict(weighted_methods.chosen)
                if weighted_methods.chosen else None,
            "classical_UCS_optimal_cost": weighted_methods.reference.cost,
        },
        "online": {
            "growing_forest": normal,
            "classical_UCS_given_same_question_and_receipts": classic_same_evidence,
            "frozen_incumbent_without_question_learning": fixed,
            "independent_shift_world": shifted,
        },
        "boundaries": {
            "real_actions": False,
            "real_witnesses": False,
            "source_hash_is_origin_authentication": False,
            "question_box_answered_question": False,
            "dogram_proved_causality": False,
            "generated_sensor_out_of_nothing": False,
            "method_synthesis_is_new_classical_mathematics": False,
            "strong_refitted_UCS_receives_same_information": True,
            "live_method_adoption": False,
            "real_time_means_replan_per_synthetic_receipt": True,
        },
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
