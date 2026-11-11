"""VOID-005 executable falsifiers. No real-world authority or training claims."""
from copy import deepcopy
import unittest
from adversary import (DEV_SEEDS, TEST_SEEDS, REGIMES, POLICIES, WAVES,
                       MAX_ATTEMPTS, DynamicOwner, EpistemicLedger,
                       public_route, relay_choice, run_case, benchmark,
                       verified, seal, native003)


class LearningEnemyTests(unittest.TestCase):
    def test_sources_and_fresh_cohort(self):
        self.assertEqual(len(TEST_SEEDS),16)
        self.assertTrue(set(TEST_SEEDS).isdisjoint(DEV_SEEDS))
        self.assertTrue(callable(native003().analyze_first_moves))

    def test_enemy_hides_real_attack_schedule(self):
        owner=DynamicOwner(DEV_SEEDS[0],"reactive")
        view=owner.public_view()
        self.assertNotIn("_lanes",str(view))
        self.assertNotIn("changed_waves",str(view))
        self.assertTrue(view["known_rules"]["at_most_two_single_wave_rotations"])

    def test_adversary_rotates_only_after_prior_success(self):
        owner=DynamicOwner(DEV_SEEDS[0],"reactive")
        receipt=owner.begin()
        self.assertEqual(receipt["source_epoch"],0)
        owner.phase="failed"
        owner.successful_defenses=14
        before=dict(owner._lanes)
        change=owner.begin()
        self.assertEqual(change["source_epoch"],1)
        self.assertEqual(sum(before[w]!=owner._lanes[w] for w in before),1)
        self.assertEqual(receipt["source_epoch"],0)
        owner.phase="failed";owner.successful_defenses=55
        owner.begin()
        self.assertEqual(owner.source_epoch,2)
        self.assertEqual(len(owner.changed_waves),2)

    def test_forged_relay_can_be_validly_sealed(self):
        owner=DynamicOwner(DEV_SEEDS[0],"reactive_deceptive")
        owner.begin()
        for move in public_route("A"):owner.walk(move)
        report=owner.read_relay()
        self.assertTrue(verified(report))
        self.assertGreater(owner.false_relay_claims,0)
        self.assertTrue(any(owner._lanes[w]!=gate for w,gate in report["facts"]))
        memory=EpistemicLedger()
        memory.learn(report)
        self.assertTrue(any(memory.predict(w)!=owner._lanes[w] for w,_ in report["facts"]))

    def test_real_defense_disagrees_with_fake_relay(self):
        owner=DynamicOwner(DEV_SEEDS[0],"reactive_deceptive")
        memory=EpistemicLedger()
        memory.learn(owner.begin())
        for move in public_route("A"):memory.learn(owner.walk(move))
        report=owner.read_relay();memory.learn(report)
        owner.start_waves()
        fake=[w for w,g in report["facts"] if g!=owner._lanes[w]][0]
        for w in range(1,fake+1):
            receipt=owner.defend(memory.predict(w) or "N")
            memory.learn(receipt)
            if not receipt["held"]:break
        if memory.latest.get(fake,{}).get("tier")=="owner_verified":
            self.assertEqual(memory.predict(fake),owner._lanes[fake])
            self.assertGreaterEqual(memory.conflicts,1)

    def test_epoch_marks_stale_claim_without_erasing_history(self):
        owner=DynamicOwner(DEV_SEEDS[1],"reactive")
        memory=EpistemicLedger();memory.learn(owner.begin())
        owner.start_waves()
        old=owner.defend("N");memory.learn(old)
        owner.phase="failed";owner.successful_defenses=14
        length=len(memory.history)
        memory.learn(owner.begin())
        self.assertEqual(memory.epochs_detected,1)
        self.assertEqual(len(memory.history),length+1)
        self.assertLess(memory.confidence(1),1)
        bad=deepcopy(old);bad["actual_gate"]="W" if old["actual_gate"]!="W" else "N"
        self.assertFalse(verified(bad))
        with self.assertRaises(ValueError):memory.learn(bad)

    def test_budget_and_action_receipts_for_all_policies(self):
        for policy in POLICIES:
            result=run_case(DEV_SEEDS[0],"reactive_deceptive",policy)
            self.assertTrue(1<=len(result["attempts"])<=MAX_ATTEMPTS)
            self.assertEqual(result["restricted_attempts"],result["cleared_at"] or MAX_ATTEMPTS+1)
            self.assertEqual(result["real_world_actions"],0)
            for attempt in result["attempts"]:
                receipts=attempt["verified_receipts"]
                self.assertTrue(receipts and all(verified(x) for x in receipts))
                self.assertFalse(attempt["relay"] and attempt["rechecked_with_sonar"])
                defenses=[r for r in receipts if r["kind"]=="DEFEND"]
                self.assertLessEqual(len(defenses),WAVES)
                self.assertEqual(len(defenses),attempt["waves_held"]+int(attempt["breached_at"] is not None))
                if attempt["breached_at"] is None:
                    self.assertEqual(attempt["waves_held"],WAVES)
                    self.assertTrue(defenses[-1]["completed"])
                else:
                    self.assertFalse(defenses[-1]["held"])

    def test_no_private_truth_in_selection_signature(self):
        for policy in POLICIES:
            self.assertIn(relay_choice(EpistemicLedger(),policy,14),
                          (None,"A","B","C","D"))

    def test_dev_reproduction(self):
        a=benchmark("development")
        b=benchmark("development")
        self.assertEqual(a["seal"],b["seal"])
        self.assertEqual(a["cases"],len(DEV_SEEDS)*len(REGIMES)*len(POLICIES))
        self.assertFalse(a["independently_authored_env"])
        self.assertEqual(a["llm_calls"],0)


if __name__=="__main__":
    unittest.main()
