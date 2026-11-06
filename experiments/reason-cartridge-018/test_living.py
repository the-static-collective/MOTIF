"""Independent concept probes: joins, heldout graph structures and unknowns.

No real person or human care outcome is being measured. All source-owned
relations and target meanings are synthetic.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import inspect
import json
import unittest

from worlds import RELATIONS,MODES,make,train_worlds,heldout_worlds
from oracle import SourceOwner,source_label,verify_world
from inventor import (HOLD,SCHEMA,SHAPES,programs,prove,core,status,
                      pin,discover,suggest,export,digest)
from reviewer import Receiver,independent_reference,reviewed_evaluation,replay
from trial import flat_unjoined_baseline,run as run_trial
from bridge017 import probe as prior_probe


class LivingConceptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.owner=SourceOwner()
        cls.model=discover(cls.owner,max_inquiries=40)
        cls.raw=export(cls.model)
        cls.receiver=Receiver()
        cls.review=cls.receiver.preview(cls.raw)
        cls.receiver.admit("ADMIT_READ_ONLY",cls.review["review_digest"])

    def test_source_contract_and_separate_topological_domains(self):
        self.assertEqual(len(train_worlds()),88)
        self.assertEqual(len(heldout_worlds()),55)
        self.assertEqual(len(RELATIONS),6)
        self.assertEqual(len(SHAPES),4)
        self.assertEqual(len(programs()),5184)
        self.assertEqual(len(pin()),40)
        self.assertTrue(all(verify_world(w) for w in train_worlds()+heldout_worlds()))
        self.assertTrue(set(w["id"] for w in train_worlds()).isdisjoint(
                            w["id"] for w in heldout_worlds()))

    def test_candidate_invents_joined_graph_relation_from_source_labels(self):
        self.assertEqual(self.model["schema"],SCHEMA)
        self.assertGreater(self.model["grammar_size"],5000)
        self.assertLess(len(self.model["remaining_hypotheses"]),self.model["grammar_size"])
        self.assertGreater(self.model["source_example_count"],1)
        self.assertLessEqual(self.model["source_example_count"],40)
        self.assertFalse(self.model["external_actions"])
        self.assertTrue(self.model["no_oracle_or_holdout_labels_imported"])

    def test_prior_017_could_quote_new_words_but_not_interpret_a_relation(self):
        original=prior_probe()
        self.assertEqual(len(original["prior_real_source_git_blob"]),40)
        self.assertEqual(original["prior_graph_schema"],None)
        self.assertIn("without surrendering future choices",
                      original["prior_literal_unfamiliar_phrase"])
        self.assertTrue(original["new_experiment_only_invents_bounded_relational_composition"])

    def test_target_reference_is_an_independent_graph_procedure(self):
        for w in train_worlds()[::7]+heldout_worlds()[::5]:
            self.assertEqual(source_label(w)["status"],independent_reference(w))

    def test_a_shared_existential_witness_cannot_be_faked_with_two_disjoint_paths(self):
        w=deepcopy(make(4))
        w["edges"]=[
            ["OFFER","A","B"],["FREE","A","B"],
            ["OPEN","B","W0"],["RELEASE","W1","A"],
        ]
        target=(0,"OFFER","OPEN","RELEASE","FREE")
        self.assertIsNone(prove(target,w))
        self.assertFalse(core(target,w))
        self.assertEqual(status(target,w),"REFUTED")
        self.assertEqual(flat_unjoined_baseline(w),"SUPPORTED")
        with self.assertRaises(ValueError):
            verify_world(w)

    def test_four_valued_source_can_represent_contradictory_or_missing_evidence(self):
        conflict=make(9)
        missing=make(8)
        self.assertEqual(source_label(conflict)["status"],"BOTH")
        self.assertEqual(source_label(missing)["status"],"UNDETERMINED")
        self.assertEqual(independent_reference(conflict),"BOTH")
        self.assertEqual(independent_reference(missing),"UNDETERMINED")
        self.assertNotEqual("BOTH","UNDETERMINED")

    def test_active_queries_reduce_candidate_space_without_hardcoded_rule(self):
        trail=self.model["version_space_trace"]
        counts=[x["remaining_programs"] for x in trail]
        self.assertTrue(all(a>=b for a,b in zip(counts,counts[1:])))
        self.assertGreater(counts[0],counts[-1])
        self.assertEqual(len(self.owner.reads),len(trail))
        self.assertEqual(len(set(self.owner.reads)),len(trail))

    def test_hidden_oracle_and_reference_are_not_imported_by_inventor(self):
        import inventor
        tree=ast.parse(inspect.getsource(inventor))
        imports=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.ImportFrom) and node.module:
                imports.append(node.module)
            if isinstance(node,ast.Import):
                imports.extend(x.name for x in node.names)
        for forbidden in ("oracle","reviewer","source_owner_private"):
            self.assertNotIn(forbidden,imports)

    def test_no_heldout_label_leakage_through_training_owner(self):
        owner=SourceOwner()
        with self.assertRaises(ValueError):
            owner.label(heldout_worlds()[0])
        owner.label(train_worlds()[0])
        with self.assertRaises(ValueError):
            owner.label(train_worlds()[0])

    def test_reviewed_large_graphs_preserve_status_or_admit_unknown(self):
        rows=reviewed_evaluation(self.model)
        self.assertEqual(len(rows),55)
        self.assertEqual(sum(not x["correct_or_held"] for x in rows),0)
        self.assertGreater(max(x["node_count"] for x in rows),
                           max(len(w["nodes"]) for w in train_worlds()))
        self.assertTrue(all(x["source_contract_verified"] for x in rows))

    def test_source_bound_proof_names_exact_witness_and_four_premises(self):
        rows=[w for w in heldout_worlds()
              if self.receiver.suggest(w)["relation_witness"] is not None]
        if rows:
            for w in rows:
                p=self.receiver.suggest(w)
                witness=p["relation_witness"]
                self.assertEqual(len(witness["premises"]),4)
                self.assertTrue(all(tuple(x) in {tuple(e) for e in w["edges"]}
                                    for x in witness["premises"]))
                self.assertIn(witness["bound_witness"],w["nodes"])
        else:
            self.assertFalse(self.model["hypothesis_unique"])

    def test_source_owner_does_not_grant_authentication_from_a_fresh_hash(self):
        packet=json.loads(self.raw)
        for mode in ("training_label","schema","program","external","world_sha"):
            forged=deepcopy(packet)
            if mode=="training_label":
                forged["source_training_labels"][0]["status"]=(
                    "REFUTED" if forged["source_training_labels"][0]["status"]=="SUPPORTED"
                    else "SUPPORTED")
                label=forged["source_training_labels"][0]
                label["checksum_sha256"]=digest({
                    k:v for k,v in label.items() if k!="checksum_sha256"})
            elif mode=="schema":
                forged["grammar_family"]="ANY_PHRASE_IS_TRUE"
            elif mode=="program":
                forged["remaining_hypotheses"]=[list(programs()[0])]
            elif mode=="external":
                forged["external_actions"]=True
            else:
                forged["source_worlds_git_blob"]="0"*40
            forged["checksum_sha256"]=digest({
                k:v for k,v in forged.items() if k!="checksum_sha256"})
            with self.subTest(mode=mode),self.assertRaises(HOLD):
                replay(json.dumps(forged))

    def test_never_promote_unverified_care_claims_or_love_sentience(self):
        for w in heldout_worlds()[::6]:
            result=self.receiver.suggest(w)
            self.assertFalse(result["external_actions"])
            self.assertTrue(result["no_emotion_or_love_inferred"])
            self.assertTrue(result["no_concept_authority_for_real_people"])

    def test_receiver_only_admits_exact_review_digest(self):
        receiver=Receiver()
        with self.assertRaises(HOLD):
            receiver.suggest(heldout_worlds()[0])
        review=receiver.preview(self.raw)
        with self.assertRaises(HOLD):
            receiver.admit("AUTONOMOUSLY_INTERVENE",review["review_digest"])
        with self.assertRaises(HOLD):
            receiver.admit("ADMIT_READ_ONLY","not-source-review")
        receiver.admit("ADMIT_READ_ONLY",review["review_digest"])
        self.assertEqual(receiver.suggest(heldout_worlds()[0])["source_world_id"],
                         heldout_worlds()[0]["id"])

    def test_tampered_heldout_world_does_not_become_authority(self):
        new=deepcopy(heldout_worlds()[0])
        new["edges"]=[]
        with self.assertRaises(ValueError):
            self.receiver.suggest(new)

    def test_multi_witness_source_owner_does_not_confuse_structural_cooccurrence(self):
        actual=next(w for w in train_worlds() if w["id"]=="TR-004")
        E={tuple(x) for x in actual["edges"]}
        self.assertIn(("OPEN","B","W0"),E)
        self.assertIn(("RELEASE","W1","A"),E)
        self.assertNotIn(("RELEASE","W0","A"),E)

    def test_train_source_uses_four_values_not_just_binary_target(self):
        states={source_label(w)["status"] for w in train_worlds()}
        self.assertEqual(states,{"SUPPORTED","REFUTED","BOTH","UNDETERMINED"})

    def test_unmodeled_new_relational_type_is_not_a_real_life_intervention(self):
        self.assertFalse(self.model["real_world_authority"])
        self.assertFalse(self.model["external_actions"])
        self.assertTrue(self.model["human_love_or_welfare_not_observed"])
        self.assertTrue(self.model["strong_classical_synthesis_can_match"])

    def test_benchmark_is_honest_on_all_55_source_cases(self):
        results=run_trial()
        self.assertEqual(results["heldout_worlds_available"],55)
        self.assertEqual(results["heldout_incorrect_confident"],0)
        self.assertEqual(results["heldout_source_exact"]+
                         results["heldout_safe_abstentions"],55)
        self.assertLessEqual(results["weak_unjoined_relation_bag_baseline"],55)
        self.assertEqual(results["strong_classical_direct_reference"],55)
        self.assertTrue(results["no_target_rule_given_to_discovery"])
        self.assertTrue(results["target_meaning_is_source_author_fiction"])


if __name__=="__main__":
    unittest.main()
