"""LEGIT-014: formal, typed candidate generator for revising MOTIF's own code.

Loads the actual LEGIT-013 generated source and the actual earlier profiler.
The *program fragments* are a finite handwritten grammar, but their
selection, Z3 counterexample validation, and measured retention are
performed by the research runner, not manual choice of winning source.

All new programs are inert until an external Z3 proof + finite regression.
No arbitrary Python generation, no auto-promotion, no runtime sandbox claim.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from itertools import product
import ast
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit013"))
sys.path.insert(0,str(HERE.parent/"legit012"))
from examiner import profile, catalog, _make_columns
from formal_oracle import prove_rule, independent_recurrence_proof
from graph_reference import make_graph,all_states,check_graph,scan
from classical_control import StrongClassicalDP

PARENT=HERE.parent/"legit013"/"generated"/"optimized_search_v4.py"
PARENT_SHA="0077c63ec1857cd70fec245addcfdde47a37c3f412ee50547a309ae3dadef044"
SCHEMA="motif.performance-gated-trial.v1"
# These algebraic identities are not presumed correct because they appear
# here. Z3 must prove the selected implication for every 152-bit mask.
PROPOSALS=(
    ("P_FULL","COLUMN"),("P_ZERO","ZERO"),
    ("C_ZERO","ZERO"),("C_FULL","PARENT"),
    ("P_EQUALS_C","PARENT"),
)
# Deliberately injected unsound hypotheses probe the mathematical rejection gate.
# They are NOT asserted as discovered shortcuts or optimization candidates.
ADVERSARIAL_HYPOTHESES=(("P_ZERO","COLUMN"),("P_FULL","PARENT"))
MAX_RULES=2
WIDTHS=(8,152,256)

class HOLD(ValueError):pass

def digest(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()

def get_parent():
    blob=PARENT.read_bytes()
    if sha256(blob).hexdigest()!=PARENT_SHA:
        raise HOLD("Previously generated algorithm changed since verified")
    root=ast.parse(blob.decode("utf-8"))
    if not any(isinstance(n,ast.FunctionDef) and n.name=="solve" for n in root.body):
        raise HOLD("Missing previous generated solver")
    spec=spec_from_file_location("pinned_motif013",PARENT)
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def _guard(kind,p,c,full):
    return {
        "P_FULL":p==full, "P_ZERO":p==0,
        "C_ZERO":c==0, "C_FULL":c==full,
        "P_EQUALS_C":p==c,
    }[kind]

def train_profile():
    previous=get_parent()
    inspected=profile() # ACTUAL original 012 operation traces
    samples=inspected["samples"]
    if not samples:raise HOLD("No original solver trace")
    size=152
    full=(1<<size)-1
    support={k:sum(_guard(k,p,c,full) for p,c,_ in samples)
             for k,_ in PROPOSALS}
    return {"samples":samples,"support":support,
            "source":"ACTUAL_LEGIT012_AND_LEGIT013_GENERATED_SOLVERS",
            "origins":inspected["summary"],
            "test_outputs_used":False}

def propose_round_one(profiled):
    """Use observed hotspot frequencies to *construct* transformation trials.

    Source plans are not pre-written code. In addition to the mandatory
    baseline, vary whether/which proven logical shortcuts to employ.
    """
    counts=profiled["support"]
    ordered=sorted(PROPOSALS,key=lambda x:(-counts[x[0]],x[0],x[1]))
    observed=[rule for rule in ordered if counts[rule[0]]>0]
    plans=[{"parent":"FIRST","rules":[]}]
    for rule in observed[:3]:
        plans.append({"parent":"FIRST","rules":[list(rule)]})
    if len(observed)>1:
        plans.append({"parent":"FIRST","rules":[list(x) for x in observed[:2]]})
        plans.append({"parent":"FIRST","rules":[list(x) for x in reversed(observed[:2])]})
    plans.append({"parent":"LAST","rules":[]})
    return distinct(plans)

def distinct(plans):
    output=[]
    seen=set()
    for p in plans:
        validate(p)
        key=digest(p)
        if key in seen:continue
        seen.add(key);output.append(p)
    return output

def validate(plan):
    if (not isinstance(plan,dict) or set(plan)!={"parent","rules"} or
        plan["parent"] not in ("FIRST","LAST") or
        not isinstance(plan["rules"],list) or len(plan["rules"])>MAX_RULES):
        raise HOLD("Unregistered source plan")
    used=set()
    for row in plan["rules"]:
        if (not isinstance(row,list) or len(row)!=2 or
            tuple(row) not in PROPOSALS+ADVERSARIAL_HYPOTHESES or row[0] in used):
            raise HOLD("Duplicate or unsupported source rule")
        used.add(row[0])

def prove(plan):
    validate(plan)
    checks=[]
    for guard,answer in plan["rules"]:
        for width in WIDTHS:
            result=prove_rule(guard,answer,width)
            if result["result"]!="UNSAT":
                raise HOLD("SMT_SAT_COUNTEREXAMPLE: "+
                           json.dumps({"guard":guard,"answer":answer,
                                       "witness":result["counterexample"]},
                                      sort_keys=True))
            checks.append({"guard":guard,"answer":answer,"width":width,
                           "z3_verdict":result["result"]})
    local=independent_recurrence_proof()
    if not local["all_properties_proved_in_encoded_finite_BitVec_theory"]:
        raise HOLD("Independent Z3 recurrence proof unavailable")
    return {"proof_checker":"EXTERNAL_Z3",
            "proofs":checks,
            "unconditional_bitset_recurrence_proved":True,
            "fixed_bitvector_widths":list(WIDTHS),
            "all_rules_verified":True,
            "formal_logic_specification_authored_in_project":True}

def emit(plan):
    validate(plan)
    guards={"P_FULL":"p == full","P_ZERO":"p == 0",
            "C_ZERO":"c == 0","C_FULL":"c == full",
            "P_EQUALS_C":"p == c"}
    results={"COLUMN":"c","ZERO":"0","PARENT":"p"}
    prior="parents[0]" if plan["parent"]=="FIRST" else "parents[-1]"
    lines=[]
    for i,(guard,answer) in enumerate(plan["rules"]):
        prefix="if" if i==0 else "elif"
        lines.append("            "+prefix+" "+guards[guard]+":\n"
                     "                bits = "+results[answer]+"\n"
                     "                avoided += 1\n")
    if lines:
        lines.append("            else:\n"
                     "                bits = p & c\n"
                     "                intersections += 1\n")
    else:
        lines.append("            bits = p & c\n"
                     "            intersections += 1\n")
    body="".join(lines)
    return '''"""Generated by MOTIF LEGIT-014 from profiler + Z3 proof + trials.
