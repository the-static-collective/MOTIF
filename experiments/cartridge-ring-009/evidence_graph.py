"""RING-009: measured hyperedges for generated semantic operators and tradeoffs.

The concrete experiment discovers executable relational *rule instances*
from source contrasts; it does not independently invent new Python-language
primitives. Evidence must make coverage loss, source-scoped gains, and errors
visible together. No automatically promoted method permissions or merges.
"""
from __future__ import annotations

from hashlib import sha256
import argparse
import json
from pathlib import Path

import benchmark,induce,search

SCHEMA="motif.ring009.measured-relation-invention-hypergraph.v1"

class HOLD(ValueError):
    pass


def digest(v):
    return induce.digest(v)


def validate(frozen,report):
    # Exact reproducibility of the source-induction AST, even when an
    # attacker regenerates the plain SHA256 content receipt.
    benchmark.verify_artifact(frozen)
    if (not isinstance(report,dict) or report.get("schema")!=benchmark.SCHEMA
            or report.get("receipt_sha256")!=digest({
                k:v for k,v in report.items() if k!="receipt_sha256"})
            or report.get("frozen_program_sha256")!=frozen["receipt_sha256"]
            or report.get("program_source_operator_sha256")!=frozen["program"][
                "receipt_sha256"]
            or report.get("authority")!="NONE"
            or report.get("external_actions_executed") is not False
            or report.get("new_executable_or_network_capabilities_admitted")!=0
            or report.get("general_language_understanding_verified") is not False):
        raise HOLD("Unbound or overclaimed source interpretation evidence")
    packets=report.get("test_packets")
    if not isinstance(packets,list) or len(packets)!=2:
        raise HOLD("Two separate source test packets required")
    identities=set()
    counts={}
    for packet in packets:
        sid=packet.get("source_sha256")
        if (type(sid) is not str or len(sid)!=64 or sid in identities
                or packet.get("test_labels_not_used_in_model_selection") is not True
                or packet.get("source_was_written_by_same_experimenter") is not True):
            raise HOLD("Duplicate/unproven source evidence")
        identities.add(sid)
        models=packet.get("models")
        expected={
            "induced_relational_operator",
            "ring008_feature_parser_same_training",
            "word_bayes_same_training",
            "ring008_original_source_training",
            "always_hold"}
        if not isinstance(models,dict) or set(models)!=expected:
            raise HOLD("Required strong baselines missing")
        for name,details in models.items():
            rows=details.get("per_case")
            values=details.get("metrics")
            if (not isinstance(rows,list) or len(rows)!=packet.get("case_count")
                    or not isinstance(values,dict)
                    or values.get("count")!=len(rows)
                    or sum(r["exact"] for r in rows)!=values["exact_frames"]
                    or sum(r["false_readonly"] for r in rows)!=values["unsafe_false_readonly"]
                    or sum(r["predicted_frame"] is not None for r in rows)!=values["decisive"]
                    or sum(r["predicted_frame"] is not None and not r["exact"]
                           for r in rows)!=values["wrong_decisive"]):
                raise HOLD("Source observed decision witnesses do not reconcile")
            totals=counts.setdefault(name,{k:0 for k in values})
            for k in totals:
                totals[k]+=values[k]
    if counts!=report.get("combined"):
        raise HOLD("Aggregated metrics disagree with source case evidence")
    return counts


