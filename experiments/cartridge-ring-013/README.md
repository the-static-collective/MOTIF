# MOTIF RING-013 — The Value of Not Knowing **and the Value of Doing Next**

**Research question:** When ambiguity is the normal state of understanding, should MOTIF ask for clarification, inspect more evidence, conduct a small safe experiment, continue experimenting, or stop? Can it decide that a reversible trial is **interesting and valuable enough to run now**, without first forcing a single interpretation?

**Implemented answer:** Yes, as a **bounded, read-only/reversible local simulation** with a declared utility and budget model. The program can automatically choose and execute simulated, safe research trials when their predicted immediate benefit **plus future option value** exceeds resource, attention, downside and opportunity costs. It can perform another test after receiving a simulated result. It can also STOP when further curiosity is not worth its cost. It never interprets a guessed linguistic directive as authorization for external effects.

**Status:** Draft stacked research branch on RING-012. No deployment, merge, user-account connection, GitHub source edits from the action planner, messages, file writes to external workspaces, financial transactions or other external effects. The only autonomous executions are controlled test-simulator functions in CI and local runs.

## The central distinction

An interpretation can remain ambiguous while its best **next *safe* experiment** is already clear.

```text
          AMBIGUOUS QUESTION / GOAL
                     │
      RING-012 SET OF POSSIBLE MEANINGS
        + PERMANENT OPEN-WORLD OTHER
                     │
  Source-authored viability prior (NOT language truth)
                     │
                  RING-013
         FINITE NEXT-MOVE EVALUATOR
             ┌────────┼────────┐
             ▼        ▼        ▼
         INSPECT    SMASH     STOP
        read-only   bounded   no more
        evidence    dry-run   action
             │        │
             └────┬───┘
                  ▼
        OBSERVE ACTUAL SIMULATED RESULT
                  │
                  ▼
          UPDATE UNCERTAINTY
                  │
                  ▼
    IS ANOTHER STEP STILL WORTH DOING?
```

There is also a **simulated** `ASK_USER` option with a declared user-attention cost. It never asks the actual user during automatic evaluation. And there is a high-reward symbolic `EXTERNAL_COMMIT` trap. That action cannot reach the executor, regardless of its tempting modeled value.

### What exactly is valued?

For each allowed action (a), the decision model evaluates a finite-horizon quantity conceptually equivalent to:

```text
V(a | evidence) =
    expected simulated useful work
  + expected newly available future options × option weight
  - time / compute / human attention costs
  - downside-risk penalty
  + curiosity weight × expected information gain
  + expected value of the best LATER safe action after its observation

STOP = 0; only do an optional action when its value is positive.
```

The **future-action term** matters: sometimes a short inspection or trial has no immediate payoff but changes which later action is worth pursuing. The planner uses a three-step finite-horizon Bellman lookahead, updates the probability of authored synthetic `USEFUL`, `UNHELPFUL`, and `SURPRISE` worlds from observations, consumes a budget, and does not repeat a completed experiment.

The alternative `SURPRISE` state remains possible. Neither the linguistic models nor the synthetic viability model establish historical truth, genuine personal preferences or real-world impact.

### Source-language grounding: it actually reads RING-012

`freeze.py` reconstructs and validates the frozen **RING-012 ambiguity-native lattice** and its original RING-011 nested binder. Each scenario's source utterance and externally supplied speaker/event/carrier are passed to RING-012, which executes its three reviewed, **correlated** source methods and retains their candidate interpretations and disagreements. RING-013 never treats their agreement as three independent witnesses.

RING-013 uses the *width* of that modeled ambiguity as a conservative, author-selected way to widen separate action-viability priors toward the `SURPRISE` state. This is a **heuristic link between two separate authored toy worlds**, not an empirically established causal link between uncertain semantics and lower action usefulness. Nothing about `REQUESTED_BY_ROOT` directly authorizes a tool call.

The action simulator gets the hidden viability label only **after** the chosen action has been selected. The planner sees only a declared prior, possible observation distributions, candidate costs/gains, existing source-lattice uncertainty and its own subsequent observations.

## Permitted actions and the exact "just smash" rule

| Candidate | Allowed autonomously in RING-013? | Meaning |
| --- | --- | --- |
| `INSPECT` | **Yes, simulation** | Perform a bounded information-only synthetic probe. |
| `SMASH_A` | **Yes, simulation** | Execute a cheap, reversible test and observe its synthetic result. |
| `SMASH_B` | **Yes, simulation** | Execute a second, more expensive reversible test if still worth doing. |
| `ASK_USER` | Only as a **simulated** decision option | Model possible value and cost of asking; never actually interrupt the person in this experiment. |
| `STOP` | **Yes** | Preserve uncertainty and exit with no further cost. |
| `EXTERNAL_COMMIT` | **Absolutely not** | An intentionally high-reward forbidden-effect adversarial example. Rejected before execution. |

**"Interesting enough" means positive modeled *net value after comparing safe alternatives*, not merely novelty or an instruction that sounds exciting.** An action must fit the finite time/compute budget, use an allowed simulated permission tier, and beat STOP. Even a beautifully phrased or apparently certain instruction does not relax the action-permission boundary.

## Calibrate, freeze, and test

**Model selection data:** 24 author-generated training scenarios plus 24 development scenarios. The source priors, task reward values, hypothetical future options, observation models and hidden viability labels were all explicitly authored for a sandbox. 24 value-function settings were executed. After observing development outcomes, the selected parameters were **frozen**:

```json
{
  "information_weight": 0.0,
  "affordance_weight": 1.0,
  "risk_weight": 0.7,
  "ambiguity_sensitivity": 0.4
}
```

