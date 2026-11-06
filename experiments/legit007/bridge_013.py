"""LEGIT-007: regression crosswire to actual MOTIF-013 witness likelihood.

Checks shared finite conditional-independence assumptions on declared unique
origins, not an independently sourced benchmark or new model.
"""
from __future__ import annotations

from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"013"))
from witness_model import _witness_likelihood

from provenance import posterior

def compare_013(packet):
    fitted=posterior(packet)
    refs=fitted["origin_signature"]
    cal=fitted["calibration"]
    claims=[]
    reliability={}
    for origin,(claim,channel) in sorted(refs.items()):
        item=cal[channel]
        reliability[origin]=(2+item["correct"])/(4+item["total"])
        claims.append((origin,claim))
    yes=_witness_likelihood(tuple(claims),reliability,True)
    no=_witness_likelihood(tuple(claims),reliability,False)
    p=yes/(yes+no)
    return {
        "motif013_conditional_root_posterior":p,
        "motif007_conditional_root_posterior":fitted["posterior"],
        "match_to_12_decimals":round(p,12)==round(fitted["posterior"],12),
        "actual_reference":"experiments/013/witness_model.py::_witness_likelihood",
        "independent_baseline":False,"source_identity_authenticated":False,
    }

if __name__=="__main__":
    import json
    from simulator import demonstration
    print(json.dumps(compare_013(demonstration()),indent=2,sort_keys=True))
