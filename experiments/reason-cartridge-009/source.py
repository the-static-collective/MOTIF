"""Independent source: two nonisomorphic directed graph families, classical BFS.

This module owns both observations and a bounded counterexample oracle.
The grammar inventor does not import this file or inspect its implementation.
Source labels on HOLDOUT are NEVER exposed to learner/challenger.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
import hashlib
import json

SOURCE_REVISION="motif.reason.grammar-009.source.v1"
INITIAL=(3,5,6,7,24)
HOLDOUT=(0,1,2,4,8,16,30,31)
ACQUISITION=tuple(m for m in range(32) if m not in HOLDOUT)
FAMILIES=("LONG_SHORT","BRIDGE")
VARIANTS=("cedar","quartz","willow")


@dataclass(frozen=True)
class Case:
    mask: int
    family: str
    variant: str="cedar"

    def __post_init__(self):
        if (type(self.mask) is not int or not 0<=self.mask<32
                or self.family not in FAMILIES or self.variant not in VARIANTS):
            raise ValueError("Unsupported source-owned five-edge world")

    def graph(self):
        names={
            "cedar":("S","A","B","C","T"),
            "quartz":("Q","J","K","L","R"),
            "willow":("W","P","X","Y","Z"),
        }[self.variant]
        s,a,b,c,t=names
        edges=(
            ((s,a),(a,b),(b,t),(s,c),(c,t))
            if self.family=="LONG_SHORT"
            else ((s,a),(a,t),(s,b),(b,t),(a,b))
        )
        return names,tuple(edge for i,edge in enumerate(edges)
                           if self.mask & (1<<i))


def bfs(case):
    if not isinstance(case,Case):
        raise ValueError("Only explicitly declared source worlds")
    nodes,edges=case.graph()
    adj={n:[] for n in nodes}
    for a,b in edges:
        adj[a].append(b)
    queue=deque([nodes[0]])
    visited={nodes[0]}
    while queue:
        u=queue.popleft()
        if u==nodes[-1]:return True
        for v in sorted(adj[u]):
            if v not in visited:
                visited.add(v)
                queue.append(v)
    return False


def witness(family,mask):
    if family not in FAMILIES or type(mask) is not int or mask not in ACQUISITION:
        raise ValueError("Protected holdout or unauthorized source-world probe")
    return {"schema":"motif.reason.grammar-009.observation.v1",
            "source_revision":SOURCE_REVISION,
            "family":family,"mask":mask,
            "reachable":bfs(Case(mask,family)),
            "kind":"SYNTHETIC_CLASSICAL_BFS",
            "real_world_authority":False}


def lessons(family):
    return tuple(witness(family,m) for m in INITIAL)


class SourceOwner:
    """Bounded counterexample service. Only acquisition values may be returned."""
    def __init__(self,family,max_queries=24):
        if family not in FAMILIES or type(max_queries) is not int or not 0<=max_queries<=24:
            raise ValueError("Unknown family or inquiry budget")
        self.family=family
        self.max_queries=max_queries
        self.calls=0
        self.issued=set(INITIAL)
        self.history=[]

    def _gate(self):
        if self.calls >= self.max_queries:
            raise ValueError("Counterexample budget exhausted")
        self.calls+=1

    def query(self,mask):
        if mask not in ACQUISITION or mask in self.issued:
            raise ValueError("Repeat or protected holdout source query")
        self._gate()
        self.issued.add(mask)
        row=witness(self.family,mask)
        self.history.append({"mechanism":"DISAGREEMENT","mask":mask,
                             "witness":row,"source_world_only":True})
        return row

    def refute_or_pass(self,truth_signature):
        if type(truth_signature) is not int or not 0<=truth_signature<(1<<32):
            raise ValueError("Unrecognized purely Boolean candidate program")
        self._gate()
        for mask in ACQUISITION:
            if mask in self.issued:
                continue
            prediction=bool(truth_signature & (1<<mask))
            actual=bfs(Case(mask,self.family))
            if prediction!=actual:
                self.issued.add(mask)
                row=witness(self.family,mask)
                self.history.append({"mechanism":"COUNTEREXAMPLE","mask":mask,
                                     "witness":row,"source_world_only":True})
                return {"status":"COUNTEREXAMPLE","observation":row}
        self.history.append({"mechanism":"ACQUISITION_PASS",
                             "source_world_only":True,
                             "does_not_certify_heldout":True})
        return {"status":"PASS_ACQUISITION","does_not_certify_heldout":True}


def heldout(family):
    if family not in FAMILIES:
        raise ValueError("Unrecognized owner")
    return tuple(Case(mask,family) for mask in HOLDOUT)


def future(family,n):
    if family not in FAMILIES or type(n) is not int or not 1<=n<=64:
        raise ValueError("Unsupported future workload")
    return tuple(Case(i%32,family,"quartz" if i<32 else "willow")
                 for i in range(n))
