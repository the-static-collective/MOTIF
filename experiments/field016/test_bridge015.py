import unittest
from bridge015 import evaluate_with_vision
from engine import invented_scene

class BridgeTests(unittest.TestCase):
  def witness(self,engine):
    return {'engine':engine,'checkpoint':'mock-synthetic','image_sha256':['a'*64],
       'xyz':[[0.,0.,1.],[1.,0.,2.],[0.,1.,2.],[1.,1.,3.]],
       'scale':'RELATIVE','real_model_executed':False,'registered_to_site':False}
  def test_zero_models(self):
    r=evaluate_with_vision(invented_scene())
    self.assertFalse(r['site_coordinates_from_model_clouds']);self.assertEqual(r['field015_3d_witnesses'],[])
  def test_one_model_tentative(self):
    r=evaluate_with_vision(invented_scene(),(self.witness('MAPANYTHING'),))
    self.assertEqual(r['field015_3d_witnesses'][0]['engine'],'MAPANYTHING')
    self.assertFalse(r['physical_panel_widths_from_model_clouds'])
  def test_two_models_are_not_ground_truth(self):
    r=evaluate_with_vision(invented_scene(),(self.witness('MAPANYTHING'),self.witness('DEPTH_ANYTHING_3')))
    self.assertFalse(r['cross_model_alignment']['site_geometry_certified'])
    self.assertTrue(r['cross_model_alignment']['status'].startswith('HOLD'))
  def test_bad_model_claim_rejected(self):
    w=self.witness('MAPANYTHING');w['registered_to_site']=True
    with self.assertRaises(ValueError):evaluate_with_vision(invented_scene(),(w,))
  def test_three_models_rejected(self):
    with self.assertRaises(ValueError):evaluate_with_vision(invented_scene(),(self.witness('MAPANYTHING'),)*3)
if __name__=='__main__':unittest.main()
