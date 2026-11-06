"""LEGIT-013: external Z3 SMT proof checker for discovered branch shortcuts.

The candidate generator imports this checker only through a deliberate
finite interface. This is a THIRD-PARTY formal solver, not a separately
authored specification: all candidate semantics/axioms are researcher-given.
No trust in hashes/source identity or automatic promotion is implied.
"""
from __future__ import annotations

from hashlib import sha256
import json

GUARDS=("P_ZERO","P_FULL","C_ZERO","C_FULL","P_EQUALS_C")
ANSWERS=("ZERO","PARENT","COLUMN","FULL")
WIDTHS=(8,152,256)

def _check():
    try:
        import z3
    except ImportError as exc:
        raise RuntimeError("External z3-solver REQUIRED; cannot certify") from exc
    return z3

def guard_eval(kind,p,c,full):
    return {
        "P_ZERO":p==0,
        "P_FULL":p==full,
        "C_ZERO":c==0,
        "C_FULL":c==full,
        "P_EQUALS_C":p==c,
    }[kind]

def answer_eval(kind,p,c,full):
    return {"ZERO":0,"PARENT":p,"COLUMN":c,"FULL":full}[kind]

def z3_guard(kind,p,c,full,z3):
    return {
        "P_ZERO":p==z3.BitVecVal(0,p.size()),
        "P_FULL":p==full,
        "C_ZERO":c==z3.BitVecVal(0,p.size()),
        "C_FULL":c==full,
        "P_EQUALS_C":p==c,
    }[kind]

def z3_answer(kind,p,c,full,z3):
    return {
        "ZERO":z3.BitVecVal(0,p.size()),
        "PARENT":p,
        "COLUMN":c,
        "FULL":full,
    }[kind]

def prove_rule(guard,answer,width):
    """Satisfiable = actual counterexample; unsat = universally sound."""
    if guard not in GUARDS or answer not in ANSWERS or width not in WIDTHS:
        raise ValueError("Outside declared proof language")
    z3=_check()
    p=z3.BitVec("parent_mask",width)
    c=z3.BitVec("evidence_mask",width)
    full=z3.BitVecVal((1<<width)-1,width)
    candidate=z3_answer(answer,p,c,full,z3)
    solver=z3.Solver()
    solver.set("timeout",5000)
    solver.add(z3_guard(guard,p,c,full,z3))
    solver.add(candidate != (p & c))
    outcome=solver.check()
    if outcome==z3.unsat:
        return {
            "result":"UNSAT","valid_all_masks":True,"width":width,
            "counterexample":None,"external_solver_version":z3.get_version_string(),
            "proof_obligation":"guard(P,C) IMPLIES proposed(P,C) == P BITAND C",
        }
    if outcome==z3.sat:
        model=solver.model()
        p0=model.eval(p,model_completion=True).as_long()
        c0=model.eval(c,model_completion=True).as_long()
        return {
            "result":"SAT","valid_all_masks":False,"width":width,
            "counterexample":{"parent":p0,"column":c0,
                              "reference":p0&c0,
                              "incorrect":answer_eval(answer,p0,c0,(1<<width)-1)},
            "external_solver_version":z3.get_version_string(),
        }
    raise RuntimeError("SMT result UNKNOWN: fail closed")

def independent_recurrence_proof(width=152):
    """Z3 proves the parent-bitset recurrence and sound source reduction."""
    z3=_check()
    p,c=z3.BitVecs("parent column",width)
    derived=p&c
    checks={}
    for name,unwanted in {
        "child_gain_outside_parent":(derived&~p)!=0,
        "child_gain_outside_evidence":(derived&~c)!=0,
        "zero_parent_has_nonzero_child":z3.And(p==0,derived!=0),
        "full_parent_changes_column":z3.And(p==((1<<width)-1),derived!=c),
    }.items():
        s=z3.Solver();s.set("timeout",5000);s.add(unwanted)
        if s.check()!=z3.unsat:raise RuntimeError("Independent SMT obligation failed: "+name)
        checks[name]="UNSAT"
    return {"solver":"Z3","version":z3.get_version_string(),
            "bitvector_width":width,
            "properties":checks,
            "all_properties_proved_in_encoded_finite_BitVec_theory":True,
            "external_formal_checker_actually_invoked":True,
            "logical_formulas_authored_by_project":True}
