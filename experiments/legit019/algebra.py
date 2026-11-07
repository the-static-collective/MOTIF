"""Bounded autonomous *conjecture miner* and formal proof gate.

Actual search groups symbolic bitvector expressions by experimental values,
conjectures equalities WITHOUT having equality identities enumerated as
theorems, asks external Z3 to DISPROVE them, and saves SAT witnesses or
UNSAT results. Proofs are of 64-bit semantics ONLY. They are NOT evidence
that a theorem is historically new (most basic rewrites are textbook).

The MINER never reads the SyGuS heldout answers. Any proof-carrying
rewrite is checked again before being applied to the synthesis engine.
"""
from __future__ import annotations
from functools import lru_cache
from itertools import combinations,product
from hashlib import sha256
import json

WIDTH=64
MASK=(1<<WIDTH)-1
OPS_UNARY=("not","shl1","shr1","shr4","shr16")
OPS_BINARY=("and","or","xor","add")
X=("x",)
ZERO=("k",0)
ONE=("k",1)
ALL=("k",MASK)
ATOMS=(X,ZERO,ONE,ALL)
class HOLD(ValueError):pass

def norm(t):
    if not isinstance(t,tuple) or not t or t[0] not in (
            "x","k")+OPS_UNARY+OPS_BINARY:
        raise HOLD("Unsupported symbolic program")
    op=t[0]
    if op=="x":
        if len(t)!=1:raise HOLD("Unknown input")
    elif op=="k":
        if len(t)!=2 or type(t[1]) is not int or not 0<=t[1]<=MASK:
            raise HOLD("Unbounded symbolic constant")
    elif op in OPS_UNARY:
        if len(t)!=2:raise HOLD("Malformed unary")
        norm(t[1])
    else:
        if len(t)!=3:raise HOLD("Malformed binary")
        norm(t[1]);norm(t[2])
    return t

def val(t,x,width=WIDTH):
    op=t[0];mask=(1<<width)-1
    if op=="x":return x&mask
    if op=="k":return t[1]&mask
    a=val(t[1],x,width)
    if op=="not":return (~a)&mask
    if op=="shl1":return (a<<1)&mask
    if op=="shr1":return a>>1
    if op=="shr4":return a>>4
    if op=="shr16":return a>>16
    b=val(t[2],x,width)
    if op=="and":return a&b
    if op=="or":return a|b
    if op=="xor":return a^b
    if op=="add":return (a+b)&mask
    raise HOLD("Unknown symbolic operation")

def z3val(t,x):
    import z3
    op=t[0]
    if op=="x":return x
    if op=="k":return z3.BitVecVal(t[1],x.size())
    a=z3val(t[1],x)
    if op=="not":return ~a
    if op=="shl1":return a<<1
    if op=="shr1":return z3.LShR(a,1)
    if op=="shr4":return z3.LShR(a,4)
    if op=="shr16":return z3.LShR(a,16)
    b=z3val(t[2],x)
    if op=="and":return a&b
    if op=="or":return a|b
    if op=="xor":return a^b
    if op=="add":return a+b
    raise HOLD("Unknown Z3 term")

def prove_equal(a,b,width=WIDTH):
    import z3
    norm(a);norm(b)
    x=z3.BitVec("external_independent_math_checker_x",width)
    solver=z3.Solver()
    solver.set(timeout=3000)
    solver.add(z3val(a,x)!=z3val(b,x))
    status=solver.check()
    if status==z3.unsat:
        return {"z3_result":"UNSAT","identity_valid":True,"width":width,
                "counterexample":None}
    if status==z3.sat:
        witness=solver.model().eval(x,model_completion=True).as_long()
        if val(a,witness,width)==val(b,witness,width):
            raise HOLD("SMT model was not a valid mathematical counterexample")
        return {"z3_result":"SAT","identity_valid":False,"width":width,
                "counterexample":{
                    "x":hex(witness),"left":hex(val(a,witness,width)),
                    "right":hex(val(b,witness,width))}}
    raise HOLD("Z3 proof timeout/unknown is NOT a successful theorem")

def expression_pool():
    """Construct candidate formulae by generic syntax enumeration.

    No theorem templates: the solver itself detects coincident outputs
    and asks whether the coincidence holds for all 64-bit inputs.
    """
    pool=list(ATOMS)
    for op in OPS_UNARY:
        pool.extend((op,a) for a in ATOMS)
    for op in OPS_BINARY:
        for a,b in combinations(ATOMS,2):
            pool.append((op,a,b))
        if op in ("xor","add","and","or"):
            pool.append((op,X,X))
    seed=tuple(pool)
    for t in seed:
        if t==X or t[0]=="k":continue
        for op in OPS_BINARY:
            pool.append((op,t,ONE))
            pool.append((op,t,X))
    return tuple(dict.fromkeys(pool))

