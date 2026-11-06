"""THOUGHT-017: strict, code-free typed macro proposal and safe fixed-template compiler.

The input grammar is new: 016 had union/subset/add/le but NO set difference,
no toggles, and no expression that can remove a held feature.
Model output is DATA, never imported Python or a command.
"""
from __future__ import annotations
import ast
import hashlib
import json
from copy import deepcopy

SCHEMA='motif.thought017.macro-proposal.v1'
OPS={'union','difference'}
REFS={'state.on','arrival.toggles'}

class ProposalError(ValueError): pass

def canonical(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=True,allow_nan=False,separators=(',',':'))

def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()

def r(name):return {'ref':name}
def op(name,a,b):return {'op':name,'args':[a,b]}

def validate_expr(node,depth=0,budget=None):
    if budget is None:budget=[0]
    budget[0]+=1
    if depth>4 or budget[0]>19 or type(node) is not dict:
        raise ProposalError('bounded typed expression required')
    if set(node)=={'ref'}:
        if type(node['ref']) is not str or node['ref'] not in REFS:raise ProposalError('unknown field reference')
    elif set(node)=={'op','args'}:
        if type(node['op']) is not str or node['op'] not in OPS or type(node['args']) is not list or len(node['args'])!=2:
            raise ProposalError('unsupported operation')
        for child in node['args']:validate_expr(child,depth+1,budget)
    else:raise ProposalError('unsupported expression shape')
    return deepcopy(node)

def validate_proposal(candidate):
    if type(candidate) is not dict or set(candidate)!={'schema','expression','purpose','proposer'}:
        raise ProposalError('exact proposal schema required')
    if candidate['schema']!=SCHEMA:raise ProposalError('unsupported proposal version')
    for field in ('purpose','proposer'):
        s=candidate[field]
        if type(s) is not str or not 4<=len(s)<=260 or any(ord(c)<32 for c in s):
            raise ProposalError('bounded description required')
    checked=deepcopy(candidate)
    checked['expression']=validate_expr(candidate['expression'])
    if len(canonical(checked))>4000:raise ProposalError('oversized proposal')
    return checked

def evaluate_macro(expression, on, toggles):
    """Small pure typed interpreter. Does not read filesystem, exec or network."""
    validate_expr(expression)
    if type(on) is not frozenset or type(toggles) is not frozenset:
        raise ProposalError('macro operands require frozen sets')
    def calc(node):
        if 'ref' in node:
            return {'state.on':on,'arrival.toggles':toggles}[node['ref']]
        a,b=map(calc,node['args'])
        return a|b if node['op']=='union' else a-b
    return calc(expression)

# AI-authored *proposal* supplied in this conversation, not claimed to be
# autonomously discovered by a background local LLM.
CHAT_MODEL_PROPOSAL={
    'schema':SCHEMA,
    'expression':op('union',
        op('difference',r('state.on'),r('arrival.toggles')),
        op('difference',r('arrival.toggles'),r('state.on'))),
    'purpose':'Build non-monotone toggle semantics from union and new set-difference primitive.',
    'proposer':'GPT-6 conversation-proposed candidate; offline evaluation, not autonomous Ollama'
}
MONOTONE_BASELINE={
    'schema':SCHEMA,
    'expression':op('union',r('state.on'),r('arrival.toggles')),
    'purpose':'Earlier monotone inventory approximation; deliberately misses off transitions.',
    'proposer':'baseline control'
}

# Only this source-owned fixed interpreter can run. The untrusted AST is
# serialized as a JSON *literal*, with no model-supplied Python/AST nodes.
TRUSTED_RUNTIME=r'''"""THOUGHT-017 fixed source-owned interpreter. REVIEW-ONLY."""
import heapq,json,sys
MACRO=json.loads(__MACRO_JSON__)
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
'''

def generate_source(proposal):
    checked=validate_proposal(proposal)
    literal=repr(canonical(checked['expression']))
    source=TRUSTED_RUNTIME.replace('__MACRO_JSON__',literal)
    parsed=ast.parse(source)
    if any(isinstance(x,(ast.ImportFrom,ast.Global,ast.Nonlocal,ast.AsyncFunctionDef)) for x in ast.walk(parsed)):
        raise ProposalError('fixed source template changed unexpectedly')
    imports={alias.name for node in ast.walk(parsed) if isinstance(node,ast.Import)
             for alias in node.names}
    if imports!={'heapq','json','sys'}:raise ProposalError('unapproved fixed runtime import')
    return '# REVIEW ONLY / MODEL PROPOSAL NEVER DIRECTLY EXECUTED\n'+source
