"""LAW-FORGE-011: new signed literal critic adversarial and source-review tests."""
from itertools import product
import inspect
import unittest

import signed_critic
from entropy_cartridge import EntropyCartridge
from learner import Question, Observation
from signed_critic import (
    SignedTerm, SignedAudit, POLICIES, signed_library, surviving_critics,
    question, bits, LEARN_BUDGET, AUDIT_BUDGET
)
from source_owner import UnknownOwner, FAMILIES, split
from trial import learn, inquire, trial, summarize


class SignedCriticTests(unittest.TestCase):
    def test_critic_imports_no_hidden_source(self):
        self.assertNotIn("from source_owner import",
                         inspect.getsource(signed_critic))
        self.assertNotIn("import source_owner", inspect.getsource(signed_critic))
        self.assertIn("from entropy_cartridge import", inspect.getsource(signed_critic))
        self.assertIn("from falsifier import", inspect.getsource(signed_critic))

    def test_mixed_literal_grammar_is_nonvacuous_on_both_anchors(self):
        corpus = signed_library()
        self.assertEqual(len(corpus), 1452)
        self.assertEqual(len({(t.positive,t.negative) for t in corpus}),
                         len(corpus))
        self.assertTrue(all(not t.fires((0,)*12) and
                            not t.fires((1,)*12) for t in corpus))
        self.assertTrue(SignedTerm((1,), (2,)).fires(
            (0,1,0) + (0,)*9))
        self.assertFalse(SignedTerm((1,), (2,)).fires(
            (0,1,1) + (0,)*9))

    def test_forbid_duplicate_misaligned_and_unsigned_mutants(self):
        for pos,neg in (((1,),()), ((1,), (1,)), ((12,), (1,)),
                        ((1,1), (3,)), ((2,1),(3,)),
                        ((0,1),(2,3))):
            with self.subTest(pos=pos,neg=neg), self.assertRaises(ValueError):
                SignedTerm(pos,neg)

    def test_source_initial_anchors_no_longer_force_empty_critics(self):
        for family in ("bit", "xor2", "or3"):
            world = UnknownOwner(family,7)
            learned,_ = learn(world)
            self.assertIn((0,)*12,dict(learned.snapshot))
            self.assertIn((1,)*12,dict(learned.snapshot))
            self.assertEqual(len(learned.survivor_indices),1)
            self.assertGreater(len(surviving_critics(learned)),0)

    def test_protocol_has_disjoint_reviewer_and_test_sources(self):
        for seed in (0,1,7,8,9,10):
            p=split(seed)
            self.assertEqual([len(p[k]) for k in (
                "initial","catalog","review","test")],
                [4,160,192,256])
            keys=tuple(p)
            for i,key in enumerate(keys):
                for second in keys[i+1:]:
                    self.assertTrue(set(p[key]).isdisjoint(p[second]))

    def test_source_never_exposes_hidden_family_in_capability_contract(self):
        w=UnknownOwner("signed_exception",8)
        self.assertNotIn("signed_exception",str(w.contract.packet()))
        self.assertTrue(len(w.positions)==5)
        self.assertEqual(len(w.catalog()),160)
        with self.assertRaises(ValueError):
            w.execute(Question(w.independent("review")[0].x,1,1))

    def test_all_methods_use_exact_same_preidentification_evidence(self):
        w=UnknownOwner("signed_exception",8)
        prior,questions=learn(w)
        for policy in POLICIES:
            result, same, _ = inquire(w,policy)
            self.assertEqual(same,questions)
            self.assertEqual(result.learning,prior)
            self.assertLessEqual(result.audit_spent,AUDIT_BUDGET)
            self.assertLessEqual(result.evidence.budget_spent,24)

    def test_cost_and_source_labels_are_not_forged(self):
        world=UnknownOwner("signed_exception",7)
        learning,_=learn(world)
        audit=SignedAudit(learning)
        proposal=audit.propose(world.catalog())
        self.assertIsNotNone(proposal)
        self.assertTrue(proposal.packet()["owner_must_execute"])
        self.assertFalse(proposal.packet()["real_world_authority"])
        measured=world.execute(proposal.card)
        altered=Observation(world.initial()[0].x,world.initial()[0].y,
                            world.contract.id)
        with self.assertRaises(ValueError):
            audit.ingest(proposal,altered,world.catalog())
        with self.assertRaises(ValueError):
            audit.ingest(proposal,measured,())
        with self.assertRaises(ValueError):
            audit.ingest(proposal,measured,tuple(q for q in world.catalog()
                                               if q!=proposal.card))

    def test_owner_response_updates_immutable_cartridge_and_rejects_replay(self):
        world=UnknownOwner("signed_exception",8)
        original=SignedAudit(learn(world)[0])
        proposed=original.propose(world.catalog())
        observed=world.execute(proposed.card)
        updated=original.ingest(proposed,observed,world.catalog())
        self.assertEqual(len(original.audit),0)
        self.assertEqual(len(updated.audit),1)
        self.assertNotEqual(original.id,updated.id)
        self.assertEqual(updated.audit_spent,proposed.card.unit_cost)
        self.assertEqual(SignedAudit.from_packet(updated.packet()),updated)
        with self.assertRaises(ValueError):
            updated.ingest(proposed,observed,world.catalog())

    def test_tampered_serialized_proposals_cannot_acquire_authority(self):
        world=UnknownOwner("bit",8)
        packet=SignedAudit(learn(world)[0]).packet()
        for modification in (
            {"status":"ADMITTED"},
            {"real_world_authority":True},
            {"source_digest":"0"*64},
            {"id":"signed-"+"0"*24},
            {"owner_must_execute":False},
            {"audit_budget":100},
            {"policy":"ACTUATE"},
            {"callback":"https://bad.invalid"},
            {"audit_spent":True},
            {"survivors":-1}
        ):
            with self.subTest(change=modification),self.assertRaises(ValueError):
                SignedAudit.from_packet({**packet,**modification})

    def test_apparent_single_rule_does_not_mean_truth(self):
        world=UnknownOwner("signed_exception",7)
        learned,_=learn(world)
        self.assertEqual(len(learned.survivor_indices),1)
        self.assertGreater(len(surviving_critics(learned)),0)
        self.assertIsNone(SignedAudit(learned).grammar_gap())
        # A surviving rule is a candidate, not a theorem about the source.
        self.assertIn(trial(world)["decision"],(
            "HOLD_WITNESSED_GRAMMAR_GAP",
            "HOLD_INDEPENDENT_FALSIFIER",
            "HOLD_INSUFFICIENT_REVIEW_COVERAGE",
            "ELIGIBLE_PREDICT_ONLY_PENDING_HUMAN_REVIEW"))

    def test_genuine_source_grammar_gap_proves_only_a_restricted_grammar(self):
        from gap import diagnose, independent_core_check
        world=UnknownOwner("four_bit_parity",8)
        rows=[]
        for combo in product((0,1),repeat=4):
            x=[0]*12
            for pos,val in zip(world.positions[:4],combo):
                x[pos]=val
            rows.append(world.read(tuple(x)))
        model=EntropyCartridge(world.contract,tuple(rows))
        self.assertEqual(model.survivor_indices,())
        gap=diagnose(model)
        self.assertIsNotNone(gap)
        self.assertTrue(independent_core_check(model,gap))
        self.assertFalse(gap.packet()["real_world_authority"])

    def test_source_revision_change_holds_without_retraining(self):
        world=UnknownOwner("bit",7)
        data=trial(world)
        self.assertEqual(data["stale_source_status"],
                         "HOLD_SOURCE_REVISION_CHANGED")
        self.assertEqual(data["real_world_authority"],False)

    def test_shifted_owner_laws_are_reviewed_not_silently_admitted(self):
        for family in ("training_review_shift","hidden_context_shift"):
            with self.subTest(family=family):
                row=trial(UnknownOwner(family,8))
                self.assertEqual(row["heldout_covered"],0)
                self.assertFalse(row["decision"].startswith("ELIGIBLE"))

    def test_no_audit_has_no_new_witnesses_and_no_cost(self):
        world=UnknownOwner("signed_exception",8)
        ledger,_,q=inquire(world,"no_audit")
        self.assertEqual(len(q),0)
        self.assertEqual(ledger.audit_spent,0)
        self.assertEqual(trial(world,"no_audit")["audit_cost"],0)

    def test_compact_sample_compares_fair_classical_controls(self):
        source=UnknownOwner("signed_exception",8)
        for policy in POLICIES:
            with self.subTest(policy=policy):
                row=trial(source,policy)
                self.assertEqual(row["heldout_cases"],256)
                self.assertLessEqual(row["total_cost"],24)
                self.assertEqual(row["heldout_wrong"],0)
        rows=[trial(UnknownOwner("bit",8),policy)
              for policy in POLICIES]
        self.assertEqual(summarize(rows)["worlds"],len(POLICIES))


if __name__=="__main__":
    unittest.main()
