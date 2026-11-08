"""RING-012: calibrate when to WIDEN, not when to pronounce a single truth.

Train native RING-011 binder + two same-source classical methods on its
original authored synthetic training contrast. Examine RING-011's *separate*
development contrast ONLY to choose conservatism / set size tradeoffs.
Freeze the ambiguity policy before importing RING-012's multi-truth world.

Importing this module never consults RING-012 world.py test labels.
The resulting interpretation model is open-world even when a *concrete*
candidate set has one member. Confidence is not independent corroboration.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import lattice
import corpus,binder,benchmark,search

SCHEMA="motif.ring012.calibrated-open-lattice.v1"


def flatten_observation(source):
    return [(c["text"],c["observed_event"],c["carrier"],
             c["semantic_graph"]) for c in corpus.flatten(source)]


def calibration_metrics(source,policy,examples):
    out={
        "examples":0,"all_admissible_readings_retained":0,
        "excluded_readings":0,"concrete_worlds_sum":0,
        "multi_world_outputs":0,"unresolved":0,
        "wrong_exclusive_root_request":0,"carrier_changes":0,
    }
    for text,event,carrier,truth in examples:
        result=lattice.combine(text,event,carrier,source,policy)
        actual={lattice.digest(x) for x in result["supported_worlds"]}
        reference=lattice.digest(truth)
        out["examples"]+=1
        out["all_admissible_readings_retained"]+=int(reference in actual)
        out["excluded_readings"]+=int(reference not in actual)
        out["concrete_worlds_sum"]+=len(actual)
        out["multi_world_outputs"]+=int(len(actual)>1)
        out["unresolved"]+=int(len(actual)==0)
        out["wrong_exclusive_root_request"]+=int(
            len(actual)==1
            and lattice.corpus.graph_map(result["supported_worlds"][0])[
                ("EVENT","REQUESTED_BY_ROOT")] is True
            and lattice.corpus.graph_map(truth)[
                ("EVENT","REQUESTED_BY_ROOT")] is False)
        out["carrier_changes"]+=int(any(
            lattice.corpus.graph_map(x)[("DOCUMENT","CARRIER")]!=carrier
            for x in result["supported_worlds"]))
    out["mean_concrete_world_count"]=round(
        out["concrete_worlds_sum"]/max(1,out["examples"]),4)
    return out


def candidate(source,threshold,novelty,widen):
    artifact={
        "schema":SCHEMA,
        "source_train_sha256":source.train_sha256,
        "derived_program_sha256":source.program_sha256,
        "source_vocabulary":list(source.lexicon),
        "params":{
            "vote_threshold":threshold,
            "novelty_threshold":novelty,
            "widen_on_disagreement":widen,
        },
        "all_method_claims_correlated":True,
        "open_world_always":True,
        "outside_effects_forbidden":True,
        "explicit_source_graph_ontology":True,
        "source_train_dev_only_used_for_calibration":True,
        "calibration_is_not_truth_or_independent_validation":True,
        "unmodeled_perspective_is_always_retained":True,
        "authority":"NONE",
    }
    artifact["receipt_sha256"]=lattice.digest(artifact)
    return artifact


def calibrate():
    # The original RING-011 authored source is carried through completely
    # rather than creating fresh "helpful" labels after seeing the test.
    frozen=search.run()
    train,program=benchmark.verify_frozen(frozen)
    dev=corpus.generate("dev",seed=2026111102,rounds=5)
    source=lattice.Sources(train,program)
    examples=flatten_observation(dev)
    scored=[]
    for threshold,novelty,widen in itertools.product(
        lattice.THRESHOLDS,lattice.NOVELTY_THRESHOLDS,(False,True)
    ):
        policy=candidate(source,threshold,novelty,widen)
        observed=calibration_metrics(source,policy,examples)
        scored.append({"policy":policy,"metrics":observed})
    # We explicitly demand ≥95% synthetic dev inclusion *or* choose the
    # most inclusive alternative. Within eligible calibrated strategies,
    # prefer smaller candidate sets but penalize falsely single root
    # directives. This is a source-chosen utility function, not an
    # independently calibrated probability statement.
    eligible=[x for x in scored if x["metrics"][
        "all_admissible_readings_retained"]>=0.95*len(examples)]
    if not eligible:
        eligible=scored
    selected=min(eligible,key=lambda x:(
        x["metrics"]["wrong_exclusive_root_request"]*50
        +x["metrics"]["excluded_readings"]*100
        +x["metrics"]["mean_concrete_world_count"],
        -x["metrics"]["multi_world_outputs"],
        x["policy"]["params"]["vote_threshold"],
        x["policy"]["params"]["novelty_threshold"],
        x["policy"]["params"]["widen_on_disagreement"],
    ))
    report=selected["policy"]
    # Frozen report itself binds development selection metrics, source
    # identities, and all candidate configurations. Never include test data.
    report.pop("receipt_sha256")
    report["source_011_frozen_receipt_sha256"]=frozen["receipt_sha256"]
    report["original_dev_source_sha256"]=dev["receipt_sha256"]
    report["calibration_candidates_executed"]=len(scored)
    report["selection_metrics_on_development_only"]=selected["metrics"]
    report["calibration_excluded_readings"]=[
        {"params":s["policy"]["params"],
         "excluded":s["metrics"]["excluded_readings"],
         "mean_worlds":s["metrics"]["mean_concrete_world_count"],
         "wrong_exclusive_root_request":s["metrics"]["wrong_exclusive_root_request"]}
        for s in scored
    ]
    report["novel_world_module_imported_during_selection"]=False
    report["test_meanings_consulted_to_select_policy"]=False
    report["receipt_sha256"]=lattice.digest(report)
    lattice.validate_policy(report)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    doc=calibrate()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(doc,sort_keys=True,indent=2)+"\n")
    print(json.dumps({
        "status":"FROZEN_OPEN_WORLD_POLICY",
        "candidates":doc["calibration_candidates_executed"],
        "params":doc["params"],
        "dev_metrics":doc["selection_metrics_on_development_only"],
        "source_011_frozen":doc["source_011_frozen_receipt_sha256"],
        "receipt_sha256":doc["receipt_sha256"],
    },sort_keys=True))


if __name__=="__main__":
    main()
