"""THOUGHT-031: source-prefetched, read-only research with a reserved model final.

The reserved final is not a synthetic answer. It is an actual separate model
request even when previous model-directed retrieval failed or pidgin was unused.
All mathematical outcomes are independently evaluated after the model stops.
"""
from __future__ import annotations
import sys,copy
from pathlib import Path
HERE=Path(__file__).resolve().parent
for d in ('thought-025','thought-026','thought-029','thought-030'):
    p=str(HERE.parent/d)
    if p not in sys.path:sys.path.insert(0,p)
from specimens import Specimen,public_brief
from stages import dev_witnesses
from abstraction import check_truth,source_owned_program_check
from interpreter import _model_answer,response_digest
from artifact_portal import ArtifactPortal,PortalError,compact
from pidgin import PARAMS
from pidgin2 import ParameterizedPidgin,PidginProtocolError
from relay import EvidenceRelay,RelayError,BLOCK

SCHEMA='motif.thought031.protected-final-evidence-relay.v1'
class RelaySessionError(ValueError):pass

def scoped_read(portal,tool_packet):
    if type(tool_packet) is not dict or tool_packet.get('tool') not in ('read','graphs','neighbors','search','catalog'):
        raise RelaySessionError('read-only operation expected')
    # All explicit model-selected reads still pass through target-blind benchmark gate.
    if tool_packet['tool']=='read' and BLOCK.search(str(tool_packet.get('artifact_id',''))):
        raise RelaySessionError('evaluator-owned benchmark sources not admissible as evidence')
    if tool_packet['tool']=='neighbors' and BLOCK.search(str(tool_packet.get('graph_id','')).split('#')[0]):
        raise RelaySessionError('benchmark graphs not admissible')
    return portal.query(tool_packet)

