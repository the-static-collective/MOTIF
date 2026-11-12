import copy,json,unittest
from pathlib import Path
from bridge009 import physical_geometry
P=json.loads((Path(__file__).parent/'fixture.json').read_text())

class BridgeTests(unittest.TestCase):
    def test_no_scale_held(self):
        r=physical_geometry(copy.deepcopy(P))
        self.assertTrue(all(x['estimate']['status']=='HOLD' for x in r['estimated_target_spans']))
        self.assertFalse(r['photo_pixels_georegistered'])
    def test_known_reference_conditional(self):
        p=copy.deepcopy(P)
        p['events']=[{'id':'e1','type':'measure','target':'target-one','value':4,'unit':'ft','quality':'user_measured'},
                     {'id':'e2','type':'proportional','value':True,'tolerance':.4}]
        r=physical_geometry(p)
        self.assertEqual(r['anchors'],1)
        self.assertTrue(all(x['estimate']['status']=='CONDITIONAL_SKETCH_GUESS' for x in r['estimated_target_spans']))
        self.assertFalse(r['estimated_target_spans'][0]['physical_installation_verified'])
    def test_rough_guess_not_anchor(self):
        p=copy.deepcopy(P)
        p['events']=[{'id':'e1','type':'measure','target':'target-one','value':4,'unit':'ft','quality':'rough_guess'},
                     {'id':'e2','type':'proportional','value':True,'tolerance':.4}]
        r=physical_geometry(p)
        self.assertEqual(r['anchors'],0)
        self.assertTrue(all(x['estimate']['status']=='HOLD' for x in r['estimated_target_spans']))
    def test_contradictions_hold(self):
        p=copy.deepcopy(P)
        p['events']=[{'id':'e1','type':'measure','target':'target-one','value':4,'unit':'ft','quality':'user_measured'},
                     {'id':'e2','type':'measure','target':'target-two','value':40,'unit':'ft','quality':'user_measured'},
                     {'id':'e3','type':'proportional','value':True,'tolerance':.4}]
        r=physical_geometry(p)
        self.assertTrue(all(x['estimate']['status']=='HOLD' for x in r['estimated_target_spans']))
if __name__=='__main__':unittest.main()
