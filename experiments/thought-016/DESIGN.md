# MOTIF THOUGHT-016 — The Bounded Algorithm Inventor

**State:** Executable offline development experiment, not a new production planner. All generated code remains `PATCH_FOR_HUMAN_REVIEW_NOT_INSTALLED`. Stacked on THOUGHT-015. It changes neither JAR;VIS nor MOTIF's active runtime. Python 3.11, standard library, no model downloads.

## What we tested

Can MOTIF operate a learned diagnostic model as a **developer and tester**, let that model narrow the choice of **composable typed program expressions**, execute *real compiled Python* for proposed programs, select only an independently checked candidate, and challenge it with a separate synthesized counterexample and a frozen holdout?

The previously tested THOUGHT-015 repairs—weighted priority, risk enforcement, resource state for a numeric risk, and relaxing better labels—cannot express **collecting keys to unlock edges**, or revisiting an earlier vertex after acquiring a new key. This is a *new problem family* for the experimental developer. It is not the invention of new mathematics.

## Example of the new reasoning requirement

A route might be blocked by a red-key gate. The traveler can go from vertex `0` to vertex `1`, acquire the red key, return to `0`, and only then traverse the locked edge to vertex `3`.

The valid answer to this small synthetic problem is:

`0 → 1 → 0 → 3`, cost `3`.

A planner treating a vertex as a single visited state will miss this route. A planner ignoring key requirements may return an impossible shortcut.

The new state requires **position × remaining risk × acquired-key set**. This is a standard **product-state graph search** idea, not a novel shortest-path algorithm. We test whether the development mechanism can *construct* it from a typed composition grammar.

## How the model is actually used

`TinyDesignModel` is a trained multinomial naive-Bayes diagnostic classifier, **not an LLM**. The training examples and mechanism labels are human-authored. It reads bounded descriptions of *development failures only*, ranks the two most promising missing mechanisms, then the separate evaluator runs three alternatives: each single mechanism and their pair. When progress is measured, it receives a development-only result and ranks the next round's possibilities. The model cannot see audit or stress examples during those proposals.

The mechanism fragments are **GATE**, **PICKUP**, **KEY_STATE**, **REVISIT**. Rather than selecting any of THOUGHT-015's four repair booleans, the compiler combines typed expressions:

```json
{"op":"subset","args":[{"ref":"edge.need"},{"ref":"state.held_keys"}]}
```

and

```json
{"op":"union","args":[{"ref":"state.held_keys"},{"ref":"arrived.pickups"}]}
```

Together with a state identity incorporating `held_keys` and permission to revisit a vertex in a *different state*, these make a working gated-route program.

The program is a bounded expression AST, **not arbitrary model-authored Python**. `grammar.py` validates an exact schema, permitted references and operators, length and depth. It emits a reviewed fixed Python evaluator with the typed program embedded as inert JSON; a model cannot add imports, write to disk, call subprocesses, introduce shell instructions, or change the objective by issuing an executable command.

The compiler produces executable `reference_solver.py`, `candidate_solver.py`, and a readable unified `candidate.diff`. The separate `oracle.py` uses a finite-state queue relaxation rather than the candidate's heap-priority search, and independently validates the returned path and risk/cost. All problem inputs are bounded, synthetic and non-sensitive.

## Model as a test author

The developer also proposes a **bounded metamorphic test transformation**: remove a key pickup from a fixed development problem and ask whether the purported route is still possible. This first version uses a **pre-designed test operator**, not free-form test invention. The oracle independently determines the expected result; the model's proposed test is never admitted as proof by itself and is **not added to the independent holdout**.

```text
baseline fixed-template algorithm
    ↓
trained diagnostic model → rank two missing mechanisms
    ↓
compile three typed program compositions in scratch
    ↓
evaluate dev cases, safety cases, and model-proposed probe
    ↓
retain one non-regressing candidate in scratch, or HOLD
    ↓
repeat on remaining development failures
    ↓
FREEZE candidate
    ↓
separate random-seed audit and stress graphs + independent oracle
    ↓
reviewable patch / HOLD  (never automatically installed)
```

The model has meaningful influence over **which candidate compositions are tried**. But the compiler, experiment grammar, grading rule, independent oracle and heldout are human-designed. This is a constrained research prototype of a software-development loop, not unrestricted algorithm invention or evidence of consciousness.

## Measured results (frozen development fixtures and synthetic seeded holdouts)

| Cohort | Old restricted reference | New composition |
|---|---:|---:|
| Development | 3 / 9 | **9 / 9** |
| Safety | 3 / 4 | **4 / 4** |
| Frozen audit | 62 / 72 | **72 / 72** |
| Random-seed stress | — | **54 / 54** |
| Developer's bounded removal-of-key probe | — | **1 / 1** |

Two development rounds compose `GATE + PICKUP`, then `KEY_STATE + REVISIT`. The separate audit is evaluated only after the candidate freezes. The **strong classical product-state oracle matches the candidate**; we do not claim the newly composed program outperforms the known correct classical method. The old baseline is deliberately insufficient, and the test design is synthetic and author-created—not external blind evidence of software-engineering skill.

## Limits and safety

- Python `-I -B`, a temporary workspace, timeouts and limited output are **not OS-grade isolation**. The only reason executing generated Python is acceptable within this experiment is that its executable *template is fixed and reviewed* and all model-controlled program data is typed and bounded. **Do not use this harness to execute arbitrary LLM-authored code.**
- Candidate feature selection is influenced by a trained classifier, but the vocabulary and DSL operators were manually designed. One deterministic development specimen cannot substantiate open-ended invention.
- SHA-256 digests support integrity checks on an already trusted source. They do not verify model identity, true evidence, authorization or authorship.
- The oracle checks claimed results rather than trusting confidence or fluent explanations.
- The program may be exported as a **reviewable patch**, never merged, deployed, or connected to third-party tools automatically. `pen_state=UNCHANGED`, `external_authority=NONE`.
- The benchmark compares against the weak prior-plan family and an independently constructed strong classical baseline. Fairer work requires independently authored unseen tasks from other domains, matched CPU budgets, negative controls and an available real generative model.
- The proposer chooses among four *new* fragments and three candidate pairings each round. Its test proposal is drawn from a preauthorized mutation template. Neither constitutes arbitrary executable code synthesis.

## How to reproduce

```bash
cd experiments/thought-016
python -m unittest -v test_thought016.py
python benchmark.py
cat candidate.diff
```

This generates only local research artifacts within this experiment's directory. It does not alter MOTIF's actual reasoning engine or create a pull request from the model's candidate automatically. GitHub commits in this PR are operator-directed publication of the **experiment and review artifacts**, not model-authorized production changes.

## Falsification gates

A report must HOLD if any frozen audit or stress output fails, if safety regresses, if a model attempts to propose an unsupported expression/operator, if source JSON is malformed, if a route violates a gate/risk constraint, or if the fixed-template evaluator cannot be executed. No extra testimony or geometry can promote a result into project truth.

## THOUGHT-017 candidate

For a genuinely harder trial, freeze an *independent* benchmark with new symbolic transition families not represented in this four-fragment vocabulary, ask a locally provisioned generative model to propose safe **new typed primitives or executable source**, and run those in an OS-enforced network-denied container/VM with CPU/memory limits, independent test authors, differential/counterexample search, and manual patch review. The current harness **must not** be extended to run raw model-generated code without that isolation.
