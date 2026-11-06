"""LEGIT-008: verifiable *integrity relative to pinned* synthetic custody.

Unlike source-root strings from 007, each original observation is compared
with an independently supplied pinned content commitment. A new alleged
origin, edited root, altered calibration, or changed audit design HOLDs.

IMPORTANT: SHA-256 is integrity, not identity. The manifest/pins MUST have
arrived through a genuinely trusted channel for this to authenticate anything;
this experiment's pins are simply synthetic fixtures. No key management,
signatures, independent attestation or real-world trust is demonstrated.
"""
from __future__ import annotations

import hashlib
import json

SCHEMA="motif.synthetic-pinned-custody.v1"
class HOLD(ValueError): pass

def sha(item):
    return hashlib.sha256(json.dumps(
        item,sort_keys=True,separators=(",",":"),allow_nan=False,
        ensure_ascii=True).encode("utf-8")).hexdigest()

def _root_signature(node):
    return {"id":node["id"],"origin":node["origin"],
            "channel":node["channel"],"claim":node["claim"]}

def seal_simulated(packet):
    """Only a synthetic *evaluator* should create the outside pins."""
    from pathlib import Path
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"legit007"))
    from provenance import validate
    graph=validate(packet)
    roots={r["origin"]:sha(_root_signature(r)) for r in packet["nodes"]
           if r["kind"]=="ROOT"}
    return {
        "schema":SCHEMA,"scope":"SYNTHETIC_ONLY",
        "case_id":packet["id"],"root_commitments":roots,
        "calibration_sha256":sha(packet["calibration"]),
        "audit_design_sha256":sha(packet["audits"]),
        "trust_anchor":"EXTERNALLY_PINNED_IN_SIMULATOR_ONLY",
        "manifest_authenticated_by_real_key":False,
    }

def verify(packet, pins):
    if not isinstance(pins,dict) or set(pins)!={
            "schema","scope","case_id","root_commitments",
            "calibration_sha256","audit_design_sha256","trust_anchor",
            "manifest_authenticated_by_real_key"}:
        raise HOLD("Unknown custody manifest")
    if (pins["schema"]!=SCHEMA or pins["scope"]!="SYNTHETIC_ONLY" or
            pins["trust_anchor"]!="EXTERNALLY_PINNED_IN_SIMULATOR_ONLY" or
            pins["manifest_authenticated_by_real_key"] is not False or
            pins["case_id"]!=packet.get("id")):
        raise HOLD("Incorrect synthetic trust anchor or scope")
    from pathlib import Path
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"legit007"))
    from provenance import validate
    graph=validate(packet)
    observed={}
    for node in packet["nodes"]:
        if node["kind"]=="ROOT":
            key=node["origin"]
            commitment=sha(_root_signature(node))
            if key in observed and observed[key]!=commitment:
                raise HOLD("Same origin contains incompatible roots")
            observed[key]=commitment
    if observed!=pins["root_commitments"]:
        raise HOLD("Unpinned origin, altered statement, missing root or spoofed identity")
    if sha(packet["calibration"])!=pins["calibration_sha256"]:
        raise HOLD("Calibration differs from sealed source ledger")
    if sha(packet["audits"])!=pins["audit_design_sha256"]:
        raise HOLD("Audit design changed after source pin")
    return {
        "schema":"motif.synthetic-custody-verification.v1",
        "status":"PINNED_RECORD_INTEGRITY_ONLY",
        "case_id":packet["id"],
        "root_count":len(observed),"copy_nodes":len(packet["nodes"])-len(observed),
        "provenance_chain_nodes_checked":len(graph["resolved"]),
        "source_manifest_sha256":sha(pins),
        "source_integrity_relative_to_pins":True,
        "origin_identity_authenticated":False,
        "pinned_manifest_signature_verified":False,
        "real_world_authority":False,
    }

def guarded(packet,pins):
    try:
        return verify(packet,pins)
    except (HOLD,ValueError,TypeError,KeyError,OverflowError) as error:
        return {"status":"HOLD_UNTRUSTED_CUSTODY","reason":str(error),
                "suggested_investigation":"OBTAIN_INDEPENDENT_ATTESTATION_UNSENT",
                "investigation_issued":False,
                "real_world_authority":False}
