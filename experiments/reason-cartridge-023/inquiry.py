"""Bounded *active inquiry* over genuinely competing source-backed answers.

An ASK is a hypothetical, not permission to contact anyone. The candidate
question partitions the finite set of explicit alternatives and maximizes
expected information gain under a *stated artificial uniform prior*.
This does not infer a human's actual preferences and cannot decide whether
a historical bAbI dataset author meant one option rather than another.

The scripted source may refuse a question or revoke contact at any time.
NO automatic execution is granted, even if the synthetic source clarifies.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations
import json
import math

SCHEMA="motif.reason023.counterfactual-question.v1"
MAX_ALTS=16


class HOLD(ValueError):
    pass


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def binary_entropy(p):
    if p<=0 or p>=1:return 0.0
    return -p*math.log2(p)-(1-p)*math.log2(1-p)


def select_question(alternatives):
    if not isinstance(alternatives,list) or not 2<=len(alternatives)<=MAX_ALTS:
        return None
    if any(not isinstance(x,str) or not x or len(x)>100 for x in alternatives):
        raise HOLD("An ungrounded candidate was offered as a source answer")
    choices=tuple(sorted(set(alternatives)))
    if len(choices)!=len(alternatives):raise HOLD("Non-unique candidate answers")
    # Balanced binary partitions maximize entropy under uniform uncertainty.
    # Enumerate only smaller-half subsets, no arbitrary giant search tree.
    count=len(choices);k=count//2
    choicesets=[tuple(t) for t in combinations(choices,k)]
    def utility(group):
        p=len(group)/count
        return binary_entropy(p)
    selected=min(choicesets,key=lambda group:(-utility(group),group))
    gain=utility(selected)
    if gain<=0:raise HOLD("No useful question can distinguish the alternatives")
    return {
        "schema":SCHEMA,
        "question":"Is the intended answer among: "+", ".join(selected)+"?",
        "if_yes":list(selected),
        "if_no":[s for s in choices if s not in selected],
        "candidate_set":list(choices),
        "model_assumption":"ARTIFICIAL_UNIFORM_PRIOR_NOT_A_CALIBRATED_BELIEF",
        "binary_question_information_gain_bits":round(gain,6),
        "source_contact_permitted_by_question_selection":False,
        "external_actions":False,
    }


class SyntheticClarifier:
    """Fictional source; held target is NOT exposed to the question selector."""
    def __init__(self,correct,*,contact=True,question_permission=True,
                 refuse=False,maximum_questions=3,revision=1):
        self.target=correct
        self.contact=contact;self.question_permission=question_permission
        self.refuse=refuse;self.maximum_questions=maximum_questions
        self.revision=revision;self.asked=0
        self.events=[]

    def ask(self,question):
        if (not self.contact or not self.question_permission
                or self.asked>=self.maximum_questions):
            raise HOLD("Source did not authorize inquiry")
        if (not isinstance(question,dict) or question.get("schema")!=SCHEMA
                or self.target not in question["candidate_set"]):
            raise HOLD("Question refers to an unrepresented source choice")
        self.asked+=1
        if self.refuse:
            response="DECLINE"
        else:
            response=("YES" if self.target in question["if_yes"] else "NO")
        record={
            "question":question,"response":response,"source_revision":self.revision,
            "fictional_source_not_real_consent":True,
            "real_contact_performed":False,"permission_to_execute":False,
        }
        self.events.append(record)
        return record


def investigate(graph,owner=None):
    if not isinstance(graph,dict) or graph.get("schema")!="motif.reason023.source-graph.v1":
        raise HOLD("No independently supported source graph")
    options=sorted(c["answer"] for c in graph["candidates"])
    if graph["status"]=="ANSWER" and len(options)==1:
        stage="SOURCE_UNIQUE_READ_ONLY";chosen=options[0]
    elif len(options)<2:
        stage="HOLD_NOT_ENOUGH_SOURCE_EVIDENCE";chosen=None
    elif owner is None:
        stage="HOLD_AMBIGUITY_NEEDS_SOURCE_PERMISSION";chosen=None
    elif not owner.contact or not owner.question_permission:
        stage="HOLD_NO_QUESTION_PERMISSION";chosen=None
    else:
        current=options;chosen=None;stage="HOLD_QUESTION_BUDGET"
        while len(current)>1:
            candidate=select_question(current)
            if candidate is None:break
            try:answer=owner.ask(candidate)
            except HOLD:
                stage="HOLD_QUESTION_BUDGET";break
            if answer["response"]=="DECLINE":
                stage="HOLD_SOURCE_REFUSED";break
            if answer["response"] not in ("YES","NO"):
                raise HOLD("Source gave an unsupported answer")
            current=(candidate["if_yes"] if answer["response"]=="YES"
                     else candidate["if_no"])
            if not current:raise HOLD("Clarification erased every source alternative")
        if len(current)==1 and stage not in ("HOLD_SOURCE_REFUSED",):
            chosen=current[0];stage="CLARIFIED_SYNTHETIC_READ_ONLY"
    if chosen is not None and chosen not in options:
        raise HOLD("Source clarification invented an answer")
    return {
        "schema":"motif.reason023.inquiry-receipt.v1",
        "origin_source_graph_sha256":digest(graph),
        "stage":stage,
        "original_source_supported_candidates":options,
        "current_source_hypothesis":chosen,
        "provenance_for_clarified_choice":next((
            c["support"] for c in graph["candidates"] if c["answer"]==chosen),[]),
        "questions":[x for x in owner.events] if owner is not None else [],
        "not_an_historical_dataset_author_clarification":True,
        "separate_contact_permission_required":True,
        "model_does_not_assume_what_real_people_need":True,
        "permission_to_execute":False,"external_actions":False,
    }
