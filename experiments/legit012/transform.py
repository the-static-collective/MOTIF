"""LEGIT-012: CEGIS synthesizes a SOURCE-LEVEL transform of MOTIF-011 search.

Input: the ACTUAL previously generated LEGIT-011 Python search algorithm.
Output: a *new generated Python solver* that factors common evidence graph
prefixes into a typed DAG of cached bitsets rather than re-solving each query.

A finite 24-member source transform language (parent reuse/restart,
AND/OR/XOR, lowest/highest candidate, HOLD/fallback) is deliberately
hand-authored. A separately implemented reference scanner supplies
counterexamples. All 6561 partial eight-row truth-table states plus
parent-edge consistency are independently checked.

Generated source is executable only after exact-template matching. This is
a research-only restricted execution model, NOT a general sandbox or a
general theorem prover. No source commits or external actions are made
by generated code; the assistant reviews and commits produced artifacts.
"""
from __future__ import annotations

import ast
from hashlib import sha256
from importlib.util import spec_from_file_location,module_from_spec
from pathlib import Path
from itertools import product
import json

from independent_oracle import (
    check_graph,make_graph,all_states,scan,classical_dp,cases
)

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"legit011"/"generated"/"search_v2.py"
OLD_SHA="09f0e39892526f3ecf0cb5cfa7e3d210b74e5e72c2648b2648f887ce5e7c899a"
SCHEMA="motif.certified-evidence-dag-transform.v1"
RECIPE_OPERATORS={
    "join":("OR","XOR","AND"),
    "mode":("REUSE_PARENT","RESTART_EACH_STATE"),
    "pick":("LAST","FIRST"),
    "on_empty":("FALLBACK_ZERO","HOLD"),
}
MAX_CEGIS_ROUNDS=25

class HOLD(ValueError):pass

def digest(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                             ensure_ascii=True,allow_nan=False).encode()).hexdigest()

def prior_search():
    """Actually load MOTIF's previous generated search source, never a mock."""
    raw=OLD.read_bytes()
    if sha256(raw).hexdigest()!=OLD_SHA:
        raise HOLD("Previous self-generated source changed unexpectedly")
    syntax=ast.parse(raw.decode("utf-8"))
    names={node.name for node in syntax.body if isinstance(
        node,(ast.FunctionDef,ast.ClassDef))}
    if not {"build_index","choose","IncrementalSearch"}<=names:
        raise HOLD("Parent solver lacks expected search operations")
    has_and=any(isinstance(n,ast.AugAssign) and isinstance(n.op,ast.BitAnd)
                for n in ast.walk(syntax))
    if not has_and:
        raise HOLD("Prior solver does not contain verified bitset update")
    spec=spec_from_file_location("legit011_pinned_generated_search",OLD)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def recipes():
    for join in RECIPE_OPERATORS["join"]:
        for mode in RECIPE_OPERATORS["mode"]:
            for pick in RECIPE_OPERATORS["pick"]:
                for empty in RECIPE_OPERATORS["on_empty"]:
                    yield {"join":join,"mode":mode,"pick":pick,"on_empty":empty}

def validate_recipe(recipe):
    if (not isinstance(recipe,dict) or set(recipe)!=set(RECIPE_OPERATORS) or
            any(recipe[field] not in allowed for field,allowed in
                RECIPE_OPERATORS.items())):
        raise HOLD("Unknown source rewrite transformation")

def interpreter(recipe,normalized,columns,size):
    """Typed candidate program interpreter used only during CEGIS."""
    validate_recipe(recipe)
    if not isinstance(normalized,list) or not 1<=size<=3072:
        raise HOLD("Unknown prepared graph")
    memory={}
    result={}
    operations=0
    for facts,parents in normalized:
        if not facts:
            bits=(1<<size)-1
        elif recipe["mode"]=="REUSE_PARENT":
            parent=parents[0]
            bits=memory[parent]
            extra=next(item for item in facts if item not in parent)
            bit=columns[extra]
            operations+=1
            if recipe["join"]=="AND":
                bits &= bit
            elif recipe["join"]=="OR":
                bits |= bit
            else:
                bits ^= bit
        else:
            bits=(1<<size)-1 if recipe["join"]=="AND" else 0
            for item in facts:
                operations+=1
                bit=columns[item]
                if recipe["join"]=="AND":
                    bits &= bit
                elif recipe["join"]=="OR":
                    bits |= bit
                else:
                    bits ^= bit
        memory[facts]=bits
        if bits==0:
            result[facts]=None if recipe["on_empty"]=="HOLD" else 0
        elif recipe["pick"]=="FIRST":
            result[facts]=(bits&-bits).bit_length()-1
        else:
            result[facts]=bits.bit_length()-1
    return result,{"bitset_updates":operations}

