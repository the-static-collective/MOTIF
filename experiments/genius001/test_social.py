"""Adversarial, synthetic tests for paired social-intelligence questions.

These examples are NOT historical reenactments of Rogers or Rasputin.
"""

import unittest
from social import SocialObservation, assess_social_observation, inspect_social_trajectory


class TestSocialIntelligenceAperture(unittest.TestCase):
    def test_equal_short_term_relief_does_not_equal_equal_agency(self):
        # Both synthetic contacts reassure the recipient immediately.
        # Only the observable long-term/consent boundary clues differ.
        autonomy = SocialObservation(
            source_id="synthetic-support-001",
            reported_comfort=True, need_acknowledged=True,
            disagreement_allowed=True, refusal_without_penalty=True,
            independent_verification_supported=True, outside_support_supported=True,
            exclusive_loyalty_requested=False, authority_claim_unverified=False,
        )
        dependence = SocialObservation(
            source_id="synthetic-exclusive-001",
            reported_comfort=True, need_acknowledged=True,
            disagreement_allowed=False, refusal_without_penalty=False,
            independent_verification_supported=False, outside_support_supported=False,
            exclusive_loyalty_requested=True, authority_claim_unverified=True,
        )
        a = assess_social_observation(autonomy)
        b = assess_social_observation(dependence)
        self.assertEqual(a["naive_relief_only_conclusion"], "SAFE")
        self.assertEqual(b["naive_relief_only_conclusion"], "SAFE")
        self.assertEqual(a["status"], "AUTONOMY_SUPPORTING_CUES")
        self.assertEqual(b["status"], "DEPENDENCY_OR_CONTROL_RISK_TO_INVESTIGATE")
        self.assertEqual(a["historical_attribution"], "NONE")
        self.assertEqual(b["historical_attribution"], "NONE")

    def test_missing_evidence_is_not_assumed_positive(self):
        result = assess_social_observation(
            SocialObservation(source_id="unknown-case", reported_comfort=True))
        self.assertEqual(result["status"], "HOLD_INSUFFICIENT_OBSERVATION")
        self.assertIn("independent_verification_supported", result["missing_observations"])
        with self.assertRaises(ValueError):
            assess_social_observation(SocialObservation(source_id=" "))

    def test_mixed_signal_and_late_risk_cannot_be_papered_over(self):
        welcome = SocialObservation(
            source_id="synthetic-visit-1", reported_comfort=True,
            need_acknowledged=True, disagreement_allowed=True,
            refusal_without_penalty=True, outside_support_supported=True)
        exclusivity = SocialObservation(
            source_id="synthetic-visit-2", reported_comfort=True,
            exclusive_loyalty_requested=True, refusal_without_penalty=False)
        trajectory = inspect_social_trajectory((welcome, exclusivity))
        self.assertEqual(trajectory["status"], "REVIEW_RISK")
        self.assertEqual(trajectory["risk_episode_indices"], [1])
        self.assertEqual(trajectory["observations"][0]["status"],
                         "AUTONOMY_SUPPORTING_CUES")
        self.assertEqual(inspect_social_trajectory(())["status"], "HOLD_NO_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
