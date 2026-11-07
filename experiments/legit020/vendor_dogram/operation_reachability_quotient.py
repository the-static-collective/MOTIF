from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable


@dataclass(frozen=True)
class OperationReachabilityReceipt:
    states: tuple[str, ...]
    operations: tuple[str, ...]
    collapse_classes: tuple[tuple[str, ...], ...]
    exact_factorization: bool
    ambiguous_classes: tuple[tuple[str, ...], ...]
    lost_operation_questions: tuple[tuple[str, str, str, bool, bool], ...]


def analyze_operation_reachability(
    states: tuple[str, ...],
    collapsed_projection: tuple[Hashable, ...],
    operations: tuple[str, ...],
    enabled: tuple[tuple[bool, ...], ...],
) -> OperationReachabilityReceipt:
    """Check whether enabled-operation questions factor through a state collapse.

    Exact preservation requires every operation's enabledness to be constant on
    every collapse fiber. This receipts only the declared finite operation family;
    it does not infer occurrence, evidence, causality, importance, or authority.
    """
    if not states or len(set(states)) != len(states):
        raise ValueError("states must be nonempty and unique")
    if len(collapsed_projection) != len(states):
        raise ValueError("collapsed_projection must provide one value per state")
    if len(set(operations)) != len(operations):
        raise ValueError("operations must be unique")
    if len(enabled) != len(states) or any(len(row) != len(operations) for row in enabled):
        raise ValueError("enabled must be a state-by-operation boolean matrix")
    if any(type(value) is not bool for row in enabled for value in row):
        raise ValueError("enabled entries must be exact booleans")

    fibers: list[tuple[str, ...]] = []
    fiber_indices: list[tuple[int, ...]] = []
    seen: list[Hashable] = []
    for value in collapsed_projection:
        if any(value == prior for prior in seen):
            continue
        seen.append(value)
        idx = tuple(j for j, other in enumerate(collapsed_projection) if other == value)
        fiber_indices.append(idx)
        fibers.append(tuple(states[j] for j in idx))

    ambiguous: list[tuple[str, ...]] = []
    lost: list[tuple[str, str, str, bool, bool]] = []
    for fiber, idx in zip(fibers, fiber_indices):
        fiber_ambiguous = False
        for op_index, operation in enumerate(operations):
            values = {enabled[j][op_index] for j in idx}
            if len(values) > 1:
                fiber_ambiguous = True
                for left_pos, left in enumerate(idx):
                    for right in idx[left_pos + 1 :]:
                        if enabled[left][op_index] != enabled[right][op_index]:
                            lost.append((states[left], states[right], operation, enabled[left][op_index], enabled[right][op_index]))
        if fiber_ambiguous:
            ambiguous.append(fiber)

    return OperationReachabilityReceipt(
        states=states,
        operations=operations,
        collapse_classes=tuple(fibers),
        exact_factorization=not ambiguous,
        ambiguous_classes=tuple(ambiguous),
        lost_operation_questions=tuple(lost),
    )


__all__ = ["OperationReachabilityReceipt", "analyze_operation_reachability"]
