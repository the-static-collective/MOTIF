"""THOUGHT-026: staged, testable language grounding -> relationship -> mathematics.

Roles and relation independently inspectable and retained on failure. A source-owned
compiler constructs typed AST; proposals are never executable text. Model stages
have NO access to independently authored task policy, role ground truth or audit.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
p=str(HERE.parent/'thought-025')
if p not in sys.path:sys.path.insert(0,p)
from abstraction import (SCHEMA as CORE_SCHEMA, evaluate_reply, check_truth,
                         source_owned_program_check, digest)
from specimens import Specimen,public_brief,independent_target

SCHEMA='motif.thought026.staged-abstraction.v1'
RELATIONS=('DIFFERENCE','INTERSECTION','UNION','SECOND','COMPLEMENT','SYMMETRIC_DIFFERENCE')
DEV_CASES=((3,5),(5,3),(7,0),(0,7))

class StageError(ValueError):pass

def _short(value, minimum=8, maximum=240):
    if type(value) is not str or not minimum<=len(value)<=maximum or any(ord(c)<32 for c in value):
        raise StageError('bounded explanation required')
    return value

def check_binding(task, reply):
    if not isinstance(task,Specimen):raise StageError('known source-owner problem required')
    if type(reply) is not dict or set(reply)!={'bindings','rationale'}:raise StageError('binding envelope invalid')
    b=reply['bindings']; ids={x[0] for x in task.fields}
    if type(b) is not dict or set(b)!={'current','event'} or any(type(x) is not str for x in b.values()) or set(b.values())!=ids:
        raise StageError('invented, repeated or unknown field identifier')
    return {'bindings':deepcopy(b),'rationale':_short(reply['rationale'])}

def check_relation(reply):
    if type(reply) is not dict or set(reply)!={'relation','rationale'}:raise StageError('relationship envelope invalid')
    if type(reply['relation']) is not str or reply['relation'] not in RELATIONS:raise StageError('unlicensed relation')
    return {'relation':reply['relation'],'rationale':_short(reply['rationale'])}

def source_owned_expression(relation):
    if relation not in RELATIONS:raise StageError('unknown relation')
    a={'ref':'state.on'};b={'ref':'arrival.toggles'};u={'ref':'universe'}
    def op(name,*args):return {'op':name,'args':list(args)}
    return {'DIFFERENCE':lambda:op('difference',a,b),
            'INTERSECTION':lambda:op('intersection',a,b),
            'UNION':lambda:op('union',a,b),
            'SECOND':lambda:b,
            'COMPLEMENT':lambda:op('difference',u,a),
            'SYMMETRIC_DIFFERENCE':lambda:op('xor',a,b)}[relation]()

def assemble(task,binding,relation):
    checked=check_binding(task,binding);r=check_relation(relation)
    return {'schema':CORE_SCHEMA,'bindings':checked['bindings'],
            'expression':source_owned_expression(r['relation']),
            'rationale':'Source-owned compiler of two separately proposed typed stages'}

def dev_witnesses(task, proposal, specimens=DEV_CASES):
    if not task.representable:raise StageError('do not Boolean-coerce unsupported tasks')
    if type(specimens) not in (tuple,list) or len(specimens)>4:raise StageError('development budget exceeded')
    ids=[n for n,_ in task.fields]
    witnesses=[]
    for a,b in specimens:
        if type(a) is not int or type(b) is not int or not 0<=a<8 or not 0<=b<8:raise StageError('invalid development input')
        raw={ids[0]:a,ids[1]:b}; actual=independent_target(task,raw)
        prediction=evaluate_reply(task,proposal,raw)
        witnesses.append({'inputs':raw,'observed':actual,'predicted':prediction,
                          'passed':actual==prediction})
    return witnesses

def predicts(proposal,task,inputs):return evaluate_reply(task,proposal,inputs)

def locate_failure(task,binding,relation,witnesses):
    """Counterfactuals use ONLY already-observed DEV witnesses; no new oracle calls.

    Hypothesis classes, NOT the true model's role/operation, are returned. A
    commutative operation may make roles fundamentally unidentifiable.
    """
    b=check_binding(task,binding);r=check_relation(relation)
    swapped={'bindings':{'current':b['bindings']['event'],'event':b['bindings']['current']},'rationale':'Counterfactual role permutation'}
    survivors=[]
    for cb in (b,swapped):
        for rel in RELATIONS:
            trial=assemble(task,cb,{'relation':rel,'rationale':'Typed counterfactual relation'})
            if all(predicts(trial,task,w['inputs'])==w['observed'] for w in witnesses):
                survivors.append({'binding_swapped':cb is swapped,'relation_changed':rel!=r['relation']})
    observed_signature=lambda bind:tuple(predicts(assemble(task,bind,r),task,w['inputs']) for w in witnesses)
    roles_equivalent_on_dev=observed_signature(b)==observed_signature(swapped)
    return {'surviving_hypothesis_pairs':len(survivors),
            'role_only_possible':any(x['binding_swapped'] and not x['relation_changed'] for x in survivors),
            'relationship_only_possible':any(not x['binding_swapped'] and x['relation_changed'] for x in survivors),
            'joint_change_possible':any(x['binding_swapped'] and x['relation_changed'] for x in survivors),
            'roles_observationally_indistinguishable_on_dev':roles_equivalent_on_dev,
            'evidence':'ONLY_ALREADY_OBSERVED_DEV_SPECIMENS',
            'correct_relation_disclosed':False,'correct_role_binding_disclosed':False}

def stage_trial(task,model,*,repair=True):
    if not isinstance(task,Specimen):raise StageError('source-owned task required')
    if not task.representable:
        return {'task':task.key,'status':'HOLD_'+task.reason,'model_calls':0,
                'role_stage':None,'relation_stage':None,'dev_oracle_queries':0,
                'frozen':None,'installed':False,'gate_owner':'EVALUATOR_NOT_MODEL'}
    if not callable(getattr(model,'bind',None)) or not callable(getattr(model,'relate',None)):
        raise StageError('model must support explicit staged methods')
    before=len(getattr(model,'calls',[]));roles=relationship=proposal=None
    history=[];observations=[];reason=''
    try:
        roles=check_binding(task,model.bind(public_brief(task)))
        history.append({'stage':'GROUND_FIELDS','status':'TYPED_HYPOTHESIS_NOT_YET_VERIFIED',
                        'binding_digest':digest(roles)})
        relationship=check_relation(model.relate(public_brief(task),roles))
        history.append({'stage':'DISCOVER_RELATION','status':'TYPED_HYPOTHESIS_NOT_YET_VERIFIED',
                        'relation_name':relationship['relation']})
        proposal=assemble(task,roles,relationship)
        observations=dev_witnesses(task,proposal)
        incorrect=[w for w in observations if not w['passed']]
        history.append({'stage':'TEST_COMPOSED_MATH','status':'PASS_DEV' if not incorrect else 'REFUTED_DEV',
                        'dev_passed':len(observations)-len(incorrect),'dev_total':len(observations)})
        if incorrect and repair:
            diagnosis=locate_failure(task,roles,relationship,observations)
            history.append({'stage':'DIAGNOSE_PARTIAL_FAILURE','diagnosis':diagnosis})
            # One bounded model repair of roles AND relation, not a hardcoded correct answer.
            # No ground truth role label/policy, audit or alternative candidate leaves evaluator.
            revised=model.repair(public_brief(task),roles,relationship,
                                  tuple(deepcopy(observations)),deepcopy(diagnosis))
            if type(revised) is not dict or set(revised)!={'binding','relationship'}:
                raise StageError('invalid repair packet')
            new_roles=check_binding(task,revised['binding'])
            new_relation=check_relation(revised['relationship'])
            corrected=assemble(task,new_roles,new_relation)
            # No additional oracle calls; reuse 4 previously observed dev witnesses.
            check=[{**w,'predicted':predicts(corrected,task,w['inputs'])} for w in observations]
            check=[{**w,'passed':w['predicted']==w['observed']} for w in check]
            history.append({'stage':'RECOMPOSE_FROM_MODEL_REPAIR',
                 'status':'PASS_DEV' if all(w['passed'] for w in check) else 'REFUTED_DEV',
                 'role_changed':new_roles['bindings']!=roles['bindings'],
                 'relation_changed':new_relation['relation']!=relationship['relation']})
            roles=new_roles;relationship=new_relation;proposal=corrected
            observations=check
    except Exception as error:
        reason=type(error).__name__+': '+str(error)[:130]
        history.append({'stage':'MODEL_OR_VALIDATOR_FAILURE','error_type':type(error).__name__})
    pass_dev=bool(observations) and all(w['passed'] for w in observations) and not reason
    frozen=program=None
    if pass_dev:
        frozen=check_truth(task,proposal) # independent evaluator after selection
        if frozen['correct']==64:program=source_owned_program_check(task,proposal)
    status=('CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED' if
            pass_dev and frozen['correct']==64 and program and program['correct']==64 else
            'HOLD_STAGE_INVALID' if reason else
            'HOLD_FROZEN_COUNTEREXAMPLE' if pass_dev else 'HOLD_DEV_CONTRADICTION')
    out={'schema':SCHEMA,'task':task.key,'status':status,
         'role_stage':roles,'relation_stage':relationship,'stage_history':history,
         'development_witnesses':observations,'dev_oracle_queries':len(DEV_CASES) if observations else 0,
         'model_calls':len(getattr(model,'calls',[]))-before,
         'partial_understanding_preserved':roles is not None or relationship is not None,
         'model_constructed_source_code':False,'compiled_expression':proposal['expression'] if proposal else None,
         'frozen':frozen,'fixed_template_program':program,'failure':reason or None,
         'no_source_installed':True,'installed':False,'external_authority':'NONE'}
    out['receipt_digest']=digest(out)
    return out
