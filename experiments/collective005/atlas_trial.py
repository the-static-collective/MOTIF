"""Source-pinned 1998 Read/Wilson Atlas train/frozen-question heldout pressure.

This extends COLLECTIVE-004's TWO honest HOLDs among 28 declared heldout
Atlas graph pairs. The new primitive language is composed from generic
vertex/edge/count atoms after a TRAIN problem exposes the missing question.

The original seven-node graphs have independent historical authorship.
Source-owner callbacks, agent selection, question grammar, train/test
protocol and adjudication are engineer-owned; not an external blind test.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE.parent/"collective004"))
sys.path.insert(0,str(HERE.parent/"collective003"))

from external_atlas import (
    source_module,carrier,LEGIT022_COMMIT,ATLAS_DATA_SHA256,
    LEGIT022_ATLAS_BLOB
)
from national_treasure_frontier import (
    build_node,verify_node,NT_CASES_COMMIT,NT_BOX_COMMIT
)
from question_inventor import HOLD,canonical,digest
from primitive_birth import (
    GRAMMAR,emit_ast,invent_question,old_question_fingerprint,
    execute_generated,independent_permutation_count,networkx_reference,
    classical_fair_reference,SimulatedAtlasSourceOwner,research_packet,
    reenter
)

SCHEMA="motif.collective005.external-atlas-frozen-primitive-research.v1"


def original_source_proof(atlas_module,protocol):
    """Verified original carrier, but does not certify external identity."""
    if (protocol.get("atlas_data_sha256")!=ATLAS_DATA_SHA256
        or not protocol.get("original_carrier_authorship_independent_of_MOTIF")
        or not protocol.get("benchmark_is_public_and_not_externally_blind")
        or atlas_module.VERSION!="3.4.2"):
        raise HOLD("Original external graph corpus not source pinned")
    return {
        "source":"Read/Wilson 1998 Graph Atlas",
        "original_atlas_data_pinned":True,
        "original_atlas_data_sha256":ATLAS_DATA_SHA256,
        "source_loaded_from":"MOTIF_LEGIT022_PINNED_SOURCE",
        "source_loader_commit":LEGIT022_COMMIT,
        "source_loader_git_blob":LEGIT022_ATLAS_BLOB,
        "dataset_originated_independently_of_MOTIF":True,
        "challenge_pair_selection_engineer_authored":True,
        "independent_external_human_authentication":False,
        "public_not_cryptographically_blinded":True,
        "human_source_authority":"NONE",
    }


def old_only_classify(task):
    a,b=(carrier(x) for x in task.graphs)
    previous=old_question_fingerprint((a,b))
    return previous, (a,b)


def run(atlas_root,case_root,box_root):
    atlas=source_module(atlas_root)
    train,heldout,protocol=atlas.cohort()
    atlas.verify_prepared(train,heldout,protocol)
    provenance=original_source_proof(atlas,protocol)
    nt=build_node("same-state-different-world",case_root,box_root)
    verify_node(nt,case_root,box_root)

    train_records=[]
    proposed=[]
    for task in train:
        prev,worlds=old_only_classify(task)
        row={"pair_ids":list(task.atlas_ids),
             "old_plus_degree_pair_language_saturated":
                prev["previous_two_question_grammars_saturated"]}
        if prev["previous_two_question_grammars_saturated"]:
            candidate=invent_question(worlds)
            row["candidate_language_status"]=candidate["status"]
            row["candidate_depths_tested"]=[x["depth"] for x in
                                            candidate["search_history"]]
            if candidate["status"]=="COMPOSED_NEW_QUESTION_PRIMITIVE_REVIEW_ONLY":
                proposed.append(candidate["selected_ast"])
                row["composed_operator"]=candidate["selected_ast"]
            else:
                row["unresolved_remains_hold"]=True
        else:
            row["not_a_question_grammar_deficit"]=True
        train_records.append(row)

    if len(proposed)!=1:
        raise HOLD("Training cohort did not uniquely establish a freeze candidate")
    frozen=proposed[0]
    if frozen!=emit_ast(4):
        raise HOLD("Training did not independently select advertised depth")
    # EVIDENCE SELECTION FREEZES HERE; no further grammar or test rule adaptation.
    frozen_sha=digest(frozen)

    tests=[]
    for task in heldout:
        old,worlds=old_only_classify(task)
        pair_ids=list(task.atlas_ids)
        if not old["previous_two_question_grammars_saturated"]:
            tests.append({
                "pair_ids":pair_ids,
                "status":"PREVIOUS_QUESTION_LANGUAGE_ALREADY_SUFFICIENT",
                "synthetic_owner_calls":0,
                "not_a_new_primitive_success":True,
            })
            continue
        # ONLY evaluate the PREVIOUSLY SELECTED frozen question. No re-select
        # from heldout candidate outcomes or adapt allowed query grammar.
        predictions=[execute_generated(frozen,g) for g in worlds]
        if predictions!=[independent_permutation_count(frozen,g) for g in worlds] or (
            predictions!=[networkx_reference(frozen,g) for g in worlds]
        ):
            raise HOLD("External Atlas heldout independent evaluators disagree")
        if predictions[0]==predictions[1]:
            tests.append({
                "pair_ids":pair_ids,
                "status":"HOLD_FROZEN_NEW_QUESTION_DOES_NOT_SEPARATE",
                "frozen_question":frozen,
                "actual_observation_pair":predictions,
                "synthetic_owner_calls":0,
                "refusal_to_guess":True,
            })
            continue
        # Matched classical baseline is allowed SAME RAW ATOMS and AST lengths.
        classical=classical_fair_reference(worlds)
        if classical!=frozen:
            raise HOLD("Frozen policy differs from fair baseline; document failure")
        reply_cases=[]
        for realized in (0,1):
            owner=SimulatedAtlasSourceOwner(worlds[realized],pair_ids)
            receipt=research_packet(
                nt,worlds,owner,
                source_atlas_proof=provenance
            )
            if receipt.get("result")!="SCOPED_SYNTHETIC_ATLAS_WORLD_IDENTIFIED":
                raise HOLD("Research packet did not produce source-owned proof")
            if receipt["new_program_ast"]!=frozen:
                raise HOLD("Heldout selection changed trained question type")
            if receipt["remaining_possible_world_indices"]!=[realized]:
                raise HOLD("Wrong independent Atlas candidate identified")
            reopened=reenter(
                json.loads(json.dumps(receipt)),nt,owner,
                source_atlas_proof=provenance
            )
            if (reopened["new_discovery_questions"]!=0
                or owner.questions!=1):
                raise HOLD("Reentry re-asked question")
            reply_cases.append({
                "realized_index_visible_only_to_evaluator":realized,
                "correctly_identified":True,
                "new_source_questions":owner.questions,
                "new_reentry_questions":reopened["new_discovery_questions"],
                "source_rechecks":owner.rechecks,
                "complete_proof_carrying_packet":receipt,
            })
        tests.append({
            "pair_ids":pair_ids,
            "status":"FROZEN_COMPOSED_PRIMITIVE_SEPARATES",
            "frozen_ast_sha256":frozen_sha,
            "source_counts_by_candidate":predictions,
            "same_grammar_classical_exact_tie":True,
            "synthetic_owner_calls":sum(r["new_source_questions"]
                                         for r in reply_cases),
            "source_observation_cases":reply_cases,
        })

    def stats(records):
        successes=sum(r["status"]=="FROZEN_COMPOSED_PRIMITIVE_SEPARATES"
                      for r in records)
        holds=sum(r["status"]=="HOLD_FROZEN_NEW_QUESTION_DOES_NOT_SEPARATE"
                  for r in records)
        old=sum(r["status"]=="PREVIOUS_QUESTION_LANGUAGE_ALREADY_SUFFICIENT"
                for r in records)
        if successes+holds+old!=len(records):
            raise HOLD("Silent omission of a source graph task")
        return {
            "all_pairs":len(records),
            "previously_resolved":old,
            "previously_unsolved":successes+holds,
            "frozen_new_primitive_newly_resolved":successes,
            "honest_holds":holds,
            "classical_same_grammar_ties":successes,
            "realized_world_observations_correct":2*successes,
            "new_source_owner_calls":sum(r["synthetic_owner_calls"]
                                          for r in records),
        }

    result={
        "schema":SCHEMA,
        "source_NT_node":nt,
        "atlas_source_provenance":provenance,
        "unmodified_original_legit022_protocol":protocol,
        "train_records":train_records,
        "train_pairs":len(train),
        "train_previous_question_grammar_holds":
            sum(r["old_plus_degree_pair_language_saturated"]
                for r in train_records),
        "training_generated_ast":frozen,
        "training_ast_sha256":frozen_sha,
        "question_growth_max_edges":GRAMMAR["max_edges"],
        "question_ast_frozen_before_any_heldout_evaluation":True,
        "heldout":stats(tests),
        "heldout_pair_records":tests,
        "had_to_grow_question_language_beyond_old_and_degreepair":True,
        "no_handwritten_four_edge_path_operator_in_primitive_library":True,
        "raw_graph_primitives_and_search_bounds_human_authored":True,
        "original_atlas_authorship_independent_but_experiment_not_blinded":True,
        "new_math_or_unrestricted_program_invention_not_established":True,
        "source_owner_is_local_simulated_not_real_independent_agent":True,
        "source_NT_mystery_remains_unanswered":True,
        "automatic_admission":False,
        "installed":False,
        "external_authority":"NONE",
        "status":"RESEARCH_HOLD_NEW_EXECUTABLE_QUESTION_COMPOSITION",
    }
    result["integrity_digest"]=digest(result)
    return result


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--atlas-root",required=True)
    parser.add_argument("--case-root",required=True)
    parser.add_argument("--box-root",required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.atlas_root,args.case_root,args.box_root),
                     indent=2,sort_keys=True))
