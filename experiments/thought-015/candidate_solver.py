"""MOTIF generated candidate. REVIEW REQUIRED; not a live execution capability."""
import heapq
import json
import sys

WEIGHTED_PRIORITY = True
ENFORCE_BUDGET = True
RESOURCE_STATE = True
RELAX_IMPROVED = True

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
    best = {first_key: 0}
    while queue:
        priority, _, u, cost, risk, path, depth = heapq.heappop(queue)
        key = (u, risk) if RESOURCE_STATE else u
        if RELAX_IMPROVED and best.get(key, float("inf")) < cost:
            continue
        if u == goal:
            return {"cost": cost, "risk": risk, "path": list(path)}
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
