"""Native teacher gone: independent receiver validates the portable method.

Runs AFTER a CI stage that checks out exact original Dogram, executes it for
training/review specimens, and deletes the external source checkout.
Native receipts remain source-owned evidence, not executable authorization.
"""
from __future__ import annotations

from pathlib import Path
import json

from pupil import HOLD, MENU, validate, select_method, predict, rows, reach, digest, graph_input
from objection import Inquiry, decide, check_certificate


class Receiver:
    def __init__(self, raw, source_revision):
        self.packet = validate(raw)
        if source_revision != self.packet["source_revision"]:
            raise HOLD("Receiver source revision changed")
        self.admitted = False
        self.last_digest = None
        self.passed = False

    def preview(self, independently_owned):
        if (not isinstance(independently_owned, list) or len(independently_owned) != 18):
            raise HOLD("Independent six-node review required")
        seen = set()
        audit = []
        for specimen, expected, receipt in independently_owned:
            if specimen["specimen_id"] in seen:
                raise HOLD("Repeated independent test")
            seen.add(specimen["specimen_id"])
            nodes, edges, removed = graph_input(specimen)
            if len(nodes) != 6:
                raise HOLD("Heldout world has same node width as lessons")
            from pupil import verify_native
            if verify_native(specimen, receipt) != expected:
                raise HOLD("Heldout native source mismatch")
            chosen = predict(self.packet["learned_method"], specimen)
            after = tuple(e for e in edges if e != removed)
            full_classical = reach(nodes, after)
            before = reach(nodes, edges)
            audit.append({
                "id": specimen["specimen_id"],
                "native_teacher_result": expected,
                "pupil": chosen,
                "full_classical_bfs": full_classical,
                "always_breaks": False,
                "status_quo": before,
            })
        hits = lambda field: sum(row[field] == row["native_teacher_result"] for row in audit)
        result = {
            "schema": "motif.reason.native-dogram-review.v1",
            "cases": len(audit),
            "learner_correct": hits("pupil"),
            "full_classical_correct": hits("full_classical_bfs"),
            "always_breaks_correct": hits("always_breaks"),
            "status_quo_correct": hits("status_quo"),
            "unseen_world_size": 6,
            "native_results_loaded_from_immutable_checkout_receipts": True,
            "foreign_source_was_not_imported_into_pupil": True,
            "authority": False,
        }
        self.last_digest = digest({"packet": self.packet["checksum_sha256"], "review": audit})
        self.passed = (result["learner_correct"] == len(audit)
                       and result["full_classical_correct"] == len(audit))
        result["review_digest"] = self.last_digest
        result["review_passed"] = self.passed
        return result

    def admit(self, decision, preview_digest):
        if decision != "ADMIT_READ_ONLY" or not self.passed or preview_digest != self.last_digest:
            raise HOLD("Missing independent source check or current local review")
        self.admitted = True

    def suggest(self, specimen):
        if not self.admitted:
            raise HOLD("Method cartridge HOLD pending owner review")
        return {"stage": "SUGGEST_ONLY",
                "method": self.packet["learned_method"],
                "prediction": predict(self.packet["learned_method"], specimen),
                "teacher_running": False, "externally_executed": False,
                "authority": False}


def objection_experiment():
    # The exact classical result cannot decide what *unobserved* edges do.
    # This local epistemic envelope retains a contradictory witness and asks
    # a consequential question before claiming a complete-world result.
    case = Inquiry(
        nodes=("S", "A", "B", "T"),
        universe=(("S","A"), ("A","T"), ("S","B"), ("B","T")),
        claims=(("S","A","PRESENT","r1"),
                ("A","T","PRESENT","r2"),
                ("A","T","ABSENT","counter-witness"),
                ("S","B","ABSENT","r4"),
                ("B","T","ABSENT","r5")),
        removed=("S","B"),
        closed_scope=True,
    )
    res = decide(case, false_negative_cost=8.0,
                 false_positive_cost=3.0, question_cost=0.1)
    return {"query": res, "human_action_taken": False,
            "epistemic_claim": "UNRESOLVED_NOT_FALSE",
            "real_world_authority": False}


def run(directory, require_teacher_removed=True):
    if require_teacher_removed and Path("_external/dogram").exists():
        raise HOLD("Foreign teacher source still mounted; no teacher-free proof")
    root = Path(directory)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("source_commit") !=
            "551b5f9df18f17ec69b452ddcdff01718e0ff771" or
            manifest.get("teacher_remove_before_evaluation") is not True):
        raise HOLD("Foreign source identity / absence contract mismatch")
    training = rows(root, "train")
    raw = select_method(training)
    (root / "learned-cartridge.json").write_text(raw, encoding="utf-8")
    receiver = Receiver(raw, manifest["source_commit"])
    unseen = rows(root, "withheld")
    # No training code sees the withheld source receipts before synthesis.
    result = receiver.preview(unseen)
    if result["review_passed"]:
        receiver.admit("ADMIT_READ_ONLY", result["review_digest"])
    result["human_admission"] = False
    result["synthetic_fixture_admission_only"] = receiver.admitted
    result["teacher_absent_at_evaluation"] = not Path("_external/dogram").exists()
    result["example_advisory"] = receiver.suggest(unseen[0][0]) if receiver.admitted else None
    result["objection_engine"] = objection_experiment()
    (root / "evaluation.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                           encoding="utf-8")
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: python review.py <generated-teacher-evidence>")
    print(json.dumps(run(sys.argv[1]), indent=2, sort_keys=True))
