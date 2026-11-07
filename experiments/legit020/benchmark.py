"""LEGIT-020: language -> mathematical perspectives -> independent witnesses.

The strong context baseline uses the same declared finite mapping as APERTURE.
A first-guess baseline is an intentionally weak ablation and cannot
establish superiority over good linguistic interpretation systems.
"""
from __future__ import annotations
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from aperture import (REFINEMENTS,open_aperture,update_context,mathalize,
                      speak_math,HOLD)
from perspectives import (graph_spectrum,graph_probe_ladder,
    prove_signedness_difference,verify_double_math,collapse_receipt,
    verify_dogram_source)

STATUS="RESEARCH_HOLD_NARROW_DETERMINISTIC_LANGUAGE_AND_KNOWN_MATH"
CHALLENGES=(
    ("Are these two graphs the same?","I mean compare linear walks.","WALK_EQ"),
    ("Are these two graphs the same?","I mean compare branching three-leaf trees.","CLAW_EQ"),
    ("Are these two graphs the same?","I mean compare graph isomorphism.","ISOMORPHIC"),
    ("Shift x right by one bit.","Treat x as an unsigned 64-bit word.","SHIFT_UNSIGNED"),
    ("Shift x right by one bit.","Treat x as a signed 64-bit word.","SHIFT_SIGNED"),
    ("The bank moved.","Erosion shifted the riverbank.","RIVERBANK"),
    ("The bank moved.","A financial institution moved its branch office.","BANK_INSTITUTION"),
    ("Double x modulo 2^64.","Use bitvector addition.","DOUBLE_ADD"),
    ("Double x modulo 2^64.","Use bitvector left shift.","DOUBLE_SHIFT"),
)

def one_case(raw,context,expected):
    old=open_aperture(raw)
    before=mathalize(old)
    if len(old.candidates)<2:
        raise HOLD("No competing readings")
    new=update_context(old,context)
    after=mathalize(new)
    if (new.source_sha256!=old.source_sha256 or new.raw!=old.raw
        or len(new.candidates)!=1 or new.candidates[0].name!=expected
        or after["parent_receipt_sha256"]!=before["receipt_sha256"]
        or before["accepted_meaning"] is not None
        or after["accepted_meaning"] is not None or new.admitted):
        raise HOLD("Context erased earlier possibility or minted intent")
    return {
        "raw":raw,"context":context,
        "original_receipt":before["receipt_sha256"],
        "context_receipt":after["receipt_sha256"],
        "original_possible_readings":[x.name for x in old.candidates],
        "compatible_reading_after_cut":new.candidates[0].name,
        "mathematical_question_after_cut":new.candidates[0].executable_question,
        "gloss_back_to_language":speak_math(expected),
        "original_alternatives_preserved":True,
        "contextual_resolution_not_authorized_intent":True,
        "one_first_guess_happened_to_match":old.candidates[0].name==expected,
        "strong_context_parser_agrees_with_aperture":REFINEMENTS.get(
            context.strip().lower())==expected,
        "admitted":False,
    }

