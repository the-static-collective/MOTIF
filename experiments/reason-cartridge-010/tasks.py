"""Source-owned structured tasks with real opinions and synthetic distortions.

The *legal holdings* are human-curated paraphrases tied to actual opinion URLs.
Decoys are deliberately generated counterfactual metadata, NOT assertions
about a court opinion. The label is a card identifier, not judicial advice.
"""
from __future__ import annotations
from dataclasses import dataclass

from casebook import CASES,QUERY_SPECS,OPINION_CARD_REVISION

FIELDS=("case_id","issue","voice","kind","layer","source_status")
SOURCE_STATUS="SOURCE_ANCHORED_PARAPHRASE"
DISTORTIONS={
    "case_id":"WRONG_COURT_OR_OPINION",
    "issue":"UNRELATED_LEGAL_QUESTION",
    "voice":"PARTY_OR_DISSENT_NOT_CONTROLLING",
    "kind":"ARGUMENT_NOT_HOLDING",
    "layer":"UNSUPPORTED_FACTUAL_INFERENCE",
    "source_status":"SYNTHETIC_UNVERIFIED_CLAIM",
}

@dataclass(frozen=True)
class Scenario:
    id: str
    query: dict
    cards: tuple[dict,...]
    expected: str

    def __post_init__(self):
        if (not self.id or set(self.query)!=set(FIELDS)
                or not isinstance(self.cards,tuple)
                or not self.cards or not isinstance(self.expected,str)):
            raise ValueError("Malformed legal issue task")


def canonical_cards(case_id):
    doc=CASES[case_id]
    return tuple({
        "id":id,"case_id":case_id,"issue":issue,"voice":voice,
        "kind":kind,"layer":layer,"source_status":SOURCE_STATUS,
        "explanation":explanation,
        "opinion_url":doc["opinion_url"],
        "citation":doc["citation"],"court":doc["court"],
        "paraphrase_not_verbatim":True,
    } for id,issue,voice,kind,layer,explanation in doc["claims"])


def make(case_id,index):
    if case_id not in CASES or type(index) is not int or not 0<=index<3:
        raise ValueError("Unsupported historical case scenario")
    issue,voice,kind,layer,expected=QUERY_SPECS[case_id][index]
    query={"case_id":case_id,"issue":issue,"voice":voice,
           "kind":kind,"layer":layer,"source_status":SOURCE_STATUS}
    real=canonical_cards(case_id)
    correct=next(x for x in real if x["id"]==expected)
    # Each distortion is one wrong claim attached to a simulation-only
    # evidence fixture. No claim about an actual court is created or changed.
    contrasts=[]
    for field,replacement in DISTORTIONS.items():
        wrong=dict(correct)
        wrong[field]=replacement
        wrong["id"]=f"DECOY-{expected}-{field}"
        wrong["explanation"]="SYNTHETIC CONTRASTIVE DISTRACTOR — NOT A COURT FINDING"
        wrong["paraphrase_not_verbatim"]=True
        contrasts.append(wrong)
    # Add actual separately voiced and differently scoped historical records.
    competing=[x for x in real if x["id"]!=expected]
    # Always place a nearly matching decoy before the genuine card:
    # a shallow first-hit strategy will fail.
    cards=tuple(contrasts + competing + [correct])
    return Scenario(f"{case_id}-{index}",query,cards,expected)


def training():
    return tuple(make(case,i) for case in ("STAMBOVSKY","LEONARD")
                 for i in range(3))


def heldout():
    return tuple(make(case,i) for case in ("NARUTO","PIERSON")
                 for i in range(3))


def unsupported():
    x=make("NARUTO",1)
    bad=dict(x.query,issue="WHO_OWNS_MONKEY_COPYRIGHT")
    return Scenario("NARUTO-UNKNOWN",bad,x.cards,"HOLD")


def unsupported_forum():
    x=make("PIERSON",0)
    bad=dict(x.query,case_id="CURRENT_MINNESOTA_SUPREME_COURT")
    return Scenario("PIERSON-WRONG-FORUM",bad,x.cards,"HOLD")
