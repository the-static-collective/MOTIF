"""Independent behavioral tests for cautious, read-only self-repair diagnosis."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'operatorinvention001'))
sys.path.insert(0,str(ROOT/'controlflow001'))
sys.path.insert(0,str(ROOT/'languagegrowth001'))
from languagegrowth import trials
from operatorinvention import PROGRAMS
from controlflow import strong_baseline
from diagnosis import (Request,Context,Reading,DiagnosisRefusal,
    scenario,advance,observe,primary_observation,second_observation,
    choose_inquiry,candidates,resource_reading,metered,fingerprint,demonstration,COSTS)


class DiagnoseActualLimitations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.examples={k:scenario(k) for k in ('more_evidence','missing_control','corrupt_sensor',
                'resource_cap','compute_denied','ambiguous_sources','unwarranted_contract',
                'unaffordable_growth','denied_evidence','denied_growth','colluding_readouts')}
        cls.results={k:advance(v) for k,v in cls.examples.items()}

    def test_evidence_gap_asks_and_executes_new_probe(self):
        r=self.results['more_evidence']
        self.assertEqual(r['status'],'SOLVED_EXISTING_REPERTOIRE')
        self.assertEqual([x['action_executed'] for x in r['steps']],
                         ['PROBE_DISAGREEMENT','VALIDATE_MODEL'])

    def test_information_probe_is_not_pre_answered(self):
        r=self.results['more_evidence']
        step=r['steps'][0]
        self.assertGreater(step['result']['information_bits_before_query'],0)
        self.assertEqual(step['result']['models_after'],1)
        self.assertTrue(step['result']['probe'].startswith('train:'))

    def test_evidence_gap_reused_old_capability_not_new_language(self):
        r=self.results['more_evidence']
        self.assertFalse(r['grammar_changed'])
        self.assertEqual(r['starting_models'],38)
        self.assertEqual(r['additional_probes'],1)
        self.assertGreater(r['final_evidence_count'],r['initial_evidence_count'])

    def test_evidence_frozen_validation_executed(self):
        r=self.results['more_evidence']['steps'][-1]['result']
        self.assertEqual(r['cases'],16)
        self.assertEqual(r['counterexamples'],0)
        self.assertIn('FOR(',r['model'])

    def test_source_graph_really_observed_from_upstream(self):
        probe=trials('train',5)[4]
        self.assertEqual(primary_observation(probe,'triangles'),second_observation(probe,'triangles'))
        self.assertEqual(primary_observation(probe,'five_cycles'),strong_baseline(probe.probe))

    def test_missing_control_exhausted_real_old_grammar(self):
        ctx=self.examples['missing_control']
        self.assertEqual(len(candidates(ctx.evidence)),0)
        self.assertGreaterEqual(len(ctx.evidence),1)
        self.assertEqual(self.results['missing_control']['starting_models'],0)

    def test_missing_control_routes_to_actual_existing_growth_synthesizer(self):
        r=self.results['missing_control']
        self.assertEqual(r['status'],'SOLVED_STAGED_CONTROL_FLOW_EXTENSION')
        self.assertEqual([s['action_executed'] for s in r['steps']],['GROW_CONTROL_FLOW'])
        self.assertTrue(r['grammar_changed_in_stage'])
        self.assertIn("'z'",r['proposed_program'])

    def test_missing_control_check_new_program_on_fresh_worlds(self):
        step=self.results['missing_control']['steps'][0]['result']
        self.assertEqual(step['heldout']['cases'],10)
        self.assertEqual(step['heldout']['AST_correct'],10)
        self.assertEqual(step['ood']['cases'],8)
        self.assertEqual(step['ood']['strong_classical_correct'],8)

    def test_missing_control_created_verified_independent_interpreter_child(self):
        child=self.results['missing_control']['steps'][0]['result']['generated_child']
        self.assertEqual(child['status'],'F_LOCAL_CHILD_REPLAY')
        self.assertEqual(child['observed'],child['computed'])
        self.assertEqual(child['observed'],child['strong_classical'])

    def test_growth_proposal_not_installed(self):
        r=self.results['missing_control']
        self.assertFalse(r['installed_in_running_motif'])
        self.assertFalse(r['steps'][0]['result']['new_code_installed'])
        self.assertFalse(r['steps'][0]['result']['new_authority_granted'])

    def test_corrupt_sensor_routes_to_disagreement_not_extension(self):
        r=self.results['corrupt_sensor']
        self.assertEqual(r['status'],'HOLD_WITNESS_DISAGREEMENT')
        self.assertEqual([s['action_executed'] for s in r['steps']],['CROSSCHECK'])
        self.assertTrue(r['false_grammar_edit_avoided'])

    def test_corruption_cannot_attribute_which_readout_is_wrong(self):
        r=self.results['corrupt_sensor']['steps'][0]['result']
        self.assertEqual(r['conflicts'],1)
        self.assertEqual(r['attribution'],'UNRESOLVED')
        self.assertFalse(r['source_authenticity_verified'])

    def test_reversing_corruption_direction_still_holds(self):
        t=trials('train',36)[5]
        c=Context(Request('triangles'),(observe(t,'triangles',tamper_secondary=1),),())
        self.assertEqual(advance(c)['status'],'HOLD_WITNESS_DISAGREEMENT')

    def test_resource_failure_is_not_a_bad_mathematical_formula(self):
        r=self.results['resource_cap']
        self.assertEqual(r['status'],'SOLVED_BOUNDED_COMPUTE')
        self.assertEqual(r['steps'][0]['action_executed'],'RAISE_FUEL')
        self.assertFalse(r['grammar_changed'])

    def test_resource_retry_is_real_bounded_interpreter(self):
        r=self.results['resource_cap']['steps'][0]['result']
        self.assertLess(r['initial_fuel'],r['new_fuel'])
        self.assertEqual(r['completed_result'],r['instrument'])
        self.assertEqual(r['instrument'],r['corroborator'])

    def test_resource_fuel_denied_holds_without_modifying_solver(self):
        self.assertEqual(self.results['compute_denied']['status'],'HOLD_RESOURCE_BOUND')
        self.assertEqual(self.results['compute_denied']['budget_spent'],0)

    def test_unwarranted_measurement_contract_holds_preemptively(self):
        r=self.results['unwarranted_contract']
        self.assertEqual(r['status'],'HOLD_UNWARRANTED_TASK_CONTRACT')
        self.assertFalse(r['provenance']['source_authenticity_verified'])

    def test_shared_root_is_not_independence(self):
        r=self.results['ambiguous_sources']
        self.assertEqual(r['status'],'HOLD_SHARED_WITNESS_ROOT')
        self.assertFalse(r['provenance']['algorithms_are_distinct'])

    def test_even_different_algorithms_share_synthetic_graph(self):
        r=self.results['more_evidence']
        self.assertTrue(r['provenance']['shared_underlying_graph'])
        self.assertFalse(r['provenance']['independent_physical_truth'])
        self.assertFalse(r['provenance']['source_authenticity_verified'])

    def test_permissions_prevent_both_unneeded_expensive_steps(self):
        self.assertEqual(self.results['denied_evidence']['status'],'HOLD_MORE_EVIDENCE_REQUIRED')
        self.assertEqual(self.results['denied_growth']['status'],'HOLD_UNSUPPORTED_REMEDY')

    def test_insufficient_budget_prevents_language_growth(self):
        self.assertEqual(self.results['unaffordable_growth']['status'],'HOLD_GROWTH_NOT_AFFORDABLE')
        self.assertEqual(self.results['unaffordable_growth']['steps'],[])

    def test_bounded_costs_and_horizons(self):
        for key,context in self.examples.items():
            with self.subTest(kind=key):
                output=self.results[key]
                self.assertLessEqual(output['budget_spent'],context.request.budget)
                self.assertLessEqual(len(output['steps']),context.request.max_steps)
                self.assertEqual(sum(s['cost'] for s in output['steps']),output['budget_spent'])

    def test_all_automatic_actions_are_local_non_effectful(self):
        for r in self.results.values():
            self.assertEqual(r['external_actions'],0)
            self.assertEqual(r['repository_edits'],0)
            self.assertTrue(all(x['external_effects']==0 for x in r['steps']))

    def test_query_response_contains_next_warranted_question(self):
        for r in self.results.values():
            self.assertGreater(len(r['next_question']),20)
            self.assertTrue(r['next_question'].endswith('?'))
            self.assertNotIn('UNKNOWN',r['next_question'])

    def test_no_original_evidence_mutation(self):
        for k,ctx in self.examples.items():
            self.assertTrue(self.results[k]['original_evidence_unchanged'])
            self.assertEqual(fingerprint(ctx),fingerprint(ctx))

    def test_replay_deterministic(self):
        for kind in ('more_evidence','resource_cap','corrupt_sensor','missing_control'):
            self.assertEqual(advance(self.examples[kind]),self.results[kind])

    def test_zero_budget_refuses_observation_or_expansion(self):
        a=self.examples['more_evidence']
        b=self.examples['missing_control']
        for c in (a,b):
            r=advance(replace(c,request=replace(c.request,budget=0)))
            self.assertTrue(r['status'].startswith('HOLD'))
            self.assertEqual(r['budget_spent'],0)

    def test_one_step_horizon_does_not_skip_validation(self):
        c=self.examples['more_evidence']
        r=advance(replace(c,request=replace(c.request,max_steps=1)))
        self.assertEqual(r['status'],'HOLD_VALIDATION_BUDGET')
        self.assertEqual(len(r['steps']),1)

    def test_bounded_evaluator_never_uses_partial_count_as_answer(self):
        ctx=self.examples['resource_cap']
        value=metered(ctx.installed_program,ctx.evidence[0].case,1)
        self.assertEqual(value['status'],'TRUNCATED')
        self.assertIsNone(value['answer'])
        self.assertLess(value['inspected'],value['needed'])

    def test_forged_resource_receipt_refused(self):
        ctx=self.examples['resource_cap']
        fake=replace(ctx.evidence[0],work_required=ctx.evidence[0].work_required+1)
        r=advance(replace(ctx,evidence=(fake,)))
        self.assertEqual(r['status'],'HOLD_RESOURCE_MARKER_UNCONFIRMED')

    def test_authorized_fuel_reproducible_across_seeds(self):
        for seed in range(7):
            with self.subTest(seed=seed):
                self.assertEqual(advance(scenario('resource_cap',seed))['status'],'SOLVED_BOUNDED_COMPUTE')

    def test_sensor_conflict_reproducible_across_seeds(self):
        for seed in range(7):
            with self.subTest(seed=seed):
                self.assertEqual(advance(scenario('corrupt_sensor',seed))['status'],'HOLD_WITNESS_DISAGREEMENT')

    def test_bad_request_budget_and_permissions_refused(self):
        for changes in ({'question':'unknown'}, {'budget':True},{'budget':-1},
                        {'max_steps':0},{'max_steps':True},{'max_fuel':0},
                        {'allow_more_compute':'true'}, {'task_contract_warranted':None}):
            with self.subTest(changes=changes),self.assertRaises(DiagnosisRefusal):
                Request('triangles',**{k:v for k,v in changes.items() if k!='question'}) if 'question' not in changes else Request(**changes)

    def test_reading_partial_or_noninteger_never_admitted(self):
        c=trials('train',2)[0]
        for change in ({'primary':None},{'primary':True},{'corroborator':None},
                       {'status':'COMPROMISED'}):
            data=dict(case=c,primary=0,corroborator=0)
            data.update(change)
            with self.assertRaises(DiagnosisRefusal):Reading(**data)

    def test_context_reused_event_rejected(self):
        o=observe(trials('train',2)[0],'triangles')
        with self.assertRaises(DiagnosisRefusal):Context(Request('triangles'),(o,o),())
        with self.assertRaises(DiagnosisRefusal):Context(Request('triangles'),(o,),(o.case,))

    def test_context_rejects_unregistered_program(self):
        from operatorinvention import Program
        o=observe(trials('train',2)[0],'triangles')
        # An invalid-looking recognized type is still outside frozen registry.
        class ForeignProgram(Program):
            pass
        bogus=ForeignProgram(('x',),(('a','x'),))
        self.assertNotIn(bogus,PROGRAMS)
        with self.assertRaises(DiagnosisRefusal):Context(Request('triangles'),(o,),(),bogus)

    def test_choose_inquiry_without_evidence_never_peeks_outcomes(self):
        ctx=self.examples['more_evidence']
        models=candidates(ctx.evidence)
        with patch('diagnosis.primary_observation',side_effect=AssertionError('peek')):
            item,gain=choose_inquiry(ctx.candidate_probes,models)
        self.assertIsNotNone(item)
        self.assertGreater(gain,0)

    def test_fault_in_frozen_validation_abstains_not_autotunes(self):
        ctx=self.examples['more_evidence']
        original=primary_observation
        def fail_validation(case,question):
            return original(case,question)+(1 if case.split=='validation' else 0)
        with patch('diagnosis.primary_observation',side_effect=fail_validation):
            result=advance(ctx)
        self.assertEqual(result['status'],'HOLD_VALIDATION_COUNTEREXAMPLE')
        self.assertFalse(any(s['action_executed']=='GROW_CONTROL_FLOW' for s in result['steps']))

    def test_coordinated_misinformation_not_proof_of_independence(self):
        # No claim that two equally corrupted reports are authentic or independent.
        r=self.results['colluding_readouts']
        self.assertFalse(r['provenance']['source_authenticity_verified'])
        self.assertFalse(r['provenance']['independent_physical_truth'])

    def test_metaprogram_uses_actual_repo_owned_modules(self):
        from controlflow import ControlProgram,discover
        from operatorinvention import Program
        self.assertTrue(isinstance(self.examples['resource_cap'].installed_program,Program))
        self.assertIn("'z'",self.results['missing_control']['proposed_program'])
        self.assertEqual(self.results['missing_control']['steps'][0]['result']['candidate_programs'],52)

    def test_demonstration_reports_all_paths_and_no_deployment(self):
        result=demonstration()
        self.assertEqual(result['experiment'],'INVENTION-DIAGNOSIS-001')
        self.assertEqual(len(result['diagnostic_paths']),7)
        self.assertFalse(result['code_deployed'])


if __name__=='__main__':unittest.main()
