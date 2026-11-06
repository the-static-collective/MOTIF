"""LEGIT-007 evaluator ONLY: seeded true worlds, dependent forwarded claims,
separate source calibration, and withheld test outcomes.

Public trial packets never contain hidden truth or simulated audit results.
Authorship is assistant-controlled; this is not independent blind research.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from random import Random

SCHEMA="motif.adversarial-witness.v1"
SEED="MOTIF-LEGIT007-20261106-source-epistemology-v1"
N=320
ACCURACY={"noisy":.57,"precise":.83,"contrarian":.31,"middling":.66}
AUDIT_MENU=(
    {"id":"cheap_sensor","accuracy":.72,"cost":.035,
     "provenance":"SIMULATED_EXPERIMENT_DESIGN",
     "independent_of":"ROOT_REPORTS_CONDITIONAL_ON_WORLD"},
    {"id":"deep_check","accuracy":.91,"cost":.12,
     "provenance":"SIMULATED_EXPERIMENT_DESIGN",
     "independent_of":"ROOT_REPORTS_CONDITIONAL_ON_WORLD"},
)
CALIBRATION_COUNTS={"noisy":70,"precise":70,"contrarian":70,"middling":70}

def seed(index,name):
    value=f"{SEED}:{index}:{name}"
    return int(sha256(value.encode()).hexdigest()[:16],16)

def calibration():
    rows=[]
    for name in sorted(ACCURACY):
        rng=Random(seed(-1,name))
        n=CALIBRATION_COUNTS[name]
        right=sum(rng.random()<ACCURACY[name] for _ in range(n))
        rows.append({"channel":name,"correct":right,"total":n,
                     "provenance":"SEPARATE_SYNTHETIC_ADJUDICATION"})
    return rows

@dataclass(frozen=True)
class Trial:
    public: dict
    truth: bool
    audit_outcomes: dict
    family: str

def trial(index):
    if type(index) is not int or not 0<=index<N:
        raise ValueError("Trial outside frozen range")
    rng=Random(seed(index,"world"))
    truth=rng.random()<.5
    family=("COPY_SWARM","DEEP_CHAIN","CONTRARIAN","SPARSE")[index%4]
    channels={
        "COPY_SWARM":("noisy","precise"),
        "DEEP_CHAIN":("noisy","precise","middling"),
        "CONTRARIAN":("contrarian","precise","noisy","middling"),
        "SPARSE":("middling","noisy"),
    }[family]
    nodes=[]
    for i,channel in enumerate(channels):
        correct=rng.random()<ACCURACY[channel]
        reported=truth if correct else not truth
        root_id=f"w{i}"
        nodes.append({"id":root_id,"kind":"ROOT","parent":None,
                      "claim":reported,"origin":f"origin_{i}","channel":channel})
        if family=="COPY_SWARM" and i==0:
            for j in range(1,9):
                nodes.append({"id":f"copy_{j}","kind":"COPY",
                              "parent":root_id,"claim":reported,
                              "origin":None,"channel":None})
        if family=="DEEP_CHAIN" and i==0:
            parent=root_id
            for j in range(1,7):
                nid=f"chain_{j}"
                nodes.append({"id":nid,"kind":"COPY","parent":parent,
                              "claim":reported,"origin":None,"channel":None})
                parent=nid
        if family=="CONTRARIAN" and i==0:
            for j in range(1,4):
                nodes.append({"id":f"forward_{j}","kind":"COPY",
                              "parent":root_id,"claim":reported,
                              "origin":None,"channel":None})
    rng.shuffle(nodes)
    audits={}
    for audit in AUDIT_MENU:
        local=Random(seed(index,audit["id"]))
        accurate=local.random()<audit["accuracy"]
        audits[audit["id"]]=truth if accurate else not truth
    public={"schema":SCHEMA,"id":f"Trial_{index:03d}",
            "scope":"SYNTHETIC_ONLY","nodes":nodes,
            "calibration":calibration(),"audits":list(AUDIT_MENU)}
    return Trial(public,truth,audits,family)

def demonstration():
    copies=[{"id":"p0","kind":"ROOT","parent":None,"claim":True,
             "origin":"campaign_root","channel":"noisy"}]
    copies += [{"id":f"p{i}","kind":"COPY","parent":f"p{i-1}",
                "claim":True,"origin":None,"channel":None}
               for i in range(1,9)]
    contrary=[{"id":"n0","kind":"ROOT","parent":None,"claim":False,
               "origin":"review_a","channel":"precise"},
              {"id":"n1","kind":"ROOT","parent":None,"claim":False,
               "origin":"review_b","channel":"middling"}]
    return {"schema":SCHEMA,"id":"NineVoicesOneOrigin",
            "scope":"SYNTHETIC_ONLY","nodes":copies+contrary,
            "calibration":calibration(),"audits":list(AUDIT_MENU)}
