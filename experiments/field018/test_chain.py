import json,sys,tempfile,unittest
from pathlib import Path
import numpy as np
import cv2
from chain import inspect_source,synthetic_chain,reframe_hints,run

class ChainTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)/'paper.png'
        self.image=np.full((600,900),224,np.uint8)
        for y in range(38,580,30):cv2.line(self.image,(25,y),(875,y),185,1)
        for x in range(150,550,47):cv2.line(self.image,(x,157),(x+19,157),30,2)
        cv2.imwrite(str(self.p),self.image)

    def test_source_hash_and_pixels(self):
        r=inspect_source(self.p)
        self.assertEqual(len(r['sources']['sketch_sha256']),64)
        self.assertGreaterEqual(r['perception']['ink_groups'],1)
        self.assertEqual(r['perception']['photos_checked'],0)

    def test_photo_pair_real_image_processing(self):
        p2=Path(self.tmp.name)/'blank.png'; cv2.imwrite(str(p2),np.full((600,900),244,np.uint8))
        q=inspect_source(self.p,[p2])
        self.assertEqual(q['perception']['photos_checked'],1)
        self.assertEqual(q['perception']['photo_pairs_checked'],0)
        self.assertEqual(q['perception']['semantic_objects_detected'],0)

    def test_two_different_sources_have_two_hashes(self):
        p2=Path(self.tmp.name)/'another.png';cv2.imwrite(str(p2),np.full((600,900),234,np.uint8))
        p3=Path(self.tmp.name)/'third.png';cv2.imwrite(str(p3),np.full((600,900),100,np.uint8))
        r=inspect_source(self.p,[p2,p3])
        self.assertEqual(len(set(r['sources']['photos_sha256'])),2)
        self.assertEqual(r['perception']['photo_pairs_checked'],1)
        self.assertEqual(r['perception']['photo_pairs_held'],1)

    def test_same_file_as_photo_rejected(self):
        with self.assertRaises(ValueError):inspect_source(self.p,[self.p])

    def test_repeated_photo_rejected(self):
        p2=Path(self.tmp.name)/'p2.png';cv2.imwrite(str(p2),self.image)
        with self.assertRaises(ValueError):inspect_source(self.p,[p2,p2])

    def test_source_missing_rejected(self):
        with self.assertRaises(ValueError):inspect_source(Path(self.tmp.name)/'absent.png')

    def test_semantics_never_claimed_from_ink(self):
        r=inspect_source(self.p,source_hints=['cage panel'])
        self.assertEqual(r['perception']['semantic_objects_detected'],0)
        self.assertEqual(r['sources']['user_hints'][0]['source'],'USER_STATEMENT_NOT_IMAGE_RECOGNITION')
        self.assertIsNone(r['sources']['user_hints'][0]['photo_bbox'])

    def test_source_hints_are_hypotheses(self):
        r=inspect_source(self.p,source_hints=['old chair','cage panel'])
        self.assertFalse(r['reasoning']['candidate_reframes'][0]['confirmed'])
        self.assertTrue(all(not x['confirmed'] for x in r['reasoning']['candidate_reframes']))

    def test_empty_hints_no_unasked_materials(self):
        r=inspect_source(self.p)
        self.assertEqual(r['reasoning']['candidate_reframes'],[])

    def test_invalid_hint_rejected(self):
        with self.assertRaises(ValueError):inspect_source(self.p,source_hints=[''])

    def test_real_geometry_always_hold(self):
        r=inspect_source(self.p)
        self.assertEqual(r['reconstruction']['status'],'HOLD_NO_CALIBRATED_3D_FROM_SOURCES')
        self.assertFalse(r['physics']['safe_dog_enclosure_established'])

    def test_no_claim_of_real_models(self):
        r=inspect_source(self.p)
        self.assertEqual(r['claims']['model_inference_calls'],0)
        self.assertFalse(r['claims']['fully_automatic_photo_to_physics_chain_passed'])

    def test_real_receipt_reproducible(self):
        self.assertEqual(inspect_source(self.p)['receipt_sha256'],inspect_source(self.p)['receipt_sha256'])

    def test_changing_pixels_changes_receipt(self):
        before=inspect_source(self.p)['receipt_sha256']
        cv2.circle(self.image,(400,320),20,25,-1);cv2.imwrite(str(self.p),self.image)
        self.assertNotEqual(before,inspect_source(self.p)['receipt_sha256'])

    def test_synthetic_mechanics_current_modules(self):
        r=synthetic_chain(16)
        self.assertIn('FIELD-015',str(r['engines_actually_invoked']))
        self.assertIn('FIELD-017',str(r['engines_actually_invoked']))
        self.assertEqual(r['first']['evaluated'],16)
        self.assertTrue(r['winning_layout_changed'])

    def test_synthetic_no_source_fraud(self):
        r=synthetic_chain(16)
        self.assertTrue(r['observation']['NOT_FROM_REAL_PHOTOGRAPH'])
        self.assertFalse(r['source_real_world_linked'])
        self.assertFalse(r['animal_containment_certified'])

    def test_synthetic_budget_one_no_magic_revision(self):
        r=synthetic_chain(1)
        self.assertEqual(r['first']['evaluated'],1)
        self.assertFalse(r['winning_layout_changed'])

    def test_synthetic_observation_changes_world_hash(self):
        r=synthetic_chain(16)
        self.assertNotEqual(r['initial_world_sha256'],r['updated_world_sha256'])

    def test_combined_stage_gate_doesnt_claim_end_to_end(self):
        r=run(self.p,source_hints=['panel','chair'],budget=8)
        keys={x['name']:x['status'] for x in r['stage_gate']}
        self.assertEqual(keys['Automatic image-semantic inventory'],'BLOCKED')
        self.assertEqual(keys['Synthetic 3D mechanics + recursive revision'],'PASS_SYNTHETIC_ONLY')
        self.assertEqual(keys['Verified safe physical construction'],'NOT_TESTED')

    def test_privacy_false(self):
        r=run(self.p,budget=2)
        self.assertFalse(r['privacy_images_embedded'])
        self.assertFalse(r['real']['privacy']['images_sent_to_external_provider'])

    def test_bad_budget(self):
        for budget in (0,300,1.5,True):
            with self.subTest(budget=budget):
                with self.assertRaises(ValueError):run(self.p,budget=budget)

if __name__=='__main__':unittest.main()
