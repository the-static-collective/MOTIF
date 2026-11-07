"""Tests distinguish synthetic responders from a genuinely invoked generative model."""
from __future__ import annotations
import copy
import json
import unittest
from critic import (CriticError, ModelWithCritic, comparison, dev_only,
                    run_arm, semantic_signature)
from research_model import candidate, MODEL_SCHEMA, PATTERNS
from program import SCHEMA, op, r

BRIEF=('Investigate transitions when arriving at a node can turn a switch '
       'off as well as on. Propose a mechanism and a discriminating test. '
       'Do not change source code or claim authority.')


def response(name):
    return {'schema':MODEL_SCHEMA,'mechanism':candidate(name),
      'suggested_test':{'on':['red'],'toggles':['red'],'reason':'Check reversible switch status'},
      'model_kind':'SYNTHETIC_RESPONSE_NOT_LLM','declared_name':name}


class FixedResponder:
    kind='SYNTHETIC_RESPONSE_NOT_LLM'
    def __init__(self,names):
        self.names=list(names);self.calls=[]
    def propose(self,brief,feedback=()):
        self.calls.append({'prompt':brief,'feedback':copy.deepcopy(feedback),
                           'simulation_only':True})
        return response(self.names[min(len(self.calls)-1,len(self.names)-1)])


class ResponsiveFake(FixedResponder):
    def __init__(self):super().__init__(['GROW','GROW','GROW'])
    def propose(self,brief,feedback=()):
        self.calls.append({'prompt':brief,'feedback':copy.deepcopy(feedback),
                           'simulation_only':True})
        return response('FLIP' if 'Do not repeat that transition function' in brief else 'GROW')


