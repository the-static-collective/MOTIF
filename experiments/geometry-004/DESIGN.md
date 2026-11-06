# MOTIF-GEOM-004 — A Missing Construction Becomes a Reusable Macro

GEOM-003 only composes a fixed grammar. GEOM-004 tests whether a missing intermediate *constructor* can be proposed as a reusable macro, by finding a construction the depth-one DSL cannot express.

**Task:** Given unlabeled triangle vertices A,B,C and target-point observations, synthesize the centroid. The direct centroid formula `(A+B+C)/3` is used as independent teacher data; it is not exposed as a candidate operation.

**No new mathematics claimed.** The new `median_line(vertex, opposite_a, opposite_b)` is an ordinary composition of `line` and `midpoint`, with no newly invented primitive or formal proof of generalization. The original restricted grammar only forms lines through original vertices, and cannot solve the centroid. A systematically expanded grammar permits lines through constructed midpoints and intersects two such medians. Selection uses 3 teacher triangles plus 20 separately generated counterexample probes, and 60 fixed nondegenerate held-out triangles. Direct centroid evaluation is the strong classical baseline. All results remain `PROPOSAL_ONLY` with `HOLD` authority. Costs of searching larger program grammars are not compared here to full-featured enumerative/SMT synthesis.

Run: `cd experiments/geometry-004 && python -m unittest -v test_invention.py && python benchmark.py`

**Falsifier:** If a structural candidate cannot generalize to the 60 holdouts or passes only because of degenerate triangles, it fails. An unbounded grammar, independent data, and a stronger synthesis baseline are required before general claims. `GEOM-005` explores a different axis: typed associations and optional geometric thought-space layouts. Neither branch automatically changes MOTIF's reasoning or deployed JAR;VIS.
