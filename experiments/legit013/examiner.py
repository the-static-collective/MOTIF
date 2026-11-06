"""LEGIT-013: profile MOTIF's own generated graph solver and synthesize
a verified, source-level shortcut from observations and Z3 counterexamples.

Input code is ACTUAL prior LEGIT-012 generated Python, pinned by SHA.
No optimizer rule is silently assumed correct: every hypothesis is checked
for *all* 152-bit candidate/evidence masks using external Z3, and every
counterexample is fed back to the hypothesizer. Saved source executes only
when its bytes equal a registered trusted source-template emission.

Rule grammar is still narrow and designed here (5 guards + ALWAYS;
4 permitted results). The generator is not unconstrained algorithm design.
"""
from __future__ import annotations

import ast
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"legit012"))
sys.path.insert(0,str(HERE.parent/"legit010"))
from bootstrap import invent_successor_search,_compressed_candidates
from graph_reference import check_graph,cases,make_graph,all_states,scan
from formal_oracle import (
    GUARDS,ANSWERS,WIDTHS,guard_eval,answer_eval,prove_rule,
    independent_recurrence_proof,
)

PARENT=HERE.parent/"legit012"/"generated"/"search_dag_v3.py"
PARENT_SHA="b9c11206bdcd0c4e61b383660aca4bd8fb98ceeb1c27da7303dc32c61bb33881"
SCHEMA="motif.self-improvement-examiner.v1"
RULE_GUARDS=("ALWAYS",)+GUARDS
LIMIT=40

class HOLD(ValueError):pass

