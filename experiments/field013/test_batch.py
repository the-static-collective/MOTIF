import unittest,tempfile,json
from pathlib import Path
from batch_vlm import PhotoRequest,parse_photo,inspect

class TestBatch(unittest.TestCase):
 def test_explicit_consent(self):
  with self.assertRaises(PermissionError):inspect([PhotoRequest('photo-0',Path('missing'))])
 def test_parse_ref(self):
  self.assertEqual(parse_photo('photo-0=/tmp/z.jpg').photo_id,'photo-0')
  with self.assertRaises(ValueError):parse_photo('not a good photo id=/tmp/z.jpg')
 def test_batch_run_with_stub_not_real_model(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'demo.png';p.write_bytes(b'NOT A REAL IMAGE TEST FIXTURE')
   def fake(photo,model,*,consent):
    self.assertTrue(consent)
    return {'objects':[{'label':'unverified rectangular object', 'bbox':[.1,.1,.45,.7],'possible_role':'boundary_module'}]}
   r=inspect([PhotoRequest('photo-0',p)],consent=True,ask=fake)
   self.assertEqual(len(r['packets'][0]['items']),1)
   self.assertFalse(r['structural_safety_verified'])
   self.assertFalse(r['photo_to_yard_registration'])
   self.assertEqual(r['packets'][0]['items'][0]['mobility'],'unknown')
   self.assertEqual(r['packets'][0]['items'][0]['status'],'tentative')
   self.assertEqual(r['packets'][0]['items'][0]['provenance'],'LOCAL_VLM_TENTATIVE')
 def test_duplicates_fail_closed(self):
  with self.assertRaises(ValueError):inspect([PhotoRequest('a',Path('x')),PhotoRequest('a',Path('y'))],consent=True,ask=lambda *a,**kw: {'objects':[]})
 def test_zero_objects_retained_as_empty(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'demo.jpg';p.write_bytes(b'DUMMY')
   r=inspect([PhotoRequest('photo-1',p)],consent=True,ask=lambda *a,**kw:{'objects':[]})
   self.assertEqual(r['packets'][0]['items'],[])
if __name__=='__main__':unittest.main()
