# MOTIF-015 — MANY ROADS (multiplex inquiry)

**Question:** Can a reasoning controller choose to offer an answer and investigate further at the same time; choose several *complementary* answer/check/question avenues at once; and avoid wasting budget on duplicated or unsafe requests?

**Prototype:** Python 3.10+ standard library. No AI models, external actions, live source retrieval, or human questions are actually sent. Everything runs against a synthetic, finite, deterministic hypothesis fixture. This is an independently reviewable experiment, **not** operational multi-agent autonomy.

## Why this differs from one-best-question reasoning

A fixed one-step selector chooses the avenue with the best individual expected decision improvement. But two questions can be jointly decisive even if either one alone tells us nothing about the correct decision.

Given four equiprobable synthetic worlds `00, 01, 10, 11`, the target answer is `YES` when exactly one bit is set (XOR), otherwise `NO`:

- `LEFT` asks for the first bit: *alone* the best answer is still 50% accurate.
- `RIGHT` is a separate answer-computation avenue determining the second bit: *alone* 50%.
- `BAIT` checks whether the state is `00`: *alone* expected decision accuracy is 75%.
- `DUPLICATE_LEFT` repeats the first question from the same declared source; it must not create extra evidence or consume a second slot.

With a two-probe budget, greedy one-step selection takes BAIT first; joint batch selection chooses LEFT+RIGHT and can resolve the target answer exactly. This is an intentionally simple constructed counterexample, not a measured improvement on real workloads.

## Interfaces

- `Avenue`: name, one of `ANSWER` / `ASK` / `VERIFY`, cost, proposed source, hypothesized observation per candidate world, human-attention flag, allow/hold gate, text prompt.
- `choose`: exactly enumerates allowed batches of at most 12 candidates, bounded by total cost, number of concurrent slots, and human-question count; maximizes **expected final decision accuracy minus probe cost**. Uses **joint observation signatures**, not independent marginal information gain. `ANSWER_AND_EXPLORE` is a valid mode when a tentative answer is already justified and further inquiry still has value.
- `execute_synthetic`: submits chosen read-only simulator callbacks to a thread pool concurrently; returns results in deterministic proposal order. This is actual concurrent dispatch in the test, not serial simulation, but it is **not** external actuation.
- `revise`: conditions on received synthetic answers without injecting the evaluator's hidden true world into the planner. An impossible result produces `HOLD_MODEL_FALSIFIED` rather than fabricated certainty.

## Reproduce

```sh
cd experiments/015
python -m unittest -v test_multiplex.py
python demo.py
```

The six tests cover a synergistic batch versus greedy one-question selection, safety and attention limits, real parallel callback dispatch, preservation of tentative answers during inquiry, falsification HOLD, and malformed inputs.

## Boundaries and the next honest falsifiers

1. **No learned question generation yet.** These are hand-designed possible observations for a small hypothesis family. The planner is never allowed to see the secret world; the simulator sees it only during response execution. No evidence of original intelligence or cross-world generalization.
2. **No reliable source authentication.** The `(origin, predicted-signature)` deduplication only blocks exact same-declaration duplicates. Different correlated sources, adversarial replies, noisy questions, missed completions, timeouts and conflicting observations require explicit probabilistic modeling, ideally an interface with 014W's evidence organ.
3. **No real conversation orchestration.** `ANSWER`/`ASK`/`VERIFY` describe avenues, not verified real responses or tool permissions. Human-question limits constrain proposal selection, but callbacks are purely synthetic and cannot solicit a person.
4. **Exact enumeration doesn't scale.** At most 12 avenues in the current implementation; larger real tasks require candidate generation, adaptive submodular approximation or Monte Carlo search with strong controls.
5. **No capability gain term yet.** This maximizes decision accuracy, not the expected number/value of new useful actions unlocked. Integrate MOTIF-003's reachability frontier and strong planning baselines to test that contribution separately.
6. **Compare fairly.** Freeze genuinely unknown world families with stochastic correlations, lagged answers, conflicting reporters, noisy channels, and changing goals. Compare against greedy one-step, best fixed two-probe diagnostic, exact Bayesian batch selection, Bayesian sequential selection, and matched-budget search. Score decision accuracy, calibrated log loss/Brier where applicable, costs, time, regret, risk-coverage, duplicate evidence and negative transfer; preserve failed worlds.
7. **No automatic authority.** No inference cartridge or checked hash authorizes network requests, edits, or external actions. Any future external adapter requires its own explicit scoped authorization and receipts.

The purpose here is narrowly falsifiable: **MOTIF can represent a concurrent portfolio of complementary avenues, potentially answer and investigate simultaneously, and avoid the specific greedy-selection trap above.**