def trial(task,portal,model,*,enable_pidgin=True,research_steps=2,preload=3):
    if not isinstance(task,Specimen) or not isinstance(portal,ArtifactPortal):
        raise RelaySessionError('typed task and approved portal required')
    if type(research_steps) is not int or not 0<=research_steps<=3:
        raise RelaySessionError('research budget 0..3')
    if type(preload) is not int or not 1<=preload<=5:raise RelaySessionError('preload budget')
    if not callable(getattr(model,'research',None)) or not callable(getattr(model,'conclude',None)):
        raise RelaySessionError('explicit research/conclusion model required')
    if not task.representable:
        return {'schema':SCHEMA,'task':task.key,
              'status':'HOLD_EVALUATOR_DECLARED_NONBOOLEAN_OR_AMBIGUOUS',
              'model_calls':0,'frozen':None,'installed':False,'gate_owner':'SOURCE_EVALUATOR_NOT_MODEL'}
    evidence=EvidenceRelay(portal).prepare(public_brief(task),limit=preload)
    packet=evidence['packet']
    available=set(packet['actually_read_artifact_ids'])
    pidgin=ParameterizedPidgin(portal,enabled=enable_pidgin)
    before=len(getattr(model,'calls',[]));transcript=[];model_issues=0
    for i in range(research_steps):
        try:
            action=model.research(public_brief(task),packet,copy.deepcopy(transcript[-3:]),pidgin.view(),enable_pidgin)
            if type(action) is not dict or type(action.get('action')) is not str:
                raise RelaySessionError('typed research action missing')
            command=action['action']
            if command=='define':
                if set(action)!={'action','symbol','template','gloss'}:raise PidginProtocolError('invalid definition shape')
                response=pidgin.define(action['symbol'],action['template'],action['gloss'])
                transcript.append({'stage':'PIDGIN_DEFINED','symbol':response['symbol'],
                                   'typed_slots':response['slot_types']})
                continue
            if command=='speak':
                if set(action)!={'action','symbol','values'}:raise PidginProtocolError('invalid speaking shape')
                request=pidgin.speak(action['symbol'],action['values'])
                origin='MODEL_PIDGIN_WITH_AUDITABLE_BACKTRANSLATION'
            elif command=='skip':
                if set(action)!={'action'}:raise RelaySessionError('skip has no args')
                transcript.append({'stage':'SKIP','model_declined_additional_retrieval':True})
                continue
            elif command in ('read','graphs','catalog','search','neighbors'):
                request={'tool':command,**{k:v for k,v in action.items() if k in PARAMS[command]}}
                origin='DIRECT_CANONICAL_TOOL'
            else:raise RelaySessionError('unknown model research operation')
            if request['tool']=='read' and request.get('artifact_id') in available:
                transcript.append({'stage':'REDUNDANT_RETRIEVAL_REFUSED','request':request})
                continue
            result=scoped_read(portal,request)
            source=result.get('artifact',{}).get('id') if type(result.get('artifact')) is dict else None
            if type(source) is str:available.add(source)
            if request['tool']=='neighbors':
                aid=str(request.get('graph_id','')).split('#')[0]
                if aid in portal._items:available.add(aid)
            # Explicitly distinguish search/list hits from actually inspected.
            transcript.append({'stage':'MODEL_DIRECTED_READ_ONLY_TOOL','request':request,
                 'source':source,'origin':origin,'result_excerpt':copy.deepcopy(result) if len(compact(result))<3500 else 'PAGED_RESULT_OVERSIZED_NOT_FORWARDABLE',
                 'tool_contents_are_untrusted':True})
        except Exception as error:
            model_issues+=1
            transcript.append({'stage':'RECOVERABLE_RESEARCH_REFUSAL','reason':type(error).__name__,
                               'final_inference_still_reserved':True})
    # The final is always a *fresh model inference* if the backend is real.
    packet['actually_read_artifact_ids']=sorted(available)
    proposal=None;failure=None
    try:
        answer=model.conclude(public_brief(task),packet,copy.deepcopy(transcript[-4:]),pidgin.view(),enable_pidgin)
        if type(answer) is not dict or set(answer)!={'bindings','relation','evidence_ids','rationale'}:
            raise RelaySessionError('final answer must contain exactly four fields')
        proposed={'action':'final',**answer}
        if not answer['evidence_ids'] or not set(answer['evidence_ids'])<=available:
            raise RelaySessionError('model cited an artifact not actually retrieved')
        proposal=_model_answer(task,proposed,available)
    except Exception as err:
        failure=type(err).__name__+': '+str(err)[:145]
    dev=frozen=fixed=None
    if proposal is not None:
        witnesses=dev_witnesses(task,proposal,((3,5),(5,3),(7,0),(0,7)))
        dev={'correct':sum(x['passed'] for x in witnesses),'total':len(witnesses),
             'first_failed':next((x for x in witnesses if not x['passed']),None)}
        if dev['correct']==dev['total']:
            frozen=check_truth(task,proposal)
            if frozen['correct']==64:fixed=source_owned_program_check(task,proposal)
    status=('REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED' if fixed and fixed['correct']==64 else
            'HOLD_INVALID_FINAL_OR_CITATION' if failure else
            'HOLD_DEV_COUNTEREXAMPLE' if dev and dev['correct']<dev['total'] else
            'HOLD_FROZEN_OR_EXECUTOR_COUNTEREXAMPLE')
    result={'schema':SCHEMA,'task':task.key,'status':status,
        'pidgin_offered':enable_pidgin,'pidgin_lexicon':pidgin.view(),
        'pidgin_was_used':len(pidgin.uses)>0,'pidgin_effectiveness':pidgin.cost_report(),
        'source_owned_prefetch_count':len(evidence['plan']['selected_artifact_ids']),
        'source_owned_prefetch_references':evidence['plan']['selected_artifact_ids'],
        'actually_read_artifact_ids':sorted(available),
        'actual_model_call_count':len(getattr(model,'calls',[]))-before,
        'model_receipts':copy.deepcopy(getattr(model,'calls',[])[before:]),
        'research_calls_requested':research_steps,'final_inference_reserved':True,
        'model_research_refusals':model_issues,'research_trace':transcript,
        'candidate':proposal,'development':dev,'frozen':frozen,'fixed_template':fixed,
        'failure':failure,'model_not_supplied_evaluator_answer':True,
        'source_artifacts_untrusted_and_unmodified':True,
        'evaluator_and_model_held_separate':True,'installed':False,'external_authority':'NONE'}
    result['receipt_digest']=response_digest(result)
    return result
