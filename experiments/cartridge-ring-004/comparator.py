"""RING-004 common-world experiment and strong classical controls.

Real pinned original GEOM-013, THOUGHT-014 and REASON-006 methods all process
the SAME synthetic cases. Ground-truth labels remain outside the read-only
Docker sandbox. This is a deliberately authored small world: a demonstrated
dataflow, not broad generalization or proof of advantage over classical BFS.

Explicit user/maintainer approval is still required before any new code is
merged into other branches. This script never modifies GitHub or outside state.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'cartridge-ring-001'))

import fixtures
import triad

SCHEMA="motif.shared-evidence-benchmark.v1"
STAGES=("geometry.procedure-repair","thought.language-dev","reason.proof-objection")


class HOLD(ValueError):
    pass


def canonical_digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                              ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def check_native(public,native):
    if (not isinstance(native,dict) or native.get("schema")!="motif.shared-native-output.v1"
            or native.get("world")!="ONE_SHARED_AUTHORED_SYNTHETIC_EVIDENCE_PACKET"
            or native.get("public_digest_sha256")!=canonical_digest(public)
            or native.get("authority")!="NONE"
            or native.get("external_action_executed") is not False
            or native.get("language_model_calls")!=0
            or not isinstance(native.get("results"),list)):
        raise HOLD("Unbound, malformed, or overclaimed native evidence")
    rows=native["results"]
    if len(rows)!=len(public["cases"]) or [x["id"] for x in rows]!=[x["id"] for x in public["cases"]]:
        raise HOLD("Native result omitted, duplicated, or reordered common cases")
    for row in rows:
        if (row.get("native_source_types")!=[
            "GEOM-013.Revision.measure",
            "THOUGHT-014.LanguageSpace.explore",
            "REASON-006.run_council"]):
            raise HOLD("Expected original source-owned methods missing")
        if row["geometry"].get("learned_distinct_steps")!=2:
            raise HOLD("Original learned native geometry algorithm not applied")
        if (row["language"].get("pen_state")!="UNCHANGED"
                or row["geometry"]["raw"].get("authority")!="NONE"
                or row["geometry"]["repaired"].get("authority")!="NONE"):
            raise HOLD("Native source attempted unexpected authority")
        for key in ("raw","repaired"):
            claim=row["reason"][key]
            if claim.get("status")=="CERTIFIED_SYNTHETIC_GRAPH_DECISION":
                if claim.get("conclusion") not in (
                        "PROVED_REACHABLE","PROVED_UNREACHABLE","UNKNOWN"):
                    raise HOLD("Unexpected native proof status")
                if not isinstance(claim.get("source_revision"),str):
                    raise HOLD("Unbound native proof revision")
    return rows


def predictions(c,n):
    lang=n["language"]
    safe=lang["safe"]
    raw=n["geometry"]["raw"]["value"]
    fixed=n["geometry"]["repaired"]["value"]
    raw_reason=n["reason"]["raw"]["conclusion"]
    fixed_reason=n["reason"]["repaired"]["conclusion"]
    def valid(x):
        return x if x in ("PROVED_REACHABLE","PROVED_UNREACHABLE") else "HOLD"
    # Every ablation receives EXACTLY the same input case. A subset omits
    # its missing source-native method and is not allowed to borrow outputs
    # secretly from the full composition.
    return {
        "all_three_native": valid(fixed_reason) if safe else "HOLD",
        "reason_only_raw_witnesses":valid(raw_reason),
        "language_plus_reason_raw":valid(raw_reason) if safe else "HOLD",
        "geometry_plus_reason_no_language":valid(fixed_reason),
        "geometry_only_no_graph": (
            "PROVED_REACHABLE" if fixed is True else
            "PROVED_UNREACHABLE" if fixed is False else "HOLD"),
        "language_only_no_sensor_or_graph":"HOLD",
        # A deliberately stronger simple controller: a non-native direct graph
        # interpretation using the repaired measurement. This can TIE the
        # native council on this simple synthetic graph, and must be reported.
        "language_plus_geometry_classical_graph": (
            "HOLD" if not safe or fixed is None else
            "PROVED_REACHABLE" if c["gate_open"] and fixed else "PROVED_UNREACHABLE"),
        "classical_raw_record_parity": (
            "HOLD" if not safe or raw is None else
            "PROVED_REACHABLE" if c["gate_open"] and raw else "PROVED_UNREACHABLE"),
        "strong_classical_dedup_and_bfs": fixtures.strong_classical(c),
    }


def summarize(public,labels,native):
    if labels.get("schema")!=fixtures.LABEL_SCHEMA or labels.get(
            "public_digest_sha256")!=canonical_digest(public):
        raise HOLD("Source packet and kept-back ground truth do not match")
    by_label={x["id"]:x["expected"] for x in labels["labels"]}
    if len(by_label)!=len(public["cases"]):
        raise HOLD("Mismatched or duplicate ground-truth IDs")
    rows=check_native(public,native)
    control_names=None
    matrix={}
    per_case=[]
    for c,row in zip(public["cases"],rows):
        expected=by_label.get(c["id"])
        if expected not in ("HOLD","PROVED_REACHABLE","PROVED_UNREACHABLE"):
            raise HOLD("Invalid or absent hidden label")
        observed=predictions(c,row)
        if control_names is None:
            control_names=tuple(observed)
            matrix={key:{"correct":0,"wrong_decisive":0,"abstained":0,
                         "correct_hold":0,"coverage":0} for key in control_names}
        if set(observed)!=set(matrix):
            raise HOLD("Inconsistent ablation set")
        for name,pred in observed.items():
            bucket=matrix[name]
            if pred==expected:
                bucket["correct"]+=1
            elif pred=="HOLD":
                bucket["abstained"]+=1
            else:
                bucket["wrong_decisive"]+=1
            if expected=="HOLD" and pred=="HOLD":
                bucket["correct_hold"]+=1
            if pred!="HOLD":
                bucket["coverage"]+=1
        per_case.append({
            "case_id":c["id"], "hidden_expected_scoring_label":expected,
            "results":observed,
            "language_source_act":row["language"]["speech_act"],
            "geometry_raw":row["geometry"]["raw"]["status"],
            "geometry_repaired":row["geometry"]["repaired"]["status"],
            "native_reason_revision":row["reason"]["repaired"].get("source_revision"),
            "native_source_methods_on_same_case":row["native_source_types"],
        })
    if matrix["all_three_native"]["correct"]>matrix[
            "strong_classical_dedup_and_bfs"]["correct"]:
        raise HOLD("Unexpectedly exceeded verified strong classical control")
    result={
        "schema":SCHEMA,
        "status":"SOURCE_NATIVE_COMMON_WORLD_SYNTHETIC_EVALUATION",
        "source_packet_sha256":canonical_digest(public),
        "count":len(per_case),
        "method_source_pins":{x.id:x.commit for x in triad.ADAPTERS},
        "native_worker_is_a_reviewed_adapter_not_independent_source_evidence":True,
        "all_methods_process_identical_synthetic_case_ids":True,
        "native_methods_invoked":list(STAGES),
        "training_labels_not_passed_to_native_container":True,
        "synthetic_author_generated_fixture":True,
        "independent_human_labeled_real_data":False,
        "actual_independent_native_task_outputs_compared":True,
        "strong_classical_baseline":"dedup_by_declared_event_id_then_original_parity_then_BFS",
        "method_results":matrix,
        "per_case":per_case,
        "external_action_executed":False,
        "real_world_authority":False,
        "limitations":"Only an invented small closed graph and synthetic event identities; original reason proof is conditional on supplied measurement witness; no real-world sensor or source authenticity.",
    }
    result["receipt_sha256"]=canonical_digest(result)
    return result


def run(*,repo_root:Path,image="python:3.11-slim",seed=2026110615,count=32):
    if shutil.which("docker") is None:
        raise HOLD("Sandbox Docker required; never run native sources on host")
    public,labels=fixtures.generate(seed=seed,count=count)
    with tempfile.TemporaryDirectory(prefix="motif-shared-source-") as tmp:
        root=Path(tmp)
        root.chmod(0o755)
        for adapter,sub in (
            (triad.BY_ID["geometry.procedure-repair"],"geometry"),
            (triad.BY_ID["thought.language-dev"],"language"),
            (triad.BY_ID["reason.proof-objection"],"reason"),
        ):
            folder=root/sub
            folder.mkdir()
            triad._extract_experiments(adapter.commit,folder,repo_root=repo_root)
        harness=root/"harness"
        harness.mkdir()
        worker=Path(__file__).resolve().parent/"native_worker.py"
        shutil.copyfile(worker,harness/"native_worker.py")
        (root/"public.json").write_text(json.dumps(public,sort_keys=True)+"\n")
        # The labels stay as Python data inside this parent process. They are
        # never written to the mounted temp directory, including in artifacts.
        cmd=[
            "docker","run","--rm","--network","none","--read-only",
            "--cap-drop","ALL","--security-opt","no-new-privileges",
            "--pids-limit","96","--memory","768m","--cpus","1.0",
            "--user","65534:65534","--tmpfs","/tmp:rw,noexec,nosuid,size=64m",
            "--mount","type=bind,source="+str(root)+",target=/work,readonly",
            "--workdir","/work/harness",
            image,"python","-B","/work/harness/native_worker.py","/work/public.json",
        ]
        out=triad._run(cmd,cwd=repo_root,timeout=150,max_stdout=4_000_000)
        try:
            native=json.loads(out)
        except ValueError as exc:
            raise HOLD("Native common-world result was not JSON") from exc
    return summarize(public,labels,native)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument("--image",default="python:3.11-slim")
    p.add_argument("--seed",type=int,default=2026110615)
    p.add_argument("--count",type=int,default=32)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        r=run(repo_root=args.repo_root,image=args.image,
              seed=args.seed,count=args.count)
        output=json.dumps(r,sort_keys=True,indent=2)+"\n"
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(output,encoding="utf-8")
            print(json.dumps({"status":r["status"],"count":r["count"],
                              "methods":r["method_results"],
                              "receipt_sha256":r["receipt_sha256"]},sort_keys=True))
        else:
            print(output,end="")
    except (HOLD,triad.HOLD,ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc),
                          "no_sandbox_fallback":True}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
