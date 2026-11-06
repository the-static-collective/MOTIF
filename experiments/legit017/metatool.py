"""LEGIT-017: build and test a reusable RESEARCH instrument.

This is the second-order experiment: an executable source-generated cache
for an independent reference verifier. It doesn't solve a user problem
faster directly; it avoids re-running the exact oracle whenever a later
candidate algorithm is tested on an already registered example.

Cross-family transfer: SAME generated cache interface is used for GRAPH,
SUBSET and TEXT instruments; it is not three separately duplicated
verifiers. All candidate correctness is still checked against the
original independent oracle on prime. Strong classical oracle caching
is a matched comparator. It is a known classical memoization strategy,
not original mathematics or unrestricted autonomous research.
"""
from __future__ import annotations
from time import perf_counter_ns
from hashlib import sha256

from tasks import direct,strong_build,strong_ask
from toolsmith import HOLD,compile_tool,review
import ast

VERIFIER_SOURCE='''"""Generated LEGIT-017 cross-domain test-witness cache.
No network, file writing or deployment rights. Research only.
"""
NO_EXTERNAL_ACTIONS = True
def build(records):
    table={}
    for key,answer in records:
        if key in table:
            raise ValueError("Duplicate independent test witness")
        table[key]=answer
    return table
def answer(table,key):
    return table[key]
'''

def compile_verifier():
    source=VERIFIER_SOURCE
    parsed=ast.parse(source)
    if any(isinstance(n,(ast.Import,ast.ImportFrom,ast.With,ast.Try,
                         ast.Global,ast.Nonlocal,ast.AsyncFunctionDef))
           for n in ast.walk(parsed)):
        raise HOLD("Verifier escaped research-only source language")
    builtins={"ValueError":ValueError}
    ns={"__builtins__":builtins}
    start=perf_counter_ns()
    exec(compile(source,"<LEGIT017-INDEPENDENT-VERIFIER-CACHE>","exec"),
         ns,ns)
    elapsed=(perf_counter_ns()-start)/1e6
    return {
        "source":source,"source_sha256":sha256(source.encode()).hexdigest(),
        "compile_ms":elapsed,"build":ns["build"],
        "answer":ns["answer"],
        "exact_fixed_source_template":True,
        "not_general_python_sandbox":True,
    }

def witness_key(task,index):
    return (task.identifier,index)

def _record(tasks,mode):
    records=[]
    for task in tasks:
        strong_context=strong_build(task) if mode=="STRONG" else None
        for n,q in enumerate(task.queries):
            actual=(direct(task,q) if mode=="ORACLE"
                    else strong_ask(task,strong_context,q))
            records.append((witness_key(task,n),actual))
    return records

def check_variants(tasks,tools,mode,cache_tool=None):
    """Full rebuild and verify; measured experiment includes all work.

    mode:
      RECHECK: independent oracle once PER candidate verification.
      CACHE: independent oracle once PER task/query, reusable generated
             witness cache shared across ALL tested strategies and families.
      STRONG: conventional indexed classical truth builder once per
              task/query, then reuse Python dictionary lookup.
    """
    if mode not in ("RECHECK","CACHE","STRONG"):
        raise HOLD("Unknown verification ablation mode")
    if mode=="CACHE" and cache_tool is None:
        raise HOLD("No verified generated research instrument")
    records=None
    table=None
    if mode!="RECHECK":
        records=_record(tasks,"ORACLE" if mode=="CACHE" else "STRONG")
        if mode=="CACHE":
            table=cache_tool["build"](records)
        else:
            table=dict(records)
        if len(table)!=len(records):
            raise HOLD("Witness alias collapse")
    comparisons=0
    for task in tasks:
        members=tools[task.family]
        for tool in members:
            ctx=tool["build"](task.instance)
            for i,q in enumerate(task.queries):
                answer=tool["answer"](ctx,q)
                if type(answer) is not bool:
                    raise HOLD("Invalid Boolean answer")
                correct=(direct(task,q) if mode=="RECHECK"
                         else cache_tool["answer"](table,witness_key(task,i))
                         if mode=="CACHE" else table[witness_key(task,i)])
                if answer!=correct:
                    raise HOLD("Algorithm failed externally checked reference")
                comparisons+=1
    return {
        "checked_tool_query_pairs":comparisons,
        "reference_calls":(
            comparisons if mode=="RECHECK" else len(records)),
        "source":"INDEPENDENT_PER_QUESTION" if mode!="STRONG"
                  else "CONVENTIONAL_CLASSICAL_PRECOMPUTED_REFERENCE",
        "no_candidate_was_exempted_from_correctness":True,
    }
