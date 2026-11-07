"""025: language-to-typed-mathematics abstraction adapter and independent grading.

Model must select BOTH slot bindings and compositional set operations. Binding
is not predetermined by source adapters; only the evaluator owns answer specs.
No model-controlled code, field names, authority, or test outcomes are trusted.
"""
from __future__ import annotations
import sys,hashlib,json
from pathlib import Path
from copy import deepcopy
from collections import Counter
HERE=Path(__file__).resolve().parent
SIB=str(HERE.parent/'thought-023')
if SIB not in sys.path:sys.path.insert(0,SIB)
from grammar import enumerate_language,validate_expression,evaluate,COLORS,canonical
from runtime import execute_source
from specimens import Specimen,independent_target,public_brief

SCHEMA='motif.thought025.abstraction-proposal.v1'
DEV=((0,0),(7,0),(0,7),(3,5),(5,2),(2,3))

class AbstractionError(ValueError):pass

def digest(obj):return hashlib.sha256(canonical(obj).encode()).hexdigest()

def lower_surface_math(expression, depth=0, counter=None):
    """Source-reviewed compiler: familiar high-level set operations -> 023 core.

    Every accepted surface program becomes a checked, bounded union/difference
    AST; this does not give any model-produced code execution or new functions.
    """
    if counter is None:counter=[0]
    counter[0]+=1
    if depth>4 or counter[0]>19 or type(expression) is not dict:
        raise AbstractionError('out-of-bounds surface expression')
    if set(expression)=={'ref'}:
        if type(expression['ref']) is not str or expression['ref'] not in ('state.on','arrival.toggles','universe'):
            raise AbstractionError('unknown abstract role or constant')
        return deepcopy(expression)
    if set(expression)!={'op','args'} or type(expression['op']) is not str or type(expression['args']) is not list:
        raise AbstractionError('unknown surface node fields')
    operation=expression['op']
    binary={'union','difference','intersection','xor','symmetric_difference'}
    unary={'complement'}
    if (operation in binary and len(expression['args'])!=2) or (operation in unary and len(expression['args'])!=1) or operation not in binary|unary:
        raise AbstractionError('unsupported source-owned operator')
    args=[lower_surface_math(arg,depth+1,counter) for arg in expression['args']]
    def op(name,a,b):return {'op':name,'args':[a,b]}
    if operation in ('union','difference'):return op(operation,*args)
    if operation=='intersection':return op('difference',args[0],op('difference',args[0],args[1]))
    if operation in ('xor','symmetric_difference'):
        return op('union',op('difference',args[0],args[1]),op('difference',args[1],args[0]))
    if operation=='complement':return op('difference',{'ref':'universe'},args[0])
    raise AbstractionError('unrecognized surface expression')

def validate_proposal(task,reply):
    if not isinstance(task,Specimen):raise AbstractionError('typed task required')
    if type(reply) is not dict or set(reply)!={'schema','bindings','expression','rationale'} or reply['schema']!=SCHEMA:
        raise AbstractionError('unknown exact proposal envelope')
    ids={f for f,_ in task.fields}
    b=reply['bindings']
    if type(b) is not dict or set(b)!={'current','event'} or any(type(x) is not str for x in b.values()) or set(b.values())!=ids:
        raise AbstractionError('invalid field binding or invented referent')
    rationale=reply['rationale']
    if type(rationale) is not str or not 8<=len(rationale)<=250 or any(ord(c)<32 for c in rationale):
        raise AbstractionError('bounded rationale required')
    ex=validate_expression(lower_surface_math(reply['expression']),'universe_constant')
    return {'schema':SCHEMA,'bindings':deepcopy(b),'expression':ex,'rationale':rationale}

def as_set(v):return frozenset(c for i,c in enumerate(COLORS) if v&(1<<i))
def as_mask(values):return sum(1<<i for i,c in enumerate(COLORS) if c in values)

def evaluate_reply(task,proposal,raw):
    checked=validate_proposal(task,proposal)
    return as_mask(evaluate(checked['expression'],as_set(raw[checked['bindings']['current']]),as_set(raw[checked['bindings']['event']]),'universe_constant'))

def raw_cases(task):
    a,b=(x[0] for x in task.fields)
    for x in range(8):
        for y in range(8):yield {a:x,b:y}

def check_truth(task,proposal):
    checked=validate_proposal(task,proposal)
    cases=list(raw_cases(task));faults=[]
    for raw in cases:
        observed=independent_target(task,raw)
        proposed=evaluate_reply(task,checked,raw)
        if observed!=proposed:faults.append({'inputs':raw,'expected':observed,'actual':proposed})
    return {'correct':len(cases)-len(faults),'total':64,'first_counterexample':faults[0] if faults else None}

def source_owned_program_check(task,proposal):
    """Separate fixed-template Python agrees with evaluator for all input pairs.

    Existing trusted 023 compiler receives source grammar and role-mapped inputs.
    The model is never allowed to supply executable Python text.
    """
    checked=validate_proposal(task,proposal)
    packet=execute_source(checked['expression'],'universe_constant')
    got=packet['results']
    passed=0
    for raw in raw_cases(task):
        x=raw[checked['bindings']['current']]
        y=raw[checked['bindings']['event']]
        passed+=int(got[x*8+y]==independent_target(task,raw))
    return {'correct':passed,'total':64,'trusted_template':True,'model_written_python':False}

