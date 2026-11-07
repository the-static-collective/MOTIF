"""Opt-in direct Ollama model translates cross-domain language into a generic set AST.

The model is not allowed to supply test answers, Python, URLs or execution.
Generic IR has no switch-specific identifiers; a SOURCE-OWNED adapter translates
it to the 023 grammar, which is subsequently checked by separate task oracle.
"""
from __future__ import annotations
import hashlib,json,sys,time
from copy import deepcopy
from pathlib import Path
HERE=Path(__file__).resolve().parent
for n in ('thought-019','thought-023'):
    p=str(HERE.parent/n)
    if p not in sys.path:sys.path.insert(0,p)
from direct_model import DirectLocalLLM,ModelTransportError,compact
from grammar import validate_expression, GrammarError

SCHEMA='motif.thought024.generic-set-expression.v1'
REF_MAP={'current':'state.on','event':'arrival.toggles','universe':'universe'}


def validate_generic(expression,depth=0,counter=None):
    if counter is None:counter=[0]
    counter[0]+=1
    if counter[0]>19 or depth>4 or type(expression) is not dict:
        raise ValueError('expression depth or node bound exceeded')
    if set(expression)=={'ref'} and type(expression['ref']) is str and expression['ref'] in REF_MAP:
        return {'ref':REF_MAP[expression['ref']]}
    if set(expression)=={'op','args'} and expression['op'] in ('union','difference') and \
        type(expression['args']) is list and len(expression['args'])==2:
        return {'op':expression['op'],'args':[validate_generic(x,depth+1,counter) for x in expression['args']]}
    raise ValueError('unknown generic expression shape or operation')


def translate_reply(reply):
    if type(reply) is not dict or set(reply)!={'expression','reason'} or \
       type(reply['reason']) is not str or not 8<=len(reply['reason'])<=200:
        raise ValueError('invalid model proposal fields')
    expr=validate_generic(reply['expression'])
    return {'expression':validate_expression(expr,'universe_constant'),
            'reason':reply['reason']}


def to_generic(source):
    reverse={v:k for k,v in REF_MAP.items()}
    if 'ref' in source:return {'ref':reverse[source['ref']]}
    return {'op':source['op'],'args':[to_generic(x) for x in source['args']]}


class DirectTransferLLM(DirectLocalLLM):
    kind='DIRECT_LOCAL_LLM_CROSS_DOMAIN_TRANSLATOR'

    def _instruction(self,brief,feedback):
        if type(brief) is not str or not 20<=len(brief)<=750 or \
            type(feedback) not in (tuple,list) or len(feedback)>2:
            raise ModelTransportError('invalid bounded task context')
        checked=[]
        for f in feedback:
            if type(f) is not dict or set(f)!={'a','b','predicted','observed'} or \
                any(type(v) is not int or not 0<=v<=7 for v in f.values()):
                raise ModelTransportError('invalid development-only feedback')
            checked.append(f)
        system=(
          'You propose one PURE mathematical expression for a described transformation of 3 category flags. '
          'You do not write code and you are not the evaluator. Return exact JSON with two keys: expression, reason. '
          'The expression is a tree with exactly these shapes: '
          '{"ref":"current"}, {"ref":"event"}, {"ref":"universe"}, '
          'or {"op":"union","args":[expression,expression]}, '
          'or {"op":"difference","args":[expression,expression]}. '
          'The universe means all three abstract categories; current means the present set; '
          'event means the second supplied set. Do not assume a domain involves switches. '
          'Translate the user-described semantics faithfully; some tasks are not expressible. '
          'No other operators, variables, assertions, permission changes or invented test results. '
          'A program will independently assess your expression on unseen inputs. '
          'Supply a short explanation in reason, >=12 characters. '
          'An example of the required STRUCTURE ONLY (not the intended answer) is '
          '{"expression":{"op":"union","args":[{"ref":"current"},{"ref":"event"}]},'
          '"reason":"This sample represents the union of two sets."}. '
          'Prior observations, if any, are only developer-test examples; they are not hidden audits.'
        )
        return system + '\nTASK_DATA_JSON=' + compact({'brief':brief,'development_feedback':checked})

    def propose(self,brief,feedback=()):
        prompt=self._instruction(brief,feedback)
        meta=self.verify_local_model()
        schema={'type':'object','properties':{'expression':{'type':'object'},
                       'reason':{'type':'string','minLength':12,'maxLength':200}},
                'required':['expression','reason'],'additionalProperties':False}
        body={'model':self.model,'prompt':prompt,'stream':False,'format':schema,
              'options':{'temperature':0,'num_predict':380,'num_ctx':2048,'num_thread':2}}
        if len(compact(body).encode())>9600:raise ModelTransportError('bounded model context exceeded')
        started=time.monotonic()
        reply=self._json(self.GENERATE,body,cap=32768)
        if reply.get('done') is not True or type(reply.get('response')) is not str:
            raise ModelTransportError('model generation incomplete')
        raw=reply['response']
        receipt={'transport':'DIRECT_LOOPBACK_OLLAMA_HTTP','http_generation_completed':True,
                 'model':self.model,'daemon_digest':meta['daemon_advertised_sha256'],
                 'round':len(self.calls)+1,'prompt_sha256':hashlib.sha256(compact(body).encode()).hexdigest(),
                 'reply_sha256':hashlib.sha256(raw.encode()).hexdigest(),
                 'elapsed_seconds':round(time.monotonic()-started,3),
                 'input_tokens':reply.get('prompt_eval_count'),
                 'output_tokens':reply.get('eval_count'),
                 'feedback_count':len(feedback),'typed_valid':False,
                 'model_identity_cryptographically_verified':False}
        self.calls.append(receipt)
        try:
            checked=translate_reply(json.loads(raw))
            receipt['typed_valid']=True
            return checked
        except Exception as exc:
            receipt['failure']=type(exc).__name__
            raise ModelTransportError('model returned invalid generic typed expression') from exc
