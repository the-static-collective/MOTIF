# COGNITION-009 — Locked action-grammar transfer to untouched original NovelGym novelties

**Frozen 2026-11-12 before executing any of these variants.** Underlying original world is owned by Tufts NovelGym; no invented simulators. Preliminary comparison only, not an adaptive-classical superiority study.

## Previous development / locked policy
COGNITION-008 native *development* seed 1 fire solved in 3 recovery actions on the first attempt for BOTH the generic classical action-grammar control and the same program with genuine MOTIF-003/Free Graph analysis. Source-level policy was not general model discovery. Before this experiment, lock source `experiments/cognition008/adapt.py` from MOTIF commit `76f797e920aee74bfab065744b051eb5fd34084a`. In COGNITION-009 only generalize the **test harness**: original NovelGym config path per variant, new seed allowance, and named score output. Proposer, native MOTIF evaluation, Free Graph, and action execution must remain byte-identical to this locked version; CI compares their complete source bodies.

## Frozen previously untested original variants
Exactly `fence`, `axe`, `chest`, `dist_trade` (native registry paths, not inspected game mechanic implementations for tuning). Preset three seeds `31001, 31021, 31041`, all distinct from seed 1 and COGNITION-007's seed cohort. Each novelty × seed × policy creates **24 original environment trials**; each policy has maximum 10 original native episode resets and 80 action-grammar recovery actions per attempt. Maximum 600 native total actions per attempt. Both policies see identical original native action names, the original DIARC public observation and the same pre-novelty action-name repertoire. No privileged novelty configuration content sent to policy; only harness chooses which config to load. No policy changes, dynamic manual advice, specialized fixes, or run-to-run code self-modification.

## Outcome classifications
1. `NATIVE_BASELINE_GOAL`: original upstream PDDL/FF plan achieves owner goal before any recovery — not a learned adaptation victory.
2. `NATIVE_RECOVERY_GOAL`: original planner fails on original task, then tested native adaptive program achieves native owner's `_goal_achieved` within 10 attempts.
3. `HOLD_NO_PROPOSALS`, `EXHAUSTED_TEN_ATTEMPTS` or `BLOCKED_UPSTREAM_RUNTIME`: no native owner success and reported as failure/hold, never a hallucinated victory.

Summaries must preserve each seed and novelty even when input engine throws, and separately distinguish baseline-completion from actual recovery.
- Primary: paired native owner recovery and baseline completion across original environments, false novelty detection/abstentions and true recovery actions used.
- Secondary: attempt counts, failed native action receipts, actual source-built Free Graph validation and genuine MOTIF-003 invocation, CPU time.
- Do **not** infer independent variety from mere seed changes if all traces match. Different novelty mechanisms are the meaningful varying axis.
- Do **not** declare a MOTIF advantage when the two policies share the exact same action-grammar proposal order. An equal result is a predicted tie. These policies are NOT a strong model-learning classical/SOTA control or original RapidLearn hybrid. This evaluates **transfer of the fixed source-observation heuristic only**.

## Native upstream custody
NovelGym SHA `0ad2cbb656177f76ff29f86793269b14879d9b89` and NovelGridWorldsV2 SHA `f5d06d4f5166ca985ca420c809129a79700d904e`. Exact original variant YAML files loaded as upstream; no engine/game action implementation patched. The unchanged upstream FF C is built with disclosed conservative `-O0` flags to avoid prior observed `-O6` segfault. Actual native agent action success and original owner goal judged independently.

No merge/deployment, no personal MEMENTO records, no background app work.
