"""Non-blind, matched-physics-call screening study; not a field trial.

The deterministic baseline samples from a complete authored option list; this
is a deliberately strong catalogue, not a weaker next-neighbor oracle.
No results are independent evidence that any construction is safe.
"""
from __future__ import annotations
from dataclasses import replace
from itertools import combinations
import json,random
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'field016'))
import engine as f16
from search import Layout,run,_assessment


def world(i):
    scene=f16.invented_scene()
    if i==0:return scene
    if i==1:return replace(scene,wind_mps=4)
    if i==2:return replace(scene,wind_mps=14)
    if i==3:
        return replace(scene,pieces=tuple(replace(p,width_m=1.25,measured_width=True) if p.id=='porous' else p for p in scene.pieces),revision=1)
    if i==4:return replace(scene,piece_clearance_m={**scene.piece_clearance_m,'porous':0.11})
    if i==5:return replace(scene,routes=tuple(replace(r,retains_access=False) if r.id=='repositioned' else r for r in scene.routes))
    if i==6:return replace(scene,salvage_connections_available=False)
    if i==7:return replace(scene,pieces=tuple(replace(p,width_m=None) if p.id=='porous' else p for p in scene.pieces))
    if i==8:return replace(scene,routes=tuple(replace(r,span_m=1.3) if r.id=='repositioned' else r for r in scene.routes))
    if i==9:return replace(scene,pieces=tuple(replace(p,mass_kg=None) if p.id=='privacy' else p for p in scene.pieces))
    raise ValueError(i)


def options(scene):
    ids=[p.id for p in scene.pieces]
    return [Layout(r.id,t) for r in scene.routes for size in range(1,min(3,len(ids))+1)
            for t in combinations(ids,size) if size==1 or scene.salvage_connections_available]


def random_best(scene,seed,budget):
    candidates=options(scene)
    rng=random.Random(seed)
    rng.shuffle(candidates)
    sampled=candidates[:budget]
    return min((_assessment(scene,c) for c in sampled),key=lambda x:(x.score,x.layout.id))


def report():
    seed=Layout('original',('privacy',))
    budgets=(1,4,8,16)
    out=[]
    for b in budgets:
        W=T=L=0
        details=[]
        for i in range(10):
            scene=world(i)
            ours=run(scene,seed,budget=b)
            own_score=tuple(ours['selected']['score'])
            # 3 deterministic seeds per authored world; same full screen budget.
            for trial in range(3):
                baseline=random_best(scene,100*i+trial,b)
                other=baseline.score
                cmp='win' if own_score<other else 'tie' if own_score==other else 'loss'
                W+=cmp=='win';T+=cmp=='tie';L+=cmp=='loss'
                details.append({'world':i,'seed':trial,'comparison':cmp,'ours':list(own_score),'catalog_random':list(other)})
        out.append({'budget':b,'wins':W,'ties':T,'losses':L,'cases':len(details),'details':details})
    return {'status':'AUTHOR_DESIGNED_BENCHMARK_NOT_BLIND','baseline':'uniform random legal composition catalogue; same full candidate evaluations (individual members vary)',
            'search':'FIELD-017 bounded best-first accessible mutations','scenarios':10,'seeds_per_scenario':3,
            'results':out,'real_human_evaluations':0,'safety_approvals':0,
            'interpretation':'A result can fail to outperform a random full-catalogue sampler; compare all wins, losses and ties.'}

if __name__=='__main__':
    r=report()
    print(json.dumps({k:v if k!='results' else [{kk:vv for kk,vv in row.items() if kk!='details'} for row in v] for k,v in r.items()},indent=2))
