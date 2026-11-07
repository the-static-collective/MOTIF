"""RING-010: induce graph-edge rewriting rules from contrastive semantic *graphs*.

This does not take a prewritten list of semantic cue words or individual
rewrite definitions. It discovers:
  - which typed graph relations changed between paired target graphs,
  - which *source text relational cues* distinguish the paired readings,
  - whether those cue tokens precede/follow the observed event action,
  - data-only REPLACE_TYPED_EDGE transformations with source support.

The execution opcode and graph relation *universe* exist in the source
contract. New rule instances and graph edit compositions are data-generated
and cannot authorize actions or invent arbitrary Python.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import sha256
import json
import math
import re
import world

SCHEMA="motif.ring010.derived-typed-graph-rewrite-program.v1"
CODE_OPS=("RELATIONAL_CUE_BEFORE_EVENT","RELATIONAL_CUE_AFTER_EVENT",
          "REPLACE_TYPED_EDGE")
MAX_RULES=500
PLACEHOLDERS={"<speaker>","<agent>","<verb>","<patient>"}

class HOLD(ValueError):
    pass


def digest(v):
    return world.digest(v)


def tokenize(s):
    if type(s) is not str or not 1<=len(s)<=320:
        raise HOLD("Malformed or oversized language observation")
    return re.findall(r"[a-z]+",s.casefold())


def abstract(text,observed):
    """External observed event is required; this is NOT open-domain NER."""
    if not isinstance(observed,dict) or set(observed)!={
            "speaker","agent","verb","patient"}:
        raise HOLD("Independently supplied bound event required")
    words=tokenize(text)
    key={value.casefold():"<"+role+">" for role,value in observed.items()
         if type(value) is str}
    if len(key)!=4:
        raise HOLD("Ambiguous lexical event bindings")
    result=[key.get(x,x) for x in words]
    if result.count("<verb>")!=1:
        raise HOLD("No unique observed-event action in the utterance")
    if any(x not in result for x in ("<speaker>","<agent>","<patient>")):
        raise HOLD("Unbound actor/patient mention")
    return result


def graphmap(graph):
    if not isinstance(graph,dict) or graph.get("schema")!=world.GRAPH_SCHEMA:
        raise HOLD("Wrong graph source")
    return {row[1]:row[2] for row in graph["edges"]}


def ngrams(words,n):
    result=set()
    for length in range(1,min(n,len(words))+1):
        for i in range(len(words)-length+1):
            cue=tuple(words[i:i+length])
            if not any(s in PLACEHOLDERS for s in cue):
                result.add(cue)
    return result


def cue_position(words,cue):
    pos=words.index("<verb>")
    positions=[]
    n=len(cue)
    for i in range(len(words)-n+1):
        if tuple(words[i:i+n])!=cue:
            continue
        if i+n<=pos:
            positions.append(("RELATIONAL_CUE_BEFORE_EVENT",pos-i-n))
        elif i>pos:
            positions.append(("RELATIONAL_CUE_AFTER_EVENT",i-pos-1))
    return positions


def differences(a,b):
    ma,mb=graphmap(a),graphmap(b)
    if set(ma)!=set(world.RELATIONS) or set(mb)!=set(world.RELATIONS):
        raise HOLD("Graph relation universe mismatch")
    delta=[]
    for rel in world.RELATIONS:
        if ma[rel]!=mb[rel]:
            node="EVENT" if rel=="POLARITY" else "UTTERANCE"
            delta.append({
                "opcode":"REPLACE_TYPED_EDGE",
                "source":[node,rel,ma[rel]],
                "target":[node,rel,mb[rel]],
            })
    return delta


def construct(train,*,min_support=3,max_cue=3,max_gap=12,purity=0.9):
    world.check(train,split="train")
    if (type(min_support) is not int or not 1<=min_support<=20
            or type(max_cue) is not int or not 1<=max_cue<=4
            or type(max_gap) is not int or not 0<=max_gap<=24
            or type(purity) is not float or purity not in (0.8,0.9,0.96,1.0)):
        raise HOLD("Invalid induction space")
    stats=Counter()
    edits=Counter()
    relation_priors=defaultdict(Counter)
    usable=0
    for pair in train["pairs"]:
        a,b=pair["a"],pair["b"]
        event=a["observed_event"]
        try:
            sa=abstract(a["text"],event)
            sb=abstract(b["text"],event)
        except HOLD:
            continue
        delta=differences(a["semantic_graph"],b["semantic_graph"])
        if not delta:
            continue
        usable+=1
        for op in delta:
            edits[(op["source"][1],op["source"][2],
                   op["target"][2])]+=1
        ea,eb=graphmap(a["semantic_graph"]),graphmap(b["semantic_graph"])
        for arm,other,vals in ((sa,sb,ea),(sb,sa,eb)):
            other_cues=ngrams(other,max_cue)
            unique=ngrams(arm,max_cue)-other_cues
            for rel in world.RELATIONS:
                relation_priors[rel][vals[rel]]+=1
            changed={op["source"][1] for op in delta}
            for rel in changed:
                for cue in unique:
                    for opcode,gap in cue_position(arm,cue):
                        if gap<=max_gap:
                            stats[(rel,vals[rel],opcode,cue)]+=1
    if usable<8:
        raise HOLD("Insufficient source-bound graph contrasts")
    rules=[]
    for (rel,value,opcode,cue),support in sorted(stats.items()):
        conflicting=sum(n for (rr,vv,oo,cc),n in stats.items()
                        if rr==rel and vv!=value and oo==opcode and cc==cue)
        correctness=support/max(1,support+conflicting)
        if support<min_support or correctness<purity:
            continue
        rules.append({
            "opcode":opcode,
            "relation":rel,
            "value":value,
            "cue":list(cue),
            "support":support,
            "conflicting_source_contrasts":conflicting,
            "training_purity":round(correctness,6),
            "derived_from":"PAIRED_TYPED_GRAPH_DIFF_AND_LEXICAL_CONTEXT",
        })
    rules.sort(key=lambda x:(-len(x["cue"]),-x["support"],
                              x["relation"],x["cue"],x["value"]))
    rules=rules[:MAX_RULES]
    if not rules:
        raise HOLD("No source-supported graph edit operators induced")
    transitions=[
        {"opcode":"REPLACE_TYPED_EDGE",
         "relation":rel,"from":before,"to":after,"source_pairs":n}
        for (rel,before,after),n in sorted(edits.items())
    ]
    defaults={}
    for rel,values in relation_priors.items():
        best,count=values.most_common(1)[0]
        # Explicitly limited default: source-created polarity baseline only.
        # Force/scope MUST be evidenced by an observed cue.
        if rel=="POLARITY":
            defaults[rel]=best
    program={
        "schema":SCHEMA,
        "source_training_sha256":train["receipt_sha256"],
        "source_pairs":len(train["pairs"]),
        "usable_contrast_pairs":usable,
        "developer_defined_instruction_set":list(CODE_OPS),
        "source_derived_transition_operator_instances":transitions,
        "source_derived_contextual_cue_operators":rules,
        "derived_transition_count":len(transitions),
        "derived_cue_count":len(rules),
        "one_bounded_relation_default":defaults,
        "parameters":{
            "min_support":min_support,
            "max_cue":max_cue,
            "max_gap":max_gap,
            "purity":purity,
        },
        "observed_event_context_required":True,
        "speaker_agent_action_patient_not_inferred_from_free_text":True,
        "new_base_computational_primitive_invented":False,
        "graph_edits_untrusted_semantic_hypotheses_only":True,
        "execution_authority":"NONE",
    }
    program["receipt_sha256"]=digest(program)
    return program


def validate(program):
    if (not isinstance(program,dict) or program.get("schema")!=SCHEMA
            or program.get("developer_defined_instruction_set")!=list(CODE_OPS)
            or program.get("execution_authority")!="NONE"
            or program.get("observed_event_context_required") is not True
            or program.get("new_base_computational_primitive_invented") is not False
            or program.get("derived_transition_count")!=len(
                program.get("source_derived_transition_operator_instances",[]))
            or program.get("derived_cue_count")!=len(
                program.get("source_derived_contextual_cue_operators",[]))
            or not 1<=program["derived_cue_count"]<=MAX_RULES
            or program.get("receipt_sha256")!=digest({
                k:v for k,v in program.items() if k!="receipt_sha256"})):
        raise HOLD("Tampered or unlimited semantic graph program")
    for op in program["source_derived_transition_operator_instances"]:
        if (op.get("opcode")!="REPLACE_TYPED_EDGE"
                or op.get("relation") not in world.RELATIONS
                or op.get("from") not in world.VALUES[op["relation"]]
                or op.get("to") not in world.VALUES[op["relation"]]
                or op["from"]==op["to"]
                or type(op.get("source_pairs")) is not int or op["source_pairs"]<1):
            raise HOLD("Unreviewed relation transition")
    for op in program["source_derived_contextual_cue_operators"]:
        if (op.get("opcode") not in CODE_OPS[:2]
                or op.get("relation") not in world.RELATIONS
                or op.get("value") not in world.VALUES[op["relation"]]
                or not isinstance(op.get("cue"),list)
                or not 1<=len(op["cue"])<=4
                or any(not re.fullmatch(r"[a-z]+",x) for x in op["cue"])
                or type(op.get("support")) is not int or op["support"]<1):
            raise HOLD("Unapproved language-to-graph operator")
    return program


def matches(words,op,max_gap):
    if "<verb>" not in words:
        return False
    action=words.index("<verb>")
    cue=op["cue"]
    for i in range(len(words)-len(cue)+1):
        if words[i:i+len(cue)]!=cue:
            continue
        if op["opcode"]=="RELATIONAL_CUE_BEFORE_EVENT":
            gap=action-(i+len(cue))
        else:
            gap=i-action-1
        if 0<=gap<=max_gap:
            return True
    return False


def parse(program,text,observed):
    validate(program)
    raw=sha256(text.encode()).hexdigest() if type(text) is str else None
    try:
        words=abstract(text,observed)
    except HOLD as exc:
        return {"status":"HOLD","semantic_graph":None,
                "reason":"SOURCE_EVENT_BINDING_UNRESOLVED",
                "detail":str(exc),"source_text_sha256":raw,
                "source_graph_edits":[]}
    grouped=defaultdict(lambda:defaultdict(list))
    for op in program["source_derived_contextual_cue_operators"]:
        if matches(words,op,program["parameters"]["max_gap"]):
            grouped[op["relation"]][op["value"]].append(op)
    assignments={}
    proofs=[]
    for rel in world.RELATIONS:
        options=grouped.get(rel,{})
        if not options:
            if rel in program["one_bounded_relation_default"]:
                assignments[rel]=program["one_bounded_relation_default"][rel]
                proofs.append({"relation":rel,"value":assignments[rel],
                               "operator":"SOURCE_PRIOR_DEFAULT_NOT_WORLD_PROOF"})
                continue
            return {"status":"HOLD","semantic_graph":None,
                    "reason":"NO_DISCRIMINATING_RELATION_CUE",
                    "unresolved_relation":rel,"source_text_sha256":raw,
                    "source_graph_edits":proofs}
        scores=[]
        for value,operators in options.items():
            strongest=max(operators,key=lambda x:(
                len(x["cue"]),x["support"]-x["conflicting_source_contrasts"]))
            scores.append((len(strongest["cue"]),strongest["support"]
                           -strongest["conflicting_source_contrasts"],
                           value,strongest))
        scores.sort(reverse=True,key=lambda x:(x[0],x[1],x[2]))
        if (len(scores)>1
                and scores[0][0:2]==scores[1][0:2]
                and scores[0][2]!=scores[1][2]):
            return {"status":"HOLD","semantic_graph":None,
                    "reason":"CONFLICTING_TYPED_RELATIONAL_EVIDENCE",
                    "unresolved_relation":rel,
                    "source_text_sha256":raw,"source_graph_edits":proofs}
        value=scores[0][2]
        assignments[rel]=value
        proofs.append({
            "opcode":"REPLACE_TYPED_EDGE",
            "relation":rel,
            "value":value,
            "cue":scores[0][3]["cue"],
            "position":scores[0][3]["opcode"],
            "source_support":scores[0][3]["support"],
            "speaker_agent_action_patient_source":"PUBLIC_OBSERVED_EVENT",
        })
    if set(assignments)!=set(world.RELATIONS):
        raise HOLD("Missing graph semantics after induction")
    graph=world.graph(tuple(assignments[rel] for rel in world.RELATIONS))
    return {
        "status":"NONAUTHORITATIVE_TYPED_GRAPH_HYPOTHESIS",
        "semantic_graph":graph,
        "source_text_sha256":raw,
        "source_graph_edits":proofs,
        "source_event_bindings_required":True,
        "real_world_speaker_or_intent_verified":False,
        "external_action_authority":"NONE",
    }
