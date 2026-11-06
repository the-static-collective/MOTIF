"""LEGIT-004: text-to-typed-countermodel bridge with learned source patterns.

Only the *question grammar* is induced from corrected teacher examples.
The measurement table is already structured and source-scoped. We neither
parse empirical paper prose nor infer the meaning of arbitrary noun phrases.
Both the learned parser and the compiler are read-only and untrusted.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit003"))
from countermodel import HOLD as CountermodelHold, compile_countermodels
from grammar import HOLD, learn, parse, normalized

RAW_SCHEMA="motif.raw-question-evidence.v1"
GRAMMAR_FILE=HERE/"teacher.json"

def trained_grammar():
    with open(GRAMMAR_FILE,encoding="utf-8") as handle:
        teacher=json.load(handle)
    if teacher.get("schema")!="motif.teacher-questions.v1":
        raise HOLD("Unknown teacher origin")
    return learn(teacher["examples"])

def _symbol(phrase):
    return re.sub(r"[^a-z0-9]+","_",normalized(phrase)).strip("_").upper()

def raw_validate(raw):
    if not isinstance(raw,dict) or set(raw)!={
            "schema","id","scope","question","indicator","observations","sources"}:
        raise HOLD("Unknown raw evidence contract")
    if raw["schema"]!=RAW_SCHEMA or raw["scope"] not in (
            "SYNTHETIC_ONLY","CURATED_PUBLIC_RESEARCH"):
        raise HOLD("Question or authority schema unsupported")
    if not isinstance(raw["id"],str) or not re.fullmatch("[A-Za-z0-9_-]{1,64}",raw["id"]):
        raise HOLD("Invalid task ID")
    normalized(raw["question"])
    normalized(raw["indicator"])
    if not isinstance(raw["sources"],list) or not isinstance(raw["observations"],list):
        raise HOLD("Source-owned table required")
    return raw

def assemble(raw, grammar):
    """Generate typed graph-reasoning constraints, not prior world hypotheses."""
    raw_validate(raw)
    interpretation=parse(raw["question"],grammar)
    if interpretation["status"]!="PARSE_PROPOSAL_ONLY":
        return None,interpretation
    if normalized(raw["indicator"])!=interpretation["proxy"]:
        return None,{"status":"HOLD_SOURCE_INDICATOR_MISMATCH",
                     "real_world_authority":False}
    observations=[]
    for row in raw["observations"]:
        if not isinstance(row,dict) or set(row)!={"group","positive","negative","source_id"}:
            raise HOLD("Invalid numeric source cohort")
        observations.append({"group":row["group"],"proxy_positive":row["positive"],
                             "proxy_negative":row["negative"],"source_id":row["source_id"]})
    typed={
        "schema":"motif.latent-countermodel.v1",
        "id":raw["id"],
        "scope":raw["scope"],
        "question":raw["question"],
        "latent_target":_symbol(interpretation["target"]),
        "observed_proxy":_symbol(interpretation["proxy"]),
        "observations":observations,
        "anchors":[],
        "sources":raw["sources"],
    }
    return typed,interpretation

def examine(raw, grammar):
    typed, meaning=assemble(raw,grammar)
    if typed is None:
        return {"task_id":raw["id"],"status":meaning["status"],
                "parser":meaning,"reasoned_claim":None,
                "real_world_authority":False}
    try:
        witness=compile_countermodels(typed)
    except CountermodelHold as error:
        return {"task_id":raw["id"],"status":"HOLD_INVALID_SOURCE_EVIDENCE",
                "failure":str(error),"parser":meaning,"reasoned_claim":None,
                "real_world_authority":False}
    affirmative=meaning["kind"]=="PROXY_POSITIVE_IMPLIES_TARGET_PRESENT"
    antecedent="positive" if affirmative else "negative"
    cells=[x for x in witness["cells"] if x["proxy"]==antecedent]
    n=sum(c["observed"] for c in cells)
    lo=sum(c["min_target_true"] for c in cells)
    hi=sum(c["max_target_true"] for c in cells)
    if n==0:
        verdict="NO_OBSERVED_ANTECEDENT_CASES"
    elif affirmative:
        if lo==n:verdict="ENTAILED_ONLY_WITHIN_ADMITTED_SAMPLE"
        elif hi<n:verdict="REFUTED_IN_EVERY_COMPATIBLE_COMPLETION"
        else:verdict="NOT_IDENTIFIABLE_FROM_ADMITTED_EVIDENCE"
    else:
        if hi==0:verdict="ENTAILED_ONLY_WITHIN_ADMITTED_SAMPLE"
        elif lo>0:verdict="REFUTED_IN_EVERY_COMPATIBLE_COMPLETION"
        else:verdict="NOT_IDENTIFIABLE_FROM_ADMITTED_EVIDENCE"
    return {"task_id":raw["id"],
            "status":"RESEARCH_HOLD",
            "parser":meaning,
            "reasoned_claim":{"kind":meaning["kind"],
                              "antecedent_proxy":antecedent,
                              "observed_antecedent_count":n,
                              "compatible_latent_true_bounds":[lo,hi],
                              "verdict":verdict,
                              "individual_probability":None},
            "evidence_digest":witness["source_packet_sha256"],
            "countermodels_preserve_evidence":True,
            "question_to_type_template_induced_from_teacher":True,
            "assumption":"Teacher-supplied claim kinds, structured evidence source, unverified text semantics",
            "native_unrestricted_language_comprehension":False,
            "real_world_authority":False}

def historical_neuroscience():
    """Reuses 002 source counts but does not annotate query's conceptual roles."""
    sys.path.insert(0,str(HERE.parent/"legit002"))
    from evidence_router import load_packet
    prior=load_packet()
    src=next(x for x in prior["source_cards"] if "counts" in x)
    return {
        "schema":RAW_SCHEMA,
        "id":"ColdFormulationNeural2024",
        "scope":"CURATED_PUBLIC_RESEARCH",
        "question":"If task based neural command following is negative, must subjective experience be absent?",
        "indicator":"task based neural command following",
        "sources":[{"id":src["id"],"url":src["url"],"provenance":"HAND_CURATED"}],
        "observations":[{"group":x["group"],"positive":x["positive_neural_task"],
                         "negative":x["negative_neural_task"],"source_id":src["id"]}
                        for x in src["counts"]],
    }

def demo():
    grammar=trained_grammar()
    return {"experiment":"MOTIF-LEGIT-004",
            "teacher_examples":grammar["teacher_count"],
            "learned_patterns":len(grammar["rules"]),
            "example":examine(historical_neuroscience(),grammar),
            "author_independent_blinded":False,
            "real_world_authority":False}

if __name__=="__main__":
    print(json.dumps(demo(),sort_keys=True,indent=2))
