import unittest
from error_dividend import Owner,DEV
from hypermap import ReasonHypermap
from viewer import render

class ViewerTests(unittest.TestCase):
    def make(self):
        o=Owner(DEV[0],"truthful")
        m=ReasonHypermap(o)
        p=m.choose_test()
        m.resolve(o,p)
        return m
    def test_01_clickable_lenses_and_source_nodes_are_embedded(self):
        page=render(self.make().public_graph())
        self.assertIn('id="plot"',page)
        self.assertIn('value="epistemic"',page)
        self.assertIn('value="narrative"',page)
        self.assertIn('function draw()',page)
        self.assertIn('motif.reason-hypermap/v0',page)
    def test_02_no_real_world_or_owner_authority_display(self):
        page=render(self.make().public_graph())
        self.assertIn("No real actions.",page)
        self.assertIn("Public synthetic specimen only.",page)
        self.assertNotIn("<iframe",page)
        self.assertNotIn("fetch(",page)
    def test_03_external_state_or_forged_authority_rejected(self):
        p=self.make().public_graph()
        p["authority"]="owner-local"
        with self.assertRaisesRegex(ValueError,"UNSAFE_VIEWER_INPUT"):render(p)
        p["authority"]="none";p["world"]="PRIVATE"
        with self.assertRaisesRegex(ValueError,"NOT_PUBLIC_SYNTHETIC_MAP"):render(p)
    def test_04_html_script_escapes_source_content(self):
        p=self.make().public_graph()
        p["nodes"][next(iter(p["nodes"]))]["label"]="</script><b>unsafe</b>"
        page=render(p)
        self.assertNotIn("</script><b>unsafe</b>",page)
        self.assertIn("\\u003c/script\\u003e",page)

if __name__=="__main__":unittest.main()
