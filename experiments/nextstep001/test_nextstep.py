"""Executable tests: a question must be useful, affordable and truly executed.

These fixtures only establish performance within the declared synthetic model.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from random import Random
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'witnesschain001'))
from witnesschain import (State, Witness, Event, TruthReceipt, synthetic_cases,
                          flip)
from nextstep import (Goal, Candidate, orient, nominate, rank, advance, _execute,
                      fingerprint, demonstration)


def sample(size=100, truth=(1,1,1), seed=7, with_ref=False):
    fixtures = synthetic_cases(truth,seed,size)
    state=State()
    for event,_ in fixtures:
        state=state.add(event)
    if with_ref:
        for event,truth_label in fixtures[:3]:
            state=state.verify(TruthReceipt(event.id,truth_label,'declared-simulator'))
    return state


class ForwardQuestions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.unreferenced=sample()
        cls.referenced=sample(with_ref=True)

    def test_orientation_separates_known_and_unknown(self):
        report=orient(self.unreferenced,Goal('absolute_polarity'))
        self.assertEqual(report['requested_answer']['status'],'HOLD_GLOBAL_FLIP_SYMMETRY')
        self.assertTrue(any('relative' in x for x in report['known_under_declared_model']))
        self.assertTrue(any('unidentifiable' in x for x in report['unknown_or_unjustified']))
        self.assertFalse(report['authenticity_verified'])

    def test_proactive_next_question_runs_without_asking_user(self):
        result=advance(self.unreferenced,Goal('absolute_polarity',budget=1,max_steps=1))
        self.assertEqual(result['steps'][0]['action_executed'],'ANSWER_RELATIVE')
        self.assertEqual(result['steps'][0]['result']['result']['status'],'I_RELATIVE_MODEL_ONLY')
        self.assertEqual(result['status'],'EXECUTED_LOCAL_STEPS')
        self.assertEqual(result['budget_spent'],1)

    def test_multistep_question_experiment_result_loop(self):
        result=advance(self.unreferenced,Goal('absolute_polarity',budget=4,max_steps=3))
        steps=result['steps']
        self.assertEqual([x['action_executed'] for x in steps],
                         ['ANSWER_RELATIVE','TEST_SYMMETRY','DESIGN_PROBE'])
        self.assertEqual(steps[1]['result']['result'],
                         'GLOBAL_FLIP_INVARIANCE_VERIFIED_IN_DECLARED_MODEL')
        self.assertEqual(steps[1]['result']['pairs_checked'],64)
        self.assertEqual(steps[2]['result']['status'],'PROPOSAL_NOT_EXECUTED')
        self.assertGreater(steps[2]['result']['result']['information_bits'],0)
        self.assertTrue(result['same_evidence_before_after'])

    def test_no_hallucinated_truth_collection(self):
        r=advance(self.unreferenced,Goal('absolute_polarity',budget=4,max_steps=3))
        self.assertFalse(r['external_evidence_acquired'])
        self.assertEqual(r['real_world_actions'],0)
        self.assertEqual(r['orientation']['assumed_reference_count'],0)
        self.assertFalse(r['steps'][2]['result']['truth_attestation_collected'])
        self.assertNotIn('F',r['orientation']['requested_answer']['status'][:1])

    def test_reference_challenge_is_proactive_and_counterfactual(self):
        before=fingerprint(self.referenced)
        result=advance(self.referenced,Goal('absolute_polarity',budget=1,max_steps=1))
        self.assertEqual(result['steps'][0]['action_executed'],'CHALLENGE_REFERENCE')
        self.assertTrue(result['steps'][0]['result']['original_unchanged'])
        self.assertEqual(before,fingerprint(self.referenced))
        self.assertEqual(result['orientation']['requested_answer']['status'],
                         'I_CONDITIONAL_ON_FIXTURE_REFERENCE')

    def test_global_challenge_reopens_unverified_basis(self):
        state=sample(with_ref=True)
        result=advance(state,Goal('absolute_polarity',budget=3,max_steps=3))
        self.assertEqual(result['steps'][0]['action_executed'],'CHALLENGE_REFERENCE')
        self.assertEqual(len(state.truth_receipts),3)
        self.assertEqual(result['steps'][0]['result']['receipt']['operation'],
                         'reopen_synthetic_reference')
        self.assertFalse(result['orientation']['authenticity_verified'])

    def test_relative_goal_prioritizes_new_frontier_not_reasking_original(self):
        r=advance(self.unreferenced,Goal('primary_audit_alignment',budget=1,max_steps=1))
        self.assertEqual(r['steps'][0]['action_executed'],'TEST_SYMMETRY')

    def test_queries_change_according_to_context(self):
        a=nominate(self.unreferenced,Goal('absolute_polarity'))
        b=nominate(self.referenced,Goal('absolute_polarity'))
        self.assertIn('TEST_SYMMETRY',{c.action for c in a})
        self.assertNotIn('CHALLENGE_REFERENCE',{c.action for c in a})
        self.assertIn('CHALLENGE_REFERENCE',{c.action for c in b})
        self.assertNotIn('TEST_SYMMETRY',{c.action for c in b})

    def test_budget_exhaustion_stops_autonomy(self):
        r=advance(self.unreferenced,Goal('absolute_polarity',budget=0,max_steps=3))
        self.assertEqual(r['steps'],[])
        self.assertEqual(r['status'],'HOLD_NO_PERMITTED_AFFORDABLE_STEP')
        self.assertEqual(r['budget_spent'],0)

    def test_horizon_and_budget_both_bounded(self):
        a=advance(self.unreferenced,Goal('absolute_polarity',budget=100,max_steps=1))
        b=advance(self.unreferenced,Goal('absolute_polarity',budget=2,max_steps=3))
        self.assertEqual(len(a['steps']),1)
        self.assertEqual(len(b['steps']),2)
        self.assertLessEqual(b['budget_spent'],2)

    def test_no_duplicate_action_or_question(self):
        r=advance(self.unreferenced,Goal('absolute_polarity',budget=9,max_steps=3))
        self.assertEqual(len({x['action_executed'] for x in r['steps']}),len(r['steps']))
        self.assertEqual(len({x['next_question'] for x in r['steps']}),len(r['steps']))

    def test_denies_unknown_tool_even_if_suggested(self):
        with self.assertRaises(PermissionError):
            _execute(self.unreferenced,'SEND_EMAIL',Goal('absolute_polarity'),100)
        with self.assertRaises(PermissionError):
            _execute(self.unreferenced,'FETCH_GROUND_TRUTH',Goal('absolute_polarity'),100)

    def test_unauthorized_probe_not_executed(self):
        goal=Goal('absolute_polarity', budget=4,max_steps=3,allowed_inquiries=frozenset())
        r=advance(self.unreferenced,goal)
        plan=next(x for x in r['steps'] if x['action_executed']=='DESIGN_PROBE')
        self.assertEqual(plan['result']['result']['status'],'HOLD_NOT_ALLOWED_OR_AFFORDABLE')
        self.assertFalse(plan['result']['truth_attestation_collected'])

    def test_invalid_goals_and_action_metadata_refused(self):
        for fn in (
            lambda:Goal('general_intelligence'),
            lambda:Goal('absolute_polarity',budget=-1),
            lambda:Goal('absolute_polarity',max_steps=0),
            lambda:Goal('absolute_polarity',max_steps=100),
            lambda:Goal('absolute_polarity',allowed_inquiries=frozenset({'HACK'})),
            lambda:Candidate('x','SEND_EMAIL','try',100,1),
            lambda:Candidate('x','ANSWER_RELATIVE','try',2,-1),
        ):
            with self.assertRaises(ValueError):fn()

    def test_no_prediction_licensed_by_origin_strings(self):
        e=Event('test',(
            Witness('a','primary','amber','upstream'),
            Witness('b','audit','amber','upstream'),
        ))
        state=State().add(e)
        self.assertEqual(len(state.accepted),0)
        result=advance(state,Goal('absolute_polarity',budget=2,max_steps=2))
        self.assertEqual(result['orientation']['ledger_events'],0)
        self.assertEqual(result['orientation']['requested_answer']['status'],
                         'HOLD_GLOBAL_FLIP_SYMMETRY')
        self.assertEqual(result['real_world_actions'],0)

    def test_fir_admission_applies_only_to_exact_ledger_count(self):
        r=_execute(self.unreferenced,'COUNT_EVIDENCE',Goal('absolute_polarity'),1)
        self.assertEqual(r['FIR_role'],'F_LOCAL')
        self.assertEqual(r['model_role'],'I')
        self.assertEqual(r['accepted_events'],100)
        self.assertFalse(r['new_evidence'])

    def test_under_declaration_does_not_fix_corrupted_reference(self):
        fixtures=synthetic_cases((1,1,1),7,100)
        state=State()
        for event,_ in fixtures:state=state.add(event)
        for event,truth in fixtures[:3]:
            state=state.verify(TruthReceipt(event.id,flip(truth),'tampered-fixture'))
        report=advance(state,Goal('absolute_polarity',budget=1,max_steps=1))
        self.assertEqual(report['steps'][0]['action_executed'],'CHALLENGE_REFERENCE')
        self.assertFalse(report['orientation']['authenticity_verified'])
        self.assertFalse(report['external_evidence_acquired'])

    def test_reproducible_output_and_receipts(self):
        goal=Goal('absolute_polarity',budget=4,max_steps=3)
        a=advance(self.unreferenced,goal)
        self.assertEqual(a,advance(self.unreferenced,goal))
        for step in a['steps']:
            self.assertEqual(step['receipt']['input_evidence_digest'],
                             step['receipt']['output_evidence_digest'])
            self.assertIn(step['next_question'],step['receipt']['question'])

    def test_output_is_json_serializable(self):
        import json
        json.dumps(demonstration())

    def test_question_ranking_is_relevance_first_not_risky_autonomy(self):
        all_candidates=(Candidate('question X','DESIGN_PROBE','x',3,1,100.0),
                        Candidate('question Y','ANSWER_RELATIVE','y',10,1,0.0))
        ranked=rank(all_candidates,1)
        self.assertEqual(ranked[0].action,'ANSWER_RELATIVE')
        self.assertEqual(rank(all_candidates,0),())

    def test_question_nominations_have_no_external_side_effects(self):
        candidates=nominate(self.unreferenced,Goal('absolute_polarity'))
        self.assertTrue(all(c.side_effect=='NONE' and c.epistemic_status=='I_PROPOSAL'
                            for c in candidates))

    def test_changed_fixture_changes_input_receipt(self):
        other=sample(100, (0,0,0), 9)
        self.assertNotEqual(fingerprint(self.unreferenced),fingerprint(other))


if __name__=='__main__':unittest.main()


class HostileProposals(unittest.TestCase):
    def test_rank_never_admits_external_action(self):
        proposals = (
            Candidate('Can I send a message?', 'SEND_EMAIL', 'untrusted model proposed it', 10, 0),
            Candidate('Can I alter a file?', 'ANSWER_RELATIVE', 'mislabelled', 10, 0,
                      side_effect='FILE_WRITE'),
            Candidate('Is it proven?', 'ANSWER_RELATIVE', 'falsely promoted', 10, 0,
                      epistemic_status='F'),
            Candidate('Can I inspect a model?', 'TEST_SYMMETRY', 'allowed', 5, 1),
        )
        self.assertEqual([x.action for x in rank(proposals, 1)], ['TEST_SYMMETRY'])

    def test_no_state_rewrite_from_unverified_truth_hypothesis(self):
        from nextstep import advance
        from witnesschain import State, Event, Witness
        state = State()
        for i in range(3):
            state = state.add(Event(f'event-{i}', (
                Witness(f'p-{i}', 'primary','amber',f'root-p-{i}'),
                Witness(f'a-{i}', 'audit','blue',f'root-a-{i}'),
            )))
        before = state
        report = advance(state, Goal('absolute_polarity',budget=3,max_steps=3))
        self.assertEqual(state, before)
        self.assertEqual(report['real_world_actions'],0)
        self.assertTrue(report['same_evidence_before_after'])
