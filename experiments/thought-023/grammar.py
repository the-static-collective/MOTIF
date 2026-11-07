"""MOTIF-023: finite source-owned grammar laboratory; all LLM output is data.

No dynamic Python source from the model, code execution or automatic grammar
installation. Closed, independently checkable set algebra over three colors.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json, hashlib, sys

HERE = Path(__file__).resolve().parent
SIB = HERE.parent / 'thought-022'
if str(SIB) not in sys.path: sys.path.insert(0,str(SIB))
from synth import classical_cegis, independent_oracle

COLORS=('red','blue','green')
EXTENSIONS=('none','universe_constant','set_complement','empty_constant')
MODEL_NAMES={'constant_universe':'universe_constant','complement':'set_complement','unknown':'none'}
SCHEMA='motif.thought023.grammar-gardener.v1'

class GrammarError(ValueError): pass

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False,ensure_ascii=True)
def digest(x): return hashlib.sha256(canonical(x).encode()).hexdigest()

def ref(s): return {'ref':s}
def op(s,*args): return {'op':s,'args':list(args)}

def validate_expression(expr,extension='none',depth=0,counter=None):
    if extension not in EXTENSIONS:raise GrammarError('unsupported extension')
    if counter is None:counter=[0]
    counter[0]+=1
    if counter[0]>19 or depth>4 or type(expr) is not dict:raise GrammarError('bounded typed AST required')
    if set(expr)=={'ref'} and type(expr['ref']) is str:
        allowed={'state.on','arrival.toggles'}
        if extension=='universe_constant':allowed.add('universe')
        if extension=='empty_constant':allowed.add('empty')
        if expr['ref'] not in allowed:raise GrammarError('unlicensed reference')
    elif set(expr)=={'op','args'} and type(expr['op']) is str and type(expr['args']) is list:
        action=expr['op'];args=expr['args']
        if action in ('union','difference') and len(args)==2: pass
        elif action=='complement' and extension=='set_complement' and len(args)==1:pass
        else:raise GrammarError('unlicensed operation')
        for child in args:validate_expression(child,extension,depth+1,counter)
    else:raise GrammarError('unknown AST keys or shape')
    return deepcopy(expr)

def evaluate(expr, on, toggles, extension='none'):
    checked=validate_expression(expr,extension)
    if type(on) is not frozenset or type(toggles) is not frozenset or \
       not on <= set(COLORS) or not toggles <= set(COLORS):
        raise GrammarError('bounded frozen-set inputs required')
    def visit(node):
        if 'ref' in node:
            return {'state.on':on, 'arrival.toggles':toggles,
                    'universe':frozenset(COLORS),'empty':frozenset()}[node['ref']]
        values=[visit(x) for x in node['args']]
        if node['op']=='union':return values[0]|values[1]
        if node['op']=='difference':return values[0]-values[1]
        if node['op']=='complement':return frozenset(COLORS)-values[0]
        raise GrammarError('invalid compiled operation')
    return visit(checked)

def input_signatures():
    return {
      'state.on':tuple(a for a in range(8) for _ in range(8)),
      'arrival.toggles':tuple(b for _ in range(8) for b in range(8)),
      'universe':(7,)*64, 'empty':(0,)*64
    }

def _nodes(x):return 1 if 'ref' in x else 1+sum(_nodes(y) for y in x['args'])

def enumerate_language(extension='none',max_depth=4):
    """Exhaustive DISTINCT truth functions under the depth/19-node grammar.

    Signature composition uses integer bit operations. Later the executable
    candidate is checked with a separate set interpreter and task bitmask spec.
    """
    if extension not in EXTENSIONS or type(max_depth) is not int or not 1<=max_depth<=4:
        raise GrammarError('invalid finite enumeration')
    atom=input_signatures();nodes=['state.on','arrival.toggles']
    if extension=='universe_constant':nodes.append('universe')
    if extension=='empty_constant':nodes.append('empty')
    entries={atom[n]:{'expression':ref(n),'depth':0,'nodes':1,'signature':atom[n]} for n in nodes}
    for depth in range(1,max_depth+1):
        previous=list(entries.values())
        fresh=[]
        for x in previous:
            if x['depth']==depth-1 and extension=='set_complement':
                ex=op('complement',x['expression']);nn=x['nodes']+1
                if nn<=19:
                    sig=tuple((~v)&7 for v in x['signature'])
                    fresh.append((sig,ex,nn))
            for y in previous:
                if max(x['depth'],y['depth'])!=depth-1:continue
                nn=x['nodes']+y['nodes']+1
                if nn>19:continue
                for operation in ('union','difference'):
                    sig=tuple((a|b if operation=='union' else a&(~b&7)) for a,b in zip(x['signature'],y['signature']))
                    fresh.append((sig,op(operation,x['expression'],y['expression']),nn))
        for sig,ex,nn in fresh:
            if sig not in entries or (entries[sig]['depth']==depth and nn<entries[sig]['nodes']):
                entries[sig]={'expression':ex,'depth':depth,'nodes':nn,'signature':sig}
    return sorted(entries.values(),key=lambda x:(x['nodes'],canonical(x['expression'])))

def validate_advice(advice):
    if type(advice) is not dict or set(advice)!={'missing_primitive','reason'}:
        raise GrammarError('exact non-executable model advice required')
    term=advice['missing_primitive'];reason=advice['reason']
    if type(term) is not str or term not in MODEL_NAMES or type(reason) is not str or not 8<=len(reason)<=200 or any(ord(c)<32 for c in reason):
        raise GrammarError('unsupported model advice')
    return {'missing_primitive':term,'reason':reason,'extension':MODEL_NAMES[term]}

NEW_TASKS={
  'invert':lambda a,b:(~a)&7,
  'nand':lambda a,b:(~(a&b))&7,
  'nor':lambda a,b:(~(a|b))&7,
  'all_on':lambda a,b:7,
}

def target_signature(task):
    if task not in NEW_TASKS:raise GrammarError('unknown evaluator-owned task')
    return tuple(NEW_TASKS[task](a,b) for a in range(8) for b in range(8))

def expressive_coverage(catalog):
    # Uses the independent evaluator on FORWARD task-family specs, not model
    # prompts. For language-value audit only, never proposal selection.
    existing={x['signature'] for x in catalog}
    return {task:target_signature(task) in existing for task in NEW_TASKS}

def proof_report(extension):
    old=enumerate_language()
    fresh=enumerate_language(extension)
    old_sigs={x['signature'] for x in old}
    new_sigs={x['signature'] for x in fresh}
    if not old_sigs<=new_sigs:raise GrammarError('extension unexpectedly erased old semantics')
    # DEV stage: the old language fails on an observable 0,0 -> 7 witness.
    baseline=classical_cegis('invert',oracle_budget=4,catalog=old)
    candidate=classical_cegis('invert',oracle_budget=4,catalog=fresh)
    chosen=candidate['candidate_expression']
    executable=None
    if candidate['status']=='REVIEW_CANDIDATE_NOT_INSTALLED':
        # Verify resulting expression with independent set evaluation on the
        # WHOLE finite domain. The candidate was already frozen by CEGIS.
        independently=sum(sum(1<<i for i,c in enumerate(COLORS)
                              if c in evaluate(chosen,
                                frozenset(c for i,c in enumerate(COLORS) if a&(1<<i)),
                                frozenset(c for i,c in enumerate(COLORS) if b&(1<<i)),extension))==
                          independent_oracle('invert',a,b)
                          for a in range(8) for b in range(8))
        if independently!=64:raise GrammarError('independent set oracle disagrees')
        executable={'set_interpreter_passed':independently,'total':64}
    out={'schema':SCHEMA,'extension':extension,'baseline_grammar_functions':len(old_sigs),
         'expanded_grammar_functions':len(new_sigs),'new_distinct_functions':len(new_sigs-old_sigs),
         'old_functions_preserved':len(old_sigs & new_sigs),
         'original_invert_status':baseline['status'],'original_invert_oracle_calls':baseline['oracle_calls'],
         'new_invert_status':candidate['status'],'new_invert_oracle_calls':candidate['oracle_calls'],
         'new_invert_frozen_passed':candidate['frozen_full_domain_passed'],
         'new_invert_expression':chosen,
         'new_invert_expression_nodes':candidate['candidate_nodes'],
         'independent_set_verification':executable,
         'new_task_family_coverage_after_selection':expressive_coverage(fresh),
         'no_model_can_grade_itself':True,'model_authored_source_executed':False,
         'grammar_installed':False,'installed':False,'external_authority':'NONE'}
    out['receipt_digest']=digest(out)
    return out
