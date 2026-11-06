"""Independent policy gates and controlled trial against developer-supplied fixtures."""
from __future__ import annotations
import copy,json,tempfile,threading,unittest
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
import sys
from model_gateway import TinyTextModel,OllamaLocalModel,ModelError,SCHEMA
from devlab import (TinyModelDeveloper,SelfDevelopmentLab,reasoning_policy_trial,
                    validate_rule,TrialError,classify,evaluate)
from fixtures import TRAIN,DEV,HELDOUT,SAFETY
from language_space import LanguageSpace
from benchmark import main
from demo import demo
sib=Path(__file__).resolve().parent.parent/'thought-013'
if not sib.is_dir():sib=Path(__file__).resolve().parent.parent/'thought013'
if str(sib) not in sys.path:sys.path.append(str(sib))
from source013 import make_engine,possible_worlds

class LabTests(unittest.TestCase):
 def setUp(self):
    t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
    self.field,self.engine,_=make_engine(Path(t.name)/'field.jsonl')
    self.pair=('m:food','m:meal')
 def test_legacy_interpreter_baseline_recognized(self):
    self.assertEqual(classify('What if meal and food connect?',self.engine,self.pair),'EXPLORE_POSSIBILITY')
 def test_model_is_trained_and_invoked(self):
    m=TinyTextModel(TRAIN)
    x=m.predict('what would disprove the premise')
    self.assertEqual(x['speech_act'],'CHALLENGE')
    self.assertGreater(x['confidence'],0)
 def test_model_proposal_is_not_pen_or_new_fact(self):
    m=TinyTextModel(TRAIN);s=LanguageSpace(self.engine)
    before=copy.deepcopy(self.field.snapshot());turn=s.explore('what would disprove the route',selected_pair=self.pair,model=m)
    self.assertEqual(turn['speech_act'],'CHALLENGE')
    self.assertTrue(turn['model_accepted_as_hypothesis'])
    self.assertEqual(turn['pen_state'],'UNCHANGED');self.assertEqual(turn['external_authority'],'NONE')
    self.assertEqual(self.field.snapshot(),before)
 def test_malicious_model_rejected(self):
    class Insecure:
      def propose(self,*args,**kwargs):
       return {'schema':SCHEMA,'speech_act':'EXECUTE_CODE','manifestation_ids':[],
               'rationale':'run shell','model_kind':'insecure','confidence':1.0}
    s=LanguageSpace(self.engine)
    x=s.explore('strange wording here',selected_pair=self.pair,model=Insecure())
    self.assertEqual(x['speech_act'],'UNKNOWN');self.assertIsNotNone(x['model_error'])
 def test_model_cannot_switch_known_referents(self):
    class Switch:
      def propose(self,*args,**kwargs):return {'schema':SCHEMA,'speech_act':'CHALLENGE',
        'manifestation_ids':['m:home-shelter','m:home-belonging'],
        'rationale':'change referents','model_kind':'untrusted','confidence':.9}
    x=LanguageSpace(self.engine).explore('strange wording here',selected_pair=self.pair,model=Switch())
    self.assertEqual(x['speech_act'],'UNKNOWN')
    self.assertFalse(x['model_accepted_as_hypothesis'])
    self.assertIsNotNone(x['model_error'])
 def test_model_cannot_claim_fabricated_confidence(self):
    class Invalid:
      def propose(self,*args,**kwargs):return {'schema':SCHEMA,'speech_act':'CHALLENGE',
        'manifestation_ids':list(self.pair),'rationale':'not calibrated',
        'model_kind':'untrusted','confidence':2.0}
    guess=Invalid();guess.pair=self.pair
    x=LanguageSpace(self.engine).explore('strange wording here',selected_pair=self.pair,model=guess)
    self.assertFalse(x['model_accepted_as_hypothesis'])
    self.assertIsNotNone(x['model_error'])
 def test_effectful_text_bypasses_model_completely(self):
    class Alarm:
      def propose(self,*args,**kwargs):raise AssertionError('must not invoke model for command')
    x=LanguageSpace(self.engine).explore('deploy all repos',selected_pair=self.pair,model=Alarm())
    self.assertEqual(x['speech_act'],'HOLD_EFFECT_REQUEST')
 def test_equal_labels_do_not_infer_same_identity(self):
    s=LanguageSpace(self.engine)
    with self.assertRaises(Exception):
      s.explore('compare these',selected_pair=('m:home-shelter','m:home-shelter'))
    self.assertNotEqual(self.engine.manifests['m:home-shelter']['concept_id'],
                        self.engine.manifests['m:home-belonging']['concept_id'])
 def test_challenge_receipt_replay_is_stable(self):
    s=LanguageSpace(self.engine);a=s.explore('i wonder whether shelter is relevant',selected_pair=self.pair)
    b=s.challenge(a['utterance_id'],'What would falsify this hypothesis?')
    self.assertEqual(len(s.snapshot()['turns']),2)
    self.assertEqual(b['status'],'QUESTION_ONLY')
    self.assertEqual(s.snapshot()['receipt_digest'],s.snapshot()['receipt_digest'])
 def test_wrong_ids_and_unsupported_model_act_hold(self):
    class Wrong:
      def propose(self,*args,**kwargs):return {'schema':SCHEMA,'speech_act':'CHALLENGE',
        'manifestation_ids':['fake','m:food'],'rationale':'test','model_kind':'bad','confidence':0.9}
    t=LanguageSpace(self.engine).explore('what would disprove the route',selected_pair=self.pair,model=Wrong())
    self.assertEqual(t['speech_act'],'UNKNOWN')
    self.assertFalse(t['model_accepted_as_hypothesis'])
 def test_candidate_rules_are_code_free_and_strict(self):
    r={'schema':'motif.thought014.rule-candidate.v1','pattern':'i wonder whether',
       'speech_act':'EXPLORE_POSSIBILITY','match':'prefix','origin':'test'}
    validate_rule(r)
    for bad in [dict(r,speech_act='PEN_COMMIT'),dict(r,pattern='.*'),
                dict(r,pattern='what'),dict(r,exec='rm -rf /')]:
      with self.assertRaises(TrialError):validate_rule(bad)
 def test_prefix_word_boundary_and_effect_guard(self):
    r={'schema':'motif.thought014.rule-candidate.v1','pattern':'i wonder whether',
       'speech_act':'EXPLORE_POSSIBILITY','match':'prefix','origin':'test'}
    self.assertEqual(classify('i wonder whethered something',self.engine,self.pair,[r]),'UNKNOWN')
    self.assertEqual(classify('i wonder whether to send a letter',self.engine,self.pair,[r]),'UNKNOWN')
 def test_selfdev_evaluates_and_does_not_install(self):
    d=TinyModelDeveloper(TRAIN)
    report=SelfDevelopmentLab(self.engine,self.pair,TRAIN,DEV,HELDOUT,SAFETY).run(developer=d)
    self.assertEqual(report['status'],'CANDIDATE_FOR_HUMAN_REVIEW_NOT_INSTALLED')
    self.assertGreater(report['development_final'],report['development_baseline'])
    self.assertGreaterEqual(report['frozen_candidate'],report['frozen_baseline'])
    self.assertEqual(report['safety_passed'],report['safety_total'])
    self.assertFalse(report['changed_source_code']);self.assertFalse(report['installed_rules'])
    self.assertTrue(any(c['kind']=='MODEL_RECEIVES_DEV_CRITIQUE' for c in d.calls))
 def test_candidate_does_not_mint_authored_edges(self):
    before=self.engine.input_digest
    SelfDevelopmentLab(self.engine,self.pair,TRAIN,DEV,HELDOUT,SAFETY).run()
    self.assertEqual(self.engine.input_digest,before)
 def test_narrow_candidate_maintains_known_legacy_actions(self):
    lab=SelfDevelopmentLab(self.engine,self.pair,TRAIN,DEV,HELDOUT,SAFETY).run()
    rules=lab['staged_rules']
    self.assertEqual(classify('what if there were a meal',self.engine,self.pair,rules),'EXPLORE_POSSIBILITY')
    self.assertEqual(classify('deploy now',self.engine,self.pair,rules),'UNKNOWN')
 def test_no_pair_does_not_misrepresent_exploration(self):
    r={'schema':'motif.thought014.rule-candidate.v1','pattern':'i wonder whether',
       'speech_act':'EXPLORE_POSSIBILITY','match':'prefix','origin':'test'}
    self.assertEqual(classify('i wonder whether',self.engine,None,[r]),'UNKNOWN')
 def test_model_heldout_is_evaluated_only_after_dev(self):
    d=TinyModelDeveloper(TRAIN)
    r=SelfDevelopmentLab(self.engine,self.pair,TRAIN,DEV,HELDOUT,SAFETY).run(developer=d)
    self.assertTrue(r['independent_audit_after_proposals'])
    self.assertTrue(all(x['test_truth_access']!='HELDOUT' for x in d.calls))
 def test_selfdevelopment_round_bounds(self):
    lab=SelfDevelopmentLab(self.engine,self.pair,TRAIN,DEV,HELDOUT,SAFETY)
    with self.assertRaises(TrialError):lab.run(max_rounds=50)
 def test_strategy_trial_is_independent_of_geometry(self):
    result=reasoning_policy_trial(self.engine,possible_worlds(self.engine),self.pair)
    self.assertIn(result['selected_after_dev'],('decision','world'))
    self.assertEqual(result['external_authority'],'NONE')
 def test_full_benchmark_and_demo(self):
    report=main();d=demo()
    self.assertEqual(report['external_authority'],'NONE')
    self.assertFalse(report['local_ollama_called'])
    self.assertTrue(d['pen_unchanged'])
 def test_no_pair_model_cannot_bypass_membrane(self):
    m=TinyTextModel(TRAIN);s=LanguageSpace(self.engine)
    x=s.explore('i wonder whether this is connected',model=m)
    self.assertIn(x['status'],('HOLD','CLARIFY_REFERENTS'))
 def test_no_automatic_model_invocation_for_013_recognized_text(self):
    class Alarm:
      def propose(self,*args,**kwargs):raise AssertionError('should not invoke model')
    x=LanguageSpace(self.engine).explore('what if food helps the meal',selected_pair=self.pair,model=Alarm())
    self.assertEqual(x['speech_act'],'EXPLORE_POSSIBILITY')
 def test_invalid_model_name_rejected(self):
    for n in ('../bad','model;rm', '', 'm'*100):
       with self.assertRaises(ModelError):OllamaLocalModel(n)

