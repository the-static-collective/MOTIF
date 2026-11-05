"""Evaluator-owned fictional teacher: it supplies *observable choices*, not thoughts."""
from itertools import product
from reason import Correction, SIGNALS, SOURCE_REVISION

# Private to synthetic evaluator, NOT passed to the pupil.
TEACHER_PRIORITY = (
    "MISSING_AUTHORITY", "CONTRADICTION", "STALE_SOURCE",
    "LOOKUP_AVAILABLE", "PLAN_POSSIBLE",
)


def answer(active):
    if not active:
        raise ValueError("No signals")
    return next(s for s in TEACHER_PRIORITY if s in active)


def teach_pair(active, index):
    choice = answer(active)
    wrong = next(s for s in active if s != choice)
    return Correction(task_ref=f"teaching-task-{index:02}", active=tuple(sorted(active)),
                      pupil_guess=wrong, teacher_choice=choice,
                      evidence_ref=f"synthetic-outcome-{index:02}",
                      source_revision=SOURCE_REVISION)


def withheld_review():
    """No two-signal training probes appear in this independent multifeature review."""
    return tuple((tuple(s for s, used in zip(SIGNALS, bits) if used),
                  answer(tuple(s for s, used in zip(SIGNALS, bits) if used)))
                 for bits in product((0, 1), repeat=len(SIGNALS)) if sum(bits) >= 3)


def rote_case_baseline(active):
    # Naive original pupil: alphabetically first signal, no learned priority.
    return sorted(active)[0]
