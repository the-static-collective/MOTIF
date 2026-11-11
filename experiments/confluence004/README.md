# CONFLUENCE-004 — THE SECOND DOOR
## Treat impossibility as a scoped result, not an unrestricted worldview

**Implemented research experiment. No real-world authority or interventions.**

> A demonstrated dead end in the currently known graph is a **finding about
> that graph**, not a demonstration that no lawful alternative can exist.
> Conversely, an absence of proof of impossibility is **not** evidence that a
> route exists.

This is the experimental version of “don't believe in impossibility; find
another route.” Its actual decision rule is:

```text
FAIL TO REACH GOAL UNDER CURRENT OPERATORS
    |
    +-- Have we exhausted finite search?
    |       +-- no: HOLD_BUDGET (not impossible)
    |       +-- yes: CERTIFIED_UNREACHABLE_IN_THIS_SCOPE
    |
    +-- Can we change the scope without losing evidence?
            +-- existing detour? follow its *verified* route
            +-- new key/tool affordance, with permission? compose a new route
            +-- missing or denied consent? HOLD and ask/stop
            +-- hazard? HOLD, never force a route
            +-- missing resource or no admitted method? bounded no-route
```

The point is to turn a dead end into a **new useful question**, not an
unfalsifiable assertion of unlimited possibility.

## What ran

- **Actual external source ancestry:** Four path corridors are deterministically
  derived from source-verified, independently published Moving AI grid benchmarks
  (the unchanged pinned `ovunctuzel/GridWorldPathfinding` files already
  admitted in CONFLUENCE-003). These are merely source coordinates.
- **Explicitly invented challenge:** Each seven-node corridor is simplified
  into an authored linear passage with a locked edge at (3,4). This is NOT the
  structure of the published map. There are seven controlled variants:
  `KEY`, `TOOL`, `DETOUR`, `DENIED`, `UNKNOWN`, `ABSENT`, `HAZARD`.
  Total: 4 corridors × 7 invented variants = **28 cases**.
- **Two levels of difficulty:** A complete walk-only graph BFS proves
  whether the *currently available walking connections* reach the goal.
  A separate augmented-state BFS then considers source-declared resources
  and authorized operators that legitimately alter what is possible.
- **Actual older MOTIF-003 integration:** Dynamically calls original
  `experiments/003/affordance.py` to inspect first actions and newly
  available options. This is an **advisory instrument**. It does not replace
  or override the planner or obtain real-world permissions.
- **Strong classical competitor:** A separate exact Dijkstra traverses the
  **same fully disclosed augmented domain**. Every successful BFS route
  must match its optimal action count. This explicitly avoids claiming
  superiority merely because a weak walk-only planner got stuck.
- **A second authored owner simulator** checks the exact action sequence
  before accepting any simulated success. Source receipt integrity and
  one-origin provenance are preserved.

## Expected / audited interpretation

Positive examples: KEY and TOOL require new author-declared resource actions
and an authorized gate operation; DETOUR needs only recognition of an existing
alternative. Negative examples: DENIED/UNKNOWN permission and HAZARD must HOLD;
ABSENT demonstrates a genuine **finite, scoped** no-route conclusion.
A low compute budget must HOLD rather than declaring impossibility.

The specific claim *not* established by this experiment is autonomous
invention of previously unknown operators, generalizing beyond the supplied
action grammar, or transferable physical-world skill.

## Reproduce

Check out the exact third-party benchmark repository to
`sources/gridbenchmark` at commit
`ffa02393942e649d4da82d5647d3159e7a7dd572`, or let the workflow
do so automatically.

```bash
python -m unittest discover -s experiments/confluence004 -p 'test_*.py' -v
python experiments/confluence004/second_door.py > confluence004-audit.json
```

The GitHub Actions job `CONFLUENCE-004 The Second Door` verifies original
source bytes and archives all trial outcomes and proofs. The experiment uses
Python standard library only and makes no model/API calls.

## Honest limits and next falsifier

All gates, tools, keys, alternative passages and permission statuses are
**engineer authored**. The third-party world provides path-coordinate
ancestry, not independent gates or real people. Each method knows the
available synthetic operator catalogue. No autonomous novel mechanism,
general language understanding, physical intervention, law-breaking,
self-modification or superiority to classical planners is shown.

For a more demanding next test, provide genuinely *hidden* action effects
through an owner-controlled instrument, unseen operator classes or
independently authored cooperative field trials. Freeze candidate-operator
grammar, question/compute budgets and matched classical contingent-planning
controls before observing outcomes. Require the system to maintain an
`OTHER_OR_UNKNOWN` possibility, explicitly offer legitimate permission
requests, and never conclude global impossibility from a bounded local model.

Draft on top of CONFLUENCE-003 PR #273 and its unmerged ancestors.
Review before merging, reusing in MCP, deploying or acting on a real yard.
