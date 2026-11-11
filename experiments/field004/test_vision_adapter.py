import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from types import SimpleNamespace
from vision_adapter import ingest_photos, _validated_input
from engine import run


class FakeClient:
    def __init__(self, text):
        self.calls=[]
        self.text=text
        self.responses=self
    def create(self,**kw):
        self.calls.append(kw)
        return SimpleNamespace(output_text=self.text)


class VisionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.p=str(Path(self.tmp.name)/'dummy.jpg')
        Path(self.p).write_bytes(b'not a real image, protocol only')
        self.good=json.dumps({'observations':[
            {'id':'o1','kind':'EXISTING_BARRIER','subject':'metal fencing',
             'status':'PHOTO_OBSERVED','source':'image:0','detail':'unknown anchors'},
            {'id':'o2','kind':'RIGID_PANEL','subject':'cage panel',
             'status':'PHOTO_OBSERVED','source':'image:0','detail':'dimensions unknown'},
            {'id':'o3','kind':'TARGET_ROUTE','subject':'dotted route',
             'status':'MODEL_TENTATIVE','source':'image:0','detail':'proposed path?'}
        ]})

    def test_no_implicit_transmission(self):
        fake=FakeClient(self.good)
        with self.assertRaises(PermissionError):
            ingest_photos([self.p],'boundary',model='fake',client=fake)
        self.assertEqual(fake.calls,[])

    def test_optin_mock_model_produces_options_without_dialogue(self):
        fake=FakeClient(self.good)
        packet=ingest_photos([self.p],'make dog boundary',model='fake',
                             allow_external=True,client=fake)
        report=run(packet)
        self.assertIn('relocate_installed',{v['id'] for v in report['inferences']})
        self.assertEqual(report['dialogue_round_trips_needed_to_propose_options'],0)
        self.assertEqual(len(fake.calls),1)
        self.assertTrue(fake.calls[0]['input'][0]['content'][1]['image_url'].startswith('data:image/jpeg;base64,'))

    def test_cannot_launder_user_status_from_vision(self):
        data=json.loads(self.good);data['observations'][0]['status']='USER_REPORTED'
        with self.assertRaises(ValueError): _validated_input('dog boundary',data,1)

    def test_cannot_cite_nonexistent_images(self):
        data=json.loads(self.good);data['observations'][0]['source']='image:90'
        with self.assertRaises(ValueError): _validated_input('dog boundary',data,1)

    def test_untrusted_extra_output_is_rejected(self):
        fake=FakeClient(json.dumps({'observations':[],'approval':'safe'}))
        with self.assertRaises(ValueError):
            ingest_photos([self.p],'dog boundary',model='fake',allow_external=True,client=fake)

    def test_model_cannot_invent_200lb_fastener_as_user_fact(self):
        packet=_validated_input('dog boundary',json.loads(self.good),1)
        self.assertEqual(packet.joiners_available,'UNKNOWN')
        self.assertFalse(run(packet)['verified_safe_pet_containment'])


if __name__=='__main__': unittest.main()
