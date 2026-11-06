"""Separate scripted source owners and a supervised capability assessor.

- Fictional recipient: controlled contact, exact speaker + revision, limited
  questions and scope-specific consent. Cannot be persuaded to change a NO.
- Synthetic language teacher: releases six labelled training spans only once.
  Evaluates an unseen twelve-item capability challenge without disclosing its
  heldout answers to the learner.

Neither component communicates with an actual person, nor authenticates real
consent. Checksums are reproducible source-owner receipts, not signatures.
"""
from __future__ import annotations

from hashlib import sha256
import json

from cases import by_id
from source_private import (
    SOURCE_VERSION,DIALOGUE,GOAL_ECHOS,
    TRAIN_POSITIVE,TRAIN_NEGATIVE,HELDOUT_POSITIVE,HELDOUT_NEGATIVE,
)


class SourceRefusal(ValueError):
    pass


def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


class Teacher:
    def __init__(self):
        self.training_reads=0
        self.checks=0

    def training(self):
        if self.training_reads:
            raise SourceRefusal("Training labels have already been consumed")
        self.training_reads+=1
        return {
            "source_revision":SOURCE_VERSION,
            "source_kind":"SIMULATED_TEACHER_SUPERVISED_SPANS",
            "training":[{"utterance":s,"desired_span":goal}
                        for s,goal in TRAIN_POSITIVE],
            "negative":list(TRAIN_NEGATIVE),
        }

    def certify(self,model):
        from syntax import SCHEMA,interpret
        if not isinstance(model,dict) or model.get("schema")!=SCHEMA:
            raise SourceRefusal("No learned grammar to independently test")
        correct=sum(interpret(model,s)==goal for s,goal in HELDOUT_POSITIVE)
        rejected=sum(interpret(model,s) is None for s in HELDOUT_NEGATIVE)
        self.checks+=1
        outcome={
            "schema":"motif.reason.golden-mirror-learns.capability-certificate.v1",
            "source_revision":SOURCE_VERSION,
            "model_sha256":digest(model),
            "unseen_positive_total":len(HELDOUT_POSITIVE),
            "unseen_positive_correct":correct,
            "unseen_negative_total":len(HELDOUT_NEGATIVE),
            "unseen_negative_rejected":rejected,
            "source_kind":"SYNTHETIC_HIDDEN_TEMPLATE_CHALLENGES",
            "self_capability_granted":(
                correct==len(HELDOUT_POSITIVE) and
                rejected==len(HELDOUT_NEGATIVE)),
            "real_person_ability_not_measured":True,
            "real_world_authority":False,
        }
        return dict(outcome,checksum_sha256=digest(outcome))


class SyntheticRecipient:
    def __init__(self,case_id):
        self.case=by_id(case_id)
        self.script=DIALOGUE[case_id]
        self.echoes=GOAL_ECHOS[case_id]
        self.turns=[]
        self.next="INITIAL"
        self.confirm_index=0
        self.closed=False

    def reply(self,scene,question):
        if scene!=self.case:
            raise SourceRefusal("Recipient identity, source or consent epoch changed")
        if (not scene["contact_allowed"] or self.closed
                or len(self.turns)>=scene["maximum_source_questions"]):
            raise SourceRefusal("No more authorized simulated recipient contact")
        if not isinstance(question,dict) or set(question)!={"kind","echo","target"}:
            raise SourceRefusal("Out-of-scope or malformed inquiry")
        kind=question["kind"]
        if kind!=self.next:
            raise SourceRefusal("Wrong source-owner dialogue stage")
        if kind=="INITIAL":
            if question["echo"] is not None or question["target"] is not None:
                raise SourceRefusal("Initial query must not project a proposed answer")
            answer=self.script["initial"]
            correction=None
            if answer is None:
                raise SourceRefusal("No scripted initial permission")
            self.next="CONFIRM"
            if "do not contact me" in answer.casefold():
                self.closed=True
        elif kind=="CONFIRM":
            if (question["target"] is not None
                    or self.confirm_index>=len(self.script["confirm"])
                    or question["echo"]!=self.echoes[self.confirm_index]):
                raise SourceRefusal("Reflected quote is not the recipient's actual words")
            answer,correction=self.script["confirm"][self.confirm_index]
            self.confirm_index+=1
            self.next="CONFIRM" if answer=="NO" and correction is not None else (
                "SCOPE" if answer=="YES" else "STOP")
        elif kind=="SCOPE":
            if (question["target"]!="OFFER_OPTIONS_ONLY"
                    or not self.echoes
                    or question["echo"]!=self.echoes[-1]
                    or self.confirm_index!=len(self.script["confirm"])):
                raise SourceRefusal("Permission must be for one named action after correction")
            answer=self.script["scope"]
            correction=None
            if answer not in ("YES","NO"):
                raise SourceRefusal("No simulated scope response exists")
            self.next="STOP"
            self.closed=True
        else:
            raise SourceRefusal("No further approved questions")
        row={
            "schema":"motif.reason.golden-mirror-learns.reply.v1",
            "case_id":scene["id"],"recipient":scene["recipient"],
            "consent_revision":scene["consent_revision"],
            "source_revision":SOURCE_VERSION,
            "question":question,"answer":answer,"correction":correction,
            "source_kind":"SCRIPTED_RECIPIENT_NOT_ACTUAL_PERSON",
            "real_human_contacted":False,
            "permission_to_execute":False,
        }
        row["checksum_sha256"]=digest(row)
        self.turns.append(row)
        return row
