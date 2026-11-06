"""THOUGHT-015 — emit executable code from a tiny, typed algorithm-repair DSL.

NO model-provided Python source is accepted. All source comes from a fixed
locally reviewed template; proposals choose only four enumerated operators.
"""
from __future__ import annotations
import ast
import hashlib
import json
from dataclasses import dataclass, replace

SCHEMA = "motif.thought015.patch-proposal.v1"
REPAIRS = ("WEIGHTED_PRIORITY", "ENFORCE_BUDGET", "RESOURCE_STATE", "RELAX_IMPROVED")

class PatchError(ValueError):
    pass

@dataclass(frozen=True)
class Config:
    weighted_priority: bool = False
    enforce_budget: bool = False
    resource_state: bool = False
    relax_improved: bool = False

    def as_dict(self):
        return {k: getattr(self, k) for k in ("weighted_priority", "enforce_budget",
                                          "resource_state", "relax_improved")}


def verify_proposal(value):
    if not isinstance(value, dict) or set(value) != {"schema", "repair", "reason", "proposer"}:
        raise PatchError("proposal must have four exact non-executable fields")
    if value["schema"] != SCHEMA or value["repair"] not in REPAIRS:
        raise PatchError("unknown repair operator")
    for key in ("reason", "proposer"):
        s = value[key]
        if not isinstance(s, str) or not 3 <= len(s) <= 200 or any(ord(c) < 32 for c in s):
            raise PatchError("invalid rationale or proposer")
    return dict(value)


def apply_repair(current, proposal):
    verify_proposal(proposal)
    if not isinstance(current, Config):
        raise PatchError("wrong typed configuration")
    key = {"WEIGHTED_PRIORITY": "weighted_priority", "ENFORCE_BUDGET": "enforce_budget",
           "RESOURCE_STATE": "resource_state", "RELAX_IMPROVED": "relax_improved"}[proposal["repair"]]
    if getattr(current, key):
        raise PatchError("no-op repair")
    return replace(current, **{key: True})


# All compiled source is a trusted, closed template, parameterized by booleans.
# No proposer/model-controlled source text, imports, eval, exec, file I/O, networking,
# dynamic attribute access or unrestricted instructions appear in the generated code.
TEMPLATE = '''"""MOTIF generated candidate. REVIEW REQUIRED; not a live execution capability."""
import heapq
import json
import sys

WEIGHTED_PRIORITY = {weighted_priority}
ENFORCE_BUDGET = {enforce_budget}
RESOURCE_STATE = {resource_state}
RELAX_IMPROVED = {relax_improved}

def solve(problem):
    n = problem["n"]
    start, goal, budget = problem["start"], problem["goal"], problem["risk_budget"]
    outgoing = [[] for _ in range(n)]
    for e in problem["edges"]:
        outgoing[e["u"]].append((e["v"], e["cost"], e["risk"]))
    for row in outgoing:
        row.sort()
    queue = []
    seq = 0
    # A priority queue is used for both approaches; initial priority determines
    # whether this is weighted Dijkstra-style search or FIFO-first discovery.
    heapq.heappush(queue, (0, seq, start, 0, 0, (start,), 0))
    first_key = (start, 0) if RESOURCE_STATE else start
    best = {{first_key: 0}}
    while queue:
        priority, _, u, cost, risk, path, depth = heapq.heappop(queue)
        key = (u, risk) if RESOURCE_STATE else u
        if RELAX_IMPROVED and best.get(key, float("inf")) < cost:
            continue
        if u == goal:
            return {{"cost": cost, "risk": risk, "path": list(path)}}
        for v, weight, hazard in outgoing[u]:
            if v in path:
                continue
            new_risk = risk + hazard
            if ENFORCE_BUDGET and new_risk > budget:
                continue
            new_cost = cost + weight
            state = (v, new_risk) if RESOURCE_STATE else v
            if RELAX_IMPROVED:
                if new_cost >= best.get(state, float("inf")):
                    continue
            elif state in best:
                continue
            best[state] = new_cost
            seq += 1
            rank = new_cost if WEIGHTED_PRIORITY else seq
            heapq.heappush(queue, (rank, seq, v, new_cost, new_risk, path + (v,), depth + 1))
    return None

if __name__ == "__main__":
    request = json.load(sys.stdin)
    print(json.dumps([solve(p) for p in request] if isinstance(request, list) else solve(request), sort_keys=True, separators=(",", ":")))
'''


def generate_source(config):
    if not isinstance(config, Config):
        raise PatchError("source configuration must be typed")
    s = TEMPLATE.format(**{k: "True" if v else "False" for k, v in config.as_dict().items()})
    parsed = ast.parse(s)
    # Validate that code generation never inserted unsupported imports or AST nodes.
    permitted_imports = {"heapq", "json", "sys"}
    if any(isinstance(node, (ast.ImportFrom, ast.AsyncFunctionDef, ast.ClassDef,
                             ast.Lambda, ast.Global, ast.Nonlocal)) for node in ast.walk(parsed)):
        raise PatchError("compiler template violated allowed structure")
    for node in ast.walk(parsed):
        if isinstance(node, ast.Import) and any(a.name not in permitted_imports for a in node.names):
            raise PatchError("unauthorized imported library")
    return s


def source_hash(source):
    return hashlib.sha256(source.encode("utf-8")).hexdigest()
