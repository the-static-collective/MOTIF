"""Actual FIELD-007 CV -> FIELD-010 editable board integration, synthetic only."""
import json, tempfile, unittest
from pathlib import Path
import cv2, numpy as np
from autodraft import propose, to_board, image_to_board

class Field011(unittest.TestCase):
    def source(self):
        g=np.full((480,900),220,np.uint8)
        for y in range(30,475,28): cv2.line(g,(20,y),(870,y),175,1)
        for x in range(130,420,41): cv2.line(g,(x,115),(x+17,115),30,2)
        for y in range(180,415,34): cv2.line(g,(690,y),(690,y+15),30,2)
        return g
    def test_real_cv_into_board(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'sample.png';cv2.imwrite(str(p),self.source())
            packet=propose(p)
            self.assertGreaterEqual(len(packet['items']),1)
            self.assertFalse(packet['asserts_safety'])
            self.assertFalse(packet['asserts_complete_desired_boundary'])
            self.assertEqual(packet['photo_to_sketch_registration'],'NOT_PERFORMED')
            b=to_board(packet)
            self.assertEqual(b['base']['source'],'user_sketch')
            self.assertEqual(b['base']['coordinate_frame'],'sketch_normalized')
            self.assertEqual(len(b['base']['items']),len(packet['items']))
            self.assertTrue(all(i['status']=='tentative' for i in b['base']['items']))
            self.assertTrue(all(not i['movable'] for i in b['base']['items']))
            self.assertTrue(all(all(0 <= v <= 1 for pt in i['points'] for v in pt) for i in b['base']['items']))
    def test_aspect_ratio_letterbox(self):
        self.assertEqual(image_to_board((0,0),800,800),[.275,0])
        self.assertEqual(image_to_board((1,1),800,800),[.725,1])
        self.assertEqual(image_to_board((.5,.5),800,800),[.5,.5])
    def test_no_fake_full_boundary(self):
        with self.assertRaises(ValueError):
            to_board({'asserts_complete_desired_boundary':True,'asserts_safety':False,'items':[]})
    def test_no_guess_on_empty(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'blank.png'
            cv2.imwrite(str(p),np.full((400,600),230,np.uint8))
            packet=propose(p)
            self.assertEqual(packet['items'],[])
            self.assertEqual(to_board(packet)['base']['items'],[])
    def test_source_geometry_is_sourced(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'sample.png';cv2.imwrite(str(p),self.source())
            packet=propose(p)
            for i in packet['items']:
                self.assertEqual(i['evidence']['source_sha256'],packet['source_sha256'])
                self.assertEqual(i['evidence']['semantic_status'],'POSSIBLE_MARK__NOT_CONFIRMED_BOUNDARY')
                self.assertFalse(i['evidence']['safety_certified'])
if __name__=='__main__':unittest.main()
