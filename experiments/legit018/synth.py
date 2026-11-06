"""LEGIT-018 typed source composition with real LEGIT-017 capability ancestry.

Proposals combine a selected exact-cost kernel with independently
verified upstream reachability and subset-sum prefilters. A naive
"AND the two ancestral solvers" proposal is deliberately unsound:
reachability AND subset-sum over ALL edges does not prove existence
of a PATH with the requested cost. Actual counterexamples reject it.

An exact path-cost DP (cost-set bitsets propagated *along DAG edges*)
is the new composition. Bounded source assembly from several typed
fragments produces executable Python; no arbitrary source invention
or general sandboxing. This is a known classical algorithm.

Episode B adapts the Episode A exact-cost recurrence to forbid nodes.
Without Episode A, this research grammar exposes only exhaustive DFS.
That is a restricted-grammar causal ablation, NOT proof of a general
advantage over classical reasoning or open-ended discovery.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from time import perf_counter_ns
import ast
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/"legit017"))
from toolsmith import compile_tool,emit as emit_017
from challenge import reference,FAMILIES

BUNDLE=ROOT/"legit017"/"generated"/"executable_research_tools.json"
PROVENANCE={
    "GRAPH":"GRAPH_STACK",
    "SUBSET":"SUBSET_BITSET",
}
KERNELS=("BAD_JOIN","DFS_EXACT","BITSET_PATH")
CAPS=("REACH","SUM")
class HOLD(ValueError):pass

def ancestry():
    packet=json.loads(BUNDLE.read_text(encoding="utf-8"))
    if (packet.get("schema")!="motif.research-tools-source-bundle.v1" or
        packet.get("production_write_approved") is not False or
        packet.get("independent_external_validation") is not False or
        set(packet.get("selected_tools",{}))!=set(PROVENANCE)):
        raise HOLD("LEGIT-017 source packet changed or unreviewed")
    tools={}
    for family,strategy in PROVENANCE.items():
        source=packet["selected_tools"][family]
        expected=sha256(source.encode()).hexdigest()
        if (packet["selected_sources_verified"].get(family)!=expected or
            source!=emit_017(family,strategy)):
            raise HOLD("Ancestral source differs from verified old generator")
        tools[family]=compile_tool(family,strategy,source)
    return {
        "tools":tools,
        "source_sha256":{k:v["source_sha256"] for k,v in tools.items()},
        "verified_upstream_017":True,
        "real_previous_programs_are_reused":True,
    }

def typed(family,kernel,prechecks=(),stageA_source=None):
    if (family not in FAMILIES or kernel not in KERNELS or
        not isinstance(prechecks,tuple) or
        tuple(sorted(set(prechecks)))!=prechecks or
        any(p not in CAPS for p in prechecks)):
        raise HOLD("Outside finite typed source grammar")
    if kernel=="BAD_JOIN" and set(prechecks)!=set(CAPS):
        raise HOLD("Naive AND join requires both tools")
    if family=="FORBIDDEN" and kernel=="BITSET_PATH":
        if type(stageA_source) is not str or not stageA_source.startswith(
            '"""LEGIT-018 generated typed DAG path'):
            raise HOLD("Exact-weight path solver not transferred from Episode A")
    if family=="EXACT" and stageA_source is not None:
        raise HOLD("Episode A cannot use a later source")
    return {"family":family,"kernel":kernel,"prechecks":prechecks,
            "ancestor_A_sha256":(sha256(stageA_source.encode()).hexdigest()
                                 if stageA_source is not None else None)}

HEADER='''"""LEGIT-018 generated typed DAG path program; no external actions.
Known algorithm fragments composed under a research-only grammar.
"""
RESEARCH_ONLY = True
NO_PRODUCTION_WRITE = True

def build(task, reach_build=None, subset_build=None):
    n=task.n
    edges=task.edges
    outgoing=[[] for _ in range(n)]
    for u,v,w in edges:
        outgoing[u].append((v,w))
'''
REACH_BUILD='''    closure=(reach_build((n,tuple((u,v) for u,v,w in edges)))
             if reach_build is not None else None)
'''
SUM_BUILD='''    sum_mask=(subset_build(tuple(w for u,v,w in edges))
              if subset_build is not None else None)
'''
NO_REACH='    closure=None\n'
NO_SUM='    sum_mask=None\n'

