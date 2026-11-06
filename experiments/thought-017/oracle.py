"""Independent bitmask oracle for toggling switches. No imports from program.py.

Independent semantic implementation: Xor integer bitmask, not union/difference
AST, then Dijkstra over (position, risk, mask). Never trusts candidate costs.
"""
import heapq

COLORS=('red','blue','green')
class OracleError(ValueError):pass

def validate_problem(p):
    if type(p) is not dict or set(p)!={'n','start','goal','risk_budget','initial_on','toggles','edges'}:
        raise OracleError('unknown graph fields')
    n=p['n']
    if type(n) is not int or not 2<=n<=7:raise OracleError('n 2..7 required')
    if any(type(p[k]) is not int or not 0<=p[k]<n for k in ('start','goal')) or p['start']==p['goal']:
        raise OracleError('bad start or goal')
    budget=p['risk_budget']
    if type(budget) is not int or not 0<=budget<=6:raise OracleError('bad risk limit')
    if type(p['toggles']) is not dict or set(p['toggles'])!={str(i) for i in range(n)}:
        raise OracleError('all toggle cells required')
    for arr in [p['initial_on'],*p['toggles'].values()]:
        if type(arr) is not list or len(arr)!=len(set(arr)) or not set(arr)<=set(COLORS):
            raise OracleError('switch set invalid')
    edges=p['edges']
    if type(edges) is not list or len(edges)>20:raise OracleError('too many edges')
    seen=set()
    for e in edges:
        if type(e) is not dict or set(e)!={'u','v','cost','risk','need'}:
            raise OracleError('bad edge fields')
        for k in ('u','v','cost','risk'):
            if type(e[k]) is not int:raise OracleError('typed edge ints')
        if not (0<=e['u']<n and 0<=e['v']<n and e['u']!=e['v'] and
                1<=e['cost']<=12 and 0<=e['risk']<=4):
            raise OracleError('edge out of range')
        if type(e['need']) is not list or len(e['need'])!=len(set(e['need'])) or not set(e['need'])<=set(COLORS):
            raise OracleError('invalid gate needs')
        if (e['u'],e['v']) in seen:raise OracleError('duplicate directed edge')
        seen.add((e['u'],e['v']))
    return p

def mask(arr):return sum(1<<COLORS.index(v) for v in arr)

def optimum(p):
    validate_problem(p)
    rows=[[] for _ in range(p['n'])]
    for e in p['edges']: rows[e['u']].append(e)
    start=(p['start'],0,mask(p['initial_on']))
    best={start:0};prev={};serial=0
    heap=[(0,serial,start)];found=None
    switch=[mask(p['toggles'][str(i)]) for i in range(p['n'])]
    while heap:
        cost,_,st=heapq.heappop(heap)
        if cost!=best[st]:continue
        u,risk,on=st
        if u==p['goal']:
            found=st;break
        for e in rows[u]:
            need=mask(e['need'])
            if on & need != need:continue
            new_risk=risk+e['risk']
            if new_risk>p['risk_budget']:continue
            child=(e['v'],new_risk,on ^ switch[e['v']]);next_cost=cost+e['cost']
            if next_cost>=best.get(child,float('inf')):continue
            best[child]=next_cost;prev[child]=st;serial+=1
            heapq.heappush(heap,(next_cost,serial,child))
    if found is None:return None
    path=[found[0]];st=found
    while st in prev:
        st=prev[st];path.append(st[0])
    path.reverse()
    return {'cost':best[found],'path':path}

def verify_answer(p,answer):
    opt=optimum(p)
    if answer is None:return opt is None
    if type(answer) is not dict or set(answer)!={'cost','risk','path'}:return False
    path=answer['path']
    if type(path) is not list or len(path)>400 or len(path)<2 or path[0]!=p['start'] or path[-1]!=p['goal']:
        return False
    edgemap={(e['u'],e['v']):e for e in p['edges']}
    on=mask(p['initial_on']);total_cost=0;total_risk=0
    for u,v in zip(path,path[1:]):
        if type(u) is not int or type(v) is not int:return False
        e=edgemap.get((u,v))
        if e is None or (on & mask(e['need']))!=mask(e['need']):return False
        total_cost+=e['cost'];total_risk+=e['risk'];on ^=mask(p['toggles'][str(v)])
    return (type(answer['cost']) is int and type(answer['risk']) is int and
            answer['cost']==total_cost and answer['risk']==total_risk and
            total_risk<=p['risk_budget'] and opt is not None and total_cost==opt['cost'])