def digest(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()

def actual_parent():
    contents=PARENT.read_bytes()
    if sha256(contents).hexdigest()!=PARENT_SHA:
        raise HOLD("Prior self-generated solver source changed")
    tree=ast.parse(contents.decode())
    if not any(isinstance(node,ast.FunctionDef) and node.name=="solve"
               for node in tree.body):
        raise HOLD("Previous reasoning solver unavailable")
    spec=spec_from_file_location("pinned_generated_motif012",PARENT)
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def catalog():
    return _compressed_candidates(invent_successor_search()["algorithm"])

def _columns(rows):
    return actual_parent().__dict__ if False else _make_columns(rows)

def _make_columns(rows):
    out={}
    for row in range(8):
        for wanted in (False,True):
            bits=0
            for i,candidate in enumerate(rows):
                if bool(candidate["truth_mask"] & (1<<row))==wanted:
                    bits |= 1<<i
            out[row,wanted]=bits
    return out

def training_graphs():
    return [cases(41000+i,8+(i%4)*8) for i in range(32)]

def trace(rows,graph,old_solver=None,columns=None):
    """Inspect actual DAG work; reconstruct its first-parent transition.

    An independent exact linear-scan oracle checks the original code
    before a trace is accepted as legitimate training evidence.
    """
    old_solver=old_solver or actual_parent().solve
    columns=columns or _make_columns(rows)
    normalized=check_graph(graph)
    actual,_=old_solver(columns,len(rows),normalized)
    expected,_=scan(rows,normalized)
    if actual!=expected:
        raise HOLD("Parent solver differs from independent semantic oracle")
    full=(1<<len(rows))-1
    state={():full}
    records=[]
    for key,parents in normalized:
        if not key:
            continue
        prior=parents[0]
        new=next(x for x in key if x not in prior)
        p=state[prior]
        c=columns[new]
        child=p&c
        state[key]=child
        records.append((p,c,child))
        predicted=(child&-child).bit_length()-1 if child else None
        if actual[key]!=predicted:
            raise HOLD("Profiler cannot explain real old algorithm")
    return records

def profile():
    methods=catalog()
    engine=actual_parent().solve
    col=_make_columns(methods)
    samples=[]
    zero_count=0
    identity_count=0
    for graph in training_graphs():
        for p,c,value in trace(methods,graph,engine,col):
            samples.append((p,c,value))
            zero_count+=int(p==0)
            identity_count+=int(p!=0 and p&c==p)
    if not samples:
        raise HOLD("No source reasoning observations")
    return {"samples":samples,
            "summary":{
                "training_graphs":len(training_graphs()),
                "training_transitions":len(samples),
                "zero_parent_transitions":zero_count,
                "unchanged_nonzero_transitions":identity_count,
                "source":"ACTUAL_GENERATED_MOTIF012_DAG_PYTHON",
                "parent_sha256":PARENT_SHA,
                "training_seeds_range":[41000,41031],
                "world_truth_not_used":True,
                "benchmark_test_cases_accessed":False,
            }}

def _matches(guard,p,c,full):
    return True if guard=="ALWAYS" else guard_eval(guard,p,c,full)

def _candidate_score(guard,samples,full,already):
    return sum(_matches(guard,p,c,full) and
               not any(_matches(prior,p,c,full) for prior in already)
               for p,c,_ in samples)

def _valid_on_examples(guard,answer,examples,full):
    return all(not _matches(guard,p,c,full) or
               answer_eval(answer,p,c,full)==expected
               for p,c,expected in examples)

def _learn_single(samples,already):
    full=(1<<152)-1
    known=[samples[0]]
    transcript=[]
    rejected=set()
    for trial_number in range(LIMIT):
        candidates=[]
        for guard in RULE_GUARDS:
            if guard in already:continue
            for answer in ANSWERS:
                if (guard,answer) in rejected:continue
                support=_candidate_score(guard,samples,full,already)
                if support<=0 or not _valid_on_examples(guard,answer,known,full):
                    continue
                candidates.append((-support,RULE_GUARDS.index(guard),
                                   ANSWERS.index(answer),guard,answer))
        if not candidates:
            return None,transcript
        candidates.sort()
        _,_,_,guard,answer=candidates[0]
        certified=prove_rule(guard if guard!="ALWAYS" else "ALWAYS",answer,152)
        event={
            "round":trial_number+1,"hypothesis":{"guard":guard,"answer":answer},
            "observed_training_support":-candidates[0][0],
            "external_smt_result":certified["result"],
            "counterexample":certified["counterexample"],
        }
        transcript.append(event)
        if certified["result"]=="SAT":
            bad=certified["counterexample"]
            known.append((int(bad["parent"],16),int(bad["column"],16),int(bad["reference"],16)))
            rejected.add((guard,answer))
            continue
        if certified["result"]!="UNSAT":
            raise HOLD("Unknown SMT proof state")
        # The rule is actually proven at three distinct bitvector widths.
        additional=[prove_rule(guard,answer,w) for w in (8,256)]
        if any(x["result"]!="UNSAT" for x in additional):
            raise HOLD("Cross-width proof mismatch")
        return {"guard":guard,"answer":answer,
                "externally_verified_widths":[8,152,256],
                "source_training_support":-candidates[0][0],
                "proof_obligation":certified["proof_obligation"]},transcript
    raise HOLD("SMT counterexample refinement budget exhausted")

def discover():
    profiled=profile()
    examples=profiled["samples"]
    rules=[]
    transcripts=[]
    for _ in range(2):
        rule,trace_events=_learn_single(examples,[x["guard"] for x in rules])
        transcripts.extend(trace_events)
        if rule is None:
            break
        if rule["guard"]=="ALWAYS":
            # An unconditional replacement can only be a globally
            # proven equivalent expression. No further branches necessary.
            rules.append(rule);break
        rules.append(rule)
    if not rules:raise HOLD("No sound source transformation discovered")
    return {
        "rules":rules,
        "examiner_transcript":transcripts,
        "genuine_smt_counterexamples":
            sum(x["external_smt_result"]=="SAT" for x in transcripts),
        "external_smt_proved_hypotheses":
            sum(x["external_smt_result"]=="UNSAT" for x in transcripts),
        "source_profiler_summary":profiled["summary"],
        "external_recurrence_proof":independent_recurrence_proof(),
    }

def emit(rules):
    if not isinstance(rules,list) or not 1<=len(rules)<=2:
        raise HOLD("Unexpected discovered rewrite")
    guard_python={
        "ALWAYS":"True","P_ZERO":"p == 0",
        "P_FULL":"p == full","C_ZERO":"c == 0",
        "C_FULL":"c == full","P_EQUALS_C":"p == c",
    }
    answer_python={
        "ZERO":"0","PARENT":"p","COLUMN":"c","FULL":"full",
    }
    if len({x["guard"] for x in rules})!=len(rules):
        raise HOLD("Repeated branch guard")
    if any(not isinstance(x,dict) or
           x.get("guard") not in guard_python or
           x.get("answer") not in answer_python for x in rules):
        raise HOLD("Unregistered executable transformation")
    fragments=[]
    for index,rule in enumerate(rules):
        keyword="if" if index==0 else "elif"
        fragments.append(
            f"            {keyword} {guard_python[rule['guard']]}:\n"
            f"                bits = {answer_python[rule['answer']]}\n"
            f"                skips += 1\n")
    fragments.append(
        "            else:\n"
        "                bits = p & c\n"
        "                intersections += 1\n")
    body="".join(fragments)
    return '''"""MOTIF LEGIT-013 generated source: conditional reasoning optimization.
Research draft; finite templates only; no independent deployment authority.
"""
RESEARCH_HOLD = True
NO_EXTERNAL_ACTIONS = True

def solve(columns,size,ordered):
    full = (1 << size) - 1
    memo = {}
    output = {}
    intersections = 0
    skips = 0
    for facts,parents in ordered:
        if not facts:
            bits = full
        else:
            prior = parents[0]
            new_fact = next(x for x in facts if x not in prior)
            p = memo[prior]
            c = columns[new_fact]
''' + body + '''        memo[facts] = bits
        output[facts] = ((bits & -bits).bit_length()-1) if bits else None
    return output, {"bitset_intersections":intersections,"branch_skips":skips}
'''

def limited_load(source,rules):
    # EXACT template bytes required; AST checks alone are insufficient.
    if not isinstance(source,str) or source!=emit(rules):
        raise HOLD("Unreviewed source text; not a registered DSL template")
    tree=ast.parse(source)
    disallowed=(ast.Import,ast.ImportFrom,ast.With,ast.AsyncWith,
                ast.Await,ast.AsyncFunctionDef,ast.Try,ast.Global,
                ast.Nonlocal,ast.Lambda,ast.Delete)
    if any(isinstance(n,disallowed) for n in ast.walk(tree)):
        raise HOLD("Source escaped the restricted subset")
    namespace={"__builtins__":{"range":range,"len":len,"next":next,
                                "bool":bool,"ValueError":ValueError}}
    exec(compile(source,"<LEGIT013-EXACT-TEMPLATE>","exec"),namespace,namespace)
    return namespace["solve"]

def construct():
    discoveries=discover()
    rules=discoveries["rules"]
    source=emit(rules)
    # Verifier already proved every rule for all 152-bit masks.
    # This signed-off by a project transcript, not authenticated source.
    raw={
        "schema":SCHEMA,"status":"PROOF_GATED_DRAFT_ONLY",
        "parent_generated_source_sha256":PARENT_SHA,
        "source_sha256":sha256(source.encode()).hexdigest(),
        "rules":rules,
        "examiner_transcript":discoveries["examiner_transcript"],
        "external_smt_verifier":"z3-solver",
        "external_smt_proved_hypotheses":
            discoveries["external_smt_proved_hypotheses"],
        "genuine_smt_counterexamples":
            discoveries["genuine_smt_counterexamples"],
        "training_profiler":discoveries["source_profiler_summary"],
        "recursive_smt_certificate":discoveries["external_recurrence_proof"],
        "generated_python_source_in_production":False,
        "proof_independent_specification_authorship":False,
        "open_world_correctness_verified":False,
        "real_world_authority":False,
    }
    artifact={"manifest":dict(raw,sha256=digest(raw)),
              "source":source,"solver":limited_load(source,rules)}
    return artifact

def reverify(artifact):
    manifest=artifact["manifest"]
    if not isinstance(manifest,dict) or not isinstance(manifest.get("sha256"),str):
        raise HOLD("Missing proof-carrying algorithm manifest")
    raw={k:v for k,v in manifest.items() if k!="sha256"}
    if digest(raw)!=manifest["sha256"]:
        raise HOLD("Corrupted transformation provenance")
    source=artifact["source"]
    if (manifest["schema"]!=SCHEMA or
        manifest["status"]!="PROOF_GATED_DRAFT_ONLY" or
        manifest["parent_generated_source_sha256"]!=PARENT_SHA or
        manifest["generated_python_source_in_production"] is not False or
        manifest["real_world_authority"] is not False or
        manifest["source_sha256"]!=sha256(source.encode()).hexdigest()):
        raise HOLD("Unsupported source or live authorization")
    rules=manifest["rules"]
    for rule in rules:
        for width in WIDTHS:
            result=prove_rule(rule["guard"],rule["answer"],width)
            if result["result"]!="UNSAT":
                raise HOLD("Z3 refutes generated transformation")
    solver=limited_load(source,rules)
    return {
        "status":"EXTERNAL_SMT_VERIFIED_TYPED_REWRITE",
        "z3_widths_checked":list(WIDTHS),
        "rules_checked":len(rules),
        "source_sha256":manifest["source_sha256"],
        "external_formal_solver_actually_invoked":True,
        "independent_specification_author":False,
        "automatic_promotion_permitted":False,
        "real_world_authority":False,
    }