def conjecture_mine(max_tries=96):
    """Counterexample-guided discovery of equalities.

    Candidate equivalence is proposed solely when initial outputs agree
    on the probes [0,1]. Every SAT counterexample is incorporated into
    the next classification. Search stops after several genuinely proved
    laws and counterexample failures, not when it merely finds an example.
    """
    candidates=expression_pool()
    probes=[0,1]
    tried=set()
    proof=[]
    refuted=[]
    proposal_count=0
    for round_number in range(max_tries):
        signatures={}
        for e in candidates:
            sig=tuple(val(e,x) for x in probes)
            signatures.setdefault(sig,[]).append(e)
        pair=None
        for group in signatures.values():
            if len(group)<2:continue
            ordered=sorted(group,key=lambda e:(len(repr(e)),repr(e)))
            for left,right in combinations(ordered[:10],2):
                # Ignore purely identical syntax. Equal values may be an
                # actual identity or only a coincidence on the probes.
                key=tuple(sorted((repr(left),repr(right))))
                if key not in tried:
                    pair=(left,right,key)
                    break
            if pair is not None:break
        if pair is None:break
        left,right,key=pair
        tried.add(key)
        proposal_count+=1
        evidence=prove_equal(left,right)
        record={
            "lhs":left,"rhs":right,
            "initial_probe_agreement":True,
            "formal":evidence,
            "search_round":round_number,
            "candidate_pool_size":len(candidates),
        }
        if evidence["identity_valid"]:
            # Both an external 64-bit SMT decision and an independent
            # finite 8-bit truth table must agree, with wrap semantics.
            if not all(val(left,x,8)==val(right,x,8) for x in range(256)):
                raise HOLD("Narrow independent model refuted formal theorem")
            record["secondary_exhaustive_8bit_check"]=256
            proof.append(record)
        else:
            refuted.append(record)
            witness=int(evidence["counterexample"]["x"],16)
            if witness not in probes:
                probes.append(witness)
        if len(proof)>=8 and len(refuted)>=2:
            break
    if not proof or not refuted:
        raise HOLD("No actual checked proof/counterexample pair discovered")
    # Select executable rewrites from proven equalities only. Normalize
    # the longer side toward the shorter side, replacing subtrees by exact
    # structural match (no untrusted wildcard matching).
    rewrites=[]
    seen=set()
    for row in proof:
        a,b=row["lhs"],row["rhs"]
        longer,shorter=(a,b) if len(repr(a))>len(repr(b)) else (b,a)
        if longer==shorter or longer in seen:
            continue
        seen.add(longer)
        rewrites.append((longer,shorter))
    return {
        "engine":"COUNTEREXAMPLE_GUIDED_BITVECTOR_IDENTITY_CONJECTURE",
        "probe_values":list(map(hex,probes)),
        "examined_proposals":proposal_count,
        "independent_source":"NONE_FOR_NEWNESS_ESTIMATE",
        "z3_formal_proved":proof,
        "z3_formal_refuted":refuted,
        "rewrites":rewrites,
        "new_math_novelty_authenticated":False,
        "mathematical_laws_historically_new":False,
        "unbounded_integer_theorems_proved":False,
        "independent_external_theorem_checker":"Z3_THIRD_PARTY_BOUNDED_BITVECTORS",
    }

def canonical(e,rewrites):
    norm(e)
    def walk(node):
        if node[0] in OPS_UNARY:
            node=(node[0],walk(node[1]))
        elif node[0] in OPS_BINARY:
            node=(node[0],walk(node[1]),walk(node[2]))
        for source,dest in rewrites:
            if node==source:return dest
        return node
    return walk(e)

def verified_rewrites(receipt):
    if not isinstance(receipt,dict) or len(receipt.get("rewrites",[]))>100:
        raise HOLD("No bounded proven rewrite set")
    formally={
        (str(row["lhs"]),str(row["rhs"]))
        for row in receipt["z3_formal_proved"]
        if row["formal"]["identity_valid"]
    }
    out=[]
    for a,b in receipt["rewrites"]:
        a,b=_tuplify(a),_tuplify(b)
        if ((str(a),str(b)) not in formally and
            (str(b),str(a)) not in formally):
            raise HOLD("Unproved equality smuggled into source rewriting")
        if not prove_equal(a,b)["identity_valid"]:
            raise HOLD("Z3 proof no longer valid")
        out.append((a,b))
    return out

def _tuplify(obj):
    if isinstance(obj,list):return tuple(_tuplify(x) for x in obj)
    return obj
