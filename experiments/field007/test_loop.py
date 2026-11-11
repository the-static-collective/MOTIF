import unittest,json,sys,tempfile
from pathlib import Path
import cv2
p6=Path(__file__).resolve().parents[1]/'field006'
if not p6.exists():p6=Path(__file__).resolve().parents[1]/'motif_field006'
sys.path.insert(0,str(p6))
from loop import analyze
import test_ink

class LoopTests(unittest.TestCase):
    def setUp(self):
        self.image=test_ink.InkTest().scene()
        self.fixture=json.loads((p6/'fixtures'/'public_example.json').read_text())
    def test_source_sketch_preserved(self):
        before=json.dumps(self.fixture,sort_keys=True)
        r=analyze(self.image,self.fixture['sketch_source'],atlas_packet=self.fixture)
        self.assertEqual(before,json.dumps(self.fixture,sort_keys=True))
        self.assertTrue(r['model_contract']['original_traces_unchanged'])
    def test_no_path_certified(self):
        r=analyze(self.image,'paper')
        self.assertFalse(r['desired_perimeter_complete'])
        self.assertFalse(r['sketch_boundary_intent_inferred'])
    def test_no_photo_coordinate_claim(self):
        r=analyze(self.image,'paper')
        self.assertTrue(r['no_unjustified_photo_to_map_coordinates'])
    def test_contract_review_accepts_only_tentative(self):
        r=analyze(self.image,'paper',atlas_packet=self.fixture)
        self.assertEqual(r['model_contract']['tentative_candidates_accepted'],r['ink']['candidate_count'])
    def test_mismatched_atlas_source_refused(self):
        with self.assertRaises(ValueError):analyze(self.image,'wrong',atlas_packet=self.fixture)
    def test_pixel_digest_present(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'sketch.png';cv2.imwrite(str(p),self.image)
            r=analyze(p,'paper')
            self.assertEqual(len(r['ink']['input_sha256']),64)
    def test_no_real_model_claim(self):
        self.assertFalse(analyze(self.image,'paper')['real_multimodal_model_run'])
if __name__=='__main__':unittest.main()
