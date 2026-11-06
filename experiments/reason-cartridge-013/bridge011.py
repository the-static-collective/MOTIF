"""Read the adversarial opinion by voice, not by counting contradictory words.

Reuses the original pinned REASON-011 four-valued verdict function. Every
individual voice is a separate scope; majority judgment is assembled from
explicit joinders, not inferred from a single opinion writer's argument.
No claim about current law or all fish-related prosecutions is emitted.
"""
from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

from reader import HOLD,read,digest

PRIOR=Path(__file__).resolve().parents[1]/"reason-cartridge-011"/"engine.py"
PRIOR_BLOB="39947e5ccfecb11ce7ab0d32ed35ef103abdaab5"

def source_pin():
    blob=PRIOR.read_bytes()
    actual=sha1(b"blob "+str(len(blob)).encode()+b"\0"+blob).hexdigest()
    if actual!=PRIOR_BLOB:raise HOLD("Prior provenance-owned logic changed")
    return actual

source_pin()
sys.path.append(str(PRIOR.parent))
from engine import verdict


def scoped_literal(case,judge):
    return {
        "forum":"US_SUPREME_COURT",
        "epoch":case["year"],
        "subject":"VOICE_"+judge,
        "predicate":"RESTRICTS_TANGIBLE_OBJECT_INTERPRETATION",
        "sign":"YES",
    }


def evaluate(case_id):
    case=read(case_id)
    props={}
    for judge,voice in case["parsed_voices"].items():
        positive=[x for x in case["evidence_nodes"]
                  if x["judge"]==judge and x["feature"]=="RESTRICTED_SCOPE"]
        negative=[x for x in case["evidence_nodes"]
                  if x["judge"]==judge and x["feature"]=="EXPANSIVE_SCOPE"]
        proposition=scoped_literal(case,judge)
        facts={}
        k=(proposition["forum"],proposition["epoch"],proposition["subject"],
           proposition["predicate"])
        if positive:
            facts[k+("YES",)]={
                "claims":sorted(x["node"] for x in positive),"rules":[]}
        if negative:
            facts[k+("NO",)]={
                "claims":sorted(x["node"] for x in negative),"rules":[]}
        status=verdict(facts,proposition)
        props[judge]={
            "voice_role":voice["role"],
            "declared_judges":voice["explicit_votes"],
            "reported_legal_interpretation_status":status["four_value"],
            "source_positive_span_ids":[x["paragraph"] for x in positive],
            "source_negative_span_ids":[x["paragraph"] for x in negative],
            "not_authoritative_as_to_other_voices":True,
        }
    # These vote counts summarize the directly named authors/joiners in
    # opinion headers, not a machine-made substantive holding.
    aligned=sum(v["declared_judges"] for v in props.values()
                if v["voice_role"] in ("JUDGMENT_ANNOUNCER",
                                      "CONCURRENCE_IN_JUDGMENT"))
    dissenting=sum(v["declared_judges"] for v in props.values()
                  if v["voice_role"]=="DISSENT")
    overall=(aligned,dissenting) if aligned and dissenting else None
    return {
        "schema":"motif.reason.adversarial-reader.four-value-voices.v1",
        "case":case_id,"prior_engine_git_blob":source_pin(),
        "per_voice_interpretations":props,
        "named_judgment_alignment":overall,
        "majority_judgment_is_not_single_majority_rationale":True,
        "opposed_views_not_source_fact_contradiction":True,
        "dissent_does_not_control_judgment":True,
        "no_current_precedential_authority_inferred":True,
        "external_actions":False,"real_world_authority":False,
    }
