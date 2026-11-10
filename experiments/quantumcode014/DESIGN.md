# QC-014 — THE STAGNATION BREAKER
## "Insanity prevention": stop repeating ineffective actions, recover the missing prerequisite, then try something that can work

**State:** Tested research draft, stacked on QC-013; no production merge or deployment. The phrase "insanity prevention" is the user's colloquial description of **adaptive action-loop failure detection**, not a psychiatric claim.

## The conceptual frontier

A goal can remain unmet for reasons that differ sharply:

- An action is *available and progressing*, even if it must be repeated (walking, long-duration work, time-dependent processes).
- An action can be *repeated with no relevant effect* because an unnoticed prerequisite is absent.
- An action can have *unobserved partial effects* even if the immediate inventory has not changed (combat damage, fatigue, exposure, waiting).
- The world can change between attempts, warranting a fresh test.
- A proposed repair can require a longer chain of **enabling actions**, not simply another attempt to finish the original goal.

**MOTIF must not equate "repeat" with "failure".** It should ask whether an attempted action produces task-relevant traction under an evidence-defined action contract, then investigate why its preconditions are missing when it does not.

```text
GOAL
  |
ACTION A x3 (observe outcomes, not imagined results)
  |
No task-relevant effect? ── NO ──> continue / update evidence
  |
 YES, and action signature has immediate expected effect
  |
Issue STAGNATION receipt, temporarily hold A
  |
Find the smallest *verifiable* missing prerequisite
  |
Ask / inspect / acquire that prerequisite by a bounded safe action
  |
Was the prerequisite actually observed to change?
  ├── YES → release A for a new test
  └── NO  → consider alternative goal or return a human-visible HOLD
  |
Preserve both failed history and successful later correction
```

This is a narrow proof of **failure-driven question generation and repair**. It is not general autonomous self-improvement or a proven production cognitive architecture.

## 1. Real historical failure replay — 161 failed crafts

Our preceding QC-013 game experiment recorded **161** attempts at `make_wood_pickaxe` in one 220-step human-informed playthrough. The avatar possessed one unit of wood but was no longer near the crafting table, so the game could not fulfill the recipe. The controller mechanically repeated the command instead of investigating the missing condition.

