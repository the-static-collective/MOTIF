"""RING-014 post-FREEZE unfamiliar source-mutation cases.

Only trial.py loads these specs AFTER verifying the calibration receipt,
reviewed original source fingerprints and exact Docker image identity.

Mutations change reviewed Python code copies only. Every correctness signal
comes from executing the REAL source-owned tests, not an authored fake test
status. Seeded mutation labels evaluate detection sensitivity afterward.

Same author created both train and heldout mutations; the heldout cases
are new to the parameter search but NOT independently sourced software bugs.
"""
from __future__ import annotations

CASES=(
    ("unseen-000",()),
    ("unseen-001",("posterior_uninformed",)),
    ("unseen-002",()),
    ("unseen-003",("stop_floor_broken",)),
    ("unseen-004",("gain_zero",)),
    ("unseen-005",()),
    ("unseen-006",("excess_permission",)),
    ("unseen-007",("budget_nonconservation",)),
    ("unseen-008",()),
    ("unseen-009",("invalid_import",)),
    ("unseen-010",()),
    ("unseen-011",("source_overclaim",)),
)
