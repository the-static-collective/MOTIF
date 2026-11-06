# REVIEW ONLY / MODEL PROPOSAL NEVER DIRECTLY EXECUTED
"""THOUGHT-017 fixed source-owned interpreter. REVIEW-ONLY."""
import heapq,json,sys
MACRO=json.loads('{"args":[{"args":[{"ref":"state.on"},{"ref":"arrival.toggles"}],"op":"difference"},{"args":[{"ref":"arrival.toggles"},{"ref":"state.on"}],"op":"difference"}],"op":"union"}')
def apply(on,toggle):
    fields={'state.on':on,'arrival.toggles':toggle}
    def calc(x):
        if 'ref' in x:return fields[x['ref']]
        a,b=(calc(v) for v in x['args'])
        if x['op']=='union':return a|b
        if x['op']=='difference':return a-b
        raise ValueError('not a typed operation')
    return calc(MACRO)
def solve(p):
    adjacency=[[] for _ in range(p['n'])]
    for e in p['edges']:adjacency[e['u']].append(e)
    for row in adjacency:row.sort(key=lambda e:(e['v'],e['cost'],e['risk']))
    start=(p['start'],0,frozenset(p['initial_on']))
    pending=[(0,0,start,(p['start'],))]
    best={start:0};serial=0
    while pending:
        cost,_,(node,risk,on),path=heapq.heappop(pending)
        if cost>best.get((node,risk,on),float('inf')):continue
        if node==p['goal']:return {'cost':cost,'risk':risk,'path':list(path)}
        for e in adjacency[node]:
            if not frozenset(e['need'])<=on:continue
            nxt_risk=risk+e['risk']
            if nxt_risk>p['risk_budget']:continue
            nxt_on=apply(on,frozenset(p['toggles'][str(e['v'])]))
            nxt=(e['v'],nxt_risk,nxt_on);nxt_cost=cost+e['cost']
            if nxt_cost>=best.get(nxt,float('inf')):continue
            best[nxt]=nxt_cost;serial+=1
            heapq.heappush(pending,(nxt_cost,serial,nxt,path+(e['v'],)))
    return None
if __name__=='__main__':
    data=json.load(sys.stdin)
    print(json.dumps([solve(x) for x in data],sort_keys=True,separators=(',',':')))
