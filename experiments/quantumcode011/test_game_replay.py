"""QC-011: a game trace is evidence of observed game events, not reality."""
from dataclasses import replace
import unittest

from game_replay import (
    NO_REALWORLD, GameState, Episode, Replay, CandidateRule,
    state, sample, interpret, derive_rules, next_questions,
    trajectory, relatte_preview, demo,
)


class SurvivalGameReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.minecraft=sample("MINECRAFT_LIKE")
        cls.last=sample("LAST_OF_US_LIKE")
        cls.long=sample("LONG_DARK_LIKE")

    def test_sample_worlds_do_not_pretend_to_be_real_gameplay(self):
        for r in (self.minecraft,self.last,self.long):
            self.assertEqual(len(r.episodes),2)
            self.assertTrue(all(ep.source=="SYNTHETIC_FIXTURE" for ep in r.episodes))
            self.assertTrue(all(ep.rights=="SYNTHETIC" for ep in r.episodes))

    def test_synthetic_playthrough_is_state_contiguous(self):
        for r in (self.minecraft,self.last,self.long):
            r.validate()
            self.assertEqual(r.episodes[0].after.pin,
                             r.episodes[1].before.pin)

    def test_source_receipts_stable(self):
        self.assertEqual(self.minecraft.pin,sample("MINECRAFT_LIKE").pin)
        self.assertEqual(len(self.minecraft.pin),64)

    def test_source_revisions_produce_new_identity(self):
        ep=self.minecraft.episodes[0]
        revised=replace(ep,claimed_reason="new provisional interpretation")
        self.assertNotEqual(ep.pin,revised.pin)

    def test_minecraft_composition_opens_actual_game_capability(self):
        changes=[interpret(x) for x in self.minecraft.episodes]
        self.assertIn("basic_tool",changes[0].gained_capabilities)
        self.assertIn("shelter",changes[1].gained_capabilities)
        self.assertTrue(all(x.world_scope==NO_REALWORLD for x in changes))

    def test_inventory_consumption_is_visible_not_inferred(self):
        changes=[interpret(x) for x in self.minecraft.episodes]
        self.assertIn(("wood",2),changes[0].spent_resources)
        self.assertIn(("wood",1),changes[1].spent_resources)

    def test_last_of_us_style_represents_resource_opportunity_cost(self):
        ch=interpret(self.last.episodes[0])
        self.assertIn(("cloth",1),ch.spent_resources)
        self.assertIn(("alcohol",1),ch.spent_resources)
        self.assertIn("first_aid_item",ch.gained_capabilities)
        self.assertFalse(ch.explanation_is_proven)

    def test_removing_hazard_does_not_prove_actual_medical_recovery(self):
        ch=interpret(self.last.episodes[1])
        self.assertIn("injury",ch.resolved_hazards)
        self.assertFalse(ch.explanation_is_proven)
        self.assertEqual(ch.world_scope,NO_REALWORLD)

    def test_long_dark_style_distinguishes_condition_change_and_cause(self):
        ch=interpret(self.long.episodes[-1])
        self.assertIn("cold",ch.resolved_hazards)
        self.assertEqual(ch.outcome,"INCONCLUSIVE")
        self.assertFalse(ch.explanation_is_proven)

    def test_next_questions_include_newly_opened_actions(self):
        qs=next_questions(self.minecraft)
        self.assertTrue(any(q.kind=="TEST_AFFORDANCE" for q in qs))
        self.assertTrue(all(q.data_needed for q in qs))

    def test_failed_action_generates_question_about_hidden_constraint(self):
        ep=replace(self.minecraft.episodes[0],outcome="FAILURE",
                   claimed_reason="attempt failed under hidden constraint")
        after=replace(self.minecraft.episodes[1],before=ep.after)
        r=Replay("MINECRAFT_LIKE",(ep,after),
                 "synthetic",True)
        q=next_questions(r)
        self.assertTrue(any(x.kind=="EXPLAIN_FAILURE" for x in q))

    def test_uncertain_vision_does_not_count_as_independent_observation(self):
        ep=replace(self.minecraft.episodes[0],
                   source="VISION_MODEL_UNVERIFIED",
                   rights="ANNOTATION_ONLY",
                   certainty="INFERRED")
        r=Replay("MINECRAFT_LIKE",(ep,self.minecraft.episodes[1]),
                 "synthetic",True)
        qs=next_questions(r)
        self.assertIn("VERIFY_VIEW",{x.kind for x in qs})
        self.assertEqual(interpret(ep).confidence,
                         "PROVISIONAL_GAME_INTERPRETATION")

    def test_vision_cannot_impersonate_verified_game_telemetry(self):
        with self.assertRaises(ValueError):
            replace(self.minecraft.episodes[0],
                    source="VISION_MODEL_UNVERIFIED",
                    certainty="OBSERVED").validate()

    def test_unbounded_copying_unapproved_footage_not_accepted(self):
        with self.assertRaises(ValueError):
            replace(self.minecraft.episodes[0],rights="UNLICENSED_RIP").validate()

    def test_no_user_playthrough_claimed_ingested(self):
        r=demo()
        self.assertFalse(r["actual_video_processed"])
        self.assertFalse(r["actual_gameplay_ingested"])
        self.assertFalse(r["real_world_survival_training"])

    def test_relatte_admission_requires_consent_and_own_review(self):
        p=relatte_preview(self.minecraft)
        self.assertEqual(p["status"],"HOLD_FOR_SEPARATE_RELATTE_OWNER_REVIEW")
        self.assertFalse(p["signed"])
        self.assertFalse(p["transported"])
        self.assertFalse(p["admitted"])
        self.assertFalse(p["executed"])
        self.assertEqual(p["real_world_actions"],0)

    def test_no_derived_data_when_consent_refused(self):
        r=replace(self.minecraft,consent_for_derived_research=False)
        p=relatte_preview(r)
        self.assertEqual(p["status"],"REFUSE_NO_DERIVATION_CONSENT")
        self.assertNotIn("packet",p)
        self.assertEqual(p["effects"],0)

    def test_relatte_packet_is_content_pinned_not_signed(self):
        p=relatte_preview(self.minecraft)
        self.assertEqual(len(p["packet_sha256"]),64)
        self.assertEqual(p["packet"]["source_pin"],self.minecraft.pin)
        self.assertEqual(p["packet"]["requested_effects"],[])
        self.assertEqual(p["packet"]["scope"],NO_REALWORLD)

    def test_relatte_adapter_is_not_native_cryptographic_crossing(self):
        p=relatte_preview(self.last)
        self.assertFalse(p["signed"])
        self.assertFalse(p["received"])
        self.assertFalse(p["admitted"])

    def test_unwitnessed_state_jump_is_rejected(self):
        second=replace(self.minecraft.episodes[1],
                       before=state((("wood",99),),(),(),1))
        r=Replay("MINECRAFT_LIKE",
                 (self.minecraft.episodes[0],second),"synthetic",True)
        with self.assertRaises(ValueError):
            r.validate()

    def test_backdated_episode_is_rejected(self):
        ep=replace(self.minecraft.episodes[1],clip_start_seconds=0,
                   before=replace(self.minecraft.episodes[1].before,
                                  clock_tick=0))
        r=Replay("MINECRAFT_LIKE",
                 (self.minecraft.episodes[0],ep),"synthetic",True)
        with self.assertRaises(ValueError):
            r.validate()

    def test_mixed_game_mechanics_are_not_silently_merged(self):
        r=Replay("MINECRAFT_LIKE",
                 (self.minecraft.episodes[0],self.last.episodes[0]),
                 "synthetic",True)
        with self.assertRaises(ValueError):
            r.validate()

    def test_unknown_game_is_rejected_not_assumed(self):
        with self.assertRaises(ValueError):
            sample("REAL_WORLD_SURVIVAL")

    def test_duplicate_episode_identity_is_rejected(self):
        r=Replay("MINECRAFT_LIKE",
                 (self.minecraft.episodes[0],
                  self.minecraft.episodes[0]),"synthetic",True)
        with self.assertRaises(ValueError):
            r.validate()

    def test_no_negative_resources_or_fabricated_inventory(self):
        with self.assertRaises(ValueError):
            state((("wood",-2),),(),(),0).validate()

    def test_correlated_success_does_not_prove_rule(self):
        rules=derive_rules(self.minecraft)
        self.assertEqual(len(rules),2)
        self.assertTrue(all(rule.conclusion==NO_REALWORLD for rule in rules))

    def test_inconsistent_effects_remain_a_conflict(self):
        e1=self.minecraft.episodes[0]
        e2=replace(e1,episode_id="second",
                   clip_start_seconds=10,clip_end_seconds=20,
                   before=e1.after,
                   after=state((("wood",0),),("basic_tool","other_tool"),(),2),
                   claimed_reason="similar action changed inventory differently")
        r=Replay("MINECRAFT_LIKE",(e1,e2),"fictional",True)
        rules=derive_rules(r)
        self.assertTrue(next(x for x in rules if x.action==e1.action).conflicts)
        self.assertTrue(any(q.kind=="RESOLVE_CONFLICT"
                            for q in next_questions(r)))

    def test_rule_counts_do_not_hide_negative_outcomes(self):
        e1=self.minecraft.episodes[0]
        e2=replace(e1,episode_id="second",
                   clip_start_seconds=10,clip_end_seconds=20,
                   before=e1.after,after=e1.after,
                   outcome="FAILURE",claimed_reason="same action failed")
        r=Replay("MINECRAFT_LIKE",(e1,e2),"fictional",True)
        rule=next(x for x in derive_rules(r) if x.action==e1.action)
        self.assertEqual(rule.witnessed_successes,1)
        self.assertEqual(rule.witnessed_failures,1)

    def test_traces_not_merged_into_human_survival_plan(self):
        x=trajectory(self.long)
        self.assertEqual(x["conclusions"],
                         "GAME_HYPOTHESES_WITH_UNRESOLVED_CAUSALITY")
        self.assertEqual(x["real_world_actions"],0)

    def test_game_event_has_actual_time_window(self):
        for ep in self.last.episodes:
            self.assertGreater(ep.clip_end_seconds,ep.clip_start_seconds)

    def test_public_synthetic_fixture_has_no_private_lived_history(self):
        r=demo()
        self.assertEqual(r["outside_effects"],0)
        self.assertFalse(r["reLATTE_native_crossing"])


if __name__=="__main__":
    unittest.main()
