# AUDIT: TYPE-CHECKED COMPOSITION; COORDINATES/WORDS ARE NOT PROOF
# {
#   "effects": {
#     "held_keys": {
#       "args": [
#         {
#           "ref": "state.held_keys"
#         },
#         {
#           "ref": "arrived.pickups"
#         }
#       ],
#       "op": "union"
#     },
#     "position": {
#       "ref": "edge.v"
#     },
#     "spent_risk": {
#       "args": [
#         {
#           "ref": "state.spent_risk"
#         },
#         {
#           "ref": "edge.risk"
#         }
#       ],
#       "op": "add"
#     }
#   },
#   "frontier": "cost",
#   "guards": [
#     {
#       "args": [
#         {
#           "args": [
#             {
#               "ref": "state.spent_risk"
#             },
#             {
#               "ref": "edge.risk"
#             }
#           ],
#           "op": "add"
#         },
#         {
#           "ref": "input.risk_budget"
#         }
#       ],
#       "op": "le"
#     },
#     {
#       "args": [
#         {
#           "ref": "edge.need"
#         },
#         {
#           "ref": "state.held_keys"
#         }
#       ],
#       "op": "subset"
#     }
#   ],
#   "identity": [
#     "position",
#     "spent_risk",
#     "held_keys"
#   ],
#   "initial": {
#     "held_keys": {
#       "ref": "start.pickups"
#     },
#     "position": {
#       "ref": "input.start"
#     },
#     "spent_risk": {
#       "lit": 0
#     }
#   },
#   "relax": true,
#   "revisit": true,
#   "schema": "motif.thought016.typed-program.v1"
# }
"""Generated THOUGHT-016 typed-plan executor. HOLD / human review only."""
import json
import sys
import heapq

PROGRAM = json.loads('{"effects":{"held_keys":{"args":[{"ref":"state.held_keys"},{"ref":"arrived.pickups"}],"op":"union"},"position":{"ref":"edge.v"},"spent_risk":{"args":[{"ref":"state.spent_risk"},{"ref":"edge.risk"}],"op":"add"}},"frontier":"cost","guards":[{"args":[{"args":[{"ref":"state.spent_risk"},{"ref":"edge.risk"}],"op":"add"},{"ref":"input.risk_budget"}],"op":"le"},{"args":[{"ref":"edge.need"},{"ref":"state.held_keys"}],"op":"subset"}],"identity":["position","spent_risk","held_keys"],"initial":{"held_keys":{"ref":"start.pickups"},"position":{"ref":"input.start"},"spent_risk":{"lit":0}},"relax":true,"revisit":true,"schema":"motif.thought016.typed-program.v1"}')

def ev(node, values):
    if 'ref' in node:
        return values[node['ref']]
    if 'lit' in node:
        return node['lit']
    a,b = (ev(x,values) for x in node['args'])
    if node['op']=='add':return a+b
    if node['op']=='union':return a|b
    if node['op']=='subset':return a<=b
    if node['op']=='le':return a<=b
    raise ValueError('unsupported plan expression')

def solve(p):
    graph=[[] for _ in range(p['n'])]
    for edge in p['edges']:
        graph[edge['u']].append(edge)
    def edge_key(x):return (x['v'],x['cost'],x['risk'])
    for g in graph:g.sort(key=edge_key)
    value={'input.start':p['start'],'input.risk_budget':p['risk_budget'],
           'start.pickups':frozenset(p['pickups'][str(p['start'])])}
    state={k:ev(v,value) for k,v in PROGRAM['initial'].items()}
    def signature(s):
        return tuple(tuple(sorted(s[k])) if isinstance(s[k],frozenset) else s[k]
                     for k in PROGRAM['identity'])
    best={signature(state):0}
    pending=[(0,0,0,state,(p['start'],))]
    serial=0
    while pending:
        _,_,cost,s,path=heapq.heappop(pending)
        sig=signature(s)
        if cost>best.get(sig,float('inf')):continue
        if s['position']==p['goal']:
            return {'cost':cost,'risk':s['spent_risk'],'path':list(path)}
        for edge in graph[s['position']]:
            if not PROGRAM['revisit'] and edge['v'] in path:continue
            context={'state.position':s['position'],'state.spent_risk':s['spent_risk'],
                     'state.held_keys':s['held_keys'],'edge.v':edge['v'],
                     'edge.risk':edge['risk'],'edge.need':frozenset(edge['need']),
                     'arrived.pickups':frozenset(p['pickups'][str(edge['v'])]),
                     'input.risk_budget':p['risk_budget']}
            if not all(ev(g,context) for g in PROGRAM['guards']):continue
            next_state={k:ev(v,context) for k,v in PROGRAM['effects'].items()}
            next_cost=cost+edge['cost'];key=signature(next_state)
            if PROGRAM['relax']:
                if next_cost>=best.get(key,float('inf')):continue
            elif key in best:continue
            best[key]=next_cost
            serial+=1
            priority=next_cost if PROGRAM['frontier']=='cost' else serial
            heapq.heappush(pending,(priority,serial,next_cost,next_state,path+(edge['v'],)))
    return None

if __name__=='__main__':
    data=json.load(sys.stdin)
    print(json.dumps([solve(x) for x in data],sort_keys=True,separators=(',',':')))
