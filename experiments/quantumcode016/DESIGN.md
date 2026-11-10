# MOTIF QC-016 — NESTED CYCLES × GOAL-DEPENDENT INFORMATION DIVIDEND
## Cycles of cycles, a real-world-relevant question, and an independently executed game falsifier

**Status:** Stacked experimental draft on QC-015 [#231](https://github.com/the-static-collective/MOTIF/pull/231). This is **game-only research**, not a survival adviser, clinical risk assessment, autonomous human assistant, deployed integration or trained policy. No real-world resource was accessed; no user data or lived-experience record was ingested; no native reLATTE crossing was performed.

## User specification

> "Expand it to detect patterns that are two to seven cycles of those cycles. And then do exactly the thing that you said too."

We implement **both**:

1. **Cycles of cycles:** an action loop may be internally valid yet only one component of a larger, periodically repeating unproductive routine. Detect repeating motifs of **2–7 independently closed primitive action cycles**, followed through **2–7 repetitions** of those larger motifs.
2. **Goal-dependent information dividend:** a proposed change should not be chosen merely because it visits a new coordinate. It must plausibly answer a **currently unanswered need-related question** or create an actual capability, with explicit evidence, permissions, resource costs and danger/uncertainty gates.

### Two-level grammar (not an unsupported claim of seven recursively learned abstractions)

```text
primitive A = [move_right, move_left]       return to anchor
primitive B = [move_up,    move_down]      return to anchor

macro M = [A, B]                          two primitive cycles
observed = [A,B, A,B, A,B, ..., A,B]      2..7 repeats of macro

metadata:
  motif_size = 2..7 primitive closed cycles
  repetition_count = 2..7 macro occurrences
  primitive_action_count = 2..7 per component
  action evidence = SHA-256 source pins
  progress = resources/capabilities/new information
  debited needs = observed vital-resource losses
```

For a 7-action primitive × 7-component macro × 7 macro repetitions, evidence uses no more than **343 game actions** and **49 primitive cycles**. This is bounded memory, not unbounded self-referential computation. There is **one source-pinned first alert**, while an `active_metacycle` state can update to show all seven observed repeats.

The prototype does **not** recursively infer seven independent levels of abstraction, compress arbitrary programs, or prove a novel mathematical theorem; it handles a precise, falsifiable *two-tier* grammar.

### Conditions that prevent a false alarm

- A genuine gain in known material or a new capability stops claiming the sequence returned to an unchanged structural state.
- A recorded increase in in-game health, nourishment, drink or energy prevents treating the activity as a materially unchanged cycle.
- Any new witnessed terrain information causes the monitor to reset the learning window.
- Unknown visibility in historical replay results in `SUSPECTED_META_CYCLE_VIEW_UNKNOWN`, never "no learning occurred".
- The source-aware monitor can re-synchronize at a **witnessed anchor** following an information gain, rather than combining the tail of one loop and the beginning of another into a false base motif.
- `ABAB` is not a new four-unit fundamental pattern when it is already two repeats of `AB`; phase `AB` / `BA` is treated as the same cycle orbit.
- No action, permission, or particular hypothesis is automatically authorized because of a metacycle alert.

## Goal-dependent information dividend

`goal_probe.py` accepts source-attributed `Goal` declarations with missing facts and desired capabilities, and `Probe` candidates whose predicted answers/enablers carry cost, exposure, permission, reachability, hazard assessment and evidence source.

It issues a *Pareto fiber* of non-dominated **goal-relevant** candidates, keeping alternatives and ties instead of manufacturing probabilities.

- **Relevant, reachable, low-exposure and attributed:** `CANDIDATE_GOAL_PROBE`, **not automatically executed**.
- **Relevant, but unknown safety/access/permission:** `HOLD_UNVERIFIED_ACCESS`.
- **Denied permission, known unsafe, high exposure:** `BLOCKED_PERMISSION_OR_HAZARD`.
- **Novel or interesting but unrelated to the unmet need:** `NOT_RELEVANT_TO_MISSING_GOAL`.
- **Requirement already observed satisfied:** `GOAL_ALREADY_OBSERVED`.

Its small integer `predicted_dividend` is explicitly an **ordinal inspection heuristic based on matched unmet requirements**, not probability of finding food, medical outcome, or actual social benefit. `reenter()` requires a **new source-attributed observation** before a predicted benefit is recorded as achieved. "We expected a water source" cannot silently become "the person drank clean water."

### Game-only live pressure test

We installed and ran the **independently authored** [Crafter 1.8.3 engine](https://github.com/danijar/crafter), reusing the QC-011 recorded-action schema and QC-015 local observation collector.

An explicitly **artificial controlled starting game condition** is set in each of four virtual worlds:
- one passable northern tile;
- one virtual water tile two positions north;
- a passable eastern tile;
- player has **3** in-game drink units;
- both controllers possess an equal privileged nearby-tile sensor.

These are **injected fixtures**, not the agent discovering naturally located water or surviving an unmodified game.

A deliberately broken baseline repeats **A=(right,left), B=(up,down)** and never uses the nearby resource. The second controller monitors nested patterns, discovers `[A,B] × 2` once the initial observed terrain stabilizes, asks what the **goal** is (virtual drinking), and compares *approaching the observed water* with *walking to an unrelated fresh tile*. It then executes a short, already authored virtual water-interaction sequence if supported.

**[Actual successful game run #42753524252](https://github.com/the-static-collective/MOTIF/actions/runs/42753524252):**

| Crafter seed | Blind: game drink / actions | Goal-directed: game drink / actions | First meta alert |
| --- | --- | --- | --- |
| 1042 | **3 / 19** | **4 / 15** | **12** |
| 2026 | 3 / 19 | 4 / 15 | 12 |
| 3199 | 3 / 19 | 4 / 15 | 12 |
| 8765 | 3 / 19 | 4 / 15 | 12 |

That's **136 actual executed Crafter game steps** in eight controlled episodes, where **all four goal-directed episodes increased an actually observed virtual resource**, unlike the blind loop. Every step was serialized, replayed and validated with the **unchanged QC-011 parser**. The relevant observation occurs in the game **after** the action, not merely inside a synthetic prediction.

The four scenarios deliberately share the **same type of injected defect**, and the comparator is intentionally incompetent. The water route is **hand-coded**, not invented through autonomous planning. This proves the wiring of *nested-cycle signal → context-relevant choice → actual game observation*, not superior survival intelligence against a competent agent.

Earlier testing exposed a real bug in the learning monitor: after the first new terrain observation it anchored a primitive at the wrong phase, classifying the entire `[down,right,left,up]` sequence as a single 4-step primitive. That meant no true multi-component metacycle was detected and **no goal action** was selected. The fix added explicitly witnessed anchor re-synchronization, retested on the actual game, and restored **step-12 metacycle detection and witnessed virtual water collection**. Both failure and correction remain visible in GitHub Actions history.

### What is actually useful for MOTIF

This is a stronger research shape than "leave the loop by doing something novel":

```text
Current unmet goal
     |
Detect nested repeated routine
     |
Determine whether the routine made relevant progress / new observations
     |
Identify missing requirement(s)
     |
Generate source-backed candidate probes
     |
Reject unrelated novelty, unsafe exposure and unsourced access
     |
Retain non-dominated low-cost candidates
     |
Execute only under the *separate* virtual game controller's authority
     |
Observe real game-world effects and retain receipt
     |
Re-enter with corrected belief and possible continuation
```

The **next relevant question** is part of the observation record. It does not imply the requested destination/resource exists in the user's actual neighborhood.

## Code and reproducibility

- `meta_cycles.py`: bounded primitive cycle extraction (2–7 actions), 2–7 primitive loops per meta motif, 2–7 repetition tracking, phase normalization, evidence pins, observation veto, cost debt and reference anchor re-synchronization.
- `goal_probe.py`: typed unmet goals, attributable predicted probes, no forced probabilities, multiple Pareto alternatives, permission/reachability/exposure gates, sourced observation re-entry.
- `game_goal_replay.py`: 4 real-game seed scenarios × 2 policies; explicitly patched starting worlds; actual nested detection and actual virtual drinking results; all QC-011-compatible game traces and comparison JSON.
- `test_meta_cycles.py`: synthetic regression tests for all metacycle lengths, multiple repetitions, realigned anchors, false positives and source integrity.
- `test_goal_probe.py`: tests for goal relevance vs novelty, Pareto ties, actual feedback, missing authority, unknown access and world-domain separation.
- `.github/workflows/quantum-code-016.yml`: pure tests, real third-party game execution, **hard asserts** that each controlled goal policy detects a meta pattern, selects the game-only water candidate and genuinely increases its recorded game resource, full QC-011 replay validation and archived evidence.

```sh
cd experiments/quantumcode016
python -m unittest -v test_meta_cycles.py test_goal_probe.py
python goal_probe.py
cd ../..
python -m pip install 'crafter==1.8.3' pillow
python experiments/quantumcode016/game_goal_replay.py
```

## Limits and the next falsifier

- **Two-level only:** the current implementation is a motif of base cycles with repeated macro motifs, not a general recursive language learner. A deeper hierarchy should require independently observed evidence of each new level rather than automatically renaming every action grouping.
- **World sensing is privileged:** terrain comes from the simulator's internal current local world, rather than camera-only perception. Its suitability as a probe is limited to this controlled game.
- **No learned world model:** the game-specific water plan and the ordinal goal scoring are written by a programmer. MOTIF did not independently invent or train a policy from Crafter's human demonstrations.
- **No real-world survival facts:** water in a videogame is not evidence of safe drinking water outside the game. Real-world actions require current local facts, permission, and domain-specific verification.
- **No proof of better planning:** the blind comparator is intentionally defective; independent planners, game-play experts and strong same-information baselines have not been evaluated.
- **Unknown event effects:** the game may have untracked scene changes and stochastic outcomes. No general performance gain across natural worlds is claimed.

**Proposed QC-017:** a *goal-first probe planner* that can derive novel candidate action sequences from typed game prerequisites, with the agent blinded to hidden world cells, and benchmark against a strong classical planner or search policy under matched observations. Detect and repair unexpected effects; do not merely memorize preauthored water-route scripts.
