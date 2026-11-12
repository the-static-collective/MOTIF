# COGNITION-006: native NovelGym world probe (frozen before code)
Date: 2026-11-12. Draft, not scored MOTIF v classical competition.

## Mission
Execute **the original NovelGym/NovelGridWorldsV2 environment**, not an imitation; obtain the original simulator's `internal_state._goal_achieved` and action outcomes for both `none` and `fire` task variants. Use original `BasePlanningAgent` and native action set; diagnose breakage under fire without injecting solution mechanics. This is an environment-integration smoke/regression, not the 20+ matched-seed competitive evaluation frozen in COGNITION-005.

## Source/immutability
- NovelGym at `0ad2cbb656177f76ff29f86793269b14879d9b89`.
- NovelGridWorldsV2 at `f5d06d4f5166ca985ca420c809129a79700d904e`.
- Python 3.10 (upstream tested up to 3.10); upstream main YAML and fire YAML, no environment code modifications. Original GPLv2 Metric-FF built in isolated CI checkout, not vendored or redistributed.
- Real `NovelGridWorldSequentialEnv`, real planning module `agents.base_planning.BasePlanningAgent`; not a hand-authored mock.
- Do NOT import `args.py` or the Tianshou training stack for the first smoke if unnecessary. Use original main RL-single configuration and YAML layering as upstream does.

## First observed trial
- Execute a single fixed seed 1 for each of `none` and `fire`, capped at 160 environment **main-agent** actions and 600 total AEC actions (stop earlier if owner goal, owner give-up, or planning stuck).
- Baseline uses original agent `policy(observation)` and follows PettingZoo action stepping; no new `use`/bucket skills for MOTIF. Record per-action native `info.success`, action names, `goal_achieved`, `given_up` and `failed_action` diagnostics. Full true source owner state stays internal to evaluator; eventual decision agent should receive only observation.
- If upstream dependency/compilation/API error: report that honestly as BLOCKED with structured trace and nonzero CI failure. Do not treat it as a model failure.
- If native fire world and no-novelty world both run, report their task outcomes; a single run does not prove statistical failure and a hanging planning loop is an environment/harness bug, not an AI defeat.
- Do not silently replace original planner, novelty injector or owner success condition; any workaround must be disclosed.

## Later controlled trial, not part of this smoke
Only after original smoke works, implement a MOTIF policy over observation/action primitives, then matched original Metric-FF, adaptive classical model-learning, upstream RapidLearn, and MOTIF on >=20 same novelty seeds with frozen budgets. Keep original task success and adoption rules; allow classical to win. Strict no claims of superiority before that external evaluation.

## Safeguards
No private records, GitHub merges, production app, unseen human subjects or real-world actions. Maximum CI timeout. A failed integration is an important finding to preserve.
