"""MOTIF-017 guards: holdouts, primitive truth table, real generated program, model boundary."""
import ast,copy,json,tempfile,threading,unittest
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from program import (CHAT_MODEL_PROPOSAL,MONOTONE_BASELINE,ProposalError,
                     generate_source,validate_proposal,evaluate_macro,op,r)
from oracle import optimum,verify_answer,OracleError
from fixtures import DEV,SAFETY,AUDIT,STRESS,challenge_cases
from lab import run_experiment,truth_table,evaluate_candidate,LabError
from model_gateway import OllamaMacroProposer,ModelUnavailable
from benchmark import main

class InventorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report,cls.source,cls.patch=run_experiment()
 def test_016_grammar_genuinely_lacks_set_difference(self):
    import sys
    sibling=Path(__file__).parent.parent/'thought-016'
    if not sibling.is_dir():sibling=Path(__file__).parent.parent/'thought016'
    sys.path.insert(0,str(sibling))
    from grammar import validate_expr,GrammarError
    with self.assertRaises(GrammarError):validate_expr(CHAT_MODEL_PROPOSAL['expression'])
 def test_model_supplied_new_typed_composition_is_not_arbitrary_python(self):
    x=validate_proposal(CHAT_MODEL_PROPOSAL)
    self.assertEqual(x['expression']['op'],'union')
    self.assertTrue(all(c['op']=='difference' for c in x['expression']['args']))
    self.assertIn('REVIEW ONLY',generate_source(CHAT_MODEL_PROPOSAL))
 def test_full_exhaustive_truth_table_64_cases(self):
    self.assertEqual(truth_table(CHAT_MODEL_PROPOSAL)['passed'],64)
    self.assertEqual(truth_table(MONOTONE_BASELINE)['passed'],27)
 def test_generated_python_is_really_executed_against_independent_oracle(self):
    a=evaluate_candidate(MONOTONE_BASELINE,DEV)
    b=evaluate_candidate(CHAT_MODEL_PROPOSAL,DEV)
    self.assertLess(a['passed'],b['passed']);self.assertEqual(b['passed'],8)
 def test_independent_oracle_does_not_accept_invented_result(self):
    p=DEV[0]['problem']
    self.assertEqual(optimum(p)['cost'],7)
    self.assertFalse(verify_answer(p,{'cost':2,'risk':0,'path':[0,1,3]}))
 def test_audit_and_stress_accept_only_correct_composition(self):
    out=self.report
    self.assertEqual(out['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
    self.assertEqual(out['frozen_audit']['candidate'],out['frozen_audit']['total'])
    self.assertEqual(out['stress']['candidate'],out['stress']['total'])
    self.assertGreater(out['frozen_audit']['candidate'],out['frozen_audit']['baseline'])
 def test_no_automatic_source_install_or_pen_promotion(self):
    self.assertFalse(self.report['installed']);self.assertFalse(self.report['model_wrote_python'])
    self.assertTrue(self.report['pen_unchanged']);self.assertEqual(self.report['external_authority'],'NONE')
    self.assertFalse(self.report['execution_is_os_isolated'])
 def test_model_source_is_only_a_json_expression_inside_trusted_template(self):
    self.assertNotIn('subprocess',self.source);self.assertNotIn('urllib',self.source)
    self.assertNotIn('os.system',self.source)
    self.assertTrue(ast.parse(self.source))
 def test_reject_prompt_injection_or_command_fields(self):
    good=copy.deepcopy(CHAT_MODEL_PROPOSAL)
    for q in [dict(good,python='import os'),dict(good,schema='unknown'),
      dict(good,expression={'op':'exec','args':[r('state.on'),r('arrival.toggles')]}),
      dict(good,expression={'ref':'env.HOME'}),
      dict(good,purpose='run\nprogram')]:
        with self.subTest(q=q):
            with self.assertRaises(ProposalError):validate_proposal(q)
 def test_reject_deep_or_unbounded_or_malformed_ast(self):
    e=r('state.on')
    for i in range(8):e=op('union',e,r('arrival.toggles'))
    p=dict(CHAT_MODEL_PROPOSAL,expression=e)
    with self.assertRaises(ProposalError):validate_proposal(p)
 def test_no_model_can_inject_new_ref_or_import(self):
    for new in [{'ref':'os.system'}, {'ref':'state.on','other':'bad'},
                {'op':'difference','args':[r('state.on'),{'ref':'__builtins__'}]}]:
      with self.assertRaises(ProposalError):validate_proposal(dict(CHAT_MODEL_PROPOSAL,expression=new))
 def test_operator_controlled_audit_bad_problem_aborts(self):
    broken=copy.deepcopy(AUDIT[:2]);broken[0]['problem']['n']=99
    with self.assertRaises(OracleError):run_experiment(audits=broken)
 def test_known_bad_proposal_goes_to_hold(self):
    report,_,diff=run_experiment(MONOTONE_BASELINE)
    self.assertEqual(report['status'],'HOLD_DEVELOPMENT_FAILURE')
    self.assertFalse(diff);self.assertFalse(report['installed'])
    self.assertIsNotNone(report['first_counterexample'])
    self.assertIsNone(report['frozen_audit'])
 def test_developer_probes_did_not_reach_frozen_audit(self):
    self.assertTrue(self.report['frozen_evaluated_after_staging'])
    self.assertFalse(self.report['proposer_seen_frozen_audit'])
    self.assertEqual(self.report['developer_probes']['total'],3)
 def test_deterministic_results_and_replay_receipt(self):
    repeat,source,diff=run_experiment()
    self.assertEqual(repeat,self.report);self.assertEqual(source,self.source)
    self.assertEqual(diff,self.patch)
    from program import digest
    self.assertEqual(self.report['receipt_digest'],digest({k:v for k,v in self.report.items() if k!='receipt_digest'}))
 def test_no_python_execution_on_bad_model_response(self):
    p=dict(CHAT_MODEL_PROPOSAL,expression={'ref':'python.main'})
    with self.assertRaises(ProposalError):evaluate_candidate(p,DEV)
 def test_missing_local_model_fails_closed(self):
    for n in ('../bad','evil;rm',''):
      with self.assertRaises(ModelUnavailable):OllamaMacroProposer(n)
 def test_full_benchmark_writes_review_artifacts_only(self):
    with tempfile.TemporaryDirectory() as d:
      x=main(d)
      self.assertEqual(x['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
      self.assertEqual({p.name for p in Path(d).iterdir()},
          {'experiment-results.json','monotone_reference.py','candidate_solver.py','candidate.diff'})

class ModelTransportTests(unittest.TestCase):
 def test_explicit_ollama_wire_path_with_stub_not_real_llm(self):
    class Handler(BaseHTTPRequestHandler):
      def do_POST(self):
        self.server.path_seen=self.path
        self.server.request=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        raw={k:v for k,v in CHAT_MODEL_PROPOSAL.items() if k!='schema'}
        body=json.dumps({'response':json.dumps(raw)}).encode()
        self.send_response(200);self.end_headers();self.wfile.write(body)
      def log_message(self,*args):pass
    server=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
      class Stub(OllamaMacroProposer):
        endpoint=f'http://127.0.0.1:{server.server_port}/api/generate'
      p=Stub('test-only').propose()
      self.assertEqual(p['expression'],CHAT_MODEL_PROPOSAL['expression'])
      self.assertEqual(server.path_seen,'/api/generate')
      self.assertFalse(server.request['stream'])
      self.assertEqual(server.request['options']['temperature'],0)
    finally:
      server.shutdown();server.server_close();thread.join(timeout=1)

if __name__=='__main__':unittest.main()
