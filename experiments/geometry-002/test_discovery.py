"""Executable invariants, independent oracle fixtures and negative controls."""
import copy
import math
import random
import unittest
from math import hypot

from benchmark import FAMILIES, SEEDS, NEGATIVE_SEEDS, negative, synthetic, run
from cartridge import make_cartridge, verify_cartridge
from demo import scenario
from discover import _geometry, _reduced_basis, discover, point_set


class GeometryDiscoveryTests(unittest.TestCase):
    def test_three_unannounced_angles_are_recovered(self):
        for family,angle in [('triangular',60),('square',90),('oblique',73)]:
            with self.subTest(family=family):
                obs=list(point_set(family,1.3,38,(4,-7)).values())
                result=discover(obs)
                self.assertEqual(result['status'],'PROPOSE_ONLY')
                self.assertEqual(result['rule']['family'],family)
                self.assertLess(abs(result['rule']['angle_degrees']-angle),0.01)
                self.assertEqual(result['inliers'],len(obs))

    def test_unknown_angle_scale_rotation_and_two_outliers(self):
        points,truth,missing=scenario()
        result=discover(points)
        self.assertEqual(result['status'],'PROPOSE_ONLY')
        self.assertEqual(result['rule']['family'],'triangular')
        self.assertLess(abs(result['rule']['angle_degrees']-60),2)
        self.assertEqual(result['inliers'],17)
        self.assertEqual(result['observed_count'],18)
        self.assertTrue(all(h['status']=='PROPOSAL_ONLY' for h in result['holes']))
        self.assertEqual(len(result['holes']),3)
        for position in missing:
            x,y=truth[position]
            self.assertTrue(any(hypot(h['xy'][0]-x,h['xy'][1]-y)<.2
                                for h in result['holes']))

    def test_nonobservations_never_become_observed(self):
        points,_,_=scenario()
        original=copy.deepcopy(points)
        result=discover(points)
        self.assertEqual(points,original)
        self.assertEqual(result['authority'].split(':')[0],'HOLD')
        self.assertTrue(all(p['witnessed_neighbors']>=4
                            for p in result['holes']))
        self.assertTrue(set(result['inlier_indices'])<=set(range(len(points))))

    def test_basis_reduction_removes_shear_not_lattice(self):
        # (1,0) and (1-cos73,sin73) span the same lattice as
        # (1,0) and (cos73,sin73); reduction is coordinate-gauge only.
        a=math.radians(73)
        baseline=(1.0,0.0,math.cos(a),math.sin(a))
        sheared=(1.0,0.0,1-math.cos(a),-math.sin(a))
        actual=_reduced_basis(sheared)
        self.assertAlmostEqual(_geometry(actual)['angle_degrees'],73,places=4)
        self.assertAlmostEqual(_geometry(baseline)['angle_degrees'],73,places=4)

    def test_permutation_robustness(self):
        points,_,_=scenario()
        a=discover(points)
        shuffled=list(points)
        random.Random(71).shuffle(shuffled)
        b=discover(shuffled)
        self.assertEqual(a['rule']['family'],b['rule']['family'])
        self.assertEqual(len(a['holes']),len(b['holes']))
        for h in a['holes']:
            self.assertTrue(any(hypot(h['xy'][0]-k['xy'][0],
                                      h['xy'][1]-k['xy'][1])<0.02
                                for k in b['holes']))

    def test_unsupported_sparse_or_degenerate_holds(self):
        self.assertEqual(discover([(float(x),float(x)) for x in range(6)])['status'],'HOLD')
        self.assertEqual(discover([(i,0) for i in range(23)])['status'],'HOLD')
        self.assertEqual(discover([(0,0)]*12)['status'],'HOLD')
        with self.assertRaises(ValueError):
            discover([(0,float('nan'))]*9)
        with self.assertRaises(ValueError):
            discover([(0,0)]*9,min_coverage=0)

    def test_nonlattice_controls_refuse(self):
        for seed in NEGATIVE_SEEDS:
            with self.subTest(seed=seed):
                self.assertEqual(discover(negative(seed))['status'],'HOLD')

    def test_frozen_development_benchmark_reports_failures(self):
        results=run()
        self.assertEqual(results['tested_worlds'],36)
        self.assertEqual(results['negative_controls'],24)
        self.assertEqual(results['proposed_models'],36)
        self.assertEqual(results['family_correct'],36)
        self.assertEqual(results['masked_centers_recovered'],60)
        self.assertEqual(results['extra_hole_proposals'],0)
        self.assertEqual(results['negative_controls_held'],24)
        # Honest partial completion is expected: no invented boundary holes.
        self.assertLess(results['masked_centers_recovered'],108)

    def test_ablation_same_observations_and_lower_residual(self):
        for family in FAMILIES:
            points,_=synthetic(family,SEEDS[0])
            refined=discover(points,refine=True)
            raw=discover(points,refine=False)
            self.assertEqual(refined['status'],raw['status'])
            self.assertEqual(refined['inliers'],raw['inliers'])
            self.assertLess(refined['normalized_rmse'],raw['normalized_rmse'])

    def test_cartridge_check_is_not_source_authentication(self):
        points,_,_=scenario()
        cartridge=make_cartridge(points)
        self.assertTrue(verify_cartridge(cartridge))
        self.assertEqual(cartridge['payload']['admission'],'HOLD')
        self.assertEqual(cartridge['payload']['effective_authority'],'NONE')
        altered=copy.deepcopy(cartridge)
        altered['payload']['input_points'][0][0]+=1
        self.assertFalse(verify_cartridge(altered))
        altered=copy.deepcopy(cartridge)
        altered['payload']['result']['rule']['family']='spirit'
        self.assertFalse(verify_cartridge(altered))
        self.assertFalse(verify_cartridge({'payload':{}}))


if __name__=='__main__':
    unittest.main()
