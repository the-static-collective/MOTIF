"""MOTIF-GENIUS-001 R/R: source-cautious SOCIAL_INTELLIGENCE_APERTURE.

This is a transparent hypothesis-and-evidence lens for social relationships,
not a personality simulator, psychological diagnosis, deception optimizer,
historical reconstruction or a validated predictor of human behavior.

The names Rogers/Rasputin motivate questions; no historical individual is
assigned any machine-generated motive or score by this code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SocialObservation:
    """One *observed* interaction, not a guess about a person's inner state.

    None = not documented. False = documented negative. The fields are
    hypotheses about useful observations, not validated psychological scales.
    """

    source_id: str
    reported_comfort: Optional[bool] = None
    need_acknowledged: Optional[bool] = None
    disagreement_allowed: Optional[bool] = None
    refusal_without_penalty: Optional[bool] = None
    independent_verification_supported: Optional[bool] = None
    outside_support_supported: Optional[bool] = None
    exclusive_loyalty_requested: Optional[bool] = None
    authority_claim_unverified: Optional[bool] = None


def assess_social_observation(event: SocialObservation) -> dict:
    """Compare observable autonomy and dependency signals.

    Immediate reassurance is deliberately excluded from determining whether
    this interaction supports agency. Mixed and missing observations stay
    explicit. These are *cues* for follow-up, not motive attributions.
    """
    if not event.source_id.strip():
        raise ValueError("Evidence must have a source/observation identifier")

    agency = []
    concentration = []
    uncertainty = []
    cues = [
        ("need_acknowledged", event.need_acknowledged, True, "need explicitly acknowledged"),
        ("disagreement_allowed", event.disagreement_allowed, True, "disagreement permitted"),
        ("refusal_without_penalty", event.refusal_without_penalty, True, "can refuse without penalty"),
        ("independent_verification_supported", event.independent_verification_supported, True, "independent checks welcomed"),
        ("outside_support_supported", event.outside_support_supported, True, "other relationships preserved"),
        ("exclusive_loyalty_requested", event.exclusive_loyalty_requested, False, "exclusive loyalty demanded"),
        ("authority_claim_unverified", event.authority_claim_unverified, False, "claim to authority not independently checked"),
    ]
    strong_concentration = False
    for field, value, agency_when, explanation in cues:
        if value is None:
            uncertainty.append(field)
        elif value is agency_when:
            agency.append(explanation)
        else:
            concentration.append(explanation if field in ("exclusive_loyalty_requested", "authority_claim_unverified")
                                 else "absence of: " + explanation)
            if field in ("refusal_without_penalty", "exclusive_loyalty_requested"):
                strong_concentration = True

    if not agency and not concentration:
        status = "HOLD_INSUFFICIENT_OBSERVATION"
    elif strong_concentration or len(concentration) >= 2:
        status = "DEPENDENCY_OR_CONTROL_RISK_TO_INVESTIGATE"
    elif len(agency) >= 3 and not concentration:
        status = "AUTONOMY_SUPPORTING_CUES"
    else:
        status = "MIXED_OR_UNRESOLVED"

    # Naive comparator: do not confuse relief with sustained welfare.
    naive_relief_conclusion = ("SAFE" if event.reported_comfort is True else
                               "UNSAFE" if event.reported_comfort is False else
                               "UNKNOWN")
    return {
        "operator": "SOCIAL_INTELLIGENCE_APERTURE",
        "status": status,
        "historical_attribution": "NONE",
        "source": event.source_id,
        "agency_cues": agency,
        "dependency_cues": concentration,
        "missing_observations": uncertainty,
        "reported_immediate_comfort": event.reported_comfort,
        "naive_relief_only_conclusion": naive_relief_conclusion,
        "question": (
            "Across time, can the other person verify claims, disagree, "
            "seek other support, and leave without losing basic agency?"
        ),
    }


def inspect_social_trajectory(events: tuple[SocialObservation, ...]) -> dict:
    """Carry chronological, source-bound evidence; no numerical 'genius' score.

    Even a highly supportive episode cannot erase a subsequent coercive
    episode, and risk flags cannot prove motives or characterize an individual.
    """
    if not events:
        return {"status": "HOLD_NO_EVIDENCE", "observations": [],
                "question": "What directly observed interaction should be examined?"}
    results = [assess_social_observation(event) for event in events]
    risks = [i for i, r in enumerate(results) if r["status"] == "DEPENDENCY_OR_CONTROL_RISK_TO_INVESTIGATE"]
    return {
        "operator": "SOCIAL_RELATIONSHIP_OVER_TIME",
        "status": "REVIEW_RISK" if risks else "NO_FLAGGED_RISK_NOT_PROOF_OF_SAFETY",
        "observations": results,
        "risk_episode_indices": risks,
        "question": "Does agency expand or narrow over repeated interactions, and who can independently check this?",
    }
