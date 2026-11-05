"""MOTIF-004: a question that precedes the candidate program.

Uses unchanged, source-pinned original MOTIF-002 and MOTIF-003 to detect an
actual conflict between two declared hypothetical objectives. If there is no
policy conflict, there is no new question and no GRAFT call. This first inquiry
is limited to one synthetic graph and one numeric measurement family.
"""
from __future__ import annotations
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE_SHA = "5ee9207f04af2826750863526af7f92b31ef8578"
PINS = {
    "experiments/002/motif002.py":
        "b9f1e7b7879a94f7ef3869bc305608c4d7fa8695",
    "experiments/003/affordance.py":
        "db25da0d50a9c8e2cd87aa576a22f969405737cf",
}
SCOPE = "SYNTHETIC_POLICY_RESEARCH_ONLY"
QUESTION = "Which bounded numeric observation can resolve the disagreement between the two declared hypothetical first-action policies?"
THRESHOLD = 2


class HOLD(ValueError):
    pass


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"), allow_nan=False)
                  .encode()).hexdigest()


def git_blob(path):
    data = path.read_bytes()
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def native_modules(original):
    original = Path(original).resolve()
    for rel, sha in PINS.items():
        full = (original / rel).resolve()
        if not full.is_relative_to(original) or not full.is_file():
            raise HOLD("Original owner source missing")
        if git_blob(full) != sha:
            raise HOLD("Original owner source pin mismatch")
    for d in ("002", "003"):
        p = str(original / "experiments" / d)
        if p not in sys.path:
            sys.path.insert(0, p)
    import motif002 as two
    import affordance as three
    return two, three


def chosen(three, rows, name):
    row = three.select_first_move(rows, priority=name)
    if row is None:
        raise HOLD("No original synthetic first move available")
    return {
        "operator": row["operator"],
        "roles": list(row["roles"]),
        "new_affordance_count": len(row["new_affordances"]),
        "immediate_delta": row["immediate_delta"],
        "reachable_after_first_move": row["reachable_after_first_move"],
    }


def inspect(original, world_mode="default"):
    two, three = native_modules(original)
    if world_mode not in ("default", "no-permissions"):
        raise HOLD("World variant is not part of the bounded diagnostic")
    world = two.scene(permissions=(world_mode == "default"))
    verbs = two.induce(two.lessons())
    rows = three.analyze_first_moves(
        world, verbs, two.possibilities, two.utility, horizon=3,
        max_worlds=500)
    if not rows or any(x["truncated"] for x in rows):
        raise HOLD("Original source has no complete evidence for decision conflict")
    immediate = chosen(three, rows, "immediate")
    choices = chosen(three, rows, "new-choices")
    if (immediate["operator"], immediate["roles"]) == (
            choices["operator"], choices["roles"]):
        raise HOLD("Two original policies agree; no decision-critical gap shown")
    if len(rows) < 2:
        raise HOLD("Insufficient distinct alternatives for inquiry")
    # This is an explicit user-specified research objective, not an inferred
    # universal welfare measure. A measurement might affect an internal
    # recommendation; it is not authority to execute a physical action.
    body = {
        "schema": "motif.self-inquiry.v0",
        "status": "QUESTION_PROPOSED_BEFORE_GRAFT_SELECTION",
        "scope": SCOPE,
        "original_source_commit": SOURCE_SHA,
        "original_source_pins": PINS,
        "provenance": "ACTUAL_ORIGINAL_MOTIF_002_003_SYNTHETIC_SIMULATOR",
        "current_world": world_mode,
        "evidence": {
            "candidate_first_moves": len(rows),
            "immediate_priority_first": immediate,
            "new_choices_priority_first": choices,
            "policy_disagreement": True,
            "world_outcome_observed": False,
        },
        "question": QUESTION,
        "missing_capability_contract": {
            "kind": "NUMERIC_OBSERVATION_FROM_BOUNDED_JSON",
            "target_path_known_to_questioner": False,
            "target_path": None,
            "output_type": "INTEGER_0_TO_10",
            "decision_rule": {
                "below_threshold": "immediate",
                "at_or_above_threshold": "new-choices",
                "threshold": THRESHOLD,
            },
            "minimum_independent_final_cases": 4,
            "require_negative_cases": True,
            "source_owner_must_generate_executable": True,
            "external_endpoint_access_needed": False,
        },
        "next_steps_authorized": {
            "inspect_public_source": True,
            "local_synthetic_replay": True,
            "produce_unsent_code_candidate": True,
            "contact_people": False,
            "connect_apis": False,
            "deploy": False,
            "write_other_repositories": False,
        },
        "candidate_executable_examined": False,
        "gap_resolved": False,
    }
    return {**body, "content_sha256": digest(body)}


def verify_question(question, original):
    if not isinstance(question, dict) or set(question) != {
        "schema", "status", "scope", "original_source_commit",
        "original_source_pins", "provenance", "current_world",
        "evidence", "question", "missing_capability_contract",
        "next_steps_authorized", "candidate_executable_examined",
        "gap_resolved", "content_sha256",
    }:
        raise HOLD("Question contract changed")
    body = dict(question)
    claimed = body.pop("content_sha256")
    if not isinstance(claimed, str) or digest(body) != claimed:
        raise HOLD("Self inquiry integrity mismatch")
    expected = inspect(original, world_mode=question["current_world"])
    if expected != question:
        raise HOLD("Question is not independently reproducible from original MOTIF")
    if (question["status"] != "QUESTION_PROPOSED_BEFORE_GRAFT_SELECTION"
            or question["scope"] != SCOPE
            or question["missing_capability_contract"]["target_path"] is not None
            or question["missing_capability_contract"]["target_path_known_to_questioner"] is not False
            or question["gap_resolved"] is not False):
        raise HOLD("Question claims nonexistent knowledge or authority")
    return question["content_sha256"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--mode", choices=("default", "no-permissions"),
                   default="default")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    try:
        question = inspect(args.source, args.mode)
        if args.out.exists():
            raise HOLD("Refusing to overwrite existing inquiry")
        args.out.write_text(json.dumps(question, indent=2) + "\n")
        print(json.dumps({"status": question["status"],
                          "digest": question["content_sha256"],
                          "policy_disagreement": True}))
    except HOLD as exc:
        print(json.dumps({"stage": "HOLD", "reason": str(exc)}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
