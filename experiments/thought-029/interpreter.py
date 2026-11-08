"""Evidence-guided language interpreter with bounded read-only artifact tools.

The LLM is a *relevance and hypothesis proposer*. It may browse any indexed,
permitted MOTIF artifact, symbolic graph or AST. It does not verify its own
interpretation. An independent task owner remains the semantic authority.
"""
from __future__ import annotations
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
HERE=Path(__file__).resolve().parent
for n in ('thought-025','thought-026'):
    p=str(HERE.parent/n)
    if p not in sys.path:sys.path.insert(0,p)
from specimens import Specimen,public_brief
from stages import check_binding,check_relation,assemble,dev_witnesses
from abstraction import check_truth,source_owned_program_check
from artifact_portal import ArtifactPortal,PortalError,compact

SCHEMA='motif.thought029.artifact-guided-interpretation.v1'
class InterpretationError(ValueError):pass


def response_digest(value):return hashlib.sha256(compact(value).encode()).hexdigest()


def _model_answer(task,answer,viewed):
    if type(answer) is not dict or set(answer)!={'action','bindings','relation','evidence_ids','rationale'} or answer['action']!='final':
        raise InterpretationError('final must contain exact typed keys')
    if type(answer['evidence_ids']) is not list or len(answer['evidence_ids'])>8 or any(type(x) is not str for x in answer['evidence_ids']):
        raise InterpretationError('bounded evidence citations required')
    # Citations only to actual tool-observed artifact metadata, never invented.
    if not set(answer['evidence_ids'])<=viewed:raise InterpretationError('citation was not retrieved')
    if type(answer['rationale']) is not str or not 8<=len(answer['rationale'])<=240:
        raise InterpretationError('bounded reasoning text required')
    b=check_binding(task,{'bindings':answer['bindings'],'rationale':answer['rationale']})
    r=check_relation({'relation':answer['relation'],'rationale':answer['rationale']})
    return assemble(task,b,r)


def _traverse_ids(response):
    ids=set()
    if type(response) is not dict:return ids
    if type(response.get('artifact')) is dict:ids.add(response['artifact'].get('id'))
    for x in response.get('items',[]):
        if type(x) is dict and type(x.get('id')) is str:ids.add(x['id'])
    for x in response.get('nodes',[]):
        if type(x) is dict and type(x.get('id')) is str:ids.add(x['id'])
    if type(response.get('graph_id')) is str:ids.add(response['graph_id'].split('#')[0])
    return ids


