import copy
import json
import unittest
from fractions import Fraction as F
from benchmark import examples, benchmark
from cartridge import make,verify
from demo import crossing
from proof import symbolic_certificate
from synthesis import (
    P, Program, point, oracles, learn, apply, evaluate, line, intersection,
    certificates, structural_candidates, midpoint, dist2
)


class MethodSynthesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=examples()
        cls.trained=learn(cls.cases[:8])

    def test_exhaustive_bounded_search_and_macro_composition(self):
        self.assertEqual(self.trained['status'],'PROPOSE_ONLY')
        self.assertEqual(self.trained['candidate_programs'],210)
        self.assertEqual(self.trained['secondary_compositions'],10)
        self.assertEqual(self.trained['matches']['nine_point_center'],1)
        self.assertEqual(self.trained['programs']['nine_point_center'].op,'midpoint')

    def test_all_40_distinct_unseen_rational_triangles(self):
        for abc in self.cases[8:]:
            with self.subTest(abc=abc):
                computed=apply(self.trained,abc)
                self.assertEqual(computed['status'],'PROPOSE_ONLY')
                self.assertEqual(computed['points'],oracles(abc))
                self.assertTrue(all(computed['witnesses'].values()))

    def test_strong_direct_classical_formula_ties(self):
        b=benchmark()
        self.assertEqual(b['learned_macro_heldout_errors'],0)
        self.assertEqual(b['direct_classical_oracle_heldout_errors'],0)
        self.assertFalse(b['universal_formal_proof'])

    def test_original_observations_immutable(self):
        abc=self.cases[0]
        old=copy.deepcopy(abc)
        apply(self.trained,abc)
        self.assertEqual(abc,old)
        self.assertEqual(old,self.cases[0])

    def test_collinear_and_duplicate_hold(self):
        for abc in [
            (point(0,0),point(1,1),point(2,2)),
            (point(0,0),point(0,0),point(1,3)),
        ]:
            self.assertIsNone(oracles(abc))
            self.assertEqual(apply(self.trained,abc)['status'],'HOLD')

    def test_wrong_metric_and_unlearned_holds(self):
        self.assertEqual(apply(self.trained,self.cases[9],geometry='taxicab')['status'],'HOLD')
        self.assertEqual(apply({'status':'HOLD'},self.cases[9])['status'],'HOLD')

    def test_missing_primitives_cause_holds(self):
        self.assertEqual(learn(self.cases[:8],allow_midpoint=False)['status'],'HOLD')
        self.assertEqual(learn(self.cases[:8],allow_perpendicular=False)['status'],'HOLD')
        self.assertEqual(learn(self.cases[:2])['status'],'HOLD')
        self.assertEqual(learn([self.cases[0]]*8)['status'],'HOLD')

    def test_exact_conditional_symbolic_identity(self):
        proof=symbolic_certificate()
        self.assertTrue(all(proof['conditional_symbolic_vector_identities'].values()))
        self.assertIn('premises',proof)

    def test_replayable_held_cartridge_and_tampering(self):
        record=make(self.cases[:8])
        self.assertTrue(verify(record))
        self.assertEqual(record['payload']['admission'],'HOLD')
        self.assertEqual(record['payload']['effective_authority'],'NONE')
        record['payload']['constructors']['orthocenter']['op']='midpoint'
        self.assertFalse(verify(record))
        self.assertFalse(verify({'payload':{'schema':'wrong'},'sha256':'fake'}))

    def test_invalid_typed_terms_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(Program('midpoint',(Program('line',(P['A'],P['B'])),P['C'])),self.cases[0])
        with self.assertRaises(ValueError):
            evaluate(Program('input',name='Z'),self.cases[0])
        self.assertIsNone(intersection(line(point(0,0),point(2,0)),
                                       line(point(0,1),point(2,1))))

    def test_actual_geom002_crossing_uses_only_observed_inliers(self):
        result=crossing(self.trained)
        self.assertEqual(result['status'],'PROPOSE_ONLY')
        self.assertEqual(result['selected_observation_count'],3)
        self.assertEqual(result['admission'],'HOLD')
        self.assertTrue(all(result['exact_rational_snapshot_witnesses'].values()))


if __name__=='__main__':
    unittest.main()