class CriticTests(unittest.TestCase):
    def test_semantics_not_string_equivalence(self):
        old = candidate('GROW')
        syntax_altered=copy.deepcopy(old)
        syntax_altered['expression']=op('union',
          op('union',r('state.on'),r('arrival.toggles')),
          r('arrival.toggles'))
        self.assertNotEqual(old['expression'],syntax_altered['expression'])
        self.assertEqual(semantic_signature(old),semantic_signature(syntax_altered))
        self.assertNotEqual(semantic_signature(old),semantic_signature(candidate('FLIP')))

    def test_dev_only_drops_answers_by_name_and_unknown_keys_hold(self):
        x={'mechanism':'GROW','observed_result':7,'oracle_expected':6,
           'disposition':'REFUTED_ON_DEV','on_mask':3,'toggles_mask':5,
           'surviving_mechanisms':['FLIP']}
        y=dev_only([x])[0]
        self.assertEqual(set(y),{'observed_result','oracle_expected','disposition','on_mask','toggles_mask'})
        self.assertNotIn('FLIP',json.dumps(y))
        with self.assertRaises(CriticError):dev_only([{**x,'frozen_audit':'private'}])
        with self.assertRaises(CriticError):dev_only([{**x,'oracle_expected':True}])

    def test_mock_critic_can_stop_repeated_failure_and_model_can_adapt(self):
        # These are scripted model fixtures, NOT a claim about live LLM quality.
        result=comparison(ResponsiveFake,BRIEF,max_calls=3,graph=False)
        self.assertEqual(result['control']['status'],'HOLD_NO_VERIFIED_MODEL_PROPOSAL')
        self.assertEqual(result['critic']['status'],'MECHANISM_VERIFIED_ON_FINITE_TRUTH_TABLE_NOT_INSTALLED')
        self.assertEqual(result['control']['model_generations'],3)
        self.assertEqual(result['critic']['model_generations'],3)
        self.assertEqual(result['critic']['semantic_replays_vetoed'],1)
        self.assertEqual(result['critic']['director_dev_probes'],1)
        self.assertEqual(result['critic']['selected_mechanism'],'FLIP')
        self.assertEqual(result['control']['selected_mechanism'],None)
        self.assertTrue(result['critic']['oracle_never_graded_critic_veto'])
        self.assertFalse(result['critic']['installed'])

    def test_critic_never_fabricates_correct_candidate(self):
        out=run_arm(FixedResponder(['GROW']),BRIEF,mode='critic',max_calls=3,graph=False)
        self.assertEqual(out['status'],'HOLD_NO_VERIFIED_MODEL_PROPOSAL')
        self.assertEqual(out['model_generations'],3)
        self.assertEqual(out['semantic_replays_vetoed'],2)
        self.assertIsNone(out['candidate'])
        self.assertIsNone(out['selected_mechanism'])

    def test_correct_model_does_not_get_overridden_by_critic(self):
        control=run_arm(FixedResponder(['FLIP']),BRIEF,mode='control',max_calls=3,graph=False)
        critic=run_arm(FixedResponder(['FLIP']),BRIEF,mode='critic',max_calls=3,graph=False)
        self.assertEqual(control['status'],critic['status'])
        self.assertEqual(control['selected_mechanism'],'FLIP')
        self.assertEqual(critic['semantic_replays_vetoed'],0)
        self.assertEqual(critic['model_generations'],1)
        self.assertEqual(critic['director_report']['dev_truth_table'],{'passed':64,'total':64})

    def test_default_executable_graph_audit_remains_independent(self):
        result=run_arm(FixedResponder(['FLIP']),BRIEF,mode='critic',max_calls=3,graph=True)
        self.assertEqual(result['status'],'PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED')
        self.assertEqual(result['director_report']['frozen_graph_audit'],{'passed':60,'total':60})
        self.assertEqual(result['director_report']['stress_graph_audit'],{'passed':80,'total':80})
        self.assertFalse(result['installed'])

    def test_model_does_not_receive_hidden_candidate_survivor_labels(self):
        model=FixedResponder(['GROW','GROW','GROW'])
        run_arm(model,BRIEF,mode='critic',max_calls=3,graph=False)
        self.assertGreaterEqual(len(model.calls),2)
        self.assertTrue(all('FLIP' not in json.dumps(c['feedback']) for c in model.calls))
        self.assertTrue(all('frozen' not in json.dumps(c) for c in model.calls))
        self.assertTrue(any('oracle_expected' in m['feedback'][-1] for m in model.calls if m['feedback']))

    def test_fixed_budget_and_unknown_mode_are_refused(self):
        for count in (0,7,True,-1):
            with self.assertRaises(CriticError):ModelWithCritic(FixedResponder(['FLIP']),max_calls=count)
        with self.assertRaises(CriticError):ModelWithCritic(FixedResponder(['GROW']),mode='autonomous_shell')
        with self.assertRaises(CriticError):comparison(None,BRIEF)

    def test_actual_model_counter_receipts_are_preserved(self):
        model=FixedResponder(['GROW','GROW'])
        out=run_arm(model,BRIEF,mode='critic',max_calls=2,graph=False)
        self.assertEqual(len(out['model_receipts']),2)
        self.assertEqual(out['model_generations'],2)
        self.assertEqual(out['director_report']['pen_state'],'UNCHANGED')
        self.assertEqual(out['external_authority'],'NONE')
        self.assertIn('receipt_digest',out)

    def test_semantic_duplicate_with_changed_syntax_is_vetoed(self):
        class EquivalentResponder(FixedResponder):
            def propose(self,brief,feedback=()):
                self.calls.append({'prompt':brief,'feedback':copy.deepcopy(feedback),
                                   'simulation_only':True})
                item=response('GROW')
                if len(self.calls)>=2:
                    item['mechanism']['expression']=op('union',
                        op('union',r('state.on'),r('arrival.toggles')),
                        r('arrival.toggles'))
                return item
        result=run_arm(EquivalentResponder(['GROW']),BRIEF,mode='critic',max_calls=3,graph=False)
        self.assertEqual(result['semantic_replays_vetoed'],2)
        self.assertEqual(result['director_dev_probes'],1)
        self.assertIsNone(result['candidate'])

    def test_real_local_http_transport_fixture_exercises_critic_director(self):
        # This is an HTTP fixture returning canned JSON, NOT a real language model.
        from test_direct_model import ServerFixture, suggestion
        with ServerFixture([suggestion('GROW'),suggestion('GROW'),suggestion('FLIP')]) as stub:
            backend=stub.Model('test-llm:0.5b')
            output=run_arm(backend,BRIEF,mode='critic',max_calls=3,graph=False)
            self.assertEqual(output['status'],'MECHANISM_VERIFIED_ON_FINITE_TRUTH_TABLE_NOT_INSTALLED')
            self.assertEqual(output['model_generations'],3)
            self.assertEqual(output['semantic_replays_vetoed'],1)
            self.assertEqual(len(output['model_receipts']),3)
            self.assertTrue(all(c['http_generation_completed'] for c in output['model_receipts']))
            posts=[t for t in stub.http.record if t[0]=='POST']
            self.assertEqual(len(posts),3)
            self.assertIn('Do not repeat that transition function',posts[-1][2]['prompt'])
            self.assertNotIn('FLIP',posts[-1][2]['prompt'])

    def test_no_feedback_rewind_or_poison(self):
        worker=ModelWithCritic(FixedResponder(['GROW']),mode='critic',max_calls=3)
        good=[{'mechanism':'GROW','observed_result':7,'oracle_expected':6,
          'disposition':'REFUTED_ON_DEV','on_mask':3,'toggles_mask':5,
          'surviving_mechanisms':['FLIP']}]
        with self.assertRaises(CriticError):worker.propose(BRIEF,good)
        worker.propose(BRIEF)
        worker.propose(BRIEF,good)
        with self.assertRaises(CriticError):worker.propose(BRIEF,())

if __name__=='__main__':unittest.main()
