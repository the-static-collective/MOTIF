import sys,unittest
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'field007'))
from benchmark import gen
from critic import review,validate_packet,dash_evidence,_point_line_distance

class CriticTests(unittest.TestCase):
    def image(self):return gen(153,'both')
    def packet(self,style='DOTTED',points=None,kind='VISIBLE_MARK'):
        return {'source_id':'s','claims':[{'id':'mark','kind':kind,'style':style,
            'points':points or [[.15,.215],[.68,.215]],'label':''}]}
    def test_supported_horizontal_ink_is_only_compatible(self):
        r=review(self.packet(),self.image(),'s')
        self.assertEqual(r['reviews'][0]['verdict'],'INK_COMPATIBLE_INTENT_UNVERIFIED')
        self.assertFalse(r['complete_route_verified'])
    def test_supported_vertical_ink(self):
        r=review(self.packet(points=[[531/640,.345],[531/640,.785]]),self.image(),'s')
        self.assertEqual(r['reviews'][0]['verdict'],'INK_COMPATIBLE_INTENT_UNVERIFIED')
    def test_fake_dashed_line_held(self):
        r=review(self.packet(points=[[.12,.71],[.72,.71]]),self.image(),'s')
        self.assertEqual(r['reviews'][0]['verdict'],'HOLD_UNSUPPORTED_DOTTED_TRACE')
    def test_paper_solid_line_cannot_certify(self):
        r=review(self.packet('SOLID',[[.2,.79],[.8,.79]]),self.image(),'s')
        self.assertEqual(r['reviews'][0]['verdict'],'HOLD_SOLID_STYLE_NOT_VERIFIED')
    def test_proposal_cannot_be_marked_dotted(self):
        p=self.packet(kind='HYPOTHETICAL_ROUTE')
        with self.assertRaises(ValueError):validate_packet(p,'s')
    def test_proposal_always_not_a_real_ink_mark(self):
        r=review(self.packet('UNKNOWN',kind='HYPOTHETICAL_ROUTE'),self.image(),'s')
        self.assertEqual(r['reviews'][0]['verdict'],'PROPOSAL_ONLY')
    def test_claims_complete_route_overruled(self):
        p=self.packet();p['claimed_complete_route']=True
        r=review(p,self.image(),'s')
        self.assertFalse(r['complete_route_verified'])
        self.assertTrue(r['critic_contradictions'])
    def test_no_false_coordinates(self):
        r=review(self.packet(),self.image(),'s')
        self.assertEqual(r['geometry_space'],'SOURCE_IMAGE_NORMALIZED_NOT_SURVEYED')
    def test_mismatched_source_refused(self):
        with self.assertRaises(ValueError):review(self.packet(),self.image(),'wrong')
    def test_invalid_numeric_coordinate_refused(self):
        p=self.packet(points=[[float('nan'),.2],[.8,.2]])
        with self.assertRaises(ValueError):validate_packet(p,'s')
    def test_two_source_claims_not_merged(self):
        p=self.packet();p['claims'].append(dict(p['claims'][0],id='mark-2',points=[[.1,.7],[.8,.7]]))
        r=review(p,self.image(),'s')
        self.assertEqual(len(r['reviews']),2)
        self.assertEqual(r['ink_compatible'],1)
        self.assertEqual(r['held'],1)
    def test_duplicate_identity_refused(self):
        p=self.packet();p['claims'].append(p['claims'][0])
        with self.assertRaises(ValueError):validate_packet(p,'s')
    def test_label_is_tentative(self):
        r=review({'source_id':'s','claims':[{'id':'a','kind':'TEXT_LABEL','style':'UNKNOWN','points':[[.5,.5]],'label':'trampoline'}]},self.image(),'s')
        self.assertEqual(r['reviews'][0]['verdict'],'MODEL_LABEL_REQUIRES_INDEPENDENT_REVIEW')
    def test_empty_packet_is_useful_cv_only(self):
        r=review({'source_id':'s','claims':[]},self.image(),'s')
        self.assertGreater(r['detected_dash_groups'],0)
        self.assertTrue(r['next_probe'].startswith('Ask a visual'))
    def test_provenance_receipt(self):
        a=review(self.packet(),self.image(),'s');b=review(self.packet(),self.image(),'s')
        self.assertEqual(a['receipt_sha256'],b['receipt_sha256'])
    def test_far_source_claim_not_accepted(self):
        r=review(self.packet(points=[[.1,.64],[.3,.68]]),self.image(),'s')
        self.assertEqual(r['held'],1)
    def test_unknown_stroke_holds(self):
        self.assertEqual(review(self.packet('UNKNOWN'),self.image(),'s')['held'],1)
    def test_bool_coordinates_refused(self):
        p=self.packet(points=[[True,.2],[.3,.4]])
        with self.assertRaises(ValueError):validate_packet(p,'s')
    def test_too_many_points_refused(self):
        p=self.packet(points=[[i/50,.2] for i in range(31)])
        with self.assertRaises(ValueError):validate_packet(p,'s')
    def test_distances(self):
        self.assertAlmostEqual(_point_line_distance((.5,.1),(0,0),(1,0)),.1)
if __name__=='__main__':unittest.main()