class HTTPGatewayTests(unittest.TestCase):
 def test_opt_in_real_http_transport_with_fake_inference_daemon(self):
    # Network transport is real loopback HTTP; server is a synthetic stub, NOT an LLM.
    from model_gateway import OllamaLocalModel
    class Handler(BaseHTTPRequestHandler):
      def do_POST(self):
        self.server.request_path=self.path
        inp=self.rfile.read(int(self.headers['Content-Length']))
        self.server.payload=json.loads(inp)
        body=json.dumps({'response':json.dumps({'speech_act':'CHALLENGE','rationale':'question'} )}).encode()
        self.send_response(200);self.send_header('Content-Type','application/json')
        self.end_headers();self.wfile.write(body)
      def log_message(self,*args):pass
    server=HTTPServer(('127.0.0.1',0),Handler)
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    try:
      # Override class endpoint in a test-only subclass; production endpoint fixed.
      class LoopbackStub(OllamaLocalModel):endpoint=f'http://127.0.0.1:{server.server_port}/api/generate'
      r=LoopbackStub('testmodel').propose('what would disprove the claim',selected_pair=['m:food','m:meal'])
      self.assertEqual(r['speech_act'],'CHALLENGE');self.assertEqual(server.request_path,'/api/generate')
      self.assertEqual(server.payload['stream'],False)
      self.assertEqual(server.payload['options']['temperature'],0)
    finally:server.shutdown();server.server_close();t.join(timeout=1)

 def test_local_model_can_propose_rule_but_independent_lab_decides(self):
    from devlab import OllamaDeveloper
    class Handler(BaseHTTPRequestHandler):
      def do_POST(self):
        data=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.seen_prompt=data['prompt']
        answer={'pattern':'i wonder whether','speech_act':'EXPLORE_POSSIBILITY','match':'prefix'}
        body=json.dumps({'response':json.dumps(answer)}).encode()
        self.send_response(200);self.end_headers();self.wfile.write(body)
      def log_message(self,*args):pass
    server=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
      class Stub(OllamaLocalModel):endpoint=f'http://127.0.0.1:{server.server_port}/api/generate'
      model=Stub('local-test-only')
      dev=OllamaDeveloper(model,TRAIN)
      with tempfile.TemporaryDirectory() as td:
        _,engine,_=make_engine(Path(td)/'field.jsonl')
        report=SelfDevelopmentLab(engine,('m:food','m:meal'),TRAIN,DEV,HELDOUT,SAFETY).run(
          max_rounds=1,developer=dev)
      self.assertEqual(report['status'],'CANDIDATE_FOR_HUMAN_REVIEW_NOT_INSTALLED')
      self.assertTrue(report['staged_rules'])
      self.assertEqual(report['safety_passed'],report['safety_total'])
      self.assertEqual(report['external_authority'],'NONE')
      self.assertTrue(any(x['kind']=='MODEL_RECEIVES_DEV_CRITIQUE' for x in dev.calls))
      self.assertNotIn('development_failed_cases',server.seen_prompt)
      self.assertNotIn(HELDOUT[0][0],server.seen_prompt)
    finally:server.shutdown();server.server_close();thread.join(timeout=1)
 def test_local_model_unsafe_rule_cannot_install(self):
    from devlab import OllamaDeveloper
    class Unsafe:
      model_kind='SYNTHETIC_UNTRUSTED'
      def suggest_rule(self,*args,**kwargs):
        return {'pattern':'what', 'speech_act':'PEN_COMMIT', 'match':'prefix'}
    with tempfile.TemporaryDirectory() as td:
      _,engine,_=make_engine(Path(td)/'source.jsonl')
      report=SelfDevelopmentLab(engine,('m:food','m:meal'),TRAIN,DEV,HELDOUT,SAFETY).run(
        max_rounds=2,developer=OllamaDeveloper(Unsafe(),TRAIN))
    self.assertEqual(report['status'],'HOLD_NO_STAGED_IMPROVEMENT')
    self.assertFalse(report['staged_rules'])
    self.assertEqual(report['rounds'][0]['disposition'],'HOLD_BAD_DSL')
    self.assertFalse(report['installed_rules'])

if __name__=='__main__':unittest.main()
