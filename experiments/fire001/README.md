# FIRE-001 — Cognitive combustion, a bounded inquiry governor

**Status:** synthetic research prototype; no autonomous real-world action or demonstrated recursive self-improvement.

The user's analogy is tested as a falsifiable scheduler: **fuel** is the value of unfinished questions and contingent follow-ups; **oxygen** is independently sourced evidence still available; **heat** is finite analysis capacity. The governor considers all three and can extinguish or park a thread when sources/budget are insufficient. **Ignition** is a scheduled source observation; **embers** are source-starved tasks; **sparks** are predeclared follow-up questions unlocked *only* after a separate synthetic verifier confirms a claim. New questions are *not* spontaneously invented.

## Experiment and boundary

- Eight generated binary questions per world, four initial roots and four contingent questions. Every question has a public value, known evidence quorum, source count and finite reasoning work. Outcomes and noisy source reports are private to the synthetic owner. Source receipts have distinct origins, but this toy cannot authenticate independence in the real world.
- Every observation, unit of reasoning and verification consumes one of 24 identical budget units. A majority of an odd number of reports supplies the proposed answer; the separate toy oracle compares it with hidden truth. Incorrect proposals cannot unlock children or score.
- The `PublicView` passed to every selector excludes the owner's truth and report schedule. MOTIF-003's **actual `affordance_keys`** is imported to count hypothetical new question affordances; it never confers authority or evidence.
- Identical worlds/budgets compare priority-by-value, naive uncertainty-based information priority, value-per-cost classical greedy, FIRE, and FIRE with no downstream spark bonus.
- Bounded self-tuning searches five *engineer-specified* spark weights on the 40 training seeds `4100..4139`, selects 1.0 and freezes it for 200 subsequently chosen test seeds `32000..32199`. This is policy parameter selection, **not free-form invention, online adaptation, or independent blind testing**. An earlier development set `9100..9299` informed the governor's design; those seeds are not presented as an untouched holdout.

## Reproduce from repository root

```sh
python -m unittest discover -s experiments/fire001 -p 'test_*.py' -v
python experiments/fire001/benchmark.py
```

Python 3.10+ standard library only. The benchmark prints deterministic JSON; `results.json` is the locally observed output. Checks cover no truth in policy view, fire extinction, duplicate-source refusal, independent verification gate, evidence/heat stages, budgets, and repeatability.

## Observed 200-world test (mean verified value per 24 budget units)

| Policy | Mean verified value | Correct tasks | Unlocked questions |
|---|---:|---:|---:|
| Value priority | **14.985** | 3.275 | 6.260 |
| Value/cost greedy | 14.915 | 3.290 | 6.260 |
| FIRE without sparks | 14.795 | 3.280 | 6.255 |
| **FIRE tuned** | **14.730** | **3.375** | **6.635** |
| Naive information priority | 14.185 | 3.180 | 6.240 |

FIRE produces more correctly completed tasks and unlocks more future questions in this toy, **but does not win the primary predeclared verified-value metric**. Its verified-value difference versus classical value/cost greedy is **−0.185** (approximate paired 95% interval **[−0.4755, +0.1055]**). Against FIRE without sparks it is **−0.065** ([−0.3682, +0.2382]). Neither supports a demonstrated value advantage. Ordinary value priority leads on measured value in this sample.

## Cautions and next falsifier

Fuel/oxygen/heat are **operational analogies**, not biophysical laws of thought. Source availability and compute costs are given by a simplified synthetic task designer, verification is provided by a toy oracle, and the follow-up dependency graph is preauthored. Goodhart risk: producing more questions is not necessarily producing more knowledge. There is no independent field observation, unauthorized actuation, novel math, or verified compounding self-improvement.

**Next hard test:** preserve this frozen implementation and compare against matched-budget exact dynamic programming (small worlds) and a learned scheduling baseline. Add source correlation, misleading source identifiers, changing evidence quality, unannounced resource changes, and a true external out-of-distribution task source. Prefer actual verified value and calibration over question count. Keep real-world permission checks outside the metaphor.
