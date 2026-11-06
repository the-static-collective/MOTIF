"""Attach actual RING-002 native experiment receipts to RING-003's hypergraph.

A receipt witnesses that a pinned native *synthetic demonstration* was run in
its own experimental world. It is not evidence that the same reasoning method
is useful for every claimed use, nor that N methods interoperate in one world.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import hypergraph as hg
import triad


def _digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def validate_native(native):
    if not isinstance(native,dict) or native.get("schema") != triad.SCHEMA:
        raise hg.HOLD("Missing source-native triad receipt schema")
    digest=native.get("receipt_sha256")
    unsigned={k:v for k,v in native.items() if k!="receipt_sha256"}
    if type(digest) is not str or digest!=_digest(unsigned):
        raise hg.HOLD("Altered or missing native experiment receipt checksum")
    if (native.get("authority")!="NONE"
            or native.get("external_action_executed") is not False
            or native.get("cross_method_compatibility")!="UNPROVEN"
            or native.get("status")!="SOURCE_NATIVE_SYNTHETIC_TRIAL"
            or native.get("no_inference_transfer_across_distinct_synthetic_worlds") is not True):
        raise hg.HOLD("Unacceptable claimed authority or cross-world result")
    selected=native.get("selected")
    results=native.get("results")
    if (not isinstance(selected,list) or not isinstance(results,list)
            or len(selected)!=len(set(selected))
            or len(results)!=len(selected)):
        raise hg.HOLD("Misaligned or duplicate native method receipts")
    match=set(selected)
    if not match.issubset(set(triad.BY_ID)):
        raise hg.HOLD("Unknown installed native method")
    observed=set()
    nodes=[]
    hyperedges=[]
    for row in results:
        if not isinstance(row,dict):
            raise hg.HOLD("Malformed native result row")
        mid=row.get("adapter")
        if mid not in match or mid in observed:
            raise hg.HOLD("Duplicate or unselected native method result")
        adapter=triad.BY_ID[mid]
        if (row.get("source_commit")!=adapter.commit
                or row.get("artifact_kind")!=adapter.artifact_kind
                or row.get("source_native_demo") is not True
                or row.get("this_is_synthetic_not_shared_real_evidence") is not True
                or row.get("isolated_no_network_read_only") is not True
                or not isinstance(row.get("reduced_result"),dict)
                or not isinstance(row.get("native_receipt_sha256"),str)
                or len(row["native_receipt_sha256"])!=64):
            raise hg.HOLD("Pinned source or isolated benchmark evidence missing")
        observed.add(mid)
        eid="receipt."+mid
        nodes.append({"id":eid,"type":"NATIVE_SYNTHETIC_DEMO_EVIDENCE",
                      "claimed_source_commit":adapter.commit,
                      "native_receipt_sha256":row["native_receipt_sha256"],
                      "authentication":"NOT_EXTERNALLY_AUTHENTICATED",
                      "cross_world_validity":"NOT_DEMONSTRATED"})
        hyperedges.append({"id":"demonstration."+mid,
                           "tails":[eid],
                           "heads":[mid],
                           "kind":"CLAIMED_STANDALONE_SYNTHETIC_DEMONSTRATION",
                           "authority":"NONE"})
    if observed != match:
        raise hg.HOLD("Missing native source method receipt")
    report={
        "schema":"motif.hypergraph-native-evidence.v1",
        "method_receipt_source_sha256":digest,
        "evidence_vertices":sorted(nodes,key=lambda x:x["id"]),
        "evidence_hyperedges":sorted(hyperedges,key=lambda x:x["id"]),
        "admitted_new_affordance_edges":0,
        "cross_method_task_improvement_measured":False,
        "caveat":"Content hashes are not authenticated source identities or outcome truth",
        "external_action_executed":False,
        "authority":"NONE",
    }
    report["receipt_sha256"]=_digest(report)
    return report


def join(task: hg.Task,native,graph=None):
    graph=graph or hg.current_graph()
    selected=graph.solve(task)
    evidence=validate_native(native)
    return {
        "schema":"motif.hypergraph-combined-evaluation.v1",
        "route":selected,
        "native_method_evidence":evidence,
        "comparison":"ROUTING_ON_DECLARED_HYPOTHESES_NOT_EMPIRICAL_COMPARISON",
        "source_demo_worlds_are_distinct":True,
        "cross_method_interoperability":"UNPROVEN",
        "actual_shared_task_outcomes":None,
        "authority":"NONE",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--triad-receipt",required=True,type=Path)
    p.add_argument("--goal",required=True)
    p.add_argument("--value",type=int,default=12)
    p.add_argument("--budget",type=int,default=6)
    a=p.parse_args()
    data=json.loads(a.triad_receipt.read_text())
    task=hg.Task("operator-declared",((a.goal,a.value),),a.budget)
    print(json.dumps(join(task,data),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
