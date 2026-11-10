# QC-015 — THE OSCILLATION FRONTIER
## Stop running in circles; distinguish informative repetition from a dead-end loop

**Research-only draft stacked on QC-014 (PR #225)**. This is a bounded game-state monitoring / low-exposure alternative proposal, not a live-world survival planner, psychological diagnostic, trained AI model, or production module.

The user's colloquial request for "insanity prevention" refers to the way an agent can keep repeating **different** actions that return it to the same circumstances without improving its position.

### The missing problem after QC-014

QC-014 could stop the identical unsuccessful craft command. But a controller can make individually valid movements **A → B → A → B → ...**, or **A → B → C → A**, and never advance toward its goal. Every individual step could count as "successful walking" while the overall sequence is stationary.

We distinguish:

1. **Structural cycle:** the same short action/state orbit recurs twice. A valid movement is not the same thing as global progress.
2. **Observed information gain:** a revisit may be worthwhile if it reveals new terrain, new resources, new constraints or another useful discovery.
3. **Capability/resources gained:** a patrol that repeatedly returns but delivers food, repairs equipment, or acquires supplies is not equivalent to wasted motion.
4. **Background cost:** a cycle can consume food, drink, energy or health even while repeating the same physical state.
5. **Safety of proposed departure:** an unfamiliar alternate tile is not automatically beneficial or safe. The experiment explicitly tested and corrected an unsafe instinct to force novelty.

The model detects **2–7 step periods**, including alternating movements and a 4-action square; its underlying type allows up to 12. It compares **two complete periods** of typed state and action history, normalizing the phase of a cycle to avoid repeatedly reporting the same A/B pattern as a new discovery. Memory is bounded and no external effects are performed by the pure monitor.

Unlike naive "repeated action = failure" rules, ordinary forward walking, new objects/material, new achievements, and observation gain suppress the anti-stagnation alert.

## First pressure: actual archived QC-013 playthroughs

We inspected the previously archived **actual Crafter game telemetry** from [Actions run #42743549945](https://github.com/the-static-collective/MOTIF/actions/runs/42743549945), artifact [#13730685595](https://github.com/the-static-collective/MOTIF/actions/runs/42743549945/artifacts/13730685595). We source-pinned two short sequences of genuine game actions and states in `observed_prior_oscillations.json`.

- Seed **1042**: `move_left → move_right → move_left → move_right`, alternating two locations, detected at the actual **game step 118**.
- Seed **2026**: `move_up → move_down → move_up → move_down`, detected at actual **game step 187**. Energy fell by one unit during the four game steps.

**Crucial observation limit:** original QC-013 traces did not record which environmental cells were first observed. Therefore these old excerpts trigger **`SUSPECTED_CYCLE_VIEW_UNKNOWN`**. The system cannot assert that the movement taught the player nothing. The receipt preserves the original archive and member hashes, and the reduced excerpt is clearly labeled as an extraction rather than independently reauthenticating the ZIP.

## Second pressure: a controlled trap in the actual independently authored game

The real third-party [Crafter](https://github.com/danijar/crafter) 1.8.3 engine was executed via GitHub Actions. The controlled scenario deliberately changes a few starting terrain tiles to create a reproducible two-location movement loop. **Those altered cells are an explicit researcher intervention**, not a natural environment discovery.

Both policies start in the same instrumented game world, with an identical privileged *nearby tile* sensor:

- **Blind:** alternate movement between two tiles.
- **QC-015:** observe task-relevant state and previously seen local terrain; when two action cycles are confirmed to have no new terrain gain, find a genuinely observed passable third tile **outside the loop** and try one step.

**[First independently successful run #42750196548](https://github.com/the-static-collective/MOTIF/actions/runs/42750196548)**:

| Seed | Blind policy | Guarded policy |
| --- | --- | --- |
| 1042 | 30 steps in 2 locations | **Cycle detected step 5; third tile reached step 6** |
| 2026 | 30 steps in 2 locations | **Cycle detected step 5; third tile reached step 6** |
| 3199 | 30 steps in 2 locations | **Cycle detected step 5; third tile reached step 6** |
| 8765 | 30 steps in 2 locations | **Cycle detected step 5; third tile reached step 6** |

All four guard runs increased the cumulative observed local terrain records from **128** to **136** while spending only six game steps; blind loops saw 128 terrain records through 30 steps.

**What this actually proves:** a prior task can be physically blocked by its *own* short repeated plan, and a limited same-sensor observation can identify a different passable neighbor that creates genuinely **new game observations**. Reaching an additional tile does **not** prove that food, shelter or lasting game survival was secured.

The result does not establish a fair general superiority claim: the blind policy is deliberately defective and the guard was explicitly programmed to search for a third tile. The policy is not autonomously learned from human playthroughs, nor a controller capable of general spatial planning.

## Third pressure: ordinary game runs and an actual harmful intervention

The first controller version automatically broke every detected structural loop and attempted a novel neighboring tile. In six ordinary 220-step game runs, that was **not** reliably beneficial: notably seed 2026's guarded game died at **62** actions versus the baseline's **188** in [run #42750196548](https://github.com/the-static-collective/MOTIF/actions/runs/42750196548). Exact causal attribution is not established; the trace shows danger/health deterioration while the character traveled in the changed trajectory.

**We did not hide that failure.** We changed the research controller so it **does not automatically override** when:
- the repeating sequence isn't a genuine **movement-only** cycle (e.g. rest, wait, combat, sleep);
- game health is low (≤6), or the cycle already had a **decrease in vital resources**;
- hostiles are actually detected within the same declared local game sensor;
- no alternative passable tile is actually observed.

In those cases the system records the suspect pattern and abstains from novel intervention; it does **not** claim the default policy is optimal or safe. The controlled fixture is still allowed to test the intentional, low-risk defect.

The revised **[successful risk-gated run #42750479707](https://github.com/the-static-collective/MOTIF/actions/runs/42750479707)** again recovered all four controlled loops at step 6. Across six ordinary game seeds, only one automatic escape was attempted; outcomes remained mixed. In particular seed 2026 now reached the experiment's **220-step cap** with game health 9 in that *run*, but seed 3199 died earlier than its comparator. Same nominal seeds have produced different trajectories in preceding tests. **A longer run in this small stochastic simulation is not evidence that the guard generally improves the policy.**

The risk gate is a conservative *research fallback*, not a validated predictor of safe movement or an intelligent general decision policy. Its concrete utility is demonstrating **when not to automatically act on a diagnostic alert**.

## What was implemented

- `cycle_field.py`: generic, pure Python `FieldState`, `FieldStep`, bounded period detection, source-pinned `CycleAlert`, phase-invariant suppression, game-vital debt, UNKNOWN-view abstention and QC-011 replay interpretation.
- `game_cycles.py`: real Crafter 1.8.3 driver; privileged radius-7 local sensor; observed terrain novelty ledger; deliberately injected two-tile scenario; ordinary QC-013-derived game-control scenario; an alternate tile chosen from **observed current passability** and risk-gated real-game testing. Saves complete replay in **unchanged QC-011 annotated-gameplay JSON format**, plus summary and comparison.
- `observed_prior_oscillations.json`: derived, source-attributed excerpts from two real previously recorded game loops.
- `test_cycle_field.py` **13 tests**, `test_archived_cycles.py` **5 tests**: two-, three-, four-action loops, useful movement, environmental observation, resources/capabilities gained, time/risk loss, duplicate alert suppression and actual historic timing.
- `.github/workflows/quantum-code-015.yml`: executes tests, **20 actual game episodes (8 controlled + 12 ordinary)**, validates all source-pinned game traces via the existing QC-011 `read_bundle` parser, verifies the third-location and terrain-information dividend of controlled trials, and archives evidence.

Reproduce (Python 3.11):

```sh
python -m pip install 'crafter==1.8.3' pillow
cd experiments/quantumcode015
python -m unittest -v test_cycle_field.py test_archived_cycles.py
cd ../..
python experiments/quantumcode015/game_cycles.py
```

## Limits / required next tests

- A repeated loop can be useful (patrolling, collecting delayed information, intentional exercise or waiting), so a structural cycle is **a diagnostic question, not a universal failure verdict**.
- The game-only terrain visibility sensor omits other kinds of useful knowledge. An object/monster can change in a known cell without our "new terrain" counter increasing. The watchdog should learn action-specific **task-value observables** rather than a single novelty threshold.
- The guard's risk controls are hand-authored and do not guarantee physical safety. The "passable" label comes from simplified game engine rules. Avoid transferring its decisions directly to real-world travel or survival.
- Crafter stochasticity prevents treating equal seeds across separate episodes as precisely paired physical counterfactuals. Need exact restorable world state, larger sample sizes, and repeated heldout tests.
- Game-only gameplay is not evidence that similar behavior is safe or useful for a human living without stable housing.
- Real policy learning remains unproven. This branch demonstrates **a reusable source-linked pattern detector and an executable bounded response**, not a trained or self-improving survival intelligence.

## Natural next frontier

**QC-016 — GOAL-DEPENDENT INFORMATION DIVIDEND:** an agent should ask which unmet requirement or valuable unknown **a proposed escape helps resolve**, score candidate probes using available causal evidence rather than mere newness, and refuse interventions where environmental hazard uncertainty overwhelms expected value. Validate with matched-information game trials and independently reviewed, opt-in real-world decision case studies.
