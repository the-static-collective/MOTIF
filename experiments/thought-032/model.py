"""Opt-in direct local Ollama inference for concept-word proposal and later reuse.

The word is never a hidden program: it expands through concept_language's exact
reviewed grammar. Inference receipts distinguish real HTTP calls from fixtures.
"""
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=str(HERE.parent/'thought-019')
if p not in sys.path:sys.path.insert(0,p)
from direct_model import DirectLocalLLM,ModelTransportError,compact

class DirectConceptLLM(DirectLocalLLM):
    kind='DIRECT_OLLAMA_SHARED_CONCEPT_LANGUAGE'

    def _send(self,phase,packet,pidgin):
        if phase not in ('PREPARE','APPLY') or type(packet) is not dict:
            raise ModelTransportError('invalid research phase')
        common=(
          'You collaborate with MOTIF to describe source-owned symbolic reasoning. '
          'This is a restricted *fictional, finite Boolean set* research environment. '
          'A source-owned example from a scripted fixture is a scoped prior proof, '
          'NOT a proof of a new story. Graph relationships are synthetic declarations, '
          'not evidence about reality. Never invent source IDs, proofs or new capabilities. '
          'Do not write code or give commands. Reply in JSON only. '
        )
        if phase=='PREPARE':
            if pidgin:
                direction=(
                  'OPTIONAL LANGUAGE EXPERIMENT. If a reusable concept is genuinely useful, '
                  'you MAY coin your own 2..16 character word, with an explicit definition. '
                  'Otherwise DECLINE; an unused vocabulary is not a failure. '
                  'Reply EXACT JSON keys choice,definition. choice is coin or decline. '
                  'For coin, definition has EXACT fields: word (your invented word), '
                  'gloss (at least 10 characters), relation (one of DIFFERENCE,INTERSECTION,UNION,SECOND,COMPLEMENT,SYMMETRIC_DIFFERENCE), '
                  'graph_pattern (one of NONE,DEPENDENCY_CHAIN,TENSION_EDGE,ASSOCIATION_BRIDGE), '
                  'proof_gate (DEV_THEN_FROZEN_64), '
                  'uncertainty (TRANSFER_REQUIRES_NEW_EVIDENCE), '
                  'next_experiment (DISCRIMINATING_DEV_QUERIES). '
                  'The word is a transparent name for these components, not a new theorem. '
                  'Example of DECLINING: {"choice":"decline","definition":null}. '
                  'Invent it only if you expect it to be useful in multiple forthcoming reasoning tasks.'
                )
            else:
                direction=(
                  'BASELINE WARMUP: inspect the same scoped prior proof and graph context; '
                  'no invented vocabulary is available. Reply EXACT JSON '
                  '{"choice":"baseline","definition":null}. '
                  'Do not assume the next task has the same roles or policy.'
                )
        else:
            direction=(
              'NEW TRANSFER TASK. Infer roles from the human story, not field order. '
              'Return JSON EXACT keys bindings,word,relation,evidence_refs,rationale. '
              'bindings MUST have current,event as distinct exact field IDs from the task. '
              'You may use one previously defined word ONLY if it appears in the supplied concept book '
              'and its meaning fits this task: set word to that exact string, relation to null. '
              'Otherwise use word=null and relation one of DIFFERENCE,INTERSECTION,UNION,SECOND,COMPLEMENT,SYMMETRIC_DIFFERENCE. '
              'DIFFERENCE is current minus event, INTERSECTION is both, UNION either, '
              'SECOND event only, COMPLEMENT is universe except current, '
              'SYMMETRIC_DIFFERENCE is exactly one of current or event. '
              'evidence_refs is an array containing only the exact available prior proof digest '
              'if you refer to it (or []); prior evidence is not new-task proof. '
              'rationale explains your hypothesis in 8-240 characters. '
              'Do NOT assert that a language word is a theorem. '
              'Your final hypothesis is tested independently AFTER this response.'
            )
        prompt=common+direction+'\nPACKET_JSON='+compact(packet)
        if len(prompt)>15000:raise ModelTransportError('model prompt budget exceeded')
        meta=self.verify_local_model()
        request={'model':self.model,'prompt':prompt,'stream':False,'format':'json',
                 'options':{'temperature':0,'num_predict':450,'num_ctx':4500,'num_thread':2}}
        start=time.monotonic()
        outer=self._json(self.GENERATE,request,cap=32768)
        if outer.get('done') is not True or type(outer.get('response')) is not str:
            raise ModelTransportError('model generation incomplete')
        raw=outer['response']
        receipt={'phase':phase,'transport':'DIRECT_LOOPBACK_OLLAMA_HTTP',
           'http_generation_completed':True,'model':self.model,
           'self_reported_daemon_digest':meta['daemon_advertised_sha256'],
           'prompt_sha256':hashlib.sha256(compact(request).encode()).hexdigest(),
           'reply_sha256':hashlib.sha256(raw.encode()).hexdigest(),
           'prompt_tokens':outer.get('prompt_eval_count'),
           'output_tokens':outer.get('eval_count'),
           'seconds':round(time.monotonic()-start,3),'parsed_as_json':False,
           'hidden_oracle_exposed':False,'code_from_model_executed':False}
        self.calls.append(receipt)
        try:
            data=json.loads(raw)
            if type(data) is not dict:raise ValueError('JSON object required')
            receipt['parsed_as_json']=True
            receipt['reply_fields']=sorted(data)[:12]
            return data
        except Exception as exc:
            receipt['parse_error']=type(exc).__name__
            raise ModelTransportError('invalid structured model output') from exc

    def prepare(self,context,pidgin_enabled):
        return self._send('PREPARE',{'context':context},pidgin_enabled)
    def apply(self,task,context,concept_book,pidgin_enabled):
        return self._send('APPLY',{'task':task,'context':context,'concept_book':concept_book},pidgin_enabled)
