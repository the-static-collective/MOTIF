import unittest
from geometry import Point,Scene,Trace,Anchor,ratio,calibrate,panel_requirements
from planner import Alternative,explore

P=Point

def scene(mode='PLAN_METRIC',tol=None,source='page',plane='yard',rectified=False):
    return Scene(source,mode,plane,'fixture:human-label',tol,rectified)

def t(name,n,source='page',plane='yard',tol=0):
    return Trace(name,source,plane,(P(0,0),P(n,0)),'fixture:manually-traced',tol)

class Calibration(unittest.TestCase):
    def test_ratio_without_known_reference(self):
        out=ratio(scene(),t('gap',120),t('panel',40))
        self.assertEqual(out.status,'PLAN_RATIO');self.assertEqual(out.center,3)
    def test_sketch_unscaled_reports_drawn_only(self):
        out=ratio(scene('SKETCH_APPROX'),t('gap',120),t('panel',40))
        self.assertEqual(out.status,'DRAWN_ONLY');self.assertEqual(out.center,3)
        self.assertIsNone(out.lower)
    def test_sketch_unscaled_cannot_claim_lengths(self):
        out=calibrate(scene('SKETCH_APPROX'),t('gap',120),((t('panel',40),Anchor('panel',4,4,'ft','user:tape')),))
        self.assertEqual(out.status,'HOLD')
    def test_one_known_anchor_scaled_plan(self):
        out=calibrate(scene(),t('gap',120),((t('panel',40),Anchor('panel',4,4,'ft','user:tape')),))
        self.assertEqual(out.center,12);self.assertEqual(out.lower,12);self.assertEqual(out.upper,12)
    def test_sketch_conditional_uncertainty(self):
        out=calibrate(scene('SKETCH_APPROX',.4),t('gap',120),((t('panel',40),Anchor('panel',4,4,'ft','user:tape')),))
        self.assertEqual(out.status,'CONDITIONAL_SKETCH_GUESS')
        self.assertLess(out.lower,8);self.assertGreater(out.upper,16)
    def test_real_pixel_error_carries(self):
        out=ratio(scene(),t('gap',120,tol=3),t('panel',40,tol=3))
        self.assertLess(out.lower,3);self.assertGreater(out.upper,3)
    def test_different_photo_hold(self):
        self.assertEqual(ratio(scene(),t('a',20,'page'),t('b',30,'other')).status,'HOLD')
    def test_different_plane_hold(self):
        self.assertEqual(ratio(scene(),t('a',20),t('b',30,plane='vertical-wall')).status,'HOLD')
    def test_perspective_photo_no_scale(self):
        out=calibrate(scene('PHOTO_UNRECTIFIED'),t('gap',120),((t('p',40),Anchor('p',4,4,'ft','known')),))
        self.assertEqual(out.status,'HOLD')
    def test_perspective_photo_no_ratio(self):
        self.assertEqual(ratio(scene('PHOTO_UNRECTIFIED'),t('gap',120),t('p',40)).status,'HOLD')
    def test_rectified_requires_verified(self):
        with self.assertRaises(ValueError):scene('RECTIFIED_PLANE')
    def test_verified_rectification_works(self):
        out=calibrate(scene('RECTIFIED_PLANE',rectified=True),t('gap',120),((t('p',40),Anchor('p',4,4,'ft','measured')),))
        self.assertEqual(out.center,12)
    def test_second_consistent_measurement_refines(self):
        a=calibrate(scene(),t('gap',120),((t('p',40),Anchor('p',4,4.5,'ft','measured')), (t('q',80),Anchor('q',8,8,'ft','measured'))))
        self.assertEqual(a.center,12)
    def test_second_inconsistent_measurement_holds(self):
        a=calibrate(scene(),t('gap',120),((t('p',40),Anchor('p',4,4,'ft','measured')), (t('q',80),Anchor('q',16,16,'ft','measured'))))
        self.assertEqual(a.status,'HOLD');self.assertIn('Conflicting',a.assumptions[0])
    def test_guessed_anchor_never_promoted(self):
        a=calibrate(scene(),t('gap',120),((t('p',40),Anchor('p',4,4,'ft','guess',False)),))
        self.assertEqual(a.status,'HOLD')
    def test_reject_mixed_units(self):
        a=calibrate(scene(),t('gap',120),((t('p',40),Anchor('p',4,4,'ft','yes')),(t('q',80),Anchor('q',2,2,'m','yes'))))
        self.assertEqual(a.status,'HOLD')
    def test_reject_cross_source_anchor(self):
        a=calibrate(scene(),t('gap',120),((t('p',40,source='other'),Anchor('p',4,4,'ft','yes')),))
        self.assertEqual(a.status,'HOLD')
    def test_reject_zero_reference_with_uncertainty(self):
        a=ratio(scene(),t('gap',120),t('p',5,tol=5))
        self.assertEqual(a.status,'HOLD')
    def test_right_angle_polyline(self):
        zig=Trace('zig','page','yard',(P(0,0),P(3,0),P(3,4)),'test',0)
        self.assertEqual(zig.nominal_length,7)
        self.assertEqual(ratio(scene(),zig,t('ref',7)).center,1)
    def test_diagonal(self):
        d=Trace('diag','page','yard',(P(0,0),P(3,4)),'test',0)
        self.assertEqual(d.nominal_length,5)
    def test_panel_range(self):
        a=calibrate(scene('SKETCH_APPROX',.4),t('gap',100),((t('p',40),Anchor('p',4,4,'ft','tape')),))
        q=panel_requirements(a,3)
        self.assertGreater(q['panels_if_upper_bound'],q['panels_possible'])
    def test_panels_without_anchor_hold(self):
        a=calibrate(scene(),t('gap',100),())
        self.assertEqual(panel_requirements(a,3)['status'],'HOLD_UNSCALED')
    def test_panel_overlap_control(self):
        a=calibrate(scene(),t('gap',100),((t('p',50),Anchor('p',5,5,'ft','tape')),))
        self.assertEqual(panel_requirements(a,3,min_overlap=.5)['panels_possible'],4)
    def test_units_required(self):
        with self.assertRaises(ValueError):Anchor('a',4,4,'','tape')
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):Point(float('nan'),1)
    def test_proportion_tolerance_bounds(self):
        with self.assertRaises(ValueError):scene('SKETCH_APPROX',.97)
    def test_explore_two_routes_ratio_without_anchor(self):
        a=explore(scene('SKETCH_APPROX'),t('ref',40),(
            Alternative('short',t('a',60),'sketch:human'),Alternative('long',t('b',120),'sketch:human')))
        self.assertEqual(a['visual_shortest'],'short')
        self.assertFalse(a['visual_shortest_is_proven_physical_shortest'])
        self.assertEqual(a['alternatives'][0]['length']['status'],'HOLD')
    def test_explore_with_anchor_and_material(self):
        a=explore(scene('SKETCH_APPROX',.5),t('ref',40),
                  (Alternative('route',t('a',120),'fixture:proposal'),), Anchor('ref',4,4,'ft','tape'),3)
        self.assertEqual(a['alternatives'][0]['panel_scenario']['status'],'CONDITIONAL_MATERIAL_SCENARIO')
    def test_explore_duplicate_held(self):
        with self.assertRaises(ValueError):explore(scene(),t('ref',40),(Alternative('r',t('a',40),'yes'),Alternative('r',t('b',40),'yes')))
    def test_explore_no_hypothesis_source(self):
        with self.assertRaises(ValueError):explore(scene(),t('ref',40),(Alternative('r',t('a',40),''),))
    def test_unanchored_probe(self):
        a=explore(scene('SKETCH_APPROX'),t('p',50),(Alternative('r',t('g',80),'human:line'),))
        self.assertEqual(a['decision_confidence'],'DRAWN_ONLY__NO_PHYSICAL_SCALE')
        self.assertIn('Measure',a['next_probe'])
    def test_uncertain_route_rank_abstains(self):
        a=explore(scene('SKETCH_APPROX',.4),t('p',40),(
            Alternative('short',t('g',80),'human:line'),Alternative('long',t('h',100),'human:line')),
            Anchor('p',4,4,'ft','tape'),3)
        self.assertEqual(a['decision_confidence'],'OVERLAPPING_INTERVALS__NO_CONFIDENT_ROUTE_RANK')
    def test_robust_metric_route_rank(self):
        a=explore(scene(),t('p',40),(
            Alternative('short',t('g',80),'human:line'),Alternative('long',t('h',200),'human:line')),
            Anchor('p',4,4,'ft','tape'))
        self.assertEqual(a['decision_confidence'],'ROBUST_UNDER_STATED_GEOMETRIC_ASSUMPTIONS')

if __name__=='__main__':unittest.main()