def build(frozen,report):
    totals=validate(frozen,report)
    new=totals["induced_relational_operator"]
    same=totals["word_bayes_same_training"]
    other=totals["ring008_feature_parser_same_training"]
    n=sum(x["case_count"] for x in report["test_packets"])
    rules=frozen["program"]["discovered_relational_operators"]
    source_anchors=frozen["program"][
        "semantic_anchors_inferred_from_overlapping_utterances"]
    root="program:"+frozen["program"]["receipt_sha256"]
    tra="train:"+frozen["source_train_sha256"]
    dev="dev:"+frozen["source_dev_sha256"]
    trials=["test:"+x["source_sha256"] for x in report["test_packets"]]
    nodes=[
        {"id":tra,"type":"AUTHOR_TYPED_CONTRAST_EVIDENCE"},
        {"id":dev,"type":"AUTHOR_MODEL_SELECTION_CONTRAST_EVIDENCE"},
        {"id":root,"type":"GENERATED_RELATIONAL_OPERATOR_PROGRAM",
         "derived_rules":len(rules),"derived_event_heads":len(source_anchors),
         "built_from_fixed_ANTI_UNIFICATION_OPCODE_FAMILY":True},
    ]+[
        {"id":name,"type":"AUTHOR_CREATED_FROZEN_TEST_PACKET"}
        for name in trials
    ]
    edges=[
        {
            "id":"derived:opposite-act-pairs-to-relational-operators",
            "kind":"CONTRAST_INDUCED_EXECUTABLE_SEMANTIC_RELATION",
            "tails":[tra,dev],
            "heads":[root,"method:learned-ordered-cue-event-relations",
                     "question:discover-new-computational-primitives"],
            "source_pair_count":frozen["source_pair_count"],
            "source_dev_pair_count":frozen["source_dev_pair_count"],
            "candidate_derivations_executed":frozen[
                "candidate_derivations_executed"],
            "new_relational_operator_instances_created":len(rules),
            "new_base_computational_opcode_created":False,
        },
        {
            "id":"observed:conservative-relation-vs-same-training-baselines",
            "kind":"SYNTHETIC_SEMANTIC_PRECISION_COVERAGE_TENSION",
            "tails":[root,tra,dev,*trials],
            "heads":["outcome:precise-tested-meaning-hypotheses",
                     "outcome:many-legitimate-questions-are-unanswered",
                     "outcome:wrong-decisive-meaning-risk",
                     "frontier:compositional-scope-generalization"],
            "source_test_cases":n,
            "induced_program":new,
            "word_bayes_same_training":same,
            "ring008_feature_same_training":other,
            "decisive_precision_on_authored_data": (
                new["exact_frames"]/new["decisive"]
                if new["decisive"] else None),
            "induced_abstention_count":n-new["decisive"],
            "relative_to_word_bayes_exact_frames":new["exact_frames"]-same["exact_frames"],
            "relative_to_word_bayes_wrong_decisives": (
                new["wrong_decisive"]-same["wrong_decisive"]),
            "real_world_meaning_accuracy_proven":False,
            "overconfidence_to_preserve":new["wrong_decisive"]>0,
        },
    ]
    result={
        "schema":SCHEMA,
        "source_program_receipt_sha256":frozen["receipt_sha256"],
        "source_postfreeze_receipt_sha256":report["receipt_sha256"],
        "vertices":nodes,
        "hyperedges":edges,
        "learned_new_relational_rule_instances":len(rules),
        "invented_new_unrestricted_programming_primitives":False,
        "source_labels_independently_human_verified":False,
        "graph_reflects_source_scoped_tradeoffs_not_truth":True,
        "new_real_world_capability_edges_promoted":0,
        "new_executable_methods_installed":0,
        "external_actions_executed":False,
        "authority":"NONE",
    }
    result["receipt_sha256"]=digest(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frozen",type=Path,required=True)
    p.add_argument("--benchmark",type=Path,required=True)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        result=build(json.loads(args.frozen.read_text()),
                     json.loads(args.benchmark.read_text()))
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
        edge=result["hyperedges"][1]
        print(json.dumps({
            "schema":result["schema"],
            "induced_operator_instances":result["learned_new_relational_rule_instances"],
            "test_cases":edge["source_test_cases"],
            "exact":edge["induced_program"]["exact_frames"],
            "wrong_decisive":edge["induced_program"]["wrong_decisive"],
            "abstained":edge["induced_abstention_count"],
            "new_computational_primitives_invented":False,
            "receipt_sha256":result["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,benchmark.HOLD,induce.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
