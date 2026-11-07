"""RING-010: both newly induced graph operations AND errors are source-bound.

This graph is evidence transport, not an authoritative ontology. A model can
be better than controls in total exact outcomes while *still unsafe to trust*
when it confuses hypothetical/quoted language with direct requests.

Every per-case witness is reconciled against reported aggregate counts.
No false interpretation is suppressed; these were all author-created labels.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import world,induce,benchmark

SCHEMA="motif.ring010.measured-graph-operator-hypergraph.v1"

class HOLD(ValueError):
    pass


def digest(x):
    return world.digest(x)


def validate(frozen,report):
    benchmark.verify_artifact(frozen)
    if (not isinstance(report,dict)
            or report.get("schema")!=benchmark.SCHEMA
            or report.get("status")!="GENERATED_GRAPH_RELATIONS_FROZEN_AND_FALSIFIED"
            or report.get("receipt_sha256")!=digest({
                k:v for k,v in report.items() if k!="receipt_sha256"})
            or report.get("frozen_program_receipt_sha256")!=frozen["receipt_sha256"]
            or report.get("induced_program_receipt_sha256")!=frozen[
                "winning_program"]["receipt_sha256"]
            or report.get("real_world_authority")!="NONE"
            or report.get("external_actions_executed") is not False
            or report.get("newly_installed_cartridge_methods")!=0
            or report.get("independent_human_language_annotation") is not False):
        raise HOLD("Over-authorized or changed semantic source testimony")
    packets=report.get("test_packets")
    if not isinstance(packets,list) or len(packets)!=2:
        raise HOLD("Two source heldout packets required")
    seen=set()
    totals={}
    for packet in packets:
        source=packet.get("packet_receipt_sha256")
        if (type(source) is not str or len(source)!=64 or source in seen
                or packet.get("heldout_labels_were_not_used_to_select_program") is not True
                or packet.get("utterances_were_author_generated") is not True):
            raise HOLD("Duplicate or incorrectly scoped heldout source")
        seen.add(source)
        models=packet.get("models")
        if (not isinstance(models,dict) or set(models)!={
                "induced_graph_relations","word_bayes_same_training",
                "word_bigram_bayes_same_training","always_hold"}):
            raise HOLD("Strong source-matched method controls missing")
        for name,entry in models.items():
            rows=entry.get("per_case")
            metrics=entry.get("metrics")
            if (not isinstance(rows,list)
                    or len(rows)!=packet.get("count")
                    or not isinstance(metrics,dict)
                    or metrics.get("cases")!=len(rows)
                    or sum(x["exact"] for x in rows)!=metrics["exact_semantic_graph"]
                    or sum(x["false_directive"] for x in rows)!=metrics[
                        "false_directive_clearance"]
                    or sum(x["abstained"] for x in rows)!=metrics["abstained"]
                    or sum(not x["abstained"] and not x["exact"] for x in rows)
                       !=metrics["wrong_decisive"]):
                raise HOLD("Case-level semantic errors contradict aggregate")
            aggregate=totals.setdefault(name,{k:0 for k in metrics})
            for k in aggregate:
                aggregate[k]+=metrics[k]
    if totals!=report.get("combined"):
        raise HOLD("Reported combined measurements disagree with source cases")
    return packets


def build(frozen,report):
    packets=validate(frozen,report)
    program=frozen["winning_program"]
    program_key="program:"+program["receipt_sha256"]
    train="train:"+frozen["source_training_sha256"]
    dev="dev:"+frozen["source_development_sha256"]
    nodes=[
        {"id":train,"type":"AUTHOR_CREATED_TYPED_SEMANTIC_GRAPH_PAIRS"},
        {"id":dev,"type":"AUTHOR_CREATED_MODEL_SELECTION_GRAPH_CONTRASTS"},
        {"id":program_key,"type":"DATA_ONLY_DERIVED_GRAPH_REWRITE_PROGRAM",
         "derived_transition_count":program["derived_transition_count"],
         "derived_relational_cue_count":program["derived_cue_count"],
         "new_ontology_not_discovered":True},
    ]
    tests=[]
    for group in packets:
        key="trial:"+group["packet_receipt_sha256"]
        tests.append(key)
        nodes.append({
            "id":key,"type":"AUTHOR_CREATED_POSTFREEZE_LANGUAGE_CHALLENGE",
            "family":group["family"],"case_count":group["count"],
            "human_language_independence_verified":False,
        })
    exact=report["combined"]["induced_graph_relations"]
    word=report["combined"]["word_bayes_same_training"]
    bigram=report["combined"]["word_bigram_bayes_same_training"]
    edges=[
        {
            "id":"derived:source-contrasts-to-graph-transformers",
            "type":"EXECUTED_TYPED_GRAPH_DELTA_INDUCTION",
            "tails":[train,dev],
            "heads":[program_key,
                     "capability:source_conditional_relation_rewrite_instances",
                     "frontier:infer_relation_types_not_given_by_author"],
            "graph_transition_operator_instances":program["derived_transition_count"],
            "surface_relation_cue_instances":program["derived_cue_count"],
            "finite_program_configs_tested":frozen["configurations_executed"],
            "generic_opcode_runtime_predefined":True,
            "semantic_relation_names_given_in_training_graphs":True,
        },
        {
            "id":"observed:graph-meaning-generalization-and-false-directive",
            "type":"MEASURED_SYNTHETIC_ACCURACY_AND_SCOPE_FAILURE",
            "tails":[train,dev,program_key,*tests],
            "heads":["outcome:correct_structured_graph_interpretations",
                     "outcome:false_directive_inference_risk",
                     "outcome:negation_and_quotation_scope_errors",
                     "frontier:infer_scope_priority_and_new_relations"],
            "exact_semantic_graph":exact["exact_semantic_graph"],
            "false_directive_clearances":exact["false_directive_clearance"],
            "wrong_decisive":exact["wrong_decisive"],
            "abstained":exact["abstained"],
            "word_bayes_same_training":word,
            "word_bigram_bayes_same_training":bigram,
            "source_world":"SAME_AUTHOR_GENERATED_GRAPHS_AND_LABELS",
            "truth_of_linguistic_intent_independently_authenticated":False,
            "test_cases_source_event_graph_preprovided":True,
            "observed_risk_requires_review_not_auto_admission":(
                exact["false_directive_clearance"]>0),
        },
    ]
    packet={
        "schema":SCHEMA,
        "source_program_receipt_sha256":frozen["receipt_sha256"],
        "source_trial_receipt_sha256":report["receipt_sha256"],
        "vertices":nodes,
        "hyperedges":edges,
        "review_priority":"DO_NOT_APPROVE_INTERPRETATIONS_AS_REAL_ACTIONS",
        "author_created_synthetic_language_not_independent_human_text":True,
        "no_private_user_messages_copied_into_public_repo":True,
        "genuine_new_mathematical_relation_primitives_verified":False,
        "data_only_new_graph_rewrite_instances_derived":True,
        "real_world_capability_edges_promoted":0,
        "real_world_authority":"NONE",
        "external_actions_executed":False,
    }
    packet["receipt_sha256"]=digest(packet)
    return packet


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--benchmark",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        out=build(json.loads(args.frozen.read_text()),
                  json.loads(args.benchmark.read_text()))
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
        evidence=out["hyperedges"][1]
        print(json.dumps({
            "schema":out["schema"],
            "induced_graph_transitions":out["hyperedges"][0][
                "graph_transition_operator_instances"],
            "induced_context_rules":out["hyperedges"][0][
                "surface_relation_cue_instances"],
            "correct_graphs":evidence["exact_semantic_graph"],
            "false_directive_interpretations":evidence["false_directive_clearances"],
            "wrong_decisive":evidence["wrong_decisive"],
            "receipt_sha256":out["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,benchmark.HOLD,induce.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
