"""RING-011 freeze learned multi-relation speech binder BEFORE novel text import.

Only source-generated train + dev contrasts enter search. The winner is
selected by zero-false-root-action-first, then complete typed graph recovery.
No novel.py import. Selection metrics are NOT test-generalization evidence.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path

import corpus,binder

SCHEMA="motif.ring011.frozen-voice-scope-induction.v1"


def measure(model,examples):
    totals={
        "cases":0,"exact_graphs":0,"wrong_decisive":0,
        "abstained":0,"false_root_action_promotion":0,
        "missed_root_action":0,"wrong_scope":0,"wrong_polarity":0,
        "wrong_root_force":0,"carrier_provenance_mismatch":0,
    }
    witnesses=[]
    for source in examples:
        expected=corpus.graph_map(source["semantic_graph"])
        raw=model(source["text"],source["observed_event"],source["carrier"])
        predicted=raw["graph"]
        actual=None if predicted is None else corpus.graph_map(predicted)
        right=actual==expected
        unjustified=actual is not None and (
            actual[("EVENT","REQUESTED_BY_ROOT")] is True
            and expected[("EVENT","REQUESTED_BY_ROOT")] is False)
        totals["cases"]+=1
        totals["exact_graphs"]+=int(right)
        totals["wrong_decisive"]+=int(actual is not None and not right)
        totals["abstained"]+=int(actual is None)
        totals["false_root_action_promotion"]+=int(unjustified)
        if actual is not None:
            totals["missed_root_action"]+=int(
                not actual[("EVENT","REQUESTED_BY_ROOT")]
                and expected[("EVENT","REQUESTED_BY_ROOT")] is True)
            totals["wrong_scope"]+=int(
                actual[("EVENT","SCOPE")]!=expected[("EVENT","SCOPE")])
            totals["wrong_polarity"]+=int(
                actual[("EVENT","POLARITY")]!=expected[("EVENT","POLARITY")])
            totals["wrong_root_force"]+=int(
                actual[("ROOT","FORCE")]!=expected[("ROOT","FORCE")])
            totals["carrier_provenance_mismatch"]+=int(
                any(actual[("DOCUMENT",k)]!=expected[("DOCUMENT",k)]
                    for k in ("CARRIER","EVIDENCE_STATUS")))
        witnesses.append({
            "source_text_sha256":raw.get("original_sha256"),
            "original_carrier":source["carrier"],
            "target":{x[1]:v for x,v in expected.items()},
            "predicted":None if actual is None else {
                x[1]:v for x,v in actual.items()},
            "exact":bool(right),
            "false_root_action_promotion":bool(unjustified),
            "abstained":actual is None,
            "scope_bind_receipts":raw.get("source_derived_rewrites",[]),
            "containment":raw.get("source_containment_graph",[]),
        })
    return {"metrics":totals,"per_case":witnesses}


def synthesize(train,dev):
    corpus.validate(train,split="train")
    corpus.validate(dev,split="dev")
    if train["receipt_sha256"]==dev["receipt_sha256"]:
        raise binder.HOLD("Training source cannot be used as independent model selection")
    attempts=[]
    for mode,support,n,gap,margin in itertools.product(
        ("FLAT","SCOPED"),(2,3),(1,2),(10,18),(1,2)):
        try:
            program=binder.derive(
                train,min_support=support,n=n,gap=gap,
                purity=1.0,binder=mode,min_margin=margin)
        except binder.HOLD:
            continue
        checked=measure(
            lambda text,observed,carrier:
            binder.predict(program,text,observed,carrier),
            corpus.flatten(dev))
        m=checked["metrics"]
        # Penalize ALL observed wrong decisions and especially accidental
        # apparent authorization of an embedded/hypothetical action.
        objective=(7*m["exact_graphs"]-12*m["wrong_decisive"]
                   -150*m["false_root_action_promotion"]-m["abstained"])
        attempts.append((program,checked,objective))
    if not attempts:
        raise binder.HOLD("No source-justified nested scope program found")
    program,checked,objective=max(attempts,key=lambda v:(
        v[1]["metrics"]["false_root_action_promotion"]==0,
        v[2],v[1]["metrics"]["exact_graphs"],
        -v[1]["metrics"]["wrong_decisive"],
        v[0]["parameters"]["binder"]=="SCOPED",
        -v[0]["source_induced_relation_count"],
        v[0]["receipt_sha256"]))
    result={
        "schema":SCHEMA,
        "status":"SOURCE_DERIVED_NESTED_VOICE_PROGRAM_FROZEN",
        "source_train_sha256":train["receipt_sha256"],
        "source_dev_sha256":dev["receipt_sha256"],
        "training_three_way_contrasts":len(train["contrasts"]),
        "development_three_way_contrasts":len(dev["contrasts"]),
        "candidate_inductions_executed":len(attempts),
        "winning_program":program,
        "winning_dev":checked["metrics"],
        "winning_dev_objective":objective,
        "selected_strategy":program["parameters"],
        "learned_graph_rewrite_instances":program["source_induced_edge_rewrites"],
        "learned_clause_context_instances":program["source_induced_relation_count"],
        "actual_programming_primitives_invented":False,
        "developer_labeled_graph_relations_and_bound_entities":True,
        "source_book_private_text_committed":False,
        "source_book_editorial_categories_abstracted":True,
        "sealed_test_imported_during_search":False,
        "sealed_test_labels_used_to_select_model":False,
        "outside_actions_authorized":False,
        "authority":"NONE",
    }
    result["receipt_sha256"]=corpus.digest(result)
    return result


def run():
    return synthesize(
        corpus.generate("train",seed=2026111101,rounds=5),
        corpus.generate("dev",seed=2026111102,rounds=5))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    doc=run()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":doc["status"],
        "candidate_inductions":doc["candidate_inductions_executed"],
        "selected":doc["selected_strategy"],
        "learned_rewrites":doc["learned_graph_rewrite_instances"],
        "learned_contexts":doc["learned_clause_context_instances"],
        "dev":doc["winning_dev"],
        "receipt":doc["receipt_sha256"],
    },sort_keys=True))


if __name__=="__main__":
    main()
