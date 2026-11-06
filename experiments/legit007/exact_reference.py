"""LEGIT-007: independent exact classical Bayesian source+audit reference.

Does NOT import candidate router or its evidence scoring. Traverses copied
witnesses, reconstructs conditional odds and enumerates both audit outcomes.
Because both methods implement classical Bayes, they should TIE exactly.
"""
from __future__ import annotations

MISTAKE=1.0
ABSTAIN=.27

def reference(packet):
    by_id={node["id"]:node for node in packet["nodes"]}
    originals={}
    def ascend(key,active):
        if key in active:
            raise ValueError("Cyclic graph")
        row=by_id[key]
        if row["kind"]=="ROOT":
            return row
        if row["kind"]!="COPY":
            raise ValueError("Unresolved source")
        parent=ascend(row["parent"],active|{key})
        if parent["claim"]!=row["claim"]:
            raise ValueError("Changed copy")
        return parent
    for key in by_id:
        origin=ascend(key,set())
        old=originals.get(origin["origin"])
        if old is not None and (old["claim"],old["channel"])!=(
                origin["claim"],origin["channel"]):
            raise ValueError("Contradictory origin")
        originals[origin["origin"]]=origin
    cal={c["channel"]:(2+c["correct"])/(4+c["total"])
         for c in packet["calibration"]}
    odds=1.0
    for original in originals.values():
        r=cal[original["channel"]]
        odds *= (r/(1-r)) if original["claim"] else ((1-r)/r)
    p=odds/(1+odds)

    def stop(probability):
        candidates={"PREDICT_TRUE":1-probability,
                    "PREDICT_FALSE":probability,"ABSTAIN":ABSTAIN}
        order=("ABSTAIN","PREDICT_FALSE","PREDICT_TRUE")
        chosen=min(order,key=lambda name:(candidates[name],order.index(name)))
        return chosen,candidates[chosen]

    terminal,baseline=stop(p)
    proposals=[]
    for query in packet["audits"]:
        accuracy=query["accuracy"]
        p_y=p*accuracy+(1-p)*(1-accuracy)
        p_n=1-p_y
        new_yes=p*accuracy/p_y
        new_no=p*(1-accuracy)/p_n
        loss=query["cost"]+p_y*stop(new_yes)[1]+p_n*stop(new_no)[1]
        proposals.append({
            "id":query["id"],"total":loss,
            "outcomes":{True:(new_yes,stop(new_yes)[0]),
                        False:(new_no,stop(new_no)[0])},
        })
    best=min(proposals,key=lambda row:(row["total"],row["id"])) if proposals else None
    if best and best["total"]+1e-10<baseline:
        return {"action":"ASK_SYNTHETIC_AUDIT","audit":best["id"],
                "p_true":p,"terminal":terminal,"loss":best["total"],
                "outcomes":best["outcomes"]}
    return {"action":terminal,"audit":None,"p_true":p,
            "terminal":terminal,"loss":baseline,"outcomes":{}}
