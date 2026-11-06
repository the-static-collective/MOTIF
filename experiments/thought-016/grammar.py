"""MOTIF THOUGHT-016 — bounded composition grammar, not Python written by a model.

A proposer chooses a typed expression tree and search policy. The compiler
renders a fixed reviewed interpreter template with canonical JSON program data.
No arbitrary model-authored source text, imports, tools or network endpoints.
"""
from __future__ import annotations
import ast
import hashlib
import json
from copy import deepcopy

SCHEMA = 'motif.thought016.typed-program.v1'
REFS = {'input.start','input.risk_budget','start.pickups','state.spent_risk',
        'state.held_keys','state.position','edge.v','edge.risk','edge.need','arrived.pickups'}
OPS = {'add':2, 'union':2, 'subset':2, 'le':2}
FIELD_NAMES = {'position','spent_risk','held_keys'}

class GrammarError(ValueError): pass

def ref(name): return {'ref':name}
def expr(op,a,b): return {'op':op,'args':[a,b]}
def lit(value): return {'lit':value}
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def digest(value): return hashlib.sha256(canonical(value).encode()).hexdigest()

def validate_expr(e,depth=0):
    if depth>5 or not isinstance(e,dict):raise GrammarError('expression depth/type invalid')
    if set(e)=={'ref'}:
        if not isinstance(e['ref'],str) or e['ref'] not in REFS:raise GrammarError('unknown field reference')
    elif set(e)=={'lit'}:
        v=e['lit']
        if type(v) is not int or not 0<=v<=12:raise GrammarError('bounded integer literal required')
    elif set(e)=={'op','args'}:
        if e['op'] not in OPS or not isinstance(e['args'],list) or len(e['args'])!=OPS[e['op']]:
            raise GrammarError('unrecognized typed expression operator')
        for sub in e['args']:validate_expr(sub,depth+1)
    else:raise GrammarError('expression contains unsupported keys')

def validate_program(p):
    if type(p) is not dict or set(p)!={'schema','initial','guards','effects','identity','frontier','relax','revisit'}:
        raise GrammarError('exact program schema required')
    if p['schema']!=SCHEMA: raise GrammarError('wrong version')
    for section,fields in (('initial',FIELD_NAMES),('effects',FIELD_NAMES)):
        values=p[section]
        if not isinstance(values,dict) or set(values)!=fields:raise GrammarError('state fields required')
        for node in values.values():validate_expr(node)
    if not isinstance(p['guards'],list) or len(p['guards'])>5:
        raise GrammarError('bounded guard list')
    for g in p['guards']:validate_expr(g)
    if not isinstance(p['identity'],list) or len(p['identity'])!=len(set(p['identity'])) or not set(p['identity']).issubset(FIELD_NAMES) or 'position' not in p['identity']:
        raise GrammarError('typed state identity required')
    if p['frontier'] not in ('fifo','cost') or type(p['relax']) is not bool or type(p['revisit']) is not bool:
        raise GrammarError('unknown search policy')
    if len(canonical(p))>6000:raise GrammarError('program too large')
    return deepcopy(p)

# General-purpose typed plan with no gate/key semantics; the old first-visit
# assumption is deliberately insufficient for collectible-key routing.
def baseline_program():
    return {'schema':SCHEMA,
      'initial':{'position':ref('input.start'),'spent_risk':lit(0),'held_keys':ref('start.pickups')},
      'guards':[expr('le',expr('add',ref('state.spent_risk'),ref('edge.risk')),ref('input.risk_budget'))],
      'effects':{'position':ref('edge.v'),'spent_risk':expr('add',ref('state.spent_risk'),ref('edge.risk')),
                 'held_keys':ref('state.held_keys')},
      'identity':['position','spent_risk'], 'frontier':'cost','relax':True,'revisit':False}

# Full composition is constructed via grammar-driven transformations, not a
# named four-operator repair token or model-supplied Python source.
def complete_program():
    p=baseline_program()
    p['guards'].append(expr('subset',ref('edge.need'),ref('state.held_keys')))
    p['effects']['held_keys']=expr('union',ref('state.held_keys'),ref('arrived.pickups'))
    p['identity'].append('held_keys')
    p['revisit']=True
    return validate_program(p)

# The only executable source material is this audited fixed template.
RUNTIME = r'''"""Generated THOUGHT-016 typed-plan executor. HOLD / human review only."""
import json
import sys
import heapq

PROGRAM = json.loads(__PROGRAM_JSON__)

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
'''

def compile_program(program):
    checked=validate_program(program)
    literal=repr(canonical(checked))
    source=RUNTIME.replace('__PROGRAM_JSON__',literal)
    tree=ast.parse(source)
    allowed={'json','sys','heapq'}
    for node in ast.walk(tree):
        if isinstance(node,(ast.ImportFrom,ast.Global,ast.Nonlocal,ast.Lambda,ast.AsyncFunctionDef)):
            raise GrammarError('unsafe trusted template changed')
        if isinstance(node,ast.Import) and any(alias.name not in allowed for alias in node.names):
            raise GrammarError('unsafe trusted imports')
    readable=json.dumps(checked,sort_keys=True,indent=2)
    commented="\n".join("# "+line for line in readable.splitlines())
    return "# AUDIT: TYPE-CHECKED COMPOSITION; COORDINATES/WORDS ARE NOT PROOF\n"+commented+"\n"+source