DP_BUILD='''    masks={}
    for excluded in (range(-1,n) if task.family=="FORBIDDEN" else (-1,)):
        for source in range(n):
            paths=[0]*n
            if source!=excluded:
                paths[source]=1
            for u in range(source,n):
                if u==excluded:
                    continue
                for v,w in outgoing[u]:
                    if v!=excluded:
                        paths[v]|=(paths[u]<<w)
            masks[excluded,source]=tuple(paths)
'''
DP_NO='    masks=None\n'
RETURN='''    return (outgoing,closure,sum_mask,masks)

def answer(ctx,query):
    outgoing,closure,sum_mask,masks=ctx
    source,target,cost,excluded=query
    if source==excluded or target==excluded:
        return False
'''
REACH_GUARD='''    if closure is not None and target not in closure[source]:
        return False
'''
SUM_GUARD='''    if sum_mask is not None and ((sum_mask>>cost)&1)==0:
        return False
'''
DFS_ANSWER='''    todo=[(source,0)]
    while todo:
        vertex,weight=todo.pop()
        if weight>cost:
            continue
        if vertex==target:
            if weight==cost:
                return True
            continue
        for nxt,w in outgoing[vertex]:
            if nxt!=excluded and nxt<=target:
                todo.append((nxt,weight+w))
    return False
'''
DP_ANSWER='''    return ((masks[excluded,source][target]>>cost)&1)==1
'''
BAD_ANSWER='''    return (closure is not None and target in closure[source]
            and sum_mask is not None and ((sum_mask>>cost)&1)==1)
'''

def emit(spec,stageA_source=None):
    checked=typed(spec["family"],spec["kernel"],spec["prechecks"],
                  stageA_source)
    if checked!=spec:
        raise HOLD("Mutation of typed source specification")
    with_reach="REACH" in spec["prechecks"]
    with_sum="SUM" in spec["prechecks"]
    source=HEADER
    source+=REACH_BUILD if with_reach else NO_REACH
    source+=SUM_BUILD if with_sum else NO_SUM
    source+=DP_BUILD if spec["kernel"]=="BITSET_PATH" else DP_NO
    source+=RETURN
    if with_reach:source+=REACH_GUARD
    if with_sum:source+=SUM_GUARD
    source+={
        "BAD_JOIN":BAD_ANSWER,
        "DFS_EXACT":DFS_ANSWER,
        "BITSET_PATH":DP_ANSWER,
    }[spec["kernel"]]
    return source

def compile_spec(spec,bank=None,stageA_source=None,provided=None):
    source=emit(spec,stageA_source)
    if provided is not None and source!=provided:
        raise HOLD("Source differs from exact typed assembly")
    tree=ast.parse(source)
    forbidden=(ast.Import,ast.ImportFrom,ast.With,ast.AsyncWith,
               ast.Try,ast.Global,ast.Nonlocal,ast.Await,ast.Lambda,
               ast.AsyncFunctionDef,ast.Yield,ast.YieldFrom)
    if any(isinstance(n,forbidden) for n in ast.walk(tree)):
        raise HOLD("Research source template contains forbidden operation")
    allowed={"range":range,"len":len,"tuple":tuple,"list":list}
    context={"__builtins__":allowed}
    started=perf_counter_ns()
    exec(compile(source,"<LEGIT018-TYPED-SOURCE>","exec"),context,context)
    compile_ms=(perf_counter_ns()-started)/1e6
    before=bank or {}
    if spec["prechecks"] and not before.get("verified_upstream_017"):
        raise HOLD("A selected source requires provenance-checked ancestor tools")
    parent_tools=before.get("tools",{})
    reach_build=parent_tools["GRAPH"]["build"] if "REACH" in spec["prechecks"] else None
    sum_build=parent_tools["SUBSET"]["build"] if "SUM" in spec["prechecks"] else None

    def build(task):
        if task.family!=spec["family"]:
            raise HOLD("Family mismatch")
        return context["build"](task,reach_build,sum_build)

    def answer(data,query):
        return context["answer"](data,query)

    return {
        "source":source,"source_sha256":sha256(source.encode()).hexdigest(),
        "spec":spec,"build":build,"answer":answer,
        "compile_ms":compile_ms,"restricted_python_template":True,
        "general_security_sandbox":False,"production_allowed":False,
    }

def explore_specs(family,bank=None,stageA_source=None):
    """Hand-bounded grammar, with conditional capability unlocks.

    No-ancestry searches can still invent a *correct* DFS tool. Inherited
    graph and subset capabilities introduce additional composition plans
    and an exact DAG bitset path operation derived from prior math.
    """
    if family not in FAMILIES:raise HOLD("Unknown challenge stage")
    plans=[typed(family,"DFS_EXACT")]
    if bank:
        plans.append(typed(family,"BAD_JOIN",("REACH","SUM"),
                           stageA_source if family=="FORBIDDEN" else None))
        plans.append(typed(family,"DFS_EXACT",("REACH","SUM"),
                           stageA_source if family=="FORBIDDEN" else None))
        plans.append(typed(family,"BITSET_PATH",("REACH","SUM"),
                           stageA_source if family=="FORBIDDEN" else None))
        plans.append(typed(family,"BITSET_PATH",(),
                           stageA_source if family=="FORBIDDEN" else None))
    return plans

def check_tool(tool,tasks):
    checked=0
    first_bad=None
    for task in tasks:
        ctx=tool["build"](task)
        for q in task.queries:
            got=tool["answer"](ctx,q)
            gold=reference(task,q)
            checked+=1
            if type(got) is not bool or got!=gold:
                first_bad={"task":task.name,"query":list(q),
                           "proposed":got,"oracle":gold}
                break
        if first_bad:break
    return {"checked_queries":checked,"correct":first_bad is None,
            "first_counterexample":first_bad}
