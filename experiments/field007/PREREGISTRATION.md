# FIELD-007 — FROZEN PRE-EVALUATION PROTOCOL
Date: 2026-11-10. **This protocol is committed BEFORE reading or scoring any FIELD-007 hidden test labels.** Preserve this original commit in Git history; deviations must be separately identified rather than silently rebranded prospective.

## Predeclared question
Does the unchanged **principle** of FIELD-006 (query source-held observations that can falsify competing relationship hypotheses, then selectively retract contradicted local predictions) yield repeatable improved **label-efficiency** on separate historical sources, compared against classical uncertainty and committee active learning? No claim of a novel method is preauthorized.

## Data independent of prior Iris/Wine research
Two new-to-MOTIF-FIELD source families bundled with scikit-learn **1.8.0** (pin exact bytes in the implementation):
1. UCI Optical Recognition of Handwritten Digits via sklearn `load_digits`, finite task **3 versus 8**; 64 optical pixel features. Dataset owner is the original authors; our `Owner` only simulates source-held labels.
2. UCI Wisconsin Diagnostic Breast Cancer via sklearn `load_breast_cancer`, binary original labels, 30 measured features; **RESEARCH ONLY; never medical guidance or decisions**.
Using public historical sklearn datasets is *not* an externally blinded or source-owner-operated 2026 assessment.

## Data partition and label budget
Three predeclared hash-ranked, row-ID-only split seeds: **211, 223, 227** (60% query pool / 20% tuning / 20% final heldout). User-facing learner sees all unlabeled pool measurements, never test labels or features during acquisition; historical owner fixture answers legal pool-row queries only. Same 12-label geometry bootstrap for all five strategies; no labels visible until source queries, no holdout-driven policy edits. Exactly **50 labels** each; checkpoint scores **20, 35, 50**. No per-seed tuning or exclusions. Baseline and MOTIF must share identical source partitions.

## Fixed strategies
- `random`: deterministic hash-ranked sampling after the shared bootstrap.
- `geometry`: farthest-first standardized pool coverage.
- `raw_margin`: smallest absolute RBF-SVM margin.
- `raw_committee`: normalized entropy of a fixed raw-feature three-way committee (SVM, logistic, random forest), uncertainty tie break.
- `counterexample_relational`: six-view committee (three raw models plus signed relational SVM, interaction relational SVM, and a relational decision tree), rank opposing predictions first by verified previous prediction error credit, then minority weight, raw-vs-relational conflict, margin and id. Each 12+ query has before-answer predictive packet; all results checked via owner receipt; local predictions matching/refuted do not establish or refute universal laws. Relationship grammar remains the existing **authored** FIELD-004 plus/difference/product constructs, not novel math. Refit committee every three questions.
If the source bootstrap has just one class, continue geometry until two classes; report that deviation and abstain from unfit committees (same for each policy).

## Fixed comparisons, endpoints, decision threshold
On each dataset/seed/checkpoint fit both (A) **raw standardized RBF SVC C=2** and (B) **same SVC C=2 with existing FIELD-004 signed relational features**; plus (C) **raw random forest 100 trees** as a strong additional classical prediction comparator. No test-guided winner selection; report all scores. Primary outcome = heldout balanced accuracy of raw SVC for `counterexample_relational` versus **best** of four individually predeclared classical acquisition strategies, at **50 labels**, for both datasets. Require a strict improvement on **both** datasets and an aggregate average gain >=0.02 balanced-accuracy points to call the cross-domain win. Secondary = 20/35/50 learning curves, relational and forest scores, AULC, actual wall time and fit count. Evaluation repeats overlapping historical specimens: no independent-unit statistical significance. A single checkpoint advantage is not a confirmed win.

## Fail-closed and test rules
No hidden label, hidden test feature, or output from tune/test may affect acquisition. Never accept forged source receipts, self-support cycles, conclusion-as-observation, or query proposals made after reveal. Counterexample support is local to a predicted label at a queried row. Include random/geometry plus strong committee/margin, same query budgets, same final-model family, and negative results. A data source hash does not authenticate historical owner identity. Save exact query list, before-answer digests, archive revision, local refutation/alternative counts, and scoring results. The code must run offline. No deployments, model-assisted external decisions, or automatic merges.

## Scope
This is an independently collected historical **source-domain transfer** test but NOT prospective external or owner-blind validation. Freeze coding policy from this document; any post-scoring changes trigger a *new exploratory* cohort, not retrospective relabeling of the original audit.
