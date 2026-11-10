# CONFLUENCE-002 — Real Native Method Weave

**Draft stacked on CONFLUENCE-001 PR #270.** No merges, model calls,
authenticated real-world observations, customer data, network reads, physical
actions, TranchNode/MCP privileges or Android deployment.

## What is actually joined

This milestone runs one concrete fictional field-planning workflow through
**four live methods**, each from its own existing source code rather than
replacing them with prose-only or hand-waved wrappers.

1. **MOTIF-003, main:** CONFLUENCE-001's `adapter003.py` dynamically loads
   original `experiments/003/affordance.py`, computes hypothetical first
   moves, and BFS-checks a synthetic route to the declared goal.
2. **MOTIF-006, main:** a new explicit typed adapter invokes the actual
   `composition.py` `induce_macros`, `replay`, `signature`, and
   `checked_apply`. Two source-owned, role-renamed **fictional** traces
   teach a three-step macro. The macro is executed against an unseen third
   role assignment, replays its primitive prerequisites, and refuses missing
   simulated permission. The `bike` type is a **declared artificial
   placeholder** for an assembly in this lab; this does not teach MOTIF the
   meaning of actual fences.
3. **FIELD-008, exact unmerged source SHA:** the real
   `grounding.BlanchLedger` and its actual FIELD-006 `Lineage` base import
   fresh CONFLUENCE source receipts through a verifying normalization adapter.
   Each pre-committed hypothetical world is registered as native PENCIL,
   predictions are resolved only against actual fixture reads, and refuted
   branches lose support without erasing surviving alternatives. Repeated
   source reports count as **one** origin. This reuses the lineage mechanism,
   **not** the entire Graph Atlas graph-question engine.
4. **COLLECTIVE-001, exact unmerged source SHA:** the real
   `answer_weave.first_answer` and `reenter` run an independently rechecked
   64-case 3-bit Boolean set oracle on a narrow, explicitly declared
   *categorical toggle* subtask. A documented bridge compares the resulting
   coverage mask `001 XOR 110 = 111` with MOTIF-006's final synthetic
   coverage mask. The original source proof nodes, their ancestry, and their
   full replay-required reentry logic are retained. **This does not prove a
   real-world fencing design or infer semantics from arbitrary text.**

The returned typed envelope links all four analyses to the original
CONFLUENCE-001 source inquiry and includes the source pin SHA, proof/field
receipt hashes, symbolic macro signature, unresolved/held cases and no-action
authority. Hashes are integrity receipts, not authenticated identities.

## Pinned branch dependencies

The source pins are deliberately frozen, because branches are unmerged and
may change. CI checks out the repository twice to `sources/`:

- FIELD-008 PR #267:
  `581ed7cbc289f65f42949dd332476eb672467a7c`.
- COLLECTIVE-001 PR #233:
  `269006b559dbc73766888bcd11f5f294b8e6aa64`.

Both exact `git rev-parse HEAD` checks are mandatory. If either source is
absent or differs, the program refuses to run, rather than quietly falling
back to the earlier approximations.

## Reproduction

From this PR's branch:

```bash
git clone --no-checkout https://github.com/the-static-collective/MOTIF.git sources/field008
git -C sources/field008 checkout 581ed7cbc289f65f42949dd332476eb672467a7c
git clone --no-checkout https://github.com/the-static-collective/MOTIF.git sources/collective001
git -C sources/collective001 checkout 269006b559dbc73766888bcd11f5f294b8e6aa64
python -m unittest discover -s experiments/confluence001 -p 'test_*.py' -v
python -m unittest discover -s experiments/confluence002 -p 'test_*.py' -v
python experiments/confluence002/benchmark.py > confluence002-benchmark.json
```

Only Python standard library code is invoked in the integrated test.
Network is used to obtain pinned repository sources, **not** by the
experimental investigator. The GitHub CI workflow performs those source
checkouts and uploads an audit artifact automatically.

## Scored comparison, limitations and next falsifiers

The benchmark is four **engineer-authored** worlds. A source-optimal exact
contingent baseline (one/two sensor questions, weighted costs 1 and 2) is
reused directly from CONFLUENCE-001. Distinguish native-method interoperability
from accuracy benefit: the expected result is **no gain over the exact
classical baseline**. Full proof re-verification is computationally expensive,
so do not claim lower CPU cost or zero work simply because no *new development
questions* were needed on COLLECTIVE reentry.

The next genuine research frontier is a **frozen, independently sourced,
unfamiliar task family**, with adverse time changes and incomplete hypothesis
catalogues, where the full system and ablations (without 006, 003, native
lineage, proof reentry) all receive the same observations, compute and source
budgets. This draft is an executable architectural crossing, not that
independent study.

No module may infer permission from simulation, use an old source receipt as
a fresh reading, treat a proof of a three-bit set rule as proof of physical
safety, or accept an unreviewed remote action tool. External use requires
separate human authorization and reviewed production contracts.
