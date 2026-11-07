"""Direct local generative model proposes BOTH input bindings and math expression.

No hand-authored domain bindings in prompts. All responses untrusted. Reuses 019
real Ollama loopback HTTP transport, finite registry and output receipts.
"""
from __future__ import annotations
import sys,json,time,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
for n in ('thought-019','thought-023'):
    p=str(HERE.parent/n)
    if p not in sys.path:sys.path.insert(0,p)
from direct_model import DirectLocalLLM,ModelTransportError,compact
from abstraction import SCHEMA

class DirectAbstractionLLM(DirectLocalLLM):
    kind='DIRECT_LLM_ABSTRACT_LANGUAGE_TO_TYPED_MATH'
    def propose(self,public_task,feedback=()):
        if type(public_task) is not dict or set(public_task)!={'story','input_fields','feature_count','meaning'}:
            raise ModelTransportError('invalid public problem contract')
        if type(feedback) not in (tuple,list) or len(feedback)>2:
            raise ModelTransportError('feedback bound')
        ids=[x['id'] for x in public_task['input_fields']]
        if len(ids)!=2 or any(type(x) is not str or len(x)>50 for x in ids):
            raise ModelTransportError('invalid field labels')
        for item in feedback:
            if type(item) is not dict or set(item)!={'inputs','observed','proposed'} or \
               set(item['inputs'])!=set(ids) or any(type(v) is not int or not 0<=v<=7 for v in [*item['inputs'].values(),item['observed'],item['proposed']]):
                raise ModelTransportError('feedback is not a permitted developer witness')
        instruction=(
            'You are translating a HUMAN DESCRIPTION into a PURE set-theoretic representation. '
            'The two input field IDs are arbitrary opaque identifiers. Do NOT assume the first field is '
            'always the primary input; infer its role by reading the story. '
            'Return ONLY JSON with exact keys: bindings,expression,rationale. '
            'bindings is an object with exactly keys current and event, and must map each '
            'to a DIFFERENT one of the two exact field IDs in the supplied task. '
            'Expression refs are only {"ref":"state.on"} (set bound to current), '
            '{"ref":"arrival.toggles"} (set bound to event), or {"ref":"universe"} '
            '(all possible feature categories). Binary expression operations are ONLY '
            '{"op":"union","args":[expr,expr]} and '
            '{"op":"difference","args":[expr,expr]}. '
            'To express both, use difference composition; to express exclusive toggling, '
            'combine two differences using union. Use exactly those AST node shapes. '
            'Any nonexpressible or ambiguous task should produce no valid answer; no invented claims. '
            'rationale should explain the mapping and transformation in at least 12 characters. '
            'Any prior numerical records are development observations, not proof of general behavior. '
            'DO NOT supply Python, deployment, operations on real people or permission changes. '
            'DO NOT invent IDs, semantic rules, test results, or more fields. '
            'The independent evaluator, NOT you, decides correctness. '
        )
        packet=compact({'task':public_task,'dev_feedback':list(feedback)})
        prompt=instruction+'\nTASK_JSON_DATA='+packet
        model=self.verify_local_model()
        format_schema={'type':'object','properties':{
            'bindings':{'type':'object','properties':{'current':{'type':'string','enum':ids},
                     'event':{'type':'string','enum':ids}},'required':['current','event'], 'additionalProperties':False},
            'expression':{'type':'object'},'rationale':{'type':'string','minLength':12,'maxLength':250}},
            'required':['bindings','expression','rationale'],'additionalProperties':False}
        request={'model':self.model,'prompt':prompt,'stream':False,'format':format_schema,
                 'options':{'temperature':0,'num_predict':450,'num_ctx':2048,'num_thread':2}}
        if len(compact(request).encode())>9800:raise ModelTransportError('prompt over budget')
        started=time.monotonic()
        outer=self._json(self.GENERATE,request,cap=32768)
        if outer.get('done') is not True or type(outer.get('response')) is not str:
            raise ModelTransportError('incomplete model response')
        raw=outer['response']
        receipt={'transport':'DIRECT_LOOPBACK_OLLAMA_HTTP','model':self.model,
                 'daemon_advertised_digest':model['daemon_advertised_sha256'],
                 'completed':True,'envelope_valid':False,'input_tokens':outer.get('prompt_eval_count'),
                 'output_tokens':outer.get('eval_count'),'elapsed_seconds':round(time.monotonic()-started,3),
                 'prompt_sha256':hashlib.sha256(compact(request).encode()).hexdigest(),
                 'reply_sha256':hashlib.sha256(raw.encode()).hexdigest(),
                 'dev_feedback_seen':len(feedback),'frozen_cases_visible':False}
        self.calls.append(receipt)
        try:
            value=json.loads(raw)
            if type(value) is not dict or set(value)!={'bindings','expression','rationale'}:raise ValueError('wrong fields')
            reply={'schema':SCHEMA,**value}
            # The evaluator's source-owned validator independently checks binding and expression.
            receipt['envelope_valid']=True
            return reply
        except Exception as exc:
            receipt['error_type']=type(exc).__name__
            raise ModelTransportError('invalid JSON abstraction proposal') from exc
