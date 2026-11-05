"""Run teacher observations -> method synthesis -> independent recipient test."""
import json
from teachers import lesson_set
from distillery import Distillery, LocalReceiver
from bench import independent_cases, evaluate
from language import Case


def main():
    lessons = lesson_set()
    raw = Distillery(lessons).synthesize()
    packet = json.loads(raw)
    destination = LocalReceiver(raw)
    independent = independent_cases()
    review = destination.preview(independent)
    if review["errors"] == 0 and review["unresolved_order_disagreements"] == 0:
        destination.admit("ADMIT_READ_ONLY", review["review_digest"])
    return {"schema": "motif.method-distillery-receipt.v1",
            "training_teacher_claims": sorted({x.teacher_claim for x in lessons}),
            "training_cases": [l.case.ref for l in lessons],
            "learned_program": packet["program"],
            "unobserved_order_pairs": packet["unobserved_order_pairs"],
            "review": {"correct": review["correct"], "total": review["cases"],
                       "unresolved_order_disagreements": review["unresolved_order_disagreements"]},
            "controls": evaluate(packet["program"]),
            "joint_case": destination.suggest(Case("third-procedure-joint", True, True)),
            "read_only_admission": destination.admitted,
            "cartridge_sha256": packet["checksum_sha256"],
            "real_world_authority": False}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
