"""Evidence-assisted reuse of previously verified MOTIF reasoning fragments.

Not a language-understanding benchmark: a NEW target's development oracle is
explicitly consulted. Each old card merely proposes a *candidate* mathematical
function. Successful transfer must be independently reverified on the new task.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for name in ('thought-025','thought-026'):
    p=str(HERE.parent/name)
    if p not in sys.path:sys.path.insert(0,p)
from specimens import Specimen,independent_target
from stages import RELATIONS,assemble
from abstraction import evaluate_reply,check_truth,source_owned_program_check,raw_cases
from proof_memory import ProofError,ProofLibrary,canonical,digest

SCHEMA='motif.thought027.evidence-assisted-transfer.v1'


def _candidate(task,rel,first,second):
    return assemble(task,{'bindings':{'current':first,'event':second},
           'rationale':'Operator-independent trial role permutation'},
           {'relation':rel,'rationale':'Prior independently checked kernel'})

def _fingerprint(task,proposal):
    return tuple(evaluate_reply(task,proposal,raw) for raw in raw_cases(task))

def _choose_query(alive,seen):
    """Choose the best separating probe from candidate semantics only.

    Crucially, NO target answer is inspected here: this is not hidden-test leakage.
    """
    choice=None;key=None
    for i in range(8):
        for j in range(8):
            if (i,j) in seen:continue
            counts=Counter(sig[i*8+j] for sig in alive)
            separation=len(alive)**2 - sum(n*n for n in counts.values())
            candidate=(separation,len(counts),-i,-j)
            if key is None or candidate>key:
                key=candidate;choice=(i,j)
    return choice


def build_candidates(task,cards,*,known_tasks):
    """Vetted old cards yield operation hypotheses, never asserted task meaning."""
    if not isinstance(task,Specimen) or not task.representable:
        raise ProofError('only known, Booleanizable task specs')
    if len(cards)>48:raise ProofError('too many library cards')
    field_names=[a for a,_ in task.fields]
    result={}
    from proof_memory import verify_card
    for card in cards:
        known=known_tasks.get(card.get('task_key'))
        if known is None:raise ProofError('unresolved source-task provenance')
        verify_card(known,card)
        # A relation certified on the OLD task is a valid reusable candidate
        # operation; its binding is never declared correct for the NEW story.
        relation=card['relation']
        if relation not in RELATIONS:raise ProofError('unknown recorded relation')
        for first,second in ((field_names[0],field_names[1]),(field_names[1],field_names[0])):
            proposed=_candidate(task,relation,first,second)
            sig=_fingerprint(task,proposed)
            key=digest(sig)
            if key not in result:
                result[key]={'proposal':proposed,'signature':sig,
                             'sources':[card['proof_digest']],
                             'source_relations':[relation]}
            else:
                result[key]['sources'].append(card['proof_digest'])
                result[key]['source_relations'].append(relation)
    return result


def reuse(task,library,task_registry,*,query_budget=4,min_dev_probes=2):
    if type(query_budget) is not int or not 1<=query_budget<=6 or \
       type(min_dev_probes) is not int or not 2<=min_dev_probes<=query_budget:
        raise ProofError('invalid development query budget')
    if not isinstance(task,Specimen):raise ProofError('task owner must supply typed spec')
    if not task.representable:
        return {'schema':SCHEMA,'task':task.key,'status':'HOLD_NON_BOOLEAN_OR_AMBIGUOUS',
                'reason':'Source owner declined Boolean coercion','oracle_queries':0,
                'no_language_meaning_inferred':True,'installed':False}
    library.recheck_all(task_registry)
    candidates=build_candidates(task,library.cards(),known_tasks=task_registry)
    if not candidates:
        return {'schema':SCHEMA,'task':task.key,'status':'HOLD_NO_VERIFIED_SOURCE_FRAGMENTS',
                'oracle_queries':0,'installed':False}
    original=len(candidates);alive=candidates.copy();used=set();observed=[]
    names=[x[0] for x in task.fields]
    for _ in range(query_budget):
        if len(alive)==1 and len(observed)>=min_dev_probes:break
        query=_choose_query({sig:v for sig,v in ((v['signature'],v) for v in alive.values())},used)
        if query is None:break
        x,y=query;raw={names[0]:x,names[1]:y}
        measured=independent_target(task,raw)  # distinct source-owned DEV oracle
        previous=len(alive)
        alive={key:v for key,v in alive.items() if v['signature'][x*8+y]==measured}
        observed.append({'inputs':raw,'actual':measured,'before':previous,
                         'surviving':len(alive),'label':'DEV_ORACLE_NOT_LLM'})
        used.add(query)
        if not alive:break
    status='HOLD_NO_REUSABLE_MECHANISM' if not alive else (
        'HOLD_INDETERMINATE_WITHIN_BUDGET' if len(alive)!=1 or len(observed)<min_dev_probes else
        'REVIEW_REUSE_CANDIDATE_NOT_INSTALLED')
    audited=fixed=None;winner=None
    if status=='REVIEW_REUSE_CANDIDATE_NOT_INSTALLED':
        winner=next(iter(alive.values()))
        audited=check_truth(task,winner['proposal'])
        if audited['correct']!=64:
            status='HOLD_FROZEN_COUNTEREXAMPLE'
        else:
            fixed=source_owned_program_check(task,winner['proposal'])
            if fixed['correct']!=64:status='HOLD_EXECUTION_DISAGREEMENT'
    packet={'schema':SCHEMA,'task':task.key,'status':status,
            'original_distinct_candidate_functions':original,
            'source_card_count':len(library.cards()),
            'oracle_queries':len(observed),'development_receipts':observed,
            'selected_relation':winner['source_relations'][0] if winner else None,
            'selected_expression':winner['proposal'] if winner else None,
            'source_proof_digests':winner['sources'] if winner else [],
            'frozen':audited,'fixed_template_execution':fixed,
            'only_evaluator_gives_new_task_ground_truth':True,
            'new_task_roles_inferred_from_language':False,
            'reused_fragments_rechecked_on_new_task':True,
            'no_model_code_executed':True,'installed':False,'external_authority':'NONE'}
    packet['receipt_digest']=digest(packet)
    return packet


def compose_difference_union(task,difference_card,union_card,known_tasks,*,binding=None):
    """Build a NEW candidate from two audited old fragments, then verify it.

    Demonstration: (A - B) union (B - A) yields symmetric difference.
    The verified predecessor components do not imply the composition is
    correct for the new story. It must earn its own development/audit evidence.
    """
    from proof_memory import verify_card
    if not isinstance(task,Specimen) or not task.representable:
        raise ProofError('task cannot be faithfully Booleanized')
    if difference_card['relation']!='DIFFERENCE' or union_card['relation']!='UNION':
        raise ProofError('composition requires independently audited difference and union')
    for card in (difference_card,union_card):
        known=known_tasks.get(card['task_key'])
        if known is None:raise ProofError('missing source owner')
        verify_card(known,card)
    names=[x[0] for x in task.fields]
    if binding is None:
        binding={'current':names[0],'event':names[1]}
    if type(binding) is not dict or set(binding)!={'current','event'} or set(binding.values())!=set(names):
        raise ProofError('invalid explicitly hypothesized target binding')
    def ref(s):return {'ref':s}
    def op(k,x,y):return {'op':k,'args':[x,y]}
    a,b=ref('state.on'),ref('arrival.toggles')
    expr=op('union',op('difference',a,b),op('difference',b,a))
    proposal={'schema':'motif.thought025.abstraction-proposal.v1','bindings':binding,
              'expression':expr,'rationale':'Compose independently proven set operations under new test'}
    # Never use task's full 64-case oracle to *choose* the candidate: already frozen.
    raw_dev=[{names[0]:x,names[1]:y} for x,y in ((3,5),(1,3),(7,0),(0,7))]
    observations=[{'inputs':raw,'actual':independent_target(task,raw),
                   'predicted':evaluate_reply(task,proposal,raw)} for raw in raw_dev]
    status='HOLD_DEVELOPMENT_CONTRADICTION'
    full=runtime=None
    if all(x['actual']==x['predicted'] for x in observations):
        full=check_truth(task,proposal)
        if full['correct']==64:
            runtime=source_owned_program_check(task,proposal)
            status='REVIEW_COMPOSED_CANDIDATE_NOT_INSTALLED' if runtime['correct']==64 else 'HOLD_EXECUTION_DISAGREEMENT'
        else:status='HOLD_FROZEN_COUNTEREXAMPLE'
    result={'schema':'motif.thought027.compositional-reuse.v1','task':task.key,
            'status':status,'derived_expression':expr,
            'source_proof_digests':[difference_card['proof_digest'],union_card['proof_digest']],
            'development':observations,'oracle_queries':len(observations),
            'frozen':full,'source_owned_runtime':runtime,
            'verified_component_does_not_certify_composition':True,
            'human_selected_binding_hypothesis':True,
            'installed':False,'external_authority':'NONE'}
    result['receipt_digest']=digest(result)
    return result
