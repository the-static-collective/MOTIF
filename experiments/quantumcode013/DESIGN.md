# MOTIF QC-013 — THE HUMAN FIELD APPRENTICE
## First real expert dataset ingestion, action-network discovery, falsification and re-entry

**State:** research-only stacked draft on [QC-012](https://github.com/the-static-collective/MOTIF/pull/216). The user's 126 MiB+ archive was analyzed **locally** and **not checked into the repository**. The public repo contains only source code, synthetic validation fixtures and aggregate observations from the publicly distributed CC BY 4.0 research dataset. No private human profile or identifiable experience is published. No real-world action was attempted.

## Source verified against the exact uploaded bytes

Uploaded path: local `dataset.zip` (not distributed here).

- **131,969,180 actual bytes**
- **SHA-256:** `7dc2589de4a246035f2fefb151bd8afac85d68d62c90311bc3afe9cca2b053e2`
- **100** `.npz` human-playthrough recordings.
- **61,902** recorded gameplay action entries after the initial row of each file.
- **61,802** fully paired earlier-state → action → later-state steps after excluding the initial placeholder.
- Every file exposes action ID, 64×64 RGB screenshots, a semantic map, position, needs/inventory series and accomplishment counters (original dataset spells the prefix `achivement_`).
- Episodes vary from **162** to **3,143** game actions; **median 441**.
- All 100 episodes end at **zero GAME health** because the recordings run to game-over. This does **not** establish human mortality, real-world survival skill, or success/failure independent of recording protocol.
- Original independently hosted research source: [Crafter Human Dataset](https://archive.org/details/crafter_human_dataset); underlying game: [Crafter](https://github.com/danijar/crafter).

We do not know which recording came from which of the five human players; episode-level partitions cannot guarantee independence across individuals.

### What the experienced players actually accomplished

| In-game achievement | Episodes observed | Median first occurrence (game action) |
|---|---:|---:|
| Collect wood | **100/100** | **14** |
| Place crafting table | **100/100** | **65** |
| Craft wooden pickaxe | **100/100** | **69** |
| Collect stone | **100/100** | **91** |
| Eat a cow | **89/100** | **100** |
| Collect drinking water | **92/100** | **124** |
| Make stone pickaxe | **78/100** | **110** |
| Defeat a zombie | **84/100** | **191** |
| Place furnace | **32/100** | **397** |

The resource acquisition and crafting chain is highly repeatable in this game: all 100 observed **wood → table → wooden pickaxe → stone** in that order. Game mechanics and recipes are likely the primary cause. Temporal order itself is **not independent proof of causality**.

**Interesting mismatch with our QC-012 controller:** our first controller concentrated on quickly building a furnace, then repeatedly died without obtaining food from animals. In the human records, **89%** of episodes collected food from a cow and **92%** collected water, whereas building a furnace appeared in only **32%**. This motivates testing an alternative **resource continuity / danger awareness** policy, not a claim that the best strategy has been learned.

## An independently held-out action graph

We restricted graph discovery to **10 preregistered game achievement types**, trained temporal precedence on 80 randomly assigned episodes and checked 20 episode holdouts.

- **19** high-support ordered achievement associations met `training both >=30` and `precedence >=95%`.
- In the 20 episode holdouts, those candidates were jointly present **314** times.
- **312/314** observed pairwise orderings matched the learned direction (**99.36%**).
- **Limit:** 314 paired comparisons are *not* 314 independent tests; many share episodes, recipe dependencies, and correlated goals. This only checks held-out **temporal-order prediction**, not counterfactual action effectiveness or new mathematics.

Exact result and per-edge verification are in the local research bundle; aggregate source receipt is in `observed_100_episodes.json`.

## First action-imitation experiment (important negative result)

To test whether watching frames alone teaches practical strategy, we trained an ExtraTrees classifier on **80** episodes and evaluated it on the **20** held-out episodes, predicting the **next raw game action** from the *previous* game inventory, achievement counters, ±3-local semantic cells, previous action, position and elapsed tick. **No after-state features** were admitted.

On **11,522** held-out next-action decisions:

| Predictor | Accuracy |
|---|---:|
| Always predict NOOP (training-majority baseline) | **38.54%** |
| Just repeat the previous action | **59.29%** |
| ExtraTrees trained from human demonstrations | **55.43%** |

The classifier beats the weak majority baseline but **loses to simple action persistence**. Its macro-F1 is only **0.158**, showing poor coverage of rare actions. On the narrower 4,691 true **action-switch** moments, a separately trained model obtained **36.84%** versus **22.68%** majority baseline. This narrower task is conditioned on knowing a switch occurred, so it is not yet an online action selector.

**Major consequence:** blindly cloning frame-level button sequences is a poor proxy for practical intelligence. The dataset's frequent NOOP and repeated movement actions encode key timing and frame persistence, not necessarily distinct practical decisions. MOTIF should learn **subgoals, option boundaries, resource tradeoffs, and failed-precondition recovery** rather than equate every action tick with a deliberative choice.

The human model is not currently connected to the live game controller, and the policy modifications below are **hand-authored from observed aggregate patterns**, not a trained agent.

## Actually tested against real game worlds — and revised after failure

We added `expert_intervention.py`, which runs the unchanged QC-012 local-debug controller versus an experimental **human-informed** controller in the *actual independently authored Crafter 1.8.3 engine* for the same nominal seeds and initial screens. Both have the same declared privileged **current nearby tile sensor (radius 7)**, so this is an instrumented research test rather than image-only play or a claim of ordinary human-equivalent observation.

Initial version:
- Candidate lasted more game actions across four nominal seeds. However, a detailed audit of the **actual recorded actions** found that the seed-2026 candidate attempted **`make_wood_pickaxe` 161 times**, repeatedly failing because the crafting table was not nearby.
- **This was not intelligent survival or adaptive progress.** It was a stuck action loop, and longer survival alone concealed that defect.

We then repaired the actual code, using the observed failure: **when a tool needs a nearby crafting table, look for the table and restore the physical precondition rather than repeat the ineffective command.** We also tightened sleeping's observed enemy-distance check after a recorded loss of 7 GAME health during sleep, an actual programmed Crafter mechanic.

**[Successful corrected real playtest #42744035682](https://github.com/the-static-collective/MOTIF/actions/runs/42744035682): 14 synthetic parser tests + 1,614 actual game steps across eight runs.**

| Seed | Original controller: steps/achievements | Revised human-informed: steps/achievements |
|---|---|---|
| 1042 | 196 / 6 (died) | **220 / 6 (alive at cap)** |
| 2026 | **220 / 6 (alive at cap)** | 188 / **7** (died) |
| 3199 | 187 / 6 (died) | **206 / 7** (died) |
| 8765 | 189 / 6 (died) | **208 / 7** (died) |

The corrected intervention lasted longer in **three of four** nominal seed pairs and shorter in one; neither policy was reliably alive on all worlds. A cap at 220 **censors** episodes rather than proving long-term survival. This is a small, exploratory comparison, with manually chosen thresholds, a privileged local game sensor, and potential stochastic divergence across runs despite identical initial screens. No reliable superiority, autonomous learning, or new causal model has been demonstrated.

**What is genuinely new here is the *feedback-triggered correction* based on an independently executed action trace:** the ineffective repetitive command was identified, the missing precondition was modeled, the code was changed, and the original game engine was run again. The archived earlier failed evidence remains available; it is not silently overwritten.

## Files

- `human_dataset.py` — bounded, read-only NPZ/ZIP parser; derives aggregate counts, temporal precedence and a real-game QC-011 `Episode/Replay` from chosen human trajectories. Never executes pickle or extracts ZIP entries to disk. No live web or private player IDs.
- `test_human_dataset.py` — **14 passing** synthetic parser tests including missing fields, previous/after alignment, data provenance, no crossing dispatch, and QC-011 compatibility.
- `observed_100_episodes.json` — actual uploaded-source SHA and compact public **aggregate-only** findings, including honest imitation and holdout results. No real footage.
- `expert_intervention.py` — hand-authored, provenance-gated alternate action priorities for actual game engine experiments; retains same debug sensor as the previous controller. Includes repair based on the initial ineffective crafting loop and an explicit sleeping-risk check.
- `.github/workflows/quantum-code-013.yml` — tests, runs real game episodes on GitHub Actions, validates *every* resulting trace with unchanged QC-011 reader, archives complete action-level telemetry and screenshot contact sheets. Original 126MiB source archive remains excluded.

### Reproduce with the supplied ZIP (local)

```sh
python -m pip install numpy
python experiments/quantumcode013/human_dataset.py /path/to/dataset.zip
python experiments/quantumcode013/human_dataset.py /path/to/dataset.zip --replay 0
```

To rerun the human-informed game experiment (no source ZIP required, uses pinned aggregate findings):

```sh
python -m pip install 'crafter==1.8.3' pillow
python experiments/quantumcode013/expert_intervention.py
```

**Reproducibility warning:** nominally identical seeds produced different action histories across separate CI workflow runs after many steps, though paired initial rendered screens matched. Do not infer full deterministic counterfactual equivalence solely from seed. A more rigorous next test should freeze and restore exact simulator state and stochastic event streams, enforce equal observation budgets, and compare multiple independent seeds.

## Next frontier — AUTOMATED FAILURE-TO-QUESTION COMPILATION

**QC-014** should make the detection of failed, ineffective or repetitive *actions* automatic. It should:
1. Read a real recorded action trace;
2. Identify a plan repeatedly failing to change relevant world state;
3. Ask which prerequisite or overlooked environmental condition is missing;
4. Propose a **bounded, inspectable replacement action** rather than blindly repeat;
5. Test that replacement in the same independent game with matched information;
6. Preserve all contrary evidence, failures and costs;
7. Evaluate against robust game-planning and behavioral-cloning baselines.

This is a narrower and more falsifiable objective than claiming MOTIF has already learned general human street survival from playing a videogame.

**Epistemic law:** in-game success can teach the structure of action and adaptation. It is not evidence that a construction, resource, hazard, medical practice or survival behavior is safe in the real world.
