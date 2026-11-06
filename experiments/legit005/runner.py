"""LEGIT-005: source-scoped meaning-to-countermodel executor.

One *logical* step beyond LEGIT-004: an induced, composed interpretation
selects a counterexample question (universal implication vs existential
countermodel), and a finite exact countermodel compiler computes the answer
**within the admitted evidence and grammar**, without probability inversion.

Questions are NOT clinical conclusions. "Can" means satisfiable within the
finite admitted sample, not metaphysical/physical possibility in general.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit003"))
from countermodel import HOLD as BoundHold, compile_countermodels
from meaning import HOLD, KINDS, learn, parse, normalize, complement_certificate

RAW_SCHEMA="motif.meaning-evidence.v1"

def trained():
    with (HERE/"teacher.json").open(encoding="utf-8") as handle:
        document=json.load(handle)
    if document.get("schema")!="motif.meaning-teachers.v1":
        raise HOLD("Unknown teacher document")
    return learn(document["examples"])


def _symbol(value):
    val=re.sub(r"[^a-z0-9]+","_",normalize(value)).strip("_").upper()
    if not 1<=len(val)<=80 or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,79}",val):
        raise HOLD("Unrepresentable meaning token")
    return val


def check_raw(raw):
    if not isinstance(raw,dict) or set(raw)!={
            "schema","id","scope","question","indicator",
            "observations","anchors","sources"}:
        raise HOLD("Unknown research evidence input")
    if raw["schema"]!=RAW_SCHEMA or raw["scope"] not in ("SYNTHETIC_ONLY","CURATED_PUBLIC_RESEARCH"):
        raise HOLD("Unsupported observation authority")
    if not isinstance(raw["id"],str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}",raw["id"]):
        raise HOLD("Unsupported case identifier")
    normalize(raw["question"])
    normalize(raw["indicator"])
    if not isinstance(raw["observations"],list) or not isinstance(raw["anchors"],list) or not isinstance(raw["sources"],list):
        raise HOLD("Typed source cohort required")
    return raw


def case_for_proof(raw,parsed):
    observations=[]
    for row in raw["observations"]:
        if not isinstance(row,dict) or set(row)!={
                "group","positive","negative","source_id"}:
            raise HOLD("Unknown observation record")
        observations.append({"group":row["group"],"proxy_positive":row["positive"],
                             "proxy_negative":row["negative"],"source_id":row["source_id"]})
    return {
        "schema":"motif.latent-countermodel.v1",
        "id":raw["id"],"scope":raw["scope"],
        "question":raw["question"],
        "latent_target":_symbol(parsed["target"]),
        "observed_proxy":_symbol(parsed["proxy"]),
        "observations":observations,"anchors":raw["anchors"],
        "sources":raw["sources"],
    }


def _bounds(kind,proof):
    cells=proof["cells"]
    polarity="negative" if kind.endswith("NEG") else "positive"
    source=[c for c in cells if c["proxy"]==polarity]
    observed=sum(c["observed"] for c in source)
    if polarity=="negative":
        low=sum(c["min_target_true"] for c in source)
        high=sum(c["max_target_true"] for c in source)
        witness="maximum_latent_target"
    else:
        low=sum(c["observed"]-c["max_target_true"] for c in source)
        high=sum(c["observed"]-c["min_target_true"] for c in source)
        witness="minimum_latent_target"
    return polarity,observed,low,high,witness


def examine(raw,grammar):
    check_raw(raw)
    proposed=parse(raw["question"],grammar)
    if proposed["status"]!="PARSED_PROPOSAL_ONLY":
        return {
            "status":"HOLD_UNRECOGNIZED_MEANING","task_id":raw["id"],
            "parser":proposed,"next_route":"PROPOSE_CLARIFICATION_UNSENT",
            "suggested_question":"What exact observed condition and hidden claim should be compared?",
            "answer":None,"real_world_authority":False,
        }
    if normalize(raw["indicator"])!=proposed["proxy"]:
        return {
            "status":"HOLD_INDICATOR_SOURCE_MISMATCH","task_id":raw["id"],
            "parser":proposed,"answer":None,"next_route":"VERIFY_INSTRUMENT_IDENTITY_UNSENT",
            "real_world_authority":False,
        }
    typed=case_for_proof(raw,proposed)
    try:
        proof=compile_countermodels(typed)
    except BoundHold as err:
        return {
            "status":"HOLD_INVALID_SOURCE_EVIDENCE","task_id":raw["id"],
            "parser":proposed,"answer":None,"validation_failure":str(err),
            "real_world_authority":False,
        }
    kind=proposed["kind"]
    polarity,count,low,high,cert=_bounds(kind,proof)
    if count==0:
        result="HOLD_NO_RELEVANT_SAMPLE_CASES"
        response=None
    elif kind.startswith("U_"):
        result=("ENTAILED_WITHIN_ALL_ADMITTED_COMPLETIONS" if high==0 else
                "NOT_ENTAILED_A_COUNTERMODEL_EXISTS")
        response=high==0
    else:
        result=("COMPATIBLE_COUNTERMODEL_EXISTS" if high>0 else
                "NO_COUNTERMODEL_IN_ADMITTED_COMPLETIONS")
        response=high>0
    return {
        "task_id":raw["id"],
        "status":"RESEARCH_HOLD",
        "parser":proposed,
        "claim":{
            "kind":kind,"relation":"negative-measurement vs hidden-target" if
                      kind.endswith("NEG") else
                      "positive-measurement vs hidden-target",
            "quantifier":"FOR_ALL_COMPATIBLE_COMPLETIONS" if
                         kind.startswith("U_") else "EXISTS_COMPATIBLE_COMPLETION",
            "counterexample_condition":(
                "PROXY_NEGATIVE_AND_TARGET_PRESENT" if
                polarity=="negative" else "PROXY_POSITIVE_AND_TARGET_ABSENT"),
            "antecedent_observed":count,
            "possible_counterexample_count_bounds":[low,high],
            "logical_answer_in_admitted_model":response,
            "verdict":result,
            "actual_hidden_target_state":None,
            "individual_probability":None,
            "countermodel_used_when_possible":cert if high>0 else None,
            "converse_entailment_status":(
                "REFUTABLE_BY_COUNTERMODEL" if high>0 else
                "HOLDS_IN_ADMITTED_COMPLETIONS"),
        },
        "proof_digest":proof["source_packet_sha256"],
        "source_authenticated":False,
        "question_patterns_learned":True,
        "logical_operators_predeclared":True,
        "native_unrestricted_language_understanding":False,
        "real_world_authority":False,
        "no_external_actions":True,
        "interpretation":"Closed finite admitted-sample semantics only; cannot establish clinical or real-world impossibility.",
    }


def neuro_packet():
    """Public hand-curated numerical evidence; no hand-labelled text roles."""
    sys.path.insert(0,str(HERE.parent/"legit002"))
    from evidence_router import load_packet
    source=next(s for s in load_packet()["source_cards"] if "counts" in s)
    raw={
        "schema":RAW_SCHEMA,"id":"NeuralCovert2024Meaning",
        "scope":"CURATED_PUBLIC_RESEARCH",
        "question":"Can subjective experience exist without neural command response?",
        "indicator":"neural command response",
        "sources":[{"id":source["id"],"url":source["url"],
                    "provenance":"HAND_CURATED"}],
        "observations":[{"group":r["group"],"positive":r["positive_neural_task"],
                         "negative":r["negative_neural_task"],
                         "source_id":source["id"]} for r in source["counts"]],
        "anchors":[]
    }
    return raw


def demo():
    grammar=trained()
    first=neuro_packet()
    second=dict(first,question="Does missing neural command response rule out subjective experience?")
    return {
        "experiment":"MOTIF-LEGIT-005",
        "source":"LEGIT-002 hand-curated 2024 clinical research cohort",
        "teacher_count":grammar["teacher_count"],
        "learned_full_combinations":len(grammar["rules"]),
        "compositions_unseen_in_teacher":grammar["novel_combinations"],
        "can_a_countermodel_exist":examine(first,grammar),
        "is_absence_entailed":examine(second,grammar),
        "logical_pairs":complement_certificate(),
        "no_real_patient_diagnosis":True,
        "independent_blind_trial":False,
        "real_world_authority":False,
    }


if __name__=="__main__":
    print(json.dumps(demo(),indent=2,sort_keys=True))
