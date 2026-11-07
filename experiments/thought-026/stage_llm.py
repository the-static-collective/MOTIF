"""Direct Ollama proposer for three separately inspectable abstraction stages.

Three possible actual HTTP calls: role grounding, relationship discovery and
optional bounded repair. Source-owned compiler and independent evaluator follow.
Model has no tools, secret, candidate source execution or arbitrary endpoints.
"""
from __future__ import annotations
import sys,json,time,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=str(HERE.parent/'thought-019')
if p not in sys.path:sys.path.insert(0,p)
from direct_model import DirectLocalLLM, ModelTransportError, compact
from stages import RELATIONS

class DirectStageLLM(DirectLocalLLM):
    kind='DIRECT_LOCAL_LLM_STAGED_ABSTRACTION'

    def _query(self,stage,public_task,context,fields,format_schema):
        if stage not in ('GROUND_FIELDS','DISCOVER_RELATION','REPAIR'):
            raise ModelTransportError('unknown model stage')
        ids=[x['id'] for x in public_task['input_fields']]
        if type(ids) is not list or len(ids)!=2 or any(type(x) is not str or not 1<=len(x)<=50 for x in ids) or ids[0]==ids[1]:
            raise ModelTransportError('invalid task field names')
        if len(compact(context))>2200:raise ModelTransportError('development-only feedback too large')
        schema={'type':'object','properties':format_schema,'required':fields,'additionalProperties':False}
        rules=('All inputs are fictional three-flag sets; do not perform real actions. '
               'Return exactly the requested JSON, no markdown or Python. '
               'The field identifiers are opaque and their descriptions matter. '
               'Never invent fields, test outcomes or claims of success. '
               'Your output is an untrusted hypothesis for independent evaluation. '
               'Do NOT assume the first input field is always the primary set. ')
        if stage=='GROUND_FIELDS':
            rules+=('GROUND FIELDS ONLY. Determine which input field is primary (current) and '
                    'which is comparison/update (event), based on the story. '
                    'bindings.current and bindings.event must be distinct exact field IDs. '
                    'You do not choose a mathematical operation at this stage. ')
        elif stage=='DISCOVER_RELATION':
            rules+=('DISCOVER THE MATHEMATICAL RELATION based on the human story and proposed role bindings. '
                    'Choose exactly ONE of DIFFERENCE (primary except comparison), '
                    'INTERSECTION (both), UNION (either), SECOND (comparison only), '
                    'COMPLEMENT (universe except primary), SYMMETRIC_DIFFERENCE (exclusive membership). '
                    'Do not output an AST or change input bindings. ')
        else:
            rules+=('REPAIR after development counterexamples. Reconsider BOTH field binding and relation. '
                    'The observations list concrete input masks and independently measured outputs; '
                    'these are NOT frozen audit cases. Determine a consistent hypothesis. '
                    'Do not simply repeat a refuted candidate. You must choose a relation from: '
                    +', '.join(RELATIONS)+'. Diagnosis describes POSSIBLE error classes, not a correct answer. ')
        prompt=rules+'\nSTAGE='+stage+'\nTASK_JSON_DATA='+compact({'task':public_task,'development_context':context})
        meta=self.verify_local_model()
        payload={'model':self.model,'prompt':prompt,'stream':False,'format':schema,
                 'options':{'temperature':0,'num_predict':360,'num_ctx':2048,'num_thread':2}}
        if len(compact(payload).encode())>11500:raise ModelTransportError('model input exceeds bound')
        start=time.monotonic()
        reply=self._json(self.GENERATE,payload,cap=32768)
        if reply.get('done') is not True or type(reply.get('response')) is not str:
            raise ModelTransportError('incomplete model generation')
        raw=reply['response'];elapsed=round(time.monotonic()-start,3)
        item={'stage':stage,'model':self.model,'daemon_sha256_advertised':meta['daemon_advertised_sha256'],
              'transport':'DIRECT_LOOPBACK_OLLAMA_HTTP','http_generation_completed':True,
              'prompt_sha256':hashlib.sha256(compact(payload).encode()).hexdigest(),
              'reply_sha256':hashlib.sha256(raw.encode()).hexdigest(),
              'input_tokens':reply.get('prompt_eval_count'),'output_tokens':reply.get('eval_count'),
              'elapsed_seconds':elapsed,'dev_context_only':True,'frozen_audit_exposed':False,
              'typed_envelope_valid':False,'identity_verified_cryptographically':False}
        self.calls.append(item)
        try:
            value=json.loads(raw)
            if type(value) is not dict or set(value)!=set(fields):raise ValueError('invalid stage reply fields')
            item['typed_envelope_valid']=True
            return value
        except Exception as e:
            item['validation_error']=type(e).__name__
            raise ModelTransportError('invalid staged model response') from e

    @staticmethod
    def _binding_schema(ids):
        return {'type':'object','properties':{
                  'current':{'type':'string','enum':ids},'event':{'type':'string','enum':ids}},
                'required':['current','event'],'additionalProperties':False}

    def bind(self,task):
        ids=[x['id'] for x in task['input_fields']]
        props={'bindings':self._binding_schema(ids),
               'rationale':{'type':'string','minLength':8,'maxLength':240}}
        return self._query('GROUND_FIELDS',task,{},['bindings','rationale'],props)

    def relate(self,task,binding):
        props={'relation':{'type':'string','enum':list(RELATIONS)},
               'rationale':{'type':'string','minLength':8,'maxLength':240}}
        return self._query('DISCOVER_RELATION',task,{'proposed_binding':binding},
                           ['relation','rationale'],props)

    def repair(self,task,binding,relationship,witnesses,diagnosis):
        if type(witnesses) not in (list,tuple) or not 1<=len(witnesses)<=4:
            raise ModelTransportError('bounded witness list required')
        ids=[x['id'] for x in task['input_fields']]
        for x in witnesses:
            if type(x) is not dict or set(x)!={'inputs','observed','predicted','passed'} or \
               type(x['inputs']) is not dict or set(x['inputs'])!=set(ids) or \
               any(type(v) is not int or not 0<=v<=7 for v in [*x['inputs'].values(),x['observed'],x['predicted']]) or type(x['passed']) is not bool:
                raise ModelTransportError('non-dev or invalid witness refused')
        if type(diagnosis) is not dict or set(diagnosis)!={
            'surviving_hypothesis_pairs','role_only_possible','relationship_only_possible',
            'joint_change_possible','roles_observationally_indistinguishable_on_dev',
            'evidence','correct_relation_disclosed','correct_role_binding_disclosed'}:
            raise ModelTransportError('unexpected diagnosis fields')
        properties={'binding':{'type':'object','properties':{
                           'bindings':self._binding_schema(ids),
                           'rationale':{'type':'string','minLength':8,'maxLength':240}},
                           'required':['bindings','rationale'],'additionalProperties':False},
                    'relationship':{'type':'object','properties':{
                            'relation':{'type':'string','enum':list(RELATIONS)},
                            'rationale':{'type':'string','minLength':8,'maxLength':240}},
                            'required':['relation','rationale'],'additionalProperties':False}}
        # Never include source-owner policy or ground-truth roles in feedback.
        context={'previous_binding':binding,'previous_relation':relationship,
                 'development_observations':list(witnesses),
                 'diagnosis':diagnosis}
        return self._query('REPAIR',task,context,['binding','relationship'],properties)
