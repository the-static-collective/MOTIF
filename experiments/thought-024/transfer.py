"""THOUGHT-024: source-owned grammar transfer evaluator and classical comparator.

The source-owned three-bit adapter and oracle define a *closed-world abstraction*.
No private project or real access/belief state is read, modified or inferred.
"""
from __future__ import annotations
import sys
from collections import Counter
from pathlib import Path
from copy import deepcopy
HERE=Path(__file__).resolve().parent
sib=str(HERE.parent/'thought-023')
if sib not in sys.path:sys.path.insert(0,sib)
from grammar import (enumerate_language, validate_expression, canonical, digest,
                     evaluate, GrammarError, COLORS)
from runtime import execute_source
from tasks import Task, oracle

SCHEMA='motif.thought024.transfer.v1'
DEV_PROBES=((0,0),(7,0),(0,7),(3,5),(2,1),(5,2))


def independent_specimen(task,a,b):
    """Evaluate human task spec using distinct integer arithmetic."""
    return oracle(task,a,b)


def expression_mask(expression,a,b,extension='universe_constant'):
    def as_set(v):return frozenset(c for i,c in enumerate(COLORS) if v & (1<<i))
    ans=evaluate(expression,as_set(a),as_set(b),extension)
    return sum(1<<i for i,c in enumerate(COLORS) if c in ans)


def task_gate(task):
    if not isinstance(task,Task):raise ValueError('known evaluator-owned task required')
    if not task.representable:return 'HOLD_NON_BOOLEAN_DOMAIN_MISMATCH'
    return None


def exhaustive(task,expression,extension):
    checked=validate_expression(expression,extension)
    outcomes=[]
    for a in range(8):
        for b in range(8):
            expected=oracle(task,a,b)
            actual=expression_mask(checked,a,b,extension)
            outcomes.append((a,b,expected,actual))
    return {'passed':sum(x[2]==x[3] for x in outcomes),'total':64,
            'first_counterexample':next(({'a':a,'b':b,'expected':e,'actual':g}
                for a,b,e,g in outcomes if e!=g),None)}


def choose_probe(candidates,seen):
    best=None; key=None
    for a in range(8):
        for b in range(8):
            if (a,b) in seen:continue
            counts=Counter(c['signature'][a*8+b] for c in candidates)
            information=len(candidates)**2-sum(n*n for n in counts.values())
            q=(information, len(counts), -a,-b)
            if key is None or q>key:key=q;best=(a,b)
    return best if key and key[0]>0 else next(((a,b) for a in range(8) for b in range(8) if (a,b) not in seen),None)


def classical_trial(task,extension='universe_constant',limit=6):
    bad=task_gate(task)
    if bad:
        return {'task':task.key,'extension':extension,'status':bad,'oracle_calls':0,
                'frozen_correct':None,'selected_expression':None,'witnesses':[]}
    if type(limit) is not int or not 1<=limit<=8:raise ValueError('invalid oracle call ceiling')
    entries=enumerate_language(extension)
    remain=list(entries);seen=set();witnesses=[]
    for _ in range(limit):
        if len(remain)<=1:break
        # Source-owned grammar coverage witness: never certify a unique candidate
        # without checking empty inputs, where old grammars cannot produce a nonempty set.
        probe=(0,0) if not seen else choose_probe(remain,seen)
        if probe is None:break
        a,b=probe;expected=oracle(task,a,b)
        remain=[x for x in remain if x['signature'][a*8+b]==expected]
        witnesses.append({'a':a,'b':b,'observed':expected,'source':'DEV_ORACLE_ONLY'})
        seen.add(probe)
        if not remain:break
    if len(remain)!=1:
        status='HOLD_GRAMMAR_INADEQUATE' if not remain else 'HOLD_AMBIGUOUS_WITHIN_BUDGET'
        return {'task':task.key,'extension':extension,'status':status,
                'oracle_calls':len(witnesses),'witnesses':witnesses,
                'remaining_candidates':len(remain),'selected_expression':None,'frozen_correct':None}
    winner=remain[0]
    # Frozen full-domain evaluation starts ONLY after selecting a single expression.
    e=exhaustive(task,winner['expression'],extension)
    accepted=e['passed']==64
    out={'task':task.key,'extension':extension,'status':
         'REVIEW_CANDIDATE_NOT_INSTALLED' if accepted else 'HOLD_FROZEN_COUNTEREXAMPLE',
         'oracle_calls':len(witnesses),'witnesses':witnesses,'remaining_candidates':len(remain),
         'selected_expression':winner['expression'],'frozen_correct':e['passed'],
         'frozen_first_counterexample':e['first_counterexample'],
         'installed':False,'external_authority':'NONE'}
    return out


