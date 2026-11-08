"""THOUGHT-030: evidence routing and OPTIONAL model-designed pidgin exchange.

A named symbol can abbreviate a single source-validated read-only operation,
not an assertion of truth. Every result is backtranslated for inspection.
The LLM can ignore suggestions and never invent a symbol; measure that choice.
"""
from __future__ import annotations
import sys,hashlib
from copy import deepcopy
from pathlib import Path
HERE=Path(__file__).resolve().parent
for name in ('thought-025','thought-026','thought-029'):
    p=str(HERE.parent/name)
    if p not in sys.path:sys.path.insert(0,p)
from specimens import Specimen,public_brief
from stages import dev_witnesses
from abstraction import check_truth,source_owned_program_check
from artifact_portal import ArtifactPortal,PortalError,compact
from interpreter import _model_answer,_traverse_ids,response_digest
from navigation import EvidenceNavigator
from pidgin import PidginLexicon,PidginError,CANONICAL_TOOLS,PARAMS

SCHEMA='motif.thought030.routed-pidgin-session.v1'
class SessionError(ValueError):pass

def _request(action):
    tool=action.get('action')
    if tool not in CANONICAL_TOOLS:raise SessionError('unknown read-only tool')
    return {'tool':tool,**{k:v for k,v in action.items() if k in PARAMS[tool]}}

