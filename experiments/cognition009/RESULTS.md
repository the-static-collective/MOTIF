# COGNITION-009 — Four untouched ORIGINAL NovelGym novelty variants (post-evaluation)

**Date:** 2026-11-12. **Status: GREEN; negative transfer finding.** Original environment owner, not hand-authored MOTIF world. Frozen preregistration: `8ea0c7642d0f409d763a5c413c41e5d5e7ef01c2`. This test **did not** compare against a validated strong classical adaptive model learner or original RapidLearn hybrid. It tested the *locked COGNITION-008 adaptive action grammar* with and without extra MOTIF-003/Free Graph speculative observers.

- Original NovelGym `0ad2cbb656177f76ff29f86793269b14879d9b89`, NovelGridWorldsV2 `f5d06d4f5166ca985ca420c809129a79700d904e`. Python 3.10; same original C Metric-FF conservatively compiled from unchanged upstream source (original `-O6` crashed on modern runner). Native `internal_state._goal_achieved` is task owner.
- Policy core was asserted **byte-identical** to COGNITION-008 implementation at `76f797e920aee74bfab065744b051eb5fd34084a`, including all action grammar, native MOTIF-003, Free Graph packets and action executor. Only the harness was generalized to different native YAMLs/seeds.
- Successful CI: https://github.com/the-static-collective/MOTIF/actions/runs/43199720508
- All 24 original-world trial owner/action receipts: https://github.com/the-static-collective/MOTIF/actions/runs/43199720508/artifacts/13933858724
- Artifact ZIP SHA-256 `e8c3c948838cae60f3e9c0558f3b08020a7e18e4b2b83f60ee6cda45295acacb`.

## All outcomes: 4 original mechanisms × 3 new seeds × 2 controls

| Original untouched novelty | Classic action-grammar recovery | MOTIF + same grammar | Original unmodified FF succeeded without recovery | Real **post-failure** recoveries |
| --- | ---: | ---: | ---: | ---: |
| Fence (unreachable old resource) | 0/3 | 0/3 | 0/3 | **0** |
| Axe (new tool precondition) | 0/3 | 0/3 | 0/3 | **0** |
| Chest (beneficial shortcut; old plan still works) | 3/3 | 3/3 | 3/3 | **0** |
| Changed trading distance | 1/3 | 1/3 | 1/3 | **0** |
| **TOTAL actual owner goal success** | **4/12** | **4/12** | **4/12** | **0** |

All 24 source-owned native trials completed with **zero runner/runtime errors** and owner-verified action receipts. The adaptive policies matched identically in every scenario (the same candidate-ordering logic and observations) and did **not recover any of the eight failing cases per policy**. Beneficial chest did not require adaptation because the old classical plan still reached the native owner goal. One of three trade-distance seeds worked directly without a recovery act.

### Failure evidence worth preserving

**Axe:** native owner denied the original `break_block` against `oak_log`, with message: `...requires tools to be broken.` The policy discovered/selected a newly available axe, and a `break_block` action subsequently returned native success, but the program did not continue through the remaining original plan to complete the task. This is a *recoverable subgoal with no follow-through*, not proof the tool does not work. The current grammar is not a true outcome-driven replanner.

**Fence:** original `approach_oak_log` failed with `No available spot around object oak_log`. The generic tool-contact hypothesis incorrectly proposed `approach_fence → collect → approach_diamond_ore → collect/place → approach_oak_log` instead of learning how the obstacle affects reachability and testing break/clear or alternative approaches. It performed two distinct programs and stopped. A strong planning controller should not be judged by this heuristic's failure.

**Distance trade:** original `trade_block_of_titanium_1` failed with `cannot craft` in two of three seeds. The task offered no *new* native action names, so the novelty-name-triggered heuristic had no candidate programs and abstained. This exposes a general blind spot: **novelty can change the preconditions of an old action without adding any new affordance labels**.

**Chest:** original planner reached the goal in all three cases despite the favorable new shortcut. No attempt was made to detect, value or exploit a beneficial novelty. Success here is not learning.

The grammar had a ten-reset *maximum*, but it exhausted its predeclared hypotheses in only 1–3 attempts. **It did not learn a new action model across all ten opportunities**, and none of this demonstrates the promised lifelong contemplation/muscle-memory architecture. The five perspective cards do not independently choose further actions, and no private MEMENTO Understory was invoked.

## Scientific conclusion
The previously observed native fire adaptation was a **special, unusually informative case**: the game directly exposed an unfamiliar held item with a suggestive name, and both heuristics solved it in three steps. Those heuristics **failed to transfer** to unseen action-precondition, reachability and unchanged-action failures. This is exactly the kind of falsifier we needed before making grand novelty claims. Understory provenance and a Free Graph packet do not, by themselves, implement a working model learner.

## Next source-grounded engineering question
Build a feedback-driven **classical adaptive replanner first**, able to notice a native failure, test an alternate action/target, update a transition/precondition hypothesis from real action outcomes, then return to the interrupted plan. Allow both controllers the same model learner and source access; MOTIF's contemplation/affordance contributions can only claim value if they improve external owner goal completion or real cost versus that strong baseline. A dedicated diagnostic scenario should separately target novelties with no new action names and the case of successful local repair without completing the original objective.

No production app, private data or game-engine modifications. Draft research only.
