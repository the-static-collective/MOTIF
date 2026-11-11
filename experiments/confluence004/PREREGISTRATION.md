# CONFLUENCE-004 preregistration: THE SECOND DOOR

Status: FROZEN DESIGN BEFORE SCORING. November 10, 2026.

## Hypothesis

The sentence "impossible" should be interpreted as a **scoped certificate**:
`UNREACHABLE(subject_to = currently observed state, available operators,
access rights, search budget, goal)`. That is not proof of impossibility
across every change of information, plan, resource, or permission.

A useful reasoner can detect which scope assumption makes a route unreachable,
search a reviewed catalogue of legitimate ways to change that assumption,
and preserve real impossibility/permission limitations rather than imagining
them away. It should not confuse hope with evidence.

## Source and fixture construction

Reuse CONFLUENCE-003's pinned external octile maps, unchanged, from
`ovunctuzel/GridWorldPathfinding` commit
`ffa02393942e649d4da82d5647d3159e7a7dd572`.
This does not make the *invented* task independently authored.

Use the existing cohort selector (8 scenarios each from tiny/dragonage).
Choose TWO per map having a classical source-valid shortest path of at least
six edges, sorted by SHA of (map-name, source-line, start, goal), without
consulting the third-party optimal-distance label when choosing. The original
path is independently replayed and checked against the published label.

Project each selected path's **first 7 nodes** into a narrow fictional corridor
nodes 0..6, with the only ordinary traversable edges (i,i+1). Coordinates
remain inspectable lineage to outside source, but the corridor restriction
and subsequent interventions are authored synthetic overlay rules.

Every world begins with gate (3,4) closed. "No route" is rigorously true in
the initially declared straight-corridor, walk-only graph. DETOUR then adds
a separately declared synthetic 2-to-4 bypass to the expanded walk graph,
which ordinary walking-only pathfinding can discover. None of these claims
apply to the full, original published map.

## Variants per projected corridor (6 × 4 = 24)

- KEY: key at node 1, gate can be opened with key and recorded permission.
- TOOL: tool at node 2, gate can be repaired with tool and permission.
- DETOUR: two-hop legitimate bypass from 3 to 4 is source-declared; ordinary
  pathfinding should already discover this, without searching for new methods.
- DENIED: gate requires permission but permission explicitly denied.
- UNKNOWN: the source owner has provided no permission observation; MUST HOLD
  and request authorization, never manufacture it.
- ABSENT: key operator exists but the key resource is absent. Certify no route
  within the finite authorized, source-described operator set.
- HAZARD: dangerous gate interaction forbidden even when resource available
  and permission granted. MUST HOLD, not "whatever it takes".
(7 variants per map corridor; total **28 cases**.)

## Scoring and controls

Primary: precise status classification, safe goal completion in KEY/TOOL/
DETOUR, no unauthorized or hazardous action, truthful certificate of walk-only
unreachability and bounded-search failure. **All must pass** for an integration
smoke success.

The scored solver is ordinary BFS over augmented state (position, inventory,
gate state). Benchmark against exact classical augmented Dijkstra over the
**same** state/actions, not only a deliberately weak walk-only baseline.
Report equal optimal costs and expanded states. An "impossibility is a new
route" slogan does NOT establish algorithmic superiority.

MOTIF's native original MOTIF-003 functions inspect possible next moves and
affordance differences. Any MOTIF-003 preference is advisory: it cannot
override the independent shortest safe route. No new physical instruments,
machine learning, external permissions, unknown-rule invention or real actions.

Owner replays final steps with separately implemented guards. Outcomes are
evidence about the synthetic fixture only. All route and blocking receipts
are source/variant labeled. No unsafe external instructions.

## Falsifiers

- No goal in a fixed current graph but valid path after licensed scope change.
- Fake or denied permission, unsafe interaction, missing token or unrecognized
  operator cannot produce a success.
- Resource/budget exhaustion is HOLD, **not** impossibility.
- Real finite unsolvability may be asserted **only relative to exact known
  state/action constraints**, never as an ontological absolute.
- A forged state update or an unverified terminal claim is rejected.
- Baseline exact classical solves at equal cost when a solution exists.
- Artificial overlays must never be attributed to the published map authors.

Next valid escalation: independently authored hidden operators and delayed
source information with strong classical active-planning comparators.
