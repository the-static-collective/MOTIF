"""Conservative source-reviewed bridge to original REASON-011 four-value evaluator.

This bridge **does not** claim to infer statute, holdings, case law or issues
from English. A separate human curator supplies issue/polarity labels after
source checks. The verified quote classifier supplies the epistemic type.
The bridge demonstrates that two opposite signs cannot be collapsed across
different legal issues, courts, or historical time frames.
"""
from __future__ import annotations

from hashlib import sha1
from pathlib import Path
import sys

from classifier import HOLD,digest
from corpus import OPINIONS,passages
from review_keys import LABELS
from receiver import Receiver

PARENT=Path(__file__).resolve().parents[1]/"reason-cartridge-011"/"engine.py"
PARENT_GIT_BLOB="39947e5ccfecb11ce7ab0d32ed35ef103abdaab5"


def pin_prior():
    data=PARENT.read_bytes()
    sha=sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if sha!=PARENT_GIT_BLOB:
        raise HOLD("Source-owned REASON-011 four-valued engine changed")
    return sha


pin_prior()
sys.path.append(str(PARENT.parent))
from engine import verdict


def literal(case_id,issue):
    opinion=OPINIONS[case_id]
    return {
        "forum":opinion["court"],
        "epoch":str(opinion["year"]),
        "subject":"CASE_"+case_id,
        "predicate":issue,
        "sign":"YES",
    }


def checked_evidence(receiver):
    if not isinstance(receiver,Receiver) or not receiver.approved:
        raise HOLD("No source-reviewed quote categorization")
    known={}
    excluded=[]
    provenance=[]
    for span in passages(True)+passages(False):
        label,issue,polarity=LABELS[span["span_id"]]
        suggested=receiver.suggest(span)
        if (suggested["stage"]!="SUGGEST_ONLY" or suggested["category"]!=label
                or polarity=="UNDECIDED" or label not in (
                "LEGAL_TREATMENT","PROCEDURAL_POSTURE")):
            excluded.append({
                "span_id":span["span_id"],"curator_class":label,
                "reason":"NOT_AN_ADMITTED_HOLDING_OR_PROCEDURAL_RESULT",
            })
            continue
        typed=literal(span["case_id"],issue)
        typed["sign"]=polarity
        k=(typed["forum"],typed["epoch"],typed["subject"],
           typed["predicate"],typed["sign"])
        if k in known:raise HOLD("Duplicate source assertion")
        known[k]={"claims":[span["span_id"]],"rules":[]}
        provenance.append({
            "span_id":span["span_id"],"curator_issue":issue,
            "curator_sign":polarity,"court":span["court"],
            "year":span["year"],"quote":span["text"],
            "url":span["opinion_url"],
            "issue_and_sign_from_human_annotation_not_inferred_by_model":True,
        })
    return known,excluded,provenance


def evaluate(receiver):
    facts,excluded,provenance=checked_evidence(receiver)
    questions=(
        ("NARUTO","ARTICLE_III_STANDING"),
        ("NARUTO","COPYRIGHT_STATUTORY_STANDING"),
        ("COCA","CAFFEINE_ADDED_INGREDIENT"),
        ("COCA","CAFFEINE_HARM_PROVEN"),
        ("STAMBOVSKY","ESTOPPEL_REPUTATION"),
        ("STAMBOVSKY","PHYSICAL_GHOST_EXISTS"),
        ("ULYSSES","PORNOGRAPHIC_INTENT"),
        ("ULYSSES","FORFEITURE_GRANTED"),
        ("PIERSON","LOWER_DECISION_AFFIRMED"),
    )
    outcomes={}
    for cid,issue in questions:
        status=verdict(facts,literal(cid,issue))
        outcomes[cid+"/"+issue]={
            "four_value":status["four_value"],
            "positive_excerpt_witness":status["positive_proof"]["claims"]
                 if status["positive_proof"] else None,
            "negative_excerpt_witness":status["negative_proof"]["claims"]
                 if status["negative_proof"] else None,
            "scope":"COURT_AND_HISTORICAL_YEAR_NOT_CURRENT_AUTHORITY",
            "live_judgment_not_inferred":True,
        }
    pairs=(
        ("NARUTO/ARTICLE_III_STANDING",
         "NARUTO/COPYRIGHT_STATUTORY_STANDING"),
        ("COCA/CAFFEINE_ADDED_INGREDIENT",
         "COCA/CAFFEINE_HARM_PROVEN"),
        ("STAMBOVSKY/ESTOPPEL_REPUTATION",
         "STAMBOVSKY/PHYSICAL_GHOST_EXISTS"),
    )
    for a,b in pairs:
        if a==b or outcomes[a]["four_value"]=="BOTH" or outcomes[b]["four_value"]=="BOTH":
            raise HOLD("Conflated epistemic issue/court source contradiction")
    return {
        "schema":"motif.reason.actual-opinion-four-value-bridge.v1",
        "source_011_engine_pin":pin_prior(),
        "human_curated_assertions":provenance,
        "excluded_nonholdings_unresolved_or_unclassified":excluded,
        "four_value_propositions":outcomes,
        "pairwise_nonconflations":[[a,b] for a,b in pairs],
        "learned_only_court_quote_type_not_full_statute_semantics":True,
        "curator_supplied_issue_and_polarity":True,
        "new_real_world_observations":0,
        "current_law_inferred":False,
        "legal_advice":False,"external_actions":False,
        "real_world_authority":False,
    }
