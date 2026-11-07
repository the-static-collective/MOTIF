"""LEGIT-019 bounded syntax-guided program search on external SyGuS tasks.

Both arms use the SAME entire grammar, expansion budget and training
examples. The treatment arm additionally has a separately measured,
Z3-proof-checked algebraic equality library from an earlier experiment;
it never gets target test labels or an extra primitive unavailable to
the control. The control already has strong observational signature
deduplication. Genuine lemma utility may therefore be zero/negative.

The result only synthesizes expression PROGRAMS that fit published finite
examples, not a proven general function equation. Heldout public examples
are checked once after BOTH programs have been frozen.
"""
from __future__ import annotations
from time import perf_counter_ns,process_time_ns
from algebra import (ATOMS,OPS_UNARY,OPS_BINARY,norm,val,canonical,
                     verified_rewrites,MASK)
from corpus import HOLD

MAX_EXPANSIONS=12000
MAX_SIZE=5
MAX_RETAIN_PER_SIZE=2400

def expr_text(t):
    op=t[0]
    if op=="x":return "x"
    if op=="k":return hex(t[1])
    if op in OPS_UNARY:return op+"("+expr_text(t[1])+")"
    return "("+expr_text(t[1])+" "+op+" "+expr_text(t[2])+")"

def search(examples,rewrites=(),max_expansions=MAX_EXPANSIONS):
    if (not isinstance(examples,tuple) or len(examples)!=10 or
        len(set(x for x,_ in examples))!=len(examples)):
        raise HOLD("Search requires exactly ten independent externally sourced examples")
    if type(max_expansions) is not int or not 100<=max_expansions<=MAX_EXPANSIONS:
        raise HOLD("Unknown search compute budget")
    for a,b in rewrites:
        norm(a);norm(b)
    inputs=tuple(x for x,y in examples)
    expected=tuple(y for x,y in examples)
    evaluated=0
    semantic_duplicates=0
    rewritten=0
    pruned=0
    seen={}
    levels={cost:[] for cost in range(1,MAX_SIZE+1)}
    memo={}
    start_wall=perf_counter_ns()
    start_cpu=process_time_ns()

    def signature(ast):
        if ast not in memo:
            memo[ast]=tuple(val(ast,x) for x in inputs)
        return memo[ast]

    def attempt(candidate,size):
        nonlocal evaluated,semantic_duplicates,rewritten,pruned
        if evaluated>=max_expansions:return "LIMIT"
        mapped=canonical(candidate,rewrites) if rewrites else candidate
        if candidate!=mapped:rewritten+=1
        values=signature(mapped)
        evaluated+=1
        if values==expected:return ("SOLVED",mapped)
        if values in seen:
            semantic_duplicates+=1
            return None
        if len(levels[size])>=MAX_RETAIN_PER_SIZE:
            pruned+=1
            return None
        seen[values]=mapped
        levels[size].append(mapped)
        return None

    found=None
    exhausted=False
    for size in range(1,MAX_SIZE+1):
        if size==1:
            candidates=ATOMS
        else:
            def gen():
                for a in levels[size-1]:
                    for op in OPS_UNARY:
                        yield(op,a)
                for cost_a in range(1,size-1):
                    cost_b=size-cost_a-1
                    if cost_b<1:continue
                    for a in levels[cost_a]:
                        for b in levels[cost_b]:
                            for op in OPS_BINARY:
                                if op in OPS_BINARY and repr(a)>repr(b):
                                    # all operators are commutative modulo 2^64
                                    continue
                                yield(op,a,b)
            candidates=gen()
        for candidate in candidates:
            result=attempt(candidate,size)
            if isinstance(result,tuple) and result[0]=="SOLVED":
                found=result[1]
                break
            if result=="LIMIT":
                exhausted=True
                break
        if found is not None or exhausted:
            break
    wall=(perf_counter_ns()-start_wall)/1e6
    cpu=(process_time_ns()-start_cpu)/1e6
    return {
        "program":found,
        "solved_10_training_examples":found is not None,
        "program_text":expr_text(found) if found is not None else None,
        "program_complexity":len(repr(found)) if found else None,
        "candidates_evaluated":evaluated,
        "unique_training_output_signatures":len(seen),
        "semantic_deduplications":semantic_duplicates,
        "formally_checked_rewrites_applied":rewritten,
        "retained_limit_prunes":pruned,
        "limit_exhausted":exhausted,
        "max_expansions":max_expansions,
        "max_ast_size":MAX_SIZE,
        "wall_ms":round(wall,6),
        "cpu_ms":round(cpu,6),
        "heldout_data_accessed":False,
        "literal_py_exec_permitted":False,
        "research_solver_externally_authored":False,
    }

def frozen_public_evaluation(report,external_rows):
    """Validate frozen synthesis against public unseen examples."""
    tree=report.get("program")
    if tree is None:
        return {"examples":len(external_rows),
                "passed":0,"exact_match_rate":0.0,
                "solved":False,"first_counterexample":None,
                "no_new_program_selected_after_test":True}
    tree=as_tuple(tree)
    norm(tree)
    hits=0
    failure=None
    for x,wanted in external_rows:
        got=val(tree,x)
        if got==wanted:hits+=1
        elif failure is None:
            failure={"x":hex(x),"expected":hex(wanted),
                     "got":hex(got)}
    return {
        "examples":len(external_rows),
        "passed":hits,
        "exact_match_rate":round(hits/len(external_rows),4),
        "solved":hits==len(external_rows),
        "first_counterexample":failure,
        "no_new_program_selected_after_test":True,
    }

def as_tuple(value):
    return tuple(as_tuple(x) for x in value) if isinstance(value,list) else value
