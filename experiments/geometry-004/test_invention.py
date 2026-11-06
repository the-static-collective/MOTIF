import unittest
from invention import *
from benchmark import main, triangles

class InventionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples=triangles(3,40)
        cls.model=discover(cls.samples,triangles(20,41))

    def test_old_grammar_cannot_reach_centroid(self):
        self.assertFalse(any(all(run(p,t)==centroid_direct(t) for t in self.samples) for p in candidate_programs(False)))

    def test_macro_was_not_given_as_new_primitive(self):
        self.assertEqual(self.model['invented_macro']['nature'],'composition of existing operators, not novel primitive')
        self.assertIn('midpoint',self.model['signature'])

    def test_finite_cegis_has_independent_checks(self):
        self.assertEqual(self.model['counterexamples_checked'],20)
        self.assertEqual(self.model['status'],'PROPOSAL_ONLY')

    def test_old_grammar_smaller_than_expanded(self):
        self.assertLess(len(candidate_programs(False)),len(candidate_programs(True)))

    def test_holdout_and_classical_agree(self):
        self.assertEqual(main()['learned_correct'],60)
        self.assertEqual(main()['classical_correct'],60)

    def test_degenerate_holds(self):
        t=(point(0,0),point(1,1),point(2,2))
        self.assertEqual(apply(self.model,t)['status'],'HOLD')
        self.assertEqual(discover([t,*self.samples])['status'],'HOLD')

    def test_missing_teacher_holds(self):
        self.assertEqual(discover(self.samples[:1])['status'],'HOLD')

    def test_independent_teacher_required(self):
        self.assertEqual(discover([self.samples[0]]*3)['status'],'HOLD')

    def test_no_outside_action(self):
        result=apply(self.model,self.samples[0])
        self.assertEqual(result['authority'],'HOLD')
        self.assertEqual(result['status'],'PROPOSAL_ONLY')

if __name__=='__main__':unittest.main()
