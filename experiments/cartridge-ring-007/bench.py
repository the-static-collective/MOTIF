"""RING-007: measure recovery without repeating RING-006 unsafe approvals.

Three way finite state:
  RECOGNIZED  → existing selective source-owned routing
  INVESTIGATE → exact scoped text review + original THOUGHT-014 raw *hypothesis*
                 + canonical graph source methods, never external actions
  UNRESOLVED  → abstain with a source-preserved question

Freeze reviewed strategy on the *previous* 006 red-team error packet. Test on
a different seed of the old phrase family AND an additional author-created
phrase family that was not in the arbitration training corpus.

Does not invent an English interpretation, install arbitrary Git branches,
train a generative model, or authenticate events beyond synthetic fixture IDs.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-006"))
import challenge, breaker, sentinel
sys.path.insert(0,str(HERE.parent/"cartridge-ring-005"))
import adaptive, policy
import arbitration,frames,manifest,challenge_v2

SCHEMA="motif.ring007.safe-investigation-benchmark.v1"

class HOLD(ValueError):
    pass


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,
                             separators=(",",":"),allow_nan=False).encode()).hexdigest()


def validate_source_output(public,plan,native):
    if (not isinstance(native,dict) or native.get("schema")!=
            "motif.ring007.investigated-native-output.v1"
            or native.get("public_digest_sha256")!=digest(public)
            or native.get("manifest_sha256")!=plan["receipt_sha256"]
            or native.get("frozen_policy_sha256")!=plan["frozen_policy_receipt_sha256"]
            or native.get("source_profile_sha256")!=plan["original_profile_receipt_sha256"]
            or native.get("strategy_sha256")!=plan["strategy_receipt_sha256"]
            or native.get("hidden_labels_not_provided") is not True
            or native.get("external_action_executed") is not False
            or native.get("authority")!="NONE"
            or not isinstance(native.get("results"),list)
            or len(native["results"])!=len(public["cases"])):
        raise HOLD("Missing, altered or unauthorized native investigation output")
    cnt=0
    for case,row,actual in zip(public["cases"],plan["routes"],native["results"]):
        if (not isinstance(actual,dict)
                or actual.get("id")!=case["id"]
                or actual.get("decision") not in policy.GOOD
                or actual.get("source_input_label_was_not_supplied") is not True
                or type(actual.get("source_method_call_count")) is not int
                or not isinstance(actual.get("source_method_invocations"),list)
                or len(actual["source_method_invocations"])!=actual[
                    "source_method_call_count"]
                or type(actual.get("elapsed_ns_inside_one_container")) is not int):
            raise HOLD("Malformed native method source receipt")
        if row["kind"]=="INVESTIGATE":
            cnt+=1
            if (not actual.get("selected_route","").startswith(
                    "INVESTIGATE_SCOPED_CANONICAL__")
                    or actual.get("reviewed_canonical_utterance")!=frames.CANONICAL
                    or actual.get("original_phrase_preserved_sha256")!=row[
                        "original_input_sha256"]
                    or actual["source_method_invocations"][0]!=
                    "THOUGHT-014.LanguageSpace.explore(raw_hypothesis)"
                    or actual.get("original_raw_language_hypothesis",{}).get(
                        "model_guess_is_not_authorization") is not True):
                raise HOLD("Original language hypothesis or canonical source witness missing")
        elif row["kind"] in ("BLOCK","UNCERTAIN","PRECHECK_HOLD"):
            if (actual["decision"]!="HOLD"
                    or actual["source_method_call_count"]!=0
                    or actual.get("proof") is not None):
                raise HOLD("Unreviewed/unsafe input executed a source-native method")
        if (row["requires_proof"] and row["kind"] in ("FAMILIAR","INVESTIGATE")
                and row["original_context"]=="PROOF"
                and actual.get("proof") is None):
            raise HOLD("Required source-owned proof missing")
    if cnt!=native.get("novel_investigations"):
        raise HOLD("Native investigation count does not match manifest")
    return True


def execute(frozen,profile,decision,public,*,repo_root:Path,image="python:3.11-slim"):
    if shutil.which("docker") is None:
        raise HOLD("Docker required; no host fallback for source execution")
    plan=manifest.make(frozen,profile,decision,public)
    with tempfile.TemporaryDirectory(prefix="motif-investigate-") as td:
        root=Path(td)
        root.chmod(0o755)
        for mid,name in (
            ("geometry.procedure-repair","geometry"),
            ("thought.language-dev","language"),
            ("reason.proof-objection","reason"),
        ):
            target=root/name
            target.mkdir()
            adaptive.comparator.triad._extract_experiments(
                adaptive.comparator.triad.BY_ID[mid].commit,
                target,repo_root=repo_root)
        harness=root/"harness"
        harness.mkdir()
        for path in (
            HERE/"frames.py",
            HERE/"review_worker.py",
            HERE.parent/"cartridge-ring-005"/"selective_worker.py",
            HERE.parent/"cartridge-ring-004"/"native_worker.py",
        ):
            shutil.copyfile(path,harness/path.name)
        (root/"public.json").write_text(json.dumps(public,sort_keys=True)+"\n")
        (root/"routes.json").write_text(json.dumps(plan,sort_keys=True)+"\n")
        # No hidden label, earlier native result, human annotation or training
        # scored data is included in the read-only Docker mount.
        cmd=[
            "docker","run","--rm","--network","none","--read-only",
            "--cap-drop","ALL","--security-opt","no-new-privileges",
            "--pids-limit","96","--memory","768m","--cpus","1.0",
            "--user","65534:65534","--tmpfs","/tmp:rw,noexec,nosuid,size=64m",
            "--mount","type=bind,source="+str(root)+",target=/work,readonly",
            "--workdir","/work/harness",
            image,"python","-B","/work/harness/review_worker.py",
            "/work/public.json","/work/routes.json",
        ]
        raw=adaptive.comparator.triad._run(cmd,cwd=repo_root,
                                             timeout=150,max_stdout=4_000_000)
        try:
            native=json.loads(raw)
        except ValueError as exc:
            raise HOLD("Native source review result was not JSON") from exc
    validate_source_output(public,plan,native)
    return plan,native


def evaluate(*,repo_root:Path,count=32,image="python:3.11-slim"):
    # Historical 005 source-native successes, followed by one RING-006
    # observed failure packet. No alternate phrase family labels used here.
    training=adaptive.training_replays(
        repo_root=repo_root,train_seeds=(2026110615,2026110616),
        count=count,image=image)
    frozen=policy.learn(training)
    profile=sentinel.train_profile(frozen,training)
    old_pub,old_truth=challenge.generate(2026110621,count=count)
    _,old_native=adaptive.execute_selective(
        frozen,old_pub,repo_root=repo_root,image=image)
    decision=arbitration.learn(frozen,profile,old_pub,old_truth,old_native)
    scores=[]
    for family,seed,creator in (
        ("RING006_SAME_PHRASE_FAMILY_NEW_EVIDENCE",2026110622,challenge.generate),
        ("RING007_ALTERNATE_AUTHOR_PHRASE_FAMILY",2026110723,challenge_v2.generate),
    ):
        public,hidden=creator(seed,count=count)
        # Separate source-native comparative executions on exactly same new
        # evidence; all labels stay in this controller until after execution.
        _,unguarded=adaptive.execute_selective(
            frozen,public,repo_root=repo_root,image=image)
        _,blanket=breaker.run_guarded(
            frozen,profile,public,repo_root=repo_root,image=image)
        plan,reviewed=execute(
            frozen,profile,decision,public,repo_root=repo_root,image=image)
        baseline,_=breaker.inspect_shift(public,hidden,unguarded)
        oldguard,_=breaker.inspect_shift(public,hidden,blanket)
        newscore,details=breaker.inspect_shift(public,hidden,reviewed)
        examined={
            "family":family,"seed":seed,
            "public_source_packet_sha256":digest(public),
            "precommitted_route_sha256":plan["receipt_sha256"],
            "expected_labels_were_not_mounted":True,
            "old_unguarded":baseline,
            "blanket_novelty_guard":oldguard,
            "reviewed_investigation":newscore,
            "investigation_source_native_calls":sum(r[
                "source_method_call_count"] for r in reviewed["results"]
                if r["context"]=="INVESTIGATE"),
            "native_original_language_hypotheses":reviewed["novel_investigations"],
            "native_case_witnesses":details,
            "source_native_review_and_canonicalization_are_separate_stages":True,
        }
        scores.append(examined)
    report={
        "schema":SCHEMA,
        "status":"HISTORICAL_ERROR_TRAINED_THREE_WAY_REVIEW_EVALUATED_ON_NEW_SOURCE_CASES",
        "frozen_policy":frozen["receipt_sha256"],
        "original_source_pins":frozen["source_pins"],
        "historical_training_cases":sum(x["count"] for _,x in training),
        "historical_failure_cases":len(old_pub["cases"]),
        "historical_failure_unsafe_decisive":decision[
            "original_native_decisive_unsafe_count"],
        "selected_investigation_strategy":decision,
        "unseen_families":scores,
        "no_external_effects":True,
        "not_a_general_semantic_classifier":True,
        "newly_installed_arbitrary_branch_methods":0,
        "synthetic_hidden_labels_are_author_defined":True,
        "can_preserve_unresolved_questions_without_guessing":True,
        "full_source_native_methods_are_not_allowed_to_override_risk_gate":True,
        "authority":"NONE",
    }
    report["receipt_sha256"]=digest(report)
    return report


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root",type=Path,default=HERE.parents[1])
    p.add_argument("--image",default="python:3.11-slim")
    p.add_argument("--count",type=int,default=32)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    try:
        result=evaluate(repo_root=args.repo_root,image=args.image,count=args.count)
        txt=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if args.out:
            args.out.parent.mkdir(parents=True,exist_ok=True)
            args.out.write_text(txt)
        print(json.dumps({
            "status":result["status"],
            "selected":result["selected_investigation_strategy"]["selected"],
            "historical_unsafe":result["historical_failure_unsafe_decisive"],
            "families":[{
                "family":x["family"],
                "unguarded_unsafe":x["old_unguarded"][
                    "unsafe_or_invalid_decisive_approvals"],
                "blanket_unsafe":x["blanket_novelty_guard"][
                    "unsafe_or_invalid_decisive_approvals"],
                "investigative_unsafe":x["reviewed_investigation"][
                    "unsafe_or_invalid_decisive_approvals"],
                "blanket_benign_coverage":x["blanket_novelty_guard"][
                    "safe_positive_decisive_coverage"],
                "investigative_benign_coverage":x["reviewed_investigation"][
                    "safe_positive_decisive_coverage"],
                "novel_source_probes":x["native_original_language_hypotheses"],
            } for x in result["unseen_families"]],
            "receipt_sha256":result["receipt_sha256"],
        },sort_keys=True))
    except (HOLD,arbitration.HOLD,manifest.HOLD,frames.ValueError
            if hasattr(frames,"ValueError") else ValueError,
            breaker.HOLD,adaptive.HOLD,policy.HOLD,
            adaptive.comparator.HOLD,adaptive.comparator.triad.HOLD,
            ValueError) as exc:
        print(json.dumps({"status":"HOLD","reason":str(exc),
                          "no_unreviewed_source_execution":True}))
        raise SystemExit(2)


if __name__=="__main__":
    main()
