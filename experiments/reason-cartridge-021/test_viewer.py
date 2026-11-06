"""Offline two-circle viewer is source-scoped and action-free."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from viewer import build


class SourceVetoViewerTests(unittest.TestCase):
    def test_real_experiment_format_generates_self_other_graph_and_repair_proof(self):
        with TemporaryDirectory() as tmp:
            sample={
                "schema":"motif.reason.other-teaches-self.benchmark.v1",
                "synthetic_source_owners":11,
                "author_outcome_matches":11,
                "no_external_actions":True,
                "not_a_mind_or_love_measurement":True,
                "case_results":[{
                    "case":"FICTIONAL_SOURCE",
                    "learner_stage":"HOLD_SOURCE_FEATURE_WITHHELD",
                    "final_proposal":"HOLD_SOURCE_FEATURE_WITHHELD",
                    "scope_only_permission":None,
                    "new_feature":None,
                    "source_feature_veto_or_disclosure":"WITHHELD_BY_SOURCE",
                    "source_question_receipts":9,
                    "self_role_reversal_wish":"YES",
                    "old_feature_contradiction_witness":{
                        "same_public_features":{"PRIVATE":True,"CHOICE":True},
                        "different_source_answers":["TRAIN-6","TRAIN-7"],
                    },
                    "synthetic_source_observations":[
                        {"id":"TRAIN-6","reply":"NO"},
                        {"id":"TRAIN-7","reply":"YES"},
                    ],
                    "DNF_program":None,
                    "reciprocity":"OTHER_UNCERTAIN",
                    "critic_rejection_reasons":["NO_ACTION_SCOPED_CONSENT"],
                }],
            }
            src=Path(tmp)/"source.json"
            out=Path(tmp)/"mirror.html"
            src.write_text(json.dumps(sample),encoding="utf8")
            result=build(src,out)
            html=out.read_text(encoding="utf8")
            self.assertEqual(result["fictional_cases"],1)
            self.assertFalse(result["external_network_requests"])
            self.assertIn("THE OTHER",html.upper())
            self.assertIn('class="self"',html)
            self.assertIn('class="other"',html)
            self.assertIn('id="source-select"',html)
            self.assertIn("TRAIN-6",html)
            self.assertIn("WITHHELD_BY_SOURCE",html)
            self.assertNotIn('<script src="http',html)
            self.assertGreater(out.stat().st_size,4000)

    def test_rejects_any_action_enabled_or_unverified_input(self):
        with TemporaryDirectory() as tmp:
            src=Path(tmp)/"source.json"
            dst=Path(tmp)/"out.html"
            src.write_text(json.dumps({
                "schema":"motif.reason.other-teaches-self.benchmark.v1",
                "synthetic_source_owners":11,
                "author_outcome_matches":11,
                "no_external_actions":False,
                "not_a_mind_or_love_measurement":True,
                "case_results":[],
            }),encoding="utf8")
            with self.assertRaises(ValueError):
                build(src,dst)


if __name__=="__main__":
    unittest.main()
