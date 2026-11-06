"""Verify the source-driven dual-circle viewer is offline and read-only."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from viewer import build


class EvidenceViewerTests(unittest.TestCase):
    def test_viewer_displays_errors_as_well_as_correct_source_answers(self):
        with TemporaryDirectory() as tmp:
            src=Path(tmp)/"benchmark.json";dest=Path(tmp)/"mirror.html"
            data={
                "schema":"motif.reason022.unimagined-distinction.benchmark.v1",
                "training_questions":180,"test_questions":750,
                "fictional_obligation_cases":7,
                "permission_to_execute":False,"external_actions":False,
                "external_test":{
                    "COUNT":{"exact_source_answers":175,
                             "incorrect_confident_answers":50,
                             "explicit_abstentions":25,
                             "independently_authored_test_questions":250,
                             "weak_fixed_answer_baseline_exact":70,
                             "model_type_from_source_training":"QUANTITY"},
                    "TIME":{"exact_source_answers":150,
                            "incorrect_confident_answers":60,
                            "explicit_abstentions":40,
                            "independently_authored_test_questions":250,
                            "weak_fixed_answer_baseline_exact":44,
                            "model_type_from_source_training":"ORDERED_TIME"},
                    "TRANSFER":{"exact_source_answers":201,
                                "incorrect_confident_answers":30,
                                "explicit_abstentions":19,
                                "independently_authored_test_questions":250,
                                "weak_fixed_answer_baseline_exact":20,
                                "model_type_from_source_training":"TRIADIC_TRANSFER"},
                },
                "external_source_failed_or_abstained_examples":[{
                    "family":"TIME","source_id":"TIME-test-1-4","question":"Where was Mary?",
                    "source_gold":"garden","model_answer":None,"model_status":"HOLD","reason":"UNKNOWN"}],
                "source_training_boolean_projection_impossibilities":[],
                "fictional_duty_source_proofs":[{
                    "source_case_id":"D02_PRIOR_PROMISE","state":"HOLD_PRIOR_DUTIES",
                    "reason":"DIRECTED_COMMITMENTS_EXCEED_FIXED_CAPACITY",
                    "relevant_deadlines":[],"prior_directed_duty_units":3,
                    "capacity_units":4,"requested_units":3,"new_request_deadline":15,
                    "current_hour":12,"production_capacity_per_hour":2,
                }],
                "actual_original_019_elf_receipts":[{
                    "source_case":"D02_PRIOR_PROMISE",
                    "critic_eligible_for_read_only_discussion":False,
                }],
            }
            src.write_text(json.dumps(data),encoding="utf8")
            result=build(src,dest)
            html=dest.read_text(encoding="utf8")
            self.assertEqual(result["real_external_benchmark_questions"],750)
            self.assertTrue(result["external_requests"] is False)
            self.assertIn('class="left"',html)
            self.assertIn('class="right"',html)
            self.assertIn('id="family"',html)
            self.assertIn("D02_PRIOR_PROMISE",html)
            self.assertIn("incorrect_confident_answers",html)
            self.assertNotIn('<script src="http',html)

    def test_viewer_cannot_publish_execution_enabled_claims(self):
        with TemporaryDirectory() as tmp:
            src=Path(tmp)/"fail.json"
            src.write_text(json.dumps({
                "schema":"motif.reason022.unimagined-distinction.benchmark.v1",
                "test_questions":750,"fictional_obligation_cases":7,
                "external_actions":True,"permission_to_execute":False,
            }),encoding="utf8")
            with self.assertRaises(ValueError):
                build(src,Path(tmp)/"out.html")


if __name__=="__main__":
    unittest.main()
