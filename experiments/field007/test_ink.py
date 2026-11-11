import unittest
import numpy as np
import cv2
from ink import extract_dashes

class InkTest(unittest.TestCase):
    def scene(self,seed=9):
        rng=np.random.default_rng(seed)
        im=np.clip(229+rng.normal(0,2,(600,900)),0,255).astype('uint8')
        for y in range(38,600,30):cv2.line(im,(35,y),(865,y),181,1)
        for x in range(145,520,43):cv2.line(im,(x,126),(x+16,126),25,3)
        for y in range(260,440,32):cv2.line(im,(713,y),(713,y+14),25,3)
        cv2.line(im,(160,500),(640,500),25,3)
        cv2.putText(im,'GARAGE',(320,320),cv2.FONT_HERSHEY_SIMPLEX,1,35,2)
        return im
    def test_two_axes_detected(self):
        found=extract_dashes(self.scene(),max_candidates=8)
        self.assertIn('H',[x.axis for x in found])
        self.assertIn('V',[x.axis for x in found])
    def test_dashes_really_supported(self):
        found=extract_dashes(self.scene())
        self.assertTrue(any(x.axis=='H' and x.width_pixels>=200 for x in found))
        self.assertTrue(any(x.axis=='V' and x.width_pixels>=70 for x in found))
    def test_not_invent_solid_line_as_dashed(self):
        found=extract_dashes(self.scene())
        self.assertFalse(any(c.axis=='H' and c.points and .79<c.points[0][1]<.88 for c in found))
    def test_blank_abstains(self):
        self.assertEqual(extract_dashes(np.full((300,450),240,np.uint8)),())
    def test_ruled_only_abstains(self):
        im=np.full((400,500),225,np.uint8)
        for y in range(35,400,28):cv2.line(im,(20,y),(480,y),180,1)
        self.assertEqual(extract_dashes(im),())
    def test_real_photo_source_not_promoted(self):
        found=extract_dashes(self.scene())
        self.assertTrue(all(x.quality=='TENTATIVE_DASH_LIKE_NOT_CONFIRMED_INTENT' for x in found))
        self.assertTrue(all(x.as_packet('paper')['status']=='TENTATIVE' for x in found))
    def test_valid_pixel_bounds(self):
        found=extract_dashes(self.scene())
        self.assertTrue(all(0<=v<=1 for x in found for xy in x.points for v in xy))
    def test_reject_invalid_crop(self):
        with self.assertRaises(ValueError):extract_dashes(self.scene(),paper_bbox=(-10,0,200,200))
    def test_reject_too_small(self):
        with self.assertRaises(ValueError):extract_dashes(np.zeros((20,20),np.uint8))
    def test_variations(self):
        for seed in range(5):
            found=extract_dashes(self.scene(seed))
            self.assertTrue(any(x.axis=='H' for x in found))
            self.assertTrue(any(x.axis=='V' for x in found))
if __name__=='__main__':unittest.main()
