"""RING-012: ambiguity-first perspective lattice, not one forced winning meaning.

For every bounded source utterance:
 * preserve each original method's nonauthoritative typed graph hypothesis;
 * preserve contradictions between observed source methods;
 * compose SOURCE-CONDITIONAL possibilities for force/scope/polarity;
 * attach the documented carrier WITHOUT asserting carrier=event truth;
 * retain an unmodeled reading in an OPEN-WORLD state even on unanimity.

The original RING-011 source-derived graph binder and two same-training
classical controls share a corpus, so their apparent agreement is CORRELATED
evidence, never independent corroboration. This module never executes actions.

Unrecognized event bindings -> explicit unresolved with NO invented graph.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import itertools
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-011"))
import binder,benchmark,corpus

SCHEMA="motif.ring012.open-perspective-lattice.v1"
METHODS=("derived_binder","word_bayes","bigram_bayes")
RELATIONS=corpus.RELATIONS
MAX_CONCRETE_WORLDS=24
THRESHOLDS=(0.0,0.25,0.5,0.75)
NOVELTY_THRESHOLDS=(0.20,0.45,0.75,1.01)

class HOLD(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()


def relation_key(rel):
    return ("ROOT","FORCE") if rel=="ROOT_FORCE" else (
        ("EVENT","SCOPE") if rel=="EVENT_SCOPE" else ("EVENT","POLARITY"))


def values(graph):
    if graph is None:
        return None
    edges=corpus.graph_map(graph)
    return {rel:edges[relation_key(rel)] for rel in RELATIONS}


class Sources:
    """Three reviewed, pinned nonauthority interpreters of SAME source text."""
    def __init__(self,train,program):
        corpus.validate(train,split="train")
        binder.validate(program)
        if program["source_train_sha256"]!=train["receipt_sha256"]:
            raise HOLD("Binder not trained on supplied original source")
        rows=corpus.flatten(train)
        self.methods={
            "derived_binder":lambda text,event,carrier:
                binder.predict(program,text,event,carrier),
            "word_bayes":benchmark.Bayes(rows,mode="WORD").parse,
            "bigram_bayes":benchmark.Bayes(rows,mode="BIGRAM").parse,
        }
        self._cache={}
        self.train_sha256=train["receipt_sha256"]
        self.program_sha256=program["receipt_sha256"]
        # Learn only the original corpus vocabulary, not future labels.
        lex=set()
        for row in rows:
            abstract=binder.abstract(row["text"],row["observed_event"])
            lex.update(token for token in abstract["tokens"]
                       if token.isalpha())
        self.lexicon=tuple(sorted(lex))

    def infer(self,utterance,event,carrier):
        key=digest({"text":utterance,"event":event,"carrier":carrier})
        if key in self._cache:
            return self._cache[key]
        if carrier not in corpus.CARRIERS:
            raise HOLD("Unapproved source carrier")
        raw={}
        for name,method in self.methods.items():
            try:
                result=method(utterance,event,carrier)
            except (binder.HOLD,ValueError) as exc:
                result={"status":"HOLD","graph":None,
                        "reason":"SOURCE_METHOD_BOUNDARY",
                        "description":str(exc)}
            hypothesis=result.get("graph")
            # Source methods must never change the event's documentary
            # carrier, nor claim any external operative authority.
            if hypothesis is not None:
                parsed=corpus.graph_map(hypothesis)
                if (parsed[("DOCUMENT","CARRIER")]!=carrier
                        or parsed[("DOCUMENT","EVIDENCE_STATUS")]!=corpus.EPISTEMIC[carrier]
                        or result.get("external_effect_permission","NONE")!="NONE"):
                    raise HOLD("Non-authoritative source method altered provenance")
            raw[name]={
                "semantic_roles":values(hypothesis),
                "method_status":result.get("status","HOLD"),
                "method_result_sha256":digest(result),
                "method_could_not_establish_graph":hypothesis is None,
            }
        self._cache[key]=raw
        return raw


def novelty_fraction(text,event,source_lexicon):
    try:
        abstract=binder.abstract(text,event)
    except binder.HOLD:
        return 1.0,False
    relevant=[w for w in abstract["tokens"] if w.isalpha()]
    unknown=sum(w not in source_lexicon for w in relevant)
    return (unknown/max(1,len(relevant))),True


def validate_policy(policy):
    if (not isinstance(policy,dict)
            or policy.get("schema")!="motif.ring012.calibrated-open-lattice.v1"
            or policy.get("authority")!="NONE"
            or policy.get("all_method_claims_correlated") is not True
            or policy.get("open_world_always") is not True
            or policy.get("outside_effects_forbidden") is not True
            or policy.get("explicit_source_graph_ontology") is not True
            or policy.get("source_train_sha256") is None
            or policy.get("derived_program_sha256") is None
            or policy.get("params",{}).get("vote_threshold") not in THRESHOLDS
            or policy["params"].get("novelty_threshold") not in NOVELTY_THRESHOLDS
            or type(policy["params"].get("widen_on_disagreement")) is not bool
            or policy.get("receipt_sha256")!=digest({
                k:v for k,v in policy.items() if k!="receipt_sha256"})):
        raise HOLD("Changed or overauthorized ambiguity policy")
    lex=policy.get("source_vocabulary")
    if (not isinstance(lex,list) or lex!=sorted(set(lex))
            or any(type(x) is not str or not x.isalpha() for x in lex)):
        raise HOLD("Unbounded or forged language-source vocabulary")
    return policy


def combine(utterance,event,carrier,source,policy):
    """Return a set-valued graph state; NEVER a tool/action instruction."""
    validate_policy(policy)
    if (source.train_sha256!=policy["source_train_sha256"]
            or source.program_sha256!=policy["derived_program_sha256"]
            or list(source.lexicon)!=policy["source_vocabulary"]):
        raise HOLD("Unmatched original trained method portfolio")
    if carrier not in corpus.CARRIERS:
        raise HOLD("Unknown documentary carrier")
    raw_sha=sha256(utterance.encode()).hexdigest() if type(utterance) is str else None
    if (type(utterance) is not str or not 1<=len(utterance)<=320
            or not isinstance(event,dict)
            or set(event)!=set(corpus.LEX)):
        return {
            "schema":SCHEMA,"source_sha256":raw_sha,
            "status":"UNRESOLVED_SOURCE",
            "supported_worlds":[],
            "other_unmodeled_readings_remain_possible":True,
            "epistemic_carrier":carrier,
            "reason":"MISSING_OR_INVALID_SOURCE_EVENT",
            "source_methods":{},"source_disagreements":[],
            "root_action_authorized":False,"external_action_executed":False,
            "authority":"NONE",
        }
    novelty,valid=novelty_fraction(utterance,event,set(source.lexicon))
    if not valid:
        return {
            "schema":SCHEMA,"source_sha256":raw_sha,
            "status":"UNRESOLVED_SOURCE",
            "supported_worlds":[],
            "other_unmodeled_readings_remain_possible":True,
            "epistemic_carrier":carrier,
            "reason":"UNBOUND_OBSERVED_EVENT",
            "source_methods":{},"source_disagreements":[],
            "root_action_authorized":False,"external_action_executed":False,
            "authority":"NONE",
        }
    predictions=source.infer(utterance,event,carrier)
    candidates={x:Counter() for x in RELATIONS}
    for name,evidence in predictions.items():
        parsed=evidence["semantic_roles"]
        if parsed is None:continue
        for rel in RELATIONS:
            candidates[rel][parsed[rel]]+=1
    if any(not rows for rows in candidates.values()):
        return {
            "schema":SCHEMA,"source_sha256":raw_sha,
            "status":"UNRESOLVED_SOURCE","supported_worlds":[],
            "other_unmodeled_readings_remain_possible":True,
            "epistemic_carrier":carrier,
            "source_methods":predictions,
            "source_disagreements":[],
            "novelty_fraction":round(novelty,4),
            "reason":"NO_FULL_METHOD_GRAPH_SUPPORTED",
            "root_action_authorized":False,
            "external_action_executed":False,"authority":"NONE",
        }
    threshold=policy["params"]["vote_threshold"]
    high_novelty=novelty>=policy["params"]["novelty_threshold"]
    conflict=any(len(counts)>1 for counts in candidates.values())
    widen=(high_novelty or (conflict and policy["params"]["widen_on_disagreement"]))
    possibilities={}
    disagreements=[]
    for rel,counted in candidates.items():
        total=sum(counted.values())
        if widen:
            vals=list(corpus.VALUES[rel])
        else:
            vals=[x for x,n in counted.items() if n/total>=threshold]
            if not vals:
                vals=[max(counted,key=lambda x:(counted[x],x))]
        possibilities[rel]=sorted(set(vals))
        if len(counted)>1:
            disagreements.append({
                "relation":rel,
                "competing_nonindependent_source_readings":dict(counted),
                "reason":"REVIEWED_METHODS_DISAGREE_KEEP_MULTIPLE",
            })
    if (len(possibilities["ROOT_FORCE"])*len(possibilities["EVENT_SCOPE"])
            *len(possibilities["EVENT_POLARITY"])>MAX_CONCRETE_WORLDS):
        raise HOLD("Too many graph assignments in bounded source ontology")
    worlds=[
        corpus.frame(force,scope,polarity,carrier,event)
        for force,scope,polarity in itertools.product(
            possibilities["ROOT_FORCE"],
            possibilities["EVENT_SCOPE"],
            possibilities["EVENT_POLARITY"],
        )
    ]
    # Every graph is a source hypothesis, *not* an event claim or effectful
    # instruction. Even a set containing only one graph remains open-world.
    return {
        "schema":SCHEMA,
        "source_sha256":raw_sha,
        "status":("MULTIPLE_SUPPORTED_PERSPECTIVES"
                  if len(worlds)>1 else "SINGLE_SUPPORTED_PERSPECTIVE_OPEN_WORLD"),
        "supported_worlds":worlds,
        "supported_world_count":len(worlds),
        "other_unmodeled_readings_remain_possible":True,
        "epistemic_carrier":carrier,
        "carrier_truth_authenticated":False,
        "source_methods":predictions,
        "source_disagreements":disagreements,
        "novelty_fraction":round(novelty,4),
        "broadened_by_source_novelty_or_conflict":widen,
        "method_agreement_is_independent_corroboration":False,
        "root_action_merely_possible":any(
            corpus.graph_map(g)[("EVENT","REQUESTED_BY_ROOT")] is True
            for g in worlds),
        "root_action_authorized":False,
        "external_action_executed":False,"authority":"NONE",
    }
