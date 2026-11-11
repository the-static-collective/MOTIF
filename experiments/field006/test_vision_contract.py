import json, unittest
from pathlib import Path
from atlas import from_dict
from vision_contract import review_model_packet,next_evidence_actions
FIXTURE=Path(__file__).parent/'fixtures/public_example.json'

class Tests(unittest.TestCase):
 def setUp(self):self.atlas=from_dict(json.loads(FIXTURE.read_text()))
 def test_empty(self):self.assertEqual(review_model_packet(self.atlas,{}).accepted_traces,())
 def test_accept_sketch_tentative(self):
  p={'candidate_traces':[{'source':'paper','kind':'DESIRED','points':[[0.1,.2],[.9,.2]],'status':'TENTATIVE','note':'maybe'}]}
  self.assertEqual(len(review_model_packet(self.atlas,p).accepted_traces),1)
 def test_original_not_modified(self):
  p={'candidate_traces':[{'source':'paper','kind':'DESIRED','points':[[0.1,.2],[.9,.2]],'status':'TENTATIVE'}]}
  before=len(self.atlas.traces);review_model_packet(self.atlas,p);self.assertEqual(len(self.atlas.traces),before)
 def test_photo_trace_refused(self):
  p={'candidate_traces':[{'source':'photo-a','kind':'DESIRED','points':[[0.1,.2],[.9,.2]],'status':'TENTATIVE'}]}
  self.assertEqual(len(review_model_packet(self.atlas,p).held),1)
 def test_model_own_claim_untrusted(self):
  p={'candidate_traces':[{'source':'paper','kind':'DESIRED','points':[[0.1,.2],[.9,.2]],'status':'USER_STATED'}]}
  self.assertEqual(len(review_model_packet(self.atlas,p).accepted_traces),0)
 def test_invalid_trace(self):
  p={'candidate_traces':[{'source':'paper','kind':'DESIRED','points':[[0.9,.2]],'status':'TENTATIVE'}]}
  self.assertEqual(len(review_model_packet(self.atlas,p).accepted_traces),0)
 def test_photo_to_map_rejected(self):
  p={'candidate_landmarks':[{'label':'New rack','source':'photo-a','sketch_xy':[.2,.3],'status':'TENTATIVE'}]}
  self.assertIn('NO_PHOTO_TO_WORLD_COORDINATES',review_model_packet(self.atlas,p).held[0])
 def test_photo_unplaced_accepted(self):
  p={'candidate_landmarks':[{'label':'New rack','source':'photo-a','status':'TENTATIVE'}]}
  self.assertEqual(review_model_packet(self.atlas,p).candidate_labels,(('photo-a','New rack'),))
 def test_sketch_landmark_possible(self):
  p={'candidate_landmarks':[{'label':'New rack','source':'paper','sketch_xy':[.3,.4],'status':'TENTATIVE'}]}
  self.assertEqual(len(review_model_packet(self.atlas,p).candidate_labels),1)
 def test_duplicate_sketch_label_held(self):
  p={'candidate_landmarks':[{'label':'entry','source':'paper','sketch_xy':[.3,.4],'status':'TENTATIVE'}]}
  self.assertEqual(len(review_model_packet(self.atlas,p).held),1)
 def test_user_intent_trace_not_looked_for_if_present(self):
  self.assertNotIn('TRACE_INTENDED_BOUNDARY',[x['id'] for x in next_evidence_actions(self.atlas)])
 def test_unknowns_ask_relevant_physical_probe(self):
  self.assertTrue(any('HAZARD_REVIEW'==x['id'] for x in next_evidence_actions(self.atlas)))
 def test_no_external_actions(self):self.assertTrue(all(not x['physical_work'] for x in next_evidence_actions(self.atlas)))
 def test_user_photo_actions(self):
  data=json.loads(FIXTURE.read_text());data['sources'][1]['kind']='USER_PHOTO'
  self.assertIn('LINK_MULTI_VIEW_WITNESSES',[x['id'] for x in next_evidence_actions(from_dict(data))])
 def test_unexpected_keys_rejected(self):
  with self.assertRaises(ValueError):review_model_packet(self.atlas,{'arbitrary_code':'run'})
if __name__=='__main__':unittest.main()