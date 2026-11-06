"""MOTIF GEOM-001: an exact, bounded flower-of-life reasoning cartridge.

The flower is a triangular lattice of equal-radius circles. Circle *centers*
are observed only when explicitly supplied. Suggested centers are hypotheses,
never retroactively added to the observations or treated as permissions.
Python 3.10+, standard library only.
"""
from collections import deque
import heapq
from itertools import combinations
from math import hypot, sqrt
from typing import Iterable

Coord = tuple[int, int]
DIRECTIONS: tuple[Coord, ...] = (
    (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)
)
EPS = 1e-8


def hex_distance(a: Coord, b: Coord = (0, 0)) -> int:
    """Minimum number of nearest-neighbor steps on the triangular lattice."""
    dq, dr = a[0] - b[0], a[1] - b[1]
    return max(abs(dq), abs(dr), abs(dq + dr))


def flower(rings: int) -> tuple[Coord, ...]:
    """Hexagonal patch: 1, 7, 19, 37 ... equal-radius circle centers."""
    if not isinstance(rings, int) or rings < 0:
        raise ValueError("rings must be a nonnegative integer")
    return tuple(sorted(
        ((q, r) for q in range(-rings, rings + 1)
         for r in range(-rings, rings + 1)
         if hex_distance((q, r)) <= rings),
        key=lambda p: (hex_distance(p), p[0], p[1]),
    ))


