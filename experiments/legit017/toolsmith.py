"""LEGIT-017: bounded executable research-tool composer.

The same hand-designed and inspectable source factory can generate working
tools for THREE distinct engineering domains. It can generate tool source,
compile it, verify it against independently coded reference behavior and
reuse the tool on later task instances.

This is NOT unrestricted autonomous algorithm discovery: every strategy and
its source template below is predeclared. Exact-template admission is not a
general Python sandbox. Graph and subset algorithms are known classical
indexing methods. External Z3 does not prove these general algorithms.
"""
from __future__ import annotations

import ast
from hashlib import sha256
from time import perf_counter_ns
from itertools import product

from tasks import Task,FAMILIES,direct,check_suite

STRATEGIES={
    "GRAPH":("GRAPH_STACK","GRAPH_QUEUE"),
    "SUBSET":("SUBSET_BITSET","SUBSET_SET"),
    "TEXT":("TEXT_LITERAL","TEXT_SHINGLES"),
}
SOURCE={
"GRAPH_STACK":'''"""LEGIT-017 bounded generated graph reachability tool; research only."""
NO_EXTERNAL_ACTIONS = True
def build(instance):
    n,edges=instance
    adjacency=[[] for _ in range(n)]
    for source,target in edges:
        adjacency[source].append(target)
    all_reached=[]
    for start in range(n):
        pending=[start]
        visited={start}
        while pending:
            vertex=pending.pop()
            for nxt in adjacency[vertex]:
                if nxt not in visited:
                    visited.add(nxt)
                    pending.append(nxt)
        all_reached.append(frozenset(visited))
    return tuple(all_reached)
def answer(context,query):
    source,target=query
    return target in context[source]
''',
"GRAPH_QUEUE":'''"""LEGIT-017 bounded generated graph reachability tool; research only."""
NO_EXTERNAL_ACTIONS = True
def build(instance):
    n,edges=instance
    adjacency=[[] for _ in range(n)]
    for source,target in edges:
        adjacency[source].append(target)
    all_reached=[]
    for start in range(n):
        pending=[start]
        visited={start}
        while pending:
            vertex=pending.pop(0)
            for nxt in adjacency[vertex]:
                if nxt not in visited:
                    visited.add(nxt)
                    pending.append(nxt)
        all_reached.append(frozenset(visited))
    return tuple(all_reached)
def answer(context,query):
    source,target=query
    return target in context[source]
''',
"SUBSET_BITSET":'''"""LEGIT-017 bounded generated subset-sum feasibility tool; research only."""
NO_EXTERNAL_ACTIONS = True
def build(weights):
    possible=1
    for value in weights:
        possible|=possible<<value
    return possible
def answer(context,target):
    return target>=0 and ((context>>target)&1)==1
''',
"SUBSET_SET":'''"""LEGIT-017 bounded generated subset-sum feasibility tool; research only."""
NO_EXTERNAL_ACTIONS = True
def build(weights):
    possible={0}
    for value in weights:
        possible|={x+value for x in possible}
    return frozenset(possible)
def answer(context,target):
    return target in context
''',
"TEXT_LITERAL":'''"""LEGIT-017 bounded generated substring membership tool; research only."""
NO_EXTERNAL_ACTIONS = True
def build(instance):
    return instance[0]
def answer(context,term):
    return term in context
''',
"TEXT_SHINGLES":'''"""LEGIT-017 bounded generated substring membership tool; research only."""
NO_EXTERNAL_ACTIONS = True
def build(instance):
    (document,)=instance
    pieces=set()
    for width in (3,4,5):
        for start in range(len(document)-width+1):
            pieces.add(document[start:start+width])
    return frozenset(pieces)
def answer(context,term):
    return term in context
''',
}
class HOLD(ValueError):pass

def emit(family,strategy):
    if family not in FAMILIES or strategy not in STRATEGIES[family]:
        raise HOLD("Unknown or cross-family source operator")
    return SOURCE[strategy]

