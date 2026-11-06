"""LEGIT-007: provenance-aware finite synthetic witness reasoning.

A report's upstream origin is more important than its number of reposts.
Distinct origins are assumed independent conditional on hidden truth.
Calibration, origin IDs, copied edges and assay accuracy are DECLARED
synthetic fixtures, never authenticated source truth or real-world authority.
Actions are research proposals only and are not executed.
"""
from __future__ import annotations
import hashlib
import json
import math
import re

SCHEMA = "motif.adversarial-witness.v1"
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,79}$")
PREDICTION_LOSS = 1.0
ABSTENTION_LOSS = .27
CALIBRATION_PRIOR = (2, 2)
BUDGET = 40000

class HOLD(ValueError):
    pass

def _strict(obj, required, label):
    if not isinstance(obj, dict) or set(obj) != set(required):
        raise HOLD("Unknown " + label + " contract")

def _id(x):
    return isinstance(x, str) and ID.fullmatch(x) is not None

def _integer(n, bottom, top):
    return type(n) is int and bottom <= n <= top

def _num(n):
    return type(n) in (int, float) and math.isfinite(n)

def digest(item):
    return hashlib.sha256(json.dumps(item, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()

def validate(packet):
    _strict(packet, ("schema", "id", "scope", "nodes", "calibration", "audits"), "packet")
    if packet["schema"] != SCHEMA or packet["scope"] != "SYNTHETIC_ONLY" or not _id(packet["id"]):
        raise HOLD("Unknown operational scope")
    if len(json.dumps(packet, allow_nan=False)) > BUDGET:
        raise HOLD("Packet too large")
    nodes = packet["nodes"]
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 48:
        raise HOLD("Expected bounded graph nodes")
    by_id = {}
    for node in nodes:
        _strict(node, ("id", "kind", "parent", "claim", "origin", "channel"), "node")
        if not _id(node["id"]) or node["id"] in by_id or type(node["claim"]) is not bool:
            raise HOLD("Ambiguous or non-Boolean report")
        if node["kind"] == "ROOT":
            if node["parent"] is not None or not _id(node["origin"]) or not _id(node["channel"]):
                raise HOLD("Malformed independently declared root")
        elif node["kind"] == "COPY":
            if not _id(node["parent"]) or node["origin"] is not None or node["channel"] is not None:
                raise HOLD("Copied report may not declare a new origin")
        elif node["kind"] == "LINEAGE_UNKNOWN":
            if node["parent"] is not None or node["origin"] is not None or node["channel"] is not None:
                raise HOLD("Unresolved lineage cannot claim independent source")
        else:
            raise HOLD("Unsupported synthesis or evidence transformation")
        by_id[node["id"]] = node
    calibration = packet["calibration"]
    if not isinstance(calibration, list) or not 1 <= len(calibration) <= 10:
        raise HOLD("Source accuracy requires explicit audit record")
    channel = {}
    for row in calibration:
        _strict(row, ("channel", "correct", "total", "provenance"), "calibration")
        if (not _id(row["channel"]) or row["channel"] in channel or
                not _integer(row["total"], 12, 100000) or
                not _integer(row["correct"], 0, row["total"]) or
                row["provenance"] != "SEPARATE_SYNTHETIC_ADJUDICATION"):
            raise HOLD("Missing admissible independent synthetic calibration")
        channel[row["channel"]] = row
    for node in nodes:
        if node["kind"] == "ROOT" and node["channel"] not in channel:
            raise HOLD("Uncalibrated origin")
    audits = packet["audits"]
    if not isinstance(audits, list) or len(audits) > 8:
        raise HOLD("Excessive or malformed audit menu")
    audit_ids = set()
    for audit in audits:
        _strict(audit, ("id", "accuracy", "cost", "provenance", "independent_of"), "audit")
        if (not _id(audit["id"]) or audit["id"] in audit_ids or
                not _num(audit["accuracy"]) or not .5 < audit["accuracy"] < 1 or
                not _num(audit["cost"]) or not 0 <= audit["cost"] <= 1 or
                audit["provenance"] != "SIMULATED_EXPERIMENT_DESIGN" or
                audit["independent_of"] != "ROOT_REPORTS_CONDITIONAL_ON_WORLD"):
            raise HOLD("Unknown or unjustified hypothetical audit")
        audit_ids.add(audit["id"])
    active = set()
    resolved = {}
    def root(nid):
        if nid in resolved:
            return resolved[nid]
        if nid in active:
            raise HOLD("Circular provenance: report copied itself")
        if nid not in by_id:
            raise HOLD("Copy points to unknown ancestor")
        active.add(nid)
        item = by_id[nid]
        if item["kind"] == "LINEAGE_UNKNOWN":
            raise HOLD("Report lineage unresolved: request provenance audit")
        if item["kind"] == "ROOT":
            leaf = nid
        else:
            leaf = root(item["parent"])
            if item["claim"] is not by_id[leaf]["claim"]:
                raise HOLD("Copied report edited its ancestor's claim")
        resolved[nid] = leaf
        active.remove(nid)
        return leaf
    for key in by_id:
        root(key)
    origins = {}
    for node in nodes:
        if node["kind"] != "ROOT":
            continue
        existing = origins.get(node["origin"])
        signature = (node["claim"], node["channel"])
        if existing is not None and existing != signature:
            raise HOLD("Equivocation by same declared upstream origin")
        origins[node["origin"]] = signature
    if not origins:
        raise HOLD("All reports without identifiable root")
    return {"by_id": by_id, "resolved": resolved,
            "origin_signature": origins, "calibration": channel}

def posterior(packet):
    v = validate(packet)
    logodds = 0.0
    contribution = []
    for origin, (claim, channel) in sorted(v["origin_signature"].items()):
        calibrated = v["calibration"][channel]
        r = (CALIBRATION_PRIOR[0] + calibrated["correct"]) / (
            sum(CALIBRATION_PRIOR) + calibrated["total"])
        evidence = (1 if claim else -1) * math.log(r / (1-r))
        logodds += evidence
        contribution.append({"origin":origin,"channel":channel,"claim":claim,
                             "reliability_mean":round(r,8),
                             "signed_log_odds":round(evidence,8)})
    p = 1 / (1 + math.exp(-max(-100, min(100,logodds))))
    v["posterior"] = p
    v["contributions"] = contribution
    v["echoes"] = len(packet["nodes"]) - len(v["origin_signature"])
    return v

def terminal(p):
    if not _num(p) or not 0 <= p <= 1:
        raise HOLD("Invalid conditional state")
    choices = [("ABSTAIN", ABSTENTION_LOSS),
               ("PREDICT_FALSE", PREDICTION_LOSS*p),
               ("PREDICT_TRUE", PREDICTION_LOSS*(1-p))]
    return min(choices, key=lambda a:(a[1], choices.index(a)))

def audit_distribution(p, accuracy):
    if not _num(p) or not 0 <= p <= 1 or not _num(accuracy) or not .5 < accuracy < 1:
        raise HOLD("Cannot model unknown audit likelihood")
    yes = p*accuracy + (1-p)*(1-accuracy)
    no = 1-yes
    p_yes = p*accuracy/yes if yes>0 else 0.0
    p_no = p*(1-accuracy)/no if no>0 else 0.0
    return ((True,yes,p_yes),(False,no,p_no))

def evaluate_audit(p, audit):
    distribution = audit_distribution(p, audit["accuracy"])
    expected = sum(prob*terminal(p_next)[1] for _,prob,p_next in distribution)
    return {
        "audit_id":audit["id"],
        "reported_accuracy_is_assumed_not_verified":True,
        "expected_terminal_risk_before_price":round(expected,9),
        "expected_total_risk":round(expected+audit["cost"],9),
        "cost":audit["cost"],
        "outcomes":[{"answer":ans,"probability":round(prob,9),
                     "updated_probability":round(p_next,9),
                     "terminal_action":terminal(p_next)[0]}
                    for ans,prob,p_next in distribution],
    }

def route(packet):
    try:
        fitted = posterior(packet)
    except (HOLD,ValueError,TypeError,OverflowError) as err:
        msg = str(err)
        investigation = ("VERIFY_UPSTREAM_LINEAGE_UNSENT" if
                         ("lineage" in msg.lower() or "ancestor" in msg.lower()
                          or "circular" in msg.lower() or "copy" in msg.lower()) else
                         "RECONCILE_OR_AUTHENTICATE_SOURCE_RECORDS_UNSENT")
        return {"schema":"motif.witness-receipt.v1",
                "status":"HOLD_INPUT","reason":msg,
                "suggested_investigation":investigation,
                "investigation_issued":False,
                "proposal":None,"world_actuated":False,
                "real_world_authority":False}
    p = fitted["posterior"]
    chosen, base_risk = terminal(p)
    audit_options = [evaluate_audit(p, a) for a in packet["audits"]]
    best = min(audit_options, key=lambda x:(x["expected_total_risk"],x["audit_id"])) if audit_options else None
    if best is not None and best["expected_total_risk"]+1e-10 < base_risk:
        proposal = {"kind":"ASK_SYNTHETIC_AUDIT_UNSENT",
                    "audit_id":best["audit_id"],
                    "possible_answers":best["outcomes"],"issued":False}
        status = "PROPOSE_AUDIT_HOLD"
        expected = best["expected_total_risk"]
    else:
        proposal = None
        status = "TERMINAL_RESEARCH_HOLD"
        expected = base_risk
    return {
        "schema":"motif.witness-receipt.v1",
        "status":status,"decision":("ASK_SYNTHETIC_AUDIT" if proposal else chosen),
        "proposal":proposal,
        "posterior_true_given_declared_calibration":round(p,9),
        "terminal_without_audit":chosen,
        "risk_of_no_action":round(base_risk,9),
        "selected_expected_total_risk":round(expected,9),
        "audit_options":audit_options,
        "distinct_declared_upstream_origins":len(fitted["origin_signature"]),
        "duplicate_or_forwarded_report_nodes":fitted["echoes"],
        "report_nodes":len(packet["nodes"]),
        "source_contributions":fitted["contributions"],
        "source_packet_sha256":digest(packet),
        "source_identity_cryptographically_authenticated":False,
        "conditional_independence_empirically_validated":False,
        "uncalibrated_real_world_trust":True,
        "world_actuated":False,"real_world_authority":False,
        "no_new_reasoning_laws_discovered":True,
    }
