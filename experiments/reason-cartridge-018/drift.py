"""A *new-source-version* exception that invalidates an otherwise accurate concept.

The original REASON-018 concept was learned against a CLOSED vocabulary of six
relations. This source-owned counterexample supplies a **seventh**, previously
unrepresented relationship: the recipient has WITHDRAWN permission. No amount
of correct inference in the old graph proves the new source revision false.

This synthetic case tests epistemic humility and explicit HOLD, not model
autonomy, live consent, or spontaneous logic invention.
"""
from __future__ import annotations

from hashlib import sha256
import json

from worlds import make,RELATIONS
from inventor import HOLD,digest,suggest
from oracle import source_label


NEW_SOURCE_REVISION="motif.reason.living-concept.correction-v2"
NEW_RELATION="WITHDRAWN"
NEW_OUTCOME="REFUTED"


def source_revision():
    w=make(0,"HELDOUT")
    original=source_label(w)
    if original["status"]!="SUPPORTED":
        raise AssertionError("The intentionally contradicted old example changed")
    assert NEW_RELATION not in RELATIONS
    body={
        "schema":"motif.reason.living-concept.exception-source-v2",
        "source_revision":NEW_SOURCE_REVISION,
        "original_case_id":w["id"],
        "original_graph_sha256":digest(w),
        "observed_new_relation":NEW_RELATION,
        "new_fact":["WITHDRAWN",w["recipient"],w["actor"]],
        "original_four_state":original["status"],
        "new_four_state":NEW_OUTCOME,
        "revision_makes_old_permission_inapplicable":True,
        "new_relation_not_in_original_grammar":True,
        "only_a_synthetic_source_correction":True,
        "contacted_a_real_person":False,
        "permission_to_act":False,
    }
    return dict(body,checksum_sha256=digest(body))


def detect(model,packet):
    expected=source_revision()
    if not isinstance(packet,dict) or packet!=expected:
        raise HOLD("Unverified synthetic new-source correction, claim or checksum")
    w=make(0,"HELDOUT")
    previous=suggest(model,w)
    if previous["status"]!="SUPPORTED" or packet["new_four_state"]==previous["status"]:
        raise HOLD("An invented change in semantics has no source-grounded witness")
    if packet["observed_new_relation"] in RELATIONS:
        raise HOLD("No new unknown conceptual primitive detected")
    return {
        "schema":"motif.reason.living-concept.source-drift-review.v1",
        "original_world":w["id"],
        "original_world_sha256":digest(w),
        "old_model_reported":previous["status"],
        "new_author_owned_evidence":packet["new_fact"],
        "new_source_owner_outcome":packet["new_four_state"],
        "old_grammar_cannot_express_new_relation":True,
        "result":"HOLD_NEW_SOURCE_FEATURE_REQUIRES_FRESH_LEARNING",
        "old_model_revised_automatically":False,
        "no_claim_that_source_correction_is_real_human_consent":True,
        "no_external_actions":True,
    }