Experimental source, NOT automatically deployed. Exact templates only.
"""
RESEARCH_HOLD = True
NO_EXTERNAL_ACTIONS = True

def solve(columns,size,ordered):
    full = (1 << size) - 1
    memo = {}
    answers = {}
    intersections = 0
    avoided = 0
    for facts,parents in ordered:
        if not facts:
            bits = full
        else:
            prior = '''+prior+'''
            new_fact = next(x for x in facts if x not in prior)
            p = memo[prior]
            c = columns[new_fact]
'''+body+'''        memo[facts] = bits
        answers[facts] = ((bits & -bits).bit_length()-1) if bits else None
    return answers, {"bitset_intersections":intersections,
                     "guarded_skips":avoided}
'''

def limited_load(source,plan):
    if source!=emit(plan):
        raise HOLD("Unexpected generated source bytes")
    tree=ast.parse(source)
    forbidden=(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal,ast.With,
               ast.AsyncWith,ast.Await,ast.Try,ast.Delete,ast.Lambda,
               ast.AsyncFunctionDef,ast.Yield,ast.YieldFrom)
    if any(isinstance(node,forbidden) for node in ast.walk(tree)):
        raise HOLD("Generated source contains forbidden Python operation")
    names={"__builtins__":{"range":range,"len":len,"next":next}}
    exec(compile(source,"<MOTIF-014-EXACT-SOURCE-TEMPLATE>","exec"),names,names)
    return names["solve"]

def compile_proved(plan):
    proof=prove(plan)
    source=emit(plan)
    program=limited_load(source,plan)
    return {"schema":SCHEMA,"plan":plan,"source":source,
            "source_sha256":sha256(source.encode()).hexdigest(),
            "proof":proof,"function":program,
            "not_production":True}

def independent_regression(rows,columns,compiled):
    """Check all 6561 lattice states against separately coded scan and DP."""
    graph=check_graph(make_graph("AllEightRowPartialStates",all_states()))
    baseline,_=scan(rows,graph)
    strong,_=StrongClassicalDP(rows).solve(graph)
    answers,_=compiled["function"](columns,len(rows),graph)
    if not baseline==strong==answers or len(answers)!=6561:
        raise HOLD("External proof omitted an execution-level problem")
    return {"states":6561,"all_outputs_match":True,
            "separate_scan_and_classical_DP":True}

def next_round(previous_best,profiled,already):
    """Actually use failed trial's selected plan as basis of mutations."""
    validate(previous_best)
    ranked=sorted(PROPOSALS,key=lambda x:(-profiled["support"][x[0]],x[0]))
    candidates=[{"parent":("LAST" if previous_best["parent"]=="FIRST" else "FIRST"),
                 "rules":[list(x) for x in previous_best["rules"]]}]
    if previous_best["rules"]:
        candidates.append({"parent":previous_best["parent"],
                           "rules":[list(x) for x in previous_best["rules"][:-1]]})
        if len(previous_best["rules"])==2:
            candidates.append({"parent":previous_best["parent"],
                               "rules":[list(x) for x in reversed(previous_best["rules"])]})
    else:
        candidates.append({"parent":previous_best["parent"],
                           "rules":[list(ranked[0])]})
    if len(previous_best["rules"])<MAX_RULES:
        for rule in ranked:
            if list(rule) not in previous_best["rules"]:
                candidates.append({"parent":previous_best["parent"],
                                   "rules":previous_best["rules"]+[list(rule)]})
                break
    novel=[p for p in distinct(candidates) if digest(p) not in already]
    if not novel:
        # A fast branchless first-round winner can exhaust the obvious
        # mutations. The feedback loop must still try an actually new
        # counter-hypothesis, not mislabel an empty round as invention.
        other=("LAST" if previous_best["parent"]=="FIRST" else "FIRST")
        probes=[{"parent":other,"rules":[list(rule)]} for rule in ranked[:3]]
        probes += [{"parent":other,"rules":[list(x) for x in ranked[:2]]}]
        novel=[p for p in distinct(probes) if digest(p) not in already]
    return novel[:3]
