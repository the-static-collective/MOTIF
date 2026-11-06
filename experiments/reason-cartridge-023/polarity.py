"""Four-valued, explicitly scoped synthetic source evidence, with REAL 011 crosswire.

A distinct source-backed bAbI answer is *not* an explicit negation of the
other answer. Four-valued BOTH applies only to explicit YES and NO evidence
for the same (speaker,revision,proposition). Missing evidence is UNDETERMINED,
never automatically refutation. Reuse the original pinned REASON-011 verdict
implementation as an independent code-path parity check.
"""
from __future__ import annotations
from hashlib import sha1
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import json

from polarity_cases import CASES,case

HERE=Path(__file__).resolve().parent
P011=HERE.parent/"reason-cartridge-011"/"engine.py"
CASEFILE=HERE/"polarity_cases.py"
PIN_011="39947e5ccfecb11ce7ab0d32ed35ef103abdaab5"
PIN_CASE="e5103f8f39f7f784bcc8711fbce5336cf5a0d18e"


class HOLD(ValueError):
    pass


def git_blob(path):
    raw=path.read_bytes()
    return sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()


def pin():
    if git_blob(P011)!=PIN_011 or git_blob(CASEFILE)!=PIN_CASE:
        raise HOLD("Prior paraconsistent reasoner or source cases changed")
    return {"real_reason011":PIN_011,"fictional_stipulations":PIN_CASE}


def prior011():
    pin()
    spec=spec_from_file_location("motif023_original_reason011",P011)
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def reason(row):
    pin()
    if row not in CASES:
        raise HOLD("Source testimony was modified or fabricated")
    yes=[];no=[];facts={}
    other_subject=row.get("external_subject_for_claim",{})
    other_epoch=row.get("external_epoch_for_claim",{})
    for id,sign,quote in row["claims"]:
        if sign not in ("YES","NO") or not quote:
            raise HOLD("Only explicit source statements count")
        s=other_subject.get(id,row["subject"])
        epoch=other_epoch.get(id,row["epoch"])
        typed=(s,epoch,row["predicate"],sign)
        facts.setdefault(typed,[]).append({
            "source_id":id,"exact_source_quote":quote,
            "owner":s,"epoch":epoch,"sign":sign,
            "fictional":True,
        })
        if s==row["subject"] and epoch==row["epoch"]:
            (yes if sign=="YES" else no).append(id)
    state=("BOTH" if yes and no else "SUPPORTED" if yes else
           "REFUTED" if no else "UNDETERMINED")
    # Compare with ORIGINAL REASON-011 verdict, not an imitation.
    imported=prior011()
    translated={}
    for (subject,epoch,predicate,sign),proofs in facts.items():
        key=("MOTIF023",epoch,subject,predicate,sign)
        translated[key]={"claims":[x["source_id"] for x in proofs],"rules":[]}
    question={"forum":"MOTIF023","epoch":row["epoch"],
              "subject":row["subject"],"predicate":row["predicate"],"sign":"YES"}
    old=imported.verdict(translated,question)
    if old["four_value"]!=state:
        raise HOLD("Original 011 four-valued semantics disagree")
    return {
        "schema":"motif.reason023.scoped-signed-proposition.v1",
        "case":row["id"],
        "context":{"person":row["subject"],"epoch":row["epoch"],
                   "proposition":row["predicate"]},
        "status":state,
        "support_source_ids":yes,"refute_source_ids":no,
        "unrelated_scoped_source_claims":[
            x for x in (x for v in facts.values() for x in v)
            if x["source_id"] not in yes+no],
        "original_011_verdict":old["four_value"],
        "source_git_blobs":pin(),
        "explicit_no_is_not_absence":True,
        "distinct_possible_answers_are_not_a_four_valued_BOTH":True,
        "permission_to_execute":False,"real_human_not_tested":True,
    }


def all_cases():
    return [reason(row) for row in CASES]
