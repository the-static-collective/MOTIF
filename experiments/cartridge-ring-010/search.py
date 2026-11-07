"""RING-010 search: synthesize and freeze typed graph-rewrite *instances*.

Search never imports novel.py. It only sees synthetic training contrasts
and separate authored development contrasts. Every candidate is a concrete
data-only relation-operator graph; changing candidate parameters changes
which cues/deltas are derived, their source supports, and their abstention.

Risk weighted model selection is not an independently validated guarantee.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path

import world,induce

SCHEMA="motif.ring010.frozen-graph-rewrite-invention.v1"


def score(program,cases):
    out={
        "cases":0,"exact_semantic_graph":0,"wrong_decisive":0,
        "abstained":0,"false_directive_clearance":0,
        "missed_directive":0,"wrong_polarity":0,"wrong_scope":0,
        "non_authoritative_hypotheses":0,
    }
    for ex in cases:
        result=induce.parse(program,ex["text"],ex["observed_event"])
        truth=induce.graphmap(ex["semantic_graph"])
        prediction=result["semantic_graph"]
        out["cases"]+=1
        if prediction is None:
            out["abstained"]+=1
            continue
        out["non_authoritative_hypotheses"]+=1
        vals=induce.graphmap(prediction)
        if vals==truth:
            out["exact_semantic_graph"]+=1
        else:
            out["wrong_decisive"]+=1
        if vals["FORCE"]=="DIRECTIVE" and truth["FORCE"]!="DIRECTIVE":
            out["false_directive_clearance"]+=1
        if vals["FORCE"]!="DIRECTIVE" and truth["FORCE"]=="DIRECTIVE":
            out["missed_directive"]+=1
        out["wrong_polarity"]+=int(vals["POLARITY"]!=truth["POLARITY"])
        out["wrong_scope"]+=int(vals["SCOPE"]!=truth["SCOPE"])
    return out


def objective(m):
    return (8*m["exact_semantic_graph"]
            -10*m["wrong_decisive"]
            -100*m["false_directive_clearance"]
            -m["abstained"])


def synthesize(train,dev):
    world.check(train,split="train")
    world.check(dev,split="dev")
    if train["receipt_sha256"]==dev["receipt_sha256"]:
        raise induce.HOLD("Identical source packets cannot be used for selection")
    results=[]
    for support,cue,gap,purity in itertools.product(
        (2,3,5),(1,2,3),(6,12,20),(0.9,1.0)
    ):
        try:
            program=induce.construct(
                train,min_support=support,max_cue=cue,
                max_gap=gap,purity=purity)
        except induce.HOLD:
            continue
        m=score(program,world.flatten(dev))
        results.append({
            "program":program,
            "dev":m,
            "objective":objective(m),
            "parameters":{"min_support":support,"max_cue":cue,
                          "max_gap":gap,"purity":purity},
        })
    if not results:
        raise induce.HOLD("All bounded derivations rejected by graph typing")
    best=max(results,key=lambda x:(
        x["dev"]["false_directive_clearance"]==0,
        x["objective"],x["dev"]["exact_semantic_graph"],
        -x["dev"]["wrong_decisive"],
        -x["program"]["derived_cue_count"],
        x["program"]["receipt_sha256"]))
    frozen={
        "schema":SCHEMA,
        "status":"SOURCE_DERIVED_GRAPH_EDIT_PROGRAM_FROZEN",
        "source_training_sha256":train["receipt_sha256"],
        "source_development_sha256":dev["receipt_sha256"],
        "training_pairs":len(train["pairs"]),
        "development_pairs":len(dev["pairs"]),
        "configurations_executed":len(results),
        "winning_program":best["program"],
        "winning_dev":best["dev"],
        "winning_objective":best["objective"],
        "selected_parameters":best["parameters"],
        "source_derived_graph_transitions":best["program"]["derived_transition_count"],
        "source_derived_surface_graph_operators":best["program"]["derived_cue_count"],
        "new_semantic_relation_instances_created":True,
        "base_graph_rewrite_opcode_invented":False,
        "heldout_language_module_imported_during_search":False,
        "heldout_labels_consulted":False,
        "source_meanings_author_generated":True,
        "event_bindings_explicitly_provided":True,
        "external_action_executed":False,"authority":"NONE",
    }
    frozen["receipt_sha256"]=world.digest(frozen)
    return frozen


def run():
    training=world.generate("train",seed=2026111001,repeats=6)
    dev=world.generate("dev",seed=2026111002,repeats=6)
    return synthesize(training,dev)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    doc=run()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(doc,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "status":doc["status"],
        "search_attempts":doc["configurations_executed"],
        "graph_transitions_induced":doc["source_derived_graph_transitions"],
        "cue_graph_operators_induced":doc["source_derived_surface_graph_operators"],
        "selected_parameters":doc["selected_parameters"],
        "dev":doc["winning_dev"],
        "receipt_sha256":doc["receipt_sha256"],
    },sort_keys=True))


if __name__=="__main__":
    main()
