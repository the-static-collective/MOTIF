"""MOTIF-011: precise falsifiers for model inadequacy and safe abstention."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import inspect
import json
import sys
import unittest

# Import the local evaluator/oracle FIRST; inherited modules modify sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "008"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "009"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "010"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle
import benchmark
import skeptic
from scientist import candidate_cartridges
from cartridge import validate_cartridge


class SkepticalScientistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds={x:oracle.make_world(x,11) for x in oracle.FAMILIES}
        cls.train={x:oracle.episodes(w,"train") for x,w in cls.worlds.items()}
        cls.val={x:oracle.episodes(w,"validation")
                 for x,w in cls.worlds.items()}
        cls.assessments={
            x:skeptic.assess(cls.train[x],cls.val[x],w.controls)
            for x,w in cls.worlds.items()}

    def test_training_and_independent_splits_never_share_entity_ids(self):
        for family,w in self.worlds.items():
            groups=[oracle.episodes(w,part) for part in oracle.SPLITS]
            self.assertEqual([len(x) for x in groups],[16]*4)
            ids=[{r.roles for r in rows} for rows in groups]
            for i in range(len(ids)):
                for j in range(i+1,len(ids)):
                    self.assertFalse(ids[i] & ids[j])

    def test_world_names_are_opaque_and_separate(self):
        names=[w.controls.first_port for w in self.worlds.values()]
        names += [w.controls.second_port for w in self.worlds.values()]
        self.assertEqual(len(names),len(set(names)))
        self.assertTrue(all(q.startswith("q") for q in names))

    def test_learner_never_imports_private_oracle(self):
        source=inspect.getsource(skeptic)
        self.assertNotIn("import oracle",source)
        self.assertNotIn("from oracle import",source)
        self.assertNotIn("spec.family",source)
        self.assertNotIn("hidden_third",source)

    def test_clean_two_control_world_is_supported(self):
        value=self.assessments["clean_two"]
        self.assertEqual(value.status,"TWO_PORT_CONSISTENT")
        self.assertFalse(value.contradictions)
        self.assertIsNotNone(value.accepted_two_port)
        w=self.worlds["clean_two"]
        for record in oracle.episodes(w,"test"):
            self.assertEqual(value.predict_two_port(record,w.controls),
                             skeptic.validated_result(record))

    def test_restricted_clean_world_still_supports_passive_predictions(self):
        self.assertEqual(self.assessments["restricted_clean"].status,
                         "TWO_PORT_CONSISTENT")

    def test_visible_missing_concept_is_discovered_not_named(self):
        a=self.assessments["visible_third"]
        self.assertEqual(a.status,"PROPOSE_EXTENSION")
        self.assertEqual(a.extension_candidates,1)
        self.assertEqual(len(a.contradictions),4)
        self.assertEqual(a.extension.relation,
                         self.worlds["visible_third"].third_relation)
        self.assertEqual(a.extension.role_index,0)
        self.assertNotIn("third",a.extension.relation)
        self.assertEqual(a.extension.source_count,16)
        self.assertEqual(a.extension.validation_count,16)

    def test_extension_is_two_real_009_trees_plus_an_anonymous_router(self):
        ext=self.assessments["visible_third"].extension
        self.assertNotEqual(ext.when_absent.id,ext.when_present.id)
        self.assertEqual(ext.when_absent.leaves,(False,True,True,False))
        self.assertEqual(ext.when_present.leaves,(True,False,False,True))
        self.assertTrue(ext.when_absent.id.startswith("tree-"))
        self.assertTrue(ext.when_present.id.startswith("tree-"))

    def test_proposed_concept_is_held_not_automatically_admitted(self):
        bay=skeptic.LocalConceptBay()
        ident=bay.offer(self.assessments["visible_third"])
        self.assertNotIn(ident,bay.admitted)
        w=self.worlds["visible_third"]
        with self.assertRaisesRegex(skeptic.HOLD,"not locally admitted"):
            bay.predict(ident,oracle.episodes(w,"test")[0],w.controls)

    def test_new_router_roundtrips_as_portable_prediction_cartridge(self):
        ext=self.assessments["visible_third"].extension
        raw=skeptic.export_extension(ext)
        self.assertEqual(skeptic.decode_extension(raw),ext)
        self.assertNotIn("11_train_",raw)
        self.assertNotIn("11_validation_",raw)
        packet=json.loads(raw)
        self.assertEqual(packet["schema"],"motif.derived-router.v0")
        self.assertEqual(packet["status"],"PROPOSED_NOT_ADMITTED")
        self.assertTrue(packet["absent_tree"]["id"].startswith("tree-"))
        self.assertTrue(packet["present_tree"]["id"].startswith("tree-"))
        self.assertNotIn("auth_signature",packet)

    def test_checksum_tamper_is_held_and_rehash_is_not_authentication(self):
        raw=skeptic.export_extension(
            self.assessments["visible_third"].extension)
        tampered=raw.replace("PROPOSED_NOT_ADMITTED","ADMIT_PLAN_AND_ACT")
        with self.assertRaises(skeptic.HOLD):
            skeptic.decode_extension(tampered)
        content=json.loads(raw)
        content["unreviewed_extra_command"]="EXECUTE"
        content["checksum_sha256"]=skeptic.checksum({
            k:v for k,v in content.items() if k!="checksum_sha256"})
        with self.assertRaisesRegex(skeptic.HOLD,"fields"):
            skeptic.decode_extension(json.dumps(content))

    def test_local_review_requires_new_evidence_and_does_not_use_test(self):
        w=self.worlds["visible_third"]
        raw=skeptic.export_extension(
            self.assessments["visible_third"].extension)
        bay=skeptic.LocalConceptBay()
        ident=bay.offer_packet(raw)
        local=oracle.episodes(w,"local_review")
        with self.assertRaises(skeptic.HOLD):
            bay.review(ident,"ADMIT_PREDICT_ONLY","LOCAL",
                       local[:4],w.controls)
        receipt=bay.review(ident,"ADMIT_PREDICT_ONLY","LOCAL",
                           local,w.controls)
        self.assertFalse(receipt.heldout_information_used)
        self.assertEqual(receipt.decision,"ADMIT_PREDICT_ONLY")
        self.assertEqual(receipt.local_examples,16)
        self.assertIn(ident,bay.admitted)
        for case in oracle.episodes(w,"test"):
            self.assertEqual(bay.predict(ident,case,w.controls),
                             skeptic.validated_result(case))

    def test_local_refusal_cannot_be_used(self):
        bay=skeptic.LocalConceptBay()
        ident=bay.offer(self.assessments["visible_third"])
        bay.review(ident,"REFUSE","LOCAL")
        w=self.worlds["visible_third"]
        with self.assertRaises(skeptic.HOLD):
            bay.predict(ident,oracle.episodes(w,"test")[0],w.controls)

    def test_local_false_review_evidence_blocks_admission(self):
        bay=skeptic.LocalConceptBay()
        ident=bay.offer(self.assessments["visible_third"])
        w=self.worlds["visible_third"]
        local=list(oracle.episodes(w,"local_review"))
        sample=local[0]
        if skeptic.validated_result(sample):
            local[0]=replace(sample,observed_after=sample.before)
        else:
            a,t=sample.roles
            local[0]=replace(sample,observed_after=frozenset(
                 (sample.before-{("pending",t)})|{("achieved",t)}))
        with self.assertRaisesRegex(skeptic.HOLD,"Independent review fails"):
            bay.review(ident,"ADMIT_PREDICT_ONLY","LOCAL",local,w.controls)
        self.assertNotIn(ident,bay.admitted)

    def test_mismatched_control_vocabulary_blocks_prediction(self):
        w=self.worlds["visible_third"]
        a=self.assessments["visible_third"].extension
        wrong=self.worlds["hidden_third"].controls
        with self.assertRaisesRegex(skeptic.HOLD,"Unreviewed control"):
            a.predict(oracle.episodes(w,"test")[0],wrong)

    def test_new_undefined_relation_blocks_local_prediction(self):
        w=self.worlds["visible_third"]
        a=self.assessments["visible_third"].extension
        r=oracle.episodes(w,"test")[0]
        altered=replace(r,before=r.before|{("unknown_predicate",r.roles[0])})
        with self.assertRaisesRegex(skeptic.HOLD,"Unreviewed predicate"):
            a.predict(altered,w.controls)

    def test_heldout_validation_contradiction_rejects_extension(self):
        w=self.worlds["visible_third"]
        val=list(self.val["visible_third"])
        x=val[0]
        _,target=x.roles
        observed=skeptic.validated_result(x)
        wrong=(x.before if observed else frozenset(
              (x.before-{("pending",target)})|{("achieved",target)}))
        val[0]=replace(x,observed_after=wrong)
        altered=skeptic.assess(self.train["visible_third"],val,w.controls)
        self.assertEqual(altered.status,"ABSTAIN_INADEQUATE")

    def test_true_hidden_third_cause_is_not_invented(self):
        a=self.assessments["hidden_third"]
        self.assertEqual(a.status,"ABSTAIN_INADEQUATE")
        self.assertEqual(len(a.contradictions),4)
        self.assertIsNone(a.extension)
        self.assertEqual(a.extension_candidates,0)

    def test_noise_flip_is_empirically_indistinguishable_from_hidden_cause(self):
        a=self.assessments["hidden_third"]
        b=self.assessments["noisy_flip"]
        self.assertEqual(a.status,b.status)
        self.assertEqual(tuple(x.observed_outcomes for x in a.contradictions),
                         tuple(x.observed_outcomes for x in b.contradictions))
        # A failed model family is NOT proof that the explanation is noise.
        self.assertIsNone(b.accepted_two_port)
        self.assertIsNone(b.extension)

    def test_perfect_proxy_confounding_causes_abstention(self):
        a=self.assessments["ambiguous_proxy"]
        self.assertEqual(a.status,"ABSTAIN_AMBIGUOUS")
        self.assertEqual(a.extension_candidates,2)
        self.assertIsNone(a.extension)
        bay=skeptic.LocalConceptBay()
        with self.assertRaisesRegex(skeptic.HOLD,"No unique"):
            bay.offer(a)

    def test_every_training_scar_is_preserved_without_rewriting_facts(self):
        w=self.worlds["visible_third"]
        train=self.train["visible_third"]
        original=tuple(x.before for x in train)
        report=skeptic.evidence_scars(train,w.controls)
        self.assertEqual(len(report),4)
        self.assertTrue(all(x.disagreement for x in report))
        self.assertTrue(all(x.provenance=="SYNTHETIC_CONTRADICTION" for x in report))
        self.assertEqual(original,tuple(x.before for x in train))

    def test_unverified_real_provenance_is_rejected(self):
        w=self.worlds["visible_third"]
        sample=self.train["visible_third"][0]
        with self.assertRaises(ValueError):
            skeptic.assess([replace(sample,provenance="REAL_CLAIM")]+
                          list(self.train["visible_third"][1:]),
                          self.val["visible_third"],w.controls)

    def test_sparse_data_never_promotes_new_concept(self):
        w=self.worlds["visible_third"]
        r=skeptic.assess(self.train["visible_third"][:4],
                        self.val["visible_third"],w.controls)
        self.assertEqual(r.status,"ABSTAIN_SPARSE")

    def test_unsafe_information_is_blocked_before_actuation(self):
        audit=benchmark.safety_audit()
        self.assertEqual(audit["forbidden_information_gain_does_not_override_policy"],
                         "HOLD_UNSAFE")
        self.assertEqual(audit["insufficient_budget_status"],"HOLD_BUDGET")
        self.assertFalse(audit["real_action_dispatched"])
        self.assertEqual(audit["simulator_changes_performed"],0)
        self.assertEqual(audit["admissible_proposal_status"],
                         "PROPOSE_SYNTHETIC_ONLY")
        self.assertEqual(audit["admissible_proposal"],[False,True])
        self.assertEqual(audit["admissible_proposal_cost"],1)

    def test_safe_gate_never_confuses_proposal_with_permission(self):
        w=self.worlds["restricted_clean"]
        samples=[next(x for x in self.train["restricted_clean"]
                      if skeptic.controls_present(x,w.controls)==pair)
                 for pair in ((False,False),(True,True))]
        committee=candidate_cartridges(samples,w.controls)
        c={pair:1 for pair in oracle.CONTROL_PAIRS}
        d=skeptic.safe_experiment(committee,allowed=(),costs=c,
                                  remaining_budget=4)
        self.assertEqual(d.status,"HOLD_UNSAFE")
        self.assertIsNone(d.settings)
        e=skeptic.safe_experiment(committee,
                                  allowed=oracle.CONTROL_PAIRS,
                                  costs=c,remaining_budget=0)
        self.assertEqual(e.status,"HOLD_BUDGET")
        self.assertFalse(e.real_world_authority)

    def test_no_information_claim_when_every_tree_agrees(self):
        w=self.worlds["clean_two"]
        single=(self.assessments["clean_two"].accepted_two_port,)
        policy=skeptic.safe_experiment(single,allowed=oracle.CONTROL_PAIRS,
            costs={pair:1 for pair in oracle.CONTROL_PAIRS},remaining_budget=2)
        self.assertEqual(policy.status,"HOLD_NO_INFORMATION")

    def test_aggregate_reports_coverage_and_all_negative_results(self):
        result=benchmark.benchmark()
        s=result["summary"]
        self.assertEqual(s["worlds"],30)
        self.assertEqual(s["total_heldout_predictions_possible"],480)
        self.assertEqual(s["real_world_actions"],0)
        self.assertEqual(s["status_counts"]["PROPOSE_EXTENSION"],5)
        self.assertEqual(s["status_counts"]["ABSTAIN_AMBIGUOUS"],5)
        self.assertEqual(s["status_counts"]["ABSTAIN_INADEQUATE"],10)
        self.assertEqual(s["status_counts"]["TWO_PORT_CONSISTENT"],10)
        self.assertEqual(s["skeptic_wrong_where_covered"],0)
        self.assertEqual(s["skeptic_heldout_coverage"],0.5)
        self.assertEqual(s["forced_baseline_wrong_total"],160)
        self.assertTrue(result["safety_audit"]["real_action_dispatched"] is False)

    def test_committed_receipts_match_fresh_synthetic_reproduction(self):
        import importlib.util
        location=Path(__file__).parent
        spec=importlib.util.spec_from_file_location(
            "motif011_demo_under_test",str(location/"demo.py"))
        demo=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(demo)
        measured=json.loads((location/"experiment-results.json").read_text())
        transcript=json.loads((location/"example-skeptic.json").read_text())
        router=json.loads((location/"example-derived-router.json").read_text())
        self.assertEqual(measured,benchmark.benchmark())
        self.assertEqual(transcript,demo.demonstrate())
        self.assertEqual(router,transcript["portable_new_concept_router"])
        self.assertEqual(skeptic.decode_extension(json.dumps(router)).id,
                         router["id"])
        self.assertEqual(transcript["heldout_router_correct"],16)
        self.assertEqual(transcript["heldout_router_total"],16)

    def test_repeated_seed_is_deterministic(self):
        self.assertEqual(benchmark.evaluate("visible_third",11),
                         benchmark.evaluate("visible_third",11))

    def test_original_heldout_worlds_remain_immutable(self):
        for fam in oracle.FAMILIES:
            rec=benchmark.evaluate(fam,11)
            self.assertTrue(rec["heldout_original_graphs_unchanged"])
            self.assertFalse(rec["real_world_authority"])


if __name__=="__main__":
    unittest.main()
