import unittest
from smoke import MECHANISMS,investigate,next_probe,probe_score
class TestDirectorSmoke(unittest.TestCase):
    def test_active_resolves_all_five(self):
        for target in MECHANISMS:
            x=investigate(target)
            self.assertTrue(x['resolved'],target)
            self.assertEqual(x['external_authority'],'NONE')
            self.assertEqual(x['pen'],'UNCHANGED')
    def test_fixed_control_also_resolves_all_five(self):
        for target in MECHANISMS:self.assertTrue(investigate(target,'fixed')['resolved'])
    def test_adaptive_uses_fewer_queries_on_author_fixtures(self):
        self.assertEqual(sum(investigate(x)['queries'] for x in MECHANISMS),5)
        self.assertEqual(sum(investigate(x,'fixed')['queries'] for x in MECHANISMS),12)
    def test_abstains_without_budget(self):
        x=investigate('FLIP',budget=0)
        self.assertFalse(x['resolved'])
        self.assertEqual(x['queries'],0)
    def test_no_untrusted_operators(self):
        with self.assertRaises(ValueError):investigate('PEN_COMMIT')
        with self.assertRaises(ValueError):next_probe(['EXECUTE_COMMAND'])
        with self.assertRaises(ValueError):next_probe(['FLIP','FLIP'])
    def test_utility_zero_for_no_difference(self):
        self.assertEqual(probe_score(MECHANISMS,0,0),0)
        self.assertGreater(probe_score(MECHANISMS,*next_probe(MECHANISMS)),0)
if __name__=='__main__':unittest.main()
