"""Independent exact two-stage classical reference for LEGIT-008.

Unlike the candidate Bellman recursion, this enumerates every depth-2
decision pattern explicitly: stop, ask A then stop or ask a DIFFERENT B
after each possible result. It imports LEGIT-007's separately written
root-evidence reference for the initial conditional posterior, never the
LEGIT-008 planner's probability or policy code.
"""
from __future__ import annotations

from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit007"))
from exact_reference import reference

def _stop(prob):
    choices=[("ABSTAIN",.27),("PREDICT_FALSE",prob),
             ("PREDICT_TRUE",1-prob)]
    return min(choices,key=lambda row:(row[1],choices.index(row)))

def _sense(prob,item):
    a=item["accuracy"]
    yes=prob*a+(1-prob)*(1-a)
    no=prob*(1-a)+(1-prob)*a
    return ((True,yes,prob*a/yes),
            (False,no,prob*(1-a)/no))

def _best_1(prob,options):
    action,risk=_stop(prob)
    best={"kind":action,"audit_id":None,"risk":risk,"children":{}}
    for item in sorted(options,key=lambda i:i["id"]):
        branches={}
        expected=item["cost"]
        for answer,weight,new in _sense(prob,item):
            action2,risk2=_stop(new)
            expected+=weight*risk2
            branches[answer]={"kind":action2,"audit_id":None,
                              "risk":risk2,"children":{}}
        if expected+1e-12<best["risk"]:
            best={"kind":"ASK_SYNTHETIC_AUDIT","audit_id":item["id"],
                  "risk":expected,"children":branches}
    return best

def exhaustive(packet):
    probability=reference(packet)["p_true"]
    instruments=packet["audits"]
    best_action,best_risk=_stop(probability)
    best={"kind":best_action,"audit_id":None,
          "risk":best_risk,"children":{}}
    # Exhaust every first hypothetical audit, allowing an independent
    # choice of continuation after both possible first answers.
    for first in sorted(instruments,key=lambda item:item["id"]):
        remainder=[item for item in instruments if item["id"]!=first["id"]]
        expected=first["cost"]
        children={}
        for answer,weight,new in _sense(probability,first):
            continuation=_best_1(new,remainder)
            expected+=weight*continuation["risk"]
            children[answer]=continuation
        if expected+1e-12<best["risk"]:
            best={"kind":"ASK_SYNTHETIC_AUDIT","audit_id":first["id"],
                  "risk":expected,"children":children}
    return {"p_true":probability,"expected_risk":best["risk"],
            "root":best,"method":"INDEPENDENT_CLASSICAL_POLICY_ENUMERATION",
            "audits_dispatched":0,"source_identity_authenticated":False}

def simulate(node,outcomes,truth,prices):
    used=set()
    policy=node
    cost=0.
    while policy["kind"]=="ASK_SYNTHETIC_AUDIT":
        name=policy["audit_id"]
        if name in used:raise AssertionError("Repeated audit")
        used.add(name)
        cost+=prices[name]
        policy=policy["children"][outcomes[name]]
    if policy["kind"]=="ABSTAIN":
        cost+=.27
    elif policy["kind"]=="PREDICT_TRUE":
        cost+=float(truth is False)
    elif policy["kind"]=="PREDICT_FALSE":
        cost+=float(truth is True)
    else:
        raise AssertionError("Unknown terminal")
    return cost,len(used)
