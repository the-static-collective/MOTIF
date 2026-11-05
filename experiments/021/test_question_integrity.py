import importlib.util
import unittest
from pathlib import Path
from copy import deepcopy

spec=importlib.util.spec_from_file_location("motif021",Path(__file__).with_name("question_integrity.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ProtocolIntegrity(unittest.TestCase):
 def setUp(self):
  self.receipts=m.load()
  self.report=m.inspect(self.receipts)

 def test_genuine_public_query_encoding_error_and_corrected_result(self):
  self.assertEqual(self.report["schema"],"motif.question-integrity-and-physical-work/v1")
  a=self.report["observations"]
  self.assertEqual(a["first_date_only_interval"]["qualified_fresh_source_count"],0)
  self.assertEqual(a["corrected_full_UTC_interval"]["qualified_fresh_source_count"],3)
  self.assertEqual(a["actual_stop_when_first_fresh"]["requests_actually_sent"],1)
  self.assertTrue(self.report["learning"]["protocol_error_detected"])
  self.assertFalse(self.report["measured_resource_units"]["causal_network_cost_savings_PROVED"])
  self.assertIsNone(self.report["measured_resource_units"]["electrical_energy_joules"])
  self.assertFalse(self.report["automatic_promotion"])
  self.assertFalse(self.report["environmental_warning"])

 def test_forged_freshness_and_electricity_cannot_pass(self):
  for modify in [
   lambda x:x["initial"]["actual_network_activity"].update(fresh_public_source_count=3),
   lambda x:x["corrected"]["actual_network_activity"].update(fresh_public_source_count=0),
   lambda x:x["conditional"].update(requests_sent=3),
   lambda x:x["conditional"].update(electrical_energy_joules=0),
   lambda x:x["conditional"].update(automatic_model_promotion=True),
   lambda x:x["conditional"]["witness"].update(reported_discharge_cfs=-2)
  ]:
   f=deepcopy(self.receipts);modify(f)
   with self.assertRaises(m.HOLD):
    m.inspect(f)

 def test_source_byte_integrity_and_readonly_limits(self):
  for filename,expected in m.FILES.values():
   b=(m.EVIDENCE/filename).read_bytes()
   self.assertEqual(m.digest(b),expected)
  self.assertFalse(self.report["learning"]["autonomous_model_weight_update"])
  self.assertTrue(self.report["measured_resource_units"]["resource_comparison_is_NONCONTEMPORANEOUS"])

if __name__=="__main__":unittest.main()
