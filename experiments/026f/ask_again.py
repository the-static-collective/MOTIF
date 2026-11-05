"""026F: native meta-search over possible T5 occupations, including no-model.

This never trains T5 or lets it certify its own competence. Every result is
conditional on the frozen synthetic examples, strong same-text controls,
unverified source claims and actual measured inference seconds.
"""
from __future__ import annotations
from dataclasses import asdict
from math import log,sqrt

ROLE_MENU=(
    ("NO_T5","Native rules, 022F Question Machine and 016 Forest only",
     "ZERO_MODEL_LATENCY"),
    ("SEMANTIC_GAP_SCOUT","T5 encoder suggests a candidate missing gate",
     "026F_DIRECT_SCORE"),
    ("QUESTION_CARTRIDGE_FINDER","T5 hint retrieves a registered 022F probe",
     "026F_END_TO_END_SCORE"),
    ("SOURCE_SIMILARITY_INDEX","T5 embeds different notes for search or near-duplicates",
     "UNTESTED_ON_INDEPENDENT_SOURCES"),
    ("REPRESENTATION_DRIFT_ALARM","T5 semantic shifts may flag new structural unknowns",
     "UNTESTED_ON_PROSPECTIVE_DRIFT"),
    ("DECODER_OBSERVER_CRITIC_HYPEMAN","T5 generates direct advice/decisions",
     "025F_NEGATIVE"),
)

def assess_careers(report:dict)->dict:
    """Deliberately conservative: NO_T5 for automated decisions always.

    Model can get a provisional *human-held* research role if it improves
    both classical routes on this tiny synthetic test without new bad gate
    labels. It can NEVER win self-granted execution permission.
    """
    m=report["methods"]
    n=report["sample_size"]
    if n!=25 or any(k not in m for k in ("NATIVE","CLASSICAL_TFIDF","REAL_T5")):
        raise ValueError("HOLD_INCOMPLETE_PROSPECTIVE_ROLE_TRIAL")
    t=m["REAL_T5"]; c=m["CLASSICAL_TFIDF"]; b=m["NATIVE"]
    delta=t["correct_gate"]-max(c["correct_gate"],b["correct_gate"])
    qdelta=t["relevant_reviewed_question_count"]-max(
        c["relevant_reviewed_question_count"],
        b["relevant_reviewed_question_count"],
    )
    false_delta=t["irrelevant_reviewed_question_count"]-min(
        c["irrelevant_reviewed_question_count"],
        b["irrelevant_reviewed_question_count"],
    )
    # A conservative paired-sample Hoeffding lower bound, for illustration.
    # n is tiny; a narrow positive score does NOT prove transfer.
    accuracy_gain=delta/n
    low=accuracy_gain-sqrt(2*log(20)/n)
    wins_semantics=delta>0 and t["false_gate_when_none"]==0
    wins_relay=qdelta>0 and t["irrelevant_reviewed_question_count"]==0
    if wins_semantics:
        provisional="SEMANTIC_GAP_SCOUT"
        hypothesis="Test a silent semantic gap index on independent source text."
    elif wins_relay:
        provisional="QUESTION_CARTRIDGE_FINDER"
        hypothesis="Test native typed question retrieval under independent truth."
    else:
        provisional="NO_T5"
        hypothesis="Try a new documented domain or a non-model semantic index before using T5."
    return {
        "question":"What use of the tiny T5 encoder, if any, supplies evidence-backed benefit beyond classical MOTIF?",
        "evaluation_method":"NATIVE_COMPARATOR_WITH_EXPLICIT_NONE_AND_UNTESTED_ROLES",
        "role_menu":[{"role":k,"contract":v,"evidence":s}
                     for k,v,s in ROLE_MENU],
        "native_automated_execution_verdict":"NO_T5",
        "provisional_research_role":provisional,
        "real_world_deployment_verdict":"HOLD_NO_INDEPENDENT_FIELD_VALIDATION",
        "delta_correct_gate_vs_best_tested_classical":delta,
        "delta_relevant_reviewed_questions_vs_best_classical":qdelta,
        "extra_irrelevant_reviewed_questions_vs_safest_classical":false_delta,
        "conservative_accuracy_gain_lower_bound_95":round(low,5),
        "cost_of_waiting_or_welfare":"HOLD_NOT_CALIBRATED",
        "inference_seconds_measured":report["t5_encoder_seconds"],
        "model_hired_for_permissions":False,
        "model_hired_for_external_actions":False,
        "model_writes_original_native_plan":False,
        "new_question_it_generates_for_next_research":hypothesis,
        "insufficient_sample_to_claim_general_advantage":True,
        "prior_decoder_results":"3/12 STATUS, 2/12 MISSING_GATE, 3/12 NEXT; NO_T5",
    }
