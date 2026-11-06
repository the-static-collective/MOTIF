"""REASON-007 synthetic source owner: independent graph mathematics.

No compiler/market imports here. Label oracle is explicitly classical BFS,
not a private model, real-world fact, third-party sensor or neural teacher.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

SOURCE_REVISION = "reason-007-four-edge-graph-source-v1"
TRAIN = (0, 3, 5, 10, 12)
CERT = tuple(n for n in range(16) if n not in TRAIN)
VARIANTS = ("cedar", "quartz", "willow")


@dataclass(frozen=True)
class Case:
    mask: int
    variant: str = "cedar"

    def __post_init__(self):
        if type(self.mask) is not int or not 0 <= self.mask < 16:
            raise ValueError("Only four-bit source feature vectors admitted")
        if self.variant not in VARIANTS:
            raise ValueError("Unknown fixture variant")

    @property
    def features(self):
        return tuple(int(bool(self.mask & (1 << i))) for i in range(4))

    @property
    def nodes(self):
        return {"cedar": ("S","A","B","T"),
                "quartz": ("Q","J","K","R"),
                "willow": ("W","P","X","Z")}[self.variant]

    @property
    def edges(self):
        s,a,b,t = self.nodes
        return ((s,a),(a,t),(s,b),(b,t))


def bfs_truth(case):
    """Independent evaluator; not implemented using the pupil's DNF language."""
    if not isinstance(case, Case):
        raise ValueError("Only source-owned graph fixtures")
    nodes = case.nodes
    graph = {n: [] for n in nodes}
    for present, (a,b) in zip(case.features, case.edges):
        if present:
            graph[a].append(b)
    queue = deque([nodes[0]])
    seen = {nodes[0]}
    while queue:
        node = queue.popleft()
        if node == nodes[-1]:
            return True
        for nxt in sorted(graph[node]):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return False


def observation(mask):
    """Teaching labels have source semantics but no real-world authenticity."""
    c = Case(mask)
    return {"mask": mask, "reachable": bfs_truth(c),
            "source_revision": SOURCE_REVISION,
            "kind": "SYNTHETIC_CLASSICAL_GRAPH_RESULT",
            "real_world_authority": False}


def training():
    return tuple(observation(mask) for mask in TRAIN)


def withheld():
    return tuple(observation(mask) for mask in CERT)


def deployment(n):
    if type(n) is not int or not 1 <= n <= 32:
        raise ValueError("Bounded deployment set")
    return tuple(Case(mask, VARIANTS[1 + i // 16])
                 for i, mask in enumerate((j % 16 for j in range(n))))


if __name__ == "__main__":
    import json
    print(json.dumps({"train": list(training()), "cert": list(withheld()),
                      "source_revision": SOURCE_REVISION}, indent=2))
