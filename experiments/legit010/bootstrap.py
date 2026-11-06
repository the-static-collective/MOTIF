"""LEGIT-010: MOTIF's *own* LEGIT-009 generator builds its successor.

LEVEL 0: invoke existing LEGIT-009 CEGIS to create all 16 executable
         Boolean cartridges from NAND alone; reverify each independently.
LEVEL 1: enumerate typed COMPOSITIONS of self-generated methods, ask a
         counterexample oracle to teach a semantics-preserving cache key,
         and emit a checksum-bearing successor-search algorithm as DATA.
LEVEL 2: run that *generated search strategy* to CEGIS-synthesize new
         three-input methods from the self-generated binary library.
LEVEL 3: compile one resulting three-input method together with an
         earlier generated two-input method into a four-input program,
         independently verified on all sixteen input states.

No arbitrary code execution, unrestricted self-edit, autonomy or new math.
The grammar, verifier and meta-search were hand-authored. Output algorithms
are typed, portable, independently verified DATA awaiting human review.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import permutations,product
from pathlib import Path
from hashlib import sha256
import json
import sys

HERE=Path(__file__).resolve().parent
sys.path.append(str(HERE.parent/"legit009"))

from synthesizer import cegis as PREVIOUS_CEGIS
from synthesizer import load_verified as PREVIOUS_LOAD
from independent_oracle import TernaryVerifier,QuaternaryVerifier,interpret

SEARCH_SCHEMA="motif.self-composed-search-program.v1"
THREE_SCHEMA="motif.self-composed-reason-cartridge.v1"
FOUR_SCHEMA="motif.second-generation-composed-cartridge.v1"
MAX_META_CEX=8
MAX_TARGET_CEX=8

class HOLD(ValueError): pass

def _hash(data):
    return sha256(json.dumps(data,sort_keys=True,separators=(",",":"),
                             allow_nan=False).encode()).hexdigest()

def _seal(data):
    return dict(data,sha256=_hash(data))

def _verify_hash(artifact):
    if not isinstance(artifact,dict) or "sha256" not in artifact:
        raise HOLD("Not a typed generated artifact")
    original={k:v for k,v in artifact.items() if k!="sha256"}
    if _hash(original)!=artifact["sha256"]:
        raise HOLD("Generated source was altered after creation")
    return original

class BinarySpecification:
    """Separate two-wire finite oracle; no explicit solution circuit."""
    def __init__(self,m):
        if type(m) is not int or not 0<=m<=15:
            raise HOLD("Boolean specification out of domain")
        self.target=m

    def label_initial(self,a,b):
        return self.truth(a,b)

    def truth(self,a,b):
        return bool((self.target>>(2*int(a)+int(b)))&1)

    def check(self,gates,output):
        for a,b in product((False,True),repeat=2):
            if interpret(gates,output,(a,b)) != self.truth(a,b):
                return (a,b,self.truth(a,b))
        return None

@lru_cache(maxsize=1)
def library():
    """Run the *actual previous engine*, not a handwritten circuit catalog."""
    results={}
    for mask in range(16):
        oracle=BinarySpecification(mask)
        # Previous, unmodified MOTIF-009 code generates each program.
        result=PREVIOUS_CEGIS(oracle,"BootstrapPrimitive"+str(mask))
        cartridge=result["cartridge"]
        PREVIOUS_LOAD(cartridge,oracle)
        if cartridge["truth_mask"]!=mask:
            raise HOLD("Previous-generation synthesis is not trustworthy")
        results[mask]=cartridge
    return results


def _primitive_eval(mask,a,b):
    return bool((mask>>(2*int(a)+int(b)))&1)


def _recipe_mask(first,second,association,order):
    result=0
    for row,bits in enumerate(product((False,True),repeat=3)):
        x,y,z=(bits[i] for i in order)
        if association=="LEFT":
            value=_primitive_eval(second,_primitive_eval(first,x,y),z)
        elif association=="RIGHT":
            value=_primitive_eval(second,x,_primitive_eval(first,y,z))
        else:
            raise HOLD("Unknown binary tree association")
        result |= int(value)<<row
    return result


@lru_cache(maxsize=1)
def catalog():
    """Derived, not pre-authored, two-level search candidates."""
    generated=library()
    all_rows=[]
    for first in range(16):
        for second in range(16):
            cost=generated[first]["gate_count"]+generated[second]["gate_count"]
            for shape in ("LEFT","RIGHT"):
                for order in permutations((0,1,2)):
                    all_rows.append({
                        "first":first,"second":second,
                        "shape":shape,"order":list(order),
                        "cost":cost,
                        "truth_mask":_recipe_mask(first,second,shape,order)})
    # Cost order guarantees representative is at least as cheap as any
    # semantically equivalent recipe. Secondarily stable ordering only.
    all_rows.sort(key=lambda r:(r["cost"],r["first"],r["second"],
                                r["shape"],r["order"]))
    if len(all_rows)!=16*16*2*6:
        raise AssertionError("Unexpected synthesis grammar")
    return all_rows


def _signature(truth_mask,indices):
    return tuple((truth_mask>>i)&1 for i in indices)


def _collision(rows,indices):
    """Independent adversarial collision asks for a missing distinguishing row."""
    groups={}
    for item in rows:
        key=_signature(item["truth_mask"],indices)
        reference=groups.setdefault(key,item)
        if reference["truth_mask"]!=item["truth_mask"]:
            diff=reference["truth_mask"]^item["truth_mask"]
            for row in range(8):
                if ((diff>>row)&1) and row not in indices:
                    return {"row":row,
                            "witness_masks":[reference["truth_mask"],
                                             item["truth_mask"]],
                            "identical_on_learned_inputs":True}
            raise AssertionError("Inconsistent collision proof")
    return None


@lru_cache(maxsize=1)
def invent_successor_search():
    """CEGIS derives a semantically complete cache-key search algorithm.

    This is a *generated meta-program*, not a hardcoded truth-table index.
    It may discover that all eight input rows are necessary; if so, that
    negative result must be reported rather than calling it a shortcut.
    """
    rows=catalog()
    known=[0]
    rounds=[]
    for _ in range(MAX_META_CEX+1):
        contradiction=_collision(rows,known)
        rounds.append({"proposed_distinguishing_indices":list(known),
                       "semantic_collision":contradiction})
        if contradiction is None:
            signatures={_signature(row["truth_mask"],known)
                        for row in rows}
            unique={row["truth_mask"] for row in rows}
            if len(unique)!=len(signatures):
                raise AssertionError("Metaproof incomplete")
            raw={
                "schema":SEARCH_SCHEMA,
                "status":"FINITE_EQUIVALENCE_CLASSES_PROVED",
                "method":"COUNTEREXAMPLE_GUIDED_SEARCH_PROGRAM_CREATION",
                "generated_by":"EXISTING_LEGIT009_CEGIS_LIBRARY_PLUS_NEW_META_VERIFIER",
                "input_arity":3,
                "allowed_ops":"TWO_COMPOSED_VERIFIED_BINARY_NAND_CARTRIDGES",
                "program":{"kind":"SEMANTIC_QUOTIENT_SEARCH",
                           "distinguishing_rows":list(known),
                           "cost_order":"MINIMUM_TOTAL_NAND_GATES"},
                "candidate_compositions":len(rows),
                "distinct_truth_functions":len(unique),
                "meta_counterexamples":len(rounds)-1,
                "source_verification":"EXHAUSTIVE_8_ROW_BOOLEAN_MODEL",
                "generated_program_requires_reverification":True,
                "python_self_rewriting_permitted":False,
                "real_world_authority":False,
            }
            return {"algorithm":_seal(raw),"counterexample_transcript":rounds}
        if contradiction["row"] in known:
            raise HOLD("False or duplicate metareasoning counterexample")
        known.append(contradiction["row"])
    raise HOLD("Semantic signature learning overran finite universe")


def _validate_search(algorithm):
    raw=_verify_hash(algorithm)
    if (set(raw)!={"schema","status","method","generated_by",
                   "input_arity","allowed_ops","program","candidate_compositions",
                   "distinct_truth_functions","meta_counterexamples",
                   "source_verification","generated_program_requires_reverification",
                   "python_self_rewriting_permitted","real_world_authority"}
        or raw["schema"]!=SEARCH_SCHEMA
        or raw["status"]!="FINITE_EQUIVALENCE_CLASSES_PROVED"
        or raw["program"].get("kind")!="SEMANTIC_QUOTIENT_SEARCH"
        or raw["program"].get("cost_order")!="MINIMUM_TOTAL_NAND_GATES"
        or raw["python_self_rewriting_permitted"] is not False
        or raw["real_world_authority"] is not False):
        raise HOLD("Unreviewed second-generation search algorithm")
    indices=raw["program"].get("distinguishing_rows")
    if (not isinstance(indices,list) or not 1<=len(indices)<=8
        or any(type(i) is not int or not 0<=i<=7 for i in indices)
        or len(set(indices))!=len(indices)):
        raise HOLD("Unknown learned observation signature")
    if _collision(catalog(),indices) is not None:
        raise HOLD("Incomplete generated semantic search policy")
    if raw["candidate_compositions"]!=len(catalog()):
        raise HOLD("Mismatched generated grammar coverage")
    return indices


def _program_instantiate(primitive,wire_a,wire_b,global_gates,input_count):
    """Translate an independently verified 2-input NAND DAG to an n-input DAG."""
    if primitive["gate_count"]!=len(primitive["gates"]):
        raise HOLD("Tampered generation-one method")
    mapping=[wire_a,wire_b]
    for x,y in primitive["gates"]:
        if type(x) is not int or type(y) is not int or not 0<=x<=y<len(mapping):
            raise HOLD("Invalid previous-program reference")
        global_gates.append(sorted((mapping[x],mapping[y])))
        mapping.append(input_count+len(global_gates)-1)
    if primitive["output"]<0 or primitive["output"]>=len(mapping):
        raise HOLD("Illegal old method output")
    return mapping[primitive["output"]]


def compose_circuit(recipe,methods=None):
    """Actually execute code produced by LEGIT-009 inside our new compiler."""
    methods=library() if methods is None else methods
    if (not isinstance(recipe,dict) or set(recipe)!={
            "first","second","shape","order","cost","truth_mask"}
        or recipe["first"] not in methods or recipe["second"] not in methods
        or recipe["shape"] not in ("LEFT","RIGHT")
        or not isinstance(recipe["order"],list)
        or sorted(recipe["order"])!=[0,1,2]):
        raise HOLD("Unknown next-generation program")
    for idx in (recipe["first"],recipe["second"]):
        PREVIOUS_LOAD(methods[idx],BinarySpecification(idx))
    first=methods[recipe["first"]]
    second=methods[recipe["second"]]
    gates=[]
    x,y,z=recipe["order"]
    if recipe["shape"]=="LEFT":
        intermediate=_program_instantiate(first,x,y,gates,3)
        out=_program_instantiate(second,intermediate,z,gates,3)
    else:
        intermediate=_program_instantiate(first,y,z,gates,3)
        out=_program_instantiate(second,x,intermediate,gates,3)
    if len(gates)!=recipe["cost"]:
        raise HOLD("Wrong emitted program size")
    observed=sum(int(interpret(gates,out,tup))<<i for i,tup in
                 enumerate(product((False,True),repeat=3)))
    if observed!=recipe["truth_mask"]:
        raise HOLD("Old generated primitive composition is unsound")
    return {"gates":gates,"output":out,"truth_mask":observed,
            "gate_count":len(gates)}


def _compressed_candidates(algorithm):
    indices=_validate_search(algorithm)
    representatives={}
    for row in catalog():
        key=_signature(row["truth_mask"],indices)
        # catalog already sorted by minimum NAND cost
        representatives.setdefault(key,row)
    if len(representatives)!=algorithm["distinct_truth_functions"]:
        raise HOLD("Faulty semantic equivalence proof")
    return list(representatives.values())


def synthesize_successor(verifier,search_algorithm,task_name):
    """CEGIS 3-bit task using the algorithm the meta-engine just generated."""
    if not isinstance(task_name,str) or not task_name.isidentifier():
        raise HOLD("Unknown successor task provenance")
    candidates=_compressed_candidates(search_algorithm)
    known={(False,False,False):verifier.label_initial(False,False,False)}
    challenges=[]
    for stage in range(MAX_TARGET_CEX+1):
        proposal=None
        for row in candidates:
            truth=row["truth_mask"]
            if all(bool((truth>>(4*int(a)+2*int(b)+int(c)))&1)==wanted
                   for (a,b,c),wanted in known.items()):
                proposal=row
                break
        if proposal is None:
            return {"status":"HOLD_UNREACHABLE_IN_TWO_PRIMITIVE_COMPOSITION",
                    "task":task_name,"counterexamples":challenges,
                    "program":None,"admitted":False,"real_world_authority":False}
        compiled=compose_circuit(proposal)
        cex=verifier.check(compiled["gates"],compiled["output"])
        if cex is None:
            raw={
                "schema":THREE_SCHEMA,
                "status":"PROVED_FINITE_THREE_BIT_PROPOSAL_ONLY",
                "task":task_name,
                "program_tree":{k:proposal[k] for k in
                                ("first","second","shape","order")},
                "compiled_NAND":compiled,
                "parent_search_program_sha256":search_algorithm["sha256"],
                "generator":"EXECUTED_LEGIT009_CODE_WITH_META_CEGIS_SEARCH_PROGRAM",
                "counterexample_count":len(challenges),
                "full_three_input_domain_exhausted":True,
                "real_world_authority":False,
            }
            return {"status":"PROVED_FINITE_THREE_BIT_PROPOSAL_ONLY",
                    "task":task_name,"counterexamples":challenges,
                    "program":_seal(raw),"admitted":False,
                    "real_world_authority":False}
        if (not isinstance(cex,tuple) or len(cex)!=4 or
            any(type(x) is not bool for x in cex)):
            raise HOLD("Untrusted three-bit verifier")
        a,b,c,y=cex
        if (a,b,c) in known:
            raise HOLD("Verifier repeated a previously known source example")
        if interpret(compiled["gates"],compiled["output"],(a,b,c))==y:
            raise HOLD("False successor counterexample")
        challenges.append({"input":[a,b,c],"expected":y,
                           "prior_program_mask":compiled["truth_mask"]})
        known[(a,b,c)]=y
    raise HOLD("Three-variable verifier exceeded finite counterexample budget")


def reverify_successor(artifact,oracle,search_algorithm):
    raw=_verify_hash(artifact)
    if (raw.get("schema")!=THREE_SCHEMA or
        raw.get("status")!="PROVED_FINITE_THREE_BIT_PROPOSAL_ONLY" or
        raw.get("parent_search_program_sha256")!=search_algorithm.get("sha256")
        or raw.get("full_three_input_domain_exhausted") is not True
        or raw.get("real_world_authority") is not False):
        raise HOLD("Unknown generated successor")
    row=raw["program_tree"]
    original=_recipe_mask(row["first"],row["second"],row["shape"],row["order"])
    expected={
        "first":row["first"],"second":row["second"],
        "shape":row["shape"],"order":row["order"],
        "cost":library()[row["first"]]["gate_count"]+
               library()[row["second"]]["gate_count"],
        "truth_mask":original,
    }
    actual=compose_circuit(expected)
    if actual!=raw["compiled_NAND"]:
        raise HOLD("Mutated or unsupported generated algorithm")
    if oracle.check(actual["gates"],actual["output"]) is not None:
        raise HOLD("Independent truth specification rejects successor")
    return {"status":"VERIFIED_TYPED_THREE_INPUT_ALGORITHM",
            "task":raw["task"],"minimum_within_search_grammar":True,
            "gate_count":actual["gate_count"],
            "sha256":artifact["sha256"],
            "real_world_authority":False}


def build_four_input(successor,search_algorithm):
    """Make the NEXT program, reusing an algorithm built by the prior stage.

    This compiler is predeclared: f(a,b,c,d)=generated_3(a,b,c) XOR d.
    The 3-argument subroutine itself was GENERATED by previous synthesis.
    A fresh 4-bit oracle must prove the resulting 16-case truth table.
    """
    verify=reverify_successor(successor,TernaryVerifier("ODD_PARITY3"),
                               search_algorithm)
    src=successor["compiled_NAND"]
    generated_binary=library()[6]  # 2-bit mask 0110: synthesized XOR
    PREVIOUS_LOAD(generated_binary,BinarySpecification(6))
    gates=[]
    # remap 3-input method to outer 4-input wire numbering
    base=[0,1,2]
    for left,right in src["gates"]:
        gates.append(sorted((base[left],base[right])))
        base.append(4+len(gates)-1)
    three_output=base[src["output"]]
    out=_program_instantiate(generated_binary,three_output,3,gates,4)
    verifier=QuaternaryVerifier()
    if verifier.check(gates,out) is not None:
        raise HOLD("Second self-composition failed independent 16-case proof")
    raw={
        "schema":FOUR_SCHEMA,
        "status":"PROVED_FINITE_FOUR_BIT_PROPOSAL_ONLY",
        "task":"ODD_PARITY4",
        "gates":gates,"output":out,"gate_count":len(gates),
        "parent_three_input_sha256":successor["sha256"],
        "parent_two_input_sha256":generated_binary["sha256"],
        "full_four_input_domain_exhausted":True,
        "no_unrestricted_code_write":True,
        "real_world_authority":False,
    }
    return _seal(raw)


def reverify_four_input(program,oracle,successor):
    raw=_verify_hash(program)
    if (raw.get("schema")!=FOUR_SCHEMA
        or raw.get("status")!="PROVED_FINITE_FOUR_BIT_PROPOSAL_ONLY"
        or raw.get("parent_three_input_sha256")!=successor.get("sha256")
        or raw.get("full_four_input_domain_exhausted") is not True
        or raw.get("real_world_authority") is not False
        or raw.get("gate_count")!=len(raw.get("gates",[]))):
        raise HOLD("Invalid third-generation method")
    if oracle.check(raw["gates"],raw["output"]) is not None:
        raise HOLD("Four-input truth table refutes generated successor")
    return {"status":"VERIFIED_TYPED_FOUR_INPUT_ALGORITHM",
            "gate_count":len(raw["gates"]),
            "sha256":program["sha256"],
            "real_world_authority":False}