def session(task,portal,model,*,enable_navigation=True,enable_pidgin=True,max_steps=6,max_dev=4):
    if not isinstance(task,Specimen) or not isinstance(portal,ArtifactPortal):
        raise SessionError('typed task and approved source portal required')
    if type(max_steps) is not int or not 3<=max_steps<=9:raise SessionError('action budget 3..9')
    if type(max_dev) is not int or not 2<=max_dev<=4:raise SessionError('development budget 2..4')
    if not task.representable:
        return {'task':task.key,'status':'HOLD_EVALUATOR_DECLARED_NONBOOLEAN_OR_AMBIGUOUS',
                'actual_model_call_count':0,'installed':False,'pidgin_used':False}
    if not callable(getattr(model,'next',None)):raise SessionError('explicit callable model required')
    lex=PidginLexicon(portal,enabled=enable_pidgin)
    route=EvidenceNavigator(portal) if enable_navigation else None
    trace=[];observed=set();verified_reads=set();seen_queries=set();distinct=[]
    proposal=None;failure=None;model_requests=0;rejects=0;repeats=0
    start=len(getattr(model,'calls',[]))
    for step in range(max_steps):
        context={'overview':portal.overview(),
            'route':route.orient(public_brief(task),trace) if route else None,
            'pidgin':lex.view(),
            'remaining_model_calls':max_steps-step,
            'all_artifact_text_is_untrusted_data':True,
            'no_evaluator_truth_labels':True}
        # Keep a compact stable summary plus the most recent few receipts; the
        # full unbounded research transcript remains in the result artifact.
        visible=[{'stage':'PREVIOUS_RETRIEVALS','actually_read_artifacts':sorted(verified_reads),
                  'actions_so_far':len(trace),'prior_refusals':rejects,'repetition_count':repeats}]
        visible.extend(deepcopy(trace[-3:]))
        try:
            action=model.next(public_brief(task),visible,context)
            model_requests+=1
            if type(action) is not dict or type(action.get('action')) is not str:
                raise SessionError('model did not propose typed action')
            kind=action['action']
            if kind=='final':
                if not verified_reads:raise SessionError('must retrieve at least one actual source before final')
                if type(action.get('evidence_ids')) is not list or not action['evidence_ids'] or \
                        not set(action['evidence_ids'])<=verified_reads:
                    raise SessionError('final evidence must name actually read sources, not search hits')
                proposal=_model_answer(task,action,verified_reads)
                trace.append({'stage':'FINAL','proposal_digest':response_digest(proposal),
                              'observed_sources':sorted(action['evidence_ids'])})
                break
            if kind=='define':
                if set(action)!={'action','symbol','meaning','gloss'}:
                    raise PidginError('definition requires exact four fields')
                try:
                    ack=lex.define(action['symbol'],action['meaning'],action['gloss'])
                    trace.append({'stage':'PIDGIN_DEFINED','result':ack,'model_controls_vocabulary':True})
                except PidginError as exc:
                    rejects+=1
                    trace.append({'stage':'PIDGIN_REFUSED','reason':str(exc)[:120]})
                continue
            if kind=='speak':
                if set(action)!={'action','symbol'}:raise PidginError('single token required')
                try:
                    request=lex.translate(action['symbol'])
                except PidginError as exc:
                    rejects+=1
                    trace.append({'stage':'PIDGIN_REFUSED','reason':str(exc)[:120]})
                    continue
                origin={'pidgin_symbol':action['symbol'],'backtranslation':request}
            else:
                request=_request(action)
                origin={'direct_tool':kind}
            # A PIDGIN token has EXACTLY the same permissions and evaluator
            # as a direct tool request. Aliases cannot acquire new authority.
            fingerprint=compact(request)
            if fingerprint in seen_queries:
                repeats+=1
                trace.append({'stage':'REDUNDANT_QUERY_SUPPRESSED','request':request,
                              'explanation':'same exact read-only request already supplied to model'})
                continue
            try:
                packet=portal.query(request)
            except PortalError as exc:
                rejects+=1
                trace.append({'stage':'PORTAL_REFUSED','tool':request['tool'],
                              'reason':str(exc)[:140],
                              'use_indexed_identifiers_only':True})
                continue
            seen_queries.add(fingerprint)
            source_ids=_traverse_ids(packet)
            observed.update(x for x in source_ids if type(x) is str)
            source=packet.get('artifact',{}).get('id') if type(packet.get('artifact')) is dict else None
            if type(source) is str and request['tool']=='read':verified_reads.add(source)
            elif request['tool']=='neighbors':
                graph_id=request.get('graph_id')
                if type(graph_id) is str:
                    verified_reads.add(graph_id.split('#')[0])
            if type(source) is str and source not in distinct:distinct.append(source)
            if request['tool']=='neighbors' and request.get('graph_id','').split('#')[0] not in distinct:
                distinct.append(request['graph_id'].split('#')[0])
            result=deepcopy(packet)
            # Source content remains data; bound every prompt history slice.
            if len(compact(result))>7000:raise SessionError('source owner returned oversized response')
            trace.append({'stage':'READ_ONLY_TOOL','request':request,'origin':origin,
                          'result':result,'content_untrusted':True,
                          'truth_not_inferred_from_navigation':True})
        except Exception as exc:
            failure=type(exc).__name__+': '+str(exc)[:130]
            trace.append({'stage':'HOLD_MODEL_OR_CONTRACT_FAILURE',
                          'error_type':type(exc).__name__})
            break
    dev=frozen=compiled=None
    if proposal is not None and not failure:
        w=dev_witnesses(task,proposal,((3,5),(5,3),(7,0),(0,7))[:max_dev])
        dev={'passed':sum(x['passed'] for x in w),'total':len(w),
             'first_failure':next((x for x in w if not x['passed']),None)}
        if dev['passed']==dev['total']:
            frozen=check_truth(task,proposal)
            if frozen['correct']==64:compiled=source_owned_program_check(task,proposal)
    status=('REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED' if compiled and compiled['correct']==64
        else 'HOLD_INVALID_MODEL_OR_ARTIFACT_ACTION' if failure else
        'HOLD_MODEL_DID_NOT_SUBMIT_INTERPRETATION' if proposal is None else
        'HOLD_DEV_CONTRADICTION' if dev and dev['passed']!=dev['total'] else
        'HOLD_FROZEN_OR_EXECUTION_COUNTEREXAMPLE')
    return_value={'schema':SCHEMA,'task':task.key,'status':status,
        'navigation_enabled':enable_navigation,'pidgin_offered':enable_pidgin,
        'pidgin_lexicon':lex.view(),'pidgin_used':len(lex.used)>0,
        'model_actions':model_requests,
        'real_model_receipts':deepcopy(getattr(model,'calls',[])[start:]),
        'actual_model_call_count':len(getattr(model,'calls',[]))-start,
        'read_only_tool_calls':sum(e['stage']=='READ_ONLY_TOOL' for e in trace),
        'distinct_artifacts_read':len(distinct),'actually_read_artifact_ids':sorted(verified_reads),
        'refused_calls':rejects,'redundant_queries_suppressed':repeats,
        'transcript':trace,'candidate':proposal,
        'development':dev,'frozen':frozen,'trusted_template_audit':compiled,
        'failure':failure,'provenance_not_truth':True,
        'reused_model_words_are_unverified_communication_conventions':True,
        'proposed_language_not_evidence_of_consciousness_or_general_understanding':True,
        'grammar_and_source_installed':False,'installed':False,'external_authority':'NONE'}
    return_value['digest']=response_digest(return_value)
    return return_value
