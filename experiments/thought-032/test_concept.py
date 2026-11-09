import copy,json,sys,threading,unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
HERE=Path(__file__).resolve().parent
for sibling in ('thought-025','thought-027'):
 p=str(HERE.parent/sibling)
 if p not in sys.path:sys.path.insert(0,p)
from specimens import BY_KEY
from concept_language import (ConceptBook,ConceptError,graph_match,
    validate_definition,semantic_signature,digest)
from experiment import (GRAPH_FIXTURE,prior_seed,session,evaluate_submission,ExperimentError)
from concept_run import ScriptedConceptAgent,main
from model import DirectConceptLLM
from direct_model import ModelTransportError

GOOD={'word':'mova','gloss':'Remove event-labeled categories from current categories',
      'relation':'DIFFERENCE','graph_pattern':'DEPENDENCY_CHAIN',
      'proof_gate':'DEV_THEN_FROZEN_64','uncertainty':'TRANSFER_REQUIRES_NEW_EVIDENCE',
      'next_experiment':'DISCRIMINATING_DEV_QUERIES'}

class Tests(unittest.TestCase):
 def test_source_owned_symbol_has_known_independently_checkable_signature(self):
    self.assertEqual(len(semantic_signature('DIFFERENCE')),64)
    self.assertEqual(semantic_signature('DIFFERENCE')[3*8+5],2)
    self.assertNotEqual(semantic_signature('DIFFERENCE'),semantic_signature('UNION'))
 def test_typing_rejects_executable_primitives_and_hidden_semantics(self):
    for bad in [{**GOOD,'word':'exec'},
      {**GOOD,'relation':'ARBITRARY_PYTHON'},
      {**GOOD,'graph_pattern':'DELETE_EDGES'},
      {**GOOD,'proof_gate':'TRUST_ME'},
      {**GOOD,'uncertainty':'ALREADY_PROVEN_ALL_CONTEXTS'},
      {**GOOD,'next_experiment':'DO_ACTION'},
      {**GOOD,'new_field':'code'},
      {**GOOD,'gloss':'bad\ncall'}]:
        with self.assertRaises(ConceptError):validate_definition(bad)
 def test_word_is_opt_in_and_session_scoped(self):
    x=ConceptBook(enabled=False)
    with self.assertRaises(ConceptError):x.admit(GOOD)
    y=ConceptBook();y.admit(GOOD)
    self.assertEqual(y.view()['coined'],1);self.assertEqual(y.view()['uses'],0)
    self.assertEqual(y.expand('mova')['relation'],'DIFFERENCE')
    self.assertEqual(y.view()['uses'],1)
    with self.assertRaises(ConceptError):ConceptBook().expand('mova')
 def test_duplicate_resisted_and_hash_tamper_rejected(self):
    b=ConceptBook();b.admit(GOOD)
    with self.assertRaises(ConceptError):b.admit({**GOOD,'word':'MOVA'})
    b.records['mova']['definition']['relation']='UNION'
    with self.assertRaises(ConceptError):b.expand('mova')
 def test_graph_dependency_chain_preserves_actual_witness_roots(self):
    report=graph_match('DEPENDENCY_CHAIN',GRAPH_FIXTURE)
    self.assertEqual(report['total_found'],1)
    self.assertEqual(report['matches'][0]['nodes'],['food','cold_storage','power'])
    self.assertEqual(report['matches'][0]['edge_origins'],['synthetic_a','synthetic_b'])
    self.assertEqual(graph_match('TENSION_EDGE',GRAPH_FIXTURE)['total_found'],0)
 def test_hypothesis_bridge_is_not_new_observation(self):
    r=graph_match('ASSOCIATION_BRIDGE',GRAPH_FIXTURE)
    self.assertGreaterEqual(r['total_found'],1)
    self.assertEqual(r['status'],'STRUCTURAL_CANDIDATES_NOT_NEW_EVIDENCE')
    self.assertFalse(r['coordinates_as_evidence'])
 def test_seed_is_independently_rechecked_but_not_global_truth(self):
    r=prior_seed()
    self.assertEqual(r['full_cases'],64)
    self.assertFalse(r['new_task_automatically_proven'])
    self.assertEqual(r['authentication'],'UNSIGNED_SYNTHETIC')
 def test_two_source_fixture_transfer_cases_independently_pass(self):
    tasks=[BY_KEY['food_recalled_elsewhere'],BY_KEY['reverse_outreach']]
    r=session(tasks,ScriptedConceptAgent(),pidgin_enabled=True)
    self.assertEqual(r['concept_book']['coined'],1)
    self.assertEqual(r['concept_book']['uses'],2)
    self.assertEqual(r['inference_calls'],3)
    for x in r['results'].values():
        self.assertEqual(x['frozen_correct'],64)
        self.assertEqual(x['trusted_executable_correct'],64)
        self.assertTrue(x['model_word_used'])
        self.assertFalse(x['installed'])
 def test_matched_scripted_baseline_uses_no_word(self):
    tasks=[BY_KEY['food_recalled_elsewhere'],BY_KEY['reverse_outreach']]
    x=session(tasks,ScriptedConceptAgent(),pidgin_enabled=False)
    self.assertEqual(x['inference_calls'],3)
    self.assertEqual(x['concept_book']['uses'],0)
    self.assertTrue(all(r['frozen_correct']==64 for r in x['results'].values()))
 def test_wrong_relation_with_reused_word_holds_on_dev(self):
    book=ConceptBook();book.admit({**GOOD,'relation':'UNION'})
    task=BY_KEY['food_recalled_elsewhere'];seed=prior_seed()
    submission={'bindings':{'current':'register_g','event':'register_f'},
       'word':'mova','relation':None,'evidence_refs':[seed['proof_digest']],
       'rationale':'This is an intentionally mistaken candidate'}
    r=evaluate_submission(task,submission,book,seed=seed)
    self.assertEqual(r['status'],'HOLD_DEV_COUNTEREXAMPLE')
    self.assertIsNone(r['frozen_correct'])
 def test_unseen_word_or_forged_citation_rejected(self):
    task=BY_KEY['food_recalled_elsewhere'];seed=prior_seed();book=ConceptBook();book.admit(GOOD)
    sample={'bindings':{'current':'register_g','event':'register_f'},
       'word':'unknown','relation':None,'evidence_refs':[],
       'rationale':'Inspect and compare two finite sets'}
    with self.assertRaises(ConceptError):evaluate_submission(task,sample,book,seed=seed)
    sample['word']='mova';sample['evidence_refs']=['forged-id']
    with self.assertRaises(ExperimentError):evaluate_submission(task,sample,book,seed=seed)
 def test_unknown_or_open_world_task_is_not_boolean_coerced(self):
    task=BY_KEY['unknown_beliefs'];s=prior_seed()
    self.assertEqual(evaluate_submission(task,{},ConceptBook(),seed=s)['status'],'HOLD_NONBOOLEAN')
 def test_offline_cli_not_a_real_llm(self):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
      dest=Path(d)/'x.json'
      self.assertEqual(main(['--output',str(dest)]),0)
      obj=json.loads(dest.read_text())
      self.assertEqual(obj['real_model_calls'],0)
      self.assertFalse(obj['actual_model_inference'])
      self.assertTrue(obj['scripted_fixture_is_not_generations'])
      self.assertFalse(obj['automatically_installed'])

