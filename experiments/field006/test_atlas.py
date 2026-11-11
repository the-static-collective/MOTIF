import json, unittest, tempfile
from pathlib import Path
from atlas import from_dict, svg_atlas, receipt, audit_preservation

FIXTURE=Path(__file__).parent/'fixtures/public_example.json'
class Tests(unittest.TestCase):
    def setUp(self):
        self.raw=json.loads(FIXTURE.read_text());self.atlas=from_dict(self.raw)
    def test_load(self):self.assertEqual(len(self.atlas.landmarks),4)
    def test_receipt(self):self.assertTrue(receipt(self.atlas)['sha256'])
    def test_no_automatic_vision_claim(self):self.assertFalse(receipt(self.atlas)['automatic_image_recognition_performed'])
    def test_no_fake_photo_registration(self):self.assertFalse(receipt(self.atlas)['photos_assumed_georegistered'])
    def test_retention(self):self.assertEqual(audit_preservation(self.atlas,('Wall','Entry'))['retained'],2)
    def test_unknown_in_retention(self):self.assertEqual(audit_preservation(self.atlas,('Wall','Yard'))['missing'],['Yard'])
    def test_private_sketch_not_embedded_by_default(self):
        svg=svg_atlas(self.atlas)
        self.assertIn('intentionally not embedded',svg);self.assertNotIn('base64',svg)
    def test_target_not_existing(self):
        self.assertIn('desired',svg_atlas(self.atlas).lower())
    def test_cross_view_only_topical(self):
        self.assertIn('Photo pixels',svg_atlas(self.atlas))
    def test_deterministic_svg(self):self.assertEqual(svg_atlas(self.atlas),svg_atlas(self.atlas))
    def test_escaped_strings(self):
        self.raw['title']='<script>alert(1)</script>'
        self.raw['landmarks'][0]['label']='<script>bad</script>'
        svg=svg_atlas(from_dict(self.raw));self.assertNotIn('<script>',svg)
    def test_duplicate_source_rejected(self):
        self.raw['sources'].append(dict(self.raw['sources'][0]))
        with self.assertRaises(ValueError):from_dict(self.raw)
    def test_missing_source_rejected(self):
        self.raw['landmarks'][0]['evidence']=['absent']
        with self.assertRaises(ValueError):from_dict(self.raw)
    def test_photo_cannot_create_map_coordinates(self):
        self.raw['landmarks'][0]['evidence']=['photo-a']
        with self.assertRaises(ValueError):from_dict(self.raw)
    def test_infinity_rejected(self):
        self.raw['landmarks'][0]['sketch_xy']=[float('inf'),0.2]
        with self.assertRaises(ValueError):from_dict(self.raw)
    def test_undesired_trace_observed_rejected(self):
        self.raw['traces'][1]['status']='OBSERVED'
        with self.assertRaises(ValueError):from_dict(self.raw)
    def test_bad_claim_link_rejected(self):
        self.raw['claims'][0]['linked_landmarks']=['nonexistent']
        with self.assertRaises(ValueError):from_dict(self.raw)
    def test_unknown_path_does_not_fetch(self):
        self.raw['sources'][0]['local_path']='/secret/not-real.png'
        svg_atlas(from_dict(self.raw),allow_private_images=False)
    def test_missing_explicit_local_image_fails(self):
        self.raw['sources'][0]['local_path']='/secret/not-real.png'
        with self.assertRaises(ValueError):svg_atlas(from_dict(self.raw),allow_private_images=True)
    def test_no_base64_without_explicit_consent(self):
        self.raw['sources'][0]['local_path']='/secret/not-real.png'
        self.assertNotIn('data:image',svg_atlas(from_dict(self.raw)))
    def test_trace_requires_sketch_source(self):
        self.raw['traces'][1]['source']='photo-a'
        with self.assertRaises(ValueError):from_dict(self.raw)
    def test_more_than_two_trace_points_preserved(self):
        self.raw['traces'][0]['points']=[[.1,.1],[.2,.2],[.3,.3]]
        self.assertIn('polyline',svg_atlas(from_dict(self.raw)))
if __name__=='__main__':unittest.main()