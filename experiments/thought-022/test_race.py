"""THOUGHT-022 correctness, source integrity and honest test accounting."""
import copy,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
for family in ('thought-017','thought-018','thought-019'):
    p=str(HERE.parent/family)
    if p not in sys.path:sys.path.insert(0,p)
from synth import (TASKS,independent_oracle,enumerate_semantics,classical_cegis,
                   choose_probe,signature)
from race import llm_cegis,hybrid_cegis,dev_feedback,offline_matrix
from live_model import GeneralTaskModel,MissingPrimitiveAdvisor
from research_model import candidate,MODEL_SCHEMA
from program import validate_expr,digest,op,r


class Responder:
    kind='SCRIPTED_FIXTURE_NOT_LLM'
    def __init__(self,expressions):self.expressions=list(expressions);self.calls=[]
    def propose(self,brief,feedback=()):
        self.calls.append({'brief':brief,'dev_feedback':copy.deepcopy(feedback),'fake':True})
        if not self.expressions:return None
        expression=self.expressions.pop(0)
        return {'schema':MODEL_SCHEMA,'mechanism':{
          'schema':'motif.thought017.macro-proposal.v1',
          'expression':expression,'purpose':'Source-owned synthetic experiment',
          'proposer':'test-only-scripted-responder'},
          'suggested_test':{'on':['red'],'toggles':['red'],
                            'reason':'Independent director may choose another test'},
          'model_kind':self.kind,'declared_name':None}

class Advisor:
    def __init__(self,value):self.value=value;self.calls=[]
    def advise(self,brief,witnesses):
        self.calls.append((brief,copy.deepcopy(witnesses)))
        return copy.deepcopy(self.value)

