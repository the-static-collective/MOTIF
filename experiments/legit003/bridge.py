"""LEGIT-003: convert the existing source-owned LEGIT-002 cohort into
an opaque-target, countermodel-ready evidence question.

This is an explicit *schema translation*, NOT automated reading of literature,
not recognition of consciousness, and not an independently learned grammar.
The compiler checks the original 002 adapter before carrying counts forward.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent / "legit002"))
from evidence_router import load_packet, run as previous_evidence_check
from countermodel import SCHEMA, compile_countermodels, validate

def from_legit002(packet):
    previous = previous_evidence_check(packet)
    sources = []
    observations = []
    for src in packet["source_cards"]:
        if "counts" not in src:
            continue
        sources.append({"id":src["id"],"url":src["url"],
                        "provenance":"HAND_CURATED"})
        for row in src["counts"]:
            observations.append({
                "group":row["group"],
                "proxy_positive":row["positive_neural_task"],
                "proxy_negative":row["negative_neural_task"],
                "source_id":src["id"],
            })
    case = {
        "schema":SCHEMA,
        "id":"CovertConsciousness2024Aggregate",
        "scope":"CURATED_PUBLIC_RESEARCH",
        "question":packet["challenge"],
        "latent_target":"SUBJECTIVE_EXPERIENCE",
        "observed_proxy":"TASK_BASED_NEURAL_COMMAND_FOLLOWING",
        "observations":observations,
        "anchors":[],
        "sources":sources,
    }
    validate(case)
    return case, previous

def demonstrate():
    case, previous = from_legit002(load_packet())
    receipt = compile_countermodels(case)
    return {
        "experiment":"MOTIF-LEGIT-003",
        "source_origin":"LEGIT-002 curated NEJM cohort counts",
        "prior_adapter_conclusion":previous["inference"],
        "compiler_receipt":receipt,
        "native_arbitrary_paper_comprehension":False,
        "source_truth_verified_independently":False,
        "real_patient_inference":False,
        "result":"COUNTERMODELS_OF_OBSERVATIONS_NOT_PERSONS",
    }

if __name__=="__main__":
    print(json.dumps(demonstrate(),sort_keys=True,indent=2))
