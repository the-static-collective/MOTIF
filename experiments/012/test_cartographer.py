"""MOTIF-012: deterministic falsifiers for causal proxy attribution and restraint."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import inspect
import json
import sys
import unittest

# Select local oracle + evaluator FIRST; inherited modules mutate sys.path.
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"008"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"009"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"010"))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"011"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import oracle
import benchmark
import cartographer
from skeptic import assess
from cartridge import validate_cartridge,export_cartridge


class CausalCartographerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world=oracle.new_world("cause_c",11)
        cls.train=oracle.natural(cls.world,"train")
        cls.validation=oracle.natural(cls.world,"validation")
        cls.start=cartographer.opening_model_space(
            cls.train,cls.validation,cls.world.controls)

    def test_model_has_no_access_to_oracle_or_hidden_family(self):
        src=inspect.getsource(cartographer)
        self.assertNotIn("from oracle import",src)
        self.assertNotIn("import oracle",src)
        self.assertNotIn("spec.family",src)
        self.assertNotIn("_effect(",src)

    def test_natural_data_cannot_distinguish_six_mechanisms(self):
        signatures=[]
        for family in oracle.FAMILIES:
            spec=oracle.new_world(family,11)
            train=oracle.natural(spec,"train")
            # Outcome signatures agree across worlds even though their
            # relation vocabulary and entity IDs are different.
            signatures.append(tuple(cartographer.validated_result(x)
                                    for x in train))
            self.assertEqual(assess(train,oracle.natural(spec,"validation"),
                                    spec.controls).status,"ABSTAIN_AMBIGUOUS")
        self.assertEqual(len(set(signatures)),1)

    def test_observation_splits_are_distinct_and_immutable(self):
        for family in oracle.FAMILIES:
            spec=oracle.new_world(family,11)
            groups=(oracle.natural(spec,"train"),
                    oracle.natural(spec,"validation"),
                    oracle.independent_suite(spec,"local_review"),
                    oracle.independent_suite(spec,"test"))
            self.assertEqual(tuple(map(len,groups)),(16,16,16,16))
            names=[{e.roles for e in group} for group in groups]
            for i in range(4):
                for j in range(i+1,4):
                    self.assertFalse(names[i] & names[j])
            self.assertTrue(all(isinstance(x.before,frozenset)
                                for group in groups for x in group))

    def test_confounding_breaks_when_candidates_are_set_independently(self):
        spec=self.world
        original=oracle.natural(spec,"train")
        self.assertTrue(all(
            ((spec.candidate_c,e.roles[0]) in e.before) ==
            ((spec.candidate_p,e.roles[1]) in e.before)
            for e in original))
        query=oracle.intervene(spec,True,False,900)
        self.assertIn((spec.candidate_c,query.roles[0]),query.before)
        self.assertNotIn((spec.candidate_p,query.roles[1]),query.before)

    def test_candidate_relations_are_inferred_from_011_not_named(self):
        c,p=cartographer.discover_candidate_relations(
            self.train,self.validation,self.world.controls)
        self.assertEqual(c.role_index,0)
        self.assertEqual(p.role_index,1)
        self.assertEqual(c.name,self.world.candidate_c)
        self.assertEqual(p.name,self.world.candidate_p)
        self.assertNotIn("cause",c.name)
        self.assertNotIn("proxy",p.name)

    def test_four_real_009_tree_cartridges_exist(self):
        self.assertEqual(len(self.start.models),4)
        self.assertEqual({m.label for m in self.start.models},
                         set(cartographer.PROGRAMS))
        for model in self.start.models:
            self.assertEqual(validate_cartridge(export_cartridge(model.tree)),
                             model.tree)
            self.assertEqual(model.tree.status,"PROPOSAL_ONLY")
            self.assertEqual(sum(map(sum,model.tree.counts)),16)
            self.assertNotIn("e12_11_train_",export_cartridge(model.tree))

    def test_hypothesis_leaves_are_explicit_programs_not_truth(self):
        for model in self.start.models:
            self.assertEqual(model.tree.leaves,
                             cartographer.PROGRAMS[model.label])
            self.assertEqual(model.tree.evidence_count,16)
            self.assertTrue(all(model.residual(*pair)==model.tree.leaves[i]
                                for i,pair in enumerate(oracle.PAIRS)))

    def test_five_worlds_preserve_same_observational_uncertainty(self):
        models=[]
        for family in oracle.FAMILIES:
            spec=oracle.new_world(family,11)
            state=cartographer.opening_model_space(
                oracle.natural(spec,"train"),
                oracle.natural(spec,"validation"),spec.controls)
            models.append(len(state.models))
        self.assertEqual(models,[4]*6)

    def test_first_question_splits_four_hypotheses_evenly(self):
        proposal=cartographer.choose(self.start)
        self.assertEqual(proposal.status,"PROPOSE_SYNTHETIC_ONLY")
        self.assertEqual(proposal.settings,(False,True))
        self.assertEqual(proposal.expected_gain_bits,1)
        self.assertEqual(proposal.predictions.count(True),2)
        self.assertEqual(proposal.predictions.count(False),2)
        self.assertFalse(proposal.real_world_authority)

    def test_second_question_reduces_version_space_four_to_two_to_one(self):
        state=self.start
        counts=[len(state.models)]
        tested=[]
        for step in range(2):
            plan=cartographer.choose(state,used=tested)
            self.assertEqual(plan.expected_gain_bits,1.0)
            evidence=oracle.intervene(self.world,*plan.settings,
                                      sequence=1000+step)
            state=cartographer.revise(state,evidence,self.world.controls)
            tested.append(plan.settings)
            counts.append(len(state.models))
        self.assertEqual(counts,[4,2,1])
        self.assertEqual(state.models[0].label,"FIRST")
        self.assertEqual(len(state.scars),2)
        self.assertEqual(cartographer.choose(state,used=tested).status,
                         "HOLD_NO_INFORMATION")

    def test_four_clean_mechanisms_are_distinguishable_in_simulation(self):
        intended={"cause_c":"FIRST","cause_p":"SECOND",
                  "joint":"JOINT","either":"EITHER"}
        for family,model in intended.items():
            sample=benchmark.evaluate(family,11,"cartographer")
            self.assertEqual(sample["provisional_model_label"],model)
            self.assertTrue(sample["independently_admitted"])
            self.assertEqual(sample["independent_review_status"],
                             "ELIGIBLE_PREDICT_ONLY_PENDING_LOCAL_DECISION")
            self.assertEqual(sample["heldout_prediction_coverage"],1)
            self.assertEqual(sample["wrong_when_covered"],0)

    def test_fixed_classical_diagnostic_ties_on_clean_worlds(self):
        for family in ("cause_c","cause_p","joint","either"):
            learned=benchmark.evaluate(family,11,"cartographer")
            fixed=benchmark.evaluate(family,11,"fixed_diagnostic")
            self.assertEqual(learned["independently_admitted"],
                             fixed["independently_admitted"])
            self.assertEqual(learned["inquiries_used"],fixed["inquiries_used"])
            self.assertEqual(learned["heldout_prediction_coverage"],
                             fixed["heldout_prediction_coverage"])

    def test_hidden_context_cannot_be_explained_as_visible_cause(self):
        for seed in oracle.SEEDS:
            row=benchmark.evaluate("latent",seed,"cartographer")
            self.assertEqual(row["independent_review_status"],
                             "HOLD_INDEPENDENT_FALSIFIER")
            self.assertFalse(row["independently_admitted"])
            self.assertGreater(row["local_review_rejected_observations"],0)
            self.assertEqual(row["heldout_prediction_coverage"],0)

    def test_intervention_noise_is_held_not_explained_away(self):
        for seed in oracle.SEEDS:
            row=benchmark.evaluate("noisy_c",seed,"cartographer")
            self.assertEqual(row["independent_review_status"],
                             "HOLD_INDEPENDENT_FALSIFIER")
            self.assertGreater(row["local_review_rejected_observations"],0)
            self.assertFalse(row["independently_admitted"])

    def test_same_visible_setting_reveals_hidden_context_disagreement(self):
        spec=oracle.new_world("latent",11)
        a=oracle.intervene(spec,True,False,110,context=False)
        b=oracle.intervene(spec,True,False,111,context=True)
        self.assertNotEqual(cartographer.validated_result(a),
                            cartographer.validated_result(b))
        c=cartographer.opening_model_space(
            oracle.natural(spec,"train"),oracle.natural(spec,"validation"),
            spec.controls)
        # Natural evidence alone cannot identify why outcomes differ.
        self.assertEqual(len(c.models),4)

    def test_wrong_after_graph_does_not_silently_override_evidence(self):
        episode=oracle.intervene(self.world,True,False,120)
        flipped=replace(episode,observed_after=episode.before)
        state=cartographer.TrialState((self.start.models[0],),(),
                                     "SINGLE_PROVISIONAL")
        revised=cartographer.revise(state,flipped,self.world.controls)
        self.assertEqual(revised.status,"OUTSIDE_GRAMMAR")
        self.assertEqual(len(revised.models),0)
        self.assertEqual(len(revised.scars),1)
        self.assertEqual(cartographer.choose(revised).status,"HOLD_NO_MODEL")

    def test_invalid_or_unverified_observation_is_rejected(self):
        x=self.train[0]
        bad=replace(x,provenance="CLAIMED_REAL_OBSERVATION")
        with self.assertRaises(ValueError):
            cartographer.revise(self.start,bad,self.world.controls)

    def test_refuse_unsafe_discrimination_even_if_information_is_one_bit(self):
        policy=oracle.declared_policy()
        result=cartographer.choose(self.start,allowed=policy["allowed"],
                                   costs=policy["costs"],
                                   remaining_budget=policy["budget"])
        self.assertEqual(result.status,"HOLD_UNSAFE")
        self.assertIsNone(result.settings)
        self.assertEqual(result.real_world_authority,False)

    def test_refuse_over_budget_but_admit_a_bounded_proposal(self):
        prices={pair:4 for pair in oracle.PAIRS}
        result=cartographer.choose(self.start,allowed=oracle.PAIRS,
                                   costs=prices,remaining_budget=1)
        self.assertEqual(result.status,"HOLD_BUDGET")
        permitted=cartographer.choose(self.start,allowed=oracle.PAIRS,
                         costs={pair:1 for pair in oracle.PAIRS},
                         remaining_budget=1)
        self.assertEqual(permitted.status,"PROPOSE_SYNTHETIC_ONLY")
        self.assertEqual(permitted.cost,1)
        self.assertFalse(permitted.real_world_authority)

    def test_negative_or_zero_intervention_cost_rejected(self):
        with self.assertRaises(ValueError):
            cartographer.choose(self.start,costs={
                pair:0 for pair in oracle.PAIRS})
        with self.assertRaises(ValueError):
            cartographer.choose(self.start,remaining_budget=-1)

    def test_local_review_requires_disjoint_factorial_evidence(self):
        state=cartographer.TrialState((self.start.models[0],),(),
                                     "SINGLE_PROVISIONAL")
        small=oracle.independent_suite(self.world,"local_review")[:4]
        result=cartographer.independent_review(
            state,small,self.world.controls)
        self.assertEqual(result.status,"HOLD_INSUFFICIENT_LOCAL_REVIEW")

    def test_review_abstains_when_two_candidate_mechanisms_remain(self):
        result=cartographer.independent_review(
            self.start,oracle.independent_suite(self.world,"local_review"),
            self.world.controls)
        self.assertEqual(result.status,"HOLD_AMBIGUOUS_OR_FALSIFIED")
        self.assertIsNone(result.proposed_model)

    def test_original_observational_world_is_immutable(self):
        before=tuple(x.before for x in self.train)
        benchmark.evaluate("cause_c",11,"cartographer")
        self.assertEqual(before,tuple(x.before for x in self.train))

    def test_naive_observation_only_baseline_is_weak_and_always_predicts(self):
        c=benchmark.evaluate("cause_c",11,"cartographer")
        p=benchmark.evaluate("cause_p",11,"cartographer")
        self.assertEqual(c["naive_observational_wrong"],0)
        self.assertGreater(p["naive_observational_wrong"],0)
        self.assertEqual(p["wrong_when_covered"],0)

    def test_real_external_operation_methods_are_absent(self):
        self.assertFalse(hasattr(cartographer,"dispatch"))
        self.assertFalse(hasattr(cartographer,"execute"))
        self.assertFalse(hasattr(cartographer,"authenticate"))
        self.assertEqual(benchmark.safe_scope_proof()["simulator_operations_dispatched"],0)

    def test_review_success_does_not_automatically_admit_a_cartridge(self):
        review=cartographer.independent_review(
            cartographer.TrialState((self.start.models[0],),(),
                                    "SINGLE_PROVISIONAL"),
            oracle.independent_suite(self.world,"local_review"),
            self.world.controls)
        self.assertEqual(review.status,
                         "ELIGIBLE_PREDICT_ONLY_PENDING_LOCAL_DECISION")
        bay=cartographer.LocalCausalBay()
        ticket=bay.offer(self.start.models[0],review)
        self.assertNotIn(ticket,bay.admitted)
        test=oracle.independent_suite(self.world,"test")[0]
        with self.assertRaises(cartographer.HOLD):
            bay.predict(ticket,test,self.world.controls)
        receipt=bay.decide(ticket,"ADMIT_PREDICT_ONLY",
                           "LOCAL_SYNTHETIC_STEWARD")
        self.assertEqual(receipt["decision"],"ADMIT_PREDICT_ONLY")
        self.assertFalse(receipt["real_world_authority"])
        self.assertEqual(bay.predict(ticket,test,self.world.controls),
                         cartographer.validated_result(test))
        bay.revoke(ticket,"LOCAL_SYNTHETIC_STEWARD")
        with self.assertRaises(cartographer.HOLD):
            bay.predict(ticket,test,self.world.controls)

    def test_falsified_cartridge_cannot_self_admit(self):
        latent=oracle.new_world("latent",11)
        start=cartographer.opening_model_space(
            oracle.natural(latent,"train"),
            oracle.natural(latent,"validation"),latent.controls)
        state=start
        seen=[]
        for i in range(2):
            offer=cartographer.choose(state,used=seen)
            evidence=oracle.intervene(latent,*offer.settings,sequence=1000+i)
            state=cartographer.revise(state,evidence,latent.controls)
            seen.append(offer.settings)
        review=cartographer.independent_review(
            state,oracle.independent_suite(latent,"local_review"),latent.controls)
        bay=cartographer.LocalCausalBay()
        ticket=bay.offer(state.models[0],review)
        with self.assertRaisesRegex(cartographer.HOLD,"falsification"):
            bay.decide(ticket,"ADMIT_PREDICT_ONLY","LOCAL")
        self.assertNotIn(ticket,bay.admitted)

    def test_unknown_relation_in_local_scene_is_refused(self):
        row=oracle.independent_suite(self.world,"test")[0]
        augmented=replace(row,before=row.before|{("unreviewed",row.roles[0])})
        with self.assertRaisesRegex(cartographer.HOLD,"Unreviewed"):
            self.start.models[0].predict(augmented,self.world.controls)

    def test_natural_source_is_not_independent_review_evidence(self):
        state=cartographer.TrialState((self.start.models[0],),(),
                                     "SINGLE_PROVISIONAL")
        with self.assertRaisesRegex(cartographer.HOLD,"new intervention"):
            cartographer.independent_review(
                state,self.train,self.world.controls)

    def test_checked_in_intervention_cartridges_match_fresh_demo(self):
        import importlib.util
        filename=Path(__file__).parent/"demo.py"
        module=importlib.util.module_from_spec(
            importlib.util.spec_from_file_location("motif012_demo_test",filename))
        module.__spec__.loader.exec_module(module)
        saved=json.loads((Path(__file__).parent/
                          "example-causal-map.json").read_text())
        self.assertEqual(saved,module.demonstrate())
        healthy=saved["supported_causal_candidate"]
        self.assertEqual(len(healthy["initial_hypotheses"]),4)
        self.assertEqual([x["candidate_count_after"]
                          for x in healthy["interventions"]],[2,1])
        self.assertEqual(healthy["local_fixture_admission"]["decision"],
                         "ADMIT_PREDICT_ONLY")
        self.assertTrue(healthy["held_before_explicit_local_decision"])
        self.assertEqual(saved["latent_source_refused"]["local_review"]["status"],
                         "HOLD_INDEPENDENT_FALSIFIER")
        self.assertEqual(saved["noisy_source_refused"]["local_review"]["status"],
                         "HOLD_INDEPENDENT_FALSIFIER")
        for card in healthy["initial_hypotheses"]:
            self.assertEqual(validate_cartridge(json.dumps(card["tree"])).id,
                             card["tree"]["id"])

    def test_world_full_record_and_ci_receipt_reproduce_exactly(self):
        saved=json.loads((Path(__file__).parent/
                          "experiment-results.json").read_text())
        result=benchmark.benchmark()
        self.assertEqual(saved,result)
        s=result["summary"]
        self.assertEqual(s["worlds_per_method"],36)
        self.assertEqual(s["methods"]["cartographer"]["independently_admitted_worlds"],24)
        self.assertEqual(s["methods"]["fixed_diagnostic"]["independently_admitted_worlds"],24)
        self.assertEqual(s["methods"]["cartographer"]["heldout_wrong_where_covered"],0)
        self.assertEqual(s["real_world_actions"],0)

if __name__=="__main__":
    unittest.main()
