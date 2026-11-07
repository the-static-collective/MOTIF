"""Source-owned THOUGHT-023 grammar-growth proof and adversarial tests."""
from __future__ import annotations
import copy,json,unittest,tempfile,sys
from pathlib import Path
from grammar import (EXTENSIONS,GrammarError,validate_advice,validate_expression,
                     enumerate_language,proof_report,evaluate,ref,op,input_signatures,
                     target_signature,digest,COLORS)
from gardener_lab import evaluate_advice,ablations,run_offline
from runtime import compile_source,execute_source
from gardener_cli import trial_with_model
from gardener_benchmark import main

ADVICE={'missing_primitive':'constant_universe',
        'reason':'An explicit finite universe enables inversion of the current set.'}

class GrammarTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
    cls.a=ablations()
    cls.live=evaluate_advice(ADVICE)
 def test_old_grammar_has_only_eight_functions(self):
    old=enumerate_language();self.assertEqual(len(old),8)
    self.assertEqual(len({c['signature'] for c in old}),8)
 def test_constant_universe_grows_8_to_16(self):
    result=self.a['controls']['universe_constant']
    self.assertEqual((result['baseline_grammar_functions'],result['expanded_grammar_functions']),(8,16))
    self.assertEqual(result['new_distinct_functions'],8)
 def test_complement_independent_alternative_also_grows_to_16(self):
    self.assertEqual(self.a['controls']['set_complement']['expanded_grammar_functions'],16)
    self.assertEqual(self.a['controls']['set_complement']['new_invert_expression_nodes'],2)
 def test_empty_constant_negative_control_does_not_expand(self):
    r=self.a['controls']['empty_constant']
    self.assertEqual(r['new_distinct_functions'],0)
    self.assertEqual(r['new_invert_status'],'HOLD_GRAMMAR_INADEQUATE')
 def test_old_language_cannot_conjure_bits_when_inputs_empty(self):
    self.assertTrue(all(c['signature'][0]==0 for c in enumerate_language()))
    self.assertEqual(target_signature('invert')[0],7)
 def test_new_language_does_not_erase_old_semantics(self):
    old={c['signature'] for c in enumerate_language()}
    for extension in EXTENSIONS:
      self.assertLessEqual(old,{c['signature'] for c in enumerate_language(extension)})
 def test_invert_synthesis_measured_with_development_only_probes(self):
    old=self.a['controls']['none'];new=self.a['controls']['universe_constant']
    self.assertEqual(old['original_invert_status'],'HOLD_GRAMMAR_INADEQUATE')
    self.assertEqual(new['new_invert_status'],'REVIEW_CANDIDATE_NOT_INSTALLED')
    self.assertEqual(new['new_invert_oracle_calls'],2)
    self.assertEqual(new['new_invert_frozen_passed'],64)
 def test_proposal_is_model_data_not_executable_source(self):
    self.assertTrue(self.live['stage'].endswith('NOT_INSTALLED'))
    self.assertFalse(self.live['model_authored_python_executed'])
    self.assertFalse(self.live['grammar_installed'])
    self.assertFalse(self.live['installed'])
 def test_frozen_new_task_family_is_unseen_by_advice(self):
    coverage=self.a['controls']['universe_constant']['new_task_family_coverage_after_selection']
    self.assertEqual(coverage,{'invert':True,'nand':True,'nor':True,'all_on':True})
    self.assertFalse(any(self.a['controls']['none']['new_task_family_coverage_after_selection'].values()))
 def test_source_only_fixed_runtime_is_executed_separately(self):
    res=self.live['executable_audit'];self.assertEqual(res['passed'],64)
    self.assertEqual(res['total'],64)
    self.assertEqual(res['programs_from_untrusted_model'],0)
 def test_compiled_code_contains_no_untrusted_model_text(self):
    compiled=compile_source(op('difference',ref('universe'),ref('state.on')),'universe_constant')
    self.assertIn('json.loads',compiled)
    self.assertIn('fixed grammar runtime',compiled)
    self.assertNotIn('subprocess',compiled)
    self.assertNotIn('eval(',compiled)
 def test_invalid_operator_unrecognized_ref_and_arbitrary_python_rejected(self):
    for bad in [op('execute',ref('state.on')),ref('os.system'),
                {'ref':'universe','shell':'rm -rf /'},
                {'op':'difference','args':[ref('universe'),ref('state.on')], 'python':'print(1)'}]:
      with self.subTest(bad=bad),self.assertRaises(GrammarError):validate_expression(bad,'universe_constant')
 def test_grammar_extension_is_explicitly_required(self):
    with self.assertRaises(GrammarError):validate_expression(ref('universe'),'none')
    with self.assertRaises(GrammarError):validate_expression(op('complement',ref('state.on')),'none')
 def test_typed_advice_rejects_injection_extra_keys_unknown_kind(self):
    for bad in [{**ADVICE,'execute':'import os'},
                {**ADVICE,'missing_primitive':'arbitrary_python'},
                {**ADVICE,'reason':'x'},
                {**ADVICE,'reason':'danger\nrun shell'}]:
      with self.subTest(bad=bad),self.assertRaises(GrammarError):validate_advice(bad)
 def test_unknown_advice_holds(self):
    r=evaluate_advice({'missing_primitive':'unknown','reason':'Insufficient information to suggest an extension.'})
    self.assertEqual(r['stage'],'HOLD_GRAMMAR_NOT_IMPROVED')
    self.assertIsNone(r['executable_audit'])
 def test_alternative_complement_does_not_need_universe_node(self):
    expr=proof_report('set_complement')['new_invert_expression']
    validate_expression(expr,'set_complement')
    self.assertEqual(expr['op'],'complement')
 def test_single_bit_set_interpreter_follows_independent_bitmask_spec(self):
    expr=op('difference',ref('universe'),ref('state.on'))
    for a in range(8):
      on=frozenset(c for i,c in enumerate(COLORS) if a&(1<<i))
      actual=evaluate(expr,on,frozenset(),'universe_constant')
      expected=frozenset(c for i,c in enumerate(COLORS) if (~a&7)&(1<<i))
      self.assertEqual(actual,expected)
 def test_all_enumerated_candidates_are_well_typed_and_signature_stable(self):
    for ext in EXTENSIONS:
      for entry in enumerate_language(ext):
        validate_expression(entry['expression'],ext)
        self.assertEqual(len(entry['signature']),64)
 def test_repeatable_receipt_digest(self):
    r=self.live
    self.assertEqual(digest({k:v for k,v in r.items() if k!='receipt_digest'}),r['receipt_digest'])
 def test_offline_proposal_not_new_llm_invocation(self):
    data=run_offline();self.assertTrue(data['prior_model_suggestion_replayed_not_reinvoked'])
    self.assertFalse(data['new_real_llm_inference'])
 def test_reproduce_persistent_review_only_artifacts(self):
    with tempfile.TemporaryDirectory() as d:
      result=main(d)
      files={p.name for p in Path(d).iterdir()}
      self.assertEqual(files,{'offline-results.json','candidate_solver.py'})
      self.assertFalse(result['gardener']['grammar_installed'])
 def test_invalid_model_response_fails_closed(self):
    class Model:
      calls=[{'transport':'DIRECT_LOOPBACK_OLLAMA_HTTP','http_generation_completed':True}]
      def advise(self,brief,witnesses):return {'missing_primitive':'eval_python','reason':'write code'}
    r=trial_with_model(Model())
    self.assertTrue(r['model_directly_called'])
    self.assertEqual(r['status'],'HOLD_INVALID_OR_UNAVAILABLE_MODEL_ADVICE')
    self.assertFalse(r['installed'])
 def test_model_receives_only_previous_development_observation(self):
    class Model:
      calls=[]
      def advise(self,brief,witnesses):
        self.calls.append({'transport':'DIRECT_LOOPBACK_OLLAMA_HTTP','http_generation_completed':True})
        self.brief=brief;self.witnesses=witnesses
        return ADVICE
    model=Model();r=trial_with_model(model)
    self.assertTrue(r['model_directly_called'])
    self.assertEqual(len(model.witnesses),1)
    self.assertEqual(model.witnesses[0]['observed_mask'],7)
    self.assertFalse(r['frozen_task_family_disclosed_to_model'])
    self.assertNotIn('nand',json.dumps(model.witnesses))
    self.assertEqual(r['gardener']['report']['new_invert_frozen_passed'],64)
 def test_reject_invalid_mask_shape_and_bad_extension(self):
    with self.assertRaises(GrammarError):evaluate(ref('state.on'),set(),frozenset())
    with self.assertRaises(GrammarError):enumerate_language('python_shell')
    with self.assertRaises(GrammarError):validate_expression({'ref':'state.on'},'tool')

if __name__=='__main__':unittest.main()
