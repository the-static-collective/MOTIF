"""RING-007 source-native three-way investigation worker (isolated Docker).

RING-006 quarantined every novel utterance. We instead inspect it with two
separate, bounded observations: a fixed grammatical/source-scope review and
the ORIGINAL pinned THOUGHT-014 model as a non-authoritative *raw-text
hypothesis*. Only reviewable read-only graph questions are translated to the
canonical query understood by the original native THOUGHT/GEOM/REASON code.

No external tool effect, source mutation or new branch execution is possible.
A native language model's guess cannot override the effect-risk review.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter_ns

import selective_worker as prior
import native_worker as native_source
import frames

SCHEMA="motif.ring007.investigated-native-output.v1"
MANIFEST="motif.ring007.reviewed-investigation-manifest.v1"
PROFILE="motif.ring006.frozen-language-profile.v1"

class HOLD(ValueError):
    pass


def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def verify(public,plan):
    if (not isinstance(public,dict) or public.get("schema")!=prior.PUBLIC_SCHEMA
            or public.get("no_labels_inside_native_runner") is not True
            or not isinstance(public.get("cases"),list)
            or not 1<=len(public["cases"])<=48
            or not isinstance(plan,dict) or plan.get("schema")!=MANIFEST
            or plan.get("public_digest_sha256")!=digest(public)
            or plan.get("authority")!="NONE"
            or plan.get("prepared_before_native_inference") is not True
            or plan.get("hidden_scoring_labels_included") is not False
            or plan.get("outside_effects_permitted") is not False
            or plan.get("source_method_registry_mutated") is not False
            or plan.get("selected_strategy") not in ("TRIAGE","BLANKET")
            or plan.get("receipt_sha256")!=digest({
                k:v for k,v in plan.items() if k!="receipt_sha256"})):
        raise HOLD("Invalid or changed source-native investigation manifest")
    profile=plan.get("frozen_language_profile")
    if (not isinstance(profile,dict) or profile.get("schema")!=PROFILE
            or profile.get("receipt_sha256")!=plan.get("original_profile_receipt_sha256")
            or profile.get("receipt_sha256")!=digest({
                k:v for k,v in profile.items() if k!="receipt_sha256"})
            or profile.get("eligible_action")!="ABSTAIN_ONLY_NOT_AUTO_CORRECT"
            or profile.get("no_new_execution_authority") is not True
            or profile.get("frozen_policy_sha256")!=plan.get(
                "frozen_policy_receipt_sha256")):
        raise HOLD("Unbound source-only training-language profile")
    allowed=profile.get("exact_public_training_utterances")
    if (not isinstance(allowed,list) or not 1<=len(allowed)<=100
            or allowed!=sorted(set(allowed))):
        raise HOLD("Wrong training language roster")
    rows=plan.get("routes")
    if not isinstance(rows,list) or len(rows)!=len(public["cases"]):
        raise HOLD("Missing or reordered source method choices")
    permitted=frozenset(prior.OPTIONS)
    seen=set()
    for case,row in zip(public["cases"],rows):
        source_context,proof=prior.context(case)
        review=frames.review(case["utterance"])
        if (not isinstance(row,dict) or row.get("id")!=case["id"]
                or row["id"] in seen
                or row.get("original_input_sha256")!=review["input_sha256"]
                or row.get("review")!=review
                or row.get("original_context")!=source_context
                or row.get("requires_proof")!=proof
                or row.get("source_graph_ids_unmodified") is not True
                or row.get("no_implicit_runtime_authority") is not True):
            raise HOLD("Source case or evidence analysis altered")
        seen.add(row["id"])
        novel=case["utterance"] not in allowed
        if review["verdict"]=="BLOCK":
            expected="BLOCK"
        elif source_context=="HOLD":
            expected="PRECHECK_HOLD"
        elif not novel:
            expected="FAMILIAR"
        elif plan["selected_strategy"]=="TRIAGE" and review["verdict"]=="EXPLORE":
            expected="INVESTIGATE"
        else:
            expected="UNCERTAIN"
        if row.get("kind")!=expected:
            raise HOLD("Novel language requires independent review before a route")
        if expected=="INVESTIGATE":
            if (row.get("canonical_utterance")!=frames.CANONICAL
                    or row.get("source_route") not in permitted):
                raise HOLD("Missing reviewed limited canonical query")
        elif expected=="FAMILIAR":
            if (row.get("canonical_utterance") is not None
                    or row.get("source_route") not in permitted):
                raise HOLD("Familiar source method provenance missing")
        elif row.get("source_route") is not None or row.get("canonical_utterance") is not None:
            raise HOLD("Unrecognized/risky utterance cannot obtain an executable route")
    return rows


def execute(public,plan):
    rows=verify(public,plan)
    admitted=[]
    admitted_routes=[]
    raw_probes={}
    raw_probe_time={}
    inspected_ids=set()
    for case,row in zip(public["cases"],rows):
        if row["kind"] in ("FAMILIAR","INVESTIGATE"):
            native_case=dict(case)
            if row["kind"]=="INVESTIGATE":
                native_case["utterance"]=frames.CANONICAL
            # We are *not* replacing the underlying source graph, trace,
            # manifestation IDs or channel events, only the bounded language
            # hypothesis for the selected same-world read-only inquiry.
            admitted.append(native_case)
            admitted_routes.append({
                "id":case["id"],
                "context":row["original_context"],
                "route":row["source_route"],
                "requires_proof":row["requires_proof"],
            })
            if row["kind"]=="INVESTIGATE":
                inspected_ids.add(case["id"])
    # Every admitted original route is rechecked by the audited prior worker.
    # The raw-text THOUGHT-014 probe is additional PENCIL-only evidence.
    if inspected_ids:
        (geom,Rec,Ev,Access,LanguageSpace,TinyTextModel,
         original_training,run_council,owner4)=native_source.bind_source_roots()
        model=TinyTextModel(original_training)
        for case in public["cases"]:
            if case["id"] not in inspected_ids:
                continue
            start=perf_counter_ns()
            engine=type("StrictSourceOnlyGraph",(),{})()
            engine.manifests={"m-route-start":object(),"m-route-end":object()}
            engine.input_digest=digest(case)
            utterance=LanguageSpace(engine).explore(
                case["utterance"],selected_pair=case["selected_pair"],model=model)
            if (utterance.get("pen_state")!="UNCHANGED"
                    or utterance.get("external_authority")!="NONE"
                    or utterance.get("selected_manifestations") is None):
                raise HOLD("Original THOUGHT-014 proposal sought external authority")
            raw_probe_time[case["id"]]=perf_counter_ns()-start
            raw_probes[case["id"]]={
                "source_class":utterance["source_class"],
                "original_speech_act":utterance["speech_act"],
                "original_interpretation_status":utterance["status"],
                "model_consulted":utterance["model_consulted"],
                "model_accepted_as_hypothesis":utterance["model_accepted_as_hypothesis"],
                "model_guess_is_not_authorization":True,
                "input_sha256":frames.review(case["utterance"])["input_sha256"],
            }
    source_results={}
    if admitted:
        subset=dict(public)
        subset["cases"]=admitted
        native_manifest={
            "schema":prior.ROUTING_SCHEMA,
            "public_digest_sha256":digest(subset),
            "policy_digest_sha256":plan["frozen_policy_receipt_sha256"],
            "routes":admitted_routes,
            "no_labels_in_route_manifest":True,
            "precommitted_before_any_native_outcomes":True,
            "authority":"NONE",
        }
        native_manifest["receipt_sha256"]=digest(native_manifest)
        native=prior.execute(subset,native_manifest)
        source_results={r["id"]:r for r in native["results"]}
    outputs=[]
    for case,row in zip(public["cases"],rows):
        if row["kind"] in ("FAMILIAR","INVESTIGATE"):
            result=dict(source_results[case["id"]])
            if row["kind"]=="INVESTIGATE":
                result["original_raw_language_hypothesis"]=raw_probes[case["id"]]
                result["reviewed_canonical_utterance"]=frames.CANONICAL
                result["original_phrase_preserved_sha256"]=row["original_input_sha256"]
                result["selected_route"]="INVESTIGATE_SCOPED_CANONICAL__"+row["source_route"]
                result["source_method_invocations"]=[
                    "THOUGHT-014.LanguageSpace.explore(raw_hypothesis)",
                    *result["source_method_invocations"]]
                result["source_method_call_count"]+=1
                result["elapsed_ns_inside_one_container"]+=raw_probe_time[case["id"]]
                result["context"]="INVESTIGATE"
        else:
            result={
                "id":case["id"],"context":row["kind"],
                "selected_route":row["kind"]+"_NO_NATIVE",
                "decision":"HOLD",
                "source_method_invocations":[],
                "source_method_call_count":0,
                "proof":None,"elapsed_ns_inside_one_container":0,
                "source_input_label_was_not_supplied":True,
                "unresolved_review_reason":row["reason"],
            }
        result["source_input_label_was_not_supplied"]=True
        outputs.append(result)
    return {
        "schema":SCHEMA,
        "public_digest_sha256":digest(public),
        "manifest_sha256":plan["receipt_sha256"],
        "frozen_policy_sha256":plan["frozen_policy_receipt_sha256"],
        "source_profile_sha256":plan["original_profile_receipt_sha256"],
        "strategy_sha256":plan["strategy_receipt_sha256"],
        "results":outputs,
        "novel_investigations":len(inspected_ids),
        "unreviewed_or_effectful_no_native_count":sum(
            row["kind"] in ("BLOCK","UNCERTAIN","PRECHECK_HOLD") for row in rows),
        "canonicalization_does_not_prove_open_domain_semantics":True,
        "all_original_source_commits_unchanged":True,
        "hidden_labels_not_provided":True,
        "external_action_executed":False,"authority":"NONE",
    }


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: review_worker.py PUBLIC_JSON ROUTE_MANIFEST_JSON")
    packet=json.loads(Path(sys.argv[1]).read_text())
    routes=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(execute(packet,routes),sort_keys=True))
