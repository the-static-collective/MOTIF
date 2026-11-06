"""Optional real local LLM proposer. Does not allow arbitrary URLs, file I/O or code."""
from __future__ import annotations
import json,re
from urllib.request import Request,build_opener,ProxyHandler,HTTPRedirectHandler
from program import SCHEMA,validate_proposal,ProposalError

class ModelUnavailable(ValueError):pass
class DenyRedirect(HTTPRedirectHandler):
    def redirect_request(self,*_args):raise ModelUnavailable('model redirect blocked')

class OllamaMacroProposer:
    endpoint='http://127.0.0.1:11434/api/generate'
    def __init__(self,model):
        if type(model) is not str or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,64}',model):
            raise ModelUnavailable('operator must specify a valid installed model')
        self.model=model
    def propose(self,feedback=()):
        # No development labels or audit specimens in prompt. Operator can opt in.
        if type(feedback) not in (tuple,list) or len(feedback)>3:
            raise ModelUnavailable('feedback bound exceeded')
        instruction=(
          'Design a code-free typed AST for switches that FLIP their on/off state '
          'when a traveler arrives. The existing monotone union rule cannot turn switches off. '
          'Available refs are state.on and arrival.toggles (both sets). '
          'Available binary ops are union and difference. Create a NEW macro '
          'out of these primitives that computes exact toggled-state update. '
          'Return a JSON object with EXACT keys expression,purpose,proposer. '
          'expression nodes are {"ref":"state.on"} or {"ref":"arrival.toggles"}, '
          'or {"op":"union"|"difference","args":[node,node]}. '
          'No code, no commands, no new refs, no tests/labels/claims of success. '
          'If unsure return invalid proposal and let evaluator HOLD. '
          'Previous feedback: '+json.dumps(list(feedback),ensure_ascii=True) )
        body=json.dumps({'model':self.model,'prompt':instruction,'stream':False,
                         'format':'json','options':{'temperature':0,'num_predict':256}}).encode()
        if len(body)>8192:raise ModelUnavailable('prompt too large')
        req=Request(self.endpoint,data=body,method='POST',headers={'Content-Type':'application/json'})
        try:
            with build_opener(ProxyHandler({}),DenyRedirect()).open(req,timeout=4) as resp:
                raw=resp.read(16385)
        except Exception as exc:raise ModelUnavailable('local LLM unavailable or failed') from exc
        if len(raw)>16384:raise ModelUnavailable('local model exceeded output limit')
        try:
            response=json.loads(json.loads(raw)['response'])
        except (ValueError,KeyError,TypeError) as exc:raise ModelUnavailable('local model returned invalid JSON') from exc
        if type(response) is not dict or set(response)!={'expression','purpose','proposer'}:
            raise ModelUnavailable('local model returned fields outside proposal contract')
        response['schema']=SCHEMA
        try:return validate_proposal(response)
        except ProposalError as exc:raise ModelUnavailable('local model proposal violates typed contract') from exc
