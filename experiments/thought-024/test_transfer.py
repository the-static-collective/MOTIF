"""Adversarial cross-domain controls, strict generic IR, and direct HTTP fixture.

Synthetic fixtures are not independent real-world validation or real LLM inference.
"""
from __future__ import annotations
import copy,json,threading,unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from tasks import TASKS,BY_KEY,Task,oracle
from transfer import (classical_trial,model_trial,exhaustive,offline_report,
                      expression_mask,DEV_PROBES,task_gate)
from transfer_llm import (validate_generic,translate_reply,to_generic,DirectTransferLLM)
from grammar import ref,op,validate_expression,enumerate_language

REVERSE={'op':'difference','args':[{'ref':'universe'},{'ref':'current'}]}
REVOKE={'op':'difference','args':[{'ref':'current'},{'ref':'event'}]}
INTERSECT={'op':'difference','args':[{'ref':'current'},
                     {'op':'difference','args':[{'ref':'current'},{'ref':'event'}]}]}

class FakeProposer:
    kind='SYNTHETIC_NOT_LLM'
    def __init__(self, expressions):self.expressions=list(expressions);self.calls=[]
    def propose(self,brief,feedback=()):
        self.calls.append({'brief':brief,'feedback':copy.deepcopy(feedback)})
        generic=self.expressions[min(len(self.calls)-1,len(self.expressions)-1)]
        return translate_reply({'expression':generic,'reason':'Synthetic proposal from fixture'})

class TransferTest(unittest.TestCase):
    def test_four_unseen_surface_domains_old_inadequate_new_succeeds(self):
        for key in ('permits_reverse','missing_supplies','not_endorsed','unblocked_access'):
            task=BY_KEY[key]
            with self.subTest(task=key):
                a=classical_trial(task,'none');b=classical_trial(task,'universe_constant')
                self.assertEqual(a['status'],'HOLD_GRAMMAR_INADEQUATE')
                self.assertEqual(a['oracle_calls'],1)
                self.assertEqual(b['status'],'REVIEW_CANDIDATE_NOT_INSTALLED')
                self.assertEqual(b['frozen_correct'],64)
                self.assertLessEqual(b['oracle_calls'],6)
                self.assertEqual(exhaustive(task,b['selected_expression'],'universe_constant')['passed'],64)
    def test_existing_grammar_still_handles_old_domain_controls(self):
        for key in ('expire_names','inventory_eligible','shift_override','renew_flip','add_donations'):
            with self.subTest(key=key):
                b=classical_trial(BY_KEY[key],'none')
                self.assertEqual(b['status'],'REVIEW_CANDIDATE_NOT_INSTALLED')
                self.assertEqual(b['frozen_correct'],64)
    def test_cross_category_dependency_cannot_be_expressed(self):
        t=BY_KEY['cross_category_threshold']
        for ext in ('none','universe_constant'):
            r=classical_trial(t,ext)
            self.assertTrue(r['status'].startswith('HOLD_'))
            self.assertNotEqual(r['frozen_correct'],64)
        self.assertEqual(oracle(t,3,0),7)
        self.assertEqual(oracle(t,1,0),0)
    def test_ternary_beliefs_held_before_binary_encoding(self):
        task=BY_KEY['open_world_truth']
        self.assertEqual(classical_trial(task,'universe_constant')['status'],'HOLD_NON_BOOLEAN_DOMAIN_MISMATCH')
        model=FakeProposer([REVERSE]);r=model_trial(task,model)
        self.assertEqual(r['status'],'HOLD_NON_BOOLEAN_DOMAIN_MISMATCH')
        self.assertEqual(model.calls,[])
    def test_generic_ast_refuses_unsafe_and_unlicensed_fields(self):
        for x in ({'ref':'__import__'}, {'op':'exec','args':[]},
                  {'op':'union','args':[{'ref':'current'}]},
                  {'op':'difference','args':[{'ref':'current'}, {'ref':'event'}],'python':'shell'},
                  {'ref':'current','eval':1}, {'ref':1}):
            with self.subTest(x=x), self.assertRaises(ValueError):validate_generic(x)
    def test_generic_translation_has_no_domain_specific_string_matching(self):
        translated=translate_reply({'expression':REVERSE,'reason':'Reverse membership in each category'})
        self.assertEqual(translated['expression'],op('difference',ref('universe'),ref('state.on')))
        self.assertEqual(to_generic(translated['expression']),REVERSE)
        for task in [BY_KEY['permits_reverse'],BY_KEY['not_endorsed']]:
            self.assertEqual(exhaustive(task,translated['expression'],'universe_constant')['passed'],64)
    def test_model_needs_evidence_not_confident_text(self):
        task=BY_KEY['permits_reverse']
        model=FakeProposer([{'ref':'current'},REVERSE])
        report=model_trial(task,model,max_calls=2)
        self.assertEqual(report['status'],'CANDIDATE_FOR_REVIEW_NOT_INSTALLED')
        self.assertEqual(report['model_calls'],2)
        self.assertEqual(report['executable_correct'],64)
        self.assertEqual(len(model.calls[1]['feedback']),1)
        self.assertEqual(set(model.calls[1]['feedback'][0]),{'a','b','predicted','observed'})
        self.assertNotIn('frozen',json.dumps(model.calls))
    def test_bad_model_replay_stays_held(self):
        report=model_trial(BY_KEY['permits_reverse'],FakeProposer([{'ref':'current'}]),max_calls=2)
        self.assertEqual(report['status'],'HOLD_NO_DEV_CONSISTENT_MODEL_PROPOSAL')
        self.assertIsNone(report['frozen_correct'])
    def test_bad_candidate_does_not_get_installed(self):
        class Invalid:
            calls=[]
            def propose(self,*args):return {'expression':{'ref':'universe'},'reason':'oops','python':'open(0)'}
        report=model_trial(BY_KEY['permits_reverse'],Invalid())
        self.assertEqual(report['status'],'HOLD_NO_DEV_CONSISTENT_MODEL_PROPOSAL')
        self.assertFalse(report['installed'])
    def test_old_and_new_catalog_exactly_bound_semantics(self):
        a=enumerate_language('none');b=enumerate_language('universe_constant')
        self.assertEqual((len(a),len(b)),(8,16))
        self.assertTrue({tuple(x['signature']) for x in a} <= {tuple(x['signature']) for x in b})
    def test_offline_report_cannot_claim_real_llm(self):
        x=offline_report([BY_KEY['permits_reverse'],BY_KEY['open_world_truth']])
        self.assertFalse(x['model_called']);self.assertTrue(x['domain_adapter_is_predefined_by_developer'])
        self.assertEqual(x['expanded_grammar_size'],16)
        self.assertFalse(x['installed'])
    def test_nonliteral_boolean_type_refused(self):
        with self.assertRaises(ValueError):oracle(BY_KEY['missing_supplies'],True,2)
        with self.assertRaises(ValueError):oracle(BY_KEY['missing_supplies'],8,2)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.log.append(('GET',self.path))
        if self.path!='/api/tags':return self.send_error(404)
        self.send_obj({'models':[{'name':'transfer-test:1b','model':'transfer-test:1b','digest':'a'*64}]})
    def do_POST(self):
        n=int(self.headers['content-length'])
        req=json.loads(self.rfile.read(n))
        self.server.log.append(('POST',self.path,req))
        output=self.server.replies.pop(0) if self.server.replies else {'expression':REVERSE,'reason':'Finite reverse control'}
        self.send_obj({'done':True,'model':req['model'],'response':json.dumps(output),
                       'prompt_eval_count':200,'eval_count':50})
    def send_obj(self,obj):
        data=json.dumps(obj).encode()
        self.send_response(200);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def log_message(self,*args):pass

