"""RING-010 source-authored graph contrasts; the learner never sees templates.

The same observed event node and its four source attributes are provided
separately from utterance text. The task is to infer an *utterance-semantics*
relational graph (force, scope, event polarity), not to perform named-entity
recognition from unrestricted English or to authenticate source reality.

Each pair shares the *same action/event* and differs only in utterance
modality, quotation, negation, condition or counterfactual scope.
Ground-truth graphs are author-defined and synthetically generated.
"""
from __future__ import annotations
from hashlib import sha256
import json
import random

SCHEMA="motif.ring010.contrastive-event-semantics.v1"
GRAPH_SCHEMA="motif.ring010.typed-utterance-graph.v1"
NODES=("UTTERANCE","EVENT")
RELATIONS=("FORCE","SCOPE","POLARITY")
VALUES={
    "FORCE":("DIRECTIVE","ASSERTION","MENTION"),
    "SCOPE":("ROOT","IMAGINED","QUOTED","CONDITIONAL"),
    "POLARITY":("POS","NEG"),
}
SEEDS={
    "train":{
        "people":["mara","sol","eli","tavi","nova","orion"],
        "verbs":["carry","deliver","mark","repair","archive","inspect"],
        "patients":["parcel","map","ledger","lamp","tablet","banner"],
    },
    "dev":{
        "people":["mara","sol","eli","tavi","nova","orion"],
        "verbs":["carry","deliver","mark","repair","archive","inspect"],
        "patients":["parcel","map","ledger","lamp","tablet","banner"],
    }
}
# Syntactic rows are authored but NOT passed to the inducer.
# Each tuple (A sentence, A semantics, B sentence, B semantics) has exactly
# the same externally declared event. Some contrasts modify two relations.
TRAIN={
 "modal":(
   ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} wonders whether {agent} might {verb} {patient}",("MENTION","IMAGINED","POS")),
   ("{speaker} requests that {agent} {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} imagines that {agent} could {verb} {patient}",("MENTION","IMAGINED","POS")),
 ),
 "quote":(
   ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} quotes {agent} saying {verb} {patient}",("MENTION","QUOTED","POS")),
   ("{speaker} requests {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} repeats a quote where {agent} says {verb} {patient}",("MENTION","QUOTED","POS")),
 ),
 "neg":(
   ("{speaker} says {agent} did {verb} {patient}",("ASSERTION","ROOT","POS"),
    "{speaker} says {agent} did not {verb} {patient}",("ASSERTION","ROOT","NEG")),
   ("{speaker} reports {agent} has {verb} {patient}",("ASSERTION","ROOT","POS"),
    "{speaker} reports {agent} has never {verb} {patient}",("ASSERTION","ROOT","NEG")),
 ),
 "condition":(
   ("{speaker} asks {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} asks {agent} to {verb} {patient} if dawn comes",("DIRECTIVE","CONDITIONAL","POS")),
   ("{speaker} requests {agent} to {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} requests {agent} to {verb} {patient} provided the clock rings",("DIRECTIVE","CONDITIONAL","POS")),
 ),
 "counterfact":(
   ("{speaker} says {agent} did {verb} {patient}",("ASSERTION","ROOT","POS"),
    "{speaker} supposes {agent} might have {verb} {patient}",("MENTION","IMAGINED","POS")),
   ("{speaker} reports {agent} has {verb} {patient}",("ASSERTION","ROOT","POS"),
    "{speaker} considers whether {agent} could have {verb} {patient}",("MENTION","IMAGINED","POS")),
 ),
}
DEV={
 "modal":(
   ("{speaker} asks {agent} to quickly {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} wonders whether {agent} might quietly {verb} {patient}",("MENTION","IMAGINED","POS")),
   ("{speaker} requests that {agent} promptly {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} imagines that {agent} could perhaps {verb} {patient}",("MENTION","IMAGINED","POS")),
 ),
 "quote":(
   ("{speaker} asks {agent} to urgently {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} quotes {agent} saying quietly {verb} {patient}",("MENTION","QUOTED","POS")),
   ("{speaker} requests {agent} to promptly {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} repeats a quote where {agent} says quietly {verb} {patient}",("MENTION","QUOTED","POS")),
 ),
 "neg":(
   ("{speaker} says {agent} did indeed {verb} {patient}",("ASSERTION","ROOT","POS"),
    "{speaker} says {agent} did not actually {verb} {patient}",("ASSERTION","ROOT","NEG")),
   ("{speaker} reports {agent} has recently {verb} {patient}",("ASSERTION","ROOT","POS"),
    "{speaker} reports {agent} has never actually {verb} {patient}",("ASSERTION","ROOT","NEG")),
 ),
 "condition":(
   ("{speaker} asks {agent} to urgently {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} asks {agent} to urgently {verb} {patient} if dawn comes",("DIRECTIVE","CONDITIONAL","POS")),
   ("{speaker} requests {agent} to promptly {verb} {patient}",("DIRECTIVE","ROOT","POS"),
    "{speaker} requests {agent} to promptly {verb} {patient} provided the clock rings",("DIRECTIVE","CONDITIONAL","POS")),
 ),
 "counterfact":(
   ("{speaker} says {agent} did indeed {verb} {patient}",("ASSERTION","ROOT","POS"),
    "{speaker} supposes {agent} might have quietly {verb} {patient}",("MENTION","IMAGINED","POS")),
   ("{speaker} reports {agent} has recently {verb} {patient}",("ASSERTION","ROOT","POS"),
    "{speaker} considers whether {agent} could have quietly {verb} {patient}",("MENTION","IMAGINED","POS")),
 ),
}


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def edges(force,scope,polarity):
    return [
        ["UTTERANCE","FORCE",force],
        ["UTTERANCE","SCOPE",scope],
        ["EVENT","POLARITY",polarity],
    ]