def model_trial(task,proposer,*,max_calls=2):
    bad=task_gate(task)
    if bad:return {'task':task.key,'status':bad,'model_calls':0,'dev_oracle_calls':0,
                   'frozen_correct':None,'installed':False,'external_authority':'NONE'}
    if type(max_calls) is not int or not 1<=max_calls<=3:raise ValueError('model budget')
    feedback=[];attempts=[];winner=None;last_expr=None
    initial_calls=len(getattr(proposer,'calls',[]))
    for _ in range(max_calls):
        try:
            raw=proposer.propose(task.brief,tuple(deepcopy(feedback)))
            if type(raw) is not dict or set(raw)!={'expression','reason'}:raise ValueError('bad model fields')
            expr=validate_expression(raw['expression'],'universe_constant')
            if type(raw['reason']) is not str or not 8<=len(raw['reason'])<=200:
                raise ValueError('invalid model rationale')
        except Exception as error:
            attempts.append({'disposition':'HOLD_INVALID_MODEL_PROPOSAL',
                             'error':type(error).__name__})
            break
        last_expr=expr
        errors=[]
        for a,b in DEV_PROBES:
            predicted=expression_mask(expr,a,b)
            expected=oracle(task,a,b)
            if predicted!=expected:errors.append({'a':a,'b':b,'predicted':predicted,'observed':expected})
        attempts.append({'disposition':'PASS_DEV' if not errors else 'REFUTED_DEV',
                         'expression_digest':digest(expr),'dev_cases_passed':len(DEV_PROBES)-len(errors),
                         'dev_cases_total':len(DEV_PROBES), 'counterexample':errors[0] if errors else None})
        if not errors:
            winner=expr;break
        feedback.append(errors[0]) # Only DEV witness, not frozen labels.
    # Disposition is separate from number of HTTP model calls as a bad model response may have used inference.
    actual_calls=len(getattr(proposer,'calls',[]))-initial_calls
    if winner is None:
        return {'task':task.key,'status':'HOLD_NO_DEV_CONSISTENT_MODEL_PROPOSAL',
                'model_calls':actual_calls,'attempts':attempts,'dev_oracle_calls':
                len(DEV_PROBES)*sum('dev_cases_passed' in x for x in attempts),
                'frozen_correct':None,'selected_expression':None,
                'installed':False,'external_authority':'NONE'}
    frozen=exhaustive(task,winner,'universe_constant')
    if frozen['passed']!=64:status='HOLD_FROZEN_COUNTEREXAMPLE'
    else:status='CANDIDATE_FOR_REVIEW_NOT_INSTALLED'
    # Independent *executed* trusted-template code for successes only.
    executable=None
    if status=='CANDIDATE_FOR_REVIEW_NOT_INSTALLED':
        output=execute_source(winner,'universe_constant')
        executable=sum(output['results'][a*8+b]==oracle(task,a,b)
                       for a in range(8) for b in range(8))
        if executable!=64:status='HOLD_EXECUTABLE_AUDIT_FAILED'
    return {'task':task.key,'status':status,'model_calls':actual_calls,
            'attempts':attempts,'dev_oracle_calls':len(DEV_PROBES)*len(attempts),
            'frozen_correct':frozen['passed'],'first_counterexample':frozen['first_counterexample'],
            'selected_expression':winner,'executable_correct':executable,
            'model_written_python_executed':False,'installed':False,'external_authority':'NONE'}


def offline_report(tasks):
    results=[]
    for task in tasks:
        old=classical_trial(task,'none');fresh=classical_trial(task,'universe_constant')
        results.append({'task':task.key,'domain':task.domain,'representable':task.representable,
                       'old':old,'expanded':fresh})
    return {'schema':SCHEMA,'status':'OFFLINE_COMPARISON_ONLY',
            'results':results,'old_grammar_size':len(enumerate_language('none')),
            'expanded_grammar_size':len(enumerate_language('universe_constant')),
            'model_called':False,'general_world_model_transfer_demonstrated':False,
            'domain_adapter_is_predefined_by_developer':True,
            'models_receive_oracle_answers_only_during_dev':True,
            'installed':False,'external_authority':'NONE'}
