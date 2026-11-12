import unittest, tempfile, json, sys
from pathlib import Path
from hashlib import sha256
import numpy as np
import cv2
from autodraft import fit_point, packet_from_components, from_image, pack_model_claims

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'field010'))

class DraftTests(unittest.TestCase):
    def picture(self):
        im=np.full((520,900),200,np.uint8)
        for y in range(32,520,24):cv2.line(im,(25,y),(875,y),170,1)
        for x in range(150,500,39):cv2.line(im,(x,112),(x+17,112),32,2)
        for y in range(205,430,29):cv2.line(im,(697,y),(697,y+16),35,2)
        return im
    def test_letterbox_mapping(self):
        self.assertEqual(fit_point((0,0),900,900),[.275,0.0]);self.assertEqual(fit_point((1,1),900,900),[.725,1.0]);
        self.assertEqual(fit_point((0.5,0.5),900,900),[.5,.5])
    def test_source_lines_not_physical_lengths(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source.png';cv2.imwrite(str(p),self.picture())
            r=from_image(p)
            self.assertGreaterEqual(len(r['items']),1)
            self.assertFalse(r['asserts_complete_desired_boundary'])
            self.assertFalse(r['asserts_physical_scale'])
            self.assertFalse(r['asserts_safety'])
            self.assertEqual(r['photo_to_sketch_registration'],'NOT_PERFORMED')
            self.assertEqual(r['source_sha256'],sha256(p.read_bytes()).hexdigest())
            self.assertTrue(all(i['status']=='tentative' for i in r['items']))
            self.assertTrue(all(i['evidence']['semantic_status']=='POSSIBLE_MARK__NOT_CONFIRMED_BOUNDARY' for i in r['items']))
            self.assertTrue(all(len(i['evidence']['source_normalized_points'])>=3 for i in r['items']))
    def test_no_source_crossing(self):
        digest='e'*64
        packet={'source_id':'other','claimed_complete_route':False,'claims':[]}
        with self.assertRaises(ValueError):pack_model_claims(packet,source_sha256=digest,width=800,height=450,source_id='sketch-1')
    def test_model_complete_route_refused(self):
        packet={'source_id':'sketch-1','claimed_complete_route':True,'claims':[]}
        with self.assertRaises(ValueError):pack_model_claims(packet,source_sha256='0'*64,width=800,height=450,source_id='sketch-1')
    def test_model_is_not_observation(self):
        packet={'source_id':'sketch-1','claimed_complete_route':False,'claims':[
          {'kind':'VISIBLE_MARK','style':'DOTTED','points':[[.2,.2],[.3,.2],[.4,.2]]}]}
        x=pack_model_claims(packet,source_sha256='f'*64,width=1000,height=450,source_id='sketch-1')
        self.assertEqual(x['method'],'UNVERIFIED_VLM_PROPOSAL_REQUIRES_PIXEL_CRITIQUE')
        self.assertEqual(x['items'][0]['status'],'tentative')
    def test_no_claims_does_not_guess(self):
        r=packet_from_components(width=800,height=400,groups=[],source_sha256='a'*64)
        self.assertEqual(r['items'],[])
    def test_reject_bad_points(self):
        for points in ([[1.1,.2],[.4,.2],[.7,.2]],[[-.1,.1],[.2,.2],[.3,.3]]):
            with self.assertRaises(ValueError):packet_from_components(width=1000,height=450,groups=[{'axis':'H','points':points}],source_sha256='a'*64)
    def test_exact_coordinate_inverse(self):
        p=fit_point((.8,.3),600,300)
        self.assertAlmostEqual(p[0],.77,places=4)
        self.assertAlmostEqual(p[1],.3,places=4)

if __name__=='__main__':unittest.main()
