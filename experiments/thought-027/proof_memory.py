"""THOUGHT-027: evidence-scoped, proof-carrying memory for MOTIF abstractions.

A VERIFIED_COMPOSITE means a source-owner finite oracle and fixed-template runtime
agreed for ONE task's 3-bit world. It is not verified general language meaning.
Individual role/relation stage claims are promoted ONLY if all oracle-consistent
models agree, and role ambiguity under commutative operations is retained.
"""
from __future__ import annotations
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

HERE=Path(__file__).resolve().parent
for family in ('thought-025','thought-026'):
    path=str(HERE.parent/family)
    if path not in sys.path:sys.path.insert(0,path)
from specimens import Specimen, public_brief, independent_target
from stages import (RELATIONS, check_binding, check_relation, assemble, stage_trial)
from abstraction import (check_truth, source_owned_program_check, evaluate_reply,
                         validate_proposal, raw_cases)

SCHEMA='motif.thought027.proof-carrying-fragment.v1'

class ProofError(ValueError):pass

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)

def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()

def _pair(task,bindings,relation):
    b={'bindings':bindings,'rationale':'Source-owned candidate binding'}
    r={'relation':relation,'rationale':'Source-owned candidate relationship'}
    return assemble(task,b,r)

def _signature(task,proposal):
    return tuple(evaluate_reply(task,proposal,c) for c in raw_cases(task))

def _target(task):
    return tuple(independent_target(task,c) for c in raw_cases(task))

def identifiable_stages(task):
    """Marginalize all 12 source-grammar hypotheses against independent oracle.

    This is an offline evaluation after success, NOT a new model prompt. If
    multiple pairs satisfy the task, individual semantics are underdetermined.
    """
    if not isinstance(task,Specimen) or not task.representable:
        raise ProofError('Boolean source-owner task only')
    target=_target(task)
    ids=[x[0] for x in task.fields]
    consistent=[]
    for x,y in ((ids[0],ids[1]),(ids[1],ids[0])):
        for rel in RELATIONS:
            p=_pair(task,{'current':x,'event':y},rel)
            if _signature(task,p)==target:
                consistent.append({'current':x,'event':y,'relation':rel})
    return {'compatible_pair_count':len(consistent),
            'binding_status':'SUPPORTED_ON_FINITE_WORLD' if len({(v['current'],v['event']) for v in consistent})==1 else 'UNDERDETERMINED',
            'relation_status':'SUPPORTED_ON_FINITE_WORLD' if len({v['relation'] for v in consistent})==1 else 'UNDERDETERMINED',
            'consistent_bindings':[list(x) for x in sorted({(v['current'],v['event']) for v in consistent})],
            'consistent_relations':sorted({v['relation'] for v in consistent}),
            'evidence':'SOURCE_OWNER_64_CASE_INDEPENDENT_INTEGER_ORACLE',
            'language_meaning_independently_verified':False}

def certify(task,trial,*,origin='UNVERIFIED_PROPOSAL_ORIGIN'):
    """Re-verify, do not trust an incoming report's claims of correctness.

    Origin is a declared label, not authentication. A caller with an arbitrary
    report cannot certify an incorrect program by editing fields or status.
    """
    if not isinstance(task,Specimen) or not task.representable:raise ProofError('task outside Boolean scope')
    if type(trial) is not dict or trial.get('task')!=task.key:
        raise ProofError('trial/task mismatch')
    if trial.get('status')!='CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED':
        raise ProofError('only independently passed composites can enter verified memory')
    if trial.get('installed') is not False:raise ProofError('installed or unclear source rejected')
    if type(origin) is not str or not 5<=len(origin)<=100:raise ProofError('invalid origin metadata')
    roles=check_binding(task,trial['role_stage'])
    relation=check_relation(trial['relation_stage'])
    candidate=assemble(task,roles,relation)
    actual=check_truth(task,candidate)
    if actual['correct']!=64 or actual['total']!=64:
        raise ProofError('independent full-domain proof failed')
    program=source_owned_program_check(task,candidate)
    if program['correct']!=64 or program['total']!=64:
        raise ProofError('trusted fixed interpreter disagreed')
    if (trial.get('frozen')!=actual or trial.get('fixed_template_program')!=program):
        raise ProofError('incoming evidence differs from independently recomputed evidence')
    ident=identifiable_stages(task)
    if ident['compatible_pair_count']==0:raise ProofError('no compatible staged hypothesis')
    if relation['relation'] not in ident['consistent_relations']:
        raise ProofError('stage relation not compatible with task')
    card={'schema':SCHEMA,'task_key':task.key,
          'task_spec_sha256':digest(public_brief(task)),
          'origin_label_unverified':origin,
          'source_owner_semantic_scope':'AUTHOR_DESIGNED_CLOSED_WORLD_THREE_BIT_SETS',
          'source_owner_not_real_world_verification':True,
          'roles':roles['bindings'],'relation':relation['relation'],
          'typed_expression':candidate['expression'],
          'function_sha256':digest(_signature(task,candidate)),
          'oracle_function_sha256':digest(_target(task)),
          'full_domain_cases_passed':64,'trusted_template_cases_passed':64,
          'identifiability':ident,'composite_status':'VERIFIED_FOR_THIS_FINITE_TASK',
          'individual_stage_correctness_not_assumed':True,
          'learned_meaning_from_human_language_proven':False,
          'model_written_code_executed':False,'installed':False,
          'external_authority':'NONE'}
    card['proof_digest']=digest(card)
    return card