This is itself an interesting finding: the synthetic selection preferred weighting **useful future options** and downside caution, but **did not reward information gain for its own sake**. It can still obtain information as a means to better later actions through the Bellman continuation term. It does not mean information has zero value in the real world.

Development-selection score was **+133.65 authored utility units** across 24 scenarios. That number was used to select the policy and is **not independent evidence of generalization**.

**Post-freeze source:** three *new-to-model-selection* authored task families: 20 novel-language scenarios, 20 misleading-prior scenarios with unfavorable hidden outcomes, and 20 scenarios where pure curiosity yields no useful work or new options. Labels enter only the outcome simulator and post-freeze scorer. Test templates and labels come from the same experimenter, not independent humans.

### Measured outcome: 60 synthetic scenarios

| Decision strategy | Realized modeled utility (sum) | Local simulated SMASH actions | Novel modeled options | Cases with negative utility |
| --- | ---: | ---: | ---: | ---: |
| **RING-013 finite lookahead frontier** | **+76.86** | **45** | **77** | **17** |
| One-step GREEDY value | +48.94 | 39 | 69 | 15 |
| Fixed SMASH_A candidate *only when expected value remains positive* | +12.98 | 26 | 32 | 15 |
| ASK_FIRST when its modeled value is positive, then continue | **−5.50** | 7 | 23 | 11 |
| Always STOP | 0.00 | 0 | 0 | 0 |

**Important:** `ALWAYS_SMASH` is the strategy's internal fixture name, but it still applies the decision floor `expected_net > 0`; it is *not* a real-world blindly-always-smash policy. Likewise, the ask-first control can choose STOP rather than incur a negative expected action cost.

The frontier beat these particular baselines on the selected author's **aggregate utility metric** while producing **17 negative-utility cases**, two more losing cases than greedy. Its gain is not risk-free, and on another distribution or utility preference it could lose. There is no statistical significance claim or independent real-world outcome calibration.

All numbers are **synthetic utility units and hypothetical future options**, not dollars, saved lives, new GitHub features, measured computing speed, verified societal impact or the user's actual preference ranking.

An impossible perfect-information safe-trial upper bound is **+190.69** synthetic utility units. The difference from +76.86 is evidence of uncertainty and missed opportunities, not a promise of future performance.

In the 60 heldout cases, the chosen policy ran **45 simulated reversible SMASH actions**, **zero actual user interruptions**, and **zero effectful external actions**. The observed action sequence and posterior update after each local simulated trial are in machine-readable receipts. It selected no extra standalone inspections in this source distribution; information was learned as a side effect of the selected safe trials.

## Method and evidence

- `scenario.py`: explicit task prior, hidden synthetic viability, reward/affordance alternatives, observation likelihood, bounded budget, and deliberately forbidden external action.
- `value.py`: executes RING-012 ambiguity source methods; broadens source opportunity priors conservatively; performs finite, bounded lookahead over useful action, learning and further action; runs only isolated author-simulated effects and logs each result.
- `freeze.py`: calibrates the small value model against source-authored train/development outcomes, binds RING-012 model provenance and freezes all selected parameters before importing the next challenge.
- `novel.py`: three separate authored generalization and value-miscalibration challenges.
- `trial.py`: evaluates five decision strategies on the **same 60 cases**, preserving complete per-action trajectories and including an impossible perfect-information bound for perspective.
- `evidence_graph.py`: verifies every case-level realized value, action permission, simulator status, option count, simulated question cost, negative-result tally, aggregate result and source-policy receipt before creating multi-head provenance hyperedges for **progress AND its costs**.
- `test_value.py`, `test_evidence.py`: tests that positive-value simulated action truly runs, negative-value action stops, source uncertainty remains open, choices consume budget, effectful actions cannot pass, and forged error/permission receipts fail.

### Reproduce

```sh
python -m unittest discover -s experiments/cartridge-ring-013 -p 'test_*.py' -v
python experiments/cartridge-ring-013/freeze.py \
  --out /tmp/ring013-frozen.json

# Loads the separate authored challenge ONLY AFTER source-policy freeze.
python experiments/cartridge-ring-013/trial.py \
  --frozen /tmp/ring013-frozen.json \
  --out /tmp/ring013-trial.json

python experiments/cartridge-ring-013/evidence_graph.py \
  --frozen /tmp/ring013-frozen.json \
  --trial /tmp/ring013-trial.json \
  --out /tmp/ring013-evidence-graph.json
```

A GitHub Actions workflow executes all test contracts, 24 value-model selections, the real RING-012 ambiguity source, 60 heldout simulator scenarios and the auditable evidence-graph build. Artifacts contain the chosen value policy, per-case simulated trajectories, and source-bound many-tail/many-head results.

## What to try in RING-014

The most valuable next test is **real bounded tool-assisted safe investigation**: run a source-controlled test suite, local-only geometry thought experiment, disposable build, or reversible isolated fixture; observe *actual measured test results*, not authored useful-work payoffs; then decide whether another internal test is worthwhile. That would connect the value-of-further-action planner to genuinely executable research cartridges.

A trusted task must explicitly define its permitted tool scope, rollback boundary, output receipts, CPU/time budget and approval threshold. It should never treat enthusiasm, interestingness, a graph-inferred directive, or a toy reward as permission to alter someone else's systems. The rules for potential effectful deployments should remain separately permissioned.

**The experiment's key architectural achievement:** an unresolved question no longer automatically causes a human-interruption or total STOP. A non-authoritative agent can calculate the modeled value of further investigation and **execute an approved internal experiment** while preserving ambiguity as the default state.

**The experiment's key limitation:** The entire source viability and reward world is fictional and developer-authored; +76.86 means the code works on that toy setup, not that MOTIF has validated real-world autonomous opportunity recognition.
