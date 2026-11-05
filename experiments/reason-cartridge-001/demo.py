"""Run the teacher -> cartridge -> independent receiver-review synthetic loop."""
import json
from reason import Pupil, LocalReceiver, SIGNALS
from teacher_fixture import teach_pair, withheld_review, rote_case_baseline


def run():
    pupil = Pupil()
    receipt = []
    for i in range(10):
        question = pupil.next_probe()
        if question is None:
            break
        correction = teach_pair(question, i)
        pupil.add(correction)
        receipt.append({"probe": question, "pupil_guess": correction.pupil_guess,
                        "teacher_chose": correction.teacher_choice})
    raw = pupil.export()
    local = LocalReceiver(raw)
    # Receiver-owned withheld evaluation, never shared with teaching pupil.
    cases = withheld_review()
    review = local.preview(cases)
    baseline_correct = sum(rote_case_baseline(a) == expected for a, expected in cases)
    if review["errors"] == 0:
        local.admit("ADMIT_READ_ONLY", review["review_digest"])
    return {"schema": "motif.reason-teaching-receipt.v1",
            "training_probes": len(receipt), "teaching_observations": receipt,
            "learned_order": pupil.learned_order(), "heldout_cases": len(cases),
            "rote_baseline_correct": baseline_correct,
            "learned_correct": review["correct"],
            "full_knowledge_teacher_correct": len(cases),
            "receiver_admitted_read_only": local.admitted,
            "example_suggestion": local.suggest(SIGNALS),
            "cartridge_checksum_sha256": json.loads(raw)["checksum_sha256"],
            "real_world_authority": False}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
