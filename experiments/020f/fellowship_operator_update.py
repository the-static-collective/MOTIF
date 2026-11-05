"""MOTIF-020F: apply an operator-provided Fellowship observation to the timeline.

The user now reports:
  - permission to use Riverside space is granted;
  - the user and Paula are core organizers;
  - they believe an achievable event is within their capacity.

These are human-reported event facts, NOT an amendment to PlanZ's public
index, not proof that food/music/safeguarding permissions are settled, and
not authorization to contact any person or submit any grant.

The exact existing InsideOutBox optimizer evaluates a NEW schedule after
removing the resolved venue-approval question.
"""
from __future__ import annotations

from dataclasses import asdict, replace
import json

from insideout import CounterfactualOpportunity, InsideOutBox, scope_only
from planz import read_planz_snapshot
from fellowship_timeline import ExternalWindowOverlay, SOURCE_DATES, WINDOWS, inputs


USER_OBSERVATION = {
    "observed_as_of": "2026-11-05",
    "origin": "USER_DIRECT_REPORT_IN_CHAT",
    "venue_use_permission": "REPORTED_GRANTED",
    "two_core_organizers": "USER_AND_PAULA",
    "operator_assessment": "WE_CAN_DO_IT",
    "not_inferred": (
        "GENERAL_EVENT_LEGAL_AUTHORITY",
        "FOOD_SERVICE_APPROVAL",
        "SAFEGUARDING_COMPLETE",
        "SOUND_AND_MUSIC_ARRANGEMENTS_FINAL",
        "VOLUNTEER_COMMITMENTS_FINAL",
        "GRANT_TEAM_ELIGIBILITY_CONFIRMED",
    ),
}

# This is an operator planning menu, not a statement that every task is
# undone. Scope is intentionally achievable for two core organizers.
NEXT_WORK = {
    "FELLOWSHIP_SIMPLE_RUN_OF_SHOW":
        ("Confirm a minimal timetable, room flow, audio responsibility, and host roles",
         6.0, 2),
    "FELLOWSHIP_INVITE_AND_HELPER_MAP":
        ("Choose only essential invitations and ask volunteers for explicit roles",
         5.0, 3),
    "FELLOWSHIP_GO_NO_GO_CHECK":
        ("Check music, food safety, accessibility, staffing, and fallback feasibility",
         3.0, 4),
}

def updated_options():
    # Unlike the earlier model, no question about *whether space is granted*
    # remains. Actual preparation steps are choices for two organizers.
    existing = tuple(
        c for c in inputs()
        if c.plan_id not in {
            "RIVERSIDE_HOST_QUESTION",
            "FELLOWSHIP_STAFFING_QUESTION",
        }
    )
    new = tuple(
        CounterfactualOpportunity(id, value, latest_tick)
        for id, (_description, value, latest_tick) in NEXT_WORK.items()
    )
    return existing + new

def analyze():
    planz = read_planz_snapshot()
    # The PlanZ snapshot remains a read-only, non-authoritative context.
    # This separate operator assertion is not written back into PlanZ.
    overlay = ExternalWindowOverlay(
        edition="USER_OBSERVED_FELLOWSHIP_UPDATE+SCENARIO_ONLY+PlanZRef=" + planz.edition,
        git_blob=planz.git_blob,
        pointer_ids=frozenset(
            set(SOURCE_DATES) | set(NEXT_WORK)
        )
    )
    baseline = updated_options()
    scenarios = {
        "reported_venue_granted_limited_capacity": (baseline, 4, 1),
        "reported_venue_granted_two_organizers_can_parallelize": (baseline, 4, 2),
        "no_viable_nexus_team_verified": (
            tuple(o for o in baseline if o.plan_id != "NEXUS_TEAM_QUESTION"), 4, 2
        ),
        "fellowship_run_sheet_must_be_decided_today": (
            tuple(
                replace(o, last_start_tick=0)
                if o.plan_id == "FELLOWSHIP_SIMPLE_RUN_OF_SHOW" else o
                for o in baseline
            ), 4, 1
        ),
        "no_defensible_time_or_value_assumptions": ((), 4, 2),
    }
    results = {}
    for case, (menu, capacity, parallel) in scenarios.items():
        result = InsideOutBox(
            overlay, menu, horizon=8,
            attention_budget=capacity,
            max_parallel=parallel,
            cognition_cost_per_tick=0.05,
        ).analyze()
        results[case] = {
            "first_review_step": result.first_batch,
            "hypothetical_total_value": result.optimal_modeled_value,
            "hypothetical_myopic_value": result.baseline_myopic_value,
            "hypothetical_cost_of_waiting_one_bucket": result.cost_of_waiting_one_tick,
            "no_actual_authority": not result.external_execution_allowed,
            "proposed_sequence": [
                {"window": WINDOWS[step.tick], "work": step.plans,
                 "imaginary_value_units": step.modeled_net_gain}
                for step in result.sequence if step.plans
            ],
            "invented_assumptions": [
                {"id": o.plan_id, "invented_reward": o.reward_if_successful,
                 "invented_last_effective_window": WINDOWS[o.last_start_tick]}
                for o in menu
            ],
        }
    return {
        "schema": "motif020f.fellowship-operator-update/v0",
        "as_of": "2026-11-05",
        "observation": USER_OBSERVATION,
        "source_planz": {
            "edition": planz.edition,
            "read_only": True,
            "authority": planz.authority,
            "original_index_conclusion": scope_only(planz)["status"],
            "planZ_field_outcomes_not_rewritten": True,
        },
        "resolved_old_question": "RIVERSIDE_HOST_QUESTION",
        "continuing_grant_question": "NEXUS_TEAM_QUESTION",
        "operational_questions_now": [
            {"id": key, "scope": description,
             "internal_last_window_is_hypothesis_not_real_deadline": WINDOWS[tick]}
            for key, (description, _value, tick) in NEXT_WORK.items()
        ],
        "scenario_model_not_verified_impact": results,
        "conclusion": (
            "Venue permission is reported settled. Stop wasting attention on "
            "permission-as-an-unknown, and plan the two-organizer minimum "
            "viable event. Nexus eligibility/team remains a separate unknown, "
            "subject to its application cutoff; do not invent a team or "
            "treat a fictional priority score as an instruction to dispatch."
        ),
        "people_contacted": False,
        "applications_submitted": False,
        "event_guaranteed": False,
    }

if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