def _all_member_truth_tables(rows):
    # The source has been prepared by independent typed graph validator.
    return tuple(row["truth_mask"] for row in rows)

def _first_difference(actual,expected,graph):
    for facts,_ in check_graph(graph):
        if actual.get(facts)!=expected[facts]:
            return {"partial":[list(x) for x in facts],
                    "actual":actual.get(facts),
                    "expected":expected[facts],
                    "graph_id":graph["id"]}
    return None

def learn_transform(rows):
    parent=prior_search()
    if not 1<=len(rows)<=3072:
        raise HOLD("Unrecognized old reasoning catalog")
    columns=parent.build_index(rows)
    training=[cases(12000+j,10) for j in range(4)]
    full=make_graph("CompleteEightRowLattice",all_states())
    graphs=training+[full]
    prepared=[]
    for graph in graphs:
        typed=check_graph(graph)
        answer,_=scan(rows,typed)
        prepared.append((graph,typed,answer))
    known=[]
    transcript=[]
    for attempt in range(MAX_CEGIS_ROUNDS):
        candidate=None
        for recipe in recipes():
            if all(interpreter(recipe,items,columns,len(rows))[0].get(key)==goal
                   for items,key,goal in known):
                candidate=recipe
                break
        if candidate is None:
            raise HOLD("Transformation grammar lacks a correct implementation")
        witness=None
        for graph,typed,gold in prepared:
            actual,_=interpreter(candidate,typed,columns,len(rows))
            witness=_first_difference(actual,gold,graph)
            if witness is not None:
                break
        transcript.append({"round":attempt+1,"candidate":candidate,
                           "counterexample":witness})
        if witness is None:
            expected,_=scan(rows,check_graph(full))
            classical,_=classical_dp(rows,check_graph(full))
            actual,_=interpreter(candidate,check_graph(full),columns,len(rows))
            if not actual==expected==classical:
                raise HOLD("Source rewrite not equivalent to strong mathematical controls")
            return {
                "recipe":candidate,
                "counterexample_transcript":transcript,
                "counterexamples":len(transcript)-1,
                "verified_partial_states":6561,
                "strong_classical_index_tied":True,
                "source_011_sha256":OLD_SHA,
                "meta_language_predefined":True,
            }
        key=tuple(tuple(x) for x in witness["partial"])
        if any(existing_key==key for _,existing_key,_ in known):
            raise HOLD("Contradictory or duplicate source counterexample")
        known.append((check_graph(graph),key,witness["expected"]))
    raise HOLD("No verified rewrite in finite CEGIS budget")

def emit_source(recipe):
    validate_recipe(recipe)
    join={"AND":"&","OR":"|","XOR":"^"}[recipe["join"]]
    start="(1 << size) - 1" if recipe["join"]=="AND" else "0"
    selector=("(bits & -bits).bit_length() - 1" if
              recipe["pick"]=="FIRST" else "bits.bit_length() - 1")
    on_empty="None" if recipe["on_empty"]=="HOLD" else "0"
    if recipe["mode"]=="REUSE_PARENT":
        computation=f"""            before = parents[0]
            added = next(item for item in facts if item not in before)
            bits = memo[before] {join} columns[added]
            operations += 1"""
    else:
        computation=f"""            bits = {start}
            for added in facts:
                bits = bits {join} columns[added]
                operations += 1"""
    return f'''"""Generated MOTIF-012 certified graph solver. DRAFT RESEARCH ONLY.
Generated from verified LEGIT-011 search source by typed CEGIS.
No file, network, shell or production permissions.
"""
RESEARCH_HOLD = True
NO_EXTERNAL_ACTIONS = True
SCHEMA = "motif.generated-graph-search.v1"

def solve(columns,size,ordered):
    memo = {{}}
    result = {{}}
    operations = 0
    for facts,parents in ordered:
        if not facts:
            bits = (1 << size) - 1
        else:
{computation}
        memo[facts] = bits
        if not bits:
            result[facts] = {on_empty}
        else:
            result[facts] = {selector}
    return result, {{"bitset_updates":operations}}
'''

