"""RING-015 reserved novel-to-calibration source changes.

Imported only after validation of source-trained policy and runtime image.
18 real source copies: ten single seeded defects, two mixed defects and
six clean/benign controls. Defect status is kept strictly evaluator-side.

These are authored test cases—not independent naturally occurring defects.
They are not a claim of future real-world software reliability.
"""
from __future__ import annotations

CASES=(
    ("heldout-01",("posterior_signal",)),
    ("heldout-02",("budget_accounting",)),
    ("heldout-03",("benign_math",)),
    ("heldout-04",("benign_control",)),
    ("heldout-05",()),
    ("heldout-06",("forbidden_ranking",)),
    ("heldout-07",("gain_zero",)),
    ("heldout-08",("invalid_import",)),
    ("heldout-09",("benign_information",)),
    ("heldout-10",("source_overclaim",)),
    ("heldout-11",("entropy_sign",)),
    ("heldout-12",("stop_floor_broken",)),
    ("heldout-13",("posterior_uninformed",)),
    ("heldout-14",()),
    ("heldout-15",("benign_control",)),
    ("heldout-16",("budget_nonconservation",)),
    ("heldout-17",("gain_zero","stop_when_negative")),
    ("heldout-18",("posterior_uninformed","budget_nonconservation")),
)
