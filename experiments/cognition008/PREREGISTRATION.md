# COGNITION-008 — Ten-attempt NovelGym adaptation (frozen before policy code)

2026-11-12; draft experiment stacked on COGNITION-007, which verified original nonadaptive FF 20/20 normal-owner victories and 0/20 original-fire-owner victories (20 repeats of the same native 15-action trajectory). **This protocol is for running real adaptive controllers on the original native environment.**

## Main question
Given an *unmodified original NovelGym* fire-world and its original failed `craft_pogo_stick` native action, can a controller re-enter the world up to ten times, use only permitted native observations and native actions, discover a previously ineffective or unseen affordance, and obtain the **real engine owner's** `internal_state._goal_achieved`? Does a MOTIF-inspired evidence/provenance/affordance controller outperform a **strong classical adaptive model learner** with equal action, model access, memory and compute budgets? A tie or both failing counts as a negative result. An obsolete static planner is NOT the main comparison.

## Environment custody
Original NovelGym SHA `0ad2cbb656177f76ff29f86793269b14879d9b89`; NovelGridWorldsV2 SHA `f5d06d4f5166ca985ca420c809129a79700d904e`. Python 3.10. Original native `NovelGridWorldSequentialEnv`, original `BasePlanningAgent`, original `fire_crafting_table.yaml`, genuine `info.success` and owner goal. Upstream C Metric-FF source remains unchanged; build `-O0 -ansi -fno-strict-aliasing -g` because the default `-O6` segfaulted in COGNITION-006. Original world code never patched.

## Information wall
Controller can read the native project's public `utils.diarc_json_utils.generate_diarc_json_from_state` observation (world's visible inventory/player/map, selected item, prior failed action), current native legal action names and their original action-success/message receipts. This is richer than strictly the original RapidLearn RL's LiDAR vector; the richness is identical across MOTIF/strong classical arms and must be disclosed. Controller **cannot** read engine `_goal_achieved`, `on_fire`, future state, randomized seed truth, player hidden data, novelty yaml filenames/contents, or directly invoke engine object `acted_upon`. Owner goal and internal state may be inspected only by the evaluator, never used for policy selection.
The original historical baseline's `action names` and prior successful plan can be offered to both as an explicitly pre-novelty learned repertoire. The action surface may reveal unfamiliar `approach_*` and `select_*` options; both controllers can use these. Do NOT hardcode strings containing fire, water, bucket, or target success into policy logic.

## Bounded ten attempts
- Development seed `1`, `fire` only, maximum 10 resets and 80 recovery-phase main-agent actions per reset, plus original planner prefix <=160 and total native actions <=600 per episode. An attempt terminates on original owner goal, given-up, truncation, native failure, or action cap; one failed action does not necessarily stop adaptive control.
- Reused knowledge across resets MUST be sourced to earlier action-success and observation-delta receipts; no magic progress from an episode that was reset.
- Both arms receive identical access to action names and two-day history, same 10 attempts, action caps, option universe and API. No native RL training claim. Classical adaptive algorithm may use relational model update, breadth-first experiment ordering, outcome-driven action grammar and revisiting formerly failed actions; it is not merely a frozen PDDL planner. MOTIF-inspired algorithm may use native MOTIF-003 proposal affordances and source-bound reflection; both must test their candidates.
- Primary metric: native owner task success by attempt 10. Secondary: first successful attempt, total recovery actions, failed tests, distinct new action attempts, novelty diagnosis, explored test paths, CPU time, memory size, false causal claims and total compute. Count all consumed actions and repeated attempts.
- **Development only**: seed 1 is already studied. No claims of generalization or superiority from it. After native development flow works, freeze *new* heldout seeds and novelty variants **before** looking at results. In particular a fire-bucket procedure discovered on seed1 is not a transferable score for unrelated `fence`, `axe`, `chest` or `dist_trade`.

## Positive/negative interpretation
Win against the strong adaptive classical comparator on unseen external tasks under matched budgets (and meaningful compute cost) qualifies for further replication, not automatic new intelligence. Only matching or beating a broken fixed-model plan is expected adaptation, not a breakthrough. Neither one development seed nor a handful of repeated identical seeds is a valid independent sample of novelty types.

## Stop/authority gates
No GitHub merges or deployment, no private MEMENTO records, no real-world actions, no phone background workers, no model self-retraining. Fail closed and archive installation/runner defects separately from cognitive failures. All hypotheses remain PENCIL until original owner action/outcome receipts support them.
