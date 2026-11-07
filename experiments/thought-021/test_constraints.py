"""Offline adversarial tests; synthetic responders are NOT generative models."""
from __future__ import annotations
import copy
import json
import unittest
from constraints import (WitnessLedger, ConstraintGuidedModel, ConstraintError,
                         run_arm, comparison, _bit_rows)
from research_model import candidate,MODEL_SCHEMA
from program import digest

BRIEF=('Investigate transitions when arriving at a node can turn a switch '
 'off as well as on. Propose a mechanism and a discriminating test. '
 'Do not change source code or claim authority.')

def reply(name):
    return {'schema':MODEL_SCHEMA,'mechanism':candidate(name),
        'suggested_test':{'on':['red'],'toggles':['red'],
          'reason':'Check the status of a repeated switch'},
        'model_kind':'SYNTHETIC_FAKE_NOT_LLM','declared_name':name}

class Scripted:
    kind='SYNTHETIC_FAKE_NOT_LLM'
    def __init__(self, names=('GROW','DRAIN','FLIP')):
        self.names=list(names);self.calls=[]
    def propose(self, brief, feedback=()):
        self.calls.append({'brief':brief,'feedback':copy.deepcopy(feedback),
                           'real_model_inference':False})
        return reply(self.names[min(len(self.calls)-1,len(self.names)-1)])

