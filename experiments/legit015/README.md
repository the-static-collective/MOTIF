# MOTIF-LEGIT-015 — The Compounding Improvement Economy

**Status: research HOLD.** This is an executable finite planning experiment, not a prediction of accelerating intelligence. Nothing here deploys or automatically promotes new code.

## Question

What if the result of an improvement isn't just more useful work, but **more capacity to make the *next* improvement**?

This is the second-order effect behind "compounding interest of improvement": better reasoning tools may make later search cheaper; better verification may open new paths; and productive output can fund additional improvements.

The negative side matters just as much. Every attempt consumes time and scarce capital. Improvements may fail, arrive too late, hit capacity ceilings or cost more to prove than they save.

## Executable mathematics

A finite-horizon state includes:

- **Work throughput**: useful output delivered by working for one period.
- **Capital**: a bounded budget for attempting new improvements.
- **Research throughput**: reduces the budget cost of later improvement experiments.
- **Attempted and successful capabilities**: prevent cost-free repeated attempts and distinguish failures from successful prerequisites.
- **Proposed improvements**: typed cost, success probability, throughput multiplier, research multiplier, and dependency prerequisites.

WORK produces output equal to current work throughput and replenishes the capital budget. An investment consumes an entire period and pays its cost even if it fails. A successful investment may multiply work throughput, research throughput, or both. A later improvement with nominal cost C costs at least one budget unit, specifically the ceiling of C divided by research throughput.

The model uses exact rational Bellman dynamic programming to maximize expected *useful work* across the remaining horizon. It does **not** reward the number of upgrades. A separate independently implemented classical dynamic program computes the same values, and a nonmemoized exhaustive policy-tree oracle independently checks smaller cases. **They tie.** No claim of superior mathematical reasoning is made.

The cost of not investing now is measured as the best expected outcome minus the outcome when WORK is forced as the first action and optimal decisions remain available afterward. This is a model counterfactual, not an observed real-world causal effect.

These are artificial work/capital units, not dollars or measured CPU seconds. WORK is assumed to both deliver useful value and replenish capital; that dual output is an explicit reinvestment assumption, not accounting evidence.

## Results from actually executed GitHub Actions

The committed generated/economy_trial_report.json contains **eight researcher-authored synthetic scenarios**, exact expected values, full hypothetical action sequences, independent classical checks, negative controls and a source-authenticated refusal from the prior actual experiment.

### 1. Faster production finances additional improvements

Initial throughput: **4 units/period**, initial capital **5 units**, and horizon **8 periods**.

The first investment costs 5 and doubles throughput to 8. One WORK period then produces 8 useful units while financing the second improvement. The second improvement costs 8 and doubles throughput again, to 16.

Optimal illustrative sequence: IMPROVE → WORK → IMPROVE → WORK × 5.

- **88** useful-work units under optimal reinvestment.
- **32** units if every period is spent working without any investment.
- **76** units if WORK is forced as the first action and an optimal policy is followed afterward.
- **12** units of modeled opportunity cost from delaying the first improvement.

That difference is meaningful inside this finite economic toy. It does **not** predict MOTIF will actually gain 2.75 times its present capability.

### 2. Non-additive compounding

A second scenario has two independent productivity doublers, each consuming resources and one decision period.

| Available upgrades | Optimal total useful work |
| --- | ---: |
| Neither | 32 |
| Only A | 56 |
| Only B | 56 |
| Both together | **96** |

Interaction: V(A,B) - V(A) - V(B) + V(neither) = **+16**.

Sixteen additional modeled work units appear beyond the sum of the isolated marginal improvements. This is an example of **complementarity** and non-additive compound gains. In other scenarios interaction can be zero or negative; it is not a universal growth law.

### 3. The improvement of the improvement process itself

This is closest to the user's idea.

We begin with throughput **3**, capital **6**, and horizon **7**.

