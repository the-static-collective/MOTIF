# COGNITION-006 — Actual native NovelGym smoke results (2026-11-12)

**STATUS: verified one-seed externally authored environment execution, NOT MOTIF superiority and NOT a statistical benchmark.** Draft, no merge or deployment.

## Verified owner source and toolchain
Original independent NovelGym `0ad2cbb656177f76ff29f86793269b14879d9b89`; NovelGridWorldsV2 `f5d06d4f5166ca985ca420c809129a79700d904e`. Both checked out at source in GitHub CI. Native `NovelGridWorldSequentialEnv`, `BasePlanningAgent`, fire YAML, PDDL and Metric-FF C implementation executed. Engine state and world rules unchanged, with Python 3.10. `ff` compiled *in CI* only, not vendored.

**Important build finding:** Upstream Makefile defaults to `-O6`; on current Ubuntu x86_64/GCC runner FF binary returned `SIGSEGV (-11)` in **both** novelty and no-novelty tasks. Initially both agents performed only one `nop` and were stuck. The original `-O6` binary's crash is a runtime/compiler defect, **not a novelty-planning failure**. A separate development run recompiled **identical upstream C source** at `-O0 -ansi -fno-strict-aliasing -g`; this corrected the crash without editing source/novelty mechanics. The difference must be disclosed if publishing these measurements.

## Native engine real-world smoke result (original owner success, not a synthetic recreation)

Green run: https://github.com/the-static-collective/MOTIF/actions/runs/43190655088
Original original environment receipts archive: https://github.com/the-static-collective/MOTIF/actions/runs/43190655088/artifacts/13931005852

| Task variant | Actual owner `goal_achieved` | Original planner main actions | Native stop condition |
| --- | --- | ---: | --- |
| **No novelty** | **TRUE** | **15** | Owner genuinely crafted the pogo stick. |
| **Fire novelty** | **FALSE** | **15** | Native `craft_pogo_stick` denied; message: `Agent is not near a crafting table.` |

The first **14 actions** in both regimes were equal and successful: acquire platinum, trade for titanium, mine diamond, gather oak/rubber, approach crafting table, craft planks and sticks. At action **15**, `craft_pogo_stick` succeeded in the normal world, and failed in the burning-crafting-table world. On the fire task the engine emitted its own action failure receipt. The current source wrapper ends the initial baseline at that first failed planned action. The owner's live success condition was read from `internal_state._goal_achieved`; no fabricated score. FF was run again separately as a **diagnostic only** after the failed action; it found a superficially legal `CRAFT_POGO_STICK` plan against its old PDDL model, demonstrating the mismatch between old plan and new world, NOT an adaptive solver.

**Interpretation:** actual independent NovelGym source on seed 1 reproduces the *mechanism* of a broken known-model classical plan under fire novelty. It does **NOT** demonstrate failure across multiple random seeds, recovery failure within 10 retries, or superiority over strong adaptive classical planning/hybrid RL. MOTIF was **not yet loaded as an action policy**. On both worlds the existing classical planner had access to its old modeled PDDL and only the original action primitives. A planner given the new fire model could plan successfully.

## Next step and fairness
Freeze a 10-attempt repeated-game comparison and ≥20 matched seeds before implementing or measuring any MOTIF advantage. Provide a legal, observable, nonprivileged NovelGym state adapter via the project's own `generate_diarc_json_from_state` and action-set names. Compare source-limited adaptive classical model update vs MOTIF's diagnostic/reflex/Understory/Graph interventions, each with the same action, reset, history and CPU budget. Report owner-verified task outcomes, time to recovery, unsuccessful probes, paid compute and false fire detections. Do not reveal `water_bucket` as privileged solution to MOTIF as a hidden oracle; actions should be discovered through the game's permitted observation/action set.

First only integrate the original environment and baseline, then score the new policy on heldout original environments. Any post-score implementation fixes require renewed confirmatory seeds.
