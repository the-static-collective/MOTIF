"""Regression and epistemic honesty checks for scoped proof-carrying memory."""
import copy,json,unittest
from proof_memory import (ProofLibrary,ProofError,certify,verify_card,
                          identifiable_stages,retain_hypotheses,digest)
from reuse import reuse,compose_difference_union,build_candidates
from ingest import ingest_report
from stages import stage_trial
from stage_fixtures import DeterministicStages
from specimens import BY_KEY

class ProofMemoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library=ProofLibrary();cls.proofs={}
        for key in ('food_safe','volunteer_eligible','food_donations','not_on_shelf'):
            task=BY_KEY[key]
            actual=stage_trial(task,DeterministicStages())
            cls.proofs[key]=cls.library.admit(task,actual,
                origin='SCRIPTED_TEST_FIXTURE_NOT_A_LIVE_LLM')

    def test_certificates_recheck_the_oracle_and_fixed_runtime(self):
        self.assertEqual(len(self.proofs),4)
        self.assertTrue(self.library.recheck_all(BY_KEY))
        for key,card in self.proofs.items():
            self.assertTrue(verify_card(BY_KEY[key],card))
            self.assertEqual(card['full_domain_cases_passed'],64)
            self.assertEqual(card['trusted_template_cases_passed'],64)
            self.assertTrue(card['individual_stage_correctness_not_assumed'])
            self.assertFalse(card['learned_meaning_from_human_language_proven'])
            self.assertFalse(card['installed'])

    def test_symmetric_intersection_cannot_claim_correct_input_roles(self):
        card=self.proofs['volunteer_eligible']
        ident=card['identifiability']
        self.assertEqual(ident['binding_status'],'UNDERDETERMINED')
        self.assertEqual(ident['relation_status'],'SUPPORTED_ON_FINITE_WORLD')
        self.assertEqual(ident['compatible_pair_count'],2)

    def test_noncommutative_difference_allows_a_unique_binding(self):
        card=self.proofs['food_safe']
        self.assertEqual(card['identifiability']['binding_status'],'SUPPORTED_ON_FINITE_WORLD')
        self.assertEqual(card['identifiability']['relation_status'],'SUPPORTED_ON_FINITE_WORLD')
        self.assertEqual(card['identifiability']['compatible_pair_count'],1)

    def test_incorrect_program_cannot_be_promoted_even_with_forged_status(self):
        t=BY_KEY['food_safe']
        wrong=stage_trial(t,DeterministicStages(incorrect_binding=True),repair=False)
        fake=copy.deepcopy(wrong)
        fake['status']='CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED'
        with self.assertRaises(ProofError):certify(t,fake)

    def test_report_tamper_or_changed_task_is_refused(self):
        orig=self.proofs['food_safe']
        tamper=copy.deepcopy(orig)
        tamper['relation']='UNION'
        with self.assertRaises(ProofError):verify_card(BY_KEY['food_safe'],tamper)
        # Even a newly recomputed SHA over a forged claim cannot beat oracle.
        tamper['proof_digest']=digest({k:v for k,v in tamper.items() if k!='proof_digest'})
        with self.assertRaises(ProofError):verify_card(BY_KEY['food_safe'],tamper)
        with self.assertRaises(ProofError):verify_card(BY_KEY['food_recalled_elsewhere'],orig)

    def test_no_promotion_for_unverified_fragments(self):
        t=BY_KEY['food_safe']
        wrong=stage_trial(t,DeterministicStages(incorrect_binding=True),repair=False)
        tentative=retain_hypotheses(t,wrong)
        self.assertFalse(tentative['eligible_for_reuse'])
        self.assertEqual(tentative['relation_hypothesis'],'DIFFERENCE')
        self.assertTrue(tentative['dev_failed'])
        with self.assertRaises(ProofError):self.library.admit(t,wrong)

    def test_proof_guided_reuse_transfers_to_second_domain(self):
        t=BY_KEY['reverse_outreach']
        result=reuse(t,self.library,BY_KEY)
        self.assertEqual(result['status'],'REVIEW_REUSE_CANDIDATE_NOT_INSTALLED')
        self.assertGreaterEqual(result['oracle_queries'],2)
        self.assertLessEqual(result['oracle_queries'],4)
        self.assertEqual(result['frozen']['correct'],64)
        self.assertEqual(result['fixed_template_execution']['correct'],64)
        self.assertFalse(result['new_task_roles_inferred_from_language'])
        self.assertFalse(result['installed'])

    def test_reverse_role_mapping_reused_not_assumed(self):
        t=BY_KEY['food_recalled_elsewhere']
        r=reuse(t,self.library,BY_KEY)
        self.assertEqual(r['status'],'REVIEW_REUSE_CANDIDATE_NOT_INSTALLED')
        self.assertEqual(r['frozen']['correct'],64)
        self.assertEqual(r['selected_expression']['bindings']['current'],'register_g')

    def test_nonboolean_task_is_not_silently_coerced(self):
        r=reuse(BY_KEY['unknown_beliefs'],self.library,BY_KEY)
        self.assertEqual(r['status'],'HOLD_NON_BOOLEAN_OR_AMBIGUOUS')
        self.assertEqual(r['oracle_queries'],0)

    def test_two_dev_witnesses_do_not_establish_general_truth(self):
        r=reuse(BY_KEY['cancel_or_add'],self.library,BY_KEY)
        self.assertEqual(r['status'],'HOLD_FROZEN_COUNTEREXAMPLE')
        self.assertEqual(r['oracle_queries'],2)
        self.assertLess(r['frozen']['correct'],64)
        self.assertFalse(r['installed'])

    def test_evidence_components_can_make_a_new_tested_composition(self):
        r=compose_difference_union(BY_KEY['cancel_or_add'],
              self.proofs['food_safe'],self.proofs['food_donations'],BY_KEY)
        self.assertEqual(r['status'],'REVIEW_COMPOSED_CANDIDATE_NOT_INSTALLED')
        self.assertEqual(r['frozen']['correct'],64)
        self.assertEqual(r['source_owned_runtime']['correct'],64)
        self.assertEqual(r['oracle_queries'],4)
        self.assertFalse(r['installed'])

    def test_cannot_compose_unproven_relation_or_unknown_origin(self):
        with self.assertRaises(ProofError):compose_difference_union(
            BY_KEY['cancel_or_add'],self.proofs['volunteer_eligible'],
            self.proofs['food_donations'],BY_KEY)
        with self.assertRaises(ProofError):build_candidates(
            BY_KEY['food_safe'],[self.proofs['food_safe']],known_tasks={})

    def test_budgets_are_strict(self):
        for size in (0,7,True):
            with self.assertRaises(ProofError):reuse(BY_KEY['food_safe'],self.library,BY_KEY,query_budget=size)

    def test_importer_recertifies_success_and_holds_unverified(self):
        success=stage_trial(BY_KEY['food_safe'],DeterministicStages())
        failed=stage_trial(BY_KEY['food_recalled_elsewhere'],
                           DeterministicStages(incorrect_binding=True),repair=False)
        r=ingest_report({'schema':'motif.thought026.staged-experiment.v1',
              'backend':'ollama',
              'results':{'food_safe':success,'food_recalled_elsewhere':failed}})
        self.assertIn('food_safe',r['certified'])
        self.assertIn('food_recalled_elsewhere',r['unverified_fragments'])
        self.assertFalse(r['origin_cryptographically_authenticated'])
        self.assertFalse(r['language_meaning_globally_certified'])
        self.assertFalse(r['installed'])

    def test_importer_rejects_forged_026_success(self):
        wrong=stage_trial(BY_KEY['food_safe'],DeterministicStages(incorrect_binding=True),repair=False)
        wrong['status']='CANDIDATE_ABSTRACTION_FOR_HUMAN_REVIEW_NOT_INSTALLED'
        r=ingest_report({'schema':'motif.thought026.staged-experiment.v1',
             'backend':'ollama','results':{'food_safe':wrong}})
        self.assertEqual(len(r['certified']),0)
        self.assertIn('food_safe',r['rejected'])

    def test_no_drift_in_026_proof_contract(self):
        output=stage_trial(BY_KEY['food_donations'],DeterministicStages())
        self.assertEqual(output['frozen']['correct'],64)
        self.assertEqual(output['fixed_template_program']['correct'],64)
        self.assertEqual(self.proofs['food_donations']['relation'],'UNION')

if __name__=='__main__':unittest.main()
