"""RING-005 genuinely selective source-native worker for a *frozen* policy.

The **unlabeled** public cases and a pre-selected, restricted route manifest
are mounted into a no-network Docker container. The worker does not see labels
or training receipts. It only invokes the pinned original source methods
named by the route. Pure preflight/graph-cut paths call no native methods;
optional council proofs are computed only on required cases.

This is a research adapter for a toy synthetic graph, not an autonomous agent.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from time import perf_counter_ns

import native_worker as source_native

PUBLIC_SCHEMA="motif.shared-evidence-public.v1"
ROUTING_SCHEMA="motif.ring005.precommitted-routes.v1"
OUTPUT_SCHEMA="motif.ring005.selective-output.v1"
OPTIONS=frozenset({
    "PRECHECK_HOLD_NO_NATIVE",
    "STATIC_GATE_CUT_NO_NATIVE",
    "SOURCE_LANGUAGE_AND_RAW_MEASUREMENT",
    "SOURCE_LANGUAGE_AND_REPAIRED_MEASUREMENT",
    "SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL",
})
EFFECT=re.compile(r"\b(?:deploy|delete|execute|merge|email|send|contact|publish|dispatch|push|wire money|grant permission)\b",re.I)


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def context(case):
    # Independent fail-closed verification of the host's route manifest.
    if (not isinstance(case,dict)
            or set(case)!={"id","gate_open","utterance","selected_pair","records","scope"}
            or not isinstance(case["id"],str)
            or not re.fullmatch(r"heldout-[0-9]{3}",case["id"])
            or type(case["gate_open"]) is not bool
            or type(case["utterance"]) is not str
            or case["scope"]!="synthetic:observer-a@cut-12:decoder-A"
            or case["selected_pair"]!=["m-route-start","m-route-end"]):
        raise ValueError("Wrong bounded public world case")
    need_proof=int(case["id"][-3:])%7==0
    if EFFECT.search(case["utterance"]):
        return ("HOLD",need_proof)
    rows=case["records"]
    if rows is None:
        return ("HOLD",need_proof)
    if not isinstance(rows,list) or len(rows)>300:
        raise ValueError("Invalid trace size")
    seen={}
    duplicate=False
    invalid=False
    for r in rows:
        if (not isinstance(r,dict) or set(r)!={"tick","channel","event_id"}
                or type(r["tick"]) is not int or not 0<=r["tick"]<8
                or r["channel"] not in ("a","b","noise")):
            raise ValueError("Malformed event")
        if r["channel"] not in ("a","b"):
            continue
        if r["event_id"] is None:
            invalid=True
            continue
        if not isinstance(r["event_id"],str):
            raise ValueError("Malformed declared event ID")
        own=(r["channel"],r["tick"])
        if r["event_id"] in seen:
            if seen[r["event_id"]]!=own:
                invalid=True
            else:
                duplicate=True
        else:
            seen[r["event_id"]]=own
    if invalid:
        return ("HOLD",need_proof)
    if need_proof:
        return ("PROOF",True)
    if not case["gate_open"]:
        return ("CUT",False)
    return ("REPAIR" if duplicate else "RAW",False)


def validate_routes(public,manifest):
    if (not isinstance(public,dict) or public.get("schema")!=PUBLIC_SCHEMA
            or public.get("no_labels_inside_native_runner") is not True
            or not isinstance(public.get("cases"),list)
            or not 1<=len(public["cases"])<=48
            or not isinstance(manifest,dict)
            or manifest.get("schema")!=ROUTING_SCHEMA
            or manifest.get("public_digest_sha256")!=digest(public)
            or manifest.get("no_labels_in_route_manifest") is not True
            or manifest.get("authority")!="NONE"
            or manifest.get("receipt_sha256")!=digest({
                k:v for k,v in manifest.items() if k!="receipt_sha256"})):
        raise ValueError("Unbound or mutated precommitted routing plan")
    rows=manifest.get("routes")
    if not isinstance(rows,list) or len(rows)!=len(public["cases"]):
        raise ValueError("Route plan does not match all cases")
    seen=set()
    for case,row in zip(public["cases"],rows):
        if (not isinstance(row,dict) or row.get("id")!=case["id"]
                or row["id"] in seen or row.get("route") not in OPTIONS
                or type(row.get("requires_proof")) is not bool
                or type(row.get("context")) is not str):
            raise ValueError("Unknown, repeated, or out-of-order route")
        seen.add(row["id"])
        category,proof=context(case)
        if category!=row["context"] or proof!=row["requires_proof"]:
            raise ValueError("Host route context does not match public input")
        acceptable={
            "HOLD":("PRECHECK_HOLD_NO_NATIVE","SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL"),
            "CUT":("STATIC_GATE_CUT_NO_NATIVE","SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL"),
            "RAW":("SOURCE_LANGUAGE_AND_RAW_MEASUREMENT",
                   "SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL"),
            "REPAIR":("SOURCE_LANGUAGE_AND_REPAIRED_MEASUREMENT",
                      "SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL"),
            "PROOF":("SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL",),
        }
        if row["route"] not in acceptable[category]:
            raise ValueError("Policy chose a method incompatible with required evidence")
    return rows


def execute(public,manifest):
    assignments=validate_routes(public,manifest)
    # Mount is readonly and source-pinned; the existing 004 adapter performs
    # audited imports. The source modules are not changed, only invoked.
    (geom,RecordedCase,RecordedEvent,IdentifierAccess,LanguageSpace,
     TinyTextModel,orig_training,run_council,owner4)=source_native.bind_source_roots()
    tiny=TinyTextModel(orig_training)
    needs_geometry=any(row["route"] not in (
        "PRECHECK_HOLD_NO_NATIVE","STATIC_GATE_CUT_NO_NATIVE")
                       for row in assignments)
    if needs_geometry:
        active,_,_,_,_,_,repaired=geom.two_revisions()
        catalog={c.channel:c for c in geom.capabilities()}
        access=IdentifierAccess(geom.SCOPE,True,True,0.25)
        if not all(repaired.distinct):
            raise ValueError("Original frozen instrument failed deduplication")
    results=[]
    for case,row in zip(public["cases"],assignments):
        start=perf_counter_ns()
        route=row["route"]
        native_calls=[]
        proof=None
        label="HOLD"
        if route=="PRECHECK_HOLD_NO_NATIVE":
            label="HOLD"
        elif route=="STATIC_GATE_CUT_NO_NATIVE":
            label="PROVED_UNREACHABLE"
        else:
            engine=type("SharedSyntheticEngine",(),{})()
            engine.manifests={"m-route-start":object(),"m-route-end":object()}
            engine.input_digest=digest(case)
            utterance=LanguageSpace(engine).explore(
                case["utterance"],selected_pair=case["selected_pair"],model=tiny)
            native_calls.append("THOUGHT-014.LanguageSpace.explore")
            safe=(utterance["status"]=="TYPED_ONLY" and
                  utterance["speech_act"] in (
                      "EXPLORE_POSSIBILITY","CHALLENGE","COMPARE","INSPECT_EVIDENCE"))
            if not safe:
                label="HOLD"
            else:
                records=None if case["records"] is None else [
                    RecordedEvent(tick=r["tick"],channel=r["channel"],
                                  event_id=r["event_id"])
                    for r in case["records"]]
                # Sentinel required by a source data type but not consulted
                # by Revision.measure; this is NOT the held-out task answer.
                source_case=RecordedCase.make(
                    case["id"],("sprout","bud"),("sprout","branch"),
                    {"appearance":"same-bud","season":"synthetic-spring"},
                    False,records,"claimed:ring005-shared",geom.SCOPE)
                instrument=active if route=="SOURCE_LANGUAGE_AND_RAW_MEASUREMENT" else repaired
                measure=instrument.measure(source_case,catalog,geom.WINDOWS,
                                           geom.BUDGET,access)
                native_calls.append("GEOM-013.Revision.measure")
                bit=measure["value"]
                if bit is None:
                    label="HOLD"
                elif route=="SOURCE_LANGUAGE_GEOMETRY_AND_COUNCIL":
                    q=owner4.Inquiry(
                        ("S","A","T"),(("S","A"),("A","T"),("S","T")),
                        (("S","A","PRESENT" if case["gate_open"] else "ABSENT",
                          case["id"]+":gate"),
                         ("A","T","PRESENT" if bit else "ABSENT",
                          case["id"]+":sensor")),
                        ("S","T"),True)
                    council=run_council(q,name=case["id"],source=None)
                    native_calls.append("REASON-006.run_council")
                    if (council["external_actions"] is not False
                            or council["real_world_authority"] is not False):
                        raise ValueError("Original proof source violated no effects")
                    label=council["after"]
                    proof={"source_revision":council["source_revision"],
                           "certificate_present":bool(council["final_witness"]),
                           "ledger_entries":len(council["ledger"]),
                           "declared_synthetic_evidence":True}
                else:
                    # Narrow invented graph S→A→T: direct classical control.
                    # Not a generic replacement for source-native proof.
                    label=("PROVED_REACHABLE" if case["gate_open"] and bit
                           else "PROVED_UNREACHABLE")
        if label not in ("HOLD","PROVED_REACHABLE","PROVED_UNREACHABLE"):
            raise ValueError("Unrecognized, unsafe, or unresolved decision status")
        if row["requires_proof"] and row["context"]!="HOLD" and proof is None:
            raise ValueError("Explicit requested proof could not be produced")
        results.append({
            "id":case["id"],"context":row["context"],
            "selected_route":route,"decision":label,
            "source_method_invocations":native_calls,
            "source_method_call_count":len(native_calls),
            "proof":proof,
            "elapsed_ns_inside_one_container":perf_counter_ns()-start,
            "source_input_label_was_not_supplied":True,
        })
    return {
        "schema":OUTPUT_SCHEMA,
        "public_digest_sha256":digest(public),
        "policy_digest_sha256":manifest["policy_digest_sha256"],
        "route_manifest_sha256":manifest["receipt_sha256"],
        "results":results,
        "native_methods_available_from_original_pins":True,
        "labels_not_provided":True,
        "external_action_executed":False,
        "authority":"NONE",
    }


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: selective_worker.py <public-json> <routing-manifest-json>")
    pub=json.loads(Path(sys.argv[1]).read_text())
    plan=json.loads(Path(sys.argv[2]).read_text())
    print(json.dumps(execute(pub,plan),sort_keys=True))
