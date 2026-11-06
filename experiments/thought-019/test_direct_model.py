"""Local HTTP integration tests are transport fixtures, NOT actual pretrained LLM tests.

GitHub Actions has a separate optional real-model job that uses an Ollama model.
"""
from __future__ import annotations
import json
import threading
import unittest
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SIB = HERE.parent / 'thought-018'
if str(SIB) not in sys.path:sys.path.insert(0,str(SIB))
from research_model import PATTERNS
from direct_model import DirectLocalLLM,ModelTransportError,run_direct,digest
from run import cli, DEFAULT_BRIEF

HASH='a'*64

def suggestion(kind):
    return {'expression':deepcopy(PATTERNS[kind]),
            'purpose':'Investigate reversible switch transitions',
            'proposer':'untrusted-test-ollama-generator',
            'on':['red'],'toggles':['red'],
            'reason':'Distinguish a reversible change'}

class Stub(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.record.append(('GET',self.path))
        if self.path!='/api/tags':return self.send_error(404)
        self.write_json({'models':[{'name':'test-llm:0.5b','model':'test-llm:0.5b','digest':HASH}]})
    def do_POST(self):
        length=int(self.headers.get('Content-Length','0'))
        data=json.loads(self.rfile.read(length))
        self.server.record.append(('POST',self.path,data))
        if self.path!='/api/generate':return self.send_error(404)
        model_output=self.server.outputs.pop(0) if self.server.outputs else suggestion('FLIP')
        self.write_json({'model':data['model'],'response':json.dumps(model_output) if isinstance(model_output,dict) else model_output,
                         'done':True,'prompt_eval_count':55,'eval_count':30,'eval_duration':100})
    def write_json(self,body):
        raw=json.dumps(body).encode()
        self.send_response(200)
        self.send_header('content-type','application/json')
        self.send_header('content-length',str(len(raw)))
        self.end_headers();self.wfile.write(raw)
    def log_message(self,*args):pass

class ServerFixture:
    def __init__(self,outputs):
        self.http=ThreadingHTTPServer(('127.0.0.1',0),Stub)
        self.http.outputs=list(outputs)
        self.http.record=[]
        self.thread=threading.Thread(target=self.http.serve_forever,daemon=True)
    def __enter__(self):
        self.thread.start()
        port=self.http.server_port
        class TestModel(DirectLocalLLM):
            TAGS=f'http://127.0.0.1:{port}/api/tags'
            GENERATE=f'http://127.0.0.1:{port}/api/generate'
        self.Model=TestModel
        return self
    def __exit__(self,*args):
        self.http.shutdown();self.http.server_close();self.thread.join(timeout=3)


class DirectLLMTests(unittest.TestCase):
    def test_real_http_round_trip_runs_executable_director_and_produces_audit(self):
        with ServerFixture([suggestion('GROW'),suggestion('FLIP')]) as service:
            import direct_model
            with patch.object(direct_model,'DirectLocalLLM',service.Model):
                out=run_direct('test-llm:0.5b',DEFAULT_BRIEF,rounds=3)
            self.assertEqual(out['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
            self.assertTrue(out['motif_directly_called_llm'])
            self.assertEqual(len(out['model_calls']),2)
            self.assertTrue(all(x['proposal_passed_typed_gate'] for x in out['model_calls']))
            self.assertEqual(out['director_report']['dev_truth_table'],{'passed':64,'total':64})
            self.assertEqual(out['director_report']['frozen_graph_audit'],{'passed':60,'total':60})
            self.assertFalse(out['installed'])
            self.assertEqual(out['external_authority'],'NONE')
            posts=[x[2] for x in service.http.record if x[0]=='POST']
            self.assertEqual(len(posts),2)
            self.assertEqual(posts[0]['model'],'test-llm:0.5b')
            self.assertEqual(posts[1]['stream'],False)
            self.assertIn('REFUTED_ON_DEV',posts[1]['prompt'])
            self.assertNotIn('frozen_audit',posts[1]['prompt'])
            self.assertNotIn('AUDIT',posts[1]['prompt'])

    def test_generator_is_the_model_not_a_replay_file(self):
        with ServerFixture([suggestion('KEEP'),suggestion('GROW')]) as service:
            import direct_model
            with patch.object(direct_model,'DirectLocalLLM',service.Model):
                out=run_direct('test-llm:0.5b',DEFAULT_BRIEF,rounds=2,graph=False)
            self.assertGreaterEqual(len(out['model_calls']),1)
            self.assertEqual(out['transport'],'DIRECT_LOCAL_OLLAMA_NO_FILE_RELAY')
            self.assertNotIn('GPT6_CONVERSATION_RELAY',json.dumps(out))
            self.assertEqual(len([x for x in service.http.record if x[0]=='POST']),2)

    def test_malformed_model_reply_held_but_inference_receipt_survives(self):
        with ServerFixture(['not-a-json']) as service:
            model=service.Model('test-llm:0.5b')
            from director import ResearchDirector
            result,_=ResearchDirector(DEFAULT_BRIEF,model=model,max_rounds=1).run(evaluate_graph=False)
            self.assertEqual(result['status'],'HOLD_NO_VERIFIED_MODEL_PROPOSAL')
            self.assertEqual(len(model.calls),1)
            self.assertFalse(model.calls[0]['proposal_passed_typed_gate'])
            self.assertEqual(len([x for x in service.http.record if x[0]=='POST']),1)
            self.assertEqual(result['external_authority'],'NONE')

    def test_extra_model_fields_and_prompt_injection_never_become_code(self):
        evil={**suggestion('FLIP'),'python':'__import__("os").system("touch /tmp/wont")'}
        with ServerFixture([evil]) as service:
            model=service.Model('test-llm:0.5b')
            with self.assertRaises(ModelTransportError):
                model.propose(DEFAULT_BRIEF)
            self.assertEqual(model.calls[0]['proposal_passed_typed_gate'],False)

    def test_client_enforces_local_only_and_no_cloud(self):
        for s in ['../malicious','http://example.com','x; whoami','model:cloud','']:
            with self.subTest(s=s),self.assertRaises(ModelTransportError):
                DirectLocalLLM(s)
        with self.assertRaises(ModelTransportError):DirectLocalLLM('valid',timeout_seconds=400)

    def test_unknown_local_model_is_not_silently_substituted(self):
        with ServerFixture([]) as service:
            m=service.Model('different:tag')
            with self.assertRaisesRegex(ModelTransportError,'NOT_INSTALLED'):
                m.verify_local_model()
            self.assertEqual(m.calls,[])
            self.assertFalse(any(x[0]=='POST' for x in service.http.record))

    def test_missing_local_endpoint_fails_without_tiny_model_fallback(self):
        class Unbound(DirectLocalLLM):
            TAGS='http://127.0.0.1:9/api/tags'
            GENERATE='http://127.0.0.1:9/api/generate'
        with self.assertRaises(ModelTransportError):Unbound('local:0.5b').verify_local_model()

    def test_input_data_guard_before_http(self):
        with ServerFixture([]) as service:
            m=service.Model('test-llm:0.5b')
            for brief in ('deploy', 'x'*350):
                with self.assertRaises(ModelTransportError):m.propose(brief)
            with self.assertRaises(ModelTransportError):m.propose(DEFAULT_BRIEF,feedback=[{'hidden_audit_cases':'leak'}])
            self.assertEqual(service.http.record,[])

    def test_digest_receipt_recomputable_without_sensitive_prompts(self):
        with ServerFixture([suggestion('FLIP')]) as service:
            import direct_model
            with patch.object(direct_model,'DirectLocalLLM',service.Model):
                out=run_direct('test-llm:0.5b',DEFAULT_BRIEF,rounds=1,graph=False)
            recorded={k:v for k,v in out.items() if k!='receipt_digest'}
            self.assertEqual(digest(recorded),out['receipt_digest'])
            self.assertFalse(out['model_calls'][0]['real_model_identity_verified'])
            self.assertEqual(out['model_fingerprint']['daemon_advertised_sha256'],HASH)

    def test_real_model_status_requires_actual_http_call(self):
        with ServerFixture([]) as service:
            class NoProposals(service.Model):
                def propose(self,brief,feedback=()):return None
            import direct_model
            with patch.object(direct_model,'DirectLocalLLM',NoProposals):
                out=run_direct('test-llm:0.5b',DEFAULT_BRIEF,rounds=1,graph=False)
            self.assertEqual(out['status'],'HOLD_NO_DIRECT_MODEL_CALL')
            self.assertFalse(out['motif_directly_called_llm'])

if __name__=='__main__':unittest.main()
