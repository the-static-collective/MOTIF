"""Synthetic hostile tests for BRIDGE-001. No real people or external acts."""
import unittest
from dataclasses import replace

from bridge import (
    Acceptance, Candidate, Goal, Offer, Scene,
    first_human_card, food, generate, options, solve, transition, workshop,
)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.scene, self.offers, self.acceptances, self.goal = workshop()

    def test_does_not_receive_a_list_of_interventions(self):
        candidates = generate(self.scene, self.offers, self.acceptances, self.goal)
        self.assertIn("ADMITTED_SIM:teach-well:ben", [c.id for c in candidates])
        self.assertIn("ADMITTED_SIM:inform-well:ben", [c.id for c in candidates])
        self.assertIn("ADMITTED_SIM:lend-kit:ada", [c.id for c in candidates])
        self.assertIn("ADMITTED_SIM:make-kit:ada", [c.id for c in candidates])
        self.assertEqual(len(candidates), 4)

    def test_declared_consent_and_cost_picks_non_depriving_two_step(self):
        r = solve(self.scene, self.offers, self.acceptances, self.goal)
        self.assertEqual(r["status"], "PROPOSED_SYNTHETIC_ONLY")
        self.assertEqual(r["known_cost"], 3)
        self.assertEqual(r["known_minutes"], 16)
        self.assertEqual({a["kind"] for a in r["actions"]}, {"teach", "inform"})
        self.assertEqual(r["delta"]["visible"]["gained"], ["ben:well"])
        for scope in ("physical", "admitted", "visible"):
            self.assertEqual(r["delta"][scope]["lost"], [])

    def test_unprotected_fast_but_depriving_loan(self):
        relaxed = replace(self.goal, preserve=False)
        r = solve(self.scene, self.offers, self.acceptances, relaxed)
        self.assertEqual(r["known_cost"], 1)
        self.assertEqual(r["actions"][0]["kind"], "loan")
        self.assertEqual(r["delta"]["visible"]["lost"], ["ben:bike"])

    def test_not_supplied_offers_generate_held_bindings(self):
        scene, offers, accepted, goal = workshop(with_offers=False)
        r = solve(scene, offers, accepted, goal)
        self.assertEqual(r["status"], "HOLD_UNVERIFIED_BRIDGE")
        self.assertEqual(len(r["held_steps"]), 2)
        self.assertFalse(r["total_duration_known"])
        self.assertFalse(r["total_cost_known"])
        card = first_human_card(r)
        self.assertEqual(card["state"], "DRAFT_NOT_SENT")
        self.assertIn("has not offered", card["first_step"])
        self.assertTrue(card["no_auto_contact"])

    def test_held_proposal_cannot_be_applied_in_admitted_mode(self):
        scene, offers, accepted, goal = workshop(with_offers=False)
        a = next(c for c in generate(scene, offers, accepted, goal)
                 if c.kind == "teach")
        self.assertEqual(a.status, "HOLD_OFFER")
        self.assertIsNone(transition(scene, a))
        self.assertIsNotNone(transition(scene, a, counterfactual=True))

    def test_missing_recipient_acceptance_remains_held(self):
        redacted = frozenset(
            x for x in self.acceptances if x.offer_id != "teach-well"
        )
        candidates = generate(self.scene, self.offers, redacted, self.goal)
        teaching = next(c for c in candidates if c.kind == "teach")
        self.assertEqual(teaching.status, "HOLD_ACCEPTANCE")
        # Alternative: a complete, accepted maker offer remains available.
        result = solve(self.scene, self.offers, redacted, self.goal)
        self.assertEqual(result["status"], "PROPOSED_SYNTHETIC_ONLY")
        self.assertEqual(result["actions"][0]["kind"], "make")

    def test_withdrawn_offer_never_becomes_admitted_sim(self):
        withdrawn = tuple(
            replace(o, declared=False) if o.id == "teach-well" else o
            for o in self.offers
        )
        candidates = generate(self.scene, withdrawn, self.acceptances, self.goal)
        a = next(c for c in candidates if c.kind == "teach")
        self.assertEqual(a.status, "HOLD_OFFER")

    def test_forged_consent_outside_recipient_scope_is_rejected(self):
        extra = self.acceptances | {Acceptance("teach-well", "ada")}
        with self.assertRaises(ValueError):
            generate(self.scene, self.offers, extra, self.goal)

    def test_cannot_create_permission_without_existing_site_access(self):
        scene = replace(self.scene, access=frozenset({("ben", "bike")}))
        r = solve(scene, self.offers, self.acceptances,
                  Goal("well", preserve=True))
        self.assertEqual(r["status"], "ABSTAIN_NO_BOUNDED_BRIDGE")
        self.assertEqual(r["candidate_bindings"], 0)

    def test_wrong_tool_cannot_imply_capability(self):
        scene = replace(self.scene,
                        requirements=frozenset({("well", "ladder"), ("bike", "kit")}))
        r = solve(scene, self.offers, self.acceptances, self.goal)
        self.assertEqual(r["status"], "ABSTAIN_NO_BOUNDED_BRIDGE")

    def test_renamed_second_domain_uses_same_grammar(self):
        scene, offers, accepted, goal = food()
        r = solve(scene, offers, accepted, goal)
        self.assertEqual(r["status"], "PROPOSED_SYNTHETIC_ONLY")
        self.assertEqual(r["known_cost"], 4)
        self.assertEqual(r["known_minutes"], 14)
        self.assertEqual({a["kind"] for a in r["actions"]}, {"inform", "make"})
        self.assertEqual(r["delta"]["visible"]["gained"], ["courier:food_relay"])
        self.assertEqual(r["delta"]["visible"]["lost"], [])

    def test_deadline_blocks_slow_plan_in_held_synthetic_model(self):
        scene, offers, accepted, goal = food()
        r = solve(scene, offers, accepted,
                  replace(goal, deadline_minutes=10))
        self.assertEqual(r["status"], "ABSTAIN_NO_BOUNDED_BRIDGE")

    def test_absent_offer_does_not_establish_deadline_feasibility(self):
        scene, offers, accepted, goal = workshop(with_offers=False)
        r = solve(scene, offers, accepted,
                  replace(goal, deadline_minutes=1))
        self.assertEqual(r["status"], "HOLD_UNVERIFIED_BRIDGE")
        self.assertIsNone(r["deadline_feasible"])

    def test_one_offer_can_cover_multiple_recipient_bindings_but_only_scoped(self):
        scene = replace(
            self.scene,
            access=self.scene.access | {("cee", "well")}
        )
        offers = tuple(
            replace(o, recipients=o.recipients | {"cee"})
            if o.id in ("teach-well", "inform-well") else o
            for o in self.offers
        )
        accepted = self.acceptances | {
            Acceptance("teach-well", "cee"), Acceptance("inform-well", "cee")
        }
        candidates = generate(scene, offers, accepted, Goal("well"))
        self.assertIn("ADMITTED_SIM:teach-well:cee",
                      [c.id for c in candidates])
        self.assertNotIn("ADMITTED_SIM:lend-kit:cee",
                         [c.id for c in candidates])

    def test_truncated_search_never_claims_optimal_solution(self):
        result = solve(self.scene, self.offers, self.acceptances, self.goal,
                       max_states=1)
        self.assertEqual(result["status"], "HOLD_TRUNCATED")
        self.assertEqual(result["actions"], [])

    def test_duplicate_offer_identity_rejected(self):
        with self.assertRaises(ValueError):
            generate(self.scene, self.offers + (self.offers[0],),
                     self.acceptances, self.goal)

    def test_unchanged_input_after_counterfactual_search(self):
        snapshot = self.scene
        before = options(self.scene)
        solve(self.scene, self.offers, self.acceptances, self.goal)
        self.assertEqual(snapshot, self.scene)
        self.assertEqual(before, options(self.scene))

    def test_repeatability_independent_of_offer_order(self):
        a = solve(self.scene, self.offers, self.acceptances, self.goal)
        b = solve(self.scene, tuple(reversed(self.offers)),
                  self.acceptances, self.goal)
        self.assertEqual(a, b)


    def test_emergent_relay_action_not_available_at_initial_cut(self):
        # Ari can teach Bea, and Bea promises to teach Cy later. Bea initially
        # lacks the skill. The second move becomes possible *because* of first.
        scene = Scene(
            requirements=frozenset({("relay", "transmitter")}),
            skills=frozenset({("ari", "relay")}),
            assets=frozenset({("t1", "transmitter")}),
            custody=frozenset({("cy", "t1")}),
            access=frozenset({("cy", "relay")}),
            known=frozenset({("cy", "relay")}),
        )
        offers = (
            Offer("ari-to-bea", "teach", "ari", "relay",
                  frozenset({"bea"}), 2, 6),
            Offer("bea-to-cy", "teach", "bea", "relay",
                  frozenset({"cy"}), 2, 6),
        )
        accepted = frozenset({
            Acceptance("ari-to-bea", "bea"),
            Acceptance("bea-to-cy", "cy"),
        })
        initial = generate(scene, offers, accepted, Goal("relay", actor="cy"))
        future_teaching = next(
            c for c in initial if c.offer_id == "bea-to-cy"
        )
        self.assertIsNone(transition(scene, future_teaching))
        result = solve(scene, offers, accepted, Goal("relay", actor="cy"))
        self.assertEqual(result["status"], "PROPOSED_SYNTHETIC_ONLY")
        self.assertEqual([a["offer_id"] for a in result["actions"]],
                         ["ari-to-bea", "bea-to-cy"])
        self.assertEqual(result["known_cost"], 4)
        self.assertEqual(result["delta"]["visible"]["gained"], ["cy:relay"])

    def test_missing_relay_consent_is_not_silently_granted(self):
        scene = Scene(
            requirements=frozenset({("relay", "transmitter")}),
            skills=frozenset({("ari", "relay")}),
            assets=frozenset({("t1", "transmitter")}),
            custody=frozenset({("cy", "t1")}),
            access=frozenset({("cy", "relay")}),
            known=frozenset({("cy", "relay")}),
        )
        offers = (
            Offer("ari-to-bea", "teach", "ari", "relay",
                  frozenset({"bea"}), 2, 6),
            Offer("bea-to-cy", "teach", "bea", "relay",
                  frozenset({"cy"}), 2, 6),
        )
        accepted = frozenset({Acceptance("bea-to-cy", "cy")})
        result = solve(scene, offers, accepted, Goal("relay", actor="cy"))
        self.assertEqual(result["status"], "HOLD_UNVERIFIED_BRIDGE")
        self.assertEqual(result["held_steps"],
                         ["HOLD_ACCEPTANCE:ari-to-bea:bea"])
        self.assertIsNone(transition(
            scene, next(x for x in generate(
                scene, offers, accepted, Goal("relay", actor="cy")
            ) if x.offer_id == "ari-to-bea")
        ))

    def test_no_false_delivery_evidence_in_first_card(self):
        result = solve(self.scene, self.offers, self.acceptances, self.goal)
        card = first_human_card(result)
        self.assertEqual(card["state"], "DRAFT_NOT_SENT")
        self.assertTrue(card["requires_human_review"])
        self.assertTrue(card["no_auto_contact"])


if __name__ == "__main__":
    unittest.main()
