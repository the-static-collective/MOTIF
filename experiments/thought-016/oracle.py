"""Independent finite-state label-correcting oracle for held key-gate paths.

Does NOT call the candidate's generated Python or DSL interpreter. Unlike
priority-queue search it performs repeated relaxations to fixed point.
"""
from __future__ import annotations
from collections import deque

class OracleError(ValueError):pass

def validate(p):
    if not isinstance(p,dict) or set(p)!={'n','start','goal','risk_budget','edges','pickups'}:
        raise OracleError('wrong graph schema')
    n=p['n']
    if type(n) is not int or not 2<=n<=7:raise OracleError('2..7 vertices')
    for k in ('start','goal'):
        if type(p[k]) is not int or not 0<=p[k]<n:raise OracleError('invalid node')
    if p['start']==p['goal']:raise OracleError('start differs from goal')
    if type(p['risk_budget']) is not int or not 0<=p['risk_budget']<=6:
        raise OracleError('invalid risk budget')
    pickups=p['pickups']
    if not isinstance(pickups,dict) or set(pickups)!={str(i) for i in range(n)}:
        raise OracleError('all node pickup entries required')
    universe={'red','blue','green'}
    for x in pickups.values():
        if not isinstance(x,list) or len(x)!=len(set(x)) or not set(x)<=universe:
            raise OracleError('bad pickups')
    edges=p['edges']
    if not isinstance(edges,list) or len(edges)>20:raise OracleError('too many edges')
    seen=set()
    for e in edges:
        if not isinstance(e,dict) or set(e)!={'u','v','cost','risk','need'}:
            raise OracleError('edge schema')
        if (any(type(e[k]) is not int for k in ('u','v','cost','risk')) or
            not (0<=e['u']<n and 0<=e['v']<n and e['u']!=e['v'] and 1<=e['cost']<=12 and 0<=e['risk']<=4)):
            raise OracleError('bad edge')
        if not isinstance(e['need'],list) or len(e['need'])!=len(set(e['need'])) or not set(e['need'])<=universe:
            raise OracleError('bad edge need')
        key=(e['u'],e['v'])
        if key in seen:raise OracleError('duplicate directed edge')
        seen.add(key)
    return p

def independent_optimum(p):
    validate(p)
    adjacency={i:[] for i in range(p['n'])}
    for e in p['edges']:adjacency[e['u']].append(e)
    start=(p['start'],0,frozenset(p['pickups'][str(p['start'])]))
    labels={start:0}
    predecessor={}
    queue=deque([start]);inq={start};relaxations=0
    while queue:
        state=queue.popleft();inq.discard(state)
        node,risk,keys=state
        for edge in adjacency[node]:
            if not set(edge['need'])<=keys:continue
            newrisk=risk+edge['risk']
            if newrisk>p['risk_budget']:continue
            newkeys=keys|set(p['pickups'][str(edge['v'])])
            child=(edge['v'],newrisk,frozenset(newkeys))
            cost=labels[state]+edge['cost']
            if cost<labels.get(child,float('inf')):
                labels[child]=cost;predecessor[child]=state
                if child not in inq:queue.append(child);inq.add(child)
                relaxations+=1
                if relaxations>200000:raise OracleError('bounded independent oracle exhausted')
    goals=[(cost,s) for s,cost in labels.items() if s[0]==p['goal']]
    if not goals:return None
    cost,state=min(goals,key=lambda x:(x[0],x[1][1],tuple(sorted(x[1][2]))))
    path=[state[0]]
    while state in predecessor:
        state=predecessor[state];path.append(state[0])
    path.reverse()
    return {'cost':cost,'path':path}

def validate_answer(p,answer):
    optimal=independent_optimum(p)
    if answer is None:return optimal is None
    if not isinstance(answer,dict) or set(answer)!={'cost','risk','path'}:
        return False
    path=answer['path']
    if (not isinstance(path,list) or not path or len(path)>p['n']*30 or
        any(type(v) is not int for v in path) or path[0]!=p['start'] or path[-1]!=p['goal']):
        return False
    lookup={(e['u'],e['v']):e for e in p['edges']}
    held=set(p['pickups'][str(p['start'])]);cost=risk=0
    for a,b in zip(path,path[1:]):
        edge=lookup.get((a,b))
        if not edge or not set(edge['need'])<=held:return False
        cost+=edge['cost'];risk+=edge['risk']
        held.update(p['pickups'][str(b)])
    return (type(answer['cost']) is int and answer['cost']==cost and
            type(answer['risk']) is int and answer['risk']==risk and
            risk<=p['risk_budget'] and optimal is not None and cost==optimal['cost'])
