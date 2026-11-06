"""LEGIT-018 registered two-episode composite-constraint challenges.

The distribution and *both* problem classes are researcher-authored:
  EXACT: exists path with exactly K total edge weight?
  FORBIDDEN: exists such a path excluding a specified node?
They are different from LEGIT-017's elementary reachability/subset-sum
queries, but neither is an independently authored external challenge.

DAG vertices are topologically numbered, edges carry positive weights;
finite semantics and an independently written path-enumeration oracle.
"""
from __future__ import annotations
from dataclasses import dataclass
from random import Random
from itertools import product

FAMILIES=("EXACT","FORBIDDEN")
N=9
TRAIN_SEEDS={"EXACT":43000,"FORBIDDEN":53000}
TEST_SEEDS={"EXACT":44000,"FORBIDDEN":54000}

@dataclass(frozen=True)
class Challenge:
    family: str
    name: str
    edges: tuple
    queries: tuple
    n: int=N

def generate(family,seed,queries=36,n=N):
    if family not in FAMILIES or type(seed) is not int or not 3<=n<=N:
        raise ValueError("Unregistered challenge")
    rng=Random(seed)
    edges={}
    # Chain is present, but its weight is unknown to the solver.
    for u in range(n-1):
        edges[u,u+1]=rng.randrange(1,5)
    for u in range(n):
        for v in range(u+2,n):
            if rng.randrange(10)<4:
                edges[u,v]=rng.randrange(1,7)
    e=tuple(sorted((u,v,w) for (u,v),w in edges.items()))
    q=[]
    for i in range(queries):
        s=rng.randrange(n)
        t=rng.randrange(s,n)
        budget=rng.randrange(0,5*n+1)
        banned=(-1 if family=="EXACT" else
                (rng.randrange(n) if i%3 else -1))
        q.append((s,t,budget,banned))
    return Challenge(family,f"{family}_{seed}",e,tuple(q),n)

def suite(phase,family):
    if phase not in ("TRAIN","HELDOUT") or family not in FAMILIES:
        raise ValueError("Unknown challenge cohort")
    seed=(TRAIN_SEEDS if phase=="TRAIN" else TEST_SEEDS)[family]
    count=8 if phase=="TRAIN" else 12
    return tuple(generate(family,seed+i,36 if phase=="TRAIN" else 48)
                 for i in range(count))

def check(tasks):
    if not isinstance(tasks,(tuple,list)) or not tasks:
        raise ValueError("Missing challenge corpus")
    seen=set()
    for t in tasks:
        if (not isinstance(t,Challenge) or t.family not in FAMILIES
            or t.name in seen or not 3<=t.n<=N or not t.queries):
            raise ValueError("Bad or duplicate problem")
        seen.add(t.name)
        if any(type(u) is not int or type(v) is not int or type(w) is not int
               or not 0<=u<v<t.n or not 1<=w<=6
               for u,v,w in t.edges):
            raise ValueError("Unbounded or cyclic source graph")
        if any(not isinstance(q,tuple) or len(q)!=4 or
               any(type(x) is not int for x in q) or
               not 0<=q[0]<=q[1]<t.n or not 0<=q[2]<=5*N or
               not -1<=q[3]<t.n or (t.family=="EXACT" and q[3]!=-1)
               for q in t.queries):
            raise ValueError("Unknown typed query")
    return len(seen)

def reference(t,q):
    """Exhaustive DFS: no shared graph closure or bitset implementation."""
    s,dest,budget,banned=q
    if s==banned or dest==banned:
        return False
    following={i:[] for i in range(t.n)}
    for u,v,w in t.edges:
        if u!=banned and v!=banned:
            following[u].append((v,w))
    def enumerate_paths(node,consumed):
        if consumed>budget:return False
        if node==dest:return consumed==budget
        for nxt,weight in following[node]:
            if nxt<=dest and enumerate_paths(nxt,consumed+weight):
                return True
        return False
    return enumerate_paths(s,0)

def classical_index(t):
    """Independently implemented optimized classical DAG bitset DP.

    Every prohibited-node/source pair gets a cost-mask for every target.
    Source-to-target exact distance queries are O(1) bit tests after
    preprocessing. Deliberately *strong*: not a strawman slow enumerator.
    """
    outgoing=[[] for _ in range(t.n)]
    for u,v,w in t.edges:outgoing[u].append((v,w))
    tables={}
    # A strong conventional baseline computes ONLY the actual query
    # (excluded-node, source) pairs. It should not be penalized by
    # indexing forbidden cases never asked by the experiment.
    needed=sorted({(q[3],q[0]) for q in t.queries})
    for banned,source in needed:
            possibilities=[0]*t.n
            if source!=banned:
                possibilities[source]=1
            for vertex in range(source,t.n):
                if vertex==banned:continue
                reach=possibilities[vertex]
                for v,w in outgoing[vertex]:
                    if v!=banned:
                        possibilities[v]|=reach<<w
            tables[banned,source]=tuple(possibilities)
    return tables

def classical_answer(index,q):
    source,target,cost,banned=q
    return bool((index[banned,source][target]>>cost)&1)

def finite_cases():
    """All 3-node DAGs with each forward edge absent or weight 1/2.

    3**3=27 graphs; 3*3 target pairs × costs 0..6 × forbidden
    values (-1,0,1,2). Filter source<=target. No generator seeds.
    """
    possible=((0,1),(0,2),(1,2))
    for k,choice in enumerate(product((0,1,2),repeat=3)):
        edges=tuple((u,v,w) for (u,v),w in zip(possible,choice) if w)
        questions=tuple((s,t,c,b)
                        for s in range(3) for t in range(s,3)
                        for c in range(7) for b in (-1,0,1,2))
        yield Challenge("FORBIDDEN",f"EXHAUSTIVE_{k}",edges,questions,3)
