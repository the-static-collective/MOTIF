# MOTIF-GEOM-001 — The Flower of Life as a Reasoning Field

**Status:** Implemented, standalone, finite synthetic geometry experiment. No physical measurements, image understanding, live intervention, divine claims, or new causal law are demonstrated.

## Question

Can a recognizable geometric construction become an executable, reviewable MOTIF reasoning cartridge, providing **structural constraints, possible missing pieces, symmetry, and useful path-search heuristics** rather than merely decorating a graph?

Use the common 19-circle flower-of-life arrangement: one center, six in ring one, twelve in ring two. All circles have radius R; adjacent centers are separated by R. The centers occupy a triangular (axial hex-coordinate) lattice:

- Cartesian: x = R(q + r/2), y = R√3·r/2
- Radial distance: max(|q|, |r|, |q+r|)
- Patch count through ring n: 1 + 3n(n+1)
- Undirected nearest-neighbor edges: 3n(3n+1)
- Exact 60° symmetry: (q,r) → (-r,q+r)

A point may be drawn without being *observed*. Observation, geometrically implied candidate, simulated route, and authorization are distinct types.

## The executable experiment

1. **Construct:** Produce the finite center field and a complete set of witnessed nearest-neighbor edges. Build the equal-radius circles and mathematically calculate circle intersections, including tangency. Never silently "fill in" missing centers.
2. **Propose:** Given an incomplete finite observed set, intersect observed circle pairs and snap results only to calibrated lattice positions within an explicitly bounded field. Label absent positions as PROPOSAL_ONLY and score existing neighbors / modeled unseen neighbors. Nothing is inserted into the observed set.
3. **Reason over the field:** Plan only along *observed* centers and *observed available* edges. Compare A* with consistent hex-distance heuristic to a strong classical zero-heuristic/Dijkstra control on precisely the same input graph. Both find shortest paths; performance can differ only in examined states, not invented capabilities.
4. **Portable evidence:** Export an integrity-checked JSON geometry envelope with rederived proposals, an explicit HOLD, and no effective authority. The SHA-256 digest ensures payload consistency but **does not authenticate a person, source code, or independent reality**.
5. **Visual witness:** Draw solid observed circles and dashed inferred hypotheses into a deterministic SVG. It is a diagram of the synthetic input, not image recognition.

## Controls and falsifiers

Run: `cd experiments/geometry-001 && python -m unittest -v test_geometry.py && python demo.py`

- Check patch counts (1, 7, 19, ...), 6-fold symmetry, exact nearest-neighbor distances, pairwise circle intersection coordinates, and sparse two-circle tangency.
- Mask two centers from a real 19-center field; compare geometric intersection reconstruction against a **strong classical neighbor-count completion** control that is given the same axial geometry. Expected result: **tie**. A geometrical picture is not automatically superior to its equivalent graph encoding.
- Compare A* to zero-heuristic search across multiple patch sizes, blocked centers, severed edges, and unreachable cases; **optimal path cost must match**, and disconnected graphs must HOLD rather than fabricate a crossing.
- Calibration check: points off this anchored/unrotated lattice are rejected; a rotated photograph or imprecisely observed physical spacing is not supported in v1.

### What would falsify a useful claim?

If the geometric representation cannot accurately regenerate intersections, has invalid symmetry, introduces missing centers into witnessed navigation, underestimates path distance incorrectly, or claims better optimality than the exact shortest-path baseline, the cartridge fails. If a more general polygonal or graph algorithm performs equally well, acknowledge the tie.

The calculated **modeled unseen neighbor** count is a planning affordance estimate conditioned on this exact synthetic geometry. It is not proof that a real capability, resource, or neighbor exists.

## Boundaries and next possible experiments

- Present implementation encodes a *known, upright, calibrated* triangular lattice. It does not infer arbitrary rotation, scale, orientation, lens distortions, perspective, unknown radius, or the exact form from a photograph.
- No "sacred" property is assumed to be a scientific mechanism. The cultural motif is a good **source of geometry**, not evidence of metaphysical causation or mathematical novelty.
- Strongest next challenge: infer an unknown lattice from noisy point observations with rotation/scale, then compete against RANSAC/lattice fitting under held-out missingness. Also compare a Delaunay/Voronoi dual, D6 group orbits, and constraint-satisfaction completion under equal information/compute.
- A MOTIF/GRAFT/CANNON crossing would require independent review, a pinned input cartridge contract, and an explicit local admission decision. **This isolated module is not silently imported into other experiments or deployed in JAR;VIS.**

## Files

- `geometry.py` — pure-stdlib construction, symmetry, intersections, candidate inference, shortest-path search, SVG.
- `test_geometry.py` — invariants, masked recovery, baseline parity, hard refusals.
- `cartridge.py` — canonical, checked, HOLD-only portable geometry evidence.
- `demo.py` — reproducible evidence receipt plus locally generated `flower-of-life.svg` and `example-geometry-cartridge.json`.

**Standing result to seek:** geometry as a *testable structural prior* that supplies constraints and admissible search guidance. Not consciousness, permission, or automatic discovery of physical laws.