class SynthesisTests(unittest.TestCase):
 def setUp(self):self.catalog=enumerate_semantics()
 def test_full_grammar_closure_is_eight_semantics(self):
    self.assertEqual(len(self.catalog),8)
    self.assertEqual(len(set(x['signature'] for x in self.catalog)),8)
    self.assertTrue(all(x['nodes']<=19 and x['depth']<=4 for x in self.catalog))
    for c in self.catalog:validate_expr(c['expression'])
 def test_classical_solves_four_different_tasks_with_two_probes(self):
    for task in ('flip','intersection','drain','replace'):
      with self.subTest(task=task):
        result=classical_cegis(task)
        self.assertEqual(result['status'],'REVIEW_CANDIDATE_NOT_INSTALLED')
        self.assertEqual(result['oracle_calls'],2)
        self.assertEqual(result['frozen_full_domain_passed'],64)
        self.assertFalse(result['installed'])
 def test_outside_grammar_is_detected_before_frozen_audit(self):
    x=classical_cegis('invert')
    self.assertEqual(x['status'],'HOLD_GRAMMAR_INADEQUATE')
    self.assertEqual(x['oracle_calls'],1)
    self.assertEqual(x['development_witnesses'][0]['on_mask'],0)
    self.assertEqual(x['development_witnesses'][0]['observed_mask'],7)
    self.assertIsNone(x['candidate_expression'])
    # All ASTs built from union/difference of empty sets yield empty set.
    self.assertTrue(all(c['signature'][0]==0 for c in self.catalog))
 def test_one_probe_budget_properly_holds(self):
    x=classical_cegis('flip',oracle_budget=1)
    self.assertEqual(x['status'],'HOLD_AMBIGUOUS_WITHIN_PROBE_BUDGET')
    self.assertEqual(x['oracle_calls'],1)
 def test_llm_is_original_source_of_its_candidate(self):
    model=Responder([candidate('GROW')['expression'], candidate('FLIP')['expression']])
    x=llm_cegis('flip',model)
    self.assertEqual(x['status'],'REVIEW_MODEL_CANDIDATE_NOT_INSTALLED')
    self.assertEqual(x['model_call_count'],2)
    self.assertEqual(x['independent_oracle_calls'],2)
    self.assertEqual(x['frozen_full_domain_passed'],64)
    self.assertEqual(x['model_sourced_final_expression'],candidate('FLIP')['expression'])
    self.assertEqual(model.calls[1]['dev_feedback'][0]['oracle_expected'],0)
    self.assertFalse(x['installed'])
 def test_llm_repeats_refuted_candidates_within_fixed_budget(self):
    d=candidate('DRAIN')['expression']
    x=llm_cegis('flip',Responder([d,d,d]),model_budget=3)
    self.assertEqual(x['status'],'HOLD_MODEL_BUDGET_EXHAUSTED')
    self.assertEqual(x['model_call_count'],3)
    self.assertEqual(x['independent_oracle_calls'],2)
    self.assertEqual(x['model_steps'][-1]['disposition'],'VETO_CONTRADICTS_PRIOR_DEV')
    self.assertIsNone(x['model_sourced_final_expression'])
 def test_syntactic_rewrite_does_not_escape_witness(self):
    grow=op('union',r('state.on'),r('arrival.toggles'))
    rewritten=op('union',grow,r('arrival.toggles'))
    x=llm_cegis('flip',Responder([grow,grow,rewritten]),model_budget=3)
    self.assertEqual(x['status'],'HOLD_MODEL_BUDGET_EXHAUSTED')
    self.assertEqual(x['model_steps'][-1]['disposition'],'VETO_CONTRADICTS_PRIOR_DEV')
 def test_hybrid_does_not_call_llm_when_classical_is_sufficient(self):
    advisor=Advisor({'missing_primitive':'complement','reason':'Review only never executed.'})
    x=hybrid_cegis('intersection',advisor)
    self.assertEqual(x['status'],'REVIEW_CANDIDATE_NOT_INSTALLED')
    self.assertFalse(x['advisor_invoked'])
    self.assertEqual(advisor.calls,[])
 def test_hybrid_advises_but_cannot_extend_language(self):
    advisor=Advisor({'missing_primitive':'complement','reason':'Cannot make a bit ON when both operands were empty.'})
    x=hybrid_cegis('invert',advisor)
    self.assertTrue(x['advisor_invoked'])
    self.assertEqual(x['status'],'HOLD_GRAMMAR_EXTENSION_REVIEW')
    self.assertFalse(x['grammar_extended'])
    self.assertFalse(x['installed'])
    self.assertEqual(x['independent_oracle_calls'],1)
 def test_hybrid_invalid_advice_holds(self):
    advisor=Advisor({'missing_primitive':'exec_python','reason':'run arbitrary code'})
    x=hybrid_cegis('invert',advisor)
    self.assertEqual(x['status'],'HOLD_GRAMMAR_INADEQUATE')
    self.assertIsNone(x['advisor_recommendation_unverified'])
 def test_invalid_model_proposal_never_promoted(self):
    class Evil:
      calls=[]
      def propose(self,brief,feedback=()):return {'schema':'WRONG','python':'import os'}
    x=llm_cegis('flip',Evil())
    self.assertEqual(x['status'],'HOLD_INVALID_MODEL_REPLY')
    self.assertIsNone(x['model_sourced_final_expression'])
 def test_unseen_set_task_matrix_is_accurate_and_nonexecuting(self):
    x=offline_matrix();self.assertEqual(x['solved'],4)
    self.assertEqual(x['grammar_inadequate'],1)
    self.assertEqual(x['total_oracle_calls'],9)
    self.assertEqual(x['grammar_distinct_functions'],8)
    self.assertFalse(x['installed'])
 def test_receipt_integrity(self):
    report=llm_cegis('drain',Responder([candidate('DRAIN')['expression']]*3))
    self.assertEqual(digest({k:v for k,v in report.items() if k!='receipt_digest'}),report['receipt_digest'])
    self.assertFalse(report['model_frozen_test_access'])
 def test_bad_oracle_inputs_rejected(self):
    for task in ('fake',None):
        with self.assertRaises(ValueError):independent_oracle(task,0,1)
    with self.assertRaises(ValueError):independent_oracle('flip',True,1)
    with self.assertRaises(ValueError):classical_cegis('flip',oracle_budget=0)
 def test_model_task_prompt_contains_spec_not_answer(self):
    m=GeneralTaskModel('test-llm:1b')
    p=m._instruction(TASKS['intersection'],())
    self.assertIn('pure',p.lower());self.assertIn('marked by this event',p)
    self.assertNotIn('independent_oracle',p)
    with self.assertRaises(Exception):m._instruction('x',())

class TransportTests(unittest.TestCase):
 def test_actual_loopback_client_uses_synthetic_http_server_not_a_real_llm(self):
    from test_direct_model import ServerFixture, suggestion
    with ServerFixture([suggestion('GROW'),suggestion('FLIP')]) as fixture:
        class LocalTestModel(GeneralTaskModel,fixture.Model):pass
        result=llm_cegis('flip',LocalTestModel('test-llm:0.5b'))
        self.assertEqual(result['status'],'REVIEW_MODEL_CANDIDATE_NOT_INSTALLED')
        self.assertEqual(result['model_call_count'],2)
        self.assertEqual(len(result['model_receipts']),2)
        self.assertTrue(all(x['http_generation_completed'] for x in result['model_receipts']))
        posts=[r for r in fixture.http.record if r[0]=='POST']
        self.assertEqual(len(posts),2)
        self.assertIn('reverses its ON/OFF status',posts[0][2]['prompt'])
        self.assertNotIn('frozen_full_domain_passed',posts[1][2]['prompt'])

if __name__=='__main__': unittest.main()
