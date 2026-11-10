"""CONFLUENCE-003 independent, source-pinned Moving AI gridworld adapter.

Data and scenario labels originate outside MOTIF. This adapter is authored here.
A* and Dijkstra have the same complete map information. Neither is learning.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from heapq import heappop, heappush
from math import hypot, sqrt
from pathlib import Path
from itertools import count
import subprocess
import json

ROOT = Path(__file__).resolve().parents[2]
THIRD = ROOT / "sources" / "gridbenchmark"
UPSTREAM_COMMIT = "ffa02393942e649d4da82d5647d3159e7a7dd572"
UPSTREAM_REPOSITORY = "ovunctuzel/GridWorldPathfinding"
BLOBS = {
    "tiny.map": "1ce59371919e079d14e5e0452697dbcc11b22696",
    "tiny.map.scen": "ae3f14aa9c5225f186e99667687b51728bb2a53b",
    "dragonage.map": "8d9046881cf55b280ede28a90e2ab134f59f67c2",
    "dragonage.map.scen": "099c97e3bf29526a41e2bac0a594ec35efebc07b",
}
SOURCE_NAMES = {"tiny": "lak110d.map", "dragonage": "lak103d.map"}
DELTAS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1),
          (1, -1), (1, 0), (1, 1))


def digest(value):
    return sha256(json.dumps(value, separators=(",", ":"), sort_keys=True,
                             allow_nan=False).encode()).hexdigest()


def verified_root():
    if not THIRD.is_dir():
        raise RuntimeError("MISSING_INDEPENDENT_SOURCE_CHECKOUT")
    revision = subprocess.check_output(["git", "-C", str(THIRD),
                                        "rev-parse", "HEAD"], text=True).strip()
    if revision != UPSTREAM_COMMIT:
        raise RuntimeError("CHANGED_INDEPENDENT_SOURCE_REVISION")
    for name, expected in BLOBS.items():
        path = THIRD / "benchmarks" / name
        if not path.is_file():
            raise RuntimeError("MISSING_INDEPENDENT_FILE_" + name)
        found = subprocess.check_output(["git", "-C", str(THIRD), "hash-object",
                                         str(path)], text=True).strip()
        if found != expected:
            raise RuntimeError("SOURCE_FILE_MODIFIED_" + name)
    return revision


@dataclass(frozen=True)
class Scene:
    bucket: int
    source_line: int
    start: tuple[int, int]
    goal: tuple[int, int]
    oracle_length: float  # evaluator only; never fed to the planning policy.


@dataclass(frozen=True)
class Grid:
    label: str
    rows: tuple[str, ...]

    @property
    def height(self):
        return len(self.rows)

    @property
    def width(self):
        return len(self.rows[0])

    def in_bounds(self, point):
        x, y = point
        return 0 <= x < self.width and 0 <= y < self.height

    def open(self, point, blocked=frozenset()):
        if not self.in_bounds(point) or point in blocked:
            return False
        return self.rows[point[1]][point[0]] == "."

    def neighbors(self, point, blocked=frozenset()):
        x, y = point
        for dx, dy in DELTAS:
            nxt = (x + dx, y + dy)
            if not self.open(nxt, blocked):
                continue
            if dx and dy and (not self.open((x + dx, y), blocked)
                              or not self.open((x, y + dy), blocked)):
                continue
            yield nxt, sqrt(2) if dx and dy else 1.0


def parse_map(name, content):
    rows = content.splitlines()
    if len(rows) < 5 or rows[0] != "type octile" or not rows[1].startswith("height "):
        raise ValueError("UNSUPPORTED_INDEPENDENT_MAP_HEADER")
    height, width = int(rows[1].split()[1]), int(rows[2].split()[1])
    if rows[3] != "map" or len(rows[4:]) != height:
        raise ValueError("MAP_SHAPE_MISMATCH")
    if not 0 < width <= 512 or not 0 < height <= 512:
        raise ValueError("UNSUPPORTED_MAP_SIZE")
    if any(len(r) != width or set(r) - set(".@T") for r in rows[4:]):
        raise ValueError("UNSUPPORTED_TERRAIN_OR_WIDTH")
    return Grid(name, tuple(rows[4:]))


def parse_scenarios(map_name, grid, content):
    rows = content.splitlines()
    if not rows or rows[0].strip() not in ("version 1", "version 1.0"):
        raise ValueError("UNSUPPORTED_SCENARIO_VERSION")
    scene = []
    for index, line in enumerate(rows[1:], start=2):
        fields = line.split()
        if len(fields) != 9:
            raise ValueError("INVALID_SCENARIO")
        bucket, source_name, w, h, sx, sy, gx, gy, length = fields
        if (not source_name.endswith("/" + SOURCE_NAMES[map_name])
                or int(w) != grid.width or int(h) != grid.height):
            raise ValueError("SCENARIO_MAP_MISMATCH")
        start, goal = (int(sx), int(sy)), (int(gx), int(gy))
        if not grid.open(start) or not grid.open(goal):
            raise ValueError("SOURCE_SCENARIO_IMPASSABLE_ENDPOINT")
        scene.append(Scene(int(bucket), index, start, goal, float(length)))
    return tuple(scene)


def load_map_and_scenarios(name):
    if name not in SOURCE_NAMES:
        raise ValueError("NO_EXTERNAL_DOMAIN_CONTRACT")
    verified_root()
    folder = THIRD / "benchmarks"
    grid = parse_map(name, (folder / (name + ".map")).read_text())
    rows = parse_scenarios(name, grid,
                           (folder / (name + ".map.scen")).read_text())
    return grid, rows


def deterministic_cohort(name, scenarios):
    selected = []
    for bucket in (0, 2, 4, 6):
        options = [s for s in scenarios if s.bucket == bucket]
        if len(options) < 2:
            raise RuntimeError("INDEPENDENT_BUCKET_TOO_SMALL")
        def key(s):
            # Never use the third-party optimal distance label in selection.
            return digest([name, s.source_line, s.start, s.goal])
        selected.extend(sorted(options, key=key)[:2])
    assert len(selected) == 8
    return tuple(selected)


def octile(a, b):
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return max(dx, dy) + (sqrt(2) - 1) * min(dx, dy)


def astar(grid, start, goal, blocked=frozenset()):
    """Conventional full-map A*, admissible 8-neighbor octile heuristic."""
    if not grid.open(start, blocked) or not grid.open(goal, blocked):
        return None
    heap = [(octile(start, goal), 0.0, start)]
    cost, parent = {start: 0.0}, {}
    visited, expanded = set(), 0
    while heap:
        _, dist, pos = heappop(heap)
        if pos in visited or dist > cost[pos] + 1e-10:
            continue
        visited.add(pos)
        expanded += 1
        if pos == goal:
            path = [pos]
            while pos in parent:
                pos = parent[pos]
                path.append(pos)
            return tuple(reversed(path)), dist, expanded
        for nxt, weight in grid.neighbors(pos, blocked):
            new = dist + weight
            if new + 1e-10 < cost.get(nxt, float("inf")):
                cost[nxt], parent[nxt] = new, pos
                heappush(heap, (new + octile(nxt, goal), new, nxt))
    return None


def dijkstra(grid, start, goal, blocked=frozenset()):
    """Separate classical no-heuristic shortest-path oracle."""
    if not grid.open(start, blocked) or not grid.open(goal, blocked):
        return None
    q = [(0.0, start)]
    best = {start: 0.0}
    seen = set()
    prev = {}
    expanded = 0
    while q:
        d, p = heappop(q)
        if p in seen:
            continue
        seen.add(p)
        expanded += 1
        if p == goal:
            out = [p]
            while p in prev:
                p = prev[p]
                out.append(p)
            return tuple(reversed(out)), d, expanded
        for n, step in grid.neighbors(p, blocked):
            candidate = d + step
            if candidate + 1e-10 < best.get(n, float("inf")):
                best[n], prev[n] = candidate, p
                heappush(q, (candidate, n))
    return None


def check_route(grid, path, blocked=frozenset()):
    if not path or any(not grid.open(p, blocked) for p in path):
        return None
    total = 0.0
    for source, target in zip(path, path[1:]):
        options = dict(grid.neighbors(source, blocked))
        if target not in options:
            return None
        total += options[target]
    return total


class GridOwner:
    """Third-party immutable map + one explicitly separate simulated revision."""

    def __init__(self, grid):
        self.grid = grid
        self.blocked = frozenset()
        self.epoch = 0
        self.issued = []
        self.origin = "ONE_GRIDBENCHMARK_CORPUS"
        self._revision_history = [self.blocked]

    def observe(self, key):
        if not self.grid.in_bounds(key):
            raise ValueError("UNREVIEWED_SENSOR_CELL")
        body = dict(schema="motif.confluence003.grid-observation.v1",
                    kind="SOURCE_OBSERVATION", key=list(key),
                    answer=self.grid.open(key, self.blocked),
                    source_revision=UPSTREAM_COMMIT, epoch=self.epoch,
                    origin=self.origin, source_type=("ORIGINAL_PUBLISHED_MAP"
                                                      if self.epoch == 0
                                                      else "CONTROLLED_SHIFT_ON_PUBLISHED_MAP"))
        packet = {**body, "sha256": digest(body)}
        self.issued.append(deepcopy(packet))
        return packet

    def verify(self, packet):
        if not isinstance(packet, dict) or packet not in self.issued:
            return False
        body = {k: v for k, v in packet.items() if k != "sha256"}
        if packet.get("sha256") != digest(body):
            return False
        if (packet.get("source_revision") != UPSTREAM_COMMIT
                or packet.get("origin") != self.origin
                or packet.get("kind") != "SOURCE_OBSERVATION"):
            return False
        epoch = packet.get("epoch")
        if type(epoch) is not int or not 0 <= epoch < len(self._revision_history):
            return False
        key = packet.get("key")
        if (type(key) is not list or len(key) != 2
                or any(type(v) is not int for v in key)):
            return False
        return (packet.get("answer") ==
                self.grid.open(tuple(key), self._revision_history[epoch]))

    def shift_block(self, target):
        if not self.grid.open(target, self.blocked):
            raise ValueError("CANNOT_BLOCK_NONPASSABLE")
        self.blocked = self.blocked | {target}
        self.epoch += 1
        self._revision_history.append(self.blocked)

    def route_reality(self, path):
        """Evaluated against CURRENT grid state, never a prior proposal."""
        return check_route(self.grid, path, self.blocked)

    def check(self):
        return all(self.verify(receipt) for receipt in self.issued)
