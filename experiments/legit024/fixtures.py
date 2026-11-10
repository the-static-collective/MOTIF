"""LEGIT-024 fixture corpus: old externally authored graphs, new project-authored math.

No solver answer, benchmark score, or policy winner is embedded in these
fixtures. Atlas train/heldout partition remains LEGIT-022's predeclared split.
Symbolic and optimization tasks are intentionally authored within this project;
they are not passed off as independent research challenges.
"""
from __future__ import annotations
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "legit022"))
from atlas import cohort

def C(v):
    return ["const", v]
def X():
    return ["x"]
def A(a, b):
    return ["add", a, b]
def M(a, b):
    return ["mul", a, b]
def P(a, n):
    return ["pow", a, n]

def sym_task(label, left, right, phase):
    return {"id": label, "kind": "polynomial_identity", "left": left,
            "right": right, "phase": phase,
            "source": "ENGINEER_AUTHORED_STANDARD_POLYNOMIAL_EXAMPLE"}

def opt_task(label, bounds, obj, conditions, phase):
    return {"id": label, "kind": "bounded_integer_optimum",
            "bounds": bounds, "objective": obj, "conditions": conditions,
            "phase": phase,
            "source": "ENGINEER_AUTHORED_FINITE_INTEGER_PROGRAM"}

def _constraint(a, op, b):
    return {"a": a, "op": op, "b": b}

def suite():
    train_graphs, heldout_graphs, origin = cohort()
    train, heldout = [], []
    for phase, source in (("training", train_graphs),
                          ("heldout", heldout_graphs)):
        destination = train if phase == "training" else heldout
        for case in source:
            for goal in ("graph_nonisomorphism", "graph_hom_witness"):
                destination.append({
                    "id": "atlas_%d_%d_%s" %
                          (case.atlas_ids[0], case.atlas_ids[1], goal),
                    "kind": goal, "graphs": case.graphs, "phase": phase,
                    "source": "READ_WILSON_1998_GRAPH_ATLAS_PROJECT_AUTHORED_PAIR"
                })

    # Training and heldout polynomials share an intentionally tiny grammar,
    # but do not share identical tasks.
    for k in (1, 2, 3, 4, 5, 6):
        left = P(A(X(), C(k)), 2)
        right = A(A(P(X(), 2), M(C(2*k), X())), C(k*k))
        if k % 3 == 0:
            right = A(right, C(1))
        train.append(sym_task("poly_train_%d" % k, left, right, "training"))
    for k in (7, 8, 9, 10, 11, 12, 13, 14):
        left = M(A(X(), C(k)), A(X(), C(-k)))
        right = A(P(X(), 2), C(-(k*k) + (1 if k % 3 == 0 else 0)))
        heldout.append(sym_task("poly_holdout_%d" % k, left, right,
                                "heldout"))

    for k in (2, 4, 6, 8, 10, 12):
        train.append(opt_task("int_train_%d" % k,
            [[0, 5], [0, 5]], [3, 1],
            [_constraint([1, 2], ">=", k),
             _constraint([1, -1], "<=", 3)], "training"))
    for k in (1, 3, 5, 7, 9, 11, 13, 15):
        heldout.append(opt_task("int_holdout_%d" % k,
            [[0, 5], [0, 5]], [2, 3],
            [_constraint([2, 1], ">=", k),
             _constraint([1, -1], ">=", -2)], "heldout"))

    ids = [t["id"] for t in train + heldout]
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate research tasks")
    return train, heldout, origin
