"""RING-005: close source discovery -> trial -> feedback -> selective execution.

A train-only policy uses two RING-004 native scored packets; distinct new
seeds are NEVER used to select or tune its initial route set. New public input
is routed before native methods run. The source native worker selectively
invokes the original pinned implementations inside a no-network Docker.

Untrusted real-world source evidence, arbitrary tool execution and automatic
code promotion remain disabled. Cost units are separate from measured timings.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-004"))
import comparator, fixtures, feedback
import policy

SCHEMA="motif.ring005.adaptive-routing-trial.v1"
ROUTING_SCHEMA="motif.ring005.precommitted-routes.v1"

class HOLD(ValueError):
    pass


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def manifest_for(frozen,public):
    policy.validate_policy(frozen)
    if public.get("schema")!=fixtures.SCHEMA:
        raise HOLD("Wrong unseen public source packet")
    rows=[]
    for case in public["cases"]:
        chosen=policy.route(frozen,case)
        rows.append({"id":case["id"],"context":chosen["context"],
                     "route":chosen["route"],
                     "requires_proof":chosen["requires_proof"]})
    manifest={
        "schema":ROUTING_SCHEMA,
        "public_digest_sha256":digest(public),
        "policy_digest_sha256":frozen["receipt_sha256"],
        "routes":rows,
        "no_labels_in_route_manifest":True,
        "precommitted_before_any_native_outcomes":True,
        "authority":"NONE",
    }
    manifest["receipt_sha256"]=digest(manifest)
    return manifest


def execute_selective(frozen,public,*,repo_root:Path,image="python:3.11-slim"):
    if shutil.which("docker") is None:
        raise HOLD("Docker required for source-native selective execution")
    manifest=manifest_for(frozen,public)
    with tempfile.TemporaryDirectory(prefix="motif-ring005-") as td:
        root=Path(td)
        root.chmod(0o755)
        for mid,sub in (
            ("geometry.procedure-repair","geometry"),
            ("thought.language-dev","language"),
            ("reason.proof-objection","reason"),
        ):
            destination=root/sub
            destination.mkdir()
            comparator.triad._extract_experiments(
                comparator.triad.BY_ID[mid].commit,destination,repo_root=repo_root)
        harness=root/"harness"
        harness.mkdir()
        shutil.copyfile(HERE/"selective_worker.py",harness/"selective_worker.py")
        shutil.copyfile(HERE.parent/"cartridge-ring-004"/"native_worker.py",
                        harness/"native_worker.py")
        (root/"public.json").write_text(json.dumps(public,sort_keys=True)+"\n")
        (root/"routes.json").write_text(json.dumps(manifest,sort_keys=True)+"\n")
        # NOTE: labels, original RING-004 scored reports, and training policy
        # are NEVER mounted into the native execution container.
        cmd=[
            "docker","run","--rm","--network","none","--read-only",
            "--cap-drop","ALL","--security-opt","no-new-privileges",
            "--pids-limit","96","--memory","768m","--cpus","1.0",
            "--user","65534:65534","--tmpfs","/tmp:rw,noexec,nosuid,size=64m",
            "--mount","type=bind,source="+str(root)+",target=/work,readonly",
            "--workdir","/work/harness",image,"python","-B",
            "/work/harness/selective_worker.py","/work/public.json","/work/routes.json",
        ]
        raw=comparator.triad._run(cmd,cwd=repo_root,timeout=150,
                                  max_stdout=4_000_000)
        try:
            native=json.loads(raw)
        except ValueError as e:
            raise HOLD("Native source worker produced invalid JSON") from e
    check_execution(frozen,public,manifest,native)
    return manifest,native


def check_execution(frozen,public,manifest,native):
    if (not isinstance(native,dict)
            or native.get("schema")!="motif.ring005.selective-output.v1"
            or native.get("public_digest_sha256")!=digest(public)
            or native.get("route_manifest_sha256")!=manifest["receipt_sha256"]
            or native.get("policy_digest_sha256")!=frozen["receipt_sha256"]
            or native.get("authority")!="NONE"
            or native.get("external_action_executed") is not False
            or native.get("labels_not_provided") is not True
            or not isinstance(native.get("results"),list)
            or len(native["results"])!=len(public["cases"])):
        raise HOLD("Unbound, missing, or over-authorized source-native output")
    counts={
        "PRECHECK_HOLD_NO_NATIVE":0,
        "STATIC_GATE_CUT_NO_NATIVE":0,
        "SOURCE_LANGUAGE_AND_RAW_MEASUREMENT":2,
        "SOURCE_LANGUAGE_AND_REPAIRED_MEASUREMENT":2,
        "SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL":3,
    }
    for case,planned,actual in zip(public["cases"],manifest["routes"],native["results"]):
        if (actual.get("id")!=case["id"]
                or actual.get("context")!=planned["context"]
                or actual.get("selected_route")!=planned["route"]
                or actual.get("decision") not in policy.GOOD
                or actual.get("source_input_label_was_not_supplied") is not True
                or type(actual.get("source_method_call_count")) is not int
                or not isinstance(actual.get("source_method_invocations"),list)
                or actual["source_method_call_count"]!=len(actual["source_method_invocations"])
                or actual["source_method_call_count"]>counts[planned["route"]]):
            raise HOLD("Source-native worker call trace violates chosen route")
        expected_names={
            "PRECHECK_HOLD_NO_NATIVE":[],
            "STATIC_GATE_CUT_NO_NATIVE":[],
            "SOURCE_LANGUAGE_AND_RAW_MEASUREMENT":[
                "THOUGHT-014.LanguageSpace.explore","GEOM-013.Revision.measure"],
            "SOURCE_LANGUAGE_AND_REPAIRED_MEASUREMENT":[
                "THOUGHT-014.LanguageSpace.explore","GEOM-013.Revision.measure"],
            "SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL":[
                "THOUGHT-014.LanguageSpace.explore","GEOM-013.Revision.measure",
                "REASON-006.run_council"],
        }[planned["route"]]
        actual_names=actual["source_method_invocations"]
        if actual_names != expected_names[:len(actual_names)]:
            raise HOLD("Unselected or reordered source-owned method invoked")
        if (planned["requires_proof"] and planned["context"]!="HOLD"
                and (actual.get("proof") is None
                     or "REASON-006.run_council" not in actual_names)):
            raise HOLD("Explicit source-owned proof requirement not met")
    return True


def score(frozen,public,hidden,manifest,native,full):
    if hidden.get("schema")!=fixtures.LABEL_SCHEMA or hidden.get(
            "public_digest_sha256")!=digest(public):
        raise HOLD("Hidden labels do not match evaluated public packet")
    if full.get("source_packet_sha256")!=digest(public):
        raise HOLD("Source-native full baseline not from the same cases")
    feedback.validate(full)
    check_execution(frozen,public,manifest,native)
    expected={x["id"]:x["expected"] for x in hidden["labels"]}
    if len(expected)!=len(public["cases"]):
        raise HOLD("Repeated or missing source-label IDs")
    totals={"correct":0,"wrong_decisive":0,"abstained":0,
            "native_source_method_calls":0,"real_measured_case_ns":0}
    by_context={}
    comparisons=[]
    for case,row,full_row in zip(public["cases"],native["results"],full["per_case"]):
        name=case["id"]
        truth=expected.get(name)
        pred=row["decision"]
        if truth not in policy.GOOD or full_row["case_id"]!=name:
            raise HOLD("Missing label or different full-native comparison case")
        context=row["context"]
        statistics=by_context.setdefault(context,{
            "correct":0,"wrong_decisive":0,"tested":0,
            "native_calls":0,"routes":{}})
        statistics["tested"]+=1
        statistics["routes"][row["selected_route"]]=(
            statistics["routes"].get(row["selected_route"],0)+1)
        if pred==truth:
            totals["correct"]+=1
            statistics["correct"]+=1
        elif pred=="HOLD":
            totals["abstained"]+=1
        else:
            totals["wrong_decisive"]+=1
            statistics["wrong_decisive"]+=1
        totals["native_source_method_calls"]+=row["source_method_call_count"]
        statistics["native_calls"]+=row["source_method_call_count"]
        totals["real_measured_case_ns"]+=row["elapsed_ns_inside_one_container"]
        comparisons.append({
            "id":name,"context":context,"route":row["selected_route"],
            "decision":pred,"label":truth,
            "correct":pred==truth,
            "full_native_correct":full_row["results"]["all_three_native"]==truth,
            "strong_classical_correct":
                full_row["results"]["strong_classical_dedup_and_bfs"]==truth,
            "source_calls":row["source_method_call_count"],
            "source_proof_attached":row.get("proof") is not None,
        })
    result={
        "schema":"motif.ring005.separate-heldout-evaluation.v1",
        "frozen_policy_receipt_sha256":frozen["receipt_sha256"],
        "public_source_sha256":digest(public),
        "route_manifest_sha256":manifest["receipt_sha256"],
        "native_worker_claimed_receipt_sha256":digest(native),
        "source_pins":frozen["source_pins"],
        "count":len(public["cases"]),
        "totals":totals,
        "by_context":by_context,
        "full_native_control_correct":full["method_results"]["all_three_native"]["correct"],
        "strong_classical_control_correct":full[
            "method_results"]["strong_classical_dedup_and_bfs"]["correct"],
        "reference_full_native_proxy_calls_if_three_per_case":3*len(public["cases"]),
        "source_only_measured_call_reduction_not_runtime_speedup":True,
        "elapsed_ns_has_no_controlled_full_native_latency_comparator":True,
        "per_case":comparisons,
        "source_method_invocations_were_selected_before_inference":True,
        "separate_heldout_labels_not_mounted_into_execution":True,
        "real_world_generalization":"UNTESTED",
        "authority":"NONE",
    }
    result["receipt_sha256"]=digest(result)
    return result


def revise(frozen,evaluation):
    """Feedback may demote failed shortcuts; it may NOT add more authority.

    A zero-error evaluation yields an unchanged executable policy with a
    separate review record, not an unjustified promotion of source methods.
    """
    policy.validate_policy(frozen)
    if (evaluation.get("schema")!="motif.ring005.separate-heldout-evaluation.v1"
            or evaluation.get("frozen_policy_receipt_sha256")!=frozen["receipt_sha256"]
            or evaluation.get("receipt_sha256")!=digest({
                k:v for k,v in evaluation.items() if k!="receipt_sha256"})):
        raise HOLD("Evaluation not bound to this previously frozen policy")
    evidence={}
    for row in evaluation["per_case"]:
        bucket=evidence.setdefault(row["context"],{"tested":0,"incorrect":0})
        bucket["tested"]+=1
        bucket["incorrect"]+=int(not row["correct"])
    successor=deepcopy(frozen)
    demoted=[]
    for category,data in evidence.items():
        if data["incorrect"]>0 and category in successor["context_routes"]:
            if successor["context_routes"][category]!=policy.METHODS["PROOF"]:
                successor["context_routes"][category]=policy.METHODS["PROOF"]
                successor["context_training"][category]["candidate_accepted"]=False
                successor["context_training"][category][
                    "frozen_route"]=policy.METHODS["PROOF"]
                demoted.append(category)
    successor["predecessor_policy_sha256"]=frozen["receipt_sha256"]
    successor["evaluated_packet_sha256"]=evaluation["public_source_sha256"]
    successor["revision_status"]="DEMOTED_AFTER_MEASURED_ERROR" if demoted else "NO_CHANGE_NO_MEASURED_ERROR"
    successor["demoted_contexts"]=sorted(demoted)
    successor["receipt_sha256"]=digest({k:v for k,v in successor.items()
                                       if k!="receipt_sha256"})
    policy.validate_policy(successor)
    return successor


def training_replays(*,repo_root:Path,train_seeds=(2026110615,2026110616),
                     count=32,image="python:3.11-slim"):
    if len(set(train_seeds))!=len(train_seeds):
        raise HOLD("Duplicate training seed")
    pairs=[]
    for seed in train_seeds:
        public,_=fixtures.generate(seed=seed,count=count)
        report=comparator.run(repo_root=repo_root,seed=seed,count=count,image=image)
        pairs.append((public,report))
    return pairs


def experiment(*,repo_root:Path,train_seeds=(2026110615,2026110616),
               heldout_seeds=(2026110617,2026110618),count=32,
               image="python:3.11-slim"):
    if (len(train_seeds)!=2 or len(heldout_seeds)!=2
            or len(set(train_seeds+heldout_seeds))!=4):
        raise HOLD("2 disjoint train seeds, 2 disjoint heldout seeds required")
    trained=training_replays(repo_root=repo_root,train_seeds=train_seeds,
                             count=count,image=image)
    original=policy.learn(trained)
    evaluations=[]
    live=original
    for i,seed in enumerate(heldout_seeds):
        public,hidden=fixtures.generate(seed=seed,count=count)
        plan,native=execute_selective(live,public,repo_root=repo_root,image=image)
        full=comparator.run(repo_root=repo_root,seed=seed,count=count,image=image)
        evaluation=score(live,public,hidden,plan,native,full)
        evaluations.append(evaluation)
        if i==0:
            live=revise(live,evaluation)
    result={
        "schema":SCHEMA,
        "status":"BOUND_SAME_WORLD_SELECTIVE_NATIVE_ROUTE_FEEDBACK_LOOP",
        "training_seeds":list(train_seeds),
        "heldout_seeds":list(heldout_seeds),
        "training_cases":sum(x["count"] for _,x in trained),
        "heldout_cases":sum(x["count"] for x in evaluations),
        "initial_policy":original,
        "after_first_feedback_policy":live,
        "evals":evaluations,
        "measured_total_native_calls_on_heldouts":sum(x["totals"]["native_source_method_calls"]
                                                    for x in evaluations),
        "declared_three_per_case_full_native_budget_proxy":sum(
            3*x["count"] for x in evaluations),
        "no_real_world_accuracy_or_speed_claim":True,
        "not_an_unrestricted_self_modifier":True,
        "external_action_executed":False,"authority":"NONE",
    }
    result["receipt_sha256"]=digest(result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root",type=Path,default=HERE.parents[1])
    p.add_argument("--count",type=int,default=32)
    p.add_argument("--image",default="python:3.11-slim")
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        r=experiment(repo_root=args.repo_root,count=args.count,image=args.image)
        data=json.dumps(r,indent=2,sort_keys=True)+"\n"
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(data,encoding="utf-8")
            print(json.dumps({
                "status":r["status"],
                "trained":r["training_cases"],
                "heldout":r["heldout_cases"],
                "native_calls":r["measured_total_native_calls_on_heldouts"],
                "proxy_all_three":r["declared_three_per_case_full_native_budget_proxy"],
                "correct_by_heldout":[x["totals"]["correct"] for x in r["evals"]],
                "classical_by_heldout":[x["strong_classical_control_correct"]
                                       for x in r["evals"]],
                "review":r["after_first_feedback_policy"]["revision_status"],
                "receipt_sha256":r["receipt_sha256"],
            },sort_keys=True))
        else:
            print(data,end="")
    except (HOLD,policy.HOLD,comparator.HOLD,
            comparator.triad.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc),
                          "no_native_execution_fallback":True}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
