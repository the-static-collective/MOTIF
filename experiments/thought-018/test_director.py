"""Independent safety, model-invocation, routing, and frozen-audit tests."""
from __future__ import annotations
import json
import threading
import unittest
from copy import deepcopy
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from director import (ResearchDirector, bitmask,color_set, independent_spec,
                      candidate_mask,info_score, choose_probe,control_trial,compare_controls)
from research_model import (TinyResearchModel,OllamaResearchModel,guard_probe,
                            validate_model_reply,candidate,PATTERNS, MODEL_SCHEMA)
from program import validate_proposal, evaluate_macro,digest,ProposalError
from fixtures import DEV,AUDIT,STRESS
from benchmark import main,BRIEF

class DirectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=main()
        cls.result=cls.report['trial']

    def test_learned_model_is_really_invoked_and_receives_observation(self):
        a=self.result
        self.assertEqual(a['model_kind'],'TRAINED_NAIVE_BAYES_FIXED_GRAMMAR')
        self.assertEqual(a['model_calls'],2)
        self.assertEqual(len(self.report['model_invocations']),2)
        self.assertEqual(a['steps'][0]['model_candidate'],'GROW')
        self.assertEqual(a['steps'][0]['disposition'],'REFUTED_ON_DEV')
        self.assertEqual(a['steps'][1]['model_candidate'],'FLIP')
        self.assertTrue(all(not x['audit_access'] for x in self.report['model_invocations']))

    def test_independent_dev_probe_refutes_false_model_hypothesis(self):
        a=self.result
        first=a['steps'][0]
        self.assertNotEqual(first['model_candidate_output'], first['independent_oracle_output'])
        self.assertTrue(first['remaining_mechanisms']==['FLIP'])
        self.assertEqual(a['selected_mechanism'],'FLIP')
        self.assertEqual(a['dev_probe_count'],1)

    def test_oracle_uses_bitmasks_not_candidate_evaluator(self):
        self.assertEqual(independent_spec('FLIP',1,1),0)
        self.assertEqual(independent_spec('GROW',1,1),1)
        self.assertEqual(independent_spec('DRAIN',1,1),0)
        self.assertEqual(candidate_mask(PATTERNS['FLIP'],1,1),0)
        self.assertEqual(candidate_mask(PATTERNS['GROW'],1,1),1)
        with self.assertRaises(ValueError):independent_spec('DEEP_THOUGHT',0,1)
        with self.assertRaises(ValueError):independent_spec('FLIP',0,99)

    def test_model_suggests_probe_but_director_may_override(self):
        candidates=dict(PATTERNS)
        bad={'on':[],'toggles':[],'reason':'No information can be learned'}
        p,status=choose_probe(candidates,set(),bad)
        self.assertNotEqual(p,(0,0))
        self.assertEqual(status,'MODEL_TEST_DEFERRED_INFORMATIVE_ALTERNATIVE')
        self.assertGreater(info_score(candidates,*p),0)

    def test_accepts_equally_informative_model_probe(self):
        candidates=dict(PATTERNS)
        p,_=choose_probe(candidates,set())
        t={'on':list(color_set(p[0])),'toggles':list(color_set(p[1])),
           'reason':'Distinguishes transition hypotheses'}
        self.assertEqual(choose_probe(candidates,set(),t)[1],
                         'MODEL_TEST_ACCEPTED_INDEPENDENT_UTILITY_CHECK')

    def test_five_target_controls_matched_and_nontrivial(self):
        c=self.report['finite_policy_controls']
        self.assertEqual(c['adaptive']['resolved'],5)
        self.assertEqual(c['fixed']['resolved'],5)
        self.assertLess(c['adaptive']['total_questions'],c['fixed']['total_questions'])
        self.assertEqual(c['adaptive']['total_questions'],5)
        self.assertEqual(c['fixed']['total_questions'],12)
        self.assertTrue(all(control_trial(t,'adaptive')['resolved'] for t in PATTERNS))

    def test_actual_017_compiled_python_executes_and_audit_is_frozen(self):
        a=self.result
        self.assertEqual(a['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
        self.assertEqual(a['dev_truth_table'],{'passed':64,'total':64})
        self.assertEqual(a['development_graph'],{'passed':8,'total':8})
        self.assertEqual(a['safety_graph'],{'passed':4,'total':4})
        self.assertEqual(a['frozen_graph_audit'],{'passed':60,'total':60})
        self.assertEqual(a['stress_graph_audit'],{'passed':80,'total':80})
        self.assertTrue(a['audit_inspected_after_selection'])
        self.assertFalse(a['frozen_audit_seen_by_model'])

    def test_source_code_and_pen_are_not_mutated(self):
        a=self.result
        self.assertFalse(a['installed'])
        self.assertEqual(a['pen_state'],'UNCHANGED')
        self.assertEqual(a['external_authority'],'NONE')
        self.assertFalse(a['model_written_python_executed'])
        self.assertTrue(a['trusted_template_only'])
        self.assertEqual(a['local_ollama_http_calls'],0)

    def test_deterministic_digest_and_no_execution_from_model_text(self):
        result=self.result
        self.assertEqual(digest({k:v for k,v in result.items() if k!='receipt_digest'}),
                         result['receipt_digest'])
        self.assertTrue(all(not r.get('source_graph_modified',False) for r in result['steps']))
        self.assertEqual(result['learned_new_general_algorithm'],False)

    def test_unknown_fields_and_executables_are_rejected(self):
        example=TinyResearchModel().propose(BRIEF)
        for bad in (dict(example,command='rm -rf /'),
                    dict(example,mechanism={'__import__':'os'}),
                    dict(example,suggested_test={'on':['red'],'toggles':['evil'],'reason':'run code'}),
                    dict(example,declared_name='RUN')):
            with self.subTest(bad=bad):
                with self.assertRaises((ValueError,ProposalError)):
                    validate_model_reply(bad)

    def test_input_limits_and_failure_to_pick_model_hold(self):
        for kwargs in ({'max_rounds':0},{'target':'unknown'}, {'max_rounds':7}):
            with self.assertRaises(ValueError):ResearchDirector(BRIEF,**kwargs)
        with self.assertRaises(ValueError):ResearchDirector('short')
        class Refuses:
            kind='MODEL_REFUSES';calls=[]
            def propose(self,*args):return None
        a,proposal=ResearchDirector(BRIEF,model=Refuses(),max_rounds=2).run(evaluate_graph=False)
        self.assertEqual(a['status'],'HOLD_NO_VERIFIED_MODEL_PROPOSAL')
        self.assertIsNone(proposal)

    def test_model_cannot_grant_itself_approval_by_claiming_outcome(self):
        class Fabricator:
            kind='FAKE';calls=[]
            def propose(self,*args):
                p=TinyResearchModel().propose(BRIEF)
                p['status']='SUCCESS_PRODUCTION_DEPLOYMENT'
                return p
        a,_=ResearchDirector(BRIEF,model=Fabricator()).run(evaluate_graph=False)
        self.assertEqual(a['status'],'HOLD_NO_VERIFIED_MODEL_PROPOSAL')
        self.assertEqual(a['steps'][0]['disposition'],'HOLD_MODEL_INVALID_OR_UNAVAILABLE')

    def test_bad_expression_cannot_run_source(self):
        class Evil:
            kind='INJECTION';calls=[]
            def propose(self,*args):
                r=TinyResearchModel().propose(BRIEF)
                r['mechanism']['expression']={'op':'execute','args':[]}
                return r
        a,_=ResearchDirector(BRIEF,model=Evil()).run()
        self.assertEqual(a['status'],'HOLD_NO_VERIFIED_MODEL_PROPOSAL')
        self.assertEqual(a['model_kind'],'INJECTION')

    def test_frozen_audit_rejects_mechanism_that_fails_heldout(self):
        # Instead of training to overfit a known failure, replace one frozen
        # artifact with an invalid specimen. The independent validator refuses
        # it before it can count as a success.
        bad=deepcopy(AUDIT[:3]);bad[0]['problem']['n']=100
        with self.assertRaises(Exception):
            ResearchDirector(BRIEF,max_rounds=5).run(audit=bad,stress=STRESS[:2])

    def test_unknown_test_blueprint_and_nonfinite_probe_rejected(self):
        for t in ({'on':['red','red'],'toggles':[],'reason':'duplicate elements'},
                  {'on':'red','toggles':[],'reason':'wrong type'},
                  {'on':[],'toggles':['blue'],'reason':'x'},
                  {'on':[],'toggles':[],'reason':'valid','shell':'open'}):
            with self.assertRaises(ValueError):guard_probe(t)

    def test_next_question_is_review_only(self):
        self.assertIn('independently authored',self.result['next_research_question'])
        self.assertTrue(self.result['status'].endswith('NOT_INSTALLED'))

class OllamaBoundaryTests(unittest.TestCase):
    def test_real_http_transport_stub_not_real_ollama(self):
        class Stub(BaseHTTPRequestHandler):
            def do_POST(self):
                body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                self.server.observed=body
                expr=deepcopy(PATTERNS['FLIP'])
                p={'expression':expr,'purpose':'A bounded toggle hypothesis',
                   'proposer':'mock-model-not-live','on':['red'],'toggles':['red'],
                   'reason':'Test whether two toggles cancel'}
                payload=json.dumps({'response':json.dumps(p)}).encode()
                self.send_response(200);self.send_header('Content-Type','application/json')
                self.end_headers();self.wfile.write(payload)
            def log_message(self,*args):pass
        server=HTTPServer(('127.0.0.1',0),Stub)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            class TestOnly(OllamaResearchModel):
                endpoint=f'http://127.0.0.1:{server.server_port}/api/generate'
            model=TestOnly('fictional-test')
            reply=model.propose('Test reversible switches',())
            mechanism,probe=validate_model_reply(reply)
            self.assertEqual(mechanism['expression'],PATTERNS['FLIP'])
            self.assertEqual(probe['on'],['red'])
            self.assertEqual(len(model.calls),1)
            self.assertFalse(server.observed['stream'])
            self.assertEqual(server.observed['options']['temperature'],0)
            self.assertNotIn('AUDIT',server.observed['prompt'])
        finally:
            server.shutdown();server.server_close();thread.join(timeout=1)

    def test_malformed_ollama_reply_returns_hold(self):
        class Stub(BaseHTTPRequestHandler):
            def do_POST(self):
                payload=json.dumps({'response':json.dumps({'code':'print(1)'})}).encode()
                self.send_response(200);self.end_headers();self.wfile.write(payload)
            def log_message(self,*args):pass
        server=HTTPServer(('127.0.0.1',0),Stub)
        th=threading.Thread(target=server.serve_forever,daemon=True);th.start()
        try:
            class TestOnly(OllamaResearchModel):
                endpoint=f'http://127.0.0.1:{server.server_port}/api/generate'
            a,_=ResearchDirector(BRIEF,model=TestOnly('stub')).run(evaluate_graph=False)
            self.assertEqual(a['status'],'HOLD_NO_VERIFIED_MODEL_PROPOSAL')
        finally:server.shutdown();server.server_close();th.join(timeout=1)

if __name__=='__main__':unittest.main()
