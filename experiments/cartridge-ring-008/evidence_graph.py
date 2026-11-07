"""RING-008: store program invention and FAILED transfer as typed hyperedges.

Key insight: a program was indeed automatically *assembled* from the
developer's small DSL and improved over an atomic seed on author-created
unseen constructions, but it ALSO made unsafe false-readonly predictions.
A measured success and a measured failure belong in the SAME source-bound
multi-head hyperedge. No permission, deployment or universal inference follows.
"""
from __future__ import annotations
from hashlib import sha256
import argparse
import json
from pathlib import Path

import engine, synthesizer

SCHEMA="motif.ring008.generated-semantic-program-hypergraph.v1"

class HOLD(ValueError):
    pass


def digest(data):
    return engine.digest(data)


def verify(artifact,bench):
    if (not isinstance(artifact,dict)
            or artifact.get("schema")!=synthesizer.SCHEMA
            or artifact.get("receipt_sha256")!=digest({
                k:v for k,v in artifact.items() if k!="receipt_sha256"})
            or artifact.get("tool_execution_authority")!="NONE"
            or artifact.get("heldout_challenge_module_imported") is not False
            or artifact.get("test_outcomes_consulted_during_search") is not False):
        raise HOLD("Malformed train-only algorithm generation receipt")
    spec=artifact.get("selected_program")
    engine.validate(spec)
    if (artifact.get("selected_program_sha256")!=digest(spec)
            or artifact.get("found_beyond_seed_set") is not True):
        raise HOLD("Generated solution did not actually move beyond atomic seeds")
    if (not isinstance(bench,dict)
            or bench.get("schema")!="motif.ring008.postfreeze-semantic-falsification.v1"
            or bench.get("receipt_sha256")!=digest({
                k:v for k,v in bench.items() if k!="receipt_sha256"})
            or bench.get("program_receipt_sha256")!=artifact["receipt_sha256"]
            or bench.get("program_ast")!=spec
            or bench.get("external_action_executed") is not False
            or bench.get("new_native_executable_admissions")!=0
            or bench.get("authority")!="NONE"):
        raise HOLD("Missing or mutated post-freeze method trial")
    packets=bench.get("test_packets")
    if not isinstance(packets,list) or len(packets)!=2:
        raise HOLD("Requires two independently seeded, author-created packets")
    seen=set()
    outcomes={}
    for p in packets:
        pid=p.get("heldout_source_packet_sha256")
        if type(pid) is not str or len(pid)!=64 or pid in seen:
            raise HOLD("Duplicate or missing new-world identity")
        seen.add(pid)
        if p.get("labels_not_used_for_program_search") is not True:
            raise HOLD("Test-label leakage or invalid selection source")
        systems=p.get("systems")
        if not isinstance(systems,dict) or set(systems)!={
            "synthesized","atomic_seed","old_single_path_grammar",
            "always_abstain","unsafe_permissive_foil"}:
            raise HOLD("Missing controls")
        for name,entry in systems.items():
            if not isinstance(entry,dict) or not isinstance(entry.get("per_case"),list):
                raise HOLD("Missing source evidence witnesses")
            rows=entry["per_case"]
            if len(rows)!=p["case_count"]:
                raise HOLD("Lost or fabricated cases")
            m=entry["metrics"]
            if (m["count"]!=len(rows)
                    or sum(x["exact"] for x in rows)!=m["exact_frames"]
                    or sum(x["false_readonly"] for x in rows)!=m[
                        "unsafe_false_readonly"]):
                raise HOLD("Wrong error count from source case evidence")
            if name not in outcomes:
                outcomes[name]={"exact_frames":0,"unsafe_false_readonly":0,
                                "wrong_decisive":0,"decisive":0}
            for k in outcomes[name]:
                outcomes[name][k]+=m[k]
    for name,metrics in outcomes.items():
        other=bench.get("combined",{}).get(name)
        if not isinstance(other,dict) or any(other.get(k)!=v
                                              for k,v in metrics.items()):
            raise HOLD("Aggregated decision metrics do not match witnesses")
    return outcomes


