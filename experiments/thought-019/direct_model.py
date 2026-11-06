"""THOUGHT-019: MOTIF itself calls a local generative LLM each round.

The model can only propose typed test mechanisms. MOTIF's THOUGHT-018 director
chooses a discriminating question and THOUGHT-017 independently evaluates.
No replay file, hidden tiny-model fallback, auto-installation, remote API,
or model-origin executable Python is accepted.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from copy import deepcopy
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

HERE = Path(__file__).resolve().parent
SIBLING = HERE.parent / 'thought-018'
if str(SIBLING) not in sys.path:
    sys.path.insert(0, str(SIBLING))
from research_model import MODEL_SCHEMA, validate_model_reply  # source-owned contract
from program import SCHEMA  # THOUGHT-018 binds the original THOUGHT-017 typed compiler


class ModelTransportError(ValueError):
    pass


class RefuseRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ModelTransportError('MODEL_REDIRECT_REFUSED')


def compact(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False, ensure_ascii=True)


def digest(obj):
    return hashlib.sha256(compact(obj).encode('ascii')).hexdigest()


def _read_bytes(response, cap):
    data = response.read(cap + 1)
    if len(data) > cap:
        raise ModelTransportError('MODEL_OUTPUT_TOO_LARGE')
    return data


class DirectLocalLLM:
    """An operator chooses one preinstalled Ollama model. Endpoint is fixed.

    Class attribute URLs permit loopback transport tests in a dedicated subclass;
    the public CLI never accepts an endpoint, URL, files or environment URL.
    
    The digest returned by Ollama is a daemon-reported model fingerprint,
    NOT a verified signature or proof that the daemon is trustworthy.
    """
    kind = 'OPT_IN_LOCAL_GENERATIVE_MODEL'
    TAGS = 'http://127.0.0.1:11434/api/tags'
    GENERATE = 'http://127.0.0.1:11434/api/generate'
    def __init__(self, model: str, *, timeout_seconds=90):
        if type(model) is not str or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,64}', model):
            raise ModelTransportError('EXPLICIT_LOCAL_MODEL_NAME_REQUIRED')
        if model.endswith(':cloud'):
            raise ModelTransportError('CLOUD_MODELS_REFUSED')
        if type(timeout_seconds) not in (float, int) or not 3 <= timeout_seconds <= 180:
            raise ModelTransportError('MODEL_TIMEOUT_OUTSIDE_BUDGET')
        self.model = model
        self.timeout = float(timeout_seconds)
        self.calls = []
        self._model_meta = None
        self._opener = build_opener(ProxyHandler({}), RefuseRedirect())

    def _json(self, url, payload=None, *, cap=16384, timeout=None):
        headers = {'Accept': 'application/json'}
        if payload is None:
            request = Request(url, headers=headers, method='GET')
        else:
            headers['Content-Type'] = 'application/json'
            request = Request(url, headers=headers, method='POST', data=compact(payload).encode())
        try:
            with self._opener.open(request, timeout=timeout or self.timeout) as response:
                content_type = response.headers.get('content-type', '').lower()
                if not content_type.startswith('application/json'):
                    raise ModelTransportError('MODEL_CONTENT_TYPE_REFUSED')
                raw = _read_bytes(response, cap)
        except ModelTransportError:
            raise
        except Exception as exc:
            raise ModelTransportError('LOCAL_MODEL_TRANSPORT_UNAVAILABLE') from exc
        try:
            response_obj = json.loads(raw)
        except (ValueError, TypeError) as exc:
            raise ModelTransportError('MODEL_OUTER_JSON_INVALID') from exc
        if type(response_obj) is not dict:
            raise ModelTransportError('MODEL_OUTER_SHAPE_INVALID')
        return response_obj

    def verify_local_model(self):
        """Check local daemon's advertised identity once, without requesting inference."""
        if self._model_meta is not None:
            return deepcopy(self._model_meta)
        listed = self._json(self.TAGS, cap=64_000, timeout=10)
        models = listed.get('models')
        if type(models) is not list or len(models) > 300:
            raise ModelTransportError('MODEL_REGISTRY_INVALID')
        match = next((m for m in models if type(m) is dict and
                      self.model in (m.get('name'), m.get('model'))), None)
        if match is None:
            raise ModelTransportError('MODEL_NOT_INSTALLED_LOCALLY')
        supplied_digest = match.get('digest')
        if type(supplied_digest) is not str or not re.fullmatch(r'[a-fA-F0-9]{64}',supplied_digest):
            raise ModelTransportError('MODEL_DIGEST_MISSING')
        self._model_meta = {'requested_name': self.model,
                            'daemon_advertised_name': match.get('name'),
                            'daemon_advertised_sha256': supplied_digest.lower(),
                            'fingerprint_provenance':'SELF_REPORTED_BY_LOCAL_DAEMON_NOT_SIGNED'}
        return deepcopy(self._model_meta)

    def _instruction(self, brief, feedback):
        if type(brief) is not str or not 8 <= len(brief) <= 300 or type(feedback) not in (tuple,list) or len(feedback)>6:
            raise ModelTransportError('OUT_OF_BOUNDS_RESEARCH_CONTEXT')
        # Include *only development* observations. Audit & stress cases and
        # their labels NEVER appear in this model prompt.
        safe=[]
        for item in feedback:
            if type(item) is not dict or set(item)-{
                'mechanism','observed_result','oracle_expected','disposition',
                'on_mask','toggles_mask','surviving_mechanisms'}:
                raise ModelTransportError('UNEXPECTED_FEEDBACK_FIELDS')
            safe.append({'your_candidate_name':str(item.get('mechanism'))[:35],
                         'developer_test_actual':item.get('observed_result'),
                         'developer_oracle_expected':item.get('oracle_expected'),
                         'disposition':item.get('disposition')})
        # This is data-only and contains no evaluator target or frozen tasks.
        task = compact({'brief':brief,'development_only_feedback':safe})
        system = (
            'You are a research model supplying ONE candidate typed set-transition '
            'mechanism and ONE diagnostic probe. Your output is DATA for a separate '
            'evaluator; you cannot assert authority. Produce only a JSON object '
            'with exactly 6 keys: expression, purpose, proposer, on, toggles, reason. '
            'expression is recursively one of {"ref":"state.on"}, '
            '{"ref":"arrival.toggles"}, or {"op":"union"|"difference",'
            '"args":[expression,expression]}. Make no other operators. '
            'on and toggles are arrays containing distinct colors from red, blue, green. '
            'purpose, proposer, reason must be short plain text. '
            'Your expression should model the task, NOT replay a previous guess. '
            'No Python, shell, URLs, external actions, fake test results or credentials. '
            'Return strictly JSON; unknown results are acceptable.'
        )
        return system + '\nTASK AS JSON DATA: ' + task

    def propose(self, brief: str, feedback=()):
        """True direct MOTIF -> Ollama HTTP inference, at most one per round."""
        # Fail closed before any HTTP request on malformed inputs.
        prompt=self._instruction(brief,feedback)
        meta=self.verify_local_model()
        body={'model': self.model, 'prompt': prompt, 'stream': False,
              'format':'json', 'options': {'temperature':0, 'num_predict':420,
                                          'num_ctx':2048, 'num_thread':2}}
        payload=compact(body).encode()
        if len(payload)>8192:
            raise ModelTransportError('MODEL_PROMPT_BUDGET_EXCEEDED')
        started=time.monotonic()
        try:
            reply=self._json(self.GENERATE,body,cap=32_768)
            elapsed=round(time.monotonic()-started,3)
            # Transport confirmation even if the model's reply is malformed:
            # no synthetic fallback may turn a bad response into a success.
            if reply.get('done') is not True or type(reply.get('response')) is not str:
                raise ModelTransportError('INCOMPLETE_MODEL_GENERATION')
            model_text=reply['response']
            if len(model_text)>10_000:
                raise ModelTransportError('MODEL_TEXT_TOO_LONG')
            # A real model call is recorded before treating its suggestion as
            # valid. Even malformed JSON is still an observed model execution.
            receipt={'round':len(self.calls)+1,
                 'transport':'DIRECT_LOOPBACK_OLLAMA_HTTP',
                 'http_generation_completed':True,
                 'proposal_passed_typed_gate':False,
                 'real_model_identity_verified':False,
                 'model_tag':self.model,'daemon_digest':meta['daemon_advertised_sha256'],
                 'prompt_sha256':hashlib.sha256(payload).hexdigest(),
                 'reply_sha256':hashlib.sha256(model_text.encode()).hexdigest(),
                 'elapsed_seconds':elapsed,
                 'prompt_eval_count':reply.get('prompt_eval_count'),
                 'eval_count':reply.get('eval_count'),
                 'eval_duration_ns':reply.get('eval_duration'),
                 'model_claimed_by_server':reply.get('model'),
                 'developer_feedback_visible_count':len(feedback),
                 'model_can_access_frozen_audit':False}
            self.calls.append(receipt)
            model_json=json.loads(model_text)
            if type(model_json) is not dict or set(model_json)!={
                'expression','purpose','proposer','on','toggles','reason'}:
                raise ModelTransportError('MODEL_PROPOSAL_FIELDS_INVALID')
            untrusted={'schema':MODEL_SCHEMA,
                'mechanism':{'schema':SCHEMA,'expression':model_json['expression'],
                             'purpose':model_json['purpose'],'proposer':model_json['proposer']},
                'suggested_test':{'on':model_json['on'],'toggles':model_json['toggles'],
                                  'reason':model_json['reason']},
                'model_kind':self.kind,'declared_name':None}
            checked_mechanism,checked_probe=validate_model_reply(untrusted)
            receipt['proposal_passed_typed_gate']=True
            return {'schema':MODEL_SCHEMA,'mechanism':checked_mechanism,
                    'suggested_test':checked_probe,
                    'model_kind':self.kind,'declared_name':None}
        except ModelTransportError:
            raise
        except (ValueError,TypeError,KeyError) as exc:
            raise ModelTransportError('MODEL_JSON_OR_TYPED_PROPOSAL_INVALID') from exc


