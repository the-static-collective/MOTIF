"""Select an appropriate type of representation using independent task evidence.

Development examples from three published bAbI task families contain actual
gold answers, which are used strictly for supervised *routing and skill
evaluation*. For each example, the solver sees only the source story and
question; withheld test labels never enter the router or reasoning engine.

Source-conditioned weights select among three developer-supplied programs.
This is NOT automatic invention of an arbitrary algorithm, nor new math.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re

from corpus import query_input
from engines import ENGINES,solve

LABELS=("QUANTITY","ORDERED_TIME","TRIADIC_TRANSFER")
SCHEMA="motif.reason022.typed-router.v1"


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,
                             separators=(",",":"),allow_nan=False).encode()).hexdigest()


def question_family(question):
    if re.fullmatch(r"How many objects is [A-Z][a-z]+ carrying\?",question):
        return "CARDINALITY_QUERY"
    if re.fullmatch(r"Where was [A-Z][a-z]+ before the [a-z]+\?",question):
        return "PREDECESSOR_QUERY"
    if re.match(r"(Who |What )",question):
        return "TRIADIC_QUERY"
    return "UNRECOGNIZED"


def discover(training):
    # This is intentionally tiny and transparent: 3 developer-provided
    # classical algorithms, calibrated on 3 independent source task families.
    if not isinstance(training,dict) or set(training)!={"COUNT","TIME","TRANSFER"}:
        raise ValueError("All three independent source training partitions required")
    scores={}
    for task,examples in training.items():
        if not 10<=len(examples)<=150:
            raise ValueError("Source training split missing or unbounded")
        detail={}
        for name in LABELS:
            attempted=0;exact=0;held=0
            for q in examples:
                reply=solve(name,query_input(q))
                if reply["status"]=="ANSWER":
                    attempted+=1
                    if reply["answer"]==q.answer:exact+=1
                else:held+=1
            detail[name]={
                "attempted":attempted,"correct":exact,"held":held,
                "incorrect":attempted-exact,"training_examples":len(examples),
                "exact_per_all":exact/len(examples),
            }
        scores[task]=detail
    selected={}
    for family,methods in scores.items():
        rated=sorted(LABELS,key=lambda x:(-methods[x]["correct"],
                                            methods[x]["incorrect"],x))
        choice=rated[0]
        if methods[choice]["correct"]<max(5,len(training[family])//5):
            raise ValueError("Source tests cannot verify any typed skill")
        selected[family]=choice
    if len(set(selected.values()))!=3:
        raise ValueError("Source evidence did not warrant distinct representations")
    grammar={"COUNT":"CARDINALITY_QUERY","TIME":"PREDECESSOR_QUERY",
             "TRANSFER":"TRIADIC_QUERY"}
    return {
        "schema":SCHEMA,
        "source_training_results":scores,
        "selected_engine_by_external_training_family":selected,
        "question_grammar_to_typed_engine":{
            grammar[task]:engine for task,engine in selected.items()},
        "developer_provided_candidate_engines":list(LABELS),
        "all_original_example_answers_are_supervisor_only":True,
        "no_test_gold_labels_used_to_select_engines":True,
        "no_claim_of_new_language_semantics":True,
        "permission_to_execute":False,
    }


def infer(model,original_query):
    if not isinstance(model,dict) or model.get("schema")!=SCHEMA:
        raise ValueError("Unverified or missing typed representation skill")
    grammar=question_family(original_query["question"])
    family=model["question_grammar_to_typed_engine"].get(grammar)
    if not family:
        return {
            "status":"HOLD","answer":None,"premises":[],
            "representation":None,"reason":"NO_VERIFIED_REPRESENTATION_TYPE",
            "actions_permitted":False,
        }
    return solve(family,original_query)


def boolean_projection_witness(training):
    """Report concrete impossible pairs using source TRAIN labels only.

    An old representation with just question class + binary EXISTS_ANY_FACT
    cannot return two different answers to indistinguishable inputs.
    This is a *weak* classical representation; the goal is to expose where a
    richer type is required, not to prove all Boolean models impossible.
    """
    rows=[]
    for family,examples in training.items():
        seen={}
        match=None
        for q in examples:
            key=(question_family(q.question),bool(q.facts))
            if key in seen and seen[key]["answer"]!=q.answer:
                a=seen[key]
                match={
                    "task":family,"old_boolean_view":{
                        "question_kind":key[0],"has_source_facts":key[1]},
                    "first":{"id":a["id"],"source_gold":a["answer"],
                             "question":a["question"]},
                    "second":{"id":q.id,"source_gold":q.answer,
                              "question":q.question},
                    "different_answer_to_same_old_view":True,
                    "old_representation_is_deliberately_weak":True,
                    "old_boolean_view_insufficient_not_all_boolean_logic":True,
                }
                break
            seen[key]={"id":q.id,"answer":q.answer,"question":q.question}
        rows.append(match or {
            "task":family,"no_source_backed_conflicting_pair_found":True,
        })
    return rows
