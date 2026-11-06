"""Direct source-pinned integration with the ACTUAL REASON-016 thinker.

Its previous finite candidate grammar understandably HOLDS when an otherwise
valid synthetic response is not in the enumerated answer vocabulary.
REASON-017 adds source-authored *quoted hypotheses*, not magical general
language understanding or improved measured human outcomes.
"""
from __future__ import annotations

from hashlib import sha1
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import sys

PRIOR=Path(__file__).resolve().parents[1]/"reason-cartridge-016"/"thinker.py"
PRIOR_BLOB="0a2272f6d996c389b0360c2fd4ca8830d1f5bdd2"


def source_pin():
    b=PRIOR.read_bytes()
    sha=sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if sha!=PRIOR_BLOB:
        raise ValueError("Actual earlier REASON-016 reasoner code changed")
    return sha


def closed_vocabulary_control():
    source_pin()
    sys.path.insert(0,str(PRIOR.parent))
    spec=spec_from_file_location("motif_original_reason016_thinker",PRIOR)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    from scenarios import by_id
    old=by_id("SOUP_OR_COMPANY")
    called=[]

    def reply(s,q):
        called.append(q["id"])
        content={
            "case_id":s["id"],"recipient":s["recipient"],
            "consent_revision":s["consent_revision"],
            "source_revision":"motif.reason.synthetic-recipient-oracle.v1",
            "question_id":q["id"],"kind":q["kind"],
            "target_action":q["target"],
            # A reply genuinely outside the earlier finite hypothesis set:
            "answer":"NEITHER_MY_WISH_IS_NOT_IN_YOUR_OPTIONS",
            "declared_fixture_origin":"SYNTHETIC_RECIPIENT_REPLY_NOT_REAL_TESTIMONY",
            "external_contact_performed":False,"human_intent_inferred":False,
        }
        return dict(content,checksum_sha256=module.digest(content))
    try:
        module.choose(old,reply)
    except module.HOLD as exc:
        return {
            "original_reason016_blob":source_pin(),
            "controlled_old_response":"NEITHER_MY_WISH_IS_NOT_IN_YOUR_OPTIONS",
            "previous_reader_result":"HOLD_OUTSIDE_ENUMERATED_PREFERENCE_VOCAB",
            "previous_reader_did_not_invent_a_choice":True,
            "source_exception":str(exc),
            "question_sequence":called,
            "real_human_reply":False,
        }
    raise AssertionError("Old reasoner unexpectedly accepted an unknown source reply")
