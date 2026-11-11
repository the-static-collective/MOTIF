import json
from pathlib import Path
import unittest
from dataclasses import replace
from engine import Input, Observation, load_packet, infer, run

FIXTURE = Path(__file__).parent/'fixtures'/'anonymous_visual_packet.json'


class AutonomousReframeTests(unittest.TestCase):
    def setUp(self):
        self.case=load_packet(json.loads(FIXTURE.read_text()))

    def test_without_back_and_forth_recovers_three_unsaid_moves(self):
        result=run(self.case)
        ids={x['id'] for x in result['inferences']}
        self.assertTrue({'reframe_target','relocate_installed','network_support','opportunistic_support','shorten_route'}.issubset(ids))
        self.assertEqual(result['dialogue_round_trips_needed_to_propose_options'],0)

    def test_ideas_are_not_observations(self):
        for idea in infer(self.case):
            self.assertEqual(idea.status,'HYPOTHESIS_NOT_OBSERVATION')
            self.assertTrue(idea.witness_ids)
            self.assertTrue(idea.prerequisites)

    def test_all_plans_remain_conditional_even_when_ties_available(self):
        r=run(replace(self.case,joiners_available='YES',permission_to_relocate='YES'))
        self.assertTrue(r['strategies'])
        self.assertFalse(r['verified_safe_pet_containment'])
        self.assertTrue(all(s['safety_status']=='NOT_VERIFIED_FOR_PET_USE' for s in r['strategies']))

    def test_no_target_marks_no_false_target_interpretation(self):
        c=replace(self.case,observations=tuple(o for o in self.case.observations if o.kind!='TARGET_ROUTE'))
        self.assertNotIn('reframe_target',{i.id for i in infer(c)})
        self.assertNotIn('recompose_perimeter',{s['id'] for s in run(c)['strategies']})

    def test_no_installed_fence_no_relocation_story(self):
        c=replace(self.case,observations=tuple(o for o in self.case.observations if o.kind!='EXISTING_BARRIER'))
        self.assertNotIn('relocate_installed',{i.id for i in infer(c)})

    def test_empty_materials_hold_without_hallucinated_options(self):
        c=Input('Set up a boundary',(Observation('x','GOAL_BOUNDARY','boundary','USER_REPORTED','request'),))
        self.assertEqual(run(c)['strategies'],[])

    def test_no_ties_are_silently_asserted(self):
        result=run(self.case)
        self.assertNotIn('CONNECTOR',[o['kind'] for o in result['observations']])
        self.assertIn('invent_join_step',{x['id'] for x in result['inferences']})
        self.assertEqual(self.case.joiners_available,'UNKNOWN')

    def test_photo_not_measurement(self):
        result=run(self.case)
        self.assertTrue(all('measured_width' not in e for e in result['observations']))
        self.assertIn('dimensions',result['limits'])

    def test_unknown_permission_remains_unknown(self):
        self.assertEqual(self.case.permission_to_relocate,'UNKNOWN')
        self.assertIn('movability',{q['id'] for q in run(self.case)['remaining_probes']})

    def test_no_exposure_field_question_disappears_only_if_verified(self):
        r=run(replace(self.case,critical_exit_closed_verified='YES'))
        self.assertNotIn('traffic_exit',{q['id'] for q in r['remaining_probes']})

    def test_dont_republish_raw_photos(self):
        self.assertNotIn('data:image',json.dumps(run(self.case)))

    def test_reproducible_receipt(self):
        self.assertEqual(run(self.case)['receipt_sha256'],run(self.case)['receipt_sha256'])

    def test_untrusted_unknown_field_rejected(self):
        raw=json.loads(FIXTURE.read_text()); raw['invented_payload']='A'
        with self.assertRaises(ValueError): load_packet(raw)

    def test_duplicate_observation_rejected(self):
        raw=json.loads(FIXTURE.read_text());raw['observations'].append(raw['observations'][0])
        with self.assertRaises(ValueError): load_packet(raw)

    def test_no_automatic_physical_actions(self):
        self.assertEqual(run(self.case)['physical_actions_executed'],0)


if __name__=='__main__': unittest.main()
