"""THOUGHT-026: genuine source-owned tests. All model fixtures are simulated."""
from __future__ import annotations
import copy,json,sys,threading,unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
HERE=Path(__file__).resolve().parent
p=str(HERE.parent/'thought-025')
if p not in sys.path:sys.path.insert(0,p)
from specimens import BY_KEY,public_brief
from stages import (SCHEMA,RELATIONS,DEV_CASES,StageError,check_binding,
 check_relation,assemble,stage_trial,dev_witnesses,locate_failure,source_owned_expression)
from stage_fixtures import DeterministicStages
from stage_llm import DirectStageLLM
from direct_model import ModelTransportError
from stage_cli import main

class StagesTests(unittest.TestCase):
 def test_complete_staged_fixture_solves_all_boolean_descriptions(self):
    for task in BY_KEY.values():
      result=stage_trial(task,DeterministicStages(),repair=True)
      if not task.representable:
        self.assertTrue(result['status'].startswith('HOLD_'),task.key)
        self.assertEqual(result['model_calls'],0)
      else:
        self.assertEqual(result['status'],'CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED',task.key)
        self.assertEqual(result['frozen']['correct'],64)
        self.assertEqual(result['fixed_template_program']['correct'],64)
        self.assertEqual(result['model_calls'],2)
        self.assertFalse(result['installed'])
 def test_bad_binding_kept_as_partial_and_repairable(self):
    t=BY_KEY['food_safe']
    bad=stage_trial(t,DeterministicStages(incorrect_binding=True),repair=False)
    self.assertEqual(bad['status'],'HOLD_DEV_CONTRADICTION')
    self.assertEqual(bad['role_stage']['bindings']['current'],'register_g')
    self.assertEqual(bad['relation_stage']['relation'],'DIFFERENCE')
    self.assertIsNone(bad['frozen'])
    fixed=stage_trial(t,DeterministicStages(incorrect_binding=True),repair=True)
    self.assertEqual(fixed['status'],'CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED')
    self.assertEqual(fixed['model_calls'],3)
    self.assertEqual(fixed['dev_oracle_queries'],4)
    self.assertTrue(fixed['stage_history'][-1]['role_changed'])
    self.assertFalse(fixed['stage_history'][-1]['relation_changed'])
 def test_bad_relation_independently_repairable(self):
    t=BY_KEY['volunteer_eligible']
    x=stage_trial(t,DeterministicStages(incorrect_relation=True),repair=True)
    self.assertEqual(x['status'],'CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED')
    self.assertTrue(x['stage_history'][-1]['relation_changed'])
    self.assertFalse(x['stage_history'][-1]['role_changed'])
 def test_wrong_repair_returns_hold_not_optimistic_success(self):
    x=stage_trial(BY_KEY['food_recalled_elsewhere'],DeterministicStages(
        incorrect_binding=True,incorrect_relation=True,repair_correct=False),repair=True)
    self.assertTrue(x['status'].startswith('HOLD_'))
    self.assertIsNone(x['frozen'])
    self.assertFalse(x['installed'])
 def test_commutative_role_permutations_are_indistinguishable(self):
    t=BY_KEY['volunteer_eligible'];m=DeterministicStages()
    b=m.bind(public_brief(t));r=m.relate(public_brief(t),b)
    obs=dev_witnesses(t,assemble(t,b,r))
    d=locate_failure(t,b,r,obs)
    self.assertTrue(d['roles_observationally_indistinguishable_on_dev'])
    self.assertFalse(d['correct_relation_disclosed'])
 def test_diagnosis_hypothesis_does_not_leak_true_policy(self):
    t=BY_KEY['food_safe'];m=DeterministicStages(incorrect_binding=True)
    b=m.bind(public_brief(t));r=m.relate(public_brief(t),b)
    obs=dev_witnesses(t,assemble(t,b,r))
    d=locate_failure(t,b,r,obs)
    self.assertTrue(d['role_only_possible'])
    self.assertNotIn('correct_roles',d)
    self.assertNotIn('DIFFERENCE',json.dumps(d))
 def test_source_owned_compiler_covers_six_relations(self):
    for term in RELATIONS:
      self.assertTrue(source_owned_expression(term))
    with self.assertRaises(StageError):source_owned_expression('EXEC_PYTHON')
 def test_unknown_field_duplicate_ref_and_injected_code_refused(self):
    t=BY_KEY['food_safe']
    for b in ({'bindings':{'current':'void','event':'register_f'},'rationale':'bounded rationale'},
              {'bindings':{'current':'register_f','event':'register_f'},'rationale':'bounded rationale'},
              {'bindings':{'current':'register_f','event':'register_g'},'rationale':'bounded rationale','python':'import os'}):
      with self.assertRaises(StageError):check_binding(t,b)
 def test_model_relation_and_control_characters_refused(self):
    for r in ({'relation':'python.eval','rationale':'valid rationale'},
              {'relation':'DIFFERENCE','rationale':'x'},
              {'relation':'DIFFERENCE','rationale':'evil\nplugin'}):
      with self.assertRaises(StageError):check_relation(r)
 def test_unsupported_cases_are_evaluator_owned_no_model_call(self):
    m=DeterministicStages()
    for k in ('vague_access','unknown_beliefs'):
      r=stage_trial(BY_KEY[k],m)
      self.assertEqual(r['model_calls'],0)
      self.assertTrue(r['status'].startswith('HOLD_'))
    self.assertEqual(m.calls,[])
 def test_strict_dev_limit_no_frozen_oracle_in_model_context(self):
    t=BY_KEY['food_safe']
    b=DeterministicStages().bind(public_brief(t))
    r={'relation':'DIFFERENCE','rationale':'Valid direct difference'}
    with self.assertRaises(StageError):dev_witnesses(t,assemble(t,b,r),[(0,0)]*5)
 def test_receipt_is_recomputable_and_no_install(self):
    from stages import digest
    r=stage_trial(BY_KEY['food_safe'],DeterministicStages())
    copy_r={k:v for k,v in r.items() if k!='receipt_digest'}
    self.assertEqual(digest(copy_r),r['receipt_digest'])
    self.assertEqual(r['external_authority'],'NONE')
 def test_scripted_offline_cli_has_zero_real_llm_calls(self):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
      out=Path(d)/'r.json'
      code=main(['--backend','offline','--tasks','food_safe,vague_access','--output',str(out)])
      self.assertEqual(code,0)
      r=json.loads(out.read_text())
      self.assertEqual(r['direct_llm_calls'],0)
      self.assertFalse(r['installed'])
      self.assertEqual(r['results']['food_safe']['frozen']['correct'],64)