def run_direct(model, brief, *, rounds=3, timeout=90, graph=True):
    from director import ResearchDirector
    worker=DirectLocalLLM(model,timeout_seconds=timeout)
    verified=worker.verify_local_model()  # absence -> HOLD, no fallback
    result,candidate=ResearchDirector(brief,model=worker,max_rounds=rounds).run(evaluate_graph=graph)
    # No inference -> hard HOLD even if other program components somehow succeeded.
    if not worker.calls:
        result['status']='HOLD_NO_DIRECT_MODEL_CALL'
    result['local_ollama_http_calls']=len(worker.calls)
    # Distinguish the model tag verified at daemon vs actual typed inference.
    report={'schema':'motif.thought019.direct-research.v1',
       'status':result['status'],'transport':'DIRECT_LOCAL_OLLAMA_NO_FILE_RELAY',
       'motif_directly_called_llm':len(worker.calls)>0,
       'model_tag':model,'model_fingerprint':verified,
       'model_calls':deepcopy(worker.calls),
       'director_report':result,
       'candidate':candidate,
       'installed':False,'externally_sent':False,'pen_unchanged':True,
       'external_authority':'NONE',
       'limitations':'Real local generative inference, if calls>0. Synthetic author-designed tasks; no model originality proof, OS sandbox, signed model identity, external system writes or self-certifying evaluator.'}
    report['receipt_digest']=digest(report)
    return report
