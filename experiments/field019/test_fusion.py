import copy,unittest
import numpy as np
from fusion import fuse, validate, EvidenceError, save_receipt, HEIGHT_M
from synthetic import packet, TRUE_SCALE

class CrossDomainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good=fuse(packet(1))
    def test_real_geometry_clean(self):
        self.assertEqual(self.good.status,'CONDITIONAL_CROSS_DOMAIN_GEOMETRY')
        self.assertAlmostEqual(self.good.horizontal_m_per_sketch_unit,TRUE_SCALE,delta=.12)
    def test_two_cameras(self):
        self.assertEqual(len(self.good.camera_poses),2)
    def test_relative_camera_baseline_estimated(self):
        from synthetic import CAMS
        import numpy as np
        g=fuse(packet(2,sketch_noise=.06,pixel_noise=.7))
        true=float(np.linalg.norm(CAMS[1][0]-CAMS[0][0]))
        self.assertAlmostEqual(g.diagnostics['camera_baseline_m_conditional'],true,delta=.3)
    def test_height_correct(self):
        self.assertAlmostEqual(self.good.predicted_world[0]['top_m'][1],-HEIGHT_M,delta=.001)
    def test_no_verification_claim(self):
        self.assertFalse(self.good.diagnostics['independent_ground_truth'])
    def test_cross_view_bad_match_holds(self):
        self.assertEqual(fuse(packet(1,corrupt=True)).status,'HOLD_CONTRADICTORY_CORRESPONDENCE')
    def test_wrong_or_unknown_focal_holds(self):
        d=packet(1); d['views'][1].pop('focal_px')
        self.assertEqual(fuse(d).status,'HOLD_UNDERCONSTRAINED')
    def test_unproven_focal_source_holds(self):
        d=packet(1);d['views'][1].pop('focal_provenance')
        self.assertEqual(fuse(d).status,'HOLD_UNDERCONSTRAINED')
    def test_false_calibration_can_bias_a_low_residual_fit(self):
        d=packet(1,sketch_noise=.03)
        for v in d['views']:v['focal_px']*=1.2
        wrong=fuse(d)
        self.assertEqual(wrong.status,'CONDITIONAL_CROSS_DOMAIN_GEOMETRY')
        self.assertGreater(abs(wrong.horizontal_m_per_sketch_unit-TRUE_SCALE),.12)
        self.assertLess(wrong.reprojection_rms_px,2.)
    def test_single_view_holds(self):
        self.assertEqual(fuse(packet(1,views=1)).status,'HOLD_UNDERCONSTRAINED')
    def test_unconfirmed_pixels_hold(self):
        d=packet(1);d['views'][0]['correspondences_source']='MODEL_TENTATIVE'
        self.assertEqual(fuse(d).status,'HOLD_UNDERCONSTRAINED')
    def test_sketch_drawing_only_hold(self):
        d=packet(1);d['sketch_proportionality']='DRAWN_ONLY'
        self.assertEqual(fuse(d).status,'HOLD_UNDERCONSTRAINED')
    def test_missing_height_hold(self):
        d=packet(1);d.pop('height_source')
        self.assertEqual(fuse(d).status,'HOLD_UNDERCONSTRAINED')
    def test_collinear_hold(self):
        d=packet(1);d['landmarks']={k:[i,0] for i,k in enumerate(d['landmarks'])}
        self.assertEqual(fuse(d).status,'HOLD_UNDERCONSTRAINED')
    def test_conflicting_sketch_correctable_only_hypothetically(self):
        g=fuse(packet(2,sketch_noise=.08))
        self.assertEqual(g.status,'CONDITIONAL_CROSS_DOMAIN_GEOMETRY')
        self.assertGreater(g.diagnostics['sketch_correction_max_fraction_of_extent'],0)
        self.assertTrue(g.diagnostics['sketch_correction_proposed_not_observed'])
    def test_unreasonable_sketch_large_error_hold(self):
        d=packet(1);d['landmarks']['p3'][0]+=1.2
        self.assertTrue(fuse(d).status.startswith('HOLD_'))
    def test_repeated_seed(self):
        for seed in (0,3,5):
            g=fuse(packet(seed))
            self.assertEqual(g.status,'CONDITIONAL_CROSS_DOMAIN_GEOMETRY')
            self.assertAlmostEqual(g.horizontal_m_per_sketch_unit,TRUE_SCALE,delta=.15)
    def test_receipt_reproducible(self):
        a=save_receipt(packet(1),self.good)
        self.assertEqual(a,save_receipt(packet(1),self.good))
        self.assertEqual(len(a['receipt_hash']),64)
    def test_no_raw_images_in_receipt(self):
        r=save_receipt(packet(1),self.good)
        self.assertNotIn('image_bytes',str(r))

if __name__=='__main__':unittest.main()
