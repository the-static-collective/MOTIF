# VOID-002 — Natural-world Crafter frontier: frozen challenge protocol

**Research HOLD.** Written without inspecting any VOID-002 game-engine result. Not a truly third-party blinded study; the researcher authored policy, selected seeds, and supplied game dynamics. Source is an independently authored game, not an externally administered agent benchmark.

## Question

When a useful game resource is not currently accessible, does original MOTIF-003's *newly reachable option* reasoning improve externally witnessed outcomes versus competent classical lookahead, with equal information and action limits?

## Exact independent software and inherited methods

- Original third-party simulator: `crafter==1.8.3` installed from PyPI in GitHub Actions; `env = crafter.Env(seed=...,length=70,view=(9,9),size=(64,64))`, `env.reset()`; no researcher edits to game tiles, objects, player status, inventory, or resource placement.
- Original QC-017 `plan.observe`, `traverse`, `check_goals` and QC-012 `Controller.tile` / `ACTS`, checked out from `the-static-collective/MOTIF@7e35ab7157755c83c6353e939a2ae1b018d70667`, with Git SHA checked by CI.
- Original MOTIF-003 `analyze_first_moves` from inherited VOID-001/MOTIF branch is directly executed on simulated view states for the experimental arm.
- **Privileged sensor disclosed:** local radius-seven engine-internal tiles, position and orientation. This is NOT image/RGB reasoning or full-map access.
- All policies share the same existing QC-017 classical BFS for routes to already observed wood/water resources. Thus this tests **exploration policy selection**, not new route-planning mathematics.

## Frozen cohort and measured outcomes

Four *previously used* game seeds `[1042,2026,3199,8765]` are development/descriptive only. Six additional selected seeds `[19001,19003,19007,19009,19013,19021]` are **new to this experiment** and designated heldout **before reading outcome results**. These are not sourced or concealed by an independent benchmark organizer. Every seed is reset separately per policy.

Per episode: at most 70 actual game `env.step` actions, stop on engine termination or two witnessed goals; no paid model calls. First goal: gain game wood. Second: gain game drink. A goal only counts when the game reports an actual resource/achievement increase after an actual step; proposed actions alone never certify success.

**Primary score per episode, fixed now:**
`verified_goals - 0.1 * (game_actions / 70) - 0.05 * (no_effect_actions / 70)`.
Heldout mean over the six specified seeds is reported for each arm. Also report witnessed goal counts, action counts, no-effect actions, early termination and per-step receipts. This scoring penalizes costly exploration modestly and never rewards simulated future opportunity itself.

## Experimental arms

1. **CLASSICAL_2PLY (strong control):** exhaustive two-action lookahead over same currently observed walkable cells, maximize union of potentially newly sensed coordinates; fixed revisitation cost.
2. **MOTIF003:** run original MOTIF-003 hypothetical-action analysis over the same observed walkable cells and not-yet-seen *coordinate* sightline predictions; rank candidate first actions by predicted immediate visibility, new available next-step choices, and bounded future reach.
3. **CLASSICAL_1PLY (ablation):** same classical objective restricted to one future move.

None of these policy scores uses hidden terrain, resource positions, unknown game physics or the outcome grader. Coordinates that could become visible after walking are **not promoted to observed facts**. A source-origin checksum is only a local integrity check, not independent authentication.

## Fairness and interpretability

- Same world *seed*, game mechanics, sensor, current tile data, fixed BFS for known resources, max 70 game steps, goal order and outcome grader in all arms.
- Different action choices may cause stochastic game outcomes to diverge after the common starting seed; paired seed is NOT an identical future trajectory.
- MOTIF-003 may use more compute than simple controls. No assertion of matched CPU time or that this is the strongest possible MCTS/POMDP/active SLAM baseline.
- Any benefit could come from an authored heuristic rather than general reasoning. Any tie or classical victory counts as a valid finding.
- Primary result is **not success unless the real third-party game supplies actual before/after receipts**. The workflow should fail rather than manufacture results if the runtime or source pin breaks.

## Next test

Use independent challenge owners and hidden-mechanism tasks with meaningful cost of information, nontrivial tool preconditions and an adaptive conversational partner. The current v2.0.0 `tau2-bench` text customer-service benchmark supplies published policy/task fixtures but requires model inference for a valid official comparison; a no-LLM extraction or static replay must never be called a tau2 benchmark score.

**No real-world actuation, human survival claims, task auto-merge, personal information, unauthorized external tools, or production MCP admission.**
