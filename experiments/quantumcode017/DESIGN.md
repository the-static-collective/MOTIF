# QC-017 — THE SELF-DIRECTED PROBE PLANNER
## From goal and current observations to generated actions, actual consequences, and repair

**Research-only draft; stacked on [QC-016 #238](https://github.com/the-static-collective/MOTIF/pull/238).** Not merged to production. No native reLATTE crossing or effect outside an instrumented computer game. No user housing, health, animal or legal detail was used or published.

## The question

Can MOTIF **construct** a source-grounded action sequence from a declared goal, a partial game observation and supplied game operators—rather than merely choosing a previously scripted action sequence?

Yes, on a **narrow, classical planning problem**: collect water or wood from local observed terrain in the independently authored [Crafter](https://github.com/danijar/crafter) 1.8.3 survival game. No route is hard-coded for any of the test layouts. `plan.py` does a bounded BFS over virtual states `(player position, facing direction)`, evaluates the known effects of four movements, and terminates with a game-resource interaction `do` if the target is actually observed and approachable. It only plans through **seen, currently passable cells** and respects the difference between walking to a cell and turning to face a solid resource.

The action grammar and mechanics are **programmer supplied**, not autonomously learned from the 100 expert recordings; BFS is a classical algorithm, not novel mathematics or evidence of superior general reasoning. The current source is a privileged 7-tile engine sensor, not visual understanding from screen pixels.

```text
Declared game need: get water / acquire wood
    |
Observe only the current radius-7 tile aperture
    |
Construct typed evidence record with source SHA256
    |
Search (position, orientation) action graph with BFS
    |
Propose shortest known feasible sequence or HOLD
    |
Execute first allowed virtual action in actual Crafter
    |
Read real game result and rebuild belief
    |
  if observed new obstruction -> recompute route
  if repeated physically ineffective move -> HOLD
  if observed actual resource gain -> goal attained, source-pinned receipt
  else continue within bounded game-action budget
    |
Preserve complete QC-011 action-level trace and result
```

## Actual executable pressure test

**[Successful CI #42755678566](https://github.com/the-static-collective/MOTIF/actions/runs/42755678566)** on commit `7e35ab7157755c83c6353e939a2ae1b018d70667`:
- **23 unit tests** passed.
- **56 actual Crafter game episodes** (4 declared game seeds × 7 scenarios × 2 controllers).
- **388 real game-engine actions** executed and verified with the **unchanged QC-011 replay parser**.
- **24/24** observed-resource QC-017 BFS goal episodes actually collected the declared resource in Crafter. Four hidden-resource cases properly **HOLD** rather than inventing visible access.
- **12/24** visible-resource cases succeeded with the separate **Manhattan greedy comparator**. This comparator is deliberately unsophisticated, not a matched-capability classical planner or machine-learning baseline.
- Four unexpected-obstacle cases rerouted after the actual in-game map was changed *between two action observations*, and then reached the resource.

**[Evidence artifact #13735651819](https://github.com/the-static-collective/MOTIF/actions/runs/42755678566/artifacts/13735651819)** contains every executed action's before/after game telemetry, a separate planner-decision log, controlled world patch declaration, per-episode result and cross-episode comparison. The ordinary source files do not contain game videos; no game video was scraped.

| Deliberately injected scene | Goal | Generated BFS | Greedy comparator |
| --- | --- | ---: | ---: |
| North water source | drink | **4/4**, 3 game steps each | 4/4, 3 steps |
| East water behind 2 rock tiles | drink | **4/4**, 6 steps | 0/4, repeated blocked moves |
| South water source | drink | **4/4**, 3 steps | 4/4, 3 steps |
| West water behind 2 rock tiles | drink | **4/4**, 6 steps | 0/4, repeated blocked moves |
| Previously open path becomes blocked after first step | drink | **4/4**, 7 steps, recomputed | 0/4 |
| Tree at a diagonal position | wood | **4/4**, 4 steps | 4/4, 5 steps |
| Resource *outside* observation aperture | drink | **4/4 correctly HOLD without any game actions** | also 4/4 HOLD |

The resource outside the observation aperture exists in the **researcher-edited simulator**, but neither controller is allowed to infer its exact position from that privileged setup. This is an explicit negative test for hallucinated availability. All access and safety statements here concern **game tiles only**.

### A real test failure caught a genuine experimental design error

Our first actual executable run passed all pure planning tests but produced **zero successful game goals**, while the game reported each attempted move as a no-op. The full output and initial unsuccessful evidence were archived in [run #42755404288](https://github.com/the-static-collective/MOTIF/actions/runs/42755404288). Inspection found that the test-harness method for clearing obstructing game objects had accidentally **deleted Crafter's player object from the engine's active object list**, disabling the game's update of all player commands.

This was **not** a failure of BFS planning, and initial CI incorrectly showed success because it only asserted trace formatting and episode counts. We:
1. Corrected the fixture to preserve the actual player object.
2. Added a fail-fast player-object registration check.
3. Strengthened CI to assert **every** visible-goal outcome actually gained the game resource (24 successes) and dynamic-obstacle episodes actually recomputed their route.
4. Re-ran the **real** third-party simulator successfully.

This is an important demonstration of the project philosophy: **a passing test suite that never checks the real-world effect of its simulated action is insufficient evidence of useful intelligence.** Source-pinned game receipts can challenge our methods as well as the planner.

## How the planner works

`plan.py` is a pure function and has no execution authority. It accepts:
- `Belief`: witnessed game position, facing, current observed tile coordinates/materials/occupancy, source refs;
- `goal`: one of two *predefined* game tasks (`game_drink_obtained`, `game_wood_obtained`);
- bounded declared operators: movement changes facing and moves only onto known passable game terrain, or changes facing toward a solid observed resource; `do` is modeled as a candidate interaction only when the player is facing a witnessed nearby goal resource.

It returns either `PLAN_CANDIDATE` with shortest *model* actions, or a typed HOLD:
- `HOLD_NO_OBSERVED_GOAL_RESOURCE` when no target exists in the permitted sensor view;
- `HOLD_OBSERVED_NO_VERIFIED_PATH` when a seen target has no verified passable approach.

It does not infer or traverse unobserved shortcuts, invent permission, make claims about human health or food and water safety, or guarantee a future game effect. A real `check_goals()` compares **actual game resource/achievement values after execution** before concluding progress.

The runner `real_game.py` replans from the latest observation at every step, so it can respond when its predicted path becomes obstructed. The dynamic-obstacle experiment explicitly inserts a new rock **after** executing the first game action. The planner's next pass uses a fresh sensor receipt, generates an alternate route, and succeeds for all four injected seed scenarios. This is adaptive recomputation from evidence, not independent learning of new game physics.

Safety/epistemics:
- action plans limited to **18** game steps, search capped at **5,000** expanded states, sensor at **7** tiles;
- no unseen targets or path segments allowed;
- two identical no-effect actual actions in sequence trigger a HOLD;
- owner/source pinned input and real-game source receipts are separate;
- research runner acts **only inside independent Crafter**; no computer access or service is opened on behalf of a real human;
- goal selection is currently supplied to the planner, not autonomously inferred from psychological needs or personal data.

## Reproduce

Pure tests use Python 3.11, standard library only:

```sh
cd experiments/quantumcode017
python -m unittest -v test_plan.py
python plan.py
```

Actual third-party engine experiment:

```sh
python -m pip install 'crafter==1.8.3' pillow
python experiments/quantumcode017/real_game.py
```

Results under `runs/crafter-qc017/`; CI also verifies each nonempty recorded episode through the existing QC-011 parser and uploads the full evidence artifact.

## What this does NOT establish

- The demonstrated BFS planner **is classical search** with supplied game-rule operators. It has not invented a general-purpose new planning algorithm.
- No competing strong planner (A*, Dijkstra, PDDL solver, MCTS, human expert or trained agent) has been benchmarked under matched information. The greedy comparator is intentionally weak.
- All virtual worlds are **researcher-patched geometric fixtures**: all local initial terrain was reset to grass, walls/targets added, and player survival stats set to permit measurement. There is no claim about unmodified, stochastic survival-game performance or outcomes on real unfamiliar maps.
- The sensor reads Crafter world tiles from engine internals, much more privileged than a human's on-screen view; no camera-based discovery has occurred.
- Goals and available game operators were supplied by a programmer; MOTIF has not yet learned action dynamics from its human expert dataset nor autonomously proposed general new skills.
- Resource interactions in game have **zero authority** as real-world drinking, construction, hunting, health or social aid advice.

## Next meaningful falsifiers

A rigorous next generation would replace researcher-authored resource mappings and obstacle layouts with **naturally generated, held-out world tasks**, implement an action observation model from actual in-game evidence, compare with a strong planning baseline sharing the same vision, and jointly select the next *question* and possible action when the goal is not yet visible. It should demonstrate **whether the agent can learn or revise an operator precondition from unexpected outcomes**, not only reroute around a newly observed wall.

**Source-law:** an executable plan matters only when independently observed consequences justify the claim of progress. The criterion for success is not that the model proposed a convincing route; it is that a separately controlled world gave verifiable feedback.
