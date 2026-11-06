"""Synthetic recipient source, separate from the planner.

A reply exists only for an allowed question, the exact version, and the
current scripted turn. The engine cannot import source_owner_private.py.
The source's checksum is useful for source-owned replay, not proof of
authentic consent from a real person.
"""
from __future__ import annotations
from hashlib import sha256
import json

from casebook import by_id
from source_owner_private import DIALOGUE,SOURCE_REVISION


class SourceRefusal(ValueError):
    pass


def hash_payload(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


class SyntheticPerson:
    def __init__(self,case_id):
        self.case=by_id(case_id)
        self.script=DIALOGUE[case_id]
        self.turns=0
        self.confirms=0
        self.stopped=False
        self.history=[]

    def answer(self,scenario,question):
        if scenario!=self.case:
            raise SourceRefusal("Changed source owner, time or recipient data")
        if not isinstance(question,dict) or set(question)!={"kind","echo","target"}:
            raise SourceRefusal("Unrecognized request")
        if (self.stopped or not self.case["contact_authorized"]
                or self.case["previous_consent"]=="NO"):
            raise SourceRefusal("No contact authority; recipient has declined")
        if self.turns>=self.case["question_budget"]:
            raise SourceRefusal("Too many interruptions")
        kind=question["kind"]
        if self.turns==0:
            if question!={"kind":"INITIAL","echo":None,"target":None}:
                raise SourceRefusal("The recipient was not asked an initial question")
            response=self.script["initial"]
            if response is None:raise SourceRefusal("No initial testimony authorized")
        elif kind=="CONFIRM":
            entries=self.script["confirms"]
            if self.confirms>=len(entries):
                raise SourceRefusal("No further clarification granted")
            confirmation=entries[self.confirms]
            if question["echo"]!=confirmation["echo"] or question["target"] is not None:
                raise SourceRefusal("Echo must accurately quote the person's correction")
            response=(confirmation["correction"] if confirmation["answer"]=="NO"
                      else "YES")
            self.confirms+=1
        elif kind=="SCOPE_PERMISSION":
            if self.confirms!=len(self.script["confirms"]):
                raise SourceRefusal("Consent was sought before understanding")
            if (question["target"]!="OFFER_OPTIONS_ONLY" or
                    not self.script["confirms"] or
                    question["echo"]!=self.script["confirms"][-1]["echo"]):
                raise SourceRefusal("Wrong action, target phrase or scope")
            response=self.script["permission"]
            if response not in ("YES","NO"):
                raise SourceRefusal("No permission answer available")
        else:
            raise SourceRefusal("Unapproved question type or sequence")
        entry={
            "case_id":self.case["case_id"],
            "recipient":self.case["recipient"],
            "consent_revision":self.case["consent_revision"],
            "source_revision":SOURCE_REVISION,
            "question":question,
            "answer":response,
            "source_class":"SYNTHETIC_RECIPIENT_TESTIMONY_ONLY",
            "actual_human_contact":False,
            "permission_to_execute":False,
        }
        entry["sha256"]=hash_payload(entry)
        self.turns+=1
        self.history.append(entry)
        if kind=="SCOPE_PERMISSION" and response=="NO":
            self.stopped=True
        if kind=="INITIAL" and isinstance(response,str) and (
                "stop contacting me" in response.casefold()
                or "leave me alone" in response.casefold()):
            self.stopped=True
        return entry
