"""Offline cross-world interactive marathon viewer smoke tests."""
import copy,json,unittest
from marathon import GROUPS,Marathon,experiment
from viewer_marathon import render

class MarathonViewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runner=Marathon(GROUPS[0],"hypermap_voi");runner.execute()
        cls.record=runner.public_record()
        cls.d={"schema":"motif.odyssey-marathon.viewer/v0",
               "group":list(GROUPS[0]),
               "records":{"hypermap_voi":cls.record},
               "study":experiment(groups=GROUPS[:1],policies=("hypermap_voi",)),
               "external_actions":False}
    def test_01_replays_actually_executed_879_plus_actions(self):
        self.assertGreaterEqual(len(self.record["global_events"]),879)
        page=render(self.d)
        self.assertIn("THE MARATHON",page)
        self.assertIn('id="seek"',page)
        self.assertIn('id="jump"',page)
        self.assertIn("mandatory_handoff",page)
    def test_02_384_distinct_gate_buttons_generated(self):
        page=render(self.d)
        self.assertIn("for(let chapter=0;chapter<4;chapter++)",page)
        self.assertIn("for(let s=0;s<12;s++)",page)
        self.assertIn("for(let gate=0;gate<8;gate++)",page)
    def test_03_no_remote_javascript_or_real_actions(self):
        page=render(self.d)
        self.assertNotIn("fetch(",page)
        self.assertNotIn("<iframe",page)
        self.assertTrue(self.record["hidden_owner_truth_excluded"])
        self.assertFalse(self.record["external_actions"])
    def test_04_script_injection_is_escaped(self):
        x=copy.deepcopy(self.d)
        x["records"]["hypermap_voi"]["global_events"][0]["payload"]["evil"]="</script><b>injected</b>"
        page=render(x)
        self.assertNotIn("</script><b>injected</b>",page)
        self.assertIn("\\u003c/script\\u003e",page)
    def test_05_fake_live_source_is_rejected(self):
        x=copy.deepcopy(self.d)
        x["records"]["hypermap_voi"]["authority"]="owner-local"
        with self.assertRaisesRegex(ValueError,"UNSAFE_MARATHON_RECORD"):render(x)
    def test_06_nonpublic_study_rejected(self):
        x=copy.deepcopy(self.d)
        x["study"]["author_synthetic_only"]=False
        with self.assertRaisesRegex(ValueError,"NON_SYNTHETIC_STUDY"):render(x)

if __name__=="__main__":unittest.main()