class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
    self.send_json({'models':[{'name':'mock:3b','digest':'a'*64}]})
 def do_POST(self):
    req=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
    self.server.posts.append(req)
    stage=req['prompt'].split('STAGE=')[1].split('\n')[0]
    if stage=='GROUND_FIELDS':
      obj={'bindings':{'current':'register_g','event':'register_f'},
           'rationale':'Recalled register is primary'}
    elif stage=='DISCOVER_RELATION':
      obj={'relation':'UNION','rationale':'A deliberately incorrect operation'}
    else:
      obj={'binding':{'bindings':{'current':'register_g','event':'register_f'},
               'rationale':'Preserve recalled as primary input'},
           'relationship':{'relation':'DIFFERENCE',
               'rationale':'Subtract shelf inventory from recalls'}}
    self.send_json({'done':True,'response':json.dumps(obj),'model':'mock:3b',
           'prompt_eval_count':100,'eval_count':40})
 def send_json(self,obj):
    raw=json.dumps(obj).encode()
    self.send_response(200);self.send_header('Content-Type','application/json')
    self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def log_message(self,*a):pass

class TransportTests(unittest.TestCase):
 def test_three_direct_http_stages_including_counterexample_repair(self):
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.posts=[]
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
      class Local(DirectStageLLM):
        TAGS=f'http://127.0.0.1:{server.server_port}/api/tags'
        GENERATE=f'http://127.0.0.1:{server.server_port}/api/generate'
      model=Local('mock:3b')
      outcome=stage_trial(BY_KEY['food_recalled_elsewhere'],model,repair=True)
      self.assertEqual(outcome['status'],'CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED')
      self.assertEqual(outcome['model_calls'],3)
      self.assertEqual(outcome['frozen']['correct'],64)
      self.assertTrue(all(call['transport']=='DIRECT_LOOPBACK_OLLAMA_HTTP' for call in model.calls))
      self.assertEqual([r['stage'] for r in model.calls],['GROUND_FIELDS','DISCOVER_RELATION','REPAIR'])
      self.assertEqual(len(server.posts),3)
      self.assertNotIn('task.policy',json.dumps(server.posts))
      self.assertNotIn('frozen_graph',json.dumps(server.posts))
      self.assertIn('development_observations',server.posts[-1]['prompt'])
    finally:server.shutdown();server.server_close();thread.join(timeout=3)
 def test_model_names_cannot_escape_loopback(self):
    with self.assertRaises(ModelTransportError):DirectStageLLM('../remote')
    with self.assertRaises(ModelTransportError):DirectStageLLM('abc:cloud')

if __name__=='__main__':unittest.main()
