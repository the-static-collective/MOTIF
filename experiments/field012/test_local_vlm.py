import unittest,json
from io import BytesIO
from local_vlm import ask_local_model,make_packet
class Response:
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,n):return json.dumps({'message':{'content':json.dumps({'objects':[
        {'label':'wire panel','possible_role':'boundary_module','bbox':[.1,.1,.7,.8]}]})}}).encode()
class TestVLM(unittest.TestCase):
    def test_default_denies_network(self):
        def trap(*args,**kw):raise AssertionError('Must never call network')
        with self.assertRaises(PermissionError):ask_local_model(b'png','model',opener=trap)
    def test_only_loopback_when_explicit(self):
        seen=[]
        def fake(req,timeout):
            seen.append((req.full_url,timeout))
            return Response()
        got=ask_local_model(b'fake','qwen3-vl:2b-instruct',consent=True,opener=fake)
        self.assertEqual(len(got['objects']),1)
        self.assertEqual(seen[0][0],'http://127.0.0.1:11434/api/chat')
    def test_bad_bbox_rejected(self):
        with self.assertRaises(ValueError):make_packet(b'abc','photo-0',{'objects':[{'label':'x','possible_role':'unknown','bbox':[0,0,2,3]}]})
    def test_safe_packet_never_certifies(self):
        p=make_packet(b'abc','photo-0',{'objects':[{'label':'wire panel','possible_role':'boundary_module','bbox':[0,.1,.9,.9]}]})
        self.assertEqual(p['items'][0]['status'],'tentative')
        self.assertEqual(p['items'][0]['mobility'],'unknown')
        self.assertIsNone(p['items'][0]['width'])
        self.assertFalse(p['safe_assembly_certified'])
        self.assertFalse(p['photo_to_sketch_registration'])
    def test_bad_semantics_fail(self):
        with self.assertRaises(ValueError):make_packet(b'abc','photo-0',{'objects':[{'label':'panel','possible_role':'safe_and_strong','bbox':[0,.1,.9,.9]}]})
    def test_no_hidden_fields(self):
        with self.assertRaises(ValueError):make_packet(b'abc','photo-0',{'objects':[], 'verified_safe':True})
    def test_bad_photo_id(self):
        with self.assertRaises(ValueError):make_packet(b'abc','../../remote/file',{'objects':[]})
if __name__=='__main__':unittest.main()
