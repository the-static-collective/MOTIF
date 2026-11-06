"""LEGIT-005 independent finite classical truth-table reference.

This solver does NOT import LEGIT-003 or LEGIT-005 countermodel execution.
It enumerates *every* possible binary latent-state assignment in tiny source
cells, constrained only by synthetic certified label counts. The universal
and possibility questions are classical logical duals over this finite family.

This is a strong exact independent algorithmic check, but its author is the
same assistant and the data are synthetic, not externally investigator-blind.
"""
from __future__ import annotations

from itertools import product


def _cell_truth_possibilities(observed,positive,negative):
    assert type(observed) is int and 0<=observed<=8
    values=set()
    for assignments in product((False,True), repeat=observed):
        truth=sum(assignments)
        if truth>=positive and observed-truth>=negative:
            values.add(truth)
    if not values:
        raise AssertionError("Inconsistent synthetic oracle constraints")
    return values


def reference_oracle(raw,kind):
    if kind not in ("U_NEG","CAN_NEG","U_POS","CAN_POS"):
        raise ValueError("Unknown logical operation")
    negative=kind.endswith("NEG")
    group_key="negative" if negative else "positive"
    anchor={(r["group"],r["proxy"]):r for r in raw["anchors"]}
    all_options=[]
    observed_total=0
    for row in raw["observations"]:
        count=row[group_key]
        observed_total+=count
        approved=anchor.get((row["group"],group_key),{})
        true_known=approved.get("known_latent_true",0)
        false_known=approved.get("known_latent_false",0)
        true_possible=_cell_truth_possibilities(count,true_known,false_known)
        # A violating individual is target-present with negative observation,
        # or target-absent with positive observation.
        violations={x if negative else count-x for x in true_possible}
        all_options.append(violations)
    if observed_total==0:
        return None
    possible_violation=any(max(options)>0 for options in all_options)
    if kind.startswith("U_"):
        return not possible_violation
    return possible_violation
