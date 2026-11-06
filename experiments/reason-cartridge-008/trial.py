"""Reproducible discovery: demonstrate a grammar gap, synthesize a macro,
certify its behavior separately, and test whether its cost amortizes.
"""
from __future__ import annotations
import json
from pathlib import Path

from source import (Case, TRAIN_MASKS, WITHHELD_MASKS, lessons, certification,
                    deployment, bfs_truth, SOURCE_REVISION)
from discover import (pin, LEGACY, EXPANDED, detect_gap, synthesize,
                      validate, old_eval, expanded_eval)
from receiver import Receiver
from market import Bid, DiscoveryMarket, make_receipt, validate_receipt
from handoff import draft as review_draft, validate_draft


def bids():
    return (
        Bid("direct-bfs","SOURCE_OWNER","DIRECT_CLASSICAL_BFS",1.0),
        Bid("missing-macro","MOTIF_INVENTOR","GAP_REPAIR_MACRO",9999999999.0),
        Bid("another-name","SECOND_PROPOSER","GAP_REPAIR_MACRO",1e12),
        Bid("no-action","SAFETY_OBSERVER","HOLD_NO_ANSWER",2.0),
    )


def certified():
    raw=synthesize(lessons())
    receiver=Receiver(raw)
    result=receiver.preview(certification())
    if result["errors"]==0:
        receiver.admit("ADMIT_READ_ONLY",result["review_digest"])
    return raw,receiver,result


def run(out=None):
    raw,receiver,check=certified()
    method=validate(raw)
    gap=detect_gap(lessons())
    one=DiscoveryMarket(raw,receiver,bids(),deployment(1)).evaluate()
    bulk=DiscoveryMarket(raw,receiver,bids(),deployment(32)).evaluate()
    extended=DiscoveryMarket(raw,receiver,bids(),deployment(64)).evaluate()
    exact_receipt=make_receipt(raw,receiver,bids(),deployment(32))
    reviewed=validate_receipt(exact_receipt,receiver)
    handoff_raw=review_draft(raw,exact_receipt,receiver)
    checked_handoff=validate_draft(handoff_raw,raw,exact_receipt,receiver)
    program=method["proposed_extension"]["program"]
    typed=(tuple(program["triple"]),tuple(program["pair"]))
    whole_domain_correct=sum(
        expanded_eval(typed,mask)==bfs_truth(Case(mask))
        for mask in range(32)
    )
    best_old=max(sum(old_eval(candidate,mask)==bfs_truth(Case(mask))
                     for mask in TRAIN_MASKS) for candidate in LEGACY)
    if (one["winning_method"]!="DIRECT_CLASSICAL_BFS"
            or bulk["winning_method"]!="GAP_REPAIR_MACRO"
            or bulk["independently_correct"]!=32
            or best_old!=4 or check["cases"]!=27 or check["errors"]):
        raise AssertionError("Missing-primitive experimental controls changed")
    result={
        "schema":"motif.reason.missing-primitive-experiment.v1",
        "source_revision":SOURCE_REVISION,
        "source_git_blob":pin(),
        "five_bit_old_grammar_candidates":len(LEGACY),
        "legacy_programs_refuted_by_teaching":gap["old_candidates_refuted"],
        "source_witnessed_legacy_unsat":gap["all_old_candidates_refuted"],
        "teaching_cases":len(TRAIN_MASKS),
        "strongest_old_program_training_accuracy":best_old,
        "expanded_grammar_candidates":len(EXPANDED),
        "surviving_new_macro_programs":
            method["proposed_extension"]["programs_consistent_with_lessons"],
        "macro_program":program,
        "fundamental_boolean_primitive_invented":False,
        "independent_source_certification":check,
        "whole_five_bit_domain_matches_classical_bfs":whole_domain_correct,
        "one_task_winner":one["winning_method"],
        "thirty_two_task_winner":bulk["winning_method"],
        "sixty_four_task_winner":extended["winning_method"],
        "thirty_two_task_correct":bulk["independently_correct"],
        "thirty_two_task_direct_classical_cost":
            bulk["direct_classical_hypothetical_cost"],
        "thirty_two_task_compiled_cost":bulk["winning_hypothetical_cost"],
        "thirty_two_task_modeled_savings":
            bulk["independent_evidence_gated_savings_points"],
        "duplicate_offers_no_credit":bulk["commonwealth_duplicate_credit"],
        "duplicate_bid_suppressed":bulk["duplicated_offers"],
        "new_validated_commonwealth_method_credit":
            bulk["commonwealth_new_method_credit"],
        "new_real_world_facts":bulk["commonwealth_new_source_facts"],
        "market_receipt_checksum":reviewed["checksum_sha256"],
        "graft_intake_state":checked_handoff["graft"]["intake_state"],
        "cannon_selection_state":checked_handoff["cannon"]["state"],
        "review_handoff_checksum":checked_handoff["checksum_sha256"],
        "read_only_fixture_admitted":receiver.admitted,
        "strong_classical_bfs_comparison_correct":32,
        "classical_planner_with_same_costs_can_match":True,
        "outside_this_five_edge_structure_tested":False,
        "graft_or_cannon_invoked":False,
        "external_actions":False,"real_world_authority":False,
    }
    if out:
        folder=Path(out)
        folder.mkdir(parents=True,exist_ok=True)
        (folder/"method-cartridge.json").write_text(raw,encoding="utf-8")
        (folder/"market-receipt.json").write_text(exact_receipt,encoding="utf-8")
        (folder/"graft-cannon-review-proposal.json").write_text(
            handoff_raw,encoding="utf-8")
        (folder/"benchmark.json").write_text(
            json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return result


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [evidence-directory]")
    print(json.dumps(run(sys.argv[1] if len(sys.argv)==2 else None),
                     indent=2,sort_keys=True))