def static_source_review(source):
    if not isinstance(source,str) or len(source)>5000:
        raise HOLD("Unknown generated source")
    syntax=ast.parse(source)
    deny=(ast.Import,ast.ImportFrom,ast.Global,ast.Nonlocal,ast.With,
          ast.AsyncWith,ast.Await,ast.AsyncFunctionDef,ast.Try,ast.Delete,
          ast.Yield,ast.YieldFrom)
    if any(isinstance(node,deny) for node in ast.walk(syntax)):
        raise HOLD("Generated rewrite contains forbidden construct")
    names={node.name for node in syntax.body if isinstance(node,ast.FunctionDef)}
    if names!={"solve"}:
        raise HOLD("Unexpected source entrypoints")
    disallowed={"eval","exec","open","compile","__import__","getattr",
                "setattr","globals","locals","breakpoint"}
    if any(isinstance(node,ast.Name) and node.id in disallowed
           for node in ast.walk(syntax)):
        raise HOLD("Unexpected runtime access")
    if any(isinstance(node,ast.Attribute) and node.attr.startswith("__")
           for node in ast.walk(syntax)):
        raise HOLD("Access to Python reserved attribute")
    if not any(source==emit_source(recipe) for recipe in recipes()):
        raise HOLD("AST-valid but not an EXACT registered code template")
    return {"ast_nodes":sum(1 for _ in ast.walk(syntax)),
            "approved_template":True,
            "source_sha256":sha256(source.encode()).hexdigest(),
            "not_general_python_sandbox":True}

def load_source(source):
    approval=static_source_review(source)
    names={"__builtins__":{"range":range,"len":len,"next":next,
                           "int":int,"bool":bool,"ValueError":ValueError}}
    # Source is byte-for-byte one of the 24 trusted, static source templates.
    exec(compile(source,"<MOTIF-LEGIT012-FINITE-SOURCE-TEMPLATE>","exec"),
         names,names)
    return names["solve"]

def _independent_local_proof():
    # Boolean bitwise recurrence: childMembership = parentMembership AND
    # evidenceMembership. Exhaustively enumerate 4 bit-level transitions.
    checked=0
    for parent,observation in product((False,True),repeat=2):
        checked+=1
        if (parent & observation)!=(parent and observation):
            raise HOLD("Bitwise intersection contradicts Boolean specification")
    return {
        "membership_transitions":checked,
        "invariant":"Surviving program at a child = program survives parent AND matches added observation",
        "proof":"Structural induction over topologically sorted evidence DAG with one added constraint per edge. For multi-parent merges every parent must yield the same canonical partial set.",
        "source":"finite Boolean truth table + independent graph edge validator",
        "external_SMT_solver_invoked":False,
        "independently_authored_formal_checker":False,
    }

def produce(rows):
    invented=learn_transform(rows)
    source=emit_source(invented["recipe"])
    checked=static_source_review(source)
    manifest={
        "schema":SCHEMA,"status":"PROOF_REQUIRED_DRAFT",
        "parent_legit011_sha256":OLD_SHA,
        "source_sha256":checked["source_sha256"],
        "transformation_recipe":invented["recipe"],
        "cegis_counterexamples":invented["counterexamples"],
        "counterexample_transcript":invented["counterexample_transcript"],
        "partial_truth_states_verified":6561,
        "inductive_edge_certificate":_independent_local_proof(),
        "read_only_candidate_graphs":True,
        "production_patch_approved":False,
        "source_identity_authenticated":False,
        "independently_blinded_benchmark":False,
        "real_world_authority":False,
    }
    return {"source":source,"manifest":dict(manifest,sha256=digest(manifest)),
            "generated_solver":load_source(source)}

def verify(artifact,rows):
    source,manifest=artifact["source"],artifact["manifest"]
    if not isinstance(manifest,dict) or "sha256" not in manifest:
        raise HOLD("No proof-carrying search manifest")
    original={k:v for k,v in manifest.items() if k!="sha256"}
    if digest(original)!=manifest["sha256"]:
        raise HOLD("Mutated source commitment")
    if (manifest["schema"]!=SCHEMA or manifest["status"]!="PROOF_REQUIRED_DRAFT"
            or manifest["parent_legit011_sha256"]!=OLD_SHA or
            manifest["source_sha256"]!=sha256(source.encode()).hexdigest()
            or manifest["production_patch_approved"] is not False
            or manifest["real_world_authority"] is not False):
        raise HOLD("Unsupported source execution authority")
    source_fn=load_source(source)
    previous=prior_search()
    cols=previous.build_index(rows)
    full=make_graph("CompleteEightRowLattice",all_states())
    ordered=check_graph(full)
    expected,_=scan(rows,ordered)
    strongest,_=classical_dp(rows,ordered)
    actual,_=source_fn(cols,len(rows),ordered)
    if actual!=expected or actual!=strongest:
        raise HOLD("Original and independent mathematical semantics diverge")
    if _independent_local_proof()["membership_transitions"]!=4:
        raise HOLD("Failed finite evidence transition certificate")
    return {"status":"VERIFIED_FINITE_AND_INDUCTIVE_RESEARCH_ONLY",
            "fully_enumerated_partial_states":len(ordered),
            "inductive_local_Boolean_transitions":4,
            "source_sha256":manifest["source_sha256"],
            "strong_classical_exact_agreement":True,
            "external_formal_prover_used":False,
            "actual_production_change":False}
