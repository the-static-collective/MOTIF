"""LEGIT-029: preregistered research worlds, including engineer-made shifts.

Old LEGIT-028 environments are TRAINING only. New G(8,.5) graph worlds
and math worlds use disjoint fixed seeds. Complement graph worlds are
CORRELATED transformations, never independent experiments. The input
metadata are free task descriptors: they don't reveal any unasked answer.
No independent external blinded testing is claimed.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from random import Random
import sys
HERE=Path(__file__).resolve().parent
for name in ("legit021","legit022","legit023","legit025","legit026",
             "legit027","legit028"):
    sys.path.insert(0,str(HERE.parent/name))
import networkx as nx
import information_worlds as previous
import tasks as math_tasks
from research import _degree,_spectrum,_graph,complement,grammar,HOLD

DOMAINS=previous.DOMAINS
GRAPH_TRAIN=(29001,29002)
GRAPH_FUTURE=(29003,29004)
MATH_TRAIN=(29011,29012)
MATH_FUTURE=(29013,29014)
MATH_FUTURE_SHIFT=(29015,29016)
WORLD_SIZE_GRAPH=8
WORLD_SIZE_MATH=16
DRAW_COUNT=1000

def _graph_sample(seed):
    rng=Random(seed)
    buckets=defaultdict(list)
    old=grammar()
    for index in range(DRAW_COUNT):
        target=(8,tuple((i,j) for i in range(8) for j in range(i+1,8)
                        if rng.randrange(2)))
        buckets[(_degree(target),_spectrum(target,old))].append(
            (index,target))
    pairs=[]
    for cluster in buckets.values():
        match=None
        for i,first in enumerate(cluster):
            for other in cluster[i+1:]:
                if not nx.is_isomorphic(_graph(first[1]),_graph(other[1])):
                    match=((first[0],other[0]),(first[1],other[1]))
                    break
            if match is not None:break
        if match is not None:pairs.append(match)
    pairs.sort(key=lambda x:x[0])
    if len(pairs)<WORLD_SIZE_GRAPH:
        raise HOLD("not enough old-grammar graph blindspots")
    return tuple(pairs[:WORLD_SIZE_GRAPH]),len(pairs)

@lru_cache(maxsize=8)
def graph_world(seed,complements=False):
    if seed not in GRAPH_TRAIN+GRAPH_FUTURE:
        raise HOLD("unregistered graph seed")
    if complements and seed not in GRAPH_FUTURE:
        raise HOLD("complements are future dependent transfer only")
    pairs,available=_graph_sample(seed)
    old=grammar()
    result=[]
    for (i,j),targets in pairs:
        if complements:
            targets=tuple(complement(g) for g in targets)
        if _spectrum(targets[0],old)!=_spectrum(targets[1],old):
            raise HOLD("old grammar distinguishes selected graph")
        result.append({
            "id":("graph_complement_" if complements else "graph_")+
                 str(seed)+"_"+str(i)+"_"+str(j),
            "payload":targets})
    return tuple(result),{
        "seed":seed,"random_draws":DRAW_COUNT,
        "old_source_blindspot_clusters":available,
        "selected_graph_cases":len(result),
        "complement_derived_from_same_seeded_carriers":complements,
        "separately_sampled_graph_carriers":not complements,
        "selected_by_old_probe_observations_only":True,
        "engineer_authored_nonblind":True,
    }

def _constraint_row(rng,coef):
    a,b=rng.choice(coef),rng.choice(coef)
    if a==b==0:a=1
    values=sorted({a*x+b*y for x in range(6) for y in range(6)})
    if len(values)<3:raise HOLD("degenerate constraint generator")
    return (a,b,rng.choice(values[1:-1]))

def _make_math(domain,rng,regime):
    if domain=="polynomial_modular_witness":
        base=tuple(rng.randint(-4,4) for _ in range(4))
        root=rng.choice((-3,-2,-1,2,3))
        pools={
            "MIXED":(1,2,3,5,6,10,14,15,21,35,55,77),
            "SEEN_SHIFT":(6,10,14,21,35,55,70,77),
            "FAR_SHIFT":(30,42,54,60,66,70,75,77)}
        factor=rng.choice(pools[regime])
        delta=math_tasks._mul(math_tasks._mul(
            math_tasks._mul((0,1),(-1,1)),(-root,1)),(factor,))
        case={"objects":(base,tuple(a+b for a,b in zip(base,delta)))}
        math_tasks.valid_poly(case)
        return case
    if domain=="integer_constraint_countermodel":
        coef={
            "MIXED":(-2,-1,0,1,2),
            "SEEN_SHIFT":(-3,-2,0,2,3),
            "FAR_SHIFT":(-5,-4,-3,0,3,4,5)}[regime]
        a=_constraint_row(rng,coef)
        b=_constraint_row(rng,coef)
        adjusted=(a[0],a[1],a[2]+rng.choice((-1,1)))
        return {"objects":((a,b),(adjusted,b))}
    raise HOLD("unsupported math task")

@lru_cache(maxsize=32)
def math_world(domain,seed,regime):
    if domain not in DOMAINS[1:]:
        raise HOLD("unsupported math goal")
    allowed=((seed in MATH_TRAIN and regime=="SEEN_SHIFT") or
             (seed in MATH_FUTURE and regime=="MIXED") or
             (seed in MATH_FUTURE_SHIFT and regime=="FAR_SHIFT"))
    if not allowed:raise HOLD("unregistered math world regime or seed")
    rng=Random(seed+1_000_003*DOMAINS.index(domain))
    qs=previous.candidate_questions(domain)
    cases=[]
    attempted=0
    while len(cases)<WORLD_SIZE_MATH and attempted<50000:
        attempted+=1
        payload=_make_math(domain,rng,regime)
        item={"id":domain+"_"+regime+"_"+str(seed)+"_"+str(len(cases)),
              "payload":payload}
        if any(previous.is_witness(previous.observation(domain,item,q))
               for q in qs[:2]):
            continue
        if not math_tasks.oracle_nonidentical(domain,payload):
            continue
        if not any(previous.is_witness(previous.observation(domain,item,q))
                   for q in qs):
            continue
        cases.append(item)
    if len(cases)!=WORLD_SIZE_MATH:
        raise HOLD("not enough guaranteed math counterexamples")
    return tuple(cases),{
        "seed":seed,"regime":regime,"case_count":len(cases),
        "draw_attempts":attempted,
        "conditional_selection_on_old_query_failure":True,
        "candidate_witness_exists_checked_for_fixture_creation":True,
        "engineer_authored_nonblind":True}

@lru_cache(maxsize=1)
def training_worlds():
    old,origin=previous.training_worlds()
    cases={name:dict(old[name]) for name in DOMAINS}
    receipts={name:{"inherited_prior_training_only":origin[name]}
              for name in DOMAINS}
    for seed in GRAPH_TRAIN:
        key="additional_graph_train_"+str(seed)
        cases[DOMAINS[0]][key],receipts[DOMAINS[0]][key]=graph_world(seed)
    for domain in DOMAINS[1:]:
        for seed in MATH_TRAIN:
            key="additional_math_train_shift_"+str(seed)
            cases[domain][key],receipts[domain][key]=math_world(
                domain,seed,"SEEN_SHIFT")
    return cases,receipts

def future_worlds():
    """MUST NOT be called before all research-policy hashes are frozen."""
    cases={domain:{} for domain in DOMAINS}
    receipts={domain:{} for domain in DOMAINS}
    for seed in GRAPH_FUTURE:
        k="graph_future_"+str(seed)
        cases[DOMAINS[0]][k],receipts[DOMAINS[0]][k]=graph_world(seed)
        k="graph_dependent_complement_"+str(seed)
        cases[DOMAINS[0]][k],receipts[DOMAINS[0]][k]=graph_world(
            seed,True)
    for domain in DOMAINS[1:]:
        for seed in MATH_FUTURE:
            k="math_future_mixed_"+str(seed)
            cases[domain][k],receipts[domain][k]=math_world(
                domain,seed,"MIXED")
        for seed in MATH_FUTURE_SHIFT:
            k="math_future_far_shift_"+str(seed)
            cases[domain][k],receipts[domain][k]=math_world(
                domain,seed,"FAR_SHIFT")
    return cases,receipts

def metadata(domain,case):
    """Cost-free typed input shape; NEVER evaluates a candidate question."""
    if domain==DOMAINS[0]:
        a,b=case["payload"]
        if a[0]!=b[0]:raise HOLD("mismatched source vertex counts")
        n=a[0]
        return (float(n),
                (len(a[1])+len(b[1]))/(n*(n-1)),
                sum(_degree(a))/n, sum(_degree(b))/n)
    a,b=case["payload"]["objects"]
    if domain=="polynomial_modular_witness":
        difference=[abs(x-y) for x,y in zip(a,b)]
        return (float(max(difference)),float(sum(difference)),
                float(sum(x>0 for x in difference)),
                float(sum(x<0 for x in a)))
    if domain=="integer_constraint_countermodel":
        rows=list(a)+list(b)
        return (float(max(abs(v) for r in rows for v in r[:2])),
                sum(abs(v) for r in rows for v in r[:2])/len(rows),
                float(max(abs(r[2]) for r in rows)),
                float(sum(r[0]==0 or r[1]==0 for r in rows)))
    raise HOLD("unknown metadata domain")
