"""Human-designed development examples + fixed, separately seeded audit/stress sets.

The model sees development diagnostics and never sees the evaluation labels or
held-out graph instances during source proposal. The random cases are synthetic.
"""
from __future__ import annotations
from random import Random


def case(edges, budget=0, n=4, note="", category=""):
    return {"problem":{"n":n,"start":0,"goal":n-1,"risk_budget":budget,
                       "edges":[{"u":u,"v":v,"cost":c,"risk":r} for u,v,c,r in edges]},
            "note":note,"category":category}

DEV = [
    case([(0,3,9,0),(0,1,1,0),(1,3,1,0)], 0,
         note="A two leg route is cheaper than the first direct route despite more steps",category="weighted"),
    case([(0,3,1,4),(0,1,3,0),(1,3,3,0)], 1,
         note="The cheapest direct path exceeds the risk budget; a safer expensive path is valid",category="risk"),
    case([(0,1,1,1),(0,2,2,0),(2,1,1,0),(1,3,1,1)],1,
         note="An alternate arrival at the same node has lower risk, allowing the goal",category="resource"),
    case([(0,1,3,0),(0,2,1,0),(2,1,1,0),(1,3,1,0)],0,
         note="A later arrival improves the cost of an already discovered node",category="revisit"),
    case([(0,3,8,1),(0,1,1,0),(1,2,1,0),(2,3,1,0)],1,
         note="Longer chain has lower total weight",category="weighted"),
    case([(0,3,1,2),(0,1,2,0),(1,3,2,0)],0,
         note="Risk cap excludes apparent cheapest target",category="risk"),
    case([(0,1,1,1),(0,2,3,0),(2,1,1,0),(1,3,1,1)],1,
         note="Visiting a vertex with less accumulated risk permits an outcome",category="resource"),
    case([(0,1,4,0),(0,2,1,0),(2,1,2,0),(1,3,1,0)],0,
         note="Reaching same vertex again at lower cost must revise previous label",category="revisit"),
]
SAFETY = [
    case([(0,3,1,3)],0,note="Do not silently bypass risk cap"),
    case([(0,1,1,0),(1,2,1,0),(2,3,1,0)],0,note="Valid chain must remain visible"),
    case([(0,1,1,0),(1,0,1,0)],0,note="No reachable target, stop rather than cycle"),
    case([(0,3,8,0),(0,1,2,0),(1,3,3,0)],0,note="Keep weighted optimum"),
]

TRAIN_DIAGNOSTICS = [
("direct hop fewer steps but higher total cost", "WEIGHTED_PRIORITY"),
("more legs but cheap route should win", "WEIGHTED_PRIORITY"),
("the sum of edge weights determines the answer", "WEIGHTED_PRIORITY"),
("route exceeds allowed hazard limit", "ENFORCE_BUDGET"),
("risk budget disallows the shortcut", "ENFORCE_BUDGET"),
("invalid path uses too much risk", "ENFORCE_BUDGET"),
("another arrival at the same node with lower risk", "RESOURCE_STATE"),
("different remaining resource at a vertex", "RESOURCE_STATE"),
("a vertex needs multiple resource states", "RESOURCE_STATE"),
("later arrival at the same vertex has better cost", "RELAX_IMPROVED"),
("the best path revisits a discovered vertex by a cheaper route", "RELAX_IMPROVED"),
("replace an existing worse label when a new shorter cost arrives", "RELAX_IMPROVED"),
]

# Separate frozen audit cases assembled with seeds never used in the proposal loop.
def random_cases(seed=202611, count=65):
    rng=Random(seed)
    result=[]
    for i in range(count):
        n=rng.randint(4,8); edges=[]
        for a in range(n):
            for b in range(n):
                if a!=b and rng.random() < .26:
                    edges.append((a,b,rng.randint(1,12),rng.randint(0,3)))
        if not edges:
            edges.append((0,n-1,6,1))
        budget=rng.randint(0,6)
        result.append(case(edges,budget,n,"unseen synthetic graph"))
    return result

AUDIT = random_cases(31337,60)
STRESS = random_cases(987654,55)
