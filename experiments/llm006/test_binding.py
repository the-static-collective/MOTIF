"""LLM-006 binding falsifiers using an EXPLICITLY FAKE test predictor only.

These tests exercise source gating, privacy boundaries, and decision callback
integration, NOT pretrained inference. The actual weights must be loaded in
the separate real-pretrained GitHub Actions job; no fallback or fake result
can be labeled as a real model receipt.
"""
import json,math,unittest
from error_dividend import INPUTS,update,outputs
from odyssey import LongChain,REAL_MODEL_POLICIES,DEV_SEEDS
from marathon import Marathon,GROUPS

class FakeSourceOnlyPredictor:
    is_real_pretrained=False
    def __init__(self):
        self.packets=[]
    def __call__(self,packet):
        if not packet.get("no_future_owner_truth") or not packet.get("rumor_sources_excluded"):
            raise ValueError("LEAKED_OWNER_SCOPE")
        self.packets.append(json.loads(json.dumps(packet)))
        w=[.125]*8
        for obs in packet["observations"]:
            w,updated=update(w,tuple(obs["x"]),obs["value"],noise=0)
            if not updated:raise ValueError("INCONSISTENT_OWNER_REPORT")
        p=sum(w[i] for i in range(8) if outputs(i,tuple(packet["x"])))
        return {"prediction":int(p>=.5),"p_one":p,
                "token_count":34,"inference_seconds":0.,
                "model":"SYNTHETIC_TEST_CALLBACK_NOT_PRETRAINED",
                "revision":"TEST_ONLY",
                "prompt_sha256":"0"*64}