def review(family,strategy,source):
    """Reject any byte variation, even AST-safe modifications."""
    canonical=emit(family,strategy)
    if type(source) is not str or source!=canonical:
        raise HOLD("Source is not exactly an authorized static template")
    tree=ast.parse(source)
    forbidden=(ast.Import,ast.ImportFrom,ast.With,ast.AsyncWith,ast.Await,
               ast.Try,ast.Global,ast.Nonlocal,ast.Lambda,ast.Delete,
               ast.AsyncFunctionDef,ast.Yield,ast.YieldFrom)
    if any(isinstance(node,forbidden) for node in ast.walk(tree)):
        raise HOLD("Generated source contains forbidden AST operation")
    defs={node.name for node in tree.body if isinstance(node,ast.FunctionDef)}
    if defs!={"build","answer"}:
        raise HOLD("Unknown tool source entrypoint")
    if any(isinstance(node,ast.Attribute) and node.attr.startswith("__")
           for node in ast.walk(tree)):
        raise HOLD("Invalid introspection")
    return {"family":family,"strategy":strategy,
            "source_sha256":sha256(source.encode()).hexdigest(),
            "exact_template":True,
            "not_a_general_security_sandbox":True,
            "source_author":"RESEARCHER_WRITTEN_FIXED_GRAMMAR"}

def compile_tool(family,strategy,source=None):
    source=emit(family,strategy) if source is None else source
    reviewed=review(family,strategy,source)
    builtins={"range":range,"len":len,"set":set,"tuple":tuple,
              "frozenset":frozenset}
    ns={"__builtins__":builtins}
    begin=perf_counter_ns()
    exec(compile(source,"<LEGIT017-CONSTRAINED-RESEARCH-TOOL>","exec"),
         ns,ns)
    elapsed=(perf_counter_ns()-begin)/1e6
    if not callable(ns.get("build")) or not callable(ns.get("answer")):
        raise HOLD("Generated tool is not executable")
    return {
        "family":family,"strategy":strategy,"source":source,
        "source_sha256":reviewed["source_sha256"],
        "compile_ms":elapsed,"build":ns["build"],"answer":ns["answer"],
        "never_permitted_to_deploy":True,
    }

def verify(tool,tasks):
    group=[x for x in tasks if x.family==tool["family"]]
    if not group or check_suite(group)!=len(group):
        raise HOLD("Empty or invalid verified task family")
    start=perf_counter_ns()
    correct=0
    for task in group:
        context=tool["build"](task.instance)
        for query in task.queries:
            if type(tool["answer"](context,query)) is not bool:
                raise HOLD("Tool returned non-Boolean reasoning answer")
            if tool["answer"](context,query)!=direct(task,query):
                raise HOLD("Generated tool fails independent exact oracle")
            correct+=1
    return {"tests":correct,
            "states":len(group),
            "independent_exact_answers_match":True,
            "source_sha256":tool["source_sha256"],
            "verification_wall_ms":(perf_counter_ns()-start)/1e6,
            "external_mathematical_prover_invoked":False}

def bounded_falsification(tool):
    """Tiny complete-model checks independent of training and holdout seeds.

    Graph: all directed 3-node graphs, every source-target pair.
    Subset: all 3-weight tuples with values 1..4, targets 0..12.
    Text: all binary strings length 4, every binary term of size 3/4.
    """
    from tasks import Task
    family=tool["family"]
    total=0
    if family=="GRAPH":
        directed=tuple((a,b) for a in range(3) for b in range(3) if a!=b)
        for edge_mask in range(1<<len(directed)):
            edges=tuple(e for i,e in enumerate(directed) if (edge_mask>>i)&1)
            task=Task("GRAPH","FINITE",(3,edges),
                      tuple((s,t) for s in range(3) for t in range(3)))
            ctx=tool["build"](task.instance)
            for q in task.queries:
                if tool["answer"](ctx,q)!=direct(task,q):
                    raise HOLD("Finite graph counterexample")
                total+=1
    elif family=="SUBSET":
        for weights in product(range(1,5),repeat=3):
            task=Task("SUBSET","FINITE",weights,tuple(range(13)))
            ctx=tool["build"](task.instance)
            for q in task.queries:
                if tool["answer"](ctx,q)!=direct(task,q):
                    raise HOLD("Finite sumset counterexample")
                total+=1
    else:
        alphabet="ab"
        for letters in product(alphabet,repeat=4):
            document="".join(letters)
            tasks=tuple("".join(word) for length in (3,4)
                        for word in product(alphabet,repeat=length))
            task=Task("TEXT","FINITE",(document,),tasks)
            ctx=tool["build"](task.instance)
            for q in tasks:
                if tool["answer"](ctx,q)!=direct(task,q):
                    raise HOLD("Finite text counterexample")
                total+=1
    return {"family":family,"exact_cases_checked":total,
            "finite_scope_only":True,
            "proof_of_arbitrary_software_behavior":False}