def trial(task,portal,model,*,max_steps=5,max_dev=4):
    """Actual model drives artifact tools; final typed math gets independent audit.

    A result is NOT a claim of independent language verification: task owner's
    source specification is known to the evaluator and is author-designed.
    """
    if not isinstance(task,Specimen):raise InterpretationError('source-owned specimen required')
    if not isinstance(portal,ArtifactPortal):raise InterpretationError('explicit approved portal required')
    if type(max_steps) is not int or not 2<=max_steps<=8:raise InterpretationError('model action budget 2..8')
    if type(max_dev) is not int or not 2<=max_dev<=4:raise InterpretationError('oracle budget 2..4')
    if not task.representable:
        return {'schema':SCHEMA,'task':task.key,'status':'HOLD_EVALUATOR_DECLARED_NONBOOLEAN_OR_AMBIGUOUS',
                'real_model_calls':0,'tool_calls':0,'frozen':None,'installed':False}
    if not callable(getattr(model,'next',None)):raise InterpretationError('model must propose portal actions')
    transcript=[];observed=set();proposal=None;failure=None
    before=len(getattr(model,'calls',[]));model_requests=0
    for _ in range(max_steps):
        try:
            action=model.next(public_brief(task),deepcopy(transcript),portal.overview())
            model_requests+=1
            if type(action) is not dict or type(action.get('action')) is not str:raise InterpretationError('unknown model action')
            if action['action']=='final':
                if not any(t['stage']=='READ_ONLY_TOOL' for t in transcript):
                    raise InterpretationError('evidence-guided result requires at least one actual portal query')
                proposal=_model_answer(task,action,observed)
                transcript.append({'stage':'FINAL_CANDIDATE','status':'TYPED_NOT_YET_VERIFIED',
                                   'citation_count':len(action['evidence_ids']),'proposal_digest':response_digest(proposal)})
                break
            if action['action'] not in ('catalog','search','graphs','read','neighbors'):
                raise InterpretationError('model action not read-only')
            params={k:v for k,v in action.items() if k in ('artifact_id','pointer','term','kind','graph_id','node_id','cursor','limit')}
            try:
                packet=portal.query({'tool':action['action'],**params})
            except PortalError as exc:
                # Model can recover from a refused hallucinated path, without
                # accessing it and without exceeding its original call budget.
                safe_request={'tool':action['action'],**{k:str(v)[:160] for k,v in params.items()}}
                transcript.append({'stage':'TOOL_REFUSED','request':safe_request,
                                   'error':str(exc)[:100],
                                   'recovery':'Use catalog or search for an EXACT indexed identifier; no file opened',
                                   'material_is_untrusted':True})
                continue
            observed|=_traverse_ids(packet)
            # Source IDs of all graph listings are exposed to the model, not held back.
            for item in packet.get('items',[]):
                if type(item) is dict and type(item.get('artifact_id')) is str:observed.add(item['artifact_id'])
            displayed=compact(packet)
            # Responses can be paginated infinitely; per-call memory budget is bounded.
            if len(displayed)>10_000:
                raise InterpretationError('portal result exceeds context budget; request smaller page')
            transcript.append({'stage':'READ_ONLY_TOOL','request':{'tool':action['action'],**params},
                               'result':packet,'material_is_untrusted':True})
        except Exception as exc:
            failure=type(exc).__name__+': '+str(exc)[:140]
            transcript.append({'stage':'HOLD_INVALID_ACTION_OR_MODEL','error_type':type(exc).__name__})
            break
    dev=frozen=compiled=None
    if proposal is not None and failure is None:
        # No final model access to hidden audit. Tests on evaluator-owned DEV
        # inputs occur only *after* final model proposal, never to improve it.
        witnesses=dev_witnesses(task,proposal,((3,5),(5,3),(7,0),(0,7))[:max_dev])
        dev={'passed':sum(w['passed'] for w in witnesses),'total':len(witnesses),'first_failure':next((x for x in witnesses if not x['passed']),None)}
        if dev['passed']==dev['total']:
            frozen=check_truth(task,proposal)
            if frozen['correct']==64:compiled=source_owned_program_check(task,proposal)
    accepted=bool(compiled and compiled['correct']==64)
    status=('REVIEW_SCOPED_INTERPRETATION_NOT_INSTALLED' if accepted else
            'HOLD_INVALID_MODEL_OR_ARTIFACT_ACTION' if failure else
            'HOLD_MODEL_DID_NOT_SUBMIT_INTERPRETATION' if proposal is None else
            'HOLD_DEV_CONTRADICTION' if dev and dev['passed']!=dev['total'] else
            'HOLD_FROZEN_OR_EXECUTION_COUNTEREXAMPLE')
    report={'schema':SCHEMA,'task':task.key,'status':status,
            'source_artifact_count':len(portal._items),'indexed_symbolic_graph_count':len(portal._graphs),
            'proposer_action_requests':model_requests,
            'actual_model_receipts':deepcopy(getattr(model,'calls',[])[before:]),
            'actual_model_call_count':len(getattr(model,'calls',[]))-before,
            'read_only_tool_calls':sum(item['stage']=='READ_ONLY_TOOL' for item in transcript),
            'visited_artifact_ids':sorted(observed),
            'transcript':transcript,'selected_expression':proposal,
            'development':dev,'frozen':frozen,'fixed_template_executable':compiled,
            'failed_reason':failure,
            'artifact_text_is_not_instruction':True,'graph_coordinates_not_proof':True,
            'model_did_not_receive_truth_policy':True,
            'evaluator_owns_task_ground_truth':True,
            'artifacts_do_not_automatically_certify_claims':True,
            'model_generated_python_executed':False,'installed':False,'external_authority':'NONE'}
    report['report_digest']=response_digest(report)
    return report