The first investment costs 2 and **does not increase ordinary productivity at all**. Instead, it makes the *research process itself* four times as effective. Two later experiments that originally cost 12 capital units each now cost only 3, making them affordable earlier.

The sequence is: RESEARCH ABOUT RESEARCH → NEW PROGRAM CAPABILITY → WORK → NEW REASONER → WORK × 3.

- **42** units of optimized useful work with the research-efficiency improvement.
- **30** units when that research capability is unavailable but the other improvements remain.
- **21** units from always working without improving.

This is explicit **second-order compounding**: improvement changes the future *cost of improving*, not just the speed of work. The assumed fourfold research improvement is **synthetic**, not an observed gain in MOTIF.

### 4. Reasons the system must refuse

The executable examples also show a one-period horizon favoring WORK; a known-failed upgrade never being selected; a productivity ceiling ending compounding; and decisions changing as hypothetical success probabilities change.

In one scenario, assumed success probability zero leads to WORK. As the *assumed* probability rises to one-quarter, one-half, three-quarters and one, an improvement becomes worthwhile and its expected value rises. The probabilities are illustrative parameters, **not estimates fitted to real development data**.

A prerequisite's failure does not unlock downstream capabilities. An investment cannot be attempted repeatedly without additional costs. All resource, improvement and time horizons are finite.

## The crucial real-world evidence boundary

LEGIT-015 actually reads the **committed LEGIT-014 trial report, generated source and retention manifest**, and verifies their matching source digest.

The observed prior decision was **HOLD_NO_RELIABLE_RUNTIME_IMPROVEMENT**. Its candidate passed formal correctness checks but did not demonstrate a sufficient advantage over earlier versions.

LEGIT-015 does not reinterpret that rejected candidate as a positive measured return. Its hypothetical probabilities and multipliers are **not calibrated from LEGIT-014**. The prior measured profiling and proof costs are preserved as provenance, but are not used as fictional per-investment costs in these scenarios.

## Reproduce and inspect

From repository root, Python 3.11 standard library only:

    python -m unittest discover -s experiments/legit015 -p 'test_*.py' -v
    python experiments/legit015/benchmark.py --emit

The dedicated Actions workflow reruns the independent conventional oracles, adversarial negative cases, exact finite risk and dependency checks, then archives the generated report. The saved report must exactly equal a fresh replay. No third-party formal prover is needed for this particular finite-rational decision model.

Important files:

- economy.py — exact model and Bellman policy generator.
- classical_reference.py — separate conventional exhaustive and memoized stochastic policy oracles.
- evidence_bridge.py — checks the actual earlier empirical HOLD.
- benchmark.py — eight declared synthetic scenarios and comparative model outcomes.
- test_economy.py — adversarial finite-economy tests.
- generated/economy_trial_report.json — actual executed model results and limitations.

## Scientific and operational limitations

This is standard **classical stochastic planning**, not an invention of new mathematics. Its source grammar, scenario probabilities, payoff multipliers and dependencies were constructed by the assistant. They have not been independently calibrated or tested against real improvement outcomes.

The model also deliberately omits financial discounting, intrinsic terminal capital value, ongoing maintenance costs, externalities, human fatigue, reliability degradation, correlated failure and measured CPU/memory overhead. These omissions can reverse a real recommendation.

The results show what conditional compound returns *could* look like, and when a planner should reject them. They do not establish that exponential self-improvement is inevitable, safe, or currently observed. No automatic production modification, GitHub merge or live external action occurs.

**Next critical frontier:** use experimentally observed distributions of past improvement outcomes, real proof and engineering costs, explicit risk intervals, and independently authored unseen tasks. Compare against strong classical resource-allocation policies while accounting for full end-to-end costs. Retain an improvement only when it meets the same rigorous correctness and performance gates as LEGIT-014.

The principle: **improvement is valuable insofar as it increases the future ability to do useful work, including future improvements, after accounting for its cost, uncertainty and opportunity cost.**
