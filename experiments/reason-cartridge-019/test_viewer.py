"""Verify that the real two-circle viewer is standalone and source-scoped."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from viewer import build


class MirrorViewerTests(unittest.TestCase):
    def test_self_contained_two_circle_view_has_no_external_javascript(self):
        with TemporaryDirectory() as temp:
            folder=Path(temp)
            benchmark=folder/"source.json"
            output=folder/"golden-mirror.html"
            synthetic={
                "schema":"motif.reason.golden-mirror.benchmark.v1",
                "source_scenarios":24,
                "human_love_or_welfare_not_measured":True,
                "case_results":[{
                    "case":"FICTIONAL_NO_CONTACT","chosen":"WAIT",
                    "stage":"WAIT_NO_CONTACT",
                    "self_assumed_welcome":{"VISIT":"YES"},
                    "other_explicit_wishes":{"VISIT":"NO"},
                    "other_scoped_permissions":[],
                    "projection_dangers":["VISIT"],
                    "difference_preserved":[],
                    "blocked_actions":{"VISIT":["OTHER_DECLINED"]},
                    "naive_self_projection_choice":"VISIT",
                    "other_only_no_self_choice":"WAIT",
                }],
            }
            benchmark.write_text(json.dumps(synthetic),encoding="utf8")
            result=build(benchmark,output)
            html=output.read_text(encoding="utf8")
            self.assertTrue(result["external_requests"] is False)
            self.assertEqual(result["scenes"],1)
            self.assertIn('class="self"',html)
            self.assertIn('class="other"',html)
            self.assertIn('id="case-select"',html)
            self.assertIn('"projection_dangers":["VISIT"]',html)
            self.assertIn("not permission to act",html)
            self.assertNotIn('<script src="https://',html)
            self.assertNotIn('permission_to_execute":true',html.lower())


if __name__=="__main__":
    unittest.main()
