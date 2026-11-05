"""026F real CPU evaluation: cached T5 encoder -> 022F -> original Forest.

25 newly frozen synthetic notes, 3 approaches, same 12 source examples.
All action and outcome scores are synthetic; T5 is not a field witness.
"""
from __future__ import annotations
from collections import Counter
import json,os,time
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
for folder in ("016","021f","022f","025f","026f"):
    p=str(ROOT/folder)
    if p not in sys.path:sys.path.append(p)
from chorus import LocalFlanT5Small
from semantic_router import CachedT5GateClassifier,ClassicalGateClassifier
from question_relay import review_semantic_question
from frozen_cases import CASES,digest
from ask_again import assess_careers

METHODS=("NATIVE","CLASSICAL_TFIDF","REAL_T5")

def benchmark():
    import torch
    torch.set_num_threads(2)
    t0=time.monotonic()
    t5=LocalFlanT5Small(os.environ.get(
        "MOTIF_FLAN_MODEL_DIR","google/flan-t5-small"
    ))
    t5._prepare()
    t_load=time.monotonic()-t0
    embedded=CachedT5GateClassifier(t5)
    classical=ClassicalGateClassifier()
    classifiers={"NATIVE":None,"CLASSICAL_TFIDF":classical,"REAL_T5":embedded}
    totals={name:Counter() for name in METHODS}
    rows=[]
    for i,case in enumerate(CASES):
        comparisons={}
        # Separate fabricated worlds are used only by the 022F simulated
        # source witness, never as model input or a real permission signal.
        hidden=("10","01","11","00")[i%4]
        for name in METHODS:
            receipt=review_semantic_question(
                case.note,classifiers[name],hidden_world=hidden,
            )
            h=receipt["hint"]
            predicted=h["possible_gate"] or "NONE"
            admitted=receipt["status"]=="ELIGIBLE_SYNTHETIC_REPLAN_ONLY"
            relevant=admitted and case.gold_gate=="FOOD"
            irrelevant=admitted and case.gold_gate!="FOOD"
            t=totals[name]
            t["correct_gate"]+=predicted==case.gold_gate
            t["missed_gate"]+=(case.gold_gate!="NONE" and predicted=="NONE")
            t["false_gate_when_none"]+=(case.gold_gate=="NONE" and predicted!="NONE")
            t["wrong_nonempty_gate"]+=(predicted not in ("NONE",case.gold_gate))
            t["new_reviewed_question_count"]+=admitted
            t["relevant_reviewed_question_count"]+=relevant
            t["irrelevant_reviewed_question_count"]+=irrelevant
            t["model_or_retriever_queries"]+=(
                h["origin"] not in ("NATIVE_LEXICAL_RULE","NO_MODEL")
            )
            assert receipt["external_actions"]==0
            assert not receipt["human_permissions_inferred"]
            assert not receipt["field_facts_changed"]
            assert not receipt["primary_native_plan_overwritten"]
            assert receipt["test_id"] in (None,"FOOD_SERVICE_GATE","REPEAT_AUDIO_TEST")
            comparisons[name]={
                "gate":predicted,"source":h["origin"],
                "question":h["text_question"],"typed_test":receipt["test_id"],
                "native_review":receipt["status"],
                "independently_reviewed_synthetic_question":admitted,
                "relevant":relevant,
                "synthetic_run":receipt["independent_synthetic_run"],
            }
        rows.append({
            "case":case.id,"note":case.note,"synthetic_gold":case.gold_gate,
            "comparison":comparisons,
            "notes_are_synthetic":True,
            "true_label_never_sent_to_encoder":True,
        })
    stats={name:dict(t) for name,t in totals.items()}
    for name in METHODS:
        for k in (
            "correct_gate","missed_gate","false_gate_when_none",
            "wrong_nonempty_gate","new_reviewed_question_count",
            "relevant_reviewed_question_count",
            "irrelevant_reviewed_question_count","model_or_retriever_queries",
        ):stats[name].setdefault(k,0)
        stats[name]["total"]=len(CASES)
    report={
        "schema":"motif026f.real-t5-feedback-and-job-research/v0",
        "actual_t5_encoder_loaded":t5._model is not None,
        "real_t5_decoder_calls":0,
        "model":"google/flan-t5-small",
        "pinned_revision":os.environ.get("MOTIF_FLAN_REVISION","LOCAL_UNPINNED"),
        "frozen_corpus_digest":digest(),
        "sample_size":len(CASES),
        "t5_model_load_seconds":round(t_load,4),
        "t5_encoder_reference_build_seconds":embedded.build_seconds,
        "t5_encoder_seconds":round(embedded.total_query_seconds+
                                    embedded.build_seconds,4),
        "t5_query_count":embedded.total_queries,
        "classical_query_count":classical.queries,
        "total_wall_seconds":round(time.monotonic()-t0,4),
        "methods":stats,
        "cases":rows,
        "human_action_or_permission_autonomous":False,
        "all_field_and_source_events_synthetic":True,
    }
    report["native_meta_reassessment"]=assess_careers(report)
    return report

if __name__=="__main__":
    print(json.dumps(benchmark(),indent=2,sort_keys=True))
