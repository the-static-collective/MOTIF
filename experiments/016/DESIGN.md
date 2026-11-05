# MOTIF-016 — THE LIVING FOREST
## Answer, question, verify, branch, converge, and stop — without confusing imagination for evidence

**Research question:** Can a bounded reasoning controller choose an immediately useful portfolio of multiple inquiry avenues *and* value actions whose main benefit is unlocking later, complementary avenues? Can it preserve a tentative answer while branching, prune falsified hypotheses after independent results, and stop before pointless extra inquiry?

**Status:** Runnable Python 3.10+ standard-library experiment, based on MOTIF-015. Entirely synthetic: no language model, real-world information gathering, human communications, causal identification, signed evidence, verified permission, tool/API access, or autonomous self-modification.

### The crucial distinction from MOTIF-015

MOTIF-015 selects an excellent **single simultaneous batch** by the joint utility of its question outcomes. But it cannot evaluate an initially uninformative question that makes a different, cheaper batch possible **later**. A shallow optimizer can prefer a locally attractive question and waste its limited budget.

MOTIF-016 adds finite **two-stage contingent planning**:

    WORLD HYPOTHESES (provisional, initially weighted)
        |
        +--> AVAILABLE ROADS: ANSWER / ASK / VERIFY
                 |
        EVALUATE ALL AFFORDABLE PORTFOLIOS
                 |
          HYPOTHETICAL RESULT BRANCHES
              /              \
           result 0         result 1
              |                |
      OPEN NEW ROADS     OPEN DIFFERENT ROADS
              |                |
       PLAN NEXT BATCH     PLAN NEXT BATCH
              \                /
           COMPARE EXPECTED DECISION VALUE
                  |
          CHOOSE FIRST PORTFOLIO
                  |
           SYNTHETIC CALLBACKS
                  |
          RECEIVE ACTUAL REPORTS
                  |
       PRUNE IMPOSSIBLE HYPOTHESES
                  |
     REPLAN / TENTATIVELY ANSWER / HOLD / STOP

Every branch in the initial preview is labeled hypothetical. Only independent callback results mutate the observed record. The method does *not* inspect the simulator's secret answer when planning.

### Interfaces

- Road: named ANSWER, ASK, or VERIFY proposal, nonnegative cost, an origin declaration, a predicted outcome **for each candidate hypothetical world**, an allow/hold flag, human-attention flag, and zero or more prerequisites of the form (prior_road, reported_value).
- LivingForest.plan: exact finite-horizon expectimax over **joint batches of at most three roads**, no more than 12 declared roads/64 worlds/three rounds. It calculates how a portfolio changes posterior answer accuracy **after** hypothetical responses and after downstream roads become available. It outputs counterfactual Forecast branches with conditional likelihood and projected next batch. Search uses a canonical transposition table for order-equivalent evidence sets.
- run_synthetic_round: reuses **MOTIF-015's actual concurrent** threadpool callback dispatcher, and supplies separately returned observations. No actuation or real question is sent.
- accept: commits only a complete response to the current selected plan (stale/partial/unauthorized results rejected). It records (road, declared_origin, reported_result), newly available doors, hypothesis pruning, cost and remaining uncertainty. A report inconsistent with every model produces HOLD_MODEL_FALSIFIED, retains the prior state and stores a counterexample; the cost of the attempted query remains charged.
- ANSWER_AND_EXPLORE: once a prior makes a tentative answer sufficiently likely, the controller may answer provisionally and **still ask** a potentially valuable question. A stronger configurable threshold stops all further requests when the answer is already decisive.
- Source-redundant exact claims are offered only once. **Declared origin is not authenticated witness identity;** correlated distinct sources require a separate probabilistic evidence organ such as MOTIF-014W.

The utility optimized here is the *expected fraction of correct decisions* minus a linear inquiry-cost penalty. This is classical finite-state metareasoning, **not a novel planning theorem, full Bayesian causal model or automatically aligned utility function**. The future "affordance" term is currently implicit: the planner values a present question for the downstream *decision value* of unlocked questions, not for raw count of available actions.

