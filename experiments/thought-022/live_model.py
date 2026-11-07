"""Actual direct local generative LLM trial for THOUGHT-022.

A 3B model may be installed by a separate operator-owned CI job; this file
never downloads it or changes a repository. Strict validated typed DSL outputs
only. Advisor returns review-only missing vocabulary, not an executable patch.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import json,re,sys,time,hashlib
HERE=Path(__file__).resolve().parent
for name in ('thought-017','thought-018','thought-019'):
    p=str(HERE.parent/name)
    if p not in sys.path:sys.path.insert(0,p)
from direct_model import DirectLocalLLM,ModelTransportError,compact
from program import SCHEMA
from research_model import MODEL_SCHEMA,validate_model_reply
from synth import TASKS


class GeneralTaskModel(DirectLocalLLM):
    """Same pinned single-loopback gateway with a task-general prompt.

    It MUST return a checked AST. It doesn't get the classical answer and
    cannot select oracle observations, alter budgets or inspect frozen cases.
    """
    def _instruction(self,brief,feedback):
        if type(brief) is not str or not 8<=len(brief)<=300 or type(feedback) not in (tuple,list) or len(feedback)>6:
            raise ModelTransportError('INVALID_RESEARCH_BRIEF_OR_FEEDBACK')
        cleaned=[]
        allowed={'mechanism','observed_result','oracle_expected','disposition','on_mask',
                 'toggles_mask','surviving_mechanisms'}
        for item in feedback:
            if type(item) is not dict or set(item)-allowed:raise ModelTransportError('UNEXPECTED_DEV_FEEDBACK')
            cleaned.append({'input_on_mask':item.get('on_mask'),
                'input_toggles_mask':item.get('toggles_mask'),
                'your_prediction':item.get('observed_result'),
                'independently_observed':item.get('oracle_expected'),
                'disposition':item.get('disposition')})
        return (
         'You are an experimental proposer. Synthesize a PURE SET TRANSITION expression from the '
         'English behavior specification. The proposed expression will be independently tested. '
         'Set inputs: state.on and arrival.toggles. Allowed AST leaves are exactly '
         '{"ref":"state.on"} and {"ref":"arrival.toggles"}. Allowed binary AST operations are '
         '{"op":"union","args":[expr,expr]} and {"op":"difference","args":[expr,expr]}. '
         'No other operators, no literal constants, no Python, no executable code. '
         'Return exactly one JSON object with six fields: expression, purpose, proposer, on, toggles, reason. '
         'purpose and proposer are strings at least five characters; reason must be at least 8 characters; '
         'on and toggles are arrays with distinct values from red, blue, green. '
         'Your suggested on/toggles probe is not graded unless the independent director chooses it. '
         'Correct previous failures using their input/output observations, never fabricate facts. '
         'DO NOT rely on sample guesses or on any hidden test answer. '
         'Return only JSON. Task and observed development data follow:\n'+
         compact({'task_brief':brief,'development_only_observations':cleaned})
        )

class MissingPrimitiveAdvisor(DirectLocalLLM):
    """An LLM can recommend a vocabulary extension ONLY after grammar exhausts.

    This is a strict suggestion. No extension is executed or installed; the
    finite grammar and target oracle remain source-owned.
    """
    def advise(self,task_brief,witnesses):
        if task_brief not in TASKS.values() or type(witnesses) is not list or len(witnesses)>8:
            raise ModelTransportError('INVALID_GRAMMAR_ADVICE_CONTEXT')
        for witness in witnesses:
            if set(witness)-{'on_mask','toggle_mask','observed_mask','eliminated_count','selection','observation'}:
                raise ModelTransportError('INVALID_WITNESS_DATA')
        self.verify_local_model()
        instruction=(
            'A finite set-expression grammar accepts only two input sets A and B, plus union and '
            'set difference. It cannot express a requested transition. Suggest one MISSING vocabulary '
            'feature only; you cannot write code, install features or judge your proposal. '
            'Reply as a JSON object EXACT keys missing_primitive and reason. '
            'missing_primitive must be complement, constant_universe, or unknown. '
            'reason is one sentence between 8 and 200 chars. This response is a review suggestion, '
            'not proof. Task and DEV-only independent witness: '+
            compact({'task_brief':task_brief,'dev_witnesses':witnesses}))
        body={'model':self.model,'prompt':instruction,'stream':False,
              'format':{'type':'object','properties':{
                'missing_primitive':{'type':'string','enum':['complement','constant_universe','unknown']},
                'reason':{'type':'string','minLength':8,'maxLength':200}},
                'required':['missing_primitive','reason'],'additionalProperties':False},
              'options':{'temperature':0,'num_predict':128,'num_ctx':2048,'num_thread':2}}
        sent=compact(body).encode('utf8')
        if len(sent)>8192:raise ModelTransportError('GRAMMAR_ADVICE_PROMPT_TOO_LONG')
        started=time.monotonic()
        reply=self._json(self.GENERATE,body,cap=32768)
        if reply.get('done') is not True or type(reply.get('response')) is not str:
            raise ModelTransportError('INCOMPLETE_GRAMMAR_ADVICE')
        content=reply['response']
        receipt={'transport':'DIRECT_LOOPBACK_OLLAMA_HTTP',
            'http_generation_completed':True,'role':'REVIEW_ONLY_GRAMMAR_ADVISOR',
            'model_tag':self.model,'prompt_sha256':hashlib.sha256(sent).hexdigest(),
            'reply_sha256':hashlib.sha256(content.encode()).hexdigest(),
            'elapsed_seconds':round(time.monotonic()-started,3),
            'prompt_eval_count':reply.get('prompt_eval_count'),
            'eval_count':reply.get('eval_count'), 'typed_valid':False}
        self.calls.append(receipt)
        try:
            obj=json.loads(content)
        except (ValueError,TypeError):raise ModelTransportError('INVALID_GRAMMAR_ADVICE_JSON')
        if type(obj) is not dict or set(obj)!={'missing_primitive','reason'} or\
            obj['missing_primitive'] not in ('complement','constant_universe','unknown') or\
            type(obj['reason']) is not str or not 8<=len(obj['reason'])<=200:
            raise ModelTransportError('INVALID_GRAMMAR_ADVICE_SCHEMA')
        receipt['typed_valid']=True
        return obj
