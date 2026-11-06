"""REASON-009: invent a Boolean grammar *shape* by general AST search.

No AND3+AND2 family is supplied. The allowed operators are only known binary
AND/OR and five variables. Enumerate unique semantic signatures for all
binary expression trees through an explicit node budget, use source-owner
counterexamples to refute inadequate lower-cost grammar tiers, and return the
smallest unrefuted typed AST. A budget is not unbounded program invention.

This learner DOES NOT IMPORT source.py, its BFS evaluator, or heldout labels.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha1, sha256
from pathlib import Path
import json

SOURCE_PATH=Path(__file__).with_name("source.py")
SOURCE_BLOB="560b72c157df71b7c01c3395e0114a595faf4908"
SOURCE_REVISION="motif.reason.grammar-009.source.v1"
OBS_SCHEMA="motif.reason.grammar-009.observation.v1"
SCHEMA="motif.reason.grammar-009.method.v1"
INITIAL=(3,5,6,7,24)
HOLDOUT=(0,1,2,4,8,16,30,31)
ACQUISITION=tuple(m for m in range(32) if m not in HOLDOUT)
LEVELS=(1,3,5,7,9,11)
MAX_BYTES=40000


class HOLD(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()


def pin_source():
    raw=SOURCE_PATH.read_bytes()
    result=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if result!=SOURCE_BLOB:
        raise HOLD("Source owner changed; cannot inherit teacher contracts")
    return result


def mask_signature(index):
    return sum(((mask>>index)&1)<<mask for mask in range(32))


def interpret(tree,mask):
    if not isinstance(tree,(tuple,list)) or not tree:
        raise HOLD("Malformed typed expression")
    if tree[0]=="VAR" and len(tree)==2 and type(tree[1]) is int and 0<=tree[1]<5:
        return bool(mask&(1<<tree[1]))
    if tree[0] in ("AND","OR") and len(tree)==3:
        left=interpret(tree[1],mask)
        right=interpret(tree[2],mask)
        return left and right if tree[0]=="AND" else left or right
    raise HOLD("Unrecognized primitive or unbounded AST")


def node_count(tree):
    if tree[0]=="VAR":
        return 1
    return 1+node_count(tree[1])+node_count(tree[2])


class Grammar:
    """Semantic dynamic programming, exact enumeration through 11 AST nodes."""
    def __init__(self):
        self.by_cost=defaultdict(list)
        self.expressions={}
        for index in range(5):
            sig=mask_signature(index)
            self.expressions[sig]=(1,["VAR",index])
            self.by_cost[1].append(sig)
        for cost in LEVELS[1:]:
            for left_cost in range(1,cost-1,2):
                right_cost=cost-1-left_cost
                for a in self.by_cost[left_cost]:
                    for b in self.by_cost[right_cost]:
                        if a>b:continue
                        for name,signature in (("AND",a&b),("OR",a|b)):
                            if signature in self.expressions:
                                continue
                            self.expressions[signature]=(
                                cost,[name,self.expressions[a][1],
                                      self.expressions[b][1]])
                            self.by_cost[cost].append(signature)

    def candidates(self,limit,labels):
        if limit not in LEVELS:
            raise HOLD("Unknown grammar complexity budget")
        return [sig for sig,(cost,_) in self.expressions.items()
                if cost<=limit and all(bool(sig&(1<<mask))==actual
                                       for mask,actual in labels.items())]

    def gaps(self,limit,labels):
        """Recheck all finite candidates; evidence per refutation is observable."""
        signatures=sorted(sig for sig,(cost,_) in self.expressions.items()
                          if cost<=limit)
        falsifiers=[]
        for sig in signatures:
            fail=next((mask for mask in sorted(labels)
                       if bool(sig&(1<<mask))!=labels[mask]),None)
            if fail is None:
                return None
            falsifiers.append([f"{sig:08x}",fail])
        return {"max_binary_ast_nodes":limit,
                "candidate_functions_refuted":len(falsifiers),
                "refutation_ledger_sha256":digest(falsifiers),
                "sample_refutations":falsifiers[:4],
                "scope":"COMPLETE_ONLY_FOR_FIXED_MONOTONE_AND_OR_DSL"}


def validate_observation(row,family):
    if (not isinstance(row,dict) or set(row)!={
            "schema","source_revision","family","mask","reachable","kind",
            "real_world_authority"}):
        raise HOLD("Unexpected source observation")
    if (row["schema"]!=OBS_SCHEMA
            or row["source_revision"]!=SOURCE_REVISION
            or row["family"]!=family
            or row["mask"] not in ACQUISITION
            or type(row["reachable"]) is not bool
            or row["kind"]!="SYNTHETIC_CLASSICAL_BFS"
            or row["real_world_authority"] is not False):
        raise HOLD("Source claim outside the acquisition/authority contract")
    return row


def family_shape(tree):
    def flatten(node):
        if node[0]=="VAR":return "EDGE"
        op=node[0]
        parts=[]
        def collect(sub):
            if sub[0]==op:
                collect(sub[1]);collect(sub[2])
            else:parts.append(flatten(sub))
        collect(node[1]);collect(node[2])
        return op+"("+",".join(sorted(parts))+")"
    return flatten(tree)


def discovery(family,initial,oracle,max_cost=11,max_calls=24):
    """Counterexample-guided synthesis with strictly protected heldout masks.

    Oracle exports query(mask) and refute_or_pass(signature); no reference to
    oracle implementation/hidden BFS is present in this learner.
    """
    pin_source()
    if (family not in ("LONG_SHORT","BRIDGE") or max_cost not in LEVELS
            or type(max_calls) is not int or not 0<=max_calls<=24
            or not isinstance(initial,tuple) or len(initial)!=5):
        raise HOLD("Invalid fixed-source bounded inquiry")
    observations={}
    for row in initial:
        validate_observation(row,family)
        if row["mask"] in observations:raise HOLD("Duplicate initial witness")
        observations[row["mask"]]=row
    if tuple(sorted(observations))!=INITIAL:
        raise HOLD("Missing source-owned initial coverage")
    grammar=Grammar()
    failed=[]
    challenges=[]
    oracle_calls=0
    selected=None
    selected_limit=None
    for limit in LEVELS:
        if limit>max_cost:break
        while True:
            labels={m:r["reachable"] for m,r in observations.items()}
            fitting=grammar.candidates(limit,labels)
            if not fitting:
                gap=grammar.gaps(limit,labels)
                if gap is None:
                    raise HOLD("False unsatisfiability report")
                failed.append(gap)
                break
            if len(fitting)>1:
                available=[m for m in ACQUISITION if m not in observations]
                if not available:
                    raise HOLD("Remaining methods observationally indistinguishable")
                scores=[]
                for mask in available:
                    ones=sum(bool(sig&(1<<mask)) for sig in fitting)
                    zeros=len(fitting)-ones
                    scores.append((min(ones,zeros),-abs(ones-zeros),-mask,mask))
                score=max(scores)
                if score[0]==0:
                    raise HOLD("No discriminating question before independent holdout")
                if oracle_calls>=max_calls:
                    raise HOLD("Reasoning inquiry budget exhausted")
                mask=score[3]
                row=oracle.query(mask)
                oracle_calls+=1
                validate_observation(row,family)
                if row["mask"]!=mask or mask in observations:
                    raise HOLD("Source answered a different question")
                observations[mask]=row
                challenges.append({"kind":"QUERY","asked":mask,
                                   "response_digest":digest(row)})
            else:
                candidate=fitting[0]
                if oracle_calls>=max_calls:
                    raise HOLD("Candidate cannot be independently challenged")
                reply=oracle.refute_or_pass(candidate)
                oracle_calls+=1
                if not isinstance(reply,dict) or reply.get("status") not in (
                        "COUNTEREXAMPLE","PASS_ACQUISITION"):
                    raise HOLD("Source refused or changed verification contract")
                if reply["status"]=="COUNTEREXAMPLE":
                    row=reply.get("observation")
                    validate_observation(row,family)
                    mask=row["mask"]
                    if mask in observations or bool(candidate&(1<<mask))==row["reachable"]:
                        raise HOLD("Fake or repeated counterexample")
                    observations[mask]=row
                    challenges.append({"kind":"COUNTEREXAMPLE","asked":mask,
                                       "rejected_signature":f"{candidate:08x}",
                                       "response_digest":digest(row)})
                else:
                    if reply.get("does_not_certify_heldout") is not True:
                        raise HOLD("Source claimed more verification than available")
                    selected=candidate
                    selected_limit=limit
                    challenges.append({"kind":"PASS_ACQUISITION",
                                       "signature":f"{candidate:08x}",
                                       "heldout_not_examined":True})
                    break
        if selected is not None:
            break
    if selected is None or selected_limit is None:
        raise HOLD("No source-tested program inside bounded recursive grammar")
    expression=grammar.expressions[selected][1]
    records=[observations[mask] for mask in sorted(observations)]
    program={
        "ast":expression,
        "binary_ast_nodes":grammar.expressions[selected][0],
        "semantic_signature":f"{selected:08x}",
        "inferred_typed_macro_shape":family_shape(expression),
        "monotone_binary_operators_only":True,
        "new_fundamental_boolean_operator":False,
    }
    body={
        "schema":SCHEMA,"source_owner_blob":pin_source(),
        "source_revision":SOURCE_REVISION,"family":family,
        "algorithm":"BOUNDED_BOTTOM_UP_SEMANTIC_AST_CEGIS",
        "grammar":"BINARY_AND_OR_OVER_FIVE_EDGE_VARIABLES",
        "complexity_cap":max_cost,
        "first_verified_complexity":selected_limit,
        "program":program,
        "initial_lessons":sorted(INITIAL),
        "public_observations":records,
        "source_observation_digest":digest(records),
        "source_challenge_trace":challenges,
        "source_oracle_calls":oracle_calls,
        "rejected_smaller_grammar_tiers":failed,
        "expression_functions_enumerated":len(grammar.expressions),
        "stage":"PROPOSE_FOR_INDEPENDENT_CERTIFICATION",
        "scope":"FIVE_EDGE_GRAPH_FAMILIES_SYNTHETIC_READ_ONLY",
        "external_actions":False,"real_world_authority":False,
    }
    packet=dict(body,checksum_sha256=digest(body))
    raw=json.dumps(packet,sort_keys=True,indent=2,allow_nan=False)+"\n"
    if len(raw.encode())>MAX_BYTES:
        raise HOLD("Method evidence exceeds bounded transport")
    return raw


def validate(raw):
    """Replay all mathematical claims without using the independent BFS."""
    if not isinstance(raw,str) or len(raw.encode())>MAX_BYTES:
        raise HOLD("Oversized or missing grammar cartridge")
    try:doc=json.loads(raw)
    except (ValueError,TypeError) as exc:raise HOLD("Unparseable grammar packet") from exc
    fields={"schema","source_owner_blob","source_revision","family","algorithm",
            "grammar","complexity_cap","first_verified_complexity","program",
            "initial_lessons","public_observations","source_observation_digest",
            "source_challenge_trace","source_oracle_calls",
            "rejected_smaller_grammar_tiers","expression_functions_enumerated",
            "stage","scope","external_actions","real_world_authority",
            "checksum_sha256"}
    if not isinstance(doc,dict) or set(doc)!=fields:
        raise HOLD("Method packet has unreviewed fields")
    if (doc["schema"]!=SCHEMA or doc["source_owner_blob"]!=pin_source()
            or doc["source_revision"]!=SOURCE_REVISION
            or doc["family"] not in ("LONG_SHORT","BRIDGE")
            or doc["algorithm"]!="BOUNDED_BOTTOM_UP_SEMANTIC_AST_CEGIS"
            or doc["grammar"]!="BINARY_AND_OR_OVER_FIVE_EDGE_VARIABLES"
            or doc["stage"]!="PROPOSE_FOR_INDEPENDENT_CERTIFICATION"
            or doc["scope"]!="FIVE_EDGE_GRAPH_FAMILIES_SYNTHETIC_READ_ONLY"
            or doc["external_actions"] is not False
            or doc["real_world_authority"] is not False
            or doc["complexity_cap"] not in LEVELS
            or doc["first_verified_complexity"] not in LEVELS):
        raise HOLD("Source-owned program or authority boundary changed")
    program=doc["program"]
    if (not isinstance(program,dict) or set(program)!={
            "ast","binary_ast_nodes","semantic_signature",
            "inferred_typed_macro_shape","monotone_binary_operators_only",
            "new_fundamental_boolean_operator"}
            or program["monotone_binary_operators_only"] is not True
            or program["new_fundamental_boolean_operator"] is not False):
        raise HOLD("Invalid invented grammar shape")
    rows=doc["public_observations"]
    if not isinstance(rows,list) or not rows:
        raise HOLD("No traceable source lessons")
    labels={}
    for row in rows:
        validate_observation(row,doc["family"])
        if row["mask"] in labels:raise HOLD("Duplicate source observation")
        labels[row["mask"]]=row["reachable"]
    if (not set(INITIAL).issubset(labels)
            or doc["initial_lessons"]!=list(INITIAL)
            or doc["source_observation_digest"]!=digest(rows)
            or rows!=sorted(rows,key=lambda r:r["mask"])):
        raise HOLD("Missing initial or mangled source evidence")
    grammar=Grammar()
    fitting=grammar.candidates(doc["first_verified_complexity"],labels)
    sig=int(program["semantic_signature"],16)
    if (len(fitting)!=1 or fitting[0]!=sig or sig not in grammar.expressions
            or grammar.expressions[sig][1]!=program["ast"]
            or grammar.expressions[sig][0]!=program["binary_ast_nodes"]
            or family_shape(program["ast"])!=program["inferred_typed_macro_shape"]
            or doc["first_verified_complexity"]>doc["complexity_cap"]
            or doc["expression_functions_enumerated"]!=len(grammar.expressions)):
        raise HOLD("Invention cannot be reproduced from public evidence")
    lower=[limit for limit in LEVELS if limit<doc["first_verified_complexity"]]
    gaps=[grammar.gaps(limit,labels) for limit in lower]
    if gaps!=doc["rejected_smaller_grammar_tiers"] or any(g is None for g in gaps):
        raise HOLD("Lower grammar refutation missing or altered")
    trace=doc["source_challenge_trace"]
    if (not isinstance(trace,list) or not trace
            or len(trace)!=doc["source_oracle_calls"]
            or trace[-1]!={"kind":"PASS_ACQUISITION",
                            "signature":program["semantic_signature"],
                            "heldout_not_examined":True}
            or any(not isinstance(t,dict) or t.get("kind") not in (
                "QUERY","COUNTEREXAMPLE","PASS_ACQUISITION") for t in trace)):
        raise HOLD("No bounded source-owned challenge receipt")
    if doc["checksum_sha256"]!=digest({k:v for k,v in doc.items()
                                     if k!="checksum_sha256"}):
        raise HOLD("Method checksum mismatch")
    return doc
