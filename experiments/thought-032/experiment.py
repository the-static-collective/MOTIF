"""Experimentally compare canonical mathematics with an optionally co-invented concept word.

Two target tasks are evaluated *only after* the LLM commits to a response. The
source-owner bitmask evaluator never appears in the LLM prompt. The prior proof
card is a scripted-fixture seed, not independent evidence of a model invention.
"""
from __future__ import annotations
import copy,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for name in ('thought-025','thought-026','thought-027'):
    p=str(HERE.parent/name)
    if p not in sys.path:sys.path.insert(0,p)
from specimens import Specimen,public_brief,BY_KEY
from stages import assemble,dev_witnesses
from abstraction import check_truth,source_owned_program_check
from proof_memory import ProofLibrary,verify_card,digest as card_digest
from stage_fixtures import DeterministicStages
from stages import stage_trial
from concept_language import ConceptBook,ConceptError,validate_definition,graph_match,RELATIONS

SCHEMA='motif.thought032.verified-concept-transfer.v1'
class ExperimentError(ValueError):pass

# Source-owned snapshot, not evidence about the outside world.
GRAPH_FIXTURE={
 'nodes':[{'id':x,'label':x} for x in ('food','cold_storage','power','meal','volunteer','venue')],
 'edges':[
  {'source':'food','target':'cold_storage','relation':'requires','origin':'synthetic_a','observed':True},
  {'source':'cold_storage','target':'power','relation':'requires','origin':'synthetic_b','observed':True},
  {'source':'food','target':'meal','relation':'associated','origin':'synthetic_a','observed':True},
  {'source':'food','target':'venue','relation':'associated','origin':'synthetic_b','observed':True},
  {'source':'volunteer','target':'meal','relation':'associated','origin':'synthetic_c','observed':True},
  {'source':'volunteer','target':'venue','relation':'associated','origin':'synthetic_d','observed':True},
  {'source':'meal','target':'venue','relation':'contradicts','origin':'synthetic_e','observed':False}
 ]}

def prior_seed():
    # Genuine independent recheck of a SOURCE-KNOWN scripted prior claim.
    task=BY_KEY['food_safe']
    lib=ProofLibrary();trial=stage_trial(task,DeterministicStages())
    proof=lib.admit(task,trial,origin='SCRIPTED_SOURCE_OWNER_FIXTURE_NOT_REAL_LLM')
    verify_card(task,proof)
    return {'proof_digest':proof['proof_digest'],'relation':proof['relation'],
      'original_problem':task.description,'bounded_scope':proof['source_owner_semantic_scope'],
      'full_cases':proof['full_domain_cases_passed'],
      'new_task_automatically_proven':False,'authentication':'UNSIGNED_SYNTHETIC'}

def public_context(seed):
    return {'proof_seed':copy.deepcopy(seed),'graph_snapshot':copy.deepcopy(GRAPH_FIXTURE),
       'graph_coordinates_prove_nothing':True,
       'approved_patterns':['NONE','DEPENDENCY_CHAIN','TENSION_EDGE','ASSOCIATION_BRIDGE'],
       'math_relations':list(RELATIONS),
       'new_task_requires_independent_oracle':True}

