"""026F POSTHOC native self-audit: turn a failure into a bounded next question.

This runs AFTER the frozen score; it never rewrites gold labels, changes a
past result, fits a threshold on the same test or deploys a new capability.
"""
from __future__ import annotations

def inspect_semantic_link(receipt:dict)->dict:
    if receipt.get("sample_size")!=25 or len(receipt.get("cases",()))!=25:
        return {"status":"HOLD_INCOMPLETE_EVIDENCE"}
    failed=[
        x for x in receipt["cases"]
        if x["comparison"]["REAL_T5"]["native_review"]=="ELIGIBLE_SYNTHETIC_REPLAN_ONLY"
        and x["synthetic_gold"]!="FOOD"
    ]
    misses=[
        x for x in receipt["cases"]
        if x["synthetic_gold"]!="NONE"
        and x["comparison"]["REAL_T5"]["gate"]!=x["synthetic_gold"]
    ]
    t=receipt["methods"]["REAL_T5"]
    classical=receipt["methods"]["CLASSICAL_TFIDF"]
    return {
        "schema":"motif026f.retrospective-diagnostic/v0",
        "analysis_phase":"POSTHOC_FIND_NEXT_FALSIFIER",
        "status":"OPEN_IMPROVEMENT_TICKET" if failed else "HOLD_NO_OBSERVED_IRRELEVANT_ADMISSIONS",
        "synthetic_irrelevant_reviewed_test_cases":[x["case"] for x in failed],
        "semantic_gate_wrong_cases":[x["case"] for x in misses],
        "t5_correct_labels":t["correct_gate"],
        "same_reference_classical_correct_labels":classical["correct_gate"],
        "critique":(
            "A source-calibrated synthetic test can be irrelevant to the "
            "specific operator note. Calibration of sensor readings is NOT "
            "independent proof that a semantic nomination matches the note."
        ),
        "question_for_next_planning_round":(
            "What independent note-to-question relevance witness could "
            "reject a false-positive meal inquiry without suppressing "
            "truly useful new questions or letting a second correlated "
            "language model certify the first?"
        ),
        "candidate_tests_for_future_shield":(
            "SOURCE_QUOTE_OR_HUMAN_CONFIRMED_RELEVANCE",
            "PROSPECTIVELY_SCORED_ABSTENTION_ON_FRESH_CASES",
            "NATIVE_SEMANTIC_AFFORDANCE_SIGNATURE_IF_AVAILABLE",
        ),
        "recommended_current_operator_action":"KEEP_T5_AS_HELD_REVIEW_ONLY",
        "original_results_immutable":True,
        "not_a_trained_or_autonomous_model":True,
        "new_field_capability_installed":False,
    }