def to_xy(coord: Coord, radius: float = 1.0) -> tuple[float, float]:
    """Centers one circle-radius apart along six directions."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    q, r = coord
    return (radius * (q + r / 2), radius * sqrt(3) * r / 2)


def from_xy(x: float, y: float, radius: float = 1.0,
            tolerance: float = 1e-7) -> Coord | None:
    """Snap to an anchored, unrotated lattice or explicitly refuse a fit."""
    if radius <= 0 or tolerance < 0:
        raise ValueError("invalid radius or tolerance")
    rf = 2 * y / (sqrt(3) * radius)
    qf = x / radius - rf / 2
    result = (round(qf), round(rf))
    return result if hypot(
        x - to_xy(result, radius)[0], y - to_xy(result, radius)[1]
    ) <= tolerance * radius else None


def rotate60(coord: Coord) -> Coord:
    """An exact 60-degree rotation of axial lattice coordinates."""
    q, r = coord
    return (-r, q + r)


def edges(centers: Iterable[Coord]) -> tuple[tuple[Coord, Coord], ...]:
    nodes = set(centers)
    return tuple(sorted(
        (a, b) for a in nodes for dq, dr in DIRECTIONS
        if (b := (a[0] + dq, a[1] + dr)) in nodes and a < b
    ))


def circle_intersections(a: tuple[float, float],
                         b: tuple[float, float],
                         radius: float) -> tuple[tuple[float, float], ...]:
    """Finite equal-radius intersections. Coincident circles abstain."""
    if radius <= 0:
        raise ValueError("radius must be positive")
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = hypot(dx, dy)
    if d < EPS * radius or d > 2 * radius + EPS * radius:
        return ()
    midpoint = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    altitude = sqrt(max(0.0, radius ** 2 - (d / 2) ** 2))
    ux, uy = -dy / d, dx / d
    if altitude <= EPS * radius:
        return (midpoint,)
    return tuple(sorted((
        (midpoint[0] + altitude * ux, midpoint[1] + altitude * uy),
        (midpoint[0] - altitude * ux, midpoint[1] - altitude * uy),
    )))


def propose_centers(observed: Iterable[Coord], max_ring: int,
                    radius: float = 1.0) -> list[dict]:
    """Geometrically propose (do not assert) centers supported by two circles.

    Each proposal is obtained by intersecting two *observed* circles,
    then checking exact lattice alignment and the declared finite search area.
    """
    if max_ring < 0:
        raise ValueError("max_ring must be nonnegative")
    nodes = set(observed)
    allowed = set(flower(max_ring))
    if not nodes <= allowed:
        raise ValueError("observed center outside declared finite field")
    parents: dict[Coord, set[tuple[Coord, Coord]]] = {}
    for a, b in combinations(sorted(nodes), 2):
        if hex_distance(a, b) > 2:
            continue
        for x, y in circle_intersections(to_xy(a, radius), to_xy(b, radius), radius):
            candidate = from_xy(x, y, radius)
            if candidate is not None and candidate in allowed and candidate not in nodes:
                parents.setdefault(candidate, set()).add((a, b))
    proposals = []
    for c, pairs in parents.items():
        neighbors = sum(
            (c[0] + dq, c[1] + dr) in nodes for dq, dr in DIRECTIONS
        )
        potential = sum(
            (c[0] + dq, c[1] + dr) in allowed
            and (c[0] + dq, c[1] + dr) not in nodes
            for dq, dr in DIRECTIONS
        )
        proposals.append({
            "center": list(c),
            "supporting_pairs": len(pairs),
            "observed_neighbors": neighbors,
            "modeled_unseen_neighbors": potential,
            "status": "PROPOSAL_ONLY",
        })
    return sorted(
        proposals,
        key=lambda x: (-x["observed_neighbors"],
                       -x["supporting_pairs"], tuple(x["center"])),
    )


def pathfind(centers: Iterable[Coord], start: Coord, goal: Coord,
             blocked: Iterable[Coord] = (),
             missing_edges: Iterable[tuple[Coord, Coord]] = (),
             geometry_heuristic: bool = True) -> dict:
    """A* versus the exact same Dijkstra/zero-heuristic search.

    Both use only the explicitly observed graph. No inferred center is added.
    The hex-distance heuristic is consistent and admissible for unit edges.
    """
    active = set(centers) - set(blocked)
    if start not in active or goal not in active:
        return {"status": "HOLD", "reason": "endpoint not observed/available",
                "path": [], "expanded": 0}
    forbidden = {frozenset(pair) for pair in missing_edges}
    best = {start: 0}
    previous: dict[Coord, Coord] = {}
    counter = 0
    def heuristic(p: Coord) -> int:
        return hex_distance(p, goal) if geometry_heuristic else 0
    queue = [(heuristic(start), heuristic(start), counter, 0, start)]
    expanded = 0
    while queue:
        _, _, _, cost, current = heapq.heappop(queue)
        if cost != best.get(current):
            continue
        expanded += 1
        if current == goal:
            path = [goal]
            while path[-1] != start:
                path.append(previous[path[-1]])
            path.reverse()
            return {"status": "PATH", "path": [list(c) for c in path],
                    "distance": cost, "expanded": expanded}
        for dq, dr in DIRECTIONS:
            nxt = (current[0] + dq, current[1] + dr)
            if nxt not in active or frozenset((current, nxt)) in forbidden:
                continue
            newcost = cost + 1
            if newcost < best.get(nxt, float("inf")):
                previous[nxt] = current
                best[nxt] = newcost
                counter += 1
                h = heuristic(nxt)
                heapq.heappush(queue, (newcost + h, h, counter, newcost, nxt))
    return {"status": "HOLD", "reason": "no witnessed route",
            "path": [], "expanded": expanded}


def svg_flower(centers: Iterable[Coord], proposed: Iterable[Coord] = (),
               radius: float = 28.0) -> str:
    """Deterministic SVG witness: solid = observed; dashed = conjecture."""
    observed = set(centers)
    hypotheses = set(proposed) - observed
    all_nodes = observed | hypotheses
    if not all_nodes:
        raise ValueError("at least one center required")
    positions = {p: to_xy(p, radius) for p in all_nodes}
    minx = min(x for x, _ in positions.values()) - radius - 10
    maxx = max(x for x, _ in positions.values()) + radius + 10
    miny = min(y for _, y in positions.values()) - radius - 10
    maxy = max(y for _, y in positions.values()) + radius + 10
    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{minx:.2f} {miny:.2f} {maxx-minx:.2f} {maxy-miny:.2f}" '
        'role="img" aria-label="Flower of life observed and proposed circles">',
        '<rect x="' + f'{minx:.2f}" y="{miny:.2f}" width="{maxx-minx:.2f}" '
        + f'height="{maxy-miny:.2f}" fill="#fdfaf2"/>',
    ]
    for c in sorted(all_nodes):
        x, y = positions[c]
        hypothesis = c in hypotheses
        stroke = '#a65c34' if hypothesis else '#274c59'
        dash = ' stroke-dasharray="4 4"' if hypothesis else ''
        elements.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius:.3f}" '
                        f'fill="none" stroke="{stroke}" stroke-width="0.85"{dash}/>')
        elements.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="1.4" fill="{stroke}"/>')
    elements.append('</svg>')
    return "\n".join(elements) + "\n"
