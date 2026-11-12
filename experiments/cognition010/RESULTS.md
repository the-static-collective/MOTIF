# COGNITION-010 — LIVE failure→observe→revise→resume verified (post-test)

**2026-11-12, DRAFT/HOLD**. This is actual original NovelGym execution on *already inspected development seed* 31001, not a fresh heldout benchmark or evidence that MOTIF beats a strong adaptive classical solver. The owner task score comes from unmodified NovelGridWorlds native `internal_state._goal_achieved`, not a language-model judgment.

## Source/protocol custody
- Preregistered before source code: commit `0f616b7d6062295669df4b2dea8e1a16c4cb84e1`.
- Exact pinned independent NovelGym `0ad2cbb656177f76ff29f86793269b14879d9b89`, NovelGridWorldsV2 `f5d06d4f5166ca985ca420c809129a79700d904e`. Original engine and problem source unchanged. Original upstream Metric-FF C compiled conservatively at `-O0 -ansi -fno-strict-aliasing -g` as disclosed for COGNITION-006/007 (upstream default `-O6` caused SIGSEGV on runner).
- Full green GitHub run and 9/9 source/safety regression tests: https://github.com/the-static-collective/MOTIF/actions/runs/43222531873
- Complete original native owner/action/learning receipts: https://github.com/the-static-collective/MOTIF/actions/runs/43222531873/artifacts/13944609208 (artifact ZIP SHA-256 `4c4d7bc3f7313d42dc3f3b8b5c3d18450a15c275f1f777419f5bddb6d53bf61b`).
- The preceding CI had an implementation defect in the MOTIF diagnostics: the adapter expected a `hypothesis` field and received only a `kind`, causing `KeyError` and silent organ HOLD, though both controllers still solved all three tasks. This was discovered from full receipts and **repaired**. Final CI asserts genuine native MOTIF-003 and Free Graph execution and **no diagnostic HOLD** on MOTIF cases. Do not cite the earlier run as native council evidence.

## Native final owner results — three known development novelty mechanisms, both controllers

| Original NovelGym novelty | Stronger live classical feedback heuristic | MOTIF with the SAME live heuristic + native MOTIF-003/Free Graph diagnostics | Native post-failure main-agent actions | Tested distinct microplans | Owner goal |
| --- | ---: | ---: | ---: | ---: | --- |
| `axe`: native break required different selected tool | 1 attempt | 1 attempt | 6 each | 1 each | **TRUE** |
| `fence`: native movement to resource obstructed | 1 attempt | 1 attempt | 53 each | 20 each | **TRUE** |
| `dist_trade`: familiar trade action's distance precondition changed | 1 attempt | 1 attempt | 12 each | 1 each | **TRUE** |
| **TOTAL** | **3/3 verified** | **3/3 verified** | | | |

All six original native world trials completed; both received real native success at the end. In each task, one *previously failed* native subgoal was later **genuinely recovered**, followed by **resumption of the remaining original planning buffer**, continued action success, and owner-confirmed final `pogo_stick` task goal. No merely local `break_block` success was counted as completion.

The original old fixed-sequence COGNITION-009 behavior had **0 genuine post-failure recoveries in these same three development regimes**. COGNITION-010 changes the task-follow-through rule, hypothesis generation and live action replanning. The comparison is a *before/after engineering test on inspected seed 31001*, not a blind causal generalization or proof of MOTIF superiority.

### Why the user-requested no-give-up invariant matters
The new controller never stops because a finite candidate list has emptied: it regenerates candidate tests from the latest DIARC/public action receipts, broadens to legal movement/interaction sequences, carries source-bound outcomes across resets, and continues until the real owner succeeds or the **10-attempt × 80-recovery-action** resource budget is exhausted (or genuine environment terminal condition). The algorithm observes every individual actual native action and restarts the original task plan after a successful retry, in the same episode.

The extra **ninth unit test** injects a separate entirely FAKE, never-solving outcome source and verifies the classical live scheduler uses **all 10 attempts and all 800 allowed post-failure actions** without declaring an early hopeless state. This verifies a bounded procedural invariant, **not** a genuine NovelGym unsolved case. All three real game cases actually completed on attempt one, so none exercised multiple resets in the original game.

### Real source module wiring and costs
Native `MOTIF-003` executed its actual hypothetical-TEST affordance code on the MOTIF arm: 8, 24, and 8 candidate options for axe, fence and changed-distance trade respectively. Actual original Free Graph `fg_core` + neighborhood validator accepted 1, 3, and 1 **nonconstituting PENCIL** packets. Public DIARC observation and source-bound transition receipts supplied the questions; neither organ had hidden owner truth. The classical comparator used identical action-model exploration and orders and achieved identical owner outcomes and action counts. The extra MOTIF proposals **did not change action choice**; their compute overhead was not controlled as part of an equal-cost superiority comparison.

The live transition model is currently a **bounded, generic grammar plus recorded action-state deltas**, not an unrestricted planner that independently induces new PDDL operators or an autonomous multi-agent genius council. No original RapidLearn/hybrid control was included. No private Understory records read or written, no background app, no model weight updates, no merged or deployed code.

## Next independent falsification
Freeze brand-new seeds and, preferably, novel original environment mechanics *before* confirming the live policy beyond known development cases. Then compare to a strong conventional adaptive model learner and upstream hybrid approach with same action budget, observation privacy and CPU time. Preserve all failures and continue while authorized resources remain; a real environment stop or exhausted bounded budget is a legitimate, honestly reported limit, not a license to invent success.
