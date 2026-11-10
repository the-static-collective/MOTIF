# MOTIF-GENIUS-007 — The Question Foundry: measured first result

**Research HOLD.** The first full frozen evaluation passed **14 adversarial tests** on GitHub Actions run **42859087149**, along with full task/hidden-world scoring and artifact upload.

Original training-only selector and future-task contract SHA-256:

**e1a18062775d9db5840913e0a4a2c5a96ed831c2c5ce0e4a04c0a189ee0efb3b**

Two validation tasks per family were evaluated first. The selected method and contract were frozen before the remaining three synthetic task seeds were used. Across seven future families, three new public task contracts per family and all 32 secret possible worlds per task, the experiment evaluated **672 finite world cases per policy**, 4,032 policy-case episodes across six strategies. All certified rewards were checked against the direct simulator truth oracle. No real-world actions.

## Results — mean certified synthetic capability reward (higher better)

| Family | DIRECT_ENTROPY | DIRECT_OPTIMAL | FOUNDRY_ENTROPY | FOUNDRY_GREEDY | FOUNDRY_LOOKAHEAD2 | FOUNDRY_OPTIMAL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PAIRABLE | 0.000 | 0.000 | 0.000 | **2.667** | **2.667** | **2.667** |
| TRIPLE | 0.000 | 0.000 | 0.000 | 0.000 | **1.292** | **1.292** |
| MIXED_POLARITY | 0.000 | 0.000 | 0.000 | **3.000** | **3.000** | **3.000** |
| MULTIGOAL | 0.000 | 3.625 | 0.000 | **4.833** | **4.833** | **4.833** |
| NO_PAIR | 0.000 | **2.417** | 0.000 | 0.000 | **2.417** | **2.417** |
| EXPENSIVE_PAIR | 0.000 | **2.333** | 0.000 | 0.000 | **2.333** | **2.333** |
| DISTRACTOR | 0.000 | 0.000 | 0.000 | **2.083** | **2.083** | **2.083** |

The table is **not** an experiment showing MOTIF beating optimal classical planning. FOUNDRY_OPTIMAL is a conventional exact Bellman planner with the SAME generated sensor action space as the foundry strategies; it was matched by one or more generated heuristic policies in all seven hand-designed toy families.

### Specific observations

1. **An intermediate question was constructed, not chosen from an input menu.** A fresh task such as cobalt_mill=0 AND windrow=1 yields a new pair-match query expression with its originating goal, instrument provenance, cost and separate truth-check receipt. The code does not recognize these English names; it composes from variable-and-value relationships.
2. **A paired measurement helps only because the operator is allowed.** Direct costs 2 per sensor; a two-sensor conjunction measurement, when explicitly supported, costs 3 and reveals only a Boolean. With 3 cost units, a two-fact capability can be certified by one generated pair question but *not* by two direct tests, which would cost 4. The apparent reward gain is due to additional declared measurement access — NOT superior inference over the same action space.
3. **TRIPLE requires looking beyond immediate reward.** A 3-cost pair measurement plus a 2-cost direct measurement can certify the three-fact goal. Immediate greedy gets 0 because its first step certifies nothing; two-question lookahead and exact DP obtain 1.292 average reward.
4. **The controls matter.** When pair measurement is unavailable (NO_PAIR) or overpriced (EXPENSIVE_PAIR, cost 5 > budget 4), composition cannot create a miraculous discount. FOUNDRY_OPTIMAL exactly matches DIRECT_OPTIMAL. No unsupported query is executed.
5. **Information gain alone is not a measure of specific goal value.** All entropy-only results were zero here because of short budgets, distractor channels and high entropy per cost of direct probes. This is highly construction-dependent. The earlier GENIUS-006 NOISE_USEFUL environment deliberately shows cases where entropy *is* useful.
6. **Exact classical optimality was never exceeded.** A full-world verifier checked all possible targets for each test task and the Bellman expectation matched exhaustive outcomes. This is a finite test of the implementation, not a theorem about unbounded worlds or AI self-improvement.

## What did not happen

- No invention of an entirely new physical measurement operator, causal variable, logic, or language-understanding model.
- No independently authored scientific question, blind external benchmark, or real laboratory result.
- No evidence that randomly changing variable names produces deep domain transfer.
- No special performance advantage over the classical exact planner given identical supported actions.
- No code merged into main, no live Trench/MCP integration, no real-world effects.

## Next research gap

The next question is whether an unfamiliar external problem can supply **truth-grounded, independently authenticated instrument semantics**, while MOTIF composes a novel question representation a separate real evaluator can execute. A valid successful result would carry (a) goal-to-question derivation, (b) instrument authorization and measured cost, (c) actual observation and provenance, (d) downstream claim with third-party verification, and (e) baseline comparison with *the same instrumentation and compute budgets*.

This remains an **executable compositional question generator under a known grammar**, not autonomous discovery of fundamentally new experimental methods.
