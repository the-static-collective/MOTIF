"""Run the actual MOTIF-020F InsideOutBox on Fellowship/grant decision windows.

Public deadline facts are source-checked independently. All action values,
effort limits, effective last-start windows and conditional scenarios are
author-declared hypotheses, NOT facts inferred from a grant or PlanZ record.

The model may recommend an inquiry as a hypothetical next choice. It cannot
submit grants, contact people, or grant itself third-party permission.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import date
from typing import Mapping
import json

from insideout import CounterfactualOpportunity, InsideOutBox, scope_only
from planz import read_planz_snapshot

SOURCE_DATES = {
    "NEXUS_TEAM_QUESTION": ("2026-11-06 17:00 America/Chicago",
        "https://nexuscp.org/apply-now-greater-mn-community-wealth-building-cohort/",
        "Nexus application cutoff verified; team confirmation by Nov 5 is an INTERNAL assumption"),
    "RIVERSIDE_HOST_QUESTION": ("2026-12-04",
        "USER_CONFIRMED_FELLOWSHIP_DATE",
        "Event date is user-confirmed; Nov 12 host decision is INTERNAL, not a church-imposed cutoff"),
    "FELLOWSHIP_STAFFING_QUESTION": ("2026-12-04",
        "USER_CONFIRMED_FELLOWSHIP_DATE",
        "Event date is user-confirmed; Nov 18 staffing review is INTERNAL"),
    "MOZILLA_EVIDENCE_OUTLINE": ("2026-12-17 23:59 America/Los_Angeles",
        "https://www.mozillafoundation.org/en/what-we-do/grantmaking/fellowship/",
        "Mozilla LOI deadline verified; event participation is NOT proof of successful impact"),
    "RJI_JOURNALISM_FIT": ("2027-01-08",
        "https://rjionline.org/about-rji-fellowships/",
        "RJI deadline verified; journalistic problem/eligibility must still be demonstrated"),
    "VOQAL_INTERVIEW_PREP": ("SUBMITTED; interview date unverified",
        "USER_PRIOR_SUBMISSION_CONFIRMATION",
        "Voqal application already submitted; this is optional preparation, not a new submission"),
}
WINDOWS = (
    "0: Nov 5 (today)",
    "1: Nov 6 before 5pm CT",
    "2: Nov 7–12",
    "3: Nov 13–18",
    "4: Nov 19–Dec 3",
    "5: Dec 4 (Fellowship)",
    "6: Dec 5–17",
    "7: Dec 18–Jan 8",
)


@dataclass(frozen=True)
class ScenarioPointer:
    id: str
    field_outcome: str = "NOT_VERIFIED"
    execution_allowed: bool = False
    third_party_approval: str = "NOT_ESTABLISHED"


@dataclass(frozen=True)
class ExternalWindowOverlay:
    """A distinct *scenario* source, deliberately NOT a PlanZ index entry."""
    edition: str
    git_blob: str
    pointer_ids: frozenset[str]

    def get(self, plan_id: str) -> ScenarioPointer:
        if plan_id not in self.pointer_ids:
            raise KeyError("HOLD_UNKNOWN_SCENARIO_ONLY_OPPORTUNITY:" + plan_id)
        return ScenarioPointer(plan_id)


def inputs():
    """Modeled value of preserving a next step, not grants won or dollar utility.

    Effective deadlines / values are stress assumptions. Formal externally
    documented deadlines are separately recorded above and NOT converted
    directly into the internal action-preparation windows.
    """
    return (
        CounterfactualOpportunity("NEXUS_TEAM_QUESTION", 7.0, 0, 1.0, 0., 0., 1),
        CounterfactualOpportunity("RIVERSIDE_HOST_QUESTION", 6.0, 2, 1.0, 0., 0., 1),
        CounterfactualOpportunity("FELLOWSHIP_STAFFING_QUESTION", 5.0, 3, 1.0, 0., 0., 1),
        CounterfactualOpportunity("MOZILLA_EVIDENCE_OUTLINE", 7.0, 6, 1.0, 0., 0., 1),
        CounterfactualOpportunity("RJI_JOURNALISM_FIT", 3.0, 7, 1.0, 0., 0., 1),
        CounterfactualOpportunity("VOQAL_INTERVIEW_PREP", 1.0, 7, 1.0, 0., 0., 1),
    )


def study():
    source = read_planz_snapshot()
    # Reading PlanZ's *real* source snapshot does not convert grant tasks to
    # PlanZ records. The external scenario uses a visibly separate overlay.
    overlay = ExternalWindowOverlay(
        edition="SCENARIO_ONLY_V1;PlanZRef=" + source.edition,
        git_blob=source.git_blob,
        pointer_ids=frozenset(SOURCE_DATES),
    )

    base = inputs()
    cases: dict[str, tuple[CounterfactualOpportunity, ...]] = {
        "base_five_to_four_attention": base,
        "confirmed_no_viable_nexus_team": tuple(x for x in base
                                          if x.plan_id != "NEXUS_TEAM_QUESTION"),
        "host_window_closes_immediately": tuple(
            replace(x, last_start_tick=0, reward_if_successful=9.)
            if x.plan_id == "RIVERSIDE_HOST_QUESTION" else x for x in base),
        "host_and_nexus_urgent_parallel": tuple(
            replace(x, last_start_tick=0, reward_if_successful=9.)
            if x.plan_id == "RIVERSIDE_HOST_QUESTION" else x for x in base),
        "nexus_question_low_expected_value": tuple(
            replace(x, reward_if_successful=1.)
            if x.plan_id == "NEXUS_TEAM_QUESTION" else x for x in base),
        "all_opportunities_still_reachable": base,
        "no_defensible_quantitative_assumptions": (),
    }
    answers = {}
    for name, opportunities in cases.items():
        capacity = 5 if name == "all_opportunities_still_reachable" else 4
        parallel = 2 if name == "host_and_nexus_urgent_parallel" else 1
        planner = InsideOutBox(
            overlay, opportunities, horizon=8, max_parallel=parallel,
            attention_budget=capacity, cognition_cost_per_tick=.05,
        )
        r = planner.analyze()
        answers[name] = {
            "status": r.status,
            "hypothetical_attention_budget": capacity,
            "hypothetical_simultaneous_capacity": parallel,
            "first_batch_now": r.first_batch,
            "optimal_modeled_value": r.optimal_modeled_value,
            "myopic_modeled_value": r.baseline_myopic_value,
            "cost_if_wait_one_bucket": r.cost_of_waiting_one_tick,
            "cost_if_empty_deliberation_one_bucket": r.cost_of_deliberation_one_tick,
            "model_plan_nonempty_batches": [
                {"window": WINDOWS[step.tick], "proposed": step.plans,
                 "fictional_gain": step.modeled_net_gain}
                for step in r.sequence if step.plans
            ],
            "assumptions": [
                {"id": x.plan_id,
                 "hypothetical_value_not_dollars_or_funding": x.reward_if_successful,
                 "internal_last_effective_window": WINDOWS[x.last_start_tick]}
                for x in opportunities
            ],
            "external_execution_allowed": r.external_execution_allowed,
            "verified_deadlines_inferred_from_PlanZ": r.real_deadlines_verified,
        }

    # Run the ONLY source-grounded planZ case without made-up utilities.
    actual_index_only = scope_only(source)
    assert actual_index_only["status"] == "HOLD_NO_VERIFIED_INACTION_VALUATION"
    return {
        "schema": "motif020f.fellowship_grants_test/v0",
        "as_of": "2026-11-05",
        "snapshot_planz": {
            "edition": source.edition,
            "source_sha_git_blob": source.git_blob,
            "count": len(source.plans),
            "relevant_context_pointers": {
                name: {"id": source.get(name).id, "next_gate": source.get(name).next_gate}
                for name in ("TRAVELING-JUBILEE-001", "GARDEN-TABLE-001", "BRIDGE-001")
            },
        },
        "known_and_reported": {
            "nexus_deadline": SOURCE_DATES["NEXUS_TEAM_QUESTION"][0],
            "nexus_eligibility_and_application_status": "UNCONFIRMED",
            "fellowship_december_4": "USER_CONFIRMED_EVENT_TARGET; NOT FULL LOGISTICS AUTHORIZATION",
            "fellowship_nov12_and_nov18": "ASSISTANT_INTERNAL_TARGETS_NOT_HARD_DEADLINES",
            "voqal": "USER_CONFIRMED_ALREADY_SUBMITTED",
            "mozilla_deadline": SOURCE_DATES["MOZILLA_EVIDENCE_OUTLINE"][0],
            "rji_deadline": SOURCE_DATES["RJI_JOURNALISM_FIT"][0],
        },
        "source_dates": SOURCE_DATES,
        "truth_only_planz_conclusion": actual_index_only,
        "cases": answers,
        "conclusion_scope": (
            "Cases show CONDITIONAL behavior of MOTIF-020F's actual finite-horizon DP. "
            "Values, windows, capacity, and response feasibility are not measured; "
            "a highest modeled priority is an inquiry to consider, not permission "
            "to contact or submit on behalf of anyone."
        ),
        "real_actions_executed": False,
        "applicant_team_composition_fabricated": False,
        "outside_contacts": False,
    }


if __name__ == "__main__":
    print(json.dumps(study(), indent=2, sort_keys=True))
