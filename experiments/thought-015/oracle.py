"""Independent, exhaustive simple-path oracle for small *synthetic* graphs.

This deliberately shares no graph search implementation with candidate code.
"""
from __future__ import annotations
import json
from functools import lru_cache

class SpecimenError(ValueError):
    pass


def validate_problem(p):
    if not isinstance(p, dict) or set(p) != {"n", "start", "goal", "risk_budget", "edges"}:
        raise SpecimenError("bad graph specimen keys")
    n = p["n"]
    if type(n) is not int or not 2 <= n <= 8:
        raise SpecimenError("graph must have 2..8 vertices")
    for k in ("start", "goal"):
        if type(p[k]) is not int or not 0 <= p[k] < n:
            raise SpecimenError("invalid source or target")
    if p["start"] == p["goal"]:
        raise SpecimenError("source and target must differ")
    if type(p["risk_budget"]) is not int or not 0 <= p["risk_budget"] <= 12:
        raise SpecimenError("invalid risk budget")
    edges = p["edges"]
    if not isinstance(edges, list) or len(edges) > 35:
        raise SpecimenError("bounded edge list required")
    seen = set()
    for e in edges:
        if not isinstance(e, dict) or set(e) != {"u", "v", "cost", "risk"}:
            raise SpecimenError("bad edge")
        u, v, cost, risk = (e[k] for k in ("u", "v", "cost", "risk"))
        if any(type(x) is not int for x in (u, v, cost, risk)) or not (
            0 <= u < n and 0 <= v < n and u != v and 1 <= cost <= 12 and 0 <= risk <= 5):
            raise SpecimenError("invalid edge values")
        if (u,v) in seen:
            raise SpecimenError("ambiguous duplicate directed edge")
        seen.add((u,v))
    return p


def independent_min_cost(p):
    validate_problem(p)
    key = json.dumps(p,sort_keys=True,separators=(",",":"))
    return _cached_independent_min_cost(key)

@lru_cache(maxsize=1024)
def _cached_independent_min_cost(key):
    p = json.loads(key)
    adj = {i: [] for i in range(p["n"])}
    for e in p["edges"]:
        adj[e["u"]].append((e["v"],e["cost"],e["risk"]))
    answers = []
    def visit(node, path, cost, risk):
        if node == p["goal"]:
            answers.append((cost, risk, tuple(path)))
            return
        for v, weight, hazard in adj[node]:
            if v not in path and risk + hazard <= p["risk_budget"]:
                visit(v, path+[v], cost+weight, risk+hazard)
    visit(p["start"], [p["start"]], 0, 0)
    return min(answers) if answers else None


def check_answer(p, answer):
    """Compare optimum *cost*, verify path, summed risk, feasibility independently."""
    objective = independent_min_cost(p)
    if answer is None:
        return objective is None
    if not isinstance(answer, dict) or set(answer) != {"cost","risk","path"}:
        return False
    path = answer["path"]
    if not isinstance(path, list) or not path or path[0] != p["start"] or path[-1] != p["goal"]:
        return False
    if len(path) != len(set(path)) or len(path)>p["n"]:
        return False
    index = {(e["u"],e["v"]):(e["cost"],e["risk"]) for e in p["edges"]}
    cost = risk = 0
    for a,b in zip(path,path[1:]):
        if (a,b) not in index:
            return False
        w,h = index[(a,b)]
        cost+=w; risk+=h
    return (type(answer["cost"]) is int and type(answer["risk"]) is int and
            answer["cost"] == cost and answer["risk"] == risk and
            risk <= p["risk_budget"] and objective is not None and cost==objective[0])
