"""Simulated *other-person source owner* with enforced contact and revision.

The fictional person can answer eight hypothetical acceptability questions,
disclose a previously omitted condition (or refuse), and separately consent
to only a discussion of options in ONE concrete scenario.

A statement that hypothetical assistance is welcome does NOT grant consent
to communicate, provide assistance, store data or contact the person.
This entire oracle is scripted and neither authenticates nor contacts people.
"""
from __future__ import annotations

from hashlib import sha256
import json

from casebook import by_id,world,ORDER
from source_private import SOURCE_VERSION,HIDDEN,owner_rule


class SourceRefusal(ValueError):
    pass


def digest(payload):
    return sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


class SyntheticOther:
    def __init__(self,case_id):
        self.case=by_id(case_id)
        self.policy,self.new_attribute,self.scope=HIDDEN[case_id]
        self.questions=[]
        self.observations={}
        self.feature_requested=False
        self.done=False

    def _receipt(self,kind,world_id,response):
        body={
            "schema":"motif.reason.other-teaches-self.receipt.v1",
            "case_id":self.case["case_id"],
            "recipient":self.case["recipient"],
            "consent_revision":self.case["consent_revision"],
            "source_version":SOURCE_VERSION,
            "kind":kind,"world_id":world_id,
            "response":response,
            "synthetic_person_not_human_testimony":True,
            "external_contact":False,
            "permission_to_execute":False,
        }
        return dict(body,checksum_sha256=digest(body))

    def _authorize(self,kind):
        if (self.done or not self.case["contact_allowed"]
                or len(self.questions)>=self.case["allowed_source_questions"]):
            raise SourceRefusal("No source permission to continue the inquiry")
        if kind=="OBSERVE" and self.feature_requested:
            raise SourceRefusal("No additional surveys after feature disclosure")

    def answer_hypothetical(self,s,w):
        self._authorize("OBSERVE")
        if s!=self.case or w not in [world(i) for i in ORDER]:
            raise SourceRefusal("Unknown source, training world or consent revision")
        if w["id"] in self.observations:
            raise SourceRefusal("Duplicated personal preference question")
        answer="YES" if owner_rule(self.policy,int(w["id"].split("-")[1])) else "NO"
        self.observations[w["id"]]=answer
        self.questions.append(("OBSERVE",w["id"]))
        return self._receipt("OBSERVE",w["id"],answer)

    def disclose_missing_distinction(self,s,witness):
        self._authorize("FEATURE")
        if s!=self.case or self.feature_requested:
            raise SourceRefusal("No repeated or wrong-person feature request")
        if (len(self.observations)!=8 or
                not isinstance(witness,dict) or set(witness)!={
                    "same_public_features","different_source_answers"}):
            raise SourceRefusal("No complete observation record or paired counterexample")
        pair=witness["different_source_answers"]
        if (not isinstance(pair,list) or len(pair)!=2
                or any(id not in self.observations for id in pair)
                or self.observations[pair[0]]==self.observations[pair[1]]):
            raise SourceRefusal("No actual contradicting source replies")
        wa=world(int(pair[0].split("-")[1]))
        wb=world(int(pair[1].split("-")[1]))
        if (wa["initial_features"]!=wb["initial_features"]
                or witness["same_public_features"]!=wa["initial_features"]):
            raise SourceRefusal("The examples must be indistinguishable in old language")
        self.feature_requested=True
        self.questions.append(("FEATURE",None))
        if self.new_attribute=="NOT_DISCLOSED":
            body={"status":"WITHHELD_BY_SOURCE",
                  "feature_name":None,"world_values":None}
        elif self.new_attribute is None:
            raise SourceRefusal("Current features are sufficient, not contradictory")
        else:
            body={
                "status":"NEW_DECLARED_FEATURE",
                "feature_name":self.new_attribute,
                # Source-owned feature truth for both the queried training
                # worlds and the changed-context heldout worlds. No labels.
                "world_values":{
                    w["id"]:bool(i&1)
                    for split in ("TRAIN","HELDOUT")
                    for i in range(8)
                    for w in [world(i,split)]
                },
            }
        return self._receipt("FEATURE",None,body)

    def consent_to_discussion(self,s,w):
        self._authorize("CONSENT")
        if (s!=self.case or w!=world(self.case["target_context"],"HELDOUT")
                or len(self.observations)!=8):
            raise SourceRefusal("Specific new source target was not justified")
        if not owner_rule(self.policy,self.case["target_context"]):
            raise SourceRefusal("Would-not-welcome an option discussion")
        answer=self.scope
        if answer not in ("YES","NO"):
            raise SourceRefusal("No consent to options discussion available")
        self.questions.append(("CONSENT",w["id"]))
        self.done=True
        return self._receipt("CONSENT",w["id"],answer)
