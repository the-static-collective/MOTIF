# MOTIF FIELD-017 — THE RECURSIVE FIELD LAB

**Research-only, draft, stacked on FIELD-016.** A bounded *hypothetical* design search that reuses the actual FIELD-016 arrangement critic and FIELD-015 analytical material-screen module. It is not a trained physics model, autonomous visual reconstruction, structural engineering approval, a verified dog-safe fence, or a field tested machine.

## User request → capability

Continue from FIELD-016 with a loop that independently generates a candidate, challenges it against physical and evidence constraints, records failures and unknowns, revises the arrangement, and repeats while computational resources remain. A user may correct the world's *inputs* directly in a shared interactive 3D schematic. **The search can mutate design choices but cannot silently mutate evidence.**

Pipeline:

```
immutable scene evidence + one starting candidate
  → generate alternate layouts from real listed routes/pieces
  → FIELD-016 evaluate → FIELD-015 physical screen
  → known model failure or still-unknown physical feasibility
  → generate and test next layout within a finite budget
  → retain complete trial trace, source digest and unresolved hazards
  → choose the lowest score under an explicit non-safety policy
  → expose one next useful interactive human clarification
  → on user-reported observation: append revision → rerun (old report preserved)
```

Operators: **MOVE_BOUNDARY**, **SUBSTITUTE_MATERIAL**, **COMPOSE_PANELS**, **REMOVE_REDUNDANT_PIECE**. All objects and routes must already appear in the scene. A path with insufficient nominal coverage, known blocked human access, failed simulated wind load, or excessive known ground opening is rejected. A path not failing these screens is still **CONDITIONAL HOLD, NOT SAFE**. Unknown physical properties are never replaced by convenient made-up quantities. A 200-pound winter zip-tie product claim cannot establish installed joint load transfer or stable anchorage.

## Scope

- `search.py`: actual F016/F015 Python adapter, typed candidate evaluation, bounded best-first revision, per-step signed world SHA-256 receipt, independent user evidence revision using F016 `reenter`.
- `loop.js`: executable offline browser equivalent using FIELD-016's existing numeric `calculate` critic; layouts, priority, and diagnostics are illustrative. Because F016's JS routine enumerates subset configurations internally, a candidate evaluation is a **bounded model assessment**, not a constant-time physics call.
- `index.html` / `app.js`: editable local UI, graphical 3D hypothetical arrangement, critic and event history, direct question widgets, source sketch/photo attachment, optional JSON input from previous workbench, local JSON export and undo.
- `test_search.py` / `test_loop.js`: numeric failure path, revision, evidence immutability, no invented geometry/permissions, screen budget accounting, HOLD discipline and reproduced outputs.
- `benchmark.py`: independent fixed-fixture search vs a *random legal whole-catalogue baseline* at matched numbers of candidate evaluations (not matched wall-clock or elementary floating point operations). **Author-generated, nonblind**, not evidence of general intelligence.

## Runnable lab

The user-facing **single-file HTML builds** embed `ui.js`, `loop.js`, and `app.js`; no external dependencies, calls, accounts, or network required. Open `MOTIF_FIELD017_Recursive_Matter_Lab.html` in a browser; the private version embeds only the user's previously provided sketch and photograph contact sheet. **These private files are not committed to GitHub.** For the repository version use a local web server in the repo root so `../field016/ui.js` resolves.

```
cd experiments/field017
python -m unittest -v test_search.py
node test_loop.js
python benchmark.py
```

No external pretrained model is invoked. MapAnything/Depth Anything 3 adapters remain experimental predecessor pathways and were **not executed** as part of FIELD-017. The displayed 3D board derives from user-entered or authored scene fields, not from physical site reconstruction or real depth.

## Actual authored results

- 23 new Python tests passed locally; 21 browser-engine JavaScript checks passed locally; predecessor FIELD-016 regression: 35 Python and 16 JavaScript checks passed.
- Python source: starting `original / privacy` layout is rejected by FIELD-015 load model. With 16 candidate evaluations, the search finds `repositioned / porous` as a **conditional HOLD** with lower declared heuristic cost; important unknowns remain.
- When given an **invented independently reported** revised porous panel width of 1.32 m rather than the hypothesized 1.50 m, the previous winner ceases to cover the route; rerunning selects a different candidate. The report never converts the hypothetical claim into an observation.
- Browser preview tested through a headless Chromium render using inline HTML, with budget 16 → 4, synthetic width update, undo and mobile viewport checks; no console errors. This validates the interface, not the physical advice.
- Fixed-fixture benchmark over 10 synthetic scenarios × 3 pseudo-random seeds: against the random-catalogue baseline, at budget 1: **3 wins / 4 ties / 23 losses**; budget 4: **10 / 7 / 13**; budget 8: **12 / 14 / 4**; budget 16: **0 / 30 / 0**. This search is **not consistently superior to random** on small budgets and ties when all options have been examined; the experiment has not demonstrated a new general-purpose planning algorithm.

## Safety and inference boundaries

1. A lower heuristic cost **is not evidence of a structurally safe fence** or even a physically installable arrangement.
2. FIELD-015 evaluates static analytical screens with authored mass, base, drag, friction assumptions. It does not simulate real joints, transient gusts, buckling, fatigue, soil, three-dimensional contacts or collisions.
3. Photos are original witnesses and may be placed in a side panel. They are **never automatically georegistered**, and the system never infers their physical dimensions from pixels.
4. No uncertainty estimate is calibrated against independent measured data. The score penalizes unverified conditions; it does not provide a probabilistic safety prediction.
5. One human edit is a claim or reported observation with provenance. It cannot upgrade a vision-model guess into a measured input.
6. The only allowed changes during autonomous search are the arrangement and the selected existing route. No fabricated piece, lessened wind, lowered clearance, stronger fastener, or unstated human permission.
7. Neither a model-generated layout nor a 3D picture certifies pet containment. Inspect holes, sharp ends, flexible mesh hazards, gate paths, and load mechanisms separately.

## Next independent pressure test

Blindly freeze third-party photos/sketches, inventory measurements, material test data, anchor capacities, and person-reviewed ground-truth real installation outcomes. Run matched-cost search/greedy/random/planner baselines and measure actual fit, corrections, hazard misses, cost and additional measurement burden. The strongest unanswered question is whether the *full source-image → semantic inventory → 3D reconstruction → hypothesis search* chain improves unseen real tasks compared with an ordinary VLM plus a simple conventional planner. No claim until that benchmark is actually conducted.
