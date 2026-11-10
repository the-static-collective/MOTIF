"""QC-015: check two source-pinned oscillations from actual QC-013 game runs."""
from pathlib import Path
import json
import unittest
from cycle_field import FieldState,FieldStep,CycleMonitor

DATA=json.loads((Path(__file__).parent/'observed_prior_oscillations.json').read_text())


def walk(case):
    m=CycleMonitor()
    alerts=[]
    states=[FieldState(tuple(pos),tuple(tuple(x) for x in case['fixed_nonvital_inventory']),
                       tuple(case['fixed_achievements']),
                       tuple(tuple(x) for x in case['vitals'][i]),
                       case['steps'][0]-1+i)
            for i,pos in enumerate(case['positions'])]
    for i,action in enumerate(case['actions']):
        x=FieldStep(states[i],action,states[i+1],None,
                    'original-archive-member:'+case['member_sha256'])
        a=m.observe(x)
        if a:alerts.append(a)
    return alerts


class ArchivedCases(unittest.TestCase):
    def test_source_is_prior_real_game_not_generated_story(self):
        self.assertIn('42743549945',DATA['archive_source'])
        self.assertEqual(len(DATA['archive_sha256']),64)
        self.assertEqual(len(DATA['cases']),2)

    def test_first_real_loop_1042_baseline_step118(self):
        a=walk(DATA['cases'][0])
        self.assertEqual(len(a),1)
        self.assertEqual(a[0].period,2)
        self.assertEqual(a[0].detected_step,118)
        self.assertEqual(a[0].action_pattern,('move_left','move_right'))
        self.assertEqual(a[0].status,'SUSPECTED_CYCLE_VIEW_UNKNOWN')

    def test_second_real_loop_2026_baseline_step187(self):
        a=walk(DATA['cases'][1])
        self.assertEqual(len(a),1)
        self.assertEqual(a[0].detected_step,187)
        self.assertEqual(a[0].action_pattern,('move_up','move_down'))
        self.assertEqual(dict(a[0].vital_debt)['energy'],-1)

    def test_view_delta_is_unavailable_not_zero(self):
        self.assertFalse(DATA['certified_no_new_scene_information'])
        self.assertTrue(all(c['new_scene_facts'] is None
                            for c in DATA['cases']))

    def test_provenance_is_constrained_to_game_only(self):
        self.assertTrue(DATA['none_of_this_is_real_world_survival_evidence'])
        self.assertTrue(all(len(c['member_sha256'])==64 for c in DATA['cases']))

if __name__=='__main__':unittest.main()
