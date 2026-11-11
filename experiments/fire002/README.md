# FIRE-002 — Productive Combustion

**Status:** executable synthetic research experiment. This stacked branch derives from FIRE-001 draft PR #275; neither branch is production, an autonomous agent, or permission to operate outside the simulator.

## What changed

FIRE-001 rewarded potentially reachable investigations. FIRE-002 instead ranks each allowed research task by **forecast certified value / remaining observation-plus-reasoning cost**. The policy uses a prior for source reliability and estimate of downstream certified yield; the online variant adjusts both *only after* a synthetic oracle explicitly verifies or rejects a claim. It does not read future reports, concealed truth, or hidden experiment regime. Completing an imagined path never counts as knowledge.

The user-proposed fire triangle remains an analogy: unanswered uncertainty is *fuel*, available independent observation is *oxygen*, bounded research effort is *heat*. Child questions are sparks, not automatically useful discoveries. Without enough independent reports or budget, inquiries remain on hold.

## Reproduction

```sh
python -m unittest discover -s experiments/fire001 -p 'test_*.py' -v
python -m unittest discover -s experiments/fire002 -p 'test_*.py' -v
python experiments/fire002/benchmark.py
```

No paid APIs. Actual GitHub Actions FIRE-002 run #43009923980 passed unit tests and reproduced `results.json`. This is a synthetically generated test whose preregistration is in `PREREGISTRATION.md`, rather than external blind evaluation.

## Observed result

The training-only search chose a spark coefficient of **1.0**. On 200 separately seeded test worlds per regime and a fixed maximum of 24 actions per world, the primary metric was **mean independently certified value**, not number of unlocked questions:

| Held-out synthetic regime | Classical value/cost | FIRE-001 | FIRE-002 frozen forecast | FIRE-002 online updates |
| --- | ---: | ---: | ---: | ---: |
| Steady independent reports | 15.175 | 14.880 | **15.245** | 15.235 |
| Root/child quality drift | 13.790 | 13.525 | **13.800** | **13.800** |
| False independence / shared source | 12.900 | 12.650 | **13.200** | 13.085 |

The online governor exceeds FIRE-001 by **+0.355**, **+0.275**, **+0.435** respectively on these three regimes (descriptive paired intervals exclude zero). **But it does not establish an improvement over the strong classical value/cost comparator**, where the corresponding paired effects were +0.060, +0.010, and +0.185, each with intervals spanning zero.

Most important: **online self-adjustment does not outperform freezing the same policy**. Its paired online-minus-frozen verified-value differences were **−0.010**, **0.000**, and **−0.115**. The correlated-regime approximate paired 95% interval for this difference was [−0.22367, −0.00633]. In this toy, the online estimator is **worse** when nominally distinct source reports actually reflect one concealed shared origin. This is evidence against claiming that adaptive learning has been demonstrated by this implementation.

## Hard boundaries

- Every source, hidden truth, value, task dependency, action cost, and verifier is an **engineer-authored synthetic fixture**. The policies do not observe actual human, physical, or scholarly evidence.
- Verification is an idealized binary synthetic owner; it does not prove a future real-world witness is trustworthy.
- Synthetic origin labels appear unique even under the correlated fixture; an unmodeled common upstream source makes apparent agreement misleading.
- The parameter sweep is finite and engineered. The online update is a bounded two-counter learning procedure, not architecture invention, general intelligence, or recursive self-improvement.
- The attempt is staged under a **draft PR / research HOLD**; it must not be merged into a real-world action agent on these results.

## Next falsifier

Model provenance lineage and effective sample size so six copies of a shared source are not six independent observations. Retrain against **strong Bayesian sequential decision and exact dynamic-programming schedulers under matched compute**, introduce changing and deceptive reliability with no regime labels, and pre-register tests on a third-party corpus. Demand measurable *incremental benefit from online updates* over the frozen controller rather than reward propagation or complexity alone.
