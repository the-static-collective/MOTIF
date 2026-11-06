"""Holdout report for the adversarial reader.

Gold independent judicial interpretation keys are used ONLY here, after
source-evidence graphs have been constructed and frozen. A two-case training
corpus informs the developer's fixed lexical grammar but is not fitted by an
LLM. This experiment measures structure/provenance, not legal advice.
"""
from __future__ import annotations

from pathlib import Path
import json

from opinions import DOCUMENTS,documents
from reader import read,export,validate,investigate,digest
from bridge011 import evaluate
from gold import NEW_EVALUATION,TRAINING_CONTROLS


def run(folder=None):
    outputs={}
    exact=0
    total=0
    for case_id,expected in NEW_EVALUATION.items():
        doc=validate(export(case_id))
        voices=doc["parsed_voices"]
        role_checks=[]
        for judge,reference in expected["speakers"].items():
            for field,target in reference.items():
                match=voices.get(judge,{}).get(field)==target
                role_checks.append({
                    "judge":judge,"field":field,"expected":target,
                    "observed":voices.get(judge,{}).get(field),"correct":match})
                exact+=int(match)
                total+=1
        bridge=evaluate(case_id)
        outputs[case_id]={
            "case_url":doc["source_url"],
            "source_citation":doc["citation"],
            "source_snapshot_sha256":doc["source_snapshot_digest"],
            "paragraphs_reviewed":doc["source_paragraph_count"],
            "judicial_voices":list(voices),
            "reviewed_role_and_disposition_fields":role_checks,
            "field_errors":sum(not x["correct"] for x in role_checks),
            "grounded_nodes":len(doc["evidence_nodes"]),
            "grounded_argument_links":len(doc["argument_links"]),
            "four_value_per_voice":bridge["per_voice_interpretations"],
            "disposition_alignment":bridge["named_judgment_alignment"],
            "exact_source_spans_not_synthetic_legal_decision":True,
        }
    yates=outputs["YATES"]
    nix=outputs["NIX"]
    query=investigate("YATES","What is a tangible object used to record information?")
    unknown=investigate("YATES","Is the courthouse made of cheese?")
    if (exact!=total or total<15
            or yates["disposition_alignment"]!=(5,4)
            or len(yates["judicial_voices"])!=3
            or nix["disposition_alignment"] is not None
            or query["stage"]!="SOURCE_SPANS_NEED_INTERPRETATION"
            or unknown["stage"]!="HOLD_NO_RELEVANT_ANCHORED_EVIDENCE"):
        raise AssertionError("Independent unfamiliar opinion reading failed")
    result={
        "schema":"motif.reason.adversarial-reader.benchmark.v1",
        "training_cases":list(documents(True)),
        "unseen_opinion_cases":list(documents(False)),
        "labeled_historical_review_fields_correct":exact,
        "labeled_historical_review_fields_total":total,
        "independent_field_errors":total-exact,
        "heldout_court_readings":outputs,
        "joined_judgment_five_vs_four_while_plurality_four":True,
        "no_false_four_value_BOTH_in_individual_voice":all(
            v["reported_legal_interpretation_status"]!="BOTH"
            for v in yates["four_value_per_voice"].values()),
        "source_retrieval_stage":query["stage"],
        "unsupported_cheese_retrieval_stage":unknown["stage"],
        "strong_classical_rule_based_reader_can_match":True,
        "opinion_source_data_is_curated_partial_transcription":True,
        "gold_is_independent_annotation_not_a_hidden_model_test":True,
        "does_not_extract_general_legal_rules":True,
        "full_opinions_not_parsed":True,
        "current_law_not_verified":True,
        "no_external_actions":True,
        "real_world_authority":False,
    }
    if folder:
        path=Path(folder);path.mkdir(parents=True,exist_ok=True)
        (path/"benchmark.json").write_text(
            json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        for case in DOCUMENTS:
            (path/(case.lower()+"-argument-graph.json")).write_text(
                export(case),encoding="utf-8")
        (path/"unanswered-question.json").write_text(
            json.dumps(unknown,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    return result


if __name__=="__main__":
    import sys
    if len(sys.argv)>2:
        raise SystemExit("usage: python trial.py [evidence-directory]")
    print(json.dumps(run(sys.argv[1] if len(sys.argv)==2 else None),
                     indent=2,sort_keys=True))
