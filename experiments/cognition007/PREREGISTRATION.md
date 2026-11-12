# COGNITION-007 — NovelGym fire: independently authored environment, 20 matched external-world seeds

2026-11-12. Protocol frozen before test code and outcomes. Experimental design is a **nonadaptive classical-model failure replication**, not a MOTIF-versus-adaptive-control competition. No claim of novel MOTIF advantage.

## Why this stage
COGNITION-006 ran original external NovelGym native source with original Metric-FF / `BasePlanningAgent`, observed same initial fourteen actions and a genuine owner-verified no-novelty task victory at action 15 vs fire-world crafting failure at action 15. Upstream `-O6` FF crashed on modern runner; identical FF source compiled with conservative `-O0 -ansi -fno-strict-aliasing -g` worked. That original one-seed comparison is development evidence, not a prevalence statistic.

## Frozen evaluation
- New matched seeds: `[20001 + 13*i for i=0..19]`, never used in COGNITION-006. Each seed is run independently under original `none` and original `fire` YAML, **40 actual native game episodes** total.
- Original pinned sources: NovelGym `0ad2cbb656177f76ff29f86793269b14879d9b89`; NovelGridWorldsV2 `f5d06d4f5166ca985ca420c809129a79700d904e`. Build original Metric-FF C code with conservative flags as already audited; no FF/game source patch.
- Exact same original `BasePlanningAgent`, agent action policy, environment controller, main-action cap 160, total action cap 600, no learned memory/recovery, original native owner goal `internal_state._goal_achieved`. Keep per-action `info.success` source records.
- Primary descriptive endpoint: matched pre-task success and fire-task success, paired difference by seed. Secondary: first failed action, main actions until owner completion/first obstruction, planner stuck status, stderr and model error separately classified.
- Do not assert all 20 pre-victories or fire-failures in advance; owner may produce unpredictable results. Every seed retained.
- Absolute case results and summary derived from owner state only, not fabricated. If environment code fails to run for any seed, report BLOCKED with per-seed exception; do not represent failure-to-run as an AI defeat.
- A static planner with a known incorrect model is not expected to adapt to unmodeled novelty. A genuine MOTIF gap is **not established** unless future MOTIF beats *strong adaptive classical and original hybrid* on matched conditions.
- No private data, mobile app, automatic deployment or physical action. No policy learning or external model calls. This stage intentionally does not try to solve the fire.
