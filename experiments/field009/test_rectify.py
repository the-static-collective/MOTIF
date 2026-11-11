import unittest
from geometry import Point,Trace
from rectify import RectangleCalibration,transform,estimate_photo_trace
P=Point

class HomographyTest(unittest.TestCase):
    def cal(self,reviewed=True,ratio=2.0):
        return RectangleCalibration('photo','table',(P(30,10),P(260,50),P(225,180),P(42,150)),
          4,4,'ft',ratio,'human:four corners','tape:4ft width','user:2-to-1 rectangle',reviewed)
    def test_rectified_width(self):
        c=self.cal();t=Trace('edge','photo','table',(c.corners[0],c.corners[1]),'human:edge',0)
        out=estimate_photo_trace(c,t)
        self.assertAlmostEqual(out['length_lower'],4,places=3)
    def test_rectified_height_using_one_length_plus_shape(self):
        c=self.cal();t=Trace('side','photo','table',(c.corners[0],c.corners[3]),'human:side',0)
        out=estimate_photo_trace(c,t)
        self.assertAlmostEqual(out['length_lower'],2,places=3)
    def test_off_plane_refused(self):
        c=self.cal();t=Trace('air','photo','above_table',(P(30,10),P(260,50)),'image',0)
        with self.assertRaises(ValueError):estimate_photo_trace(c,t)
    def test_unreviewed_refused(self):
        c=self.cal(False);t=Trace('a','photo','table',(P(30,10),P(260,50)),'image',0)
        with self.assertRaises(ValueError):estimate_photo_trace(c,t)
    def test_bad_corners_refused(self):
        c=RectangleCalibration('photo','table',(P(0,0),P(100,0),P(5,5),P(0,100)),4,4,'ft',2,'a','b','c',True)
        t=Trace('a','photo','table',(P(0,0),P(100,0)),'image',0)
        with self.assertRaises(ValueError):transform(c,t)
    def test_units_interval_propagates(self):
        c=self.cal()
        c=RectangleCalibration(c.source_id,c.plane_id,c.corners,3.8,4.2,'ft',c.aspect_ratio,'a','b','c',True)
        t=Trace('a','photo','table',(c.corners[0],c.corners[1]),'image',0)
        out=estimate_photo_trace(c,t)
        self.assertAlmostEqual(out['length_lower'],3.8,places=3)
        self.assertAlmostEqual(out['length_upper'],4.2,places=3)
    def test_wrong_assumed_shape_changes_height(self):
        c=self.cal(ratio=1.)
        t=Trace('side','photo','table',(c.corners[0],c.corners[3]),'human:side',0)
        out=estimate_photo_trace(c,t)
        self.assertAlmostEqual(out['length_lower'],4,places=3)
        self.assertIn('separately known aspect ratio',out['flags'][2])
    def test_no_cross_photo_registration(self):
        c=self.cal();t=Trace('a','other-photo','table',(P(30,10),P(260,50)),'image',0)
        with self.assertRaises(ValueError):transform(c,t)

if __name__=='__main__':unittest.main()
