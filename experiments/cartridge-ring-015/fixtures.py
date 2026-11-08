"""RING-015: independently scoped, reviewed source mutations and benign edits.

The selector does not see artificial defect labels. It sees only real
read-only source inspections and executable test outcomes. Our fixture
generator copies unchanged RING-013 Python and makes exact anchored
test-only edits; original GitHub sources never change.

A *changed* region is not identical to a defect: benign math/control edits
are included as negative controls. Heldout cases live in sealed.py and
are not imported by training / policy selection.
"""
from __future__ import annotations
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"cartridge-ring-014"))
import fixtures as base

SOURCE=base.SOURCE
PATCHES={
    **base.PATCHES,
    "benign_math":(
        ('w:belief[w]*action["signal_distribution"][w].get(signal,0.0)',
         'w:(1.0*belief[w])*action["signal_distribution"][w].get(signal,0.0)'),
    ),
    "benign_control":(
        ('budget-=action["budget_units"]',
         'budget=budget-action["budget_units"]'),
    ),
    "benign_information":(
        ('return max(0.0,prior-after)',
         'return max(0.0,prior-after)+0.0'),
    ),
}
# Set of known test-only edits. In a real deployment, changes can be
# arbitrary and a static region tag cannot authenticate correctness.
base.PATCHES.update({
    key:val for key,val in PATCHES.items() if key not in base.PATCHES})

TRAIN=(
    ("train-01",("posterior_signal",)),
    ("train-02",("budget_accounting",)),
    ("train-03",("entropy_sign",)),
    ("train-04",("stop_when_negative",)),
    ("train-05",("benign_math",)),
    ("train-06",("benign_control",)),
    ("train-07",("benign_information",)),
    ("train-08",("source_overclaim",)),
    ("train-09",()),
    ("train-10",("forbidden_ranking",)),
    ("train-11",("invalid_import",)),
    ("train-12",("posterior_uninformed",)),
)
DEV=(
    ("dev-01",("gain_zero",)),
    ("dev-02",("stop_floor_broken",)),
    ("dev-03",("benign_math",)),
    ("dev-04",("benign_control",)),
    ("dev-05",()),
    ("dev-06",("budget_nonconservation",)),
)
SEVERE=frozenset(PATCHES)-{
    "benign_math","benign_control","benign_information"}

def make(root,repo,specs):
    if not all(isinstance(changes,tuple) and
               all(x in PATCHES for x in changes)
               for _,changes in specs):
        raise ValueError("Unknown, unreviewed change")
    output=base.make(root,repo,specs)
    for row in output:
        row["seeded_defect"]=any(
            x in SEVERE for x in
            row["mutation_labels_visible_only_to_calibration_and_scorer"])
        row["benign_edit"]=bool(
            row["intentional_defect"] and not row["seeded_defect"])
        row["hidden_mutation_labels_not_visible_to_selector"]=True
    return output

def source_root(repo):
    return base.root_for_source(repo)
