# VOID-005 — post-score evidence report

**Classification: research HOLD. This report was added after the frozen heldout run and does not modify the predeclared protocol or controller.** All source data and policies are from a programmer-authored deterministic wave fortress, not an independently authored real-world environment.

## Reproducibility

- Draft experiment: https://github.com/the-static-collective/MOTIF/pull/292
- **Green, verified GitHub Actions:** https://github.com/the-static-collective/MOTIF/actions/runs/43093606747 (head `23972bbb948b663bd1be665dd6b2994f0b36dd59`).
- **Full source/action receipts:** artifact `13888569935`, https://github.com/the-static-collective/MOTIF/actions/runs/43093606747/artifacts/13888569935 ; artifact SHA-256 `41cd093698c08b174dcf886501e13a13cc7604602dc07eb450825424ddccb589`.
- Frozen cohort and primary metric committed before execution in `fc2090b041d324b6a561077b52f05b5b86abe8d7`; CI checked exact bytes against historical commit.
- All 9 falsifier tests passed. CI executed **144 heldout cases** = 16 fresh seeds × 3 regimes × 3 policies and audited source-owned game receipts for every attempt. Only synthetic action effects, zero paid model calls or external effects. The report's independently checked full heldout evidence seal is `f95dc6940d69a83c4df7e7c8a720c108a6874b7bedce5972068a1e3be453d0c1`.

## Frozen 16-seed results

The score is the **restricted attempt of first actual 24-wave clear**, where failure through attempt 14 scores 15. Lower is better.

| Regime | Policy | Clear by 10 | Clear by 14 | Mean restricted attempts |
|---|---|---:|---:|---:|
| Stable, fixed gates | MOTIF native + VOI gate | 16/16 | 16/16 | 9.2500 |
| Stable | Classical VOI, iteration-aware | 16/16 | 16/16 | 9.2500 |
| Stable | Classical stale (ablation) | 16/16 | 16/16 | 9.3125 |
| Reactive drift: at most 2 counter-moves | MOTIF native + VOI | 0/16 | 16/16 | 11.8125 |
| Reactive drift | Classical VOI | 0/16 | 16/16 | 11.8125 |
| Reactive drift | Classical stale (ablation) | 1/16 | 16/16 | 11.1875 |
| Reactive + sealed false relay reports | MOTIF native + VOI | 0/16 | **15/16** | 13.4375 |
| Reactive + deception | Classical VOI | 0/16 | **15/16** | 13.4375 |
| Reactive + deception | Classical stale (ablation) | 0/16 | **16/16** | 13.1875 |

**Primary result: exact MOTIF vs competent classical VOI tie, across all 48 paired seed×regime cases.** No demonstrated architectural or algorithmic performance advantage. The 14-attempt time budget genuinely prevented 1/16 completion in the most difficult regime.

**Key negative result:** the conservative global epoch-conflict model is too blunt. With only one gate changed at a time, both change-aware policies spend extra sonar checks on historically correct early waves; the deliberately overconfident stale-memory ablation was descriptively faster and cleared the one case they failed. This is *not* a justification for generally trusting stale evidence. The next source-aware controller should distinguish **probability of a local change** from indiscriminate loss of confidence in every fact.

## Instrumented evidence

- 32 owner epoch changes observed in each reactive regime/policy cohort (two per evaluated case).
- In the reactive+deceptive regime, the MOTIF arm received **63 resealed false relay claims** across 16 cases and logged **92 evidence conflicts**. Its source-downgrade/attempt receipts are archived. A receipt seal certified source text integrity, **not** the hidden gate truth.
- For MOTIF and classical VOI, total sonar uses across 16 seeds: stable **86**, reactive **118**, reactive+deceptive **144**. The stale ablation consumed **94**, **94**, **97**, respectively. Different policies can change the timing of the triggered enemy adaptation.
- Most difficult uncompleted MOTIF/classical case: seed **93262** in the deception regime. By attempt 14 it defended **23 of 24** waves; the final unseen wave breached. This counts as **failure**, not a near-win.
- None of the controllers accessed hidden gate truth before permitted owner receipt actions; future information affordances were hypothetical. The program's test source gives it a possibility of an epoch shift but not the changed wave identity.

## Scientific disposition

This is an intentionally engineered deterministic, rule-driven opponent. It is NOT learning weights, inferring defender policies, independently generated survival game mechanics, or a third-party-blinded AI benchmark. The classical comparator is a competent two-horizon value heuristic, **not an exact POMDP or Bayesian changepoint optimum**; we cannot infer MOTIF would outperform strong classical algorithms. Hazards and relay dishonesty were inserted by the same research authors, not established empirical adversarial behavior.

**Next falsifier:** use an explicitly sparse Bayesian changepoint posterior over wave-specific reliability and source dependence, and test source-local targeted verification vs strong classical Bayes/DP with equal actions, new seeded scenarios and externally authored adversarial content. Preserve old failed evidence and never retune against these 16 now-observed heldout seeds.