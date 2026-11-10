# CONFLUENCE-003 frozen design — unfamiliar-source transfer (before execution)

**Pre-score contract, November 10, 2026.** Source examples were inspected
when choosing this experiment, so this is **not blinded independent discovery**.
The worlds and published path-length labels were authored by other people,
unlike CONFLUENCE-001/002's four invented material scenarios.

## Third-party dataset

Upstream repository: `ovunctuzel/GridWorldPathfinding`, commit
`ffa02393942e649d4da82d5647d3159e7a7dd572`. Files:
`benchmarks/{tiny,dragonage}.map` and matching `.map.scen`.
The author republishes Moving AI Lab pathfinding benchmarks. Cite Nathan R.
Sturtevant (2012), "Benchmarks for Grid-Based Pathfinding", IEEE TCIAIG.
The map dataset is used by pin and source checkout, **not republished**.

Actual baseline map domain: Moving AI octile grids, diagonal cost sqrt(2),
no diagonal corner cutting, plain `.` traversable in these two maps.
Scenario labels are **held from the planner** until independent comparison.
Algorithm input: full source map and start/goal (same information A*/Dijkstra).
This deliberately does NOT claim unknown-world exploration.

## Selection rule fixed before scoring

For each independent map, use scenarios from buckets 0,2,4,6; select
the two scenarios with smallest SHA-256 of
`map short-name + ":" + line-index + ":" + start + ":" + goal`,
never using published distance labels in selection. 8 per map / 16 total.
Preserve the original line indices and expected optimal lengths in evaluator
records. This is a fixed deterministic audit cohort; the same published
source was explored before design, so not an unseen-world holdout.

## Primary evaluation (positive only if actually observed)

1. Parse the **external unchanged source files**, verify repository revision
   and expected Git blob IDs, check scenario dimensions, cell legality and
   published paths.
2. Require a source-labeled grid goal to be reached by an independently
   checked route whose cost agrees (tolerance 1e-4) with both a separate
   Dijkstra implementation and the source-published optimal length.
3. Compare route length/number expanded to classical A* with octile
   heuristic; no claim of novelty or faster-than-A* without matched compute.
4. Independently execute canonical MOTIF-003 as an affordance diagnostic.
   Its suggested first move may NOT displace A* if inferior.
5. Invoke canonical MOTIF-006 for a **typed, replayed, permission-guarded,
   two-step symbolic route proof**, provided the actual source path has at
   least two edges. The `bike` type in its code is an explicit synthetic
   adapter for a path segment, not a general-purpose geometric ontology.
6. Use native FIELD-008/006 source-verified lineage on two incompatible
   conditional states of a chosen first move. Controlled post-plan blocking
   is clearly separate from the immutable third-party map.
7. Reenter the actual COLLECTIVE-001 finite 3-bit XOR proof on an explicitly
   mapped three-option local direction set after the controlled change.
   The proof only certifies a 3-bit Boolean toggle; **not** the physical
   grid path, map authorship, or any real-world action.
8. Compare full approach with no-003, no-006, no-lineage, and no-COLLECTIVE
   ablations under identical source information and search. Report if
   ablation changes only receipts, not task accuracy.

## Secondary shift test

If an original source-planned route begins with an edge and the start has
another exit, inject **one artificial blocked cell at the first planned
destination**. Do not alter the original map or scenario labels. Freeze the
revised observation before rerouting, replan with normal A*, and check
its new path with Dijkstra against the updated simulator. A fresh classical
A* replan is the **strong comparator** and should tie. Do not compare a shifted
cost to the original source optimal length.

## Hard HOLD conditions

Unsupported terrain, missing source pin, source tampering, unsupported
semantic mapping, nonverifiable synthetic change, invalid route, source
length disagreement, absent route or permission gate => report HOLD or fail
the audit; never invent facts or a victory. A source SHA is integrity, not
authenticated worldly witness identity.

**No external action, app, MCP, user data, autonomous code revision or
general human-level reasoning is allowed in this challenge.**