The original complete data are independently archived under:
- [GitHub Actions #42743549945](https://github.com/the-static-collective/MOTIF/actions/runs/42743549945)
- [Full actual game telemetry artifact #13730685595](https://github.com/the-static-collective/MOTIF/actions/runs/42743549945/artifacts/13730685595)

`observed_qc013_stall.json` is a reduced, source-hash-pinned excerpt extracted from that original game trace, not an invented replacement for the original ZIP. It records the full-archive SHA256 and the selected JSON member SHA256, 161 attempts, and the actual first three failures at **game steps 17, 18, 19**.

**QC-014's detector identifies task nonprogress at step 19**, as soon as the third ineffective attempt has occurred, without needing to see later actions. The original remained stuck through several more bursts, including one continuous **44-step** block.

The detector doesn't assume the cause from the repeated failures alone. The `diagnose_craft` subsystem checks the **game's actual recipe rules** plus observable nearby utility state to distinguish:
- missing materials;
- missing nearby crafting equipment;
- unknown utility presence; and
- preconditions that appear satisfied, requiring a new hypothesis.

That distinction matters: **detection is evidence of repeated nonprogress, not proof of a particular cause.** The explanation must still be checked.

## 2. Actual independent game engine — repeated correction experiment

We ran the real [Crafter](https://github.com/danijar/crafter) game engine (version 1.8.3) with an explicitly **controlled, manually constructed game-state fixture**: each episode starts with wood, a previously placed crafting table **three or more reachable game tiles away**, and an unavailable wooden pickaxe. A deliberately defective controller continuously requests `make_wood_pickaxe` without checking whether the table is nearby.

Both policies begin with the **same injected game world and 30-step maximum**:
- **Blind retry:** repeatedly issues `make_wood_pickaxe`.
- **Guarded repair:** observes actual task outcomes, detects failure after 3 attempts, consults the canonical game recipe, finds the table using the existing declared privileged nearby-tile sensor, walks back to it, verifies the prerequisite, and retries crafting.

**[Verified CI game run #42747058048](https://github.com/the-static-collective/MOTIF/actions/runs/42747058048)**:

| Game seed | Blind retry | QC-014 guarded repair | Verdict |
| --- | --- | --- | --- |
| 1042 | **30** attempted commands, **no pickaxe** | Pickaxe crafted at **step 6** | Repair |
| 2026 | 30, no pickaxe | Pickaxe at step 6 | Repair |
| 3199 | 30, no pickaxe | Pickaxe at step 6 | Repair |
| 8765 | 30, no pickaxe | Pickaxe at step 6 | Repair |

This is genuine execution against an externally authored game, but it is a **fault-injection test**, not a naturally occurring 4-seed survey of crafting problems. The table/wood/achievement initial conditions are explicitly injected by the test harness; do not present them as earned by the controller. The four worlds use similar targeted failure constructions, so the four positive corrections are not evidence of general policy performance.

The guarded policy has **extra canonical recipe knowledge** on detecting a failure and both policies retain a privileged local tile sensor. The result establishes that the detector and repair can execute through the game rules under these constrained test conditions. It does **not** establish a fair learned-policy advantage over a source-equipped independent competitor.

### Natural world runs — important contrary evidence

We also ran the *same* QC-013 human-informed game heuristic with and without the generic watchdog on normal starting worlds, each capped at 220 steps. No artificial crafting table or wood was injected into these four natural scenarios.

| Seed | Baseline game steps | Guarded game steps | Interpretation |
| --- | ---: | ---: | --- |
| 1042 | 195 (health 0) | **220** (health 9) | Guarded survived to experiment cap |
| 2026 | **220** (health 6) | 193 (health 8) | Guarded ended earlier; fewer steps |
| 3199 | **215** (health 0) | 213 (health 0) | Similar failure |
| 8765 | 208 (health 0) | 208 (health 0) | No meaningful difference |

**Mixed results.** A failure guard alone is not a general survival policy. It can help with specific blocked actions and still make a worse decision in another situation. The seed 2026 regression is a required next investigation, not something to hide.

All comparisons remain small and exploratory, with the game's stochastic updates and no independent policy-training setup. A 220-step cap does not imply permanent survival.

The run executed **1,816 genuine Crafter engine steps** across 16 episodes; all full game traces passed the **unchanged QC-011 parser** and were archived. The virtual action traces have no authority concerning real-world medical, animal or material safety.

## 3. Code and controls

`insanity.py` — reusable, environment-neutral observation contract:
- `Snapshot`: resources, milestones, position, optional facing and observed time.
- `Observation`: append-only source-pinned before/action/after step.
- `assess()`: **action-specific outcome signatures**, never infer success from an unrelated health/drink timer; successful `make`/ `place` requires resulting item/achievement; `move` may count position or orientation; repeated `do` combat and `sleep` are labeled **UNRESOLVED** rather than falsely called failures.
- `StagnationGuard`: threshold of three consecutive evidenced nonprogress attempts, one historical alert per unchanged relevant signature, explicit action HOLD, and release only after newly attributed evidence. A new plan step is not implied merely by a time delay.
- `diagnose_craft()`: checks a **source-owned game recipe** and actual prerequisites, exposes a named missing-condition research question and zero outside effects.
- `inspect_qc011_replay()`: reads existing QC-011 game action records without playing the game; no automatic action rights.

`game_loop.py` — real Crafter adapter:
- Runs both the controlled failing construction and ordinary seeded games.
- On a held craft request, checks actual game recipe requirements, looks for the missing table, requests a bounded search, and retries only if the conditions actually change.
- Limits recovery searching to 18 steps before reporting a HOLD; it does **not** infinitely recurse into another exploration plan.
- Records actual next-state telemetry, attributed actions, diagnoses, and full QC-011 compatible replay JSON.
- **Does not run a trained neural network or publish any physical-world survival instructions.**

`test_insanity.py` — **31 tests** of immediate versus delayed effects, false-positive control, unknowns, repeated task failure, source attribution, bounded retries, explicit release and QC-011 generic replay shape.

`test_archived_case.py` — **5 tests** of the reduced actual QC-013 source-pinned failure excerpt; first alert at step 19, never requires looking ahead.

`.github/workflows/quantum-code-014.yml` — runs all tests, installs real Crafter 1.8.3, runs all 16 actual game episodes, revalidates every real trace using unchanged QC-011 `ingest.read_bundle` and uploads raw game-only action evidence.

### Reproduce

Python 3.11:

```sh
python -m pip install 'crafter==1.8.3' pillow
cd experiments/quantumcode014
python -m unittest -v test_insanity.py test_archived_case.py
cd ../..
python experiments/quantumcode014/game_loop.py
```

Results: `runs/crafter-qc014/` (not tracked in source control).

## What we have — and don't

**Demonstrated:** An agent-independent monitor detects and interrupts a verifiably ineffective repeat, asks for missing prerequisites, restores a resource in an actual third-party game, and resumes to complete the formerly impossible action. It distinguishes valid repeated action and hidden-delay mechanics.

**Not demonstrated:** An open-ended general solution to all infinite loops or planning failure; discovery of arbitrary unknown game rules; training a neural model from the 100 expert traces; automatic recognition of all cyclic/oscillating plans; player-independent, fair statistical policy advantage; autonomous high-level self-improvement; improvement of real-life survival or medical outcomes.

A strong future test would require a domain-neutral **progress contract** for every action type, detection of A↔B cycles even when individual actions move the character, external witness outcomes, withheld domain rules, and matched-information comparisons with competent controllers.

### Transfer back to the user's real-world insight

The relevant abstraction is **not** "if the person still lacks the resource, repeat the recommendation." It is "the person already understands the need; which missing capability prevents success, and what new, physically possible action might supply that capability?"

That principle has immediate conceptual relevance to food access, transportation, repairs, veterinary access, equipment and shelter—but **nothing in Crafter establishes a safe or effective real-world intervention**. Apply it to the real world only with actual local evidence, consent, conditions, safety and permission.
