"""Source-owned independent BFS evidence for a five-edge, two-route graph.

No learner imports this module. The source defines topology and heldout truth,
not an implementation of the learner's Boolean macro language.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

SOURCE_REVISION = "motif.reason.eight.five-edge-source.v1"
TRAIN_MASKS = (3, 5, 6, 7, 24)
WITHHELD_MASKS = tuple(x for x in range(32) if x not in TRAIN_MASKS)
TOPOLOGY = "DIRECTED_THREE_HOP_OR_TWO_HOP"
VARIANTS = ("cedar", "quartz", "willow")


@dataclass(frozen=True)
class Case:
    mask: int
    variant: str = "cedar"
    topology: str = TOPOLOGY

    def __post_init__(self):
        if (type(self.mask) is not int or not 0 <= self.mask < 32
                or self.variant not in VARIANTS or self.topology != TOPOLOGY):
            raise ValueError("Source-owned graph topology or feature domain changed")

    @property
    def nodes(self):
        return {
            "cedar": ("S", "A", "B", "C", "T"),
            "quartz": ("Q", "J", "K", "L", "R"),
            "willow": ("W", "P", "X", "Y", "Z"),
        }[self.variant]

    @property
    def edges(self):
        s,a,b,c,t = self.nodes
        return ((s,a),(a,b),(b,t),(s,c),(c,t))

    @property
    def features(self):
        return tuple(int(bool(self.mask & (1 << j))) for j in range(5))


def bfs_truth(case):
    """Independent classical traversal. The Boolean formula is not invoked."""
    if not isinstance(case, Case):
        raise ValueError("Unknown source-owned case")
    nodes = case.nodes
    active = {node: [] for node in nodes}
    for enabled, (a,b) in zip(case.features, case.edges):
        if enabled:
            active[a].append(b)
    seen = {nodes[0]}
    queue = deque([nodes[0]])
    while queue:
        current = queue.popleft()
        if current == nodes[-1]:
            return True
        for neighbor in sorted(active[current]):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return False


def observable(mask):
    case = Case(mask)
    return {
        "schema": "motif.reason.eight.public-source-observation.v1",
        "mask": case.mask,
        "features": list(case.features),
        "reachable": bfs_truth(case),
        "source_revision": SOURCE_REVISION,
        "source_type": "SYNTHETIC_BFS_NOT_REAL_WORLD_EVIDENCE",
        "real_world_authority": False,
    }


def lessons():
    return tuple(observable(m) for m in TRAIN_MASKS)


def certification():
    return tuple(Case(m) for m in WITHHELD_MASKS)


def deployment(size):
    if type(size) is not int or not 1 <= size <= 64:
        raise ValueError("Bounded prospective workload")
    return tuple(Case(i % 32, "quartz" if i < 32 else "willow")
                 for i in range(size))


if __name__ == "__main__":
    import json
    print(json.dumps({
        "source_revision": SOURCE_REVISION,
        "teaching": list(lessons()),
        "holdout_count": len(certification()),
    }, indent=2))