class TransportTests(unittest.TestCase):
    def test_direct_http_honors_typed_ir_and_pure_feedback_only(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        server.replies=[{'expression':{'ref':'current'},'reason':'Keep the original flags'},
                        {'expression':REVERSE,'reason':'Reverse the current membership'}]
        server.log=[]
        t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
        try:
            class Loopback(DirectTransferLLM):
                TAGS=f'http://127.0.0.1:{server.server_port}/api/tags'
                GENERATE=f'http://127.0.0.1:{server.server_port}/api/generate'
            model=Loopback('transfer-test:1b')
            r=model_trial(BY_KEY['missing_supplies'],model,max_calls=2)
            self.assertEqual(r['status'],'CANDIDATE_FOR_REVIEW_NOT_INSTALLED')
            self.assertEqual(r['frozen_correct'],64)
            self.assertEqual(r['model_calls'],2)
            posts=[x[2] for x in server.log if x[0]=='POST']
            self.assertEqual(len(posts),2)
            self.assertEqual(posts[0]['model'],'transfer-test:1b')
            self.assertNotIn('switch',posts[0]['prompt'].lower().split('task_data_json=')[1])
            self.assertIn('development_feedback',posts[1]['prompt'])
            self.assertNotIn('frozen',posts[1]['prompt'].lower().split('task_data_json=')[1])
            self.assertTrue(all(x['typed_valid'] for x in model.calls))
            self.assertFalse(r['installed'])
        finally:
            server.shutdown();server.server_close();t.join(timeout=2)

if __name__=='__main__':unittest.main()
