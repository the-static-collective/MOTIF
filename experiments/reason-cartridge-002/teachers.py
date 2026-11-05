"""Independent, synthetic teacher owners. Pupil never imports teacher programs."""
from dataclasses import dataclass
from language import Case, SOURCE_REVISION, State, execute, digest, label, transition, HOLD


@dataclass(frozen=True)
class Lesson:
    teacher_claim: str
    case: Case
    events: tuple[dict, ...]
    source_revision: str
    receipt: str

    def __post_init__(self):
        label(self.teacher_claim)
        if self.source_revision != SOURCE_REVISION:
            raise HOLD("Teacher revision mismatch")


def teach(teacher, case):
    """Teacher code is evaluator-owned; exported result is only public transitions."""
    if teacher not in ("TEACHER_A", "TEACHER_B"):
        raise HOLD("Unknown teacher fixture")
    if case.need_lookup and case.need_challenge:
        raise HOLD("Neither teacher demonstrated joint-requirement problems")
    if teacher == "TEACHER_A" and case.need_challenge:
        raise HOLD("A does not handle counterexample requirements")
    if teacher == "TEACHER_B" and case.need_lookup:
        raise HOLD("B does not handle exact-lookup requirements")
    steps = [{"op": "VERIFY_SOURCE", "guard": "ALWAYS"}]
    if teacher == "TEACHER_A" and case.need_lookup:
        steps.append({"op": "EXACT_LOOKUP", "guard": "ALWAYS"})
    if teacher == "TEACHER_B" and case.need_challenge:
        steps.append({"op": "TEST_COUNTEREXAMPLE", "guard": "ALWAYS"})
    steps.append({"op": "DRAFT_HYPOTHESIS", "guard": "ALWAYS"})
    result = execute(steps, case)
    if result["result"] != "DRAFT":
        raise HOLD("Teacher fixture failed")
    receipt = digest({"teacher": teacher, "ref": case.ref,
                      "context": case.context(), "events": result["events"],
                      "revision": SOURCE_REVISION})
    return Lesson(teacher, case, tuple(result["events"]), SOURCE_REVISION, receipt)


def lesson_set():
    # No both-needed problem appears in training. Neutral probe disambiguates guards.
    return (
        teach("TEACHER_A", Case("demo-lookup-only", True, False)),
        teach("TEACHER_B", Case("demo-challenge-only", False, True)),
        teach("TEACHER_B", Case("demo-neither", False, False)),
    )