def verify_card(task,card):
    """Authenticate *content integrity* against source-owner oracle, not origin.

    Hashes alone are not signatures. Always recompute the proof after retrieval.
    """
    if type(card) is not dict or card.get('schema')!=SCHEMA or card.get('task_key')!=task.key:
        raise ProofError('invalid card schema/task')
    copy={k:v for k,v in card.items() if k!='proof_digest'}
    if set(card)!=set(copy)|{'proof_digest'} or card['proof_digest']!=digest(copy):
        raise ProofError('proof record integrity failed')
    roles=card['roles'];rel=card['relation']
    if card['task_spec_sha256']!=digest(public_brief(task)) or card['installed'] is not False:
        raise ProofError('scope changed or source installed')
    c=_pair(task,roles,rel)
    if c['expression']!=card['typed_expression'] or digest(_signature(task,c))!=card['function_sha256']:
        raise ProofError('candidate differs from proof')
    if digest(_target(task))!=card['oracle_function_sha256']:
        raise ProofError('source-owner truth changed')
    if check_truth(task,c)['correct']!=64:
        raise ProofError('not actually correct for declared domain')
    ident=identifiable_stages(task)
    if ident!=card['identifiability']:
        raise ProofError('stage-identifiability labels contradicted')
    # This is a *verification of an earlier runtime receipt*, NOT repeating
    # the subprocess on every retrieval. Full source re-certification repeats it.
    if card['trusted_template_cases_passed']!=64 or card['full_domain_cases_passed']!=64:
        raise ProofError('proof coverage insufficient')
    return True

def retain_hypotheses(task,trial):
    """Retain useful tentative pieces without inflating their epistemic status."""
    if not isinstance(task,Specimen) or type(trial) is not dict or trial.get('task')!=task.key:
        raise ProofError('invalid failed trial')
    if trial.get('status')=='CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED':
        raise ProofError('successful trial belongs in certifier')
    role=trial.get('role_stage');relation=trial.get('relation_stage')
    # Distinguish typed/well-formed from semantically correct.
    if role is not None:role=check_binding(task,role)['bindings']
    if relation is not None:relation=check_relation(relation)['relation']
    card={'schema':'motif.thought027.unverified-fragment.v1',
          'task_key':task.key,'binding_hypothesis':role,'relation_hypothesis':relation,
          'status':'TYPED_HYPOTHESES_NOT_BEHAVIORALLY_CERTIFIED',
          'source_trial_status':trial.get('status'),
          'dev_failed':any(w.get('passed') is False for w in trial.get('development_witnesses',[])),
          'eligible_for_reuse':False,'installed':False}
    card['digest']=digest(card)
    return card

class ProofLibrary:
    """In-memory source-owned artifact. No implicit persistence or authority."""
    def __init__(self):self._records={}
    def admit(self,task,trial,*,origin='UNVERIFIED_PROPOSAL_ORIGIN'):
        card=certify(task,trial,origin=origin)
        self._records[(card['task_key'],card['function_sha256'])]=deepcopy(card)
        return deepcopy(card)
    def cards(self):return [deepcopy(v) for v in self._records.values()]
    def recheck_all(self,task_registry):
        for card in self._records.values():
            task=task_registry.get(card['task_key'])
            if task is None:raise ProofError('unknown or removed source-owner task')
            verify_card(task,card)
        return True
