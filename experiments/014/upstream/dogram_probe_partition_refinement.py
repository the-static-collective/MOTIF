from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Mapping


ProbeValue = Hashable


@dataclass(frozen=True)
class ProbePartitionRefinementReceipt:
    states: tuple[str, ...]
    partitions: dict[str, tuple[tuple[str, ...], ...]]
    cover_relations: tuple[tuple[str, str], ...]
    separating_probes: tuple[str, ...]
    minimal_separators: tuple[str, ...]


def _require_hashable(value: ProbeValue) -> None:
    try:
        hash(value)
    except TypeError as exc:
        raise ValueError("probe outputs must be hashable") from exc


def _partition(states: tuple[str, ...], outputs: tuple[ProbeValue, ...]) -> tuple[tuple[str, ...], ...]:
    blocks: dict[ProbeValue, list[str]] = {}
    for state, output in zip(states, outputs):
        _require_hashable(output)
        blocks.setdefault(output, []).append(state)
    return tuple(tuple(block) for block in blocks.values())


def factorization_map(
    stronger_outputs: tuple[ProbeValue, ...],
    weaker_outputs: tuple[ProbeValue, ...],
) -> tuple[tuple[ProbeValue, ProbeValue], ...] | None:
    """Return the deterministic map witnessing that weaker factors through stronger.

    A witness exists exactly when equal stronger outputs always imply equal weaker
    outputs. The result is a finite output-to-output map. This receipts only the
    declared information refinement; it makes no claim about evidence or truth.
    """

    if len(stronger_outputs) != len(weaker_outputs):
        raise ValueError("probe output tuples must have equal length")

    witness: dict[ProbeValue, ProbeValue] = {}
    for stronger, weaker in zip(stronger_outputs, weaker_outputs):
        _require_hashable(stronger)
        _require_hashable(weaker)
        if stronger in witness and witness[stronger] != weaker:
            return None
        witness[stronger] = weaker
    return tuple(sorted(witness.items(), key=lambda item: repr(item[0])))


def probe_refines(
    stronger_outputs: tuple[ProbeValue, ...],
    weaker_outputs: tuple[ProbeValue, ...],
) -> bool:
    """Return whether the partition induced by stronger refines weaker."""

    return factorization_map(stronger_outputs, weaker_outputs) is not None


def analyze_probe_family(
    states: tuple[str, ...],
    probes: Mapping[str, tuple[ProbeValue, ...]],
    target_pair: tuple[str, str],
) -> ProbePartitionRefinementReceipt:
    """Analyze a finite deterministic probe family as a partition-refinement poset.

    Probe names are treated as declared decoder choices. Equal outputs induce an
    equivalence relation on the finite state set. Refinement is tested by exact
    deterministic factorization, and minimal separators are minimal only within
    the supplied probe family.
    """

    if not states or len(set(states)) != len(states):
        raise ValueError("states must be nonempty and unique")
    if len(target_pair) != 2 or target_pair[0] == target_pair[1]:
        raise ValueError("target_pair must contain two distinct states")
    if any(state not in states for state in target_pair):
        raise ValueError("target_pair states must belong to states")
    if not probes:
        raise ValueError("at least one probe is required")

    probe_items = tuple(probes.items())
    for name, outputs in probe_items:
        if not isinstance(name, str) or not name:
            raise ValueError("probe names must be nonempty strings")
        if len(outputs) != len(states):
            raise ValueError("each probe must provide one output per state")
        for output in outputs:
            _require_hashable(output)

    partitions = {name: _partition(states, outputs) for name, outputs in probe_items}
    normalized = tuple(partitions.values())
    if len(set(normalized)) != len(normalized):
        raise ValueError("probe family must not contain duplicate induced partitions")

    strict_refinements: list[tuple[str, str]] = []
    for stronger_name, stronger_outputs in probe_items:
        for weaker_name, weaker_outputs in probe_items:
            if stronger_name == weaker_name:
                continue
            if probe_refines(stronger_outputs, weaker_outputs):
                strict_refinements.append((stronger_name, weaker_name))

    cover_relations: list[tuple[str, str]] = []
    for stronger_name, weaker_name in strict_refinements:
        has_middle = any(
            middle_name not in (stronger_name, weaker_name)
            and (stronger_name, middle_name) in strict_refinements
            and (middle_name, weaker_name) in strict_refinements
            for middle_name, _ in probe_items
        )
        if not has_middle:
            cover_relations.append((stronger_name, weaker_name))

    state_index = {state: index for index, state in enumerate(states)}
    left_index = state_index[target_pair[0]]
    right_index = state_index[target_pair[1]]
    separating_probes = tuple(
        name
        for name, outputs in probe_items
        if outputs[left_index] != outputs[right_index]
    )

    minimal_separators = tuple(
        name
        for name in separating_probes
        if not any(
            other != name
            and other in separating_probes
            and (name, other) in strict_refinements
            for other, _ in probe_items
        )
    )

    return ProbePartitionRefinementReceipt(
        states=states,
        partitions=partitions,
        cover_relations=tuple(cover_relations),
        separating_probes=separating_probes,
        minimal_separators=minimal_separators,
    )


__all__ = [
    "ProbePartitionRefinementReceipt",
    "analyze_probe_family",
    "factorization_map",
    "probe_refines",
]
