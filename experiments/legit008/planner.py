"""LEGIT-008: exact bounded adaptive TWO-question reason planning.

The planner's new mathematical operation is a Bellman backup that decides
*after* observing the first hypothetical answer whether to ask the second.
It is a classical finite POMDP-style value-of-information calculation. It
can exceed the one-step planner's expected value, but CANNOT exceed optimal
classical multi-step reasoning with the same premises and horizon.

No experiment is dispatched. Outcomes are simulated ONLY by the evaluator.
"""
from __future__ import annotations

from pathlib import Path
import math
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit007"))
from provenance import posterior, terminal, audit_distribution, route as previous_route
from custody import guarded

class HOLD(ValueError):pass

def _audit_plan(p, audit, children):
    """Return exact expectation of one audit, with conditional policies."""
    path=[]
    future=0.
    for answer,prob,p_after in audit_distribution(p,audit["accuracy"]):
        child=children(answer,p_after)
        future+=prob*child["expected_risk"]
        path.append({
            "answer":answer,"answer_probability":prob,
            "posterior_true":p_after,"continuation":child})
    return {
        "action":"ASK_SYNTHETIC_AUDIT",
        "audit_id":audit["id"],
        "audit_cost":audit["cost"],
        "expected_risk":audit["cost"]+future,
        "branches":path,
        "issued":False,
    }

def plan(p, audits, horizon=2):
    """Exact unrounded finite search, deterministic tie-break and no repeats."""
    if type(horizon) is not int or not 0<=horizon<=2:
        raise HOLD("Unsupported planning horizon")
    if len(audits)>4:
        raise HOLD("Exact plan has a four-audit resource limit")
    if len({a["id"] for a in audits})!=len(audits):
        raise HOLD("Repeated audit labels")
    # Caller must first run provenance.validate on the packet.
    if not isinstance(p,(float,int)) or not math.isfinite(p) or not 0<=p<=1:
        raise HOLD("Invalid conditional posterior")
    for a in audits:
        if not 0.5<a["accuracy"]<1 or not 0<=a["cost"]<=1:
            raise HOLD("Invalid declared hypothetical instrument")
    nodes=0
    def recurse(probability,remaining,depth):
        nonlocal nodes
        nodes+=1
        name,cost=terminal(probability)
        best={"action":name,"audit_id":None,"expected_risk":cost,
              "posterior_true":probability,"branches":[],"issued":False}
        if depth==0 or not remaining:
            return best
        for i,item in enumerate(remaining):
            others=remaining[:i]+remaining[i+1:]
            choice=_audit_plan(probability,item,
                               lambda ans,new:recurse(new,others,depth-1))
            # Explicit prefer STOP at ties, lexical ID across equal asks.
            if choice["expected_risk"]+1e-12<best["expected_risk"]:
                best=choice
        return best
    tree=recurse(float(p),sorted(audits,key=lambda a:a["id"]),horizon)
    return {"tree":tree,"states_visited":nodes,
            "horizon":horizon,"method":"EXACT_FINITE_BELLMAN_BACKUP",
            "all_audits_unsent":True,"real_world_authority":False}

def decide(packet,pinned_manifest,depth=2):
    verify=guarded(packet,pinned_manifest)
    if verify["status"]!="PINNED_RECORD_INTEGRITY_ONLY":
        return {"status":"HOLD_UNTRUSTED_CUSTODY","custody":verify,
                "policy":None,"real_world_authority":False}
    fitted=posterior(packet)
    plan_receipt=plan(fitted["posterior"],packet["audits"],depth)
    legacy=previous_route(packet)
    if legacy["status"]=="HOLD_INPUT":
        raise AssertionError("Trusted packet cannot fail legacy validation")
    tree=plan_receipt["tree"]
    if depth==2 and tree["expected_risk"]>legacy["selected_expected_total_risk"]+1e-8:
        raise AssertionError("Exact two-step planner unexpectedly inferior to one-step")
    return {
        "schema":"motif.proof-carrying-meta-reasoner.v1",
        "status":"RESEARCH_PROPOSAL_ONLY",
        "custody":verify,
        "horizon":depth,
        "policy":tree,
        "conditional_source_posterior":fitted["posterior"],
        "baseline_one_step_risk":legacy["selected_expected_total_risk"],
        "expected_research_loss":tree["expected_risk"],
        "expected_risk_improvement_over_one_step":
            legacy["selected_expected_total_risk"]-tree["expected_risk"],
        "states_visited":plan_receipt["states_visited"],
        "claimed_novel_math":False,
        "audits_dispatched":0,
        "real_world_authority":False,
    }

def rollout(tree,answers,truth):
    """Evaluator-only: reveal hidden answers after entire policy is frozen."""
    total=0.
    path=[]
    used=set()
    current=tree
    while current["action"]=="ASK_SYNTHETIC_AUDIT":
        if current["audit_id"] in used:
            raise AssertionError("Audit repeated")
        used.add(current["audit_id"])
        total+=current["audit_cost"]
        answer=answers[current["audit_id"]]
        choice=next((c for c in current["branches"]
                     if c["answer"] is answer),None)
        if choice is None:
            raise AssertionError("Unknown future audit outcome")
        path.append({"audit_id":current["audit_id"],"simulated_answer":answer})
        current=choice["continuation"]
    terminal_name=current["action"]
    if terminal_name=="ABSTAIN":
        total+=.27
    elif terminal_name=="PREDICT_TRUE":
        total+=float(truth is False)
    elif terminal_name=="PREDICT_FALSE":
        total+=float(truth is True)
    else:
        raise AssertionError("Unknown terminal policy")
    return {"loss":total,"audits_simulated":len(used),
            "terminal_action":terminal_name,"path":path}