### Frozen counterexample

Eight equally likely invented worlds have three unknown binary properties: MODE, LEFT, and RIGHT. The requested decision is YES when LEFT XOR RIGHT, otherwise NO.

- SCOUT costs **0.20** and reveals MODE, completely irrelevant to the current YES/NO decision. Without future planning its expected answer improvement is **zero**.
- FAST_A_0, FAST_B_0, FAST_A_1, FAST_B_1 cost **0.35 each**, and are usable only after SCOUT reveals their matching mode. Both complementary ports can be examined concurrently.
- BAIT costs **0.60** and recognizes just one distinguished no-world. It raises immediate expected accuracy from **0.50 to 0.625**.
- Two expensive direct port questions cost **1.00 each**. A prohibited apparent perfect-answer shortcut is excluded by its allow gate; a duplicate source cannot masquerade as another independent question.
- Every method receives a budget of **1.25**, at most **two inquiry rounds** and **two simultaneous questions**.

Prediction fixed before executing the benchmark: a one-round optimizer will choose BAIT for immediate value. A two-round exact lookahead can choose SCOUT first, then both cheap mode-specific questions in parallel for a combined cost of **0.90**. A simple hand-coded **classical fixed diagnostic** can achieve the *same* thing.

Run python benchmark.py to evaluate all eight hidden worlds, keeping per-world results, cost and branch traces; the benchmark must print its own actual computed values. Run python demo.py for an actual synthetic portfolio, future-branch preview and independently returned observations; python -m unittest -v test_forest.py checks parallel execution, budget/attention/allow gates, branch values, inconsistent reports, tentative answers, stop rules, duplicate suppression, stale plans, ablation and classical baseline.

### Honest limits and next falsifiers

1. **Not general question generation:** the tiny grammar, synthetic prior, test costs, gate conditions, all candidate answers, and every conditional outcome are explicitly supplied. The inference is an exact enumeration over these declarations. Planning success does not establish that MOTIF can invent a useful new question or recognize real affordances.
2. **The strong fixed diagnostic ties:** this world is deliberately designed to make *adaptivity visible*, not to demonstrate any advantage over a prepared optimal classical policy. Also compare to classical expectimax / dynamic programming on identical posterior inputs, which should mathematically match.
3. **A world can be wrong:** unexpected observations cause HOLD, not automatic discovery of the missing cause. Next add a safe candidate-expansion protocol and score how often an invented hypothesis is independently falsified.
4. **No stochastic evidence:** the current model is noiseless and depends on calibrated, trusted model predictions. Integrate MOTIF-014W joint witness/actuator uncertainty and test correlated reports, unreliable intervention receipts, and drift. Use Brier/log loss and coverage-risk curves, not just binary exact identification.
5. **Combinatorial expansion:** exact partition-and-portfolio search is bounded and small. On larger grammars it can explode. Benchmark against adaptive greedy, Monte Carlo tree search, Bayesian experimental design, fixed diagnostics and cost-aware branch-and-bound under identical time/compute budgets.
6. **No external adapter:** all questions are synthetic callbacks. Real JAR;VIS routes require explicit user-scoped approval, human attention ceilings, capability checks, idempotent requests, cancellation, timeouts, provenance and revocation receipts. A plan does not grant permission to execute.
7. **No physical reachability yet:** introduce state-dependent resource/capability graphs from MOTIF-003; distinguish newly **feasible**, **valuable**, and **permitted** actions. Score real expected utility and future opportunities in independent frozen synthetic worlds, not a reward for making pointless branches.
8. **Sequential baselines matter:** this initial controller chooses a parallel batch, waits for **all** results, then replans. It cannot exploit partially completed asynchronous replies, early stopping while siblings are in flight, latency-aware speculation, speculative cancellation or cross-branch work stealing. Those are separate experiments.

**Reproducible scientific claim:** Given this fully specified finite synthetic world and equal constraints, the algorithm is able to choose a first question that has no immediate decision value but creates the possibility of an informative parallel second batch. This is a compositional inquiry primitive—not a verified autonomous scientist.
