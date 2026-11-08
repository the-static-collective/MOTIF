# MOTIF NEXT-STEP-001 — Ask forward; do the safe next thing

**Experimental, local, synthetic.** This is a concrete first implementation of a user-requested interaction pattern:

**Answer-ish → orient what is known / unknown / identifiable → nominate the next useful question → execute a permitted action to answer it → return the result with a receipt.**

The system does **not** ask the user to re-prompt for each safe step. It takes at most three bounded, deterministic, read-only computational steps. It does **not** execute outside actions, visit websites, contact humans, acquire independent truth evidence, learn arbitrary natural language, or claim general autonomous capability. For now its domain is the existing MOTIF `WITNESS-CHAIN-001` toy witness model.

## Why this is a distinct cartridge

Earlier MOTIF investigations could nominate possible inquiries and produce query-relative conclusions, but the human still had to direct the next turn. This cartridge implements a bounded *follow-through* controller:

1. **Orient:** `orient` extracts the requested answer's evidence status, what is conditionally answerable, what is unidentifiable, what additional evidence might be needed, and an evidence digest. `F`, `I` and `HOLD` are not conflated.
2. **Nominate:** `nominate` proposes *questions* paired with registered, concrete computational actions. The available questions respond to the actual state. No independent source is fabricated.
3. **Select:** `rank` orders by a declared relevance-first policy under a separate computational budget; unknown/effectful/unjustifiably pre-admitted proposals cannot pass the admission filter.
4. **Act:** `_execute` is an allowlisted dispatcher, not `eval` or a general tool call. Local operations answer a narrower question, check global symmetry exhaustively, calculate a hypothetical information-gain probe, challenge a reference *in a copy*, or recount finite evidence using upstream FIR receipts.
5. **Show:** `advance` returns the initial orientation plus each self-nominated question, rationale, concrete action, result, status, input/output digests, budget and honesty flags; no automatic repeated steps beyond `max_steps <= 3`.

The two budgets are **different**: `Goal.budget` is a local analysis budget; `Goal.inquiry_budget` is merely an affordability ceiling for **designing** a future synthetic verification. The latter is never spent and no verification is dispatched. This distinction prevents a plan being mistaken for an executed external experiment.

## Example: asking which witness is right

Input: 100 independently generated *synthetic* triple-witness events from `WITNESS-CHAIN-001`, with no trusted reference. The original absolute polarity question cannot be answered because the model is globally flip-symmetric.

`NEXT-STEP-001` automatically performs three additional **local computations**:

- **Next question:** *What useful relationship can we answer now, without assuming absolute truth?* → Runs relative-alignment inference and returns a conditional model estimate.
- **Next question:** *Could any number of ordinary independent triplets resolve the ambiguity?* → Exhaustively compares the likelihood under every model and its global flip for all 8 observed triplet patterns, 64 comparisons total. The equality survives every comparison in the declared finite grammar.
- **Next question:** *Which permitted verification would most reduce uncertainty next?* → Runs `propose` from `WITNESS-CHAIN-001`, with expected information gain and cost. **The proposal is not executed**, and no authenticity receipt or external observation is collected.

With conditional fixture reference receipts, the next question changes: *What remains justified if the reference is challenged?* The engine runs a copy-only counterfactual and reports the original versus the reopened model.

## Tests / reproducibility

```sh
cd experiments/nextstep001
python -m unittest -v test_nextstep.py
python nextstep.py
python benchmark.py
```

Python 3.10+, standard library, stacked `experiments/witnesschain001/` and its dependencies. The GitHub workflow runs the previous mathematical suites and the new cartridge suite.

A fixed **8 hypotheses × 5 seeds = 40 synthetic-world** sweep checks protocol behavior, not intelligence or real-life usefulness. Expected local observations: 120 read-only computational steps, 40 exhaustive finite-symmetry checks, 40 hypothetical verification designs without collecting truth, **zero** external actions and **zero** ledger mutations. No score from the sweep can establish that users will find the nominated questions best.

## Known limitations / next integration

- This version uses **five handcrafted questions and local handlers** for a single finite witness domain. It does not generate arbitrary follow-up questions in natural language, discover any domain's action semantics, or know a human's goals without an explicit `Goal`. `relevance` is a developer-declared heuristic, not trained user preference.
- Upstream source roots and fixture truth claims are **not authenticated**. A correct-looking model estimate does not license a real-world fact.
- A finite exact symmetry check is admitted only as a property of the declared eight-hypothesis model, not the outside world.
- Checking whether a verification would be informative is **not** conducting the verification. Future real adapters must individually declare read/write/irreversible effects, permissions, execution receipts, and independently verified evidence before acting.
- This is a read-only experimental branch; no code was deployed as an agent and no previously merged components were modified.

**Frontier:** Connect typed, verified read-only adapters for MOTIF-003 affordance exploration, ALEX evidence lookup and JAR;VIS tasks, and evaluate which self-nominated questions materially improve a human's task outcome against baseline suggestions and comparable classical policies.
