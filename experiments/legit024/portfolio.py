"""MOTIF-LEGIT-024: typed mathematical tool ecology, with exact acceptance contracts.

This is an executable, project-authored research experiment, not an autonomous
general theorem prover. All task formats are bounded. No eval, shell, network,
remote code, arbitrary Python expression parsing, or credential use.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from itertools import permutations, product
from math import prod
from pathlib import Path
from time import process_time_ns
import sys

HERE = Path(__file__).resolve().parent
for name in ("legit021", "legit022", "legit023"):
    sys.path.insert(0, str(HERE.parent / name))

from graph_inventor import reference_count, characterize
from methods import hom_count, joint_wl_separation, vf2pp_decision
from trial import prior_apertures
from shoulders import frozen_policies

# Method IDs are stable executable contracts, never marketing adjectives.
METHODS = {
    "polynomial_identity": ("sympy_exact", "native_polyring",
                             "motif_sample_then_certify"),
    "bounded_integer_optimum": ("z3_optimize", "ortools_cp_sat",
                                "native_exhaustive"),
    "graph_nonisomorphism": ("joint_1wl", "vf2pp"),
    "graph_hom_witness": ("motif_inherited_021", "classical_training_dp"),
}
DEFAULT = dict(METHODS)
NOT_INTEGRATED = ("Lean4_mathlib_formal_certificates", "cvc5_sygus",
                  "nauty_traces", "unrestricted_theorem_synthesis")


class Refuse(ValueError):
    pass


def _coeff(x):
    if type(x) is not int or abs(x) > 1000:
        raise Refuse("non-integer or out-of-range coefficient")
    return x


def _poly_add(a, b):
    c = a.copy()
    for k, v in b.items():
        c[k] = c.get(k, 0) + v
    return {k: v for k, v in c.items() if v}


def _poly_mul(a, b):
    c = {}
    for i, x in a.items():
        for j, y in b.items():
            c[i+j] = c.get(i+j, 0) + x*y
    return {k: v for k, v in c.items() if v}


def native_poly(node, depth=0):
    """Tiny total AST over Z[x], no string interpretation or code execution."""
    if depth > 10 or not isinstance(node, (list, tuple)) or not node:
        raise Refuse("invalid/big polynomial tree")
    tag = node[0]
    if tag == "x" and len(node) == 1:
        return {1: 1}
    if tag == "const" and len(node) == 2:
        c = _coeff(node[1])
        return {0: c} if c else {}
    if tag in ("add", "mul") and len(node) == 3:
        a = native_poly(node[1], depth+1)
        b = native_poly(node[2], depth+1)
        out = _poly_add(a, b) if tag == "add" else _poly_mul(a, b)
        if out and max(out) > 20:
            raise Refuse("degree bound exceeded")
        return out
    if tag == "pow" and len(node) == 3:
        if type(node[2]) is not int or not (0 <= node[2] <= 6):
            raise Refuse("exponent bound exceeded")
        base = native_poly(node[1], depth+1)
        out = {0: 1}
        for _ in range(node[2]):
            out = _poly_mul(out, base)
            if out and max(out) > 20:
                raise Refuse("degree bound exceeded")
        return out
    raise Refuse("unknown polynomial operator")


def poly_value(p, x):
    return sum(c*x**k for k, c in p.items())


def sympy_poly(node):
    import sympy as sp
    x = sp.Symbol("x")
    def walk(n):
        tag = n[0]
        if tag == "x":
            return x
        if tag == "const":
            return sp.Integer(n[1])
        if tag == "add":
            return walk(n[1]) + walk(n[2])
        if tag == "mul":
            return walk(n[1]) * walk(n[2])
        if tag == "pow":
            return walk(n[1]) ** n[2]
        raise Refuse("unknown polynomial operator")
    out = sp.Poly(sp.expand(walk(node)), x, domain="ZZ")
    return {int(k[0]): int(v) for k, v in out.terms() if v}


def _poly_answer(task, method):
    a, b = task["left"], task["right"]
    # Validate complete AST and degree even when the selected engine is SymPy.
    native_a, native_b = native_poly(a), native_poly(b)
    if method in ("sympy_exact", "motif_sample_then_certify"):
        if method == "motif_sample_then_certify":
            # These are suggestive observations only; all candidates still
            # pass through exact symbolic proof before any verified claim.
            samples = [(x, poly_value(native_a, x), poly_value(native_b, x))
                       for x in (0, 1, 2)]
        else:
            samples = []
        first, second = sympy_poly(a), sympy_poly(b)
    else:
        first, second = native_a, native_b
        samples = []
    diff = _poly_add(first, {k: -v for k, v in second.items()})
    if not diff:
        return {"verdict": "IDENTITY", "degree": max(first, default=0),
                "observations": samples}
    # Nonzero integer polynomial of degree d cannot vanish at d+1
    # distinct integers, so this search is complete.
    degree = max(diff)
    witness = next(x for x in range(degree+1) if poly_value(diff, x))
    return {"verdict": "COUNTEREXAMPLE", "x": witness,
            "values": [poly_value(first, witness),
                       poly_value(second, witness)],
            "observations": samples}


def validate_opt(task):
    bounds = task.get("bounds")
    goal = task.get("objective")
    conditions = task.get("conditions")
    if not isinstance(bounds, list) or not 1 <= len(bounds) <= 4:
        raise Refuse("invalid integer variable count")
    cardinality = 1
    for row in bounds:
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            raise Refuse("invalid bound")
        lo, hi = map(_coeff, row)
        if hi < lo or hi-lo > 15:
            raise Refuse("unbounded search")
        cardinality *= hi-lo+1
    if cardinality > 4096:
        raise Refuse("too many assignments for independent verification")
    n = len(bounds)
    if not isinstance(goal, list) or len(goal) != n:
        raise Refuse("invalid objective")
    for c in goal:
        _coeff(c)
    if not isinstance(conditions, list) or len(conditions) > 14:
        raise Refuse("invalid condition list")
    for c in conditions:
        if not isinstance(c, dict) or set(c) != {"a", "op", "b"}:
            raise Refuse("invalid linear constraint")
        if not isinstance(c["a"], list) or len(c["a"]) != n:
            raise Refuse("invalid linear row")
        for v in c["a"]:
            _coeff(v)
        _coeff(c["b"])
        if c["op"] not in ("<=", ">=", "=="):
            raise Refuse("invalid relation")
    return n, cardinality


def allowed(task, xs):
    for row in task["conditions"]:
        lhs = sum(a*x for a, x in zip(row["a"], xs))
        if row["op"] == "<=" and not lhs <= row["b"]:
            return False
        if row["op"] == ">=" and not lhs >= row["b"]:
            return False
        if row["op"] == "==" and not lhs == row["b"]:
            return False
    return True


def exhaustive_opt(task):
    """Independent complete finite oracle; never optimized by the solver."""
    validate_opt(task)
    choices = (range(lo, hi+1) for lo, hi in task["bounds"])
    best = None
    for xs in product(*choices):
        if allowed(task, xs):
            objective = sum(a*x for a, x in zip(task["objective"], xs))
            if best is None or (objective, xs) < (best[0], tuple(best[1])):
                best = (objective, list(xs))
    if best is None:
        return {"verdict": "INFEASIBLE"}
    return {"verdict": "OPTIMUM", "value": best[0], "assignment": best[1]}


def _z3_opt(task):
    import z3
    n, _ = validate_opt(task)
    opt = z3.Optimize()
    opt.set(timeout=1500)
    xs = [z3.Int("x%d" % i) for i in range(n)]
    for x, (lo, hi) in zip(xs, task["bounds"]):
        opt.add(x >= lo, x <= hi)
    for row in task["conditions"]:
        lhs = z3.Sum([a*x for a, x in zip(row["a"], xs)])
        opt.add({"<=": lambda: lhs <= row["b"],
                 ">=": lambda: lhs >= row["b"],
                 "==": lambda: lhs == row["b"]}[row["op"]]())
    cost = z3.Sum([a*x for a, x in zip(task["objective"], xs)])
    opt.minimize(cost)
    status = opt.check()
    if status == z3.unsat:
        return {"verdict": "INFEASIBLE"}
    if status != z3.sat:
        return {"verdict": "ABSTAIN", "reason": "Z3 unknown or timeout"}
    model = opt.model()
    assignment = [model.eval(x).as_long() for x in xs]
    return {"verdict": "OPTIMUM", "value": sum(a*x for a, x in
            zip(task["objective"], assignment)), "assignment": assignment}


def _ortools_opt(task):
    from ortools.sat.python import cp_model
    n, _ = validate_opt(task)
    model = cp_model.CpModel()
    xs = [model.new_int_var(lo, hi, "x%d" % i)
          for i, (lo, hi) in enumerate(task["bounds"])]
    for row in task["conditions"]:
        lhs = sum(a*x for a, x in zip(row["a"], xs))
        if row["op"] == "<=":
            model.add(lhs <= row["b"])
        elif row["op"] == ">=":
            model.add(lhs >= row["b"])
        else:
            model.add(lhs == row["b"])
    model.minimize(sum(a*x for a, x in zip(task["objective"], xs)))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 1.5
    solver.parameters.num_search_workers = 1
    result = solver.solve(model)
    if result == cp_model.INFEASIBLE:
        return {"verdict": "INFEASIBLE"}
    if result != cp_model.OPTIMAL:
        return {"verdict": "ABSTAIN", "reason": "CP-SAT not proven optimal"}
    assignment = [solver.value(x) for x in xs]
    return {"verdict": "OPTIMUM", "value": sum(a*x for a, x in
            zip(task["objective"], assignment)), "assignment": assignment}


def _adj(g):
    n, edges = g
    if type(n) is not int or not (0 <= n <= 7):
        raise Refuse("invalid graph size")
    rows = [set() for _ in range(n)]
    for e in edges:
        if len(e) != 2:
            raise Refuse("invalid edge")
        a, b = e
        if not (0 <= a < n and 0 <= b < n) or a == b:
            raise Refuse("invalid simple graph")
        rows[a].add(b)
        rows[b].add(a)
    return tuple(frozenset(row) for row in rows)


def brute_isomorphic(first, second):
    """Exact independent graph oracle for <=7 vertices (not VF2++)."""
    A, B = _adj(first), _adj(second)
    if len(A) != len(B):
        return False
    if sorted(map(len, A)) != sorted(map(len, B)):
        return False
    n = len(A)
    edges_B = {(i, j) for i in range(n) for j in B[i] if i < j}
    edges_A = [(i, j) for i in range(n) for j in A[i] if i < j]
    for perm in permutations(range(n)):
        if all(len(A[u]) == len(B[perm[u]]) for u in range(n)) and {
            tuple(sorted((perm[u], perm[v]))) for u, v in edges_A
        } == edges_B:
            return True
    return False


@lru_cache(1)
def _graph_orders():
    from atlas import cohort
    train, _, _ = cohort()
    order, _ = frozen_policies(train)
    priors, _ = prior_apertures()
    return {
        "motif_inherited_021": tuple(priors) +
            tuple(p for p in order["CANONICAL_CONNECTED"] if p not in priors),
        "classical_training_dp": tuple(
            order["CLASSICAL_DP_OPTIMAL_TRAINING_QUESTIONS"])
    }


def _hom_witness(task, method):
    a, b = task["graphs"]
    _adj(a)
    _adj(b)
    for source in _graph_orders()[method]:
        p, q = hom_count(source, a)["value"], hom_count(source, b)["value"]
        if p != q:
            return {"verdict": "SEPARATING_HOM_COUNT",
                    "source": source, "values": [p, q]}
    return {"verdict": "ABSTAIN", "reason": "No witness in bounded grammar"}


def execute(task, method):
    kind = task["kind"]
    if method not in METHODS.get(kind, ()):
        raise Refuse("method not eligible for problem contract")
    if kind == "polynomial_identity":
        native_poly(task["left"])
        native_poly(task["right"])
        return _poly_answer(task, method)
    if kind == "bounded_integer_optimum":
        validate_opt(task)
        if method == "z3_optimize":
            return _z3_opt(task)
        if method == "ortools_cp_sat":
            return _ortools_opt(task)
        return exhaustive_opt(task)
    if kind == "graph_nonisomorphism":
        a, b = task["graphs"]
        _adj(a)
        _adj(b)
        if method == "vf2pp":
            result = vf2pp_decision(a, b)
            return {"verdict": ("ISOMORPHIC" if result["isomorphic"]
                                else "NONISOMORPHIC")}
        result = joint_wl_separation(a, b)
        return {"verdict": ("NONISOMORPHIC" if result["conclusion"] ==
                            "CERTIFIED_NONISOMORPHIC_BY_INVARIANT"
                            else "ABSTAIN"),
                "reason": result["conclusion"]}
    if kind == "graph_hom_witness":
        return _hom_witness(task, method)
    raise Refuse("unsupported task")


def verify(task, method, output):
    """Proof obligation enforced independently of the candidate's opinion.

    Does NOT claim a formal Lean certificate; independent exact checking for
    these tiny finite problem domains is the acceptance contract.
    """
    kind = task["kind"]
    if output["verdict"] == "ABSTAIN":
        return {"status": "ABSTAIN", "checked_by": "not_promoted"}
    if kind == "polynomial_identity":
        A, B = native_poly(task["left"]), native_poly(task["right"])
        if (A, B) != (sympy_poly(task["left"]), sympy_poly(task["right"])):
            raise Refuse("native and SymPy coefficient oracles disagree")
        equivalent = A == B
        if equivalent != (output["verdict"] == "IDENTITY"):
            raise Refuse("polynomial conclusion disagrees with exact coefficients")
        if not equivalent:
            x = output["x"]
            if type(x) is not int or not (0 <= x <= max(_poly_add(
                A, {k:-v for k,v in B.items()}))):
                raise Refuse("invalid polynomial witness")
            if [poly_value(A, x), poly_value(B, x)] != output["values"] or (
                    output["values"][0] == output["values"][1]):
                raise Refuse("false polynomial witness")
        return {"status": "VERIFIED", "checked_by":
                "independent_SymPy_and_native_integer_polynomial_ring"}
    if kind == "bounded_integer_optimum":
        truth = exhaustive_opt(task)
        if truth["verdict"] != output["verdict"]:
            raise Refuse("solver verdict disagrees with exhaustive finite oracle")
        if truth["verdict"] == "OPTIMUM":
            xs = output.get("assignment")
            if not isinstance(xs, list) or len(xs) != len(task["bounds"]):
                raise Refuse("missing model")
            if any(type(x) is not int or not lo <= x <= hi for x, (lo, hi)
                   in zip(xs, task["bounds"])) or not allowed(task, xs):
                raise Refuse("invalid integer model")
            if output["value"] != truth["value"] or sum(a*x for a,x in zip(
                task["objective"], xs)) != truth["value"]:
                raise Refuse("suboptimal or incorrect objective")
        if method == "native_exhaustive":
            # Pure exhaustive search is not independent of itself. Require a
            # separate optimizer before claiming cross-validated acceptance.
            other = _z3_opt(task)
            if other["verdict"] != truth["verdict"] or (
                other["verdict"] == "OPTIMUM" and
                other["value"] != truth["value"]):
                raise Refuse("native method lacks Z3 independent concurrence")
        return {"status": "VERIFIED",
                "checked_by": ("exhaustive_enumerator_and_Z3" if
                               method == "native_exhaustive" else
                               "independent_exhaustive_enumerator")}
    if kind == "graph_nonisomorphism":
        a, b = task["graphs"]
        independent = brute_isomorphic(a, b)
        if output["verdict"] != ("ISOMORPHIC" if independent
                                 else "NONISOMORPHIC"):
            raise Refuse("graph claim disagrees with exhaustive permutations")
        return {"status": "VERIFIED",
                "checked_by": "exhaustive_bijection_enumerator"}
    if kind == "graph_hom_witness":
        a, b = task["graphs"]
        source = output["source"]
        counts = [reference_count(source, a), reference_count(source, b)]
        if (output["verdict"] != "SEPARATING_HOM_COUNT" or
                counts != output["values"] or counts[0] == counts[1]):
            raise Refuse("invalid independent homomorphism witness")
        return {"status": "VERIFIED",
                "checked_by": "LEGIT021_independent_vertex_assignment_counter"}
    raise Refuse("unknown verification contract")


def try_method(task, method):
    begin = process_time_ns()
    try:
        answer = execute(task, method)
        acceptance = verify(task, method, answer)
        return {
            "method": method, "status": acceptance["status"],
            "certificate": answer,
            "verification": acceptance["checked_by"],
            "cpu_ms": round((process_time_ns()-begin)/1_000_000, 5),
        }
    except (ImportError, ModuleNotFoundError) as ex:
        return {"method": method, "status": "UNAVAILABLE",
                "reason": type(ex).__name__, "cpu_ms": round(
                    (process_time_ns()-begin)/1_000_000, 5)}
    except (Refuse, ValueError, ArithmeticError) as ex:
        return {"method": method, "status": "REJECTED",
                "reason": str(ex), "cpu_ms": round(
                    (process_time_ns()-begin)/1_000_000, 5)}


def execute_portfolio(task, ordering):
    """Run next method after ABSTAIN; reject fabrication without promotion."""
    attempts = []
    for name in ordering:
        result = try_method(task, name)
        attempts.append(result)
        if result["status"] == "VERIFIED":
            break
    return {"task_id": task["id"], "kind": task["kind"],
            "status": ("VERIFIED" if attempts and attempts[-1]["status"] ==
                       "VERIFIED" else "RESEARCH_HOLD"),
            "tried": attempts, "method_count": len(attempts),
            "cpu_ms": round(sum(x["cpu_ms"] for x in attempts), 5)}
