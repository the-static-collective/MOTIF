"""MOTIF-011 tangible scientist transcript and source-owned tree router.

Run:
    python demo.py

This emits a *synthetic* six-world skepticism report and an actual portable
derived-router cartridge composed from two MOTIF-009 decision-tree cartridges.
Local admission is prediction-only and no verified authorship is claimed.
"""
from __future__ import annotations
import json

from oracle import SEEDS, make_world, episodes
from benchmark import demo as outcomes  # Resolve local benchmark before shared imports.
from skeptic import (assess, LocalConceptBay, export_extension,
                     decode_extension, validated_result)


def demonstrate():
    spec=make_world("visible_third",SEEDS[0])
    study=assess(episodes(spec,"train"),
                 episodes(spec,"validation"),spec.controls)
    if study.status!="PROPOSE_EXTENSION" or study.extension is None:
        raise AssertionError("No independently validated third relation")
    packet=json.loads(export_extension(study.extension))
    held=LocalConceptBay()
    ticket=held.offer_packet(json.dumps(packet))
    was_held=ticket not in held.admitted
    local=episodes(spec,"local_review")
    review=held.review(ticket,"ADMIT_PREDICT_ONLY",
                       "LOCAL_SYNTHETIC_REVIEWER",local,spec.controls)
    testing=episodes(spec,"test")
    predictions=[held.predict(ticket,e,spec.controls) for e in testing]
    truths=[validated_result(e) for e in testing]
    return {
        "experiment":"MOTIF-011",
        "mode":"SYNTHETIC_SKEPTICAL_SCIENTIST",
        "research_cases":outcomes()["cases"],
        "portable_new_concept_router":packet,
        "router_was_held_until_local_review":was_held,
        "local_review":{
            "decision":review.decision,
            "examples":review.local_examples,
            "used_heldout_test_labels":review.heldout_information_used,
            "real_world_authority":review.real_world_authority,
        },
        "heldout_router_correct":sum(p==t for p,t in zip(predictions,truths)),
        "heldout_router_total":len(truths),
        "cost_and_safety":outcomes()["unsafe_interventions"],
        "all_raw_observations_remained_immutable":True,
        "real_external_actions":0,
    }


if __name__=="__main__":
    print(json.dumps(demonstrate(),sort_keys=True,indent=2))