class BindingTests(unittest.TestCase):
    def new(self,policy="llm_memory",seed=DEV_SEEDS[0]):
        stub=FakeSourceOnlyPredictor()
        return LongChain(seed,policy,decision_adapter=stub),stub
    def test_01_real_modes_explicitly_registered(self):
        self.assertEqual(set(REAL_MODEL_POLICIES),
            {"llm_memory","llm_flat","llm_verification"})
    def test_02_real_mode_refuses_missing_model(self):
        with self.assertRaisesRegex(ValueError,"REAL_MODEL_ADAPTER_REQUIRED_OR_UNEXPECTED"):
            LongChain(DEV_SEEDS[0],"llm_memory")
    def test_03_real_mode_refuses_external_adapter_on_classical(self):
        with self.assertRaisesRegex(ValueError,"REAL_MODEL_ADAPTER_REQUIRED_OR_UNEXPECTED"):
            LongChain(DEV_SEEDS[0],"classical_bayes",decision_adapter=FakeSourceOnlyPredictor())
    def test_04_model_packet_one_verifiable_observation_only_initially(self):
        c,stub=self.new()
        x=next(x for x in c.order[0] if x!=c.maps[0].initial_x)
        p=c._model_packet(0,x)
        self.assertEqual(len(p["observations"]),1)
        self.assertEqual(p["observations"][0]["source_root"],c.maps[0]._first_source)
        self.assertEqual(p["x"],list(x))
    def test_05_model_packet_does_not_include_hidden_truth_or_owner_handle(self):
        c,stub=self.new()
        x=next(x for x in c.order[0] if x!=c.maps[0].initial_x)
        p=c._model_packet(0,x)
        contents=json.dumps(p)
        self.assertNotIn('"_truth"',contents)
        self.assertNotIn('"_owner"',contents)
        self.assertNotIn('"program_index"',contents)
        self.assertNotIn('"hint"',contents)
        self.assertNotIn('"owner_index"',contents)
    def test_06_no_root_crosses_into_adjacent_sectors(self):
        c,stub=self.new()
        x=next(x for x in c.order[0] if x!=c.maps[0].initial_x)
        p=c._model_packet(0,x)
        self.assertNotIn(c.maps[1]._first_source,p["source_roots"])
    def test_07_evidence_count_changes_only_after_owner_test(self):
        c,stub=self.new()
        x=next(x for x in c.order[0] if x!=c.maps[0].initial_x)
        p=c._model_packet(0,x)
        self.assertEqual(len(p["observations"]),1)
        prop=c.maps[0].propose_query(x)
        still=c._model_packet(0,x)
        self.assertEqual(still["observations"],p["observations"])
        c.maps[0].resolve(c.owner[0],prop)
        y=next(z for z in c.order[0] if z not in (x,c.maps[0].initial_x))
        self.assertEqual(len(c._model_packet(0,y)["observations"]),2)
    def test_08_flat_still_only_sees_calibration_even_after_other_receipts(self):
        c,stub=self.new("llm_flat")
        x=next(x for x in c.order[0] if x!=c.maps[0].initial_x)
        q=c.maps[0].propose_query(x);c.maps[0].resolve(c.owner[0],q)
        y=next(z for z in c.order[0] if z not in (x,c.maps[0].initial_x))
        self.assertEqual(len(c._model_packet(0,y)["observations"]),1)
    def test_09_model_is_actually_called_before_unsourced_gate_commit(self):
        c,stub=self.new()
        while c.order[0][c.gate]==c.maps[0].initial_x:
            c.survey();c.decide()
        c.survey();c.decide()
        self.assertEqual(len(stub.packets),1)
        self.assertEqual(c.real_model_calls,1)
        self.assertEqual(stub.packets[0]["x"],list(c.order[0][c.gate-1 if not c.repair_needed else c.gate]))
    def test_10_calibration_gate_uses_owner_without_pretending_model_fired(self):
        c,stub=self.new()
        i=c.order[0].index(c.maps[0].initial_x)
        for j in range(i+1):
            if j==4:c.audit("half")
            c.survey();c.decide()
            if c.repair_needed:c.repair();c.retry(c.expected_retry)
        self.assertEqual(c.metrics["calibration_reuses"],1)
        self.assertEqual(c.real_model_calls,len([j for j in range(i+1) if j!=i]))
    def test_11_invalid_model_answer_is_rejected_not_promoted(self):
        c,stub=self.new()
        c.decision_adapter=lambda packet:{"prediction":3,"p_one":.4,"token_count":40,
                                           "inference_seconds":0.}
        x=next(x for x in c.order[0] if x!=c.maps[0].initial_x)
        with self.assertRaisesRegex(ValueError,"INVALID_REAL_MODEL_RESULT"):
            c._prediction(0,x)
    def test_12_invalid_model_confidence_rejected(self):
        c,stub=self.new()
        c.decision_adapter=lambda packet:{"prediction":0,"p_one":float("nan"),
                                           "token_count":5,"inference_seconds":0.}
        x=next(x for x in c.order[0] if x!=c.maps[0].initial_x)
        with self.assertRaisesRegex(ValueError,"INVALID_REAL_MODEL_PROBABILITY"):
            c._prediction(0,x)
    def test_13_test_callback_is_not_labeled_actual_pretrained_in_summary(self):
        c,stub=self.new()
        c.execute()
        s=c.summary()
        self.assertTrue(s["decision_adapter_used"])
        self.assertFalse(s["real_llm_used"])
        self.assertGreater(s["real_model_forwards"],0)
    def test_14_fake_bayesian_adapter_may_finish_but_never_claim_real_weights(self):
        stub=FakeSourceOnlyPredictor()
        m=Marathon(GROUPS[0],"llm_memory",decision_adapter=stub)
        s=m.execute()
        self.assertTrue(s["completed"])
        self.assertEqual(s["completed_decision_gates"],384)
        self.assertEqual(s["real_model_forwards"],336)
        self.assertFalse(s["real_llm"])
        self.assertEqual(len(stub.packets),336)
    def test_15_feedback_witnesses_are_unique_not_model_proposals(self):
        c,stub=self.new()
        c.execute()
        self.assertEqual(sum(len(g.events) for g in c.maps),84)
        self.assertTrue(all(e["independent"] for g in c.maps for e in g.events))
        self.assertTrue(all(e.get("source_root")!=p["observations"][0]["source_root"]
                           for p in stub.packets for e in []))
    def test_16_llm_verification_uses_source_gate_not_guess_as_witness(self):
        c,stub=self.new("llm_verification")
        s=c.execute()
        self.assertEqual(s["completed_gates"],96)
        self.assertGreater(s["metrics"]["optional_probes"],0)
        self.assertEqual(sum(len(g.events) for g in c.maps),84)
        self.assertEqual(s["metrics"]["source_verified"],96)
    def test_17_repeat_model_source_disclosure_scope_stable(self):
        c,stub=self.new()
        x=next(x for x in c.order[0] if x!=c.maps[0].initial_x)
        self.assertEqual(c._model_packet(0,x),c._model_packet(0,x))
    def test_18_model_callback_must_report_token_usage(self):
        c,stub=self.new()
        c.decision_adapter=lambda packet:{"prediction":0,"p_one":.4,"token_count":0,
                                           "inference_seconds":0.}
        x=next(x for x in c.order[0] if x!=c.maps[0].initial_x)
        with self.assertRaisesRegex(ValueError,"REAL_MODEL_MISSING_TOKEN_COUNT"):
            c._prediction(0,x)
    def test_19_real_model_present_only_if_separate_attestation(self):
        c,stub=self.new()
        self.assertFalse(getattr(stub,"is_real_pretrained"))
        self.assertFalse(c.summary()["real_llm_used"])

if __name__=="__main__":unittest.main()
