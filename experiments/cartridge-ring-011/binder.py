"""RING-011 contrast-derived, inspectable hierarchical semantic scope binder.

The source has to provide an observed event and documentary carrier.
The learner DOES NOT receive the generator's template IDs or precompiled
English indicator words. It extracts lexical + structural features from
paired *target graph differences*; generates typed graph relation rewrites.

New computational primitive? NO: segment, bracket stack, token substitution,
cue matching, and graph-edge projection are audited developer-written opcodes.
New bounded source-evidenced relation rule INSTANCES? YES.

A hypothesized directive is NOT permission. The carrier and epistemic status
are never converted into witnessed-event truth or corroboration.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from hashlib import sha256
import json
import re
import corpus

SCHEMA="motif.ring011.generated-hierarchical-scope-program.v1"
MAX_RULES=320
OPERATORS=("ABSTRACT_SOURCE_EVENT","BIND_SURFACE_CONTAINMENT",
           "CONTRAST_GRAPH_EDGE","INFER_RELATION_BY_CUE",
           "RENDER_NONAUTHORITATIVE_GRAPH")
RELS=corpus.RELATIONS
BRACKET={"[":"]","(":")"}
CLOSE={v:k for k,v in BRACKET.items()}

class HOLD(ValueError):
    pass


def digest(v):
    return corpus.digest(v)


def lex(text):
    if type(text) is not str or not 1<=len(text)<=320:
        raise HOLD("Source utterance outside bounded language envelope")
    return re.findall(r"[a-z]+|\[|\]|\(|\)",text.casefold())


def abstract(text,observed):
    if (not isinstance(observed,dict) or set(observed)!=set(corpus.LEX)
            or any(type(x) is not str or not x.isalpha() or len(x)>40
                   for x in observed.values())):
        raise HOLD("Explicit source event / speaker bindings required")
    raw=lex(text)
    names={v.casefold():"<"+k+">" for k,v in observed.items()}
    if len(names)!=4:
        raise HOLD("Nonunique or ambiguous event binding lexemes")
    src=[names.get(token,token) for token in raw]
    if src.count("<verb>")!=1 or any(
            anchor not in src for anchor in ("<speaker>","<agent>","<patient>")):
        raise HOLD("Utterance does not uniquely refer to source-observed event")
    stack=[]
    depths=[]
    segments=[]
    for word in src:
        if word in BRACKET:
            depths.append(len(stack))
            segments.append("/".join(stack))
            stack.append(word)
        elif word in CLOSE:
            if not stack or stack[-1]!=CLOSE[word]:
                raise HOLD("Unbalanced structural scope delimiters")
            depths.append(len(stack)-1)
            segments.append("/".join(stack))
            stack.pop()
        else:
            depths.append(len(stack))
            segments.append("/".join(stack))
    if stack:
        raise HOLD("Unclosed structural speech scope")
    i=src.index("<verb>")
    return {"tokens":src,"depth":depths,"segments":segments,
            "event_index":i,"event_depth":depths[i]}


def extract(text,observed,*,n=2,gap=12,binder="SCOPED"):
    info=abstract(text,observed)
    words=info["tokens"]
    depth=info["depth"]
    event=info["event_index"]
    feats=set()
    # Absence of a modifier can be learned only as a source-supported default;
    # no artificial feature mentions a semantic graph label or ground truth.
    feats.add("structure:depth:"+str(info["event_depth"]))
    if binder=="SCOPED":
        feats.add("structure:scope_path:"+info["segments"][event])
    if binder not in ("SCOPED","FLAT"):
        raise HOLD("Unreviewed variable-binding operator")
    for width in range(1,n+1):
        for i in range(len(words)-width+1):
            part=words[i:i+width]
            if any(t in BRACKET or t in CLOSE or t.startswith("<")
                   for t in part):
                continue
            if i+width<=event and event-(i+width)<=gap:
                location="BEFORE"
            elif i>event and i-event-1<=gap:
                location="AFTER"
            else:
                continue
            cue=" ".join(part)
            feats.add("event:"+location+":"+cue)
            if binder=="SCOPED":
                scope="ROOT" if depth[i]==0 else "EMBEDDED"
                # Source-named ROOT vs embedded clause prevents a request
                # heard in somebody else's quote from overriding parent voice.
                if all(depth[j]==depth[i] for j in range(i,i+width)):
                    feats.add("owner:"+scope+":"+location+":"+cue)
    # Orthogonal root-clause features for directive vs reported speech.
    # These do not encode which lexical cues mean what; learner discovers
    # such connections from paired target-graph changes.
    root=[w for w,d in zip(words,depth) if d==0 and w.isalpha()]
    for width in range(1,min(n,len(root))+1):
        for i in range(len(root)-width+1):
            feats.add("root:"+str(width)+":"+" ".join(root[i:i+width]))
    return feats,info


def target(ex):
    m=corpus.graph_map(ex["semantic_graph"])
    return {
        "ROOT_FORCE":m[("ROOT","FORCE")],
        "EVENT_SCOPE":m[("EVENT","SCOPE")],
        "EVENT_POLARITY":m[("EVENT","POLARITY")],
    }


def derive(train,*,min_support=2,n=2,gap=12,purity=0.9,
           binder="SCOPED",min_margin=1):
    corpus.validate(train,split="train")
    if (type(min_support) is not int or not 1<=min_support<=12
            or type(n) is not int or not 1<=n<=3
            or type(gap) is not int or not 2<=gap<=22
            or type(purity) is not float or purity not in (0.8,0.9,0.96,1.0)
            or binder not in ("SCOPED","FLAT")
            or type(min_margin) is not int or not 0<=min_margin<=4):
        raise HOLD("Invalid bounded relation-induction configuration")
    counts=Counter()
    prior=defaultdict(Counter)
    observed_deltas=Counter()
    examples=0
    # Observe only source-written typed contrasts. Distinct features in the
    # changed graph reading receive discriminative support; same target
    # unchanged relations cannot create spurious source "proof".
    for triple in train["contrasts"]:
        rows=[]
        for ex in triple.values():
            feats,_=extract(ex["text"],ex["observed_event"],
                            n=n,gap=gap,binder=binder)
            vals=target(ex)
            for rel,v in vals.items():
                prior[rel][v]+=1
            rows.append((feats,vals))
        for i,(feats,vals) in enumerate(rows):
            for rel in RELS:
                # Source contrast determines whether this relation is
                # meaningfully different across current same-event views.
                alternatives={x[1][rel] for x in rows}
                if len(alternatives)<2:
                    continue
                distinct=set(feats)
                for j,(other,other_vals) in enumerate(rows):
                    if j!=i and other_vals[rel]!=vals[rel]:
                        distinct-=other
                for cue in distinct:
                    counts[(rel,vals[rel],cue)]+=1
            examples+=1
        for i,(fa,a) in enumerate(rows):
            for fb,b in rows[i+1:]:
                for rel in RELS:
                    if a[rel]!=b[rel]:
                        observed_deltas[(rel,a[rel],b[rel])]+=1
    if examples<20:
        raise HOLD("Too little independent contrast support to induce binder")
    rules=[]
    for (rel,val,feature),support in counts.items():
        conflict=sum(c for (r,v,f),c in counts.items()
                     if r==rel and v!=val and f==feature)
        proportion=support/max(1,support+conflict)
        if support<min_support or proportion<purity:
            continue
        rules.append({
            "opcode":"INFER_RELATION_BY_CUE",
            "relation":rel,"value":val,"feature":feature,
            "source_support":support,"source_contradictions":conflict,
            "pairwise_purity":round(proportion,6),
            "source":"MEANING_DIFFERENCE_OF_SAME_EVENT_CONTRASTS",
        })
    rules.sort(key=lambda z:(-z["source_support"],
                             -len(z["feature"]),z["relation"],
                             z["feature"],z["value"]))
    rules=rules[:MAX_RULES]
    if not rules:
        raise HOLD("No source-derived clauses or relation cues")
    defaults={}
    # Only event POLARITY may use a source-derived default; letting
    # FORCE or SCOPE default can silently promote quoted instructions.
    for relation in ("EVENT_POLARITY",):
        best,value_count=prior[relation].most_common(1)[0]
        defaults[relation]=best
    deltas=[
        {"opcode":"CONTRAST_GRAPH_EDGE","relation":rel,
         "from":a,"to":b,"source_pair_count":count}
        for (rel,a,b),count in sorted(observed_deltas.items())
    ]
    artifact={
        "schema":SCHEMA,
        "source_train_sha256":train["receipt_sha256"],
        "seen_three_way_contrasts":len(train["contrasts"]),
        "example_utterances":examples,
        "author_defined_runtime_ops":list(OPERATORS),
        "derived_relation_graph_transitions":deltas,
        "derived_contextual_binding_rules":rules,
        "source_induced_relation_count":len(rules),
        "source_induced_edge_rewrites":len(deltas),
        "defaults_only_for_polarity":defaults,
        "parameters":{
            "min_support":min_support,"n":n,"gap":gap,"purity":purity,
            "binder":binder,"min_margin":min_margin,
        },
        "event_entities_and_carrier_source_provided_not_language_discovered":True,
        "carrier_proof_promotion_forbidden":True,
        "new_base_computational_primitives_invented":False,
        "authority":"NONE",
    }
    artifact["receipt_sha256"]=digest(artifact)
    return artifact


def validate(program):
    if (not isinstance(program,dict) or program.get("schema")!=SCHEMA
            or program.get("author_defined_runtime_ops")!=list(OPERATORS)
            or program.get("authority")!="NONE"
            or program.get("carrier_proof_promotion_forbidden") is not True
            or program.get("new_base_computational_primitives_invented") is not False
            or program.get("source_induced_relation_count")!=len(
                program.get("derived_contextual_binding_rules",[]))
            or program.get("source_induced_edge_rewrites")!=len(
                program.get("derived_relation_graph_transitions",[]))
            or not 1<=program["source_induced_relation_count"]<=MAX_RULES
            or program.get("receipt_sha256")!=digest({
                k:v for k,v in program.items() if k!="receipt_sha256"})):
        raise HOLD("Unknown or changed source-derived graph binder")
    params=program.get("parameters")
    if (not isinstance(params,dict)
            or set(params)!={"min_support","n","gap","purity","binder","min_margin"}
            or params["binder"] not in ("SCOPED","FLAT")
            or params["purity"] not in (0.8,0.9,0.96,1.0)):
        raise HOLD("Unreviewed graph binder search scope")
    for rule in program["derived_contextual_binding_rules"]:
        if (rule.get("opcode")!="INFER_RELATION_BY_CUE"
                or rule.get("relation") not in RELS
                or rule.get("value") not in corpus.VALUES[rule["relation"]]
                or type(rule.get("feature")) is not str
                or not 1<=len(rule["feature"])<=100
                or type(rule.get("source_support")) is not int
                or rule["source_support"]<params["min_support"]):
            raise HOLD("Invalid executable relational rule")
    for edge in program["derived_relation_graph_transitions"]:
        if (edge.get("opcode")!="CONTRAST_GRAPH_EDGE"
                or edge.get("relation") not in RELS
                or edge.get("from") not in corpus.VALUES[edge["relation"]]
                or edge.get("to") not in corpus.VALUES[edge["relation"]]
                or edge["from"]==edge["to"]):
            raise HOLD("Invalid graph-diff transformation")
    if set(program.get("defaults_only_for_polarity",{}))!={"EVENT_POLARITY"}:
        raise HOLD("Unreviewed default could promote an apparent directive")
    return program


def predict(program,text,observed,carrier):
    validate(program)
    if carrier not in corpus.CARRIERS:
        raise HOLD("Unsupported document carrier")
    source_sha=sha256(text.encode()).hexdigest() if type(text) is str else None
    try:
        feats,info=extract(text,observed,**{
            k:program["parameters"][k] for k in ("n","gap","binder")})
    except HOLD as exc:
        return {"status":"HOLD","graph":None,
                "reason":"UNBOUND_OR_UNBALANCED_SOURCE_EVENT",
                "details":str(exc),"original_sha256":source_sha}
    matched=defaultdict(lambda:defaultdict(list))
    for rule in program["derived_contextual_binding_rules"]:
        if rule["feature"] in feats:
            matched[rule["relation"]][rule["value"]].append(rule)
    assigned={}
    receipts=[]
    for rel in RELS:
        votes=matched.get(rel,{})
        if not votes:
            if rel not in program["defaults_only_for_polarity"]:
                return {"status":"HOLD","graph":None,
                        "reason":"NO_SOURCE_DERIVED_RELATION_BINDING",
                        "unresolved_relation":rel,"original_sha256":source_sha}
            val=program["defaults_only_for_polarity"][rel]
            receipts.append({"relation":rel,"value":val,
                             "provenance":"TRAINING_PREVALENCE_NOT_AUTHENTICATED_EVIDENCE"})
            assigned[rel]=val
            continue
        ranking=[]
        for v,rules in votes.items():
            # Maximum corroborated specificity, not indiscriminate sum of
            # overlapping n-gram cues from a single utterance.
            strongest=max(rules,key=lambda a:(a["source_support"],
                                             len(a["feature"])))
            rank=strongest["source_support"]-strongest["source_contradictions"]
            ranking.append((rank,len(strongest["feature"]),v,strongest))
        ranking.sort(reverse=True,key=lambda r:(r[0],r[1],r[2]))
        if (len(ranking)>1
                and ranking[0][0]-ranking[1][0] < program[
                    "parameters"]["min_margin"]):
            return {"status":"HOLD","graph":None,
                    "reason":"CONFLICTED_SOURCE_DERIVED_RELATION",
                    "unresolved_relation":rel,"original_sha256":source_sha}
        chosen=ranking[0]
        assigned[rel]=chosen[2]
        receipts.append({
            "opcode":"INFER_RELATION_BY_CUE",
            "relation":rel,"value":chosen[2],
            "feature":chosen[3]["feature"],
            "source_support":chosen[3]["source_support"],
            "speaker_source":"EXPLICIT_OBSERVED_EVENT_NOT_INFERRED",
        })
    force,scope,polarity=(assigned[r] for r in RELS)
    graph=corpus.frame(force,scope,polarity,carrier,observed)
    path=list(info["segments"][info["event_index"]].split("/"))
    if path==[""]:
        path=[]
    # Nested scope is an actual source-structured containment graph. Bracket
    # boundaries are syntactic, not evidence that a quoted event occurred.
    containment=[
        ["SCOPE_"+str(i),"CONTAINS","SCOPE_"+str(i+1)]
        for i in range(len(path))
    ]+[["SCOPE_"+str(len(path)),"BINDS","EVENT"]]
    return {
        "status":"NONAUTHORITATIVE_NESTED_GRAPH_HYPOTHESIS",
        "graph":graph,
        "source_containment_graph":containment,
        "source_event_bracket_depth":info["event_depth"],
        "source_derived_rewrites":receipts,
        "original_sha256":source_sha,
        "source_event_and_carrier_from_input":True,
        "evidence_status":"CARRIER_METADATA_ONLY_NOT_CORROBORATION",
        "external_effect_permission":"NONE",
    }