def evaluate_submission(task,submission,book,*,seed):
    if not isinstance(task,Specimen) or type(submission) is not dict:
        raise ExperimentError('task and exact model envelope needed')
    if not task.representable:return {'status':'HOLD_NONBOOLEAN','installed':False,'model_word_used':False}
    if set(submission)!={'bindings','word','relation','evidence_refs','rationale'}:
        raise ExperimentError('unexpected answer fields')
    b=submission['bindings']
    if type(b) is not dict or set(b)!={'current','event'} or set(b.values())!={x[0] for x in task.fields}:
        raise ExperimentError('invalid field roles')
    phrase=submission['rationale']
    if type(phrase) is not str or not 8<=len(phrase)<=240:raise ExperimentError('missing explanation')
    refs=submission['evidence_refs']
    if type(refs) is not list or len(refs)>3 or any(r!=seed['proof_digest'] for r in refs):
        raise ExperimentError('invented proof citation')
    relation=submission['relation'];word=submission['word']
    used=False;concept=None;graph=None
    if word is not None:
        if relation is not None:raise ExperimentError('cannot mix invented word and canonical relation')
        if type(word) is not str:raise ExperimentError('invalid word')
        concept=book.expand(word)
        relation=concept['relation'];used=True
        graph=graph_match(concept['graph_pattern'],GRAPH_FIXTURE)
    else:
        if relation not in RELATIONS:raise ExperimentError('invalid canonical operation')
    candidate=assemble(task,
        {'bindings':b,'rationale':phrase},
        {'relation':relation,'rationale':phrase})
    # Frozen audit is never allowed to guide a revision in this trial.
    dev=dev_witnesses(task,candidate,((3,5),(5,3),(7,0),(0,7)))
    count=sum(x['passed'] for x in dev)
    frozen=executor=None
    if count==4:
        frozen=check_truth(task,candidate)
        if frozen['correct']==64:executor=source_owned_program_check(task,candidate)
    status=('REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED' if executor and executor['correct']==64 else
        'HOLD_DEV_COUNTEREXAMPLE' if count<4 else 'HOLD_FROZEN_OR_EXECUTION_COUNTEREXAMPLE')
    return {'task':task.key,'status':status,'model_word_used':used,
      'word':word if used else None,'decoded_relation':relation,
      'declared_proof_citations':refs,'seed_card_is_prior_scope_only':True,
      'graph_structural_match':graph,'dev_correct':count,'dev_total':4,
      'frozen_correct':frozen['correct'] if frozen else None,
      'trusted_executable_correct':executor['correct'] if executor else None,
      'code_from_model_executed':False,'cross_domain_meaning_preverified':False,
      'installed':False,'authority':'NONE'}

def session(tasks,model,*,pidgin_enabled):
    if type(tasks) not in (list,tuple) or any(not isinstance(t,Specimen) for t in tasks):
        raise ExperimentError('known synthetic target tasks required')
    if len(tasks)!=2:raise ExperimentError('exactly two transfer targets')
    seed=prior_seed();ctx=public_context(seed);book=ConceptBook(enabled=pidgin_enabled)
    before=len(getattr(model,'calls',[]));history=[];training=None
    try:
        training=model.prepare(ctx,pidgin_enabled)
        if pidgin_enabled:
            if type(training) is not dict or set(training)!={'choice','definition'}:
                raise ExperimentError('invent-or-decline packet required')
            if training['choice']=='coin':
                book.admit(training['definition'])
            elif training['choice']=='decline':
                if training['definition'] is not None:raise ExperimentError('decline must not add term')
            else:raise ExperimentError('unknown model choice')
        else:
            if type(training) is not dict or set(training)!={'choice','definition'} or training['choice']!='baseline' or training['definition'] is not None:
                raise ExperimentError('baseline does not create a word')
    except Exception as err:
        history.append({'stage':'PREPARE_HOLD','failure':type(err).__name__})
    outcomes={}
    for task in tasks:
        try:
            answer=model.apply(public_brief(task),ctx,book.view(),pidgin_enabled)
            outcomes[task.key]=evaluate_submission(task,answer,book,seed=seed)
        except Exception as e:
            outcomes[task.key]={'task':task.key,'status':'HOLD_INVALID_MODEL_OUTPUT',
                  'error_type':type(e).__name__, 'model_word_used':False,'installed':False}
    receipts=copy.deepcopy(getattr(model,'calls',[])[before:])
    result={'schema':SCHEMA,'backend_kind':getattr(model,'kind','UNKNOWN'),
      'pidgin_offered':pidgin_enabled,'source_owned_seed_digest':seed['proof_digest'],
      'model_inference_receipts':receipts,'inference_calls':len(receipts),
      'concept_book':book.view(),'concept_use_receipts':copy.deepcopy(book.use_receipts),
      'results':outcomes,'history':history,
      'all_preexisting_graph_edges_are_untrusted_synthetic':True,
      'model_never_obtains_task_truth_policy':True,
      'no_external_actions':True,'installed':False,'authority':'NONE'}
    result['result_digest']=card_digest(result)
    return result
