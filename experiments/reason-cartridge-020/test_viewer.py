"""Offline viewer regression: two circles, source data, no network access."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from viewer import build


class GoldenMirrorLearnsViewerTests(unittest.TestCase):
    def test_svg_contains_both_corrected_circles_without_remote_scripts(self):
        with TemporaryDirectory() as t:
            root=Path(t)
            source=root/"benchmark.json"
            destination=root/"mirror-learns.html"
            sample={
                "schema":"motif.reason.golden-mirror-learns.benchmark.v1",
                "synthetic_scenarios":16,
                "source_author_matches":16,
                "learned_executable_templates":2,
                "source_teacher_unseen_positive_correct":8,
                "source_teacher_unseen_positive_total":8,
                "source_teacher_unseen_negative_rejected":6,
                "source_teacher_unseen_negative_total":6,
                "no_empathy_or_experienced_love_measured":True,
                "external_actions":False,
                "independent_source_teacher_skill_certificate":{
                    "self_capability_granted":True,
                },
                "learned_program":{"templates":[]},
                "all_case_outcomes":[{
                    "case":"FICTIONAL_PROJECTION","source_revision":1,
                    "new_dual_circle_result":"HOLD_NO_CONTACT",
                    "old_fixed_grammar_result":"HOLD_NO_CONTACT",
                    "new_reported_goal":None,"original_017_was_inadequate":False,
                    "recipient_source_turns":0,"projection_status":"OTHER_UNCERTAIN",
                    "concept_versions":[],"discarded_concepts":[],
                    "four_process_critic_approved":False,
                }],
            }
            source.write_text(json.dumps(sample),encoding="utf8")
            result=build(source,destination)
            html=destination.read_text(encoding="utf8")
            self.assertEqual(result["case_count"],1)
            self.assertTrue(result["external_requests"] is False)
            self.assertIn('class="diagram"',html)
            self.assertIn('class="metrics"',html)
            self.assertIn('id="other"',html)
            self.assertIn('id="self"',html)
            self.assertIn("permission to execute",html.lower())
            self.assertIn("FICTIONAL_PROJECTION",html)
            self.assertNotIn('<script src="http',html)
            self.assertGreater(destination.stat().st_size,5000)

    def test_visualization_refuses_non_synthetic_or_action_enabled_input(self):
        with TemporaryDirectory() as t:
            a=Path(t)/"b.json"
            a.write_text(json.dumps({
                "schema":"motif.reason.golden-mirror-learns.benchmark.v1",
                "synthetic_scenarios":16,
                "no_empathy_or_experienced_love_measured":True,
                "external_actions":True,
            }),encoding="utf8")
            with self.assertRaises(ValueError):
                build(a,Path(t)/"denied.html")


if __name__=="__main__":
    unittest.main()
