"""EVALUATOR-OWNED recipient oracle: synthetic replies, never live people.

Only this module may import owner_truth.py. The planner imports neither.
This controlled source simulates a recipient's distinct answers and allows an
independent reviewer to replay the dialogue. A digest is a content checksum,
NOT authentication of a real person or consent.
"""
from __future__ import annotations
from hashlib import sha256
import json

from owner_truth import PROFILE,PERMISSION_REPLY
from scenarios import by_id

SOURCE_REVISION="motif.reason.synthetic-recipient-oracle.v1"


class SourceRefusal(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


class SourceOwner:
    def __init__(self,case_id):
        self.case=by_id(case_id)
        self.profile=PROFILE[case_id]
        self.asked=[]
        self.blocked=False
        self.replies=[]
        if self.profile not in [p["id"] for p in self.case["possible_preferences"]]:
            raise SourceRefusal("Undisclosed profile not in the public hypothesis family")

    def answer(self,scenario,question):
        if scenario != self.case or scenario["consent_revision"]!=self.case["consent_revision"]:
            raise SourceRefusal("Changed person, epoch or preferences")
        if not scenario["permission_to_ask"] or scenario["general_consent"]=="NO":
            raise SourceRefusal("Person never granted permission for contact")
        if self.blocked or question["id"] in self.asked:
            raise SourceRefusal("Consent declined or the question already asked")
        if question not in scenario["questions"] or not question["noncoercive"]:
            raise SourceRefusal("Question not source-approved")
        if len(self.asked)>=scenario["max_questions"]:
            raise SourceRefusal("Exceeded allowed interruptions")
        self.asked.append(question["id"])
        if question["kind"]=="PREFERENCE":
            response=question["partition"][self.profile]
        elif question["kind"]=="CONSENT":
            response=PERMISSION_REPLY.get((scenario["id"],question["target"]),"NO")
        else:
            raise SourceRefusal("Unknown information source")
        if question["kind"]=="CONSENT" and response=="NO":
            self.blocked=True
        record={
            "case_id":scenario["id"],"recipient":scenario["recipient"],
            "consent_revision":scenario["consent_revision"],
            "source_revision":SOURCE_REVISION,
            "question_id":question["id"],"kind":question["kind"],
            "target_action":question["target"],"answer":response,
            "declared_fixture_origin":"SYNTHETIC_RECIPIENT_REPLY_NOT_REAL_TESTIMONY",
            "external_contact_performed":False,
            "human_intent_inferred":False,
        }
        record["checksum_sha256"]=digest(record)
        self.replies.append(record)
        return record