class ConstraintTests(unittest.TestCase):
    def test_each_witness_is_a_finite_observation_not_general_law(self):
        w=WitnessLedger()
        self.assertTrue(w.observe({'on_mask':3,'toggles_mask':5,'oracle_expected':6,
             'observed_result':7,'disposition':'REFUTED_ON_DEV','mechanism':'GROW'}))
        self.assertEqual(w.count,1)
        self.assertEqual(w.facts()[0]['observed_bit_rows'],(
            {'color':'red','previous':True,'event':True,'observed_next':False},
            {'color':'blue','previous':True,'event':False,'observed_next':True},
            {'color':'green','previous':False,'event':True,'observed_next':True}))
        self.assertFalse(w.satisfies(candidate('GROW')))
        self.assertFalse(w.satisfies(candidate('DRAIN')))
        self.assertTrue(w.satisfies(candidate('FLIP')))
        self.assertEqual(w.violations(candidate('DRAIN'))[0]['proposal_output_mask'],2)
        self.assertFalse(w.observe({'on_mask':3,'toggles_mask':5,'oracle_expected':6,
             'observed_result':7,'disposition':'REFUTED_ON_DEV','mechanism':'GROW'}))
        self.assertEqual(w.count,1)

    def test_contradictory_claimed_observation_fails_closed(self):
        w=WitnessLedger();a={'on_mask':3,'toggles_mask':5,'oracle_expected':6,
           'observed_result':7,'disposition':'REFUTED_ON_DEV','mechanism':'GROW'}
        w.observe(a)
        with self.assertRaisesRegex(ConstraintError,'CONTRADICTORY'):
            w.observe({**a,'oracle_expected':7})
        with self.assertRaises(Exception):w.observe({**a,'audit_label':'FLIP'})
        with self.assertRaises(Exception):w.observe({**a,'oracle_expected':True})

    def test_constraint_guidance_screening_reduces_wasted_dev_probes(self):
        control=run_arm(Scripted(),BRIEF,mode='control',max_calls=3,graph=False)
        guided=run_arm(Scripted(),BRIEF,mode='constraint',max_calls=3,graph=False)
        self.assertEqual(guided['model_generations'],3)
        self.assertEqual(guided['constraints_observed'],1)
        self.assertEqual(guided['constraint_veto_count'],1)
        self.assertEqual(guided['director_dev_probes'],1)
        self.assertLess(guided['director_dev_probes'],control['director_dev_probes'])
        self.assertEqual(guided['selected_mechanism'],'FLIP')
        self.assertEqual(guided['status'],'MECHANISM_VERIFIED_ON_FINITE_TRUTH_TABLE_NOT_INSTALLED')
        self.assertEqual(guided['model_notes'][0]['violations'][0]['proposal_output_mask'],2)
        self.assertFalse(guided['installed'])

    def test_correct_model_candidate_kept_and_full_independent_audit(self):
        out=run_arm(Scripted(['FLIP']),BRIEF,mode='constraint',max_calls=3,graph=True)
        self.assertEqual(out['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
        self.assertEqual(out['director_report']['dev_truth_table'],{'passed':64,'total':64})
        self.assertEqual(out['director_report']['frozen_graph_audit'],{'passed':60,'total':60})
        self.assertEqual(out['director_report']['stress_graph_audit'],{'passed':80,'total':80})
        self.assertEqual(out['model_generations'],1)
        self.assertEqual(out['constraints_observed'],0)
        self.assertFalse(out['installed'])

    def test_repeating_bad_model_never_gets_oracle_fabrication_or_patch(self):
        out=run_arm(Scripted(['GROW']),BRIEF,mode='constraint',max_calls=3,graph=False)
        self.assertEqual(out['model_generations'],3)
        self.assertEqual(out['constraint_veto_count'],2)
        self.assertEqual(out['director_dev_probes'],1)
        self.assertEqual(out['status'],'HOLD_NO_VERIFIED_MODEL_PROPOSAL')
        self.assertIsNone(out['candidate'])
        self.assertFalse(out['installed'])

    def test_malformed_feedback_outside_dev_context_refused(self):
        m=ConstraintGuidedModel(Scripted(),mode='constraint',max_calls=3)
        bad=[{'mechanism':'GROW','on_mask':3,'toggles_mask':5,
             'oracle_expected':6,'observed_result':7,
             'disposition':'REFUTED_ON_DEV','hidden_audit':'leaked'}]
        with self.assertRaises(Exception):m.propose(BRIEF,bad)
        self.assertEqual(m.model_generations,0)
        with self.assertRaises(ConstraintError):m.propose('deploy')

    def test_feedback_cannot_precede_candidate_or_rewind(self):
        m=ConstraintGuidedModel(Scripted(['GROW']),max_calls=3)
        f={'mechanism':'GROW','on_mask':3,'toggles_mask':5,
             'oracle_expected':6,'observed_result':7,'disposition':'REFUTED_ON_DEV'}
        with self.assertRaises(ConstraintError):m.propose(BRIEF,[f])
        m.propose(BRIEF)
        m.propose(BRIEF,[f])
        with self.assertRaises(ConstraintError):m.propose(BRIEF,[])

    def test_no_correct_answer_leaked_to_model_feedback(self):
        model=Scripted(['GROW','DRAIN','FLIP'])
        run_arm(model,BRIEF,mode='constraint',max_calls=3,graph=False)
        self.assertEqual(len(model.calls),3)
        for call in model.calls:
            packet=json.dumps(call)
            self.assertNotIn('FLIP',packet)
            self.assertNotIn('frozen_graph_audit',packet)
            self.assertNotIn('surviving_reviewed_hypotheses',packet)
            self.assertNotIn('hidden_audit',packet)
        self.assertIn('MUST satisfy',model.calls[1]['brief'])

    def test_all_three_arms_same_call_ceiling_and_zero_authority(self):
        out=comparison(Scripted,BRIEF,max_calls=3,graph=False)
        self.assertEqual(set(out['runs']),{'control','semantic','constraint'})
        self.assertEqual(out['model_inference_limit_per_arm'],3)
        for arm in out['runs'].values():
            self.assertLessEqual(arm['model_generations'],3)
            self.assertEqual(arm['external_authority'],'NONE')
            self.assertFalse(arm['installed'])
            self.assertEqual(arm['receipt_digest'],digest({k:v for k,v in arm.items() if k!='receipt_digest'}))
        self.assertEqual(out['receipt_digest'],digest({k:v for k,v in out.items() if k!='receipt_digest'}))

    def test_invalid_config_rejected(self):
        for v in (0,7,True,-1):
            with self.assertRaises(ConstraintError):ConstraintGuidedModel(Scripted(),max_calls=v)
        with self.assertRaises(ConstraintError):ConstraintGuidedModel(Scripted(),mode='root-shell')
        with self.assertRaises(ConstraintError):comparison(None,BRIEF)

    def test_actual_http_fixture_without_claiming_real_llm(self):
        from test_direct_model import ServerFixture, suggestion
        with ServerFixture([suggestion('GROW'),suggestion('DRAIN'),suggestion('FLIP')]) as stub:
            backend=stub.Model('test-llm:0.5b')
            out=run_arm(backend,BRIEF,mode='constraint',max_calls=3,graph=False)
            self.assertEqual(out['model_generations'],3)
            self.assertEqual(out['constraint_veto_count'],1)
            self.assertEqual(out['status'],'MECHANISM_VERIFIED_ON_FINITE_TRUTH_TABLE_NOT_INSTALLED')
            self.assertEqual(len(out['model_receipts']),3)
            self.assertTrue(all(c['http_generation_completed'] for c in out['model_receipts']))
            self.assertFalse(out['installed'])

if __name__=='__main__':unittest.main()
