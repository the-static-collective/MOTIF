"""MOTIF-027F POSTHOC: did three encoder heads show useful diversity?

This is not a prospective test: all outcomes in the first 50-case corpus
have already been observed. No threshold or architecture learned here may
be evaluated on the same cases as if unseen, or be silently deployed.

A hindsight 'pick whichever head was right' ceiling is not an executable
policy. It only reveals possible complementarity worth *independent* tests.
"""
from __future__ import annotations
from collections import Counter

def ask_about_specialization_again(report:dict)->dict:
    cases=report.get("cases",())
    if len(cases)!=50:
        return {"status":"HOLD_POSTHOC_EVIDENCE_MISSING"}
    roles=("SCOUT","SKEPTIC","CARTRIDGE_FINDER")
    correct=Counter()
    distinct=Counter()
    all_wrong=[]
    oracle_any=0
    three_agreed=0
    split=0
    false_none=[]
    for row in cases:
        by_role={n["role"]:n["label"] for n in row["specialist_nodes"]}
        if not by_role: # native preflight bypass; no T5 vote happened
            continue
        if set(by_role)!=set(roles):
            return {"status":"HOLD_INCOMPLETE_SPECIALIST_RECORD"}
        gold=row["gold"]
        right=[k for k,v in by_role.items() if v==gold]
        oracle_any+=bool(right)
        for role in right:
            correct[role]+=1
        for role in ("SKEPTIC","CARTRIDGE_FINDER"):
            distinct[role]+=(
                by_role[role]==gold and by_role["SCOUT"]!=gold
            )
        if not right:all_wrong.append(row["id"])
        labels=set(by_role.values())
        three_agreed+=len(labels)==1
        split+=len(labels)>1
        if gold=="NONE" and row["methods"]["THREE_T5_2_OF_3"]["held_review_question"]:
            false_none.append(row["id"])
    single=report["scores"]["SINGLE_T5_ANCHORED"]
    two=report["scores"]["THREE_T5_2_OF_3"]
    anchor=report["scores"]["SOURCE_ANCHOR_ONLY"]
    consensus_gain=two["correct_held_offers"]-single["correct_held_offers"]
    anchor_gain=anchor["correct_held_offers"]-two["correct_held_offers"]
    if consensus_gain<=0 and anchor_gain>0:
        answer="THREE_T5_VOTING_NOT_EARNED"
        next_question=(
            "On a NEW independently authored corpus, could three distinct "
            "tasks—not three votes on the same category—help? Test one T5 "
            "as synonym scout, a second as quotation locator, and a third "
            "as counterexample/negation finder. Compare against the same "
            "three tasks implemented without any LLM and preserve human "
            "review/inaction costs."
        )
    else:
        answer="HOLD_WEAK_CORRELATED_EVIDENCE"
        next_question=(
            "Can a prospective holdout justify dynamic selective specialist "
            "calls at the same evidence and computation budget as a strong "
            "classical source-relevance model?"
        )
    return {
        "schema":"motif027f.posthoc-specialization-audit/v0",
        "phase":"POSTHOC_NOT_NEW_BLINDED_EVIDENCE",
        "status":answer,
        "heads":tuple(roles),
        "head_correct_on_called_cases":dict(correct),
        "additional_correct_when_scout_wrong":dict(distinct),
        "hindsight_any_head_correct_count":oracle_any,
        "hindsight_oracle_is_not_an_action_policy":True,
        "cases_all_heads_wrong":all_wrong,
        "all_heads_agreed_cases":three_agreed,
        "heads_disagreed_cases":split,
        "false_review_offers_on_none_cases":false_none,
        "quorum_gain_over_single_in_correct_held_offers":consensus_gain,
        "source_only_gain_over_quorum_in_correct_held_offers":anchor_gain,
        "candidate_new_role_assignment":"UNTESTED_SEQUENTIAL_DISTINCT_JOBS",
        "next_research_question":next_question,
        "model_authority":"NONE",
        "model_inferred_external_permissions":False,
    }