class MockOllama(BaseHTTPRequestHandler):
 def do_GET(self):
    self.send_json({'models':[{'name':'test:1b','digest':'a'*64}]})
 def do_POST(self):
    request=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
    self.server.reqs.append(request)
    if 'PREPARE' in request['prompt']:
        result={'choice':'decline','definition':None}
    else:
        result={'bindings':{'current':'register_g','event':'register_f'},
          'word':None,'relation':'DIFFERENCE','evidence_refs':[],
          'rationale':'Return recalled items that are absent from inventory'}
    self.send_json({'model':request['model'],'done':True,'response':json.dumps(result),
                    'prompt_eval_count':250,'eval_count':50})
 def send_json(self,value):
    data=json.dumps(value).encode();self.send_response(200)
    self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)))
    self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass

class TransportTests(unittest.TestCase):
 def test_real_http_adapter_is_not_mistaken_for_scripted_emergence(self):
    server=ThreadingHTTPServer(('127.0.0.1',0),MockOllama);server.reqs=[]
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    try:
      class Local(DirectConceptLLM):
        TAGS=f'http://127.0.0.1:{server.server_port}/api/tags'
        GENERATE=f'http://127.0.0.1:{server.server_port}/api/generate'
      model=Local('test:1b')
      result=session([BY_KEY['food_recalled_elsewhere'],BY_KEY['reverse_outreach']],model,pidgin_enabled=True)
      self.assertEqual(result['inference_calls'],3)
      self.assertTrue(all(x['transport']=='DIRECT_LOOPBACK_OLLAMA_HTTP' for x in model.calls))
      self.assertEqual(result['concept_book']['coined'],0)
      self.assertEqual(result['concept_book']['uses'],0)
      self.assertIn('PACKET_JSON=',server.reqs[0]['prompt'])
      self.assertNotIn('"policy"',server.reqs[-1]['prompt'].split('PACKET_JSON=')[-1])
    finally:
      server.shutdown();server.server_close();t.join(timeout=3)
 def test_local_llm_disallows_cloud_tag(self):
    with self.assertRaises(ModelTransportError):DirectConceptLLM('x:cloud')

if __name__=='__main__':unittest.main()
