# QC-012 — WE ACTUALLY PLAYED THE SURVIVAL GAME
## Third-party executable game environment, real telemetry, source-pinned replay

**Research experiment, not a live-world survival agent.** Stacked on QC-011, not merged or deployed. Game: [Crafter](https://github.com/danijar/crafter), an independently authored MIT-licensed survival benchmark published by Danijar Hafner et al. We did not merely fabricate a plausible story or interpret an imagined game: we installed the actual third-party engine **crafter 1.8.3** on GitHub Actions, executed game commands, recorded returned game states and reward/achievement results, and fed the complete action stream into the existing QC-011 replay validator.

## Actual run and downloadable evidence

**[Successful game run #42739251036](https://github.com/the-static-collective/MOTIF/actions/runs/42739251036)**.

**[Complete gameplay evidence artifact](https://github.com/the-static-collective/MOTIF/actions/runs/42739251036/artifacts/13728825201)** contains for each of the three playthroughs:
- `annotated_gameplay.json` — *every actual action* and its before/after observed **game** state, in QC-011's parser format;
- `summary.json` — milestones, executed step count, final inventory, surviving or ended status, reward, source hash and reLATTE preview status;
- `actual_gameplay_frames.png` — a montage of actual screenshots returned by the game environment, not illustrations;
- root `comparison.json` — a compact cross-run table and honest noncomparable-observation warning.

Artifact ID: `13728825201`; retention as reported by GitHub: through **2026-12-10** (downloadable from the run's Artifacts section while available).

### Measurements from actual runner telemetry

| Policy | Seed | Actions executed | Game achievements unlocked | Final health | Ended |
|---|---:|---:|---:|---:|---|
| Local-debug heuristic | 1042 | **193** | **6** | 0 | Yes |
| Local-debug heuristic | 2026 | **181** | **6** | 0 | Yes |
| Random control | 1042 | **198** | **3** | 0 | Yes |

**Total: 572 actual game steps.** All three playthroughs ended with the avatar's health at zero, not by successfully finishing the 220-action cap.

The heuristic's six achievements in both runs were: `collect_wood`, `place_table`, `make_wood_pickaxe`, `collect_stone`, `place_furnace`, `collect_drink`. The random control unlocked `collect_wood`, `place_table`, `wake_up` on seed 1042.

The first heuristic run's factual mini-trace:
- **Step 5:** collected wood for the first time.
- **Step 11:** placed a crafting table (wood consumed) — new persistent affordance.
- **Step 12:** crafted a wooden pickaxe — a new tool.
- **Step 96:** first collected stone with an appropriate tool.
- **Step 103:** placed a furnace (stone consumed) — more capability composition.
- **Step 159:** first gathered drinking water.
- **Step 193:** avatar died; **the log does not establish the precise cause** of the final loss of health.

Second heuristic run:
- **Steps 7, 12, 13:** wood, table, pickaxe.
- **Step 20:** gathered stone.
- **Step 28:** placed furnace.
- **Step 153:** gathered water.
- **Step 181:** avatar died.

These transitions were computed from the real simulator's returned inventory/achievement data. They were not authored as an invented QC-011 example.

### What the proof DOES and DOES NOT demonstrate

This is actual agent-driven interaction with a **real external software environment**, and that is a materially stronger test of the replay pipeline than QC-011's wholly fabricated game events. We found that the completed full telemetry streams pass the **unchanged QC-011 local JSON parser**, including contiguous before/after checks and time ordering.

However, the controller is a **new hand-written Python heuristic**, not MOTIF planning autonomously, and **not** a neural language model or an independently trained gameplay agent.

**Important fair-comparison boundary:** the controller reads *current local world tile types directly through Crafter's internal world object*, within a 7-tile radius, and the random control does not receive this observation. That is privileged instrumentation relative to a human or an RGB-only agent. Comparing **6 achievements against 3** on one shared seed does **not** demonstrate superior AI reasoning or robust generalization. The other seed is a replication of the heuristic's game behavior only. No independently validated learning or benefit of QC-011 over baselines is claimed.

The true user-relevant payoff is that **actions produce real, surprising consequences in a third-party simulation**, including failure after several successful constructions, rather than only matching a fixture that our program invented in advance.

The proposed next observation should be **why the avatars died**; the current summary does not resolve whether the final losses were due to enemies, fatigue, starvation, or something else. The QC-011 action replay contains health, drink, food and energy deltas for every action and allows that question to be tested, not guessed.

### Rights and player demonstrations

We also found a real, **CC BY 4.0** human-expert dataset from the game's author:

[Crafter Human Dataset, Internet Archive](https://archive.org/details/crafter_human_dataset)

According to its dataset description: **100 real game episodes, five game-experienced human players**, total download approximately 125.9 MB, all 22 achievements unlocked across the recordings. It contains actual demonstrations, not game-like synthetic scenarios. It was **discovered, not downloaded or analyzed** in this experiment. Attribute the source under its CC BY 4.0 license if any derived dataset is published.

Official [Crafter Complete Walkthrough (Human Expert)](https://www.youtube.com/watch?v=2bALHna35os) is also linked directly from the author's project page. This is a watchable human expert playthrough; this experiment did not capture or automatically parse its frames.

Other interesting videos: *The Last of Us Part I* no-commentary long playthrough; *The Long Dark* Interloper day-one survival tutorial, and multi-episode *Project Zomboid* long-term survival. Videos can be used as source references without copying or claiming to have analyzed their action contents. The expert dataset offers a much cleaner next test because recorded telemetry is more precise than inferring a state from an edited video.

## Pipeline that was actually executed

```text
GitHub runner (Ubuntu, Python 3.11)
    |
pip install crafter==1.8.3
    |
create real independent game world (seed 1042 / seed 2026)
    |
small hand-written policy (current local tile instrument, or random)
    |
env.step(real game action) -> real game state / reward / achievements
    |
mark each before/action/after transition; do not invent causal proof
    |
QC-011 Episode + Replay checks
    |
output true collected telemetry and game screenshot contact sheet
    |
unchanged QC-011 ingest.read_bundle(...) validates serialized JSON
    |
reLATTE HOLD-only source-pinned preview (NO receiver admission)
    |
downloadable GitHub Actions artifact for human examination
```

All three recorded streams remain **GAME ONLY**. No medical or physical-world survival facts can be derived from game physics.

### Run it again

Workflow: `.github/workflows/quantum-code-012.yml`.

Locally with Python 3.11:

```sh
python -m pip install 'crafter==1.8.3' pillow
python experiments/quantumcode012/play_crafter.py
```

Results appear in `runs/crafter-qc012`. This location is intentionally untracked. The GitHub Actions workflow also uploads those artifacts automatically.

## Next experiment, now based on *real failure*

1. Read the **actual action-by-action health trajectory** near the end of each run. Determine from observed game state and available hazard telemetry what precipitated death, and label unknowns.
2. Modify one clear plan element to preserve food/energy/health, or avoid a verified nearby danger, without inventing map access.
3. Replay unchanged seeds, then held-out seeds. Include a matched-information classic heuristic and an equal-budget random control.
4. Ingest an **actual human expert episode** from the licensed dataset, source-pin it, and compare the action sequences without treating demonstration as universal optimum.
5. Teach MOTIF to make its own reviewed predictions about what a new tool or shelter enables, then let the simulator falsify those predictions. That—not 6 achievements on one seed—would begin to test learning of an action-network model.

**Source/authority boundary:** no video was scraped, no copyrighted game footage was copied, no physical-world actions happened, and no native reLATTE crossing was sent. Only a HOLD-only research preview was generated.
