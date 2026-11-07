from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

from .probe_partition_refinement import factorization_map


ProjectionValue = Hashable


@dataclass(frozen=True)
class AntiCollapseReachabilityReceipt:
    states: tuple[str, ...]
    lawful_quotient: bool
    factorization_witness: tuple[tuple[ProjectionValue, ProjectionValue], ...] | None
    collapse_classes: tuple[tuple[str, ...], ...]
    preserved_distinctions: tuple[tuple[str, str], ...]
    lost_distinctions: tuple[tuple[str, str], ...]


def _collapse_classes(
    states: tuple[str, ...],
    outputs: tuple[ProjectionValue, ...],
) -> tuple[tuple[str, ...], ...]:
    remaining = set(range(len(states)))
    classes: list[tuple[str, ...]] = []
    for index in range(len(states)):
        if index not in remaining:
            continue
        block = tuple(
            states[other]
            for other in range(index, len(states))
            if other in remaining and outputs[other] == outputs[index]
        )
        for other in range(index, len(states)):
            if other in remaining and outputs[other] == outputs[index]:
                remaining.remove(other)
        classes.append(block)
    return tuple(classes)


def analyze_collapse(
    states: tuple[str, ...],
    rich_projection: tuple[ProjectionValue, ...],
    collapsed_projection: tuple[ProjectionValue, ...],
) -> AntiCollapseReachabilityReceipt:
    """Receipt distinguishability lost by a declared deterministic collapse.

    The collapsed projection is lawful only when it deterministically factors
    through the richer projection. Pairwise loss is then measured only among
    distinctions visible in the richer projection. This reports information
    loss under the declared projections; it does not grade importance, meaning,
    evidence, causality, or ontology.
    """

    if not states or len(set(states)) != len(states):
        raise ValueError("states must be nonempty and unique")
    if len(rich_projection) != len(states) or len(collapsed_projection) != len(states):
        raise ValueError("each projection must provide one output per state")

    witness = factorization_map(rich_projection, collapsed_projection)
    lawful = witness is not None
    classes = _collapse_classes(states, collapsed_projection)

    if not lawful:
        return AntiCollapseReachabilityReceipt(
            states=states,
            lawful_quotient=False,
            factorization_witness=None,
            collapse_classes=classes,
            preserved_distinctions=(),
            lost_distinctions=(),
        )

    preserved: list[tuple[str, str]] = []
    lost: list[tuple[str, str]] = []
    for left in range(len(states)):
        for right in range(left + 1, len(states)):
            if rich_projection[left] == rich_projection[right]:
                continue
            pair = (states[left], states[right])
            if collapsed_projection[left] == collapsed_projection[right]:
                lost.append(pair)
            else:
                preserved.append(pair)

    return AntiCollapseReachabilityReceipt(
        states=states,
        lawful_quotient=True,
        factorization_witness=witness,
        collapse_classes=classes,
        preserved_distinctions=tuple(preserved),
        lost_distinctions=tuple(lost),
    )


__all__ = ["AntiCollapseReachabilityReceipt", "analyze_collapse"]
