# VOID-006 — Post-score evidence report: Reflex Forge

**DRAFT RESEARCH HOLD.** This note was written after the 20-seed heldout evaluation. It does not alter the frozen experiment's preregistration or the scored policy. Source is a programmer-authored 24-wave adaptive fortress, NOT a new independent game benchmark or simulated biological motor cortex.

## Reproducibility and anomaly

- Frozen before method implementation: `PREREGISTRATION.md` commit `55afb93c38a9adc4cb142b8fd4444c1d02ff71e0`; the workflow independently compared the current file with historical Git bytes before running tests.
- Initial run `43114123860`: all **9** unit tests, development simulator and all 240 test cases **executed successfully**, but a final audit assertion failed because the development command had intentionally omitted detailed receipts (`--full`) while the shared audit expected them. This is a **harness-only audit failure**, not a scored-policy failure. Its output was preserved.
- Single correction: commit `30dbc918243869dea8e410431bfd85e2c12a92e3` added `--full` to the development logging command only. **No policy rules, heldout seeds, metric, owner mechanics or inference methods were changed.**
- **Green complete workflow**: https://github.com/the-static-collective/MOTIF/actions/runs/43114412109 ; all 9 tests, all source/receipt validations, all 48 development and 240 heldout episodes, full artifact archival passed.
- **Complete action receipts**: https://github.com/the-static-collective/MOTIF/actions/runs/43114412109/artifacts/13898190798 ; archive SHA256 `09bcddc47ea8d2dc4b544118effd0a950530d8518a37bb203ee18530eaf2ed19`.

## Frozen first-success attempt results (20 new seeds each)

Primary endpoint: first verified complete defense of all 24 waves; failures at 14 attempts count as 15. Smaller is better.

| Regime | Controller | Wins by 14 / 20 | Mean restricted attempts | Mean deliberate gate lookups | Mean cached gate defenses |
| --- | --- | ---: | ---: | ---: | ---: |
| Stable | Muscle compiled | 20 | 9.15 | 54.30 | 80.35 |
| Stable | Matched classical sparse | 20 | 9.15 | 134.65 | 0 |
| Stable | VOID-005 classical VOI | 20 | 9.15 | 134.65 | 0 |
| Stable | VOID-005 stale ablation | 20 | 9.15 | 132.95 | 0 |
| Reactive | Muscle compiled | 20 | 11.00 | 57.90 | 93.70 |
| Reactive | Matched classical sparse | 20 | 11.00 | 151.60 | 0 |
| Reactive | VOID-005 classical VOI | 20 | 11.70 | 162.95 | 0 |
| Reactive | VOID-005 stale ablation | 20 | 10.95 | 149.05 | 0 |
| Reactive + deceptive relay | Muscle compiled | **20** | **12.55** | 59.35 | 102.00 |
| Reactive + deceptive relay | Matched classical sparse | **20** | **12.55** | 161.35 | 0 |
| Reactive + deceptive relay | VOID-005 classical VOI | **16** | **13.15** | 163.90 | 0 |
| Reactive + deceptive relay | VOID-005 stale ablation | **18** | **12.75** | 158.10 | 0 |

### Attribution — distinguish two effects

1. **Procedural cache benefit:** `muscle_compiled` and **same-information same-reliability** `classical_sparse` tied **exactly in all 60 paired seed×regime outcomes**. The cache replaced roughly **60% (stable), 62% (reactive) and 63% (reactive+deceptive)** of per-wave declarative gate lookups with cached action selections. Its chunk executor still dispatched and checked *every* primitive defense. This reduction is in a deliberately instrumented policy-operation count, **not measured inference wall-time, energy or human consciousness**. Thus no new survival strategy advantage has been shown.
2. **Sparse selective trust benefit:** both new sparse controllers were better *descriptively* than the old coarse-global-confidence `classical_voi` in reactive regimes: **11.00 vs 11.70** attempts (reactive) and **12.55 vs 13.15** attempts (deceptive). In the deceptive regime they cleared **20/20 vs 16/20** under the 14-attempt ceiling. This is due to a **hand-coded local trust and source-precedence model** shared by both new arms, **not special muscle-memory intelligence**, not an exact Bayesian posterior, and not proof of robust generalization. The new source seeds are author-selected and the fortress's change mechanism was already examined in VOID-005.

### Behavioral evidence

- Muscle controller automatically executed an average **80.35** (stable), **93.70** (reactive), and **102.00** (deceptive) confirmed habitual defense steps per episode. Most of these steps belonged to **three-or-more-wave contiguous chunks**: mean **79.75, 92.60, and 99.85** respectively.
- In the 20-case reactive group, verified contradictions triggered **25 immediate cached-habit invalidations** during defense; in the deceptive group **21**. No hidden effect or fake relay may become a reflex merely by being signed.
- All 240 cases passed the final full source/defense receipt audit. The full archive includes source_epoch, sonar/relay reports, per-wave successes, failures, cached action flags, and actual winner verification.
- This is an **engineered zero-LLM Python procedure**, not trained reinforcement learning, motor learning, a natural-language question-answering agent or actual subconscious thought. Source hash is local integrity, not authentication of external actors.

## Next falsifier

Use a real action-cost model (CPU time / model calls / token usage) and **independently authored changing environments**; allow a cached controller to return control to active hypothesis revision when a context cue or negative prediction error is detected. Compare against established hierarchical RL options / policy caching with equal resources. Introduce **context-dependent gate schedules** so a memorized wave number alone cannot solve the task, and test whether contextualized habits relearn or catastrophically repeat.
