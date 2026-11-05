# MOTIF-019 — What if the question we are asking is priced incorrectly?

**Executed against public USGS source data on November 5, 2026.** The research protocol, six revision lenses, candidate decision grammar, training 2023, development September 2025, and untouched March 2026 test window were fixed before the holdout fetch.

**[First source-backed live run and complete temporary raw-source archive](https://github.com/the-static-collective/MOTIF/actions/runs/42040325426)**. **[Revised cost-self-critique run, successful](https://github.com/the-static-collective/MOTIF/actions/runs/42040857789)**, including eleven-plus offline adversarial tests and separate live source steps. The latest run artifact includes all raw USGS JSON responses, the exact frozen model coefficients and question-policy cartridge, and its scored result; artifacts have **30-day retention**. The canonical, concise source-derived receipts are in `experiments/019/evidence/final-question-evolution-2026-11-05.json` and `final-value-function-diagnostic-2026-11-05.json`.

## What the six-step question machine actually did

MOTIF's bounded declarative decision instrument considered whether information is worth seeking, source-query price, missing answers, event drift, historical station-health probes, and false claims of health. It used **May 2023** USGS records to train three small classical models; **September 2025** USGS data (already inspected by experiment 018) to revise question-choice policy. It then froze the selection and source boundaries **before reading March 2026 data**.

| Lens | Selected research question |
| --- | --- |
| Q0 — measurements are free | **both_graceful** (query both rivers, fall back to available readings) |
| Q1 — one question has a cost | **downstream** (do not request another source) |
| Q2 — failed answers cost extra | downstream |
| Q3 — conditionally query when local river changes | downstream |
| Q4 — ask a cheap question about recent station health | downstream |
| Q5 — false-positive health probes can themselves waste work | downstream |

The question grammar expanded to include three novel, *operational* ways of asking whether a source is healthy. The chosen policy **changed once (Q0→Q1)**, then remained unchanged. Calling that six independently successful improvements would be false. Code never autonomously rewrote itself; only a bounded JSON policy decision criterion evolved.

The final **frozen selection was downstream persistence**. The machine's source-only-influence SHA-256 was `d6c24709882faee4e66a2b32ad0502422f5ac8d526025da114571a8a6a705cac`. Freeze integrity is a content hash, not an agency-authenticated contemporaneous record.

## The physical March 2026 test

There were **300 downstream target cases** where Mankato's historical readings at origin and target were present. Source readings needed to calculate auxiliary river features were present in only:

- Blue Earth: **35/300** cases
- Le Sueur: **116/300** cases
- Both: **35/300** cases

Missing optional river features do **not** remove a Mankato target or turn missingness into a fabricated zero observation.

| Frozen policy / independently predeclared alternative | March 2026 raw MAE, cfs | March 2026 declared weighted objective, cfs equivalent |
| --- | ---: | ---: |
| **Frozen policy — no new query (downstream)** | **185.3333** | **213.7933** |
| Le Sueur alone, graceful fallback | 155.8044 | 255.6909 |
| Health_last3 proxy + graceful fallback | **150.4962** | 261.5924 |
| Ask both every time, graceful fallback | 150.4962 | 351.6839 |

**The selected frozen strategy produced no raw improvement versus its own downstream baseline**, so the system returned `HOLD_NO_INDEPENDENT_QUESTION_VALUE`. Other predeclared alternatives reduced raw MAE by up to **34.8371 cfs** (18.8% versus persistence) on the same March observations, but their hypothetical query prices made them *worse on the stipulated utility objective*. The source-health strategies are post-test comparisons **not allowed to replace the frozen policy**.

## The surprise: the 'cost' wasn't measured

The system initially asked whether it was worthwhile to check whether a gauge could answer.

But the assumed per-source question price was fixed at **8% of 2023 training persistence MAE**, which became **37.382353 cfs-equivalent research credits** in the latest run. That number is **not** actual money, latency, operator effort, or the verified cost of being wrong.

An added meta-diagnostic computed, *after opening the 2026 test*, the **hypothetical break-even source-credit price** at which each strategy would have outscored the downstream baseline under the already-frozen weights.

| Alternative | Posthoc break-even cost per source-credit, cfs equivalents |
| --- | ---: |
| Ask both unconditionally | 9.7674 |
| Ask Le Sueur only | 18.5661 |
| Health_last3 or health_last6 | **18.8795** |
| Health_last1 | 14.0824 |
| Trend-gated inquiry | 10.3910 |

Our stipulated **37.382353** price was higher than every computed alternative's break-even threshold. That entirely explains why the cost-aware policy chose not to inquire, **within this particular made-up cost model and scored sample**. These thresholds are **posthoc diagnostic numbers, not revised admissible strategy thresholds**.

The machine therefore generated a more fundamental question:

> **Are our research credit prices the wrong question? What actual latency, missing-answer and opportunity costs justify asking?**

That is a new epistemic boundary: what should the learning system optimize, who is authorized to define that value, and what observable event would falsify its utility model?

## Proposed next physically meaningful test

**Don't optimize another imaginary score.** Collect *actual issue-time measurements* for query latency, actual station response availability, rate limit, and resulting opportunity cost. Ideally use a scheduled, read-only public-source monitoring instrument that (a) logs the timestamp and result of each permitted source request, (b) keeps unsuccessful and delayed responses in the denominator, (c) predeclares physical-world performance and latency metrics, (d) freezes strategy before it accumulates the next target outcomes. The user/operator chooses the real-world value function; the learner may propose and falsify **estimates**, not claim authority over human value.

For now this remains retrospective source-backed research with public environmental data. No forecast was actually issued in March 2026; historical report timestamps do not authenticate when values became available, and USGS discharge ratings may be revised. The loop isn't a generally capable self-rewriting agent. A better posthoc score is not proof of an improved independently tested policy. No flood alerts, autonomous source-code changes, or physical actions.
