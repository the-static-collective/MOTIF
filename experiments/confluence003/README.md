# CONFLUENCE-003 — The Unfamiliar World Test

**Source:** third-party Moving AI Lab 2D pathfinding benchmark maps, accessed
through an exact commit of `ovunctuzel/GridWorldPathfinding`. **Not** an
engineer-authored four-world fencing fixture. We use the independently
published path-length oracle only in the evaluator, never in the planner.

**Research HOLD / stacked draft** on CONFLUENCE-002 (#271), itself stacked
on CONFLUENCE-001 (#270). This is the first *external input domain* for the
integrated cartridge machinery; it is not an autonomous language-understanding
agent, a new A* implementation, a truly blinded benchmark or deployed service.

## Important up-front result criterion

The underlying path planner is **ordinary A***, using the full source map.
Dijkstra is a separate classical source-cost check. Neither needs MOTIF's
proof machinery to find the shortest path. We are testing whether native MOTIF
components preserve useful **verified explanations, guards, conditional
retractions, changes, and reusable scope-limited proofs** while handling an
unfamiliar dataset. We **do not claim a pathfinding performance improvement**.

## Exact origins

- Nathan Sturtevant, *Benchmarks for Grid-Based Pathfinding*, IEEE Transactions
  on Computational Intelligence and AI in Games 4(2):144–148 (2012).
- Moving AI Lab public benchmark map/scenario format:
  `https://movingai.com/benchmarks/formats.html`.
- The external repository `ovunctuzel/GridWorldPathfinding` is checked out
  at **`ffa02393942e649d4da82d5647d3159e7a7dd572`**.
- We inspect `benchmarks/tiny.map`, `tiny.map.scen`,
  `dragonage.map`, `dragonage.map.scen` from that source checkout.
  File-specific git blob hashes are checked on every run.
- Unmerged internal dependencies are checked out at separate source pins:
  FIELD-008 `581ed7cbc289f65f42949dd332476eb672467a7c` and
  COLLECTIVE-001 `269006b559dbc73766888bcd11f5f294b8e6aa64`.

The source maps are **read from a fresh external checkout**, not rewritten
inside MOTIF. Source checksums authenticate **bytes within the pinned Git
checkout**, not the human identity of every upstream producer.

## Scope of the actual native crossing

The external task is "get from this source-provided grid coordinate to the
source-provided destination under standard octile map rules."

MOTIF-003 directly analyzes new opportunities after hypothetical local moves.
MOTIF-006 directly learns and replays a two-edge, source-verified symbolic
macro with guard checks; its generic type names are a manually authored bridge.
FIELD-008/006 directly processes a source-backed, precommitted hypothesis
about whether a particular next cell may become blocked; a clearly declared
*engineer-inserted* obstacle triggers targeted retraction, preserving original
historical evidence. COLLECTIVE-001 directly reenters its original exact
Boolean-source proof after a three-option local direction mask changes.

**The COLLECTIVE proof certifies XOR on three encoded options only.**
It does **not** certify a grid route, all grid geometry, physical movement
or user authorization. The A*/Dijkstra and source checks handle paths.

## Independent benchmark and methodological boundaries

See `PREREGISTRATION.md` committed before implementation/score. The cohort
is 16 deterministic source-provided scenarios (8 from each map), with fixed
selection based on coordinates/line index rather than published shortest-path
length. This was not hidden from the experiment designers, and we inspected
source examples before freezing the selection.

For each case:

- Original route length is independently confirmed against source-published
  optimal length, Dijkstra and route replay.
- Where possible, a single **artificial** blocked first-step cell is inserted
  after the original plan. A* replans on the controlled revised map, checked
  with revised Dijkstra. The original source label cannot certify a modified
  map, and is never used for the mutated world's score.
- A strong **replanning A*** has the same revised map and information. Any
  replan benefit over a nonreplanning controller is unsurprising classical
  planning, not a novel algorithm.
- The identical classical route is tested with and without each MOTIF
  method; removing a proof layer is expected to affect *receipts*, not path
  accuracy. Any route differences in these ablations cause the audit to fail.

This is an **interoperability and epistemic robustness** study. It does not
establish generalization to third-party unknown mechanics, calibrated
probability, independent self-improvement, novel math, new empirical laws
or original planning algorithms.

## Reproduce

Check out the external repository into `sources/gridbenchmark` at the exact
SHA, and the FIELD/COLLECTIVE pinned sources into `sources/field008` and
`sources/collective001`, as the GitHub Actions workflow does. Then:

```sh
python -m unittest discover -s experiments/confluence003 -p 'test_*.py' -v
python experiments/confluence003/trial.py > confluence003-external-audit.json
```

The new workflow `.github/workflows/confluence-003.yml` checks out all
sources, executes the earlier CONFLUENCE tests, verifies the new adversarial
suite, runs the fixed 16-scenario benchmark and publishes the complete JSON
ledger as an inspectable artifact.

**No code generated here has access to personal credentials, remote service
actions, TranchNode identity, phone execution or physical-world authority.**

## Next falsifier

Run truly new **independently authored hidden-mechanism cases**. Deliver a
source owner that reveals only requested local sensor readings, not the full
map. Give classical Bayes/active search, D*/LPA*, competent A* replanning,
PDDL/BFS and a no-MOTIF variant identical sensor/action budgets and equal
compute. Predeclare scoring before a blind evaluation, then measure accuracy,
query and computation cost, safe abstention, detection and recovery from
change, provenance errors, and the marginal contribution of each native
method. Treat failure to beat strong baselines as an informative outcome.
