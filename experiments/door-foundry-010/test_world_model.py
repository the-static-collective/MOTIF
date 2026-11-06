"""MOTIF-010: source, evidence, independent Bayes, decision and tampering tests."""
import json,os,shutil,tempfile,unittest
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import world_model as model

class WorldModels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=Path(os.environ["MOTIF009_QUESTION_DIR"])
        cls.tmp=tempfile.TemporaryDirectory(prefix="motif010-")
        cls.root=Path(cls.tmp.name)
        cls.summary=model.compare_all(cls.original,cls.root/"benchmark")
        cls.first=model.read(cls.root/"benchmark"/"LEFT_PARTIAL"/"replay.json")
        cls.worlds=[{"id":k,"side":k.split("_")[0].lower(),
           "wall_extent":k.split("_")[1].lower()} for k in model.WORLD_IDS]
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_all_four_original_real_png_models_retained(self):
        original,worlds=model.verify_original(self.original)
        self.assertEqual(len(worlds),4)
        self.assertEqual(len({w["start_png_sha256"] for w in worlds}),4)
        self.assertFalse(original["custody"]["current_world_identified"])

    def test_first_observation_contract_is_strictly_simulated(self):
        e=model.make_event(1,"wall_extent","partial")
        self.assertEqual(model.verify_event(e,1),Fraction(9,10))
        self.assertFalse(e["real_human_answer"])
        self.assertFalse(e["physical_observation"])
        self.assertEqual(e["source"],model.READ_ONLY)

    def test_source_world_prior_is_not_overwritten(self):
        self.assertEqual(model.typed_weights(self.first["initial_prior"]),model.PRIORS)
        self.assertNotEqual(model.typed_weights(self.first["posterior"]),model.PRIORS)
        self.assertEqual(model.PRIORS["LEFT_PARTIAL"],Fraction(1,10))

    def test_correct_synthetic_evidence_concentrates_but_never_makes_certainty(self):
        p=model.typed_weights(self.first["posterior"])
        self.assertGreater(p["LEFT_PARTIAL"],Fraction(4,5))
        self.assertLess(p["LEFT_PARTIAL"],Fraction(1))
        self.assertEqual(sum(p.values()),1)
        self.assertTrue(all(x>0 for x in p.values()))

    def test_update_agrees_exactly_with_independent_likelihood_product(self):
        used=[]
        for i,e in enumerate(self.first["history"],1):
            model.verify_event(e["evidence"],i)
            used.append(e["evidence"])
            truth=model.independent_batch_posterior(model.PRIORS,self.worlds,used)
            self.assertEqual(model.typed_weights(e["posterior"]),truth)

    def test_append_only_hash_receipts_preserve_contradictions(self):
        prior=self.first["original_009_question_receipt_sha256"]
        for i,r in enumerate(self.first["history"],1):
            self.assertEqual(r["sequence"],i)
            self.assertEqual(r["previous_receipt_sha256"],prior)
            body=dict(r);prior=body.pop("content_sha256")
            self.assertEqual(model.digest(body),prior)
            self.assertTrue(r["contradictory_evidence_never_erased"])
        self.assertEqual(prior,self.first["last_chain_sha256"])

    def test_each_evidence_update_reoptimizes_which_question_to_ask_next(self):
        for row in self.first["history"]:
            new=model.typed_weights(row["posterior"])
            score,policy=model.classical.optimal(
                self.worlds,new,model.classical.standard_costs(),2)
            self.assertEqual(policy,row["next_question_policy"])
            self.assertAlmostEqual(float(score),row["next_question_expected_loss"])
            self.assertEqual(policy.get("question_id"),
                             row["next_question_proposed_but_unsent"])

    def test_synthetic_out_of_sample_forecasts_improve_over_frozen_prior(self):
        r=self.summary
        self.assertEqual(len(r["four_synthetic_cases"]),4)
        self.assertAlmostEqual(r["frozen_mean_brier"],.25)
        self.assertAlmostEqual(r["updated_mean_brier"],.0324)
        self.assertLess(r["updated_mean_log_loss"],r["frozen_mean_log_loss"])
        self.assertTrue(r["designed_perfect_agreement_sensor_fixtures"])

    def test_fixture_decisions_have_lower_regret_not_real_actions(self):
        self.assertEqual(self.summary["frozen_mean_decision_regret"],2.5)
        self.assertEqual(self.summary["updated_mean_decision_regret"],0)
        self.assertEqual(self.first["custody"]["actual_actions"],0)
        self.assertFalse(self.summary["results_do_not_prove_generalization"] is False)

    def test_heldout_observation_not_assimilated(self):
        used=[r["evidence"] for r in self.first["history"]]
        posterior=model.independent_batch_posterior(model.PRIORS,self.worlds,used)
        self.assertEqual(posterior,model.typed_weights(self.first["posterior"]))
        self.assertFalse(self.first["heldout_used_for_training"])
        self.assertEqual(self.first["heldout_event"]["event_id"],"SIM-004")

    def test_noisy_conflicting_observations_are_not_deleted_or_forced_to_zero(self):
        a=model.make_event(1,"wall_extent","full")
        b=model.make_event(2,"wall_extent","partial")
        moved=model.increment(model.PRIORS,self.worlds,a)
        restored=model.increment(moved,self.worlds,b)
        self.assertLess(moved["LEFT_PARTIAL"],model.PRIORS["LEFT_PARTIAL"])
        self.assertEqual(restored,model.PRIORS)
        self.assertNotEqual(a["content_sha256"],b["content_sha256"])

    def test_untrusted_source_even_if_self_rehashed_cannot_claim_human_evidence(self):
        e=model.make_event(1,"side","left")
        e["source"]="EXTERNAL_CERTIFIED_OBSERVATION"
        b=dict(e);b.pop("content_sha256")
        e["content_sha256"]=model.digest(b)
        with self.assertRaises(model.HOLD):model.verify_event(e,1)

    def test_forged_observed_human_answer_is_refused(self):
        e=model.make_event(1,"side","left")
        e["real_human_answer"]=True
        b=dict(e);b.pop("content_sha256")
        e["content_sha256"]=model.digest(b)
        with self.assertRaises(model.HOLD):model.verify_event(e,1)

    def test_sensor_likelihood_requires_bounded_normalized_rational(self):
        for bad in ["1","0","1/2","9/09","nan"]:
            with self.subTest(value=bad),self.assertRaises(model.HOLD):
                model.make_event(1,"side","left",bad)

    def test_unknown_observation_schema_not_invented(self):
        with self.assertRaises(model.HOLD):
            model.make_event(1,"person_identity","Alice")
        with self.assertRaises(model.HOLD):
            model.make_event(1,"side","yellow")
        with self.assertRaises(model.HOLD):
            model.make_event(True,"side","left")

    def test_replay_does_not_accept_duplicate_or_out_of_order_evidence(self):
        bad=[model.make_event(1,"side","left"),
             model.make_event(1,"side","left")]
        target=self.root/"bad-events"
        with self.assertRaises(model.HOLD):
            model.single_replay(self.original,"LEFT_PARTIAL",target,events=bad)
        self.assertFalse(target.exists())

    def test_source_packet_false_prior_rejected_even_when_rehashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"scenes"
            shutil.copytree(self.original,folder)
            f=folder/"active-question.json"
            p=json.loads(f.read_text())
            p["analysis"]["cost_model"]["prior_probability"]["LEFT_PARTIAL"]=.25
            b=dict(p);b.pop("content_sha256")
            p["content_sha256"]=model.digest(b)
            f.write_text(json.dumps(p))
            with self.assertRaises(model.HOLD):model.verify_original(folder)

    def test_png_swap_refused_without_accepting_merely_changed_text_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"scenes"
            shutil.copytree(self.original,folder)
            p=folder/"worlds"/"LEFT_PARTIAL"/"start.png"
            p.write_bytes(p.read_bytes()+b"forgery")
            with self.assertRaises(model.HOLD):model.verify_original(folder)

    def test_exact_source_belief_information_is_kept_read_only(self):
        self.assertTrue(self.first["assumptions"]["priors_not_measured_in_the_field"])
        self.assertTrue(self.first["assumptions"]["out_of_support_worlds_not_considered"])
        self.assertTrue(self.first["assumptions"]["authored_sensor_reliability_not_calibrated"])
        self.assertFalse(self.first["custody"]["real_scene_identified"])

    def test_benchmark_does_not_overclaim_superiority_to_matched_classical_bayes(self):
        self.assertTrue(self.summary["fair_classical_Bayes_matches_exactly"])
        self.assertTrue(self.summary["results_do_not_prove_generalization"])
        self.assertTrue(self.summary["reality_was_not_observed"])
        self.assertEqual(self.summary["real_effects"],0)

    def test_prior_already_well_informed_may_not_need_another_question(self):
        posterior=model.typed_weights(self.first["posterior"])
        result=model.classical.analyze(self.worlds,posterior,
                                       model.classical.standard_costs())
        self.assertFalse(result["query_dispatched"])
        self.assertFalse(result["actual_hypothesis_identified"])

    def test_source_evidence_and_benchmark_records_hash_exactly(self):
        for r in (self.first,self.summary):
            body=dict(r);claimed=body.pop("content_sha256")
            self.assertEqual(model.digest(body),claimed)

    def test_outputs_are_append_only_no_silent_overwrites(self):
        with self.assertRaises(model.HOLD):
            model.compare_all(self.original,self.root/"benchmark")
        with self.assertRaises(model.HOLD):
            model.single_replay(self.original,"LEFT_PARTIAL",
              self.root/"benchmark"/"LEFT_PARTIAL")

if __name__=="__main__":unittest.main()