def run():
    upstream=verify_dogram_source()
    graph=graph_spectrum()
    ladder=graph_probe_ladder()
    signed=prove_signedness_difference()
    double=verify_double_math()
    initial={
        "graph":open_aperture("Are these two graphs the same?"),
        "shift":open_aperture("Shift x right by one bit."),
        "bank":open_aperture("The bank moved."),
    }
    cases=[one_case(*row) for row in CHALLENGES]
    n=len(cases)
    naive=sum(x["one_first_guess_happened_to_match"] for x in cases)
    strong=sum(x["strong_context_parser_agrees_with_aperture"] for x in cases)
    if n!=9 or naive!=4 or strong!=9:
        raise HOLD("Incorrect source-anchored context experiment")
    lost={k:collapse_receipt(v) for k,v in initial.items()}
    for receipt in lost.values():
        count=len(receipt["source_readings"])
        if len(receipt["lost_reading_pairs"])!=count*(count-1)//2:
            raise HOLD("Failed Dogram distinction-loss calibration")
    unknown=mathalize(open_aperture("A sentence with no declared decoder."))
    if unknown["language_to_math_candidates"] or unknown["accepted_meaning"] is not None:
        raise HOLD("Unknown language falsely interpreted")
    return {
        "schema":"motif.legit020.aperture-mathalizer-report.v1",
        "experiment":"MOTIF-LEGIT-020",
        "title":"APERTURE_DOGRAM_MATHALIZING",
        "status":STATUS,
        "source":"PINNED_CANONICAL_DOGRAM_AND_APERTURE_ARCHITECTURE",
        "original_Dogram_math_sources":upstream,
        "aperture_contract":{
            "source_document":"the-static-collective/the-daily-slice/slices/2026/09/2026-09-17/aperture-hold-the-meanings-open.md",
            "sparse_address_space_size":27,
            "axes":["SIGNAL_CONTEXT_GAP","FACT_IDEA_RELATION",
                    "SUBSTANCE_LINEAGE_AUTHORITY"],
            "initial_ambiguity_preserved":True,
            "context_creates_descendant_not_history_rewrite":True,
            "context_not_authority":True,
            "unknown_language_holds":True,
            "T5_optional_provider_not_semantic_authority":True,
        },
        "perspective_geometry":graph,
        "dogram_graph_probe_ladder":ladder,
        "bitvector_signedness_counterexample":signed,
        "bitvector_double_math_language_bridge":double,
        "Dogram_anti_collapse_probes":lost,
        "registered_context_cases":cases,
        "comparison":{
            "tests":n,
            "deliberately_early_single_reading_baseline_matches":naive,
            "aperture_after_declared_context_matches":n,
            "strong_context_aware_parser_matches":strong,
            "no_superiority_over_strong_context_parser":True,
            "not_fair_open_world_language_benchmark":True,
            "early_single_guess_is_intentionally_weak_ablation":True,
            "mathalizer_has_only_declared_grammar":True,
        },
        "gates":{
            "original_Dogram_math_modules_pinned":True,
            "actual_graph_path_equivalence_vs_branch_separation":True,
            "actual_external_Z3_signedness_difference":True,
            "actual_external_Z3_equivalent_double_implementations":True,
            "ambiguous_language_not_silently_collapsed":True,
            "reversible_raw_provenance_and_context_lineage":True,
            "general_language_understanding_demonstrated":False,
            "new_math_historically_original":False,
            "improves_external_SyGuS_2017_results":False,
            "independently_verified_recursive_compounding":False,
            "automatic_source_promotion":False,
        },
        "new_public_Dogram_operator":False,
        "human_intent_deduced_from_math":False,
        "real_world_authority":False,
        "main_branch_automatically_changed":False,
    }

def main():
    if sys.argv[1:] not in ([],["--emit"]):
        raise SystemExit("Usage: python experiments/legit020/benchmark.py [--emit]")
    report=run()
    if sys.argv[1:]:
        Path("/tmp/motif-legit020-aperture-mathalizing.json").write_text(
            json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "experiment":report["experiment"],"status":report["status"],
        "graph_equal_under_paths":report["perspective_geometry"]["perspective_PATH"]["equal"],
        "graph_equal_under_branch":report["perspective_geometry"]["perspective_BRANCH"]["equal"],
        "branch_witness":report["perspective_geometry"]["perspective_BRANCH"]["star_sequence"][-1],
        "real_bitvector_type_counterexample":report["bitvector_signedness_counterexample"]["example_x"],
        "known_double_identity_reproved":report["bitvector_double_math_language_bridge"]["external_Z3_proves_equivalence"],
        "contextual_cases":report["comparison"],
        "lost_distinctions":{k:len(v["lost_reading_pairs"])
                              for k,v in report["Dogram_anti_collapse_probes"].items()},
    },indent=2,sort_keys=True))
if __name__=="__main__":main()
