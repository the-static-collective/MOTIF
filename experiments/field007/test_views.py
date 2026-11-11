import unittest
import numpy as np
import cv2
from views import compare,cross_photo_packet

class TestViews(unittest.TestCase):
    def textured(self):
        rng=np.random.default_rng(17);im=np.full((380,520),220,np.uint8)
        for i in range(165):
            x,y=int(rng.integers(15,505)),int(rng.integers(15,365))
            color=int(rng.integers(30,180))
            cv2.rectangle(im,(x,y),(x+int(rng.integers(4,22)),y+int(rng.integers(4,16))),color,-1)
        return im
    def test_shifted_same_image(self):
        a=self.textured();M=np.float32([[1,0,13],[0,1,24]])
        b=cv2.warpAffine(a,M,(a.shape[1],a.shape[0]),borderValue=225)
        r=compare(a,b)
        self.assertEqual(r.status,'TENTATIVE_VISUAL_OVERLAP')
        self.assertGreater(r.geometric_inliers,20)
    def test_different_image_holds(self):
        a=self.textured();rng=np.random.default_rng(51)
        b=np.clip(rng.normal(180,20,(380,520)),0,255).astype('uint8')
        self.assertEqual(compare(a,b).status,'HOLD')
    def test_blank_holds(self):
        a=np.full((320,400),220,np.uint8)
        self.assertEqual(compare(a,a).reason,'INSUFFICIENT_FEATURES')
    def test_no_world_placement(self):
        self.assertNotIn('sketch_xy',compare(self.textured(),self.textured()).__dict__)
    def test_input_tiny_refused(self):
        with self.assertRaises(ValueError):compare(np.zeros((5,10),np.uint8),self.textured())
    def test_duplicate_id_refused(self):
        with self.assertRaises(ValueError):cross_photo_packet([('a','x'),('a','y')])
if __name__=='__main__':unittest.main()
