# COGNITION-008 — Actual native owner recovery, one development seed (post-test)

**Date:** 2026-11-12. Draft/HOLD. Real original external NovelGym engine, not our invented world. This is a *development demonstration* of two action-grammar scripts recovering from a broken plan, **not proof MOTIF outperforms a strong adaptive classical or hybrid agent** and not a heldout generalization result.

## Verified source and execution
- Original NovelGym `0ad2cbb656177f76ff29f86793269b14879d9b89`; original NovelGridWorldsV2 `f5d06d4f5166ca985ca420c809129a79700d904e`. Original code unchanged. Original GPLv2 Metric-FF C compiled conservatively to avoid the already documented upstream -O6 runner segfault.
- Native owner `internal_state._goal_achieved`, same seed 1 as previously examined COGNITION-006. Both controllers received the same project's DIARC inventory/map/action-success observation, original legal action names (including unfamiliar new choices), and prior non-novelty repertoire. This is a richer sensor interface than original paper's LiDAR RL representation.
- Verified GitHub CI: https://github.com/the-static-collective/MOTIF/actions/runs/43198787202
- Source-owned development JSON: https://github.com/the-static-collective/MOTIF/actions/runs/43198787202/artifacts/13934007735
- Preregistered at `024754f80c07a38eda49d8fa7c63f3531a28c7f9` before adaptation policy code.

## Owner-verified original game outcomes

| Controller | Success by attempt | Recovery actions | CPU seconds measured in this individual CI case |
| --- | --- | ---: | ---: |
| `classical_adaptive` (action-grammar heuristic) | **1/10** | **3** | 0.05437 |
| `motif_adaptive` (same action script + actual MOTIF-003/Free Graph observer) | **1/10** | **3** | 0.04253 |

Both controllers proposed the **identical native action sequence** on the first attempted program. Actual native action receipts:

1. `select_water_bucket`: **success**. The public DIARC inventory already showed `water_bucket=1` before adaptation; no water retrieval required.
2. `collect`: **success**. Actual inventory deltas: `water_bucket=-1`, `bucket=+1`. The native fire-crafting-table world was altered via ordinary permitted game actions.
3. `craft_pogo_stick`: **success**. Real owner `_goal_achieved=True` and native inventory `pogo_stick=+1` (with expected resource consumption).

No direct manipulation of native private `on_fire` flag, no engine patch and no fabricated reward. Native MOTIF-003 generated **five possible hypothetical action-program affordances**, and actual Free Graph `fg_core`/native neighborhood accepted an **unresolved, nonconstituting** question packet (two links, three nodes). The classical policy used the **same** affordance-informed action grammar and outcome access, but without the extra native graph observer. Both got the same result. The two CPU readings are single-process noisy samples; the MOTIF implementation does **not** demonstrate lower compute or superior intelligence from this timing difference.

## Important interpretation
- This native fire development task is *easy once the action names and full inventory are exposed*: the agent is already holding the previously unseen consumable at the failed crafting station. An ordinary, source-conditioned classical heuristic discovers the same repair in just three extra actions. This is **evidence against using this seed as a headline MOTIF breakthrough**.
- `classical_adaptive` is a source-conditioned action-sequence grammar, **not** a state-of-the-art adaptive symbolic model learner or the original RapidLearn hybrid RL. Do not label this an equally strong validated SOTA baseline. The stronger comparison in COGNITION-005 remains OPEN.
- No model weights trained, no private MEMENTO records imported, no always-on contemplation, no OS background service and no merger or deployment. Understory itself was not invoked; the experimental program stores ordinary source-bound action receipts in an in-memory journal.
- Reset cap is 10 but **both solved on attempt 1**. This does not show learning by repeated trials, nor memory carrying a useful surprise across resets.

## Engineering falsifiers
Eight native organ + domain-neutral action grammar tests passed. Initial public-observation CI failed because the file was named `inspect.py`, shadowing Python's standard-library `inspect`; renamed to `aperture_probe.py`, reran native public aperture successfully, then added the two adaptive controllers. The final scored run is GREEN.

## Next research result needed
Freeze unfamiliar novelty variants and untouched source-world cases before running the existing code, ideally `fence`, `axe`, `chest`, `dist_trade`. Do not tune on their result before declaring a separate confirmatory cohort. The real question is generalization to previously unseen mechanics with stronger source-equal classical model-update, hybrid RL and actual opportunity to use longer-term memory. If both controllers tie/fail there, report that.