def model_trial(task,proposer,max_calls=2,dev=DEV):
    if type(max_calls) is not int or not 1<=max_calls<=3:raise AbstractionError('max model calls must be 1..3')
    if not isinstance(task,Specimen):raise AbstractionError('typed task required')
    # The evaluator owns these human-judgment gates; DO NOT report as model inference.
    if not task.representable:
        return {'task':task.key,'status':'HOLD_'+task.reason,'model_calls':0,'dev_oracle_calls':0,
                'model_declared_mapping':None,'frozen':None,'installed':False}
    feedback=[]; attempts=[];winner=None
    before=len(getattr(proposer,'calls',[]))
    for round_no in range(max_calls):
        try:
            raw=proposer.propose(public_brief(task),tuple(feedback))
            proposal=validate_proposal(task,raw)
        except Exception as exc:
            attempts.append({'round':round_no+1,'disposition':'HOLD_BAD_MODEL_OUTPUT',
                             'error_type':type(exc).__name__,'error_detail':str(exc)[:120]});break
        # Budget at most four oracle calls in all, not four per model proposal.
        # For a second proposal recheck previous observed constraints and 2 fresh cases.
        probes=(dev[:2] if round_no==0 else dev[:4])
        errors=[]; tested=[]
        for a,b in probes:
            raw_case={task.fields[0][0]:a,task.fields[1][0]:b}
            expected=independent_target(task,raw_case)
            predicted=evaluate_reply(task,proposal,raw_case)
            tested.append({'input':raw_case,'observed':expected,'proposed':predicted})
            if predicted!=expected:errors.append(tested[-1])
        # Cumulative first 2 probes are reused on next proposal; only 4 distinct oracle queries total.
        attempts.append({'round':round_no+1,'bindings':proposal['bindings'],
                         'expression_digest':digest(proposal['expression']),
                         'disposition':'PASS_DEV' if not errors else 'REFUTED_DEV',
                         'probes':tested,'first_counterexample':errors[0] if errors else None})
        if not errors:winner=proposal;break
        feedback.append({'inputs':errors[0]['input'],'observed':errors[0]['observed'],
                         'proposed':errors[0]['proposed']})
    model_calls=len(getattr(proposer,'calls',[]))-before
    distinct={canonical(item['input']) for item in sum([a.get('probes',[]) for a in attempts],[])}
    if winner is None:
        return {'task':task.key,'status':'HOLD_NO_DEV_CONSISTENT_MODEL_MAPPING',
                'model_calls':model_calls,'dev_oracle_calls':len(distinct),'attempts':attempts,
                'model_declared_mapping':None,'frozen':None,'installed':False}
    frozen=check_truth(task,winner)
    program=source_owned_program_check(task,winner) if frozen['correct']==64 else None
    status='CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED' if frozen['correct']==64 and program['correct']==64 else 'HOLD_FROZEN_COUNTEREXAMPLE'
    return {'task':task.key,'status':status,'model_calls':model_calls,'dev_oracle_calls':len(distinct),
            'attempts':attempts,'model_declared_mapping':winner,'frozen':frozen,'program':program,
            'source_written_by_model':False,'installed':False}

def classical_without_language(task,limit=4):
    """Strong nonlanguage baseline: exhaustive 16 functions × both role orders.

    Source-only baseline receives independent oracle examples, so it is NOT
    a no-data language understanding system or a matched overall-cost contest.
    """
    if not task.representable:return {'task':task.key,'status':'HOLD_'+task.reason,'dev_oracle_calls':0,'frozen_correct':None}
    ids=[f for f,_ in task.fields]
    catalog=enumerate_language('universe_constant'); candidates={}
    for permutation in ((ids[0],ids[1]),(ids[1],ids[0])):
        for entry in catalog:
            proposal={'schema':SCHEMA,'bindings':dict(zip(('current','event'),permutation)),
                     'expression':entry['expression'],'rationale':'Classical enumerator candidate'}
            signature=tuple(evaluate_reply(task,proposal,raw) for raw in raw_cases(task))
            if signature not in candidates:candidates[signature]=proposal
    alive=candidates.copy();witnesses=[];used=set()
    for _ in range(limit):
        if len(alive)<=1:break
        options=[]
        for a,b in ((0,0),(7,0),(0,7),(3,5),(5,2),(2,3)):
            if (a,b) in used:continue
            counts=Counter(sig[a*8+b] for sig in alive)
            score=len(alive)**2-sum(c*c for c in counts.values())
            options.append((score,-a,-b,a,b))
        if not options:break
        _,_,_,a,b=max(options)
        y=independent_target(task,{ids[0]:a,ids[1]:b})
        alive={sig:prop for sig,prop in alive.items() if sig[a*8+b]==y}
        used.add((a,b));witnesses.append({'a':a,'b':b,'observed':y})
    if len(alive)!=1:
        return {'task':task.key,'status':'HOLD_AMBIGUOUS_OR_MISSING_GRAMMAR','dev_oracle_calls':len(witnesses),
                'remaining':len(alive),'frozen_correct':None,'witnesses':witnesses}
    choice=next(iter(alive.values())); f=check_truth(task,choice)
    return {'task':task.key,'status':'REVIEW_CLASSICAL_CANDIDATE_NOT_INSTALLED' if f['correct']==64 else 'HOLD_FROZEN_ERROR',
            'dev_oracle_calls':len(witnesses),'remaining':len(alive),
            'frozen_correct':f['correct'],'chosen_roles':choice['bindings'],'witnesses':witnesses}
