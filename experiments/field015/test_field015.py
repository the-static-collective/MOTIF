"""Offline authored negative controls; real model checkpoints are NOT exercised."""
import tempfile,unittest
from pathlib import Path
import numpy as np
from physics import Panel,screen,assembly
from truss import Node,Link,solve
from reconstruction import witness,compare,mapanything_points,da3_points,run

class Field015(unittest.TestCase):
    def base(self,opacity=1):
        return Panel("p",1.5,1,5,.35,opacity,1.4,.6,"FREESTANDING")
    def test_opaque_wind_fail(self):
        p=screen(self.base(),8)
        self.assertAlmostEqual(p["force_n"],82.32)
        self.assertEqual(p["status"],"MODEL_FAILS_ASSUMED_LOAD_CASE")
    def test_open_mesh_different(self):
        p=screen(self.base(.2),8)
        self.assertAlmostEqual(p["force_n"],16.464)
        self.assertFalse(p["verified_structure"])
    def test_unknown_never_approved(self):
        self.assertEqual(screen(Panel("unknown"),8)["status"],"HOLD_UNKNOWN_PROPERTIES")
    def test_bad_fraction(self):
        with self.assertRaises(ValueError):screen(self.base(1.2),8)
    def test_connected_does_not_certify(self):
        a=self.base();b=Panel("second")
        s=assembly([a,b],[("p","second","ZIP_TIE")],8)
        self.assertFalse(s["overall_stability_verified"])
    def test_singular_chain(self):
        n=[Node("a",0,0,True,True),Node("b",2,0,True,True),Node("c",2,1,fx=50)]
        m=lambda x,y:Link(x,y,2e11,.0001)
        self.assertEqual(solve(n,[m("a","b"),m("b","c")])["status"],"HOLD_SINGULAR_UNBRACED_OR_UNANCHORED")
        self.assertEqual(solve(n,[m("a","b"),m("b","c"),m("a","c")])["status"],"HOLD_UNVALIDATED_3D_AND_JOINTS")
    def test_no_model_inference_consent(self):
        with self.assertRaises(PermissionError):run("da3","none",["no-photo"],"none",False)
    def test_local_checkpoint_missing(self):
        with self.assertRaises(ValueError):run("da3","/missing",[__file__],"no",True)
    def test_mapanything_contract(self):
        self.assertEqual(mapanything_points([{"pts3d":np.ones((3,4,3))}]).shape,(12,3))
        with self.assertRaises(ValueError):mapanything_points([{"pts3d_cam":np.ones((3,4,3))}])
    def test_mock_da3_pose_inverse(self):
        class P:pass
        p=P();p.depth=np.ones((1,4,4))*2
        p.intrinsics=np.array([[[4,0,0],[0,4,0],[0,0,1]]])
        p.extrinsics=np.eye(4)[None,:,:].copy()
        p.extrinsics[0,0,3]=2
        self.assertTrue(np.any(np.isclose(da3_points(p)[:,0],-2)))
    def test_two_models_agree_not_truth(self):
        with tempfile.TemporaryDirectory() as d:
            s=Path(d)/"sketch.jpg";s.write_bytes(b"fake-image-fixture")
            a=witness("MAPANYTHING","test",[str(s)],np.ones((5,3)),False)
            b=witness("DEPTH_ANYTHING_3","test",[str(s)],np.ones((5,3)),False)
            self.assertFalse(a["registered_to_site"])
            self.assertEqual(compare(a,b),"HOLD_NO_INDEPENDENT_POINT_CORRESPONDENCE_OR_METRIC_SITE_FRAME")

if __name__=="__main__":unittest.main()
