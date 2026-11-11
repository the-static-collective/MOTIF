import tempfile,unittest,sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]/'field007'))
from benchmark import gen
from loop import run

class LoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        import cv2
        self.image=self.root/'sketch.png';cv2.imwrite(str(self.image),gen(19,'both'))
    def tearDown(self):self.tmp.cleanup()
    def packet(self,loc=.7):return {'source_id':'sk','claims':[{'id':'bad','kind':'VISIBLE_MARK',
        'style':'DOTTED','points':[[.13,loc],[.65,loc]]}]}
    def test_no_model(self):
        r=run(self.image,'sk',self.root/'out')
        self.assertEqual(r['model_call_count'],0)
        self.assertEqual(r['first']['claims'],[])
        self.assertTrue((self.root/'out'/'first_pass.png').exists())
    def test_contradiction_emits_crop(self):
        r=run(self.image,'sk',self.root/'out',first_packet=self.packet())
        self.assertEqual(r['focus']['status'],'CROP_CREATED_FOR_HUMAN_OR_OPT_IN_LOCAL_VLM')
        self.assertTrue((self.root/'out'/'focus.png').exists())
    def test_second_pass_remains_tentative(self):
        r=run(self.image,'sk',self.root/'out',first_packet=self.packet(),second_packet={'source_id':'sk','claims':[]})
        self.assertFalse(r['change']['automatic_evidence_promotion'])
        self.assertFalse(r['complete_route_verified'])
    def test_supported_line_no_emergency_crop(self):
        r=run(self.image,'sk',self.root/'out',first_packet=self.packet(.215))
        self.assertEqual(r['focus']['status'],'NO_UNSUPPORTED_MODEL_TRACE')
    def test_mismatched_source_in_model_packet_fails(self):
        with self.assertRaises(ValueError):run(self.image,'sk',self.root/'out',first_packet={'source_id':'bad','claims':[]})
    def test_privacy_flag(self):
        self.assertTrue(run(self.image,'sk',self.root/'out')['image_source_private'])
if __name__=='__main__':unittest.main()
