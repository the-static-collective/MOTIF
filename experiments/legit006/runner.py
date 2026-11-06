"""LEGIT-006: unannotated text -> induced semantic proposition -> finite
evidence-ledger truth check, with source and scope guards. No external effects.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
from grammar import HOLD as GrammarHold, learn, parse, normalized
from ledger import HOLD as LedgerHold, evaluate, inspect

def learned():
    with (HERE/"teacher.json").open(encoding="utf-8") as file:
        data=json.load(file)
    if data.get("schema")!="motif.semantic-adversary-teacher.v1":
        raise GrammarHold("Unrecognized teacher provenance")
    return learn(data["records"])


def examine(sentence,ledger,grammar):
    # Validate world assumptions BEFORE looking at plausible surface language.
    try:
        source=inspect(ledger)
    except (LedgerHold, TypeError, ValueError) as e:
        return {
            "status":"HOLD_INVALID_SOURCE_LEDGER","claim":None,"answer":None,
            "failure":str(e),"real_world_authority":False}
    parsed=parse(sentence,grammar)
    if parsed["status"]!="PARSE_PROPOSAL_ONLY":
        return {"status":"HOLD_UNKNOWN_MEANING","claim":None,"answer":None,
                "parser":parsed,"suggested_question":
                "Which exact target and measured condition does this statement assert?",
                "sent":False,"real_world_authority":False}
    if normalized(parsed["target"])!=normalized(ledger["target"]):
        return {"status":"HOLD_TARGET_MISMATCH","claim":None,"answer":None,
                "parser":parsed,"real_world_authority":False}
    if parsed["indicator"] is not None and normalized(parsed["indicator"])!=normalized(ledger["indicator"]):
        return {"status":"HOLD_INDICATOR_MISMATCH","claim":None,"answer":None,
                "parser":parsed,"real_world_authority":False}
    result=evaluate(ledger,parsed["kind"])
    return {"status":("HOLD_CONFLICTING_EVIDENCE" if result["value"] is None else
                      "RESEARCH_PROPOSAL_ONLY"),
            "claim":parsed,"answer":result["value"],
            "proof":{
                "worlds":result["worlds"],
                "witnesses":result["supporting_counts"],
                "value_within_declared_ledger":result["value"],
                "status":result["verdict"],
                "ledger_digest":result["ledger_digest"]},
            "method":"LEARNED_SURFACE_COMPOSITION_PLUS_CLASSICAL_MODEL_CHECK",
            "source_authentication":False,
            "individual_probability":None,
            "actual_target_state":None,
            "real_world_authority":False,
            "external_actions":False}


def example():
    """The defining adversarial minimal pair: same words, one crucial 'no'."""
    grammar=learned()
    ledger={
        "schema":"motif.synthetic-epistemic-ledger.v1",
        "id":"SilenceAndSignals",
        "scope":"SYNTHETIC_ONLY",
        "target":"hidden shelter",
        "indicator":"sonar ping",
        "reports":[]}
    left="there is no evidence that hidden shelter exists."
    right="there is evidence that hidden shelter does not exist."
    return {
        "experiment":"MOTIF-LEGIT-006",
        "question_a":left,
        "interpretation_a":examine(left,ledger,grammar),
        "question_b":right,
        "interpretation_b":examine(right,ledger,grammar),
        "actual_hidden_shelter_exists":None,
        "independently_blinded_examiner":False,
        "scope":"SYNTHETIC_ONLY",
        "real_world_authority":False}

if __name__=="__main__":
    print(json.dumps(example(),sort_keys=True,indent=2))
