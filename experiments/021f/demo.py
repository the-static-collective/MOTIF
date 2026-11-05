"""MOTIF-021F — run one read-only three-role chorus beside a real MOTIF decision.

Default is a SCRIPTED text fixture for reproducible CI; it is **not** LLM
inference. Pass --local-t5 only if the FLAN-T5-small checkpoint is already in
the local cache and optional CPU inference dependencies are installed.
"""
from __future__ import annotations

from dataclasses import asdict
import argparse
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "020f"))
from fellowship_operator_update import analyze  # noqa: E402
from chorus import PublicProjection, parallel_critique, LocalFlanT5Small


class ScriptedTextFixture:
    name = "SCRIPTED_FIXTURE_NOT_AN_LLM"
    responses = {
        "OBSERVER": "Venue use is reported granted; food handling and actual performer roles remain open.",
        "CRITIC": "Permission for the room does not settle food safety or audio access; verify the room rules before advertising promises.",
        "HYPEMAN": "You already have two core organizers and a room. Draft one simple run sheet before adding optional modules.",
    }

    def generate(self, prompt: str) -> str:
        for role in self.responses:
            if prompt.startswith("ROLE=" + role + "."):
                return self.responses[role]
        raise ValueError("Unknown role")


def sample_projection():
    return PublicProjection(
        problem="December 4 Fellowship: smallest viable gathering with two organizers.",
        facts=(
            "User reports permission to use the room is granted.",
            "User reports that the user and Paula are core organizers.",
            "Fellowship target date: December 4.",
        ),
        uncertainties=(
            "Exact room access/cleanup and host publicity terms.",
            "Food handling and musical participant responsibilities not reconfirmed.",
            "Nexus group eligibility and submission are not established.",
        ),
        proposed_next="Pick one minimal, owner-approved run sheet; check any irreversible grant deadline separately.",
    )


def run(*, local_t5: bool = False, grace_seconds: float = 0.25) -> dict:
    projection = sample_projection()
    backend = LocalFlanT5Small() if local_t5 else ScriptedTextFixture()
    result = parallel_critique(analyze, projection, backend,
                               sidecar_grace_seconds=grace_seconds)
    plan = result.native
    evidence = plan["scenario_model_not_verified_impact"]["reported_venue_granted_limited_capacity"]
    return {
        "schema": "motif021f.observer-critic-hypeman/v0",
        "backend": backend.name,
        "actual_llm_inference": local_t5 and all(n.status == "UNVERIFIED_TEXT_AVAILABLE"
                                                for n in result.notes),
        "native_motif": {
            "reported_venue_status": plan["observation"]["venue_use_permission"],
            "source_planz_still_index_only": plan["source_planz"]["authority"] == "INDEX_ONLY",
            "next_modeled_question": evidence["first_review_step"],
            "hypothetical_scenario_value": evidence["hypothetical_total_value"],
            "event_not_guaranteed": not plan["event_guaranteed"],
        },
        "sidecar": {
            "mode": result.mode,
            "completed_by_cutoff": result.sidecar_completed,
            "notes": [asdict(n) for n in result.notes],
            "native_wall_ms": result.native_wall_ms,
            "total_wall_ms": result.end_to_end_wall_ms,
            "time_budget_after_native_ms": result.sidecar_budget_ms,
            "adopted_suggestions": False,
            "no_external_actions": not result.external_actions,
        },
        "explanation": (
            "Native planner made its decision independently. Text notes are "
            "unverified commentary and cannot modify permissions, deadlines, "
            "funding choices or action selection. The default example is a "
            "deterministic scripted fixture, NOT an executed T5 model."
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-t5", action="store_true",
                        help="Opt into locally cached FLAN-T5-small, no download")
    parser.add_argument("--grace", type=float, default=.25,
                        help="Max seconds to wait for commentary AFTER native plan")
    opts = parser.parse_args()
    print(json.dumps(run(local_t5=opts.local_t5,
                         grace_seconds=opts.grace), indent=2, sort_keys=True))
