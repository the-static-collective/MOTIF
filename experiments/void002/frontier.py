"""VOID-002: same-information frontier exploration over observed Crafter tiles.

Predicted sightline coordinates are NOT observed terrain or verified resources.
MOTIF-003 is the actual source module, not a renamed classical heuristic.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "void001"))
WALKABLE = frozenset(("grass", "path", "sand"))
DIRECTIONS = (("move_left", (-1, 0)), ("move_right", (1, 0)),
              ("move_up", (0, -1)), ("move_down", (0, 1)))
RADIUS = 7
GRID_SIZE = 64
POLICIES = ("classical_2ply", "motif003", "classical_1ply")


def source_moves(belief, position):
    grid = belief.grid
    return tuple((action, (position[0] + delta[0], position[1] + delta[1]))
                 for action, delta in DIRECTIONS
                 if (position[0] + delta[0], position[1] + delta[1]) in grid
                 and grid[(position[0] + delta[0], position[1] + delta[1])].material in WALKABLE
                 and not grid[(position[0] + delta[0], position[1] + delta[1])].object_present)


def potential_reveal(position, seen):
    """Potentially exposed coordinates, NOT assumed resource discoveries."""
    x, y = position
    return frozenset((x + dx, y + dy)
                     for dx in range(-RADIUS, RADIUS + 1)
                     for dy in range(-RADIUS, RADIUS + 1)
                     if abs(dx) + abs(dy) <= RADIUS
                     and 0 <= x + dx < GRID_SIZE and 0 <= y + dy < GRID_SIZE
                     and (x + dx, y + dy) not in seen)


def score_future(path, seen, visited):
    unknown = frozenset().union(*(potential_reveal(pos, seen) for pos in path))
    return len(unknown) - .25 * sum(visited[pos] for pos in path)


def classical_pick(belief, seen, visited, depth=2):
    options = source_moves(belief, belief.start)
    if not options:
        return None
    def evaluate(pos, path, n):
        if n == 0:
            return score_future(path, seen, visited)
        onward = source_moves(belief, pos)
        if not onward:
            return score_future(path, seen, visited)
        return max(evaluate(nxt, path + (nxt,), n - 1) for _, nxt in onward)
    return max(options, key=lambda item: (
        evaluate(item[1], (item[1],), depth - 1),
        -visited[item[1]],
        -next(i for i, (a, _) in enumerate(DIRECTIONS) if a == item[0])
    ))[0]


def motif_pick(belief, seen, visited):
    """MOTIF-003 analyses simulated first moves; no hidden map observations."""
    from mesh import native003
    native = native003()
    start = frozenset({("position", str(belief.start[0]), str(belief.start[1]))})
    options = source_moves(belief, belief.start)
    if not options:
        return None

    def position(state):
        _, x, y = next(x for x in state if x[0] == "position")
        return (int(x), int(y))

    def possibilities(state, verbs):
        pos = position(state)
        for action, dest in source_moves(belief, pos):
            if action not in verbs:
                continue
            base = frozenset(x for x in state if x[0] != "position")
            newly = frozenset(("potential", str(x), str(y))
                              for x, y in potential_reveal(dest, seen))
            yield (action, (), base | newly | frozenset({
                ("position", str(dest[0]), str(dest[1]))
            }))

    def utility(state, original):
        coords = {(int(x), int(y)) for tag, x, y in state if tag == "potential"}
        return len(coords) - .25 * visited[position(state)]

    rows = native.analyze_first_moves(
        start, tuple(a for a, _ in DIRECTIONS), possibilities, utility,
        horizon=2, max_worlds=64)
    by_action = {r["operator"]: r for r in rows}
    return max(options, key=lambda item: (
        by_action[item[0]]["immediate_delta"],
        len(by_action[item[0]]["new_affordances"]),
        by_action[item[0]]["reachable_after_first_move"],
        -visited[item[1]],
        -next(i for i, (a, _) in enumerate(DIRECTIONS) if a == item[0])
    ))[0]


def choose(belief, seen, visited, policy):
    if policy not in POLICIES:
        raise ValueError("UNDECLARED_POLICY")
    seen = frozenset(seen)
    if not {c.xy for c in belief.cells}.issubset(seen):
        raise ValueError("CURRENT_OBSERVATION_NOT_IN_SEEN_LEDGER")
    if policy == "motif003":
        return motif_pick(belief, seen, visited)
    return classical_pick(belief, seen, visited,
                          depth=2 if policy == "classical_2ply" else 1)