def build(artifact,bench):
    outcomes=verify(artifact,bench)
    auto=outcomes["synthesized"]
    seed=outcomes["atomic_seed"]
    diff={k:auto[k]-seed[k] for k in seed}
    if auto["unsafe_false_readonly"]<=0:
        risk="NONE_OBSERVED_AUTHOR_SYNTHETIC_ONLY"
    else:
        risk="UNSAFE_READONLY_CONFUSION_OBSERVED_AND_UNRESOLVED"
    train="train:"+artifact["source_train_sha256"]
    dev="dev:"+artifact["source_dev_sha256"]
    generated="program:"+artifact["selected_program_sha256"]
    nodes=[
        {"id":train,"kind":"AUTHOR_TRAINING_SEMANTIC_EXAMPLES"},
        {"id":dev,"kind":"AUTHOR_MODEL_SELECTION_SEMANTIC_EXAMPLES"},
        {"id":generated,"kind":"AUTO_COMPOSED_TYPED_SEMANTIC_PROGRAM",
         "program":artifact["selected_program"],
         "not_a_novel_universal_language_algorithm":True},
    ]
    tails=[generated,train,dev]
    for packet in bench["test_packets"]:
        ref="test:"+packet["heldout_source_packet_sha256"]
        nodes.append({"id":ref,"kind":"AUTHOR_SEPARATELY_FROZEN_TEST_EXAMPLES",
                      "case_count":packet["case_count"]})
        tails.append(ref)
    edges=[
        {
            "id":"observed:finite-synthesis-composition",
            "tails":[train,dev],
            "heads":[generated,"capability:typed_role_hypothesis",
                     "question:learning_new_semantic_operators"],
            "kind":"EXECUTED_TYPED_PROGRAM_SEARCH",
            "candidate_programs_executed":artifact["candidate_programs_tried"],
            "found_beyond_initial_programs":True,
            "search_space":"PREAUDITED_FINITE_DSL_NOT_NEW_PYTHON_OPERATORS",
        },
        {
            "id":"observed:semantic-composition-pros-cons",
            "tails":tails,
            "heads":["outcome:more_exact_typed_semantic_frames",
                     "outcome:unsafe_readonly_misclassification",
                     "outcome:unsupported_case_abstention",
                     "frontier:novel_operator_synthesis_and_authentic_meaning_evidence"],
            "kind":"CONDITIONAL_SYNTHETIC_LANGUAGE_GENERALIZATION_FALSIFIER",
            "synthesized_metrics":auto,
            "strongest_atomic_seed_metrics":seed,
            "synthesized_minus_atomic":diff,
            "unsafe_hypothesis_risk":risk,
            "source_world":"AUTHOR_CREATED_TEXT_NOT_INDEPENDENT_LANGUAGE",
            "source_case_labels_externally_verified":False,
            "measured_as_real_world_accuracy":False,
        },
    ]
    record={
        "schema":SCHEMA,
        "source_train_selection_receipt":artifact["receipt_sha256"],
        "source_frozen_test_receipt":bench["receipt_sha256"],
        "vertices":nodes,"hyperedges":edges,
        "true_general_language_invention_verified":False,
        "auto_composed_new_grammar_program_within_dsl":True,
        "source_falsification_preserved":True,
        "unsafe_false_clearances_are_not_suppressed":True,
        "real_world_algorithm_permission_promotions":0,
        "executable_code_self_rewriting":False,
        "external_action_executed":False,
        "authority":"NONE",
    }
    record["receipt_sha256"]=digest(record)
    return record


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artifact",required=True,type=Path)
    p.add_argument("--benchmark",required=True,type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        result=build(json.loads(args.artifact.read_text()),
                     json.loads(args.benchmark.read_text()))
        encoded=json.dumps(result,sort_keys=True,indent=2)+"\n"
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(encoded)
        print(json.dumps({
            "schema":result["schema"],
            "positive_transfer":result["hyperedges"][1][
                "synthesized_minus_atomic"]["exact_frames"],
            "unsafe_false_clearances":result["hyperedges"][1][
                "synthesized_metrics"]["unsafe_false_readonly"],
            "invention_claim_verified":result["true_general_language_invention_verified"],
            "receipt_sha256":result["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,engine.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc)}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
