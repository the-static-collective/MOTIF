"""Viewer can display the real source graph and never execute an action."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from viewer import build


class SourceViewerTest(unittest.TestCase):
    def test_renders_explicit_errors_ambiguous_proof_and_original_elf_results(self):
        with TemporaryDirectory() as temp:
            src=Path(temp)/"benchmark.json"
            dst=Path(temp)/"many-truth.html"
            sample={
                "schema":"motif.reason023.many-truth-benchmark.v1",
                "external_test_counts":{
                    "total":250,"source_single_answer":220,
                    "source_non_unique":30,"single_answer_wrong":2,
                },
                "permission_to_execute":False,"external_actions":False,
                "source_nonunique_examples":[{
                    "source_id":"TOY-1","question":"What did Bill give to Mary?",
                    "all_source_supported_answers":["apple","football"],
                    "source_gold_for_scoring_only":"apple",
                    "old_answer":"football",
                    "gold_is_in_ambiguity_set":True,
                    "complete_source_witnessed_graph":{
                        "proof_edges":[],"assumptions_considered":[],
                    },
                }],
                "independently_pinned_011_four_value_cases":[{
                    "case":"BOTH","status":"BOTH",
                    "context":{"person":"P","epoch":"R1","proposition":"W"},
                    "support_source_ids":["S1"],"refute_source_ids":["S2"],
                    "unrelated_scoped_source_claims":[],
                    "original_011_verdict":"BOTH",
                }],
                "scripted_ambiguous_case":{
                    "owner_confirmed":{"current_source_hypothesis":"football"},
                    "owner_declined":{"stage":"HOLD_SOURCE_REFUSED"},
                    "no_contact":{"stage":"HOLD_NO_QUESTION_PERMISSION"},
                    "no_source_owner":{"stage":"HOLD_AMBIGUITY_NEEDS_SOURCE_PERMISSION"},
                },
                "scope_sensitive_original_019_elves":[{
                    "recommended_read_only_question_or_wait":"WAIT",
                    "four_original_subprocess_reports":{
                        "CRITIC":{"judgments":{"ASK_PREFERENCE":{
                            "refusals":["NO_QUESTION_PERMISSION"]}}}},
                }],
            }
            src.write_text(json.dumps(sample),encoding="utf8")
            details=build(src,dst)
            html=dst.read_text(encoding="utf8")
            self.assertEqual(details["external_test_cases"],250)
            self.assertFalse(details["network_requests"])
            self.assertIn('class="self"',html)
            self.assertIn('class="other"',html)
            self.assertIn('id="example"',html)
            self.assertIn('id="polar"',html)
            self.assertIn("HOLD_SOURCE_REFUSED",html)
            self.assertIn("TOY-1",html)
            self.assertNotIn('<script src="http',html)

    def test_rejects_incorrect_scoring_or_action_authority(self):
        with TemporaryDirectory() as temp:
            src=Path(temp)/"b.json"
            src.write_text(json.dumps({
                "schema":"motif.reason023.many-truth-benchmark.v1",
                "external_test_counts":{"total":250},
                "external_actions":True,"permission_to_execute":False,
            }),encoding="utf8")
            with self.assertRaises(ValueError):
                build(src,Path(temp)/"out.html")


if __name__=="__main__":
    unittest.main()
