import copy
import unittest
from pathlib import Path
import importlib.util

spec=importlib.util.spec_from_file_location("motif020",
    Path(__file__).with_name("ghot_resource_bridge.py"))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class GhotBridgeTest(unittest.TestCase):
    def setUp(self):
        self.receipt=m.read_pinned()
        self.result=m.inspect(self.receipt)
    def test_real_source_pinned_computation_not_imaginary_credits(self):
        self.assertEqual(self.result["schema"],"motif.embodied-question/v1")
        self.assertEqual(self.result["measured_work"]["reparse_median_cpu_ns"],100424701)
        self.assertEqual(self.result["measured_work"]["reuse_median_cpu_ns"],28376628)
        self.assertEqual(self.result["measured_work"]["median_cpu_ns_reduction_per_batch"],72048073)
        self.assertEqual(self.result["measured_work"]["actual_source_bytes_read_per_batch"],2426750)
        self.assertEqual(self.result["measured_work"]["bytes_read_saved"],0)
        self.assertEqual(self.result["measured_work"]["json_validations_reuse"],1)
        self.assertIsNone(self.result["measured_work"]["electrical_energy_joules"])
        self.assertFalse(self.result["independent_Joules_verified"])
        self.assertFalse(self.result["automatic_promotion"])
        self.assertTrue(self.result["identical_evidence_derived_answer"])
        self.assertIn("freshness",str(self.result["next_question"]))

    def test_no_fabricated_power_or_execution(self):
        self.assertEqual(self.result["GHOT_scheduler_hypothetical_action"],"run_here")
        self.assertFalse(self.result["GHOT_actual_execution"])
        self.assertFalse(self.result["remote_execution"])
        self.assertFalse(self.result["authority"])

    def test_corrupted_source_or_score_rejected(self):
        for mutation in [
            lambda r:r["source"].update(source_kind="invented"),
            lambda r:r["resource_accounting"].update(real_energy_joules_measured=True),
            lambda r:r["power"].update(real_task_dispatched=True),
            lambda r:r["benchmark"].update(all_answers_bitwise_equal=False),
            lambda r:r["benchmark"]["observed"].update(cpu_time_delta_ns_reparse_minus_reuse=-1),
            lambda r:r["benchmark"]["raw_trials"][0].update(cpu_time_ns=100),
            lambda r:r["benchmark"]["raw_trials"][0].update(json_validation_parses=0),
        ]:
            bad=copy.deepcopy(self.receipt)
            mutation(bad)
            with self.assertRaises(m.HOLD):
                m.inspect(bad)

    def test_checksum_uses_git_blob_identity_not_filename(self):
        p=m.SOURCE
        self.assertEqual(m.githash(p.read_bytes()),m.GHOT_GIT_BLOB)
        self.assertNotEqual(m.githash(p.read_bytes()+b"\n"),m.GHOT_GIT_BLOB)

if __name__=="__main__":unittest.main()
