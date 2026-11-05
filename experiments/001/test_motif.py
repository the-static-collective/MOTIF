"""Run with: python -m unittest -v test_motif.py"""
import unittest
from motif import F, TransitionLearner, candidates, scenario, search, synthetic_lessons, value

class MotifTests(unittest.TestCase):
    def setUp(self):
        self.rules = TransitionLearner().fit(synthetic_lessons())
        self.start, self.entities = scenario()

    def test_learns_role_relative_rules_from_demonstrations(self):
        self.assertEqual(set(self.rules), {'repair', 'teach'})
        self.assertEqual(self.rules['repair'].observations, 3)
        self.assertIn(('permits','?0','?1','?2'), self.rules['repair'].requires)
        self.assertIn(('skill','?1','repair'), self.rules['repair'].requires)
        self.assertNotIn(('likes','?0','tea'), self.rules['repair'].requires)

    def test_unseen_entities_plan_three_steps(self):
        result = search(self.start,self.rules,self.entities)
        self.assertEqual(result['score'],24)
        self.assertEqual(len(result['path']),3)
        self.assertEqual(set(result['resulting_world']) - set(self.start),
                         {F('usable','bike1'),F('usable','bike2'),F('skill','Jo','repair')})

    def test_permission_absence_holds(self):
        no_permission, entities = scenario(False)
        self.assertEqual(list(candidates(no_permission,self.rules,entities)), [])
        self.assertEqual(search(no_permission,self.rules,entities)['path'],[])

    def test_missing_tool_blocks_repair(self):
        limited = self.start - {F('tool','Mira','wrench'),F('tool','Jo','wrench')}
        result = search(frozenset(limited),self.rules,self.entities)
        self.assertNotIn(F('usable','bike1'),result['resulting_world'])
        self.assertNotIn(F('usable','bike2'),result['resulting_world'])

    def test_world_not_mutated_by_imagination(self):
        initial = self.start.copy()
        search(self.start,self.rules,self.entities)
        self.assertEqual(self.start,initial)

    def test_unseen_pattern_fails_closed(self):
        # Dataset teaches repair with a wrench. It must not guess that a spoon works.
        spoon_only = (self.start - {F('tool','Mira','wrench'),F('tool','Jo','wrench')}) | {F('tool','Mira','spoon')}
        self.assertFalse(any(a=='repair' for a,_,_ in candidates(frozenset(spoon_only),self.rules,self.entities)))

if __name__ == '__main__': unittest.main()
