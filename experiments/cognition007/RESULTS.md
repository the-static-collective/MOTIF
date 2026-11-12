# COGNITION-007 — Verified 20-seed original NovelGym/Metric-FF static-model novelty gap

**Date:** 2026-11-12. **STATUS: GREEN, native external-world baseline replication.** The evaluation is a deliberately nonadaptive baseline; **MOTIF was not scored** and no strong adaptive classical or hybrid baseline was run. This file is a post-score report; frozen seed/policy protocol at `587f591bd3f64ccdaa1e7f8615a6694af76b830a` was unchanged.

## Native real-environment evidence
- Original independent NovelGym source `0ad2cbb656177f76ff29f86793269b14879d9b89`; NovelGridWorldsV2 `f5d06d4f5166ca985ca420c809129a79700d904e`. Checked out and executed unmodified in isolated GitHub CI on Python 3.10.
- Metric-FF C source unchanged but compiled with **`-O0 -ansi -fno-strict-aliasing -g`**. Original upstream `-O6` default **crashed with SIGSEGV -11** under the same modern runner in COGNITION-006. Conservative compilation removed the compiler/runtime blocker; this alteration is disclosed.
- Original `BasePlanningAgent` picks **every agent action**. The independently implemented NovelGridWorlds engine's real `internal_state._goal_achieved` determines victory. No MOTIF action recommendation, ad-hoc invented reward or custom fire mechanics.
- Green GitHub Actions: https://github.com/the-static-collective/MOTIF/actions/runs/43191548323
- Original 40 full action/owner receipts: https://github.com/the-static-collective/MOTIF/actions/runs/43191548323/artifacts/13931575914
- Artifact ZIP SHA-256: `02a6ae9a02095cf57e2a14ed50aca5972eb1ad59ad28cd77305097f4e15341bd`

## Frozen 20 seeds × 2 original variants

Exactly `[20001+13*i for i=0..19]`, 40 native cases and zero runtime errors:

| Outcome | Original normal world | Original fire-novelty world |
| --- | ---: | ---: |
| Native owner task victories | **20/20** | **0/20** |
| Native main-agent steps before stopping | 15 each | 15 each |
| Native first 14 planned steps | successful and identical | successful and identical |
| Step 15 | `craft_pogo_stick`: success, goal achieved | `craft_pogo_stick`: actual failure, goal not achieved |
| Original stop | `ORIGINAL_OWNER_GOAL_ACHIEVED` | `ORIGINAL_PLAN_ACTION_FAILED` |

The fire engine's authentic step-15 message in COGNITION-006 was `Agent is not near a crafting table.` In the unmodified fire novelty the crafting table object does not satisfy the original crafting action's precondition. Simply replaying a previously successful symbolic plan fails.

**Crucial limitation:** All 20 seeds produced **the identical first 14 actions and identical action-15 obstruction**. The task's native seed changes did not create meaningful diversity in the observed decision problem, so these 20 matched cases are repetitions of a deterministic failure mode, **not 20 independent kinds of challenge**. Do not interpret 0/20 as an independent estimate of static planner generalization to all novelties.

This documents a failure of an **obsolete, nonadaptive symbolic model** under one independently authored novelty mechanism. It does not show the failure of classical methods generally: replanning with an updated model could solve the task.

## Next controlled experiment not performed here
A legitimate MOTIF advantage requires a real policy that receives permitted original NovelGym observations, discovers actions without reading the hidden owner target, maintains memory across up to ten original-environment attempts, and competes with both a **strong adaptive classical model learner** and the original planning+learning baseline with equivalent action/CPU/feedback budgets on **new and varied** external novelty regimes. This branch implements none of those solver arms.

Recommended next source-native interface: use NovelGym's actual `utils.diarc_json_utils.generate_diarc_json_from_state` to expose observation, failure message, inventory/map and public action names; guarantee no direct read of the object `on_fire` predicate by the policy. Before scoring, freeze unseen `fence`, `axe`, `trader`, `chest` novelty variants so a procedure hardcoded for the already inspected bucket/fire mechanics cannot appear successful by cheating.

No game sources redistributed, no private records or production changes, no automatic merge.