def graph(attrs):
    if len(attrs)!=3 or any(
            val not in VALUES[key] for key,val in zip(RELATIONS,attrs)):
        raise ValueError("Unrecognized semantics")
    return {"schema":GRAPH_SCHEMA,"edges":edges(*attrs)}


def observed(rng,lex):
    speaker,agent=rng.sample(lex["people"],2)
    return {
        "speaker":speaker,"agent":agent,
        "verb":rng.choice(lex["verbs"]),
        "patient":rng.choice(lex["patients"]),
    }


def example(template,meaning,context):
    return {
        "text":template.format(**context),
        "observed_event":dict(context),
        "semantic_graph":graph(meaning),
    }


def generate(split,*,seed=2026111011,repeats=5):
    forms={"train":TRAIN,"dev":DEV}.get(split)
    if forms is None or type(seed) is not int or type(repeats) is not int or not 1<=repeats<=12:
        raise ValueError("Train and dev source types only")
    rng=random.Random(seed)
    rows=[]
    for _,pairs in sorted(forms.items()):
        for ta,va,tb,vb in pairs:
            for _ in range(repeats):
                context=observed(rng,SEEDS[split])
                rows.append({
                    "a":example(ta,va,context),
                    "b":example(tb,vb,context),
                })
    rng.shuffle(rows)
    result={
        "schema":SCHEMA,"split":split,"pairs":rows,
        "speaker_and_event_observations_explicitly_provided":True,
        "template_ids_hidden_from_learner":True,
        "semantic_graphs_author_labeled":True,
        "no_real_world_utterances":True,
    }
    result["receipt_sha256"]=digest(result)
    return result


def check(dataset,*,split=None):
    if (not isinstance(dataset,dict) or dataset.get("schema")!=SCHEMA
            or dataset.get("split") not in ("train","dev","novel")
            or (split is not None and dataset["split"]!=split)
            or not isinstance(dataset.get("pairs"),list)
            or not 1<=len(dataset["pairs"])<=180
            or dataset.get("speaker_and_event_observations_explicitly_provided") is not True
            or dataset.get("semantic_graphs_author_labeled") is not True
            or dataset.get("receipt_sha256")!=digest({
                k:v for k,v in dataset.items() if k!="receipt_sha256"})):
        raise ValueError("Unauthenticated or malformed semantic evidence")
    for pair in dataset["pairs"]:
        if not isinstance(pair,dict) or set(pair)!={"a","b"}:
            raise ValueError("A contrast requires two arms")
        a,b=pair["a"],pair["b"]
        for arm in (a,b):
            if not isinstance(arm,dict) or set(arm)!={
                    "text","observed_event","semantic_graph"}:
                raise ValueError("Malformed graph-labeled utterance")
            ctx=arm["observed_event"]
            g=arm["semantic_graph"]
            if (type(arm["text"]) is not str or not 1<=len(arm["text"])<=320
                    or not isinstance(ctx,dict)
                    or set(ctx)!={"speaker","agent","verb","patient"}
                    or not all(type(x) is str and x.isalpha() and 1<=len(x)<=40
                               for x in ctx.values())
                    or g.get("schema")!=GRAPH_SCHEMA
                    or not isinstance(g.get("edges"),list)
                    or len(g["edges"])!=3
                    or set(tuple(e) for e in g["edges"]) != set(
                        tuple(e) for e in edges(*[
                            next((e[2] for e in g["edges"] if e[1]==rel),None)
                            for rel in RELATIONS]))):
                raise ValueError("Graph edge contract violated")
            for relation in RELATIONS:
                entry=[e for e in g["edges"] if e[1]==relation]
                if len(entry)!=1 or entry[0][2] not in VALUES[relation]:
                    raise ValueError("Typed graph relation violated")
        if a["observed_event"]!=b["observed_event"]:
            raise ValueError("Semantic contrast must hold source event constant")
        if a["semantic_graph"]==b["semantic_graph"]:
            raise ValueError("Meaning contrast must change at least one graph relation")
    return dataset


def flatten(dataset):
    check(dataset)
    return [row for pair in dataset["pairs"] for row in (pair["a"],pair["b"])]
