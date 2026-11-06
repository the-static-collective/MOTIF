"""Reproduce the 19-circle flower, reconstruction and matched search control."""
import json
from pathlib import Path

from geometry import DIRECTIONS, flower, pathfind, propose_centers, svg_flower


def run() -> dict:
    real = set(flower(2))
    removed = {(0, 1), (1, -1)}
    observed = real - removed
    proposals = propose_centers(observed, max_ring=2)
    found = {tuple(p["center"]) for p in proposals}

    # Classical lattice completion control, given EXACTLY the same known grid.
    # It is intentionally strong and should tie geometric intersection here.
    topological_control = {
        c for c in real - observed
        if sum((c[0] + dq, c[1] + dr) in observed
               for dq, dr in DIRECTIONS) >= 2
    }

    field = flower(6)
    start, goal = (-6, 0), (6, 0)
    astar = pathfind(field, start, goal, geometry_heuristic=True)
    dijkstra = pathfind(field, start, goal, geometry_heuristic=False)

    svg = svg_flower(observed, found)
    Path(__file__).with_name("flower-of-life.svg").write_text(
        svg, encoding="utf-8"
    )

    return {
        "experiment": "MOTIF-GEOM-001",
        "field": "2-ring anchored triangular lattice of equal-radius circles",
        "full_centers": len(real),
        "observed_centers": len(observed),
        "masked_oracle_centers": [list(p) for p in sorted(removed)],
        "geometry_proposals": [list(p) for p in sorted(found)],
        "topological_control_proposals": [
            list(p) for p in sorted(topological_control)
        ],
        "completion_ties_topological_control": found == topological_control,
        "navigation": {
            "astar": {k: v for k, v in astar.items() if k != "path"},
            "zero_heuristic": {k: v for k, v in dijkstra.items() if k != "path"},
            "same_optimal_distance": astar.get("distance") == dijkstra.get("distance"),
        },
        "authority": "proposal-only; no inferred center or route causes external action",
        "svg": "flower-of-life.svg",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
