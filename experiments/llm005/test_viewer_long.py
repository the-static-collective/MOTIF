"""Viewer smoke/escape tests with real authored 200+-step completed traces."""
import unittest
from odyssey import LongChain,DEV_SEEDS,experiment,POLICIES
from viewer_long import render

class ViewerLongTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed=DEV_SEEDS[0]
        cls.runs={}
        for p in ("classical_bayes","hypermap_voi"):
            x=LongChain(seed,p);x.execute();cls.runs[p]=x
        cls.data={"schema":"motif.odyssey-viewer/v0","seed":seed,
                  "study":experiment(seeds=DEV_SEEDS[:1],policies=("classical_bayes","hypermap_voi")),
                  "traces":{p:v.public_trace() for p,v in cls.runs.items()},
                  "reason_maps":{str(i):g.public_graph() for i,g in enumerate(cls.runs["hypermap_voi"].maps)},
                  "external_actions":False}
    def test_01_generated_page_is_actual_interactive_html(self):
        page=render(self.data)
        self.assertIn('<input id="seek" type="range"',page)
        self.assertIn('id="sectors"',page)
        self.assertIn('id="jumpError"',page)
        self.assertIn('id="compare"',page)
        self.assertIn('id="lens"',page)
        self.assertIn("report-bears-on-rivals",page)
        self.assertIn("function inspectEvidence",page)
    def test_02_contains_real_219_plus_event_data(self):
        page=render(self.data)
        self.assertGreater(len(self.runs["hypermap_voi"].events),219)
        self.assertIn("commit_correct",page)
        self.assertIn("bridge_relay",page)
        self.assertIn("reason_dividends",page)
    def test_03_no_remote_fetch_or_external_calls(self):
        page=render(self.data)
        self.assertNotIn("fetch(",page)
        self.assertNotIn("<iframe",page)
        self.assertIn("Read-only offline HTML",page)
    def test_04_escaping_blocks_embedded_script_termination(self):
        import copy
        p=copy.deepcopy(self.data)
        p["traces"]["hypermap_voi"]["events"][0]["meta"]["attacker"]="</script><h1>oops</h1>"
        page=render(p)
        self.assertNotIn("</script><h1>oops</h1>",page)
        self.assertIn("\\u003c/script\\u003e",page)
    def test_05_untrusted_world_rejected_before_html(self):
        import copy
        d=copy.deepcopy(self.data)
        d["study"]["author_synthetic_only"]=False
        with self.assertRaisesRegex(ValueError,"NONPUBLIC_STUDY"):render(d)
    def test_06_owner_authority_bypass_rejected(self):
        import copy
        d=copy.deepcopy(self.data)
        d["traces"]["hypermap_voi"]["external_actions"]=True
        with self.assertRaisesRegex(ValueError,"UNSAFE_SOURCE_OR_AUTHORITY"):render(d)

if __name__=="__main__":unittest.main()
