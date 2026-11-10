# FIELD-004 — The Relational Gap Challenge

**Question:** Can MOTIF's fact → possibility → relationship grammar carry useful information into predictive models and outperform the **original FIELD-003 depth-three CART**, *and* a genuinely competitive **same-label classical portfolio**? What happens in untouched-by-model-development split seeds?

**Research status: unmerged, exploratory, HOLD.** This is a challenge to our previous comparator, **not** evidence of a new AI algorithm or scientific law.

## From FIELD-003, unchanged

- The owning source and pinned historical physical measurements remain **UCI Iris and Wine** (exact CSV bytes inherited from FIELD-003; UCI DOI 10.24432/C56C76 and DOI 10.24432/C5PC7J).
- Class definition and binary target, record hashes, 60% pool / 20% tune / 20% test split, and original label budgets **60 Iris / 75 Wine** remain unchanged.
- We **replay the existing FIELD-003 active or random query policy**, preserving actual source receipts and query sequence. The code stops BEFORE FIELD-003 evaluates test labels, instead of reusing its published test scores to select a new model.
- Every candidate uses the **same acquired labels**; no model is trained on tune/test labels. The common unlabeled training pool is used to compute feature scaling for all methods.

## New contest, three clearly separated comparisons

1. **Original reference:** FIELD-003's source tree of depth 3, training on the same acquired labels and original scaled raw features (same code, not a port or substitute).
2. **Competitive classical:** eight candidates on raw measured features, including CART depth 3/5, random forest, ExtraTrees, linear and RBF SVM, logistic regression and kNN. Select one by deterministic **four-fold stratified *training-label-only* CV** using balanced accuracy, then fit it on all acquired labels.
3. **MOTIF relational challenge:** seven candidates that compose pairwise **signed sums, differences, and products** of **at most six** training-relevant fields, then fit trees/forests/SVMs. Field selection is *inside the CV pipeline* and relearned in each training fold (no fold-level leakage). Same fold splits and same label budget. Additionally, fit the winning relational estimator **without** added relational features, holding model family and hyperparameters fixed—an ablation isolating what feature composition buys.

These operators are **standard classical feature engineering**. The study measures the benefit of making relational features inspectable and automatically selectable; a favorable score would **not** prove an advantage over all classical ML, novelty of mathematical operators, recursive self-improvement, or causal discovery. The relative sizes of the candidate portfolios are different, so a win is not a universal complexity-controlled victory.

All choices, CV scores, chosen axes, dataset revisions, training row ID sequence digests, individual source receipt digests and final frozen packet digest are preserved **before scoring**. The final tuning split is reported but not used for selecting anything. The test split is scored once for each pinned case. A source hash is not a certificate of the primary source identity.

## Exploratory vs audit

We reused familiar public benchmark data; **this is not a prospectively preregistered or blind evaluation**. The original FIELD-003 splits 11/23/37 and additional development splits 53/67/79 informed the pursuit of more competitive model families. Seed **83** was inspected during development; it is classified as exploratory, not audited.

The **frozen-audit cohort** uses fixed different split seeds **97/101/107**, after the approach was fixed. Nothing was tuned from their test scores. All seeds repeatedly resample the *same* finite historical dataset; aggregated correct counts are **correlated observations**, not independent people/specimens or a significance test. Multiple choices of architectures occurred during exploratory work; these numbers should not be interpreted as an unbiased prospective effect estimate.

## Actual results: correct historical labels / repeated evaluation total

| Cohort | Source / acquisition | Original depth-3 CART | Best CV raw classical | CV relational | Winning estimator *without* relation features |
|---|---|---:|---:|---:|---:|
| Exploratory 7 splits | Iris / active | 198/210 | 199/210 | **202/210** | 200/210 |
| Exploratory 7 splits | Iris / random | 196/210 | 202/210 | **203/210** | 201/210 |
| Exploratory 7 splits | Wine / active | 251/259 | **254/259** | **254/259** | 252/259 |
| Exploratory 7 splits | Wine / random | 242/259 | 256/259 | **257/259** | 251/259 |
| **Frozen audit 3 splits** | **Iris / active** | **86/90** | 85/90 | **86/90** | **86/90** |
| **Frozen audit 3 splits** | **Iris / random** | **86/90** | **86/90** | **86/90** | **86/90** |
| **Frozen audit 3 splits** | **Wine / active** | 107/111 | **109/111** | 108/111 | **109/111** |
| **Frozen audit 3 splits** | **Wine / random** | 104/111 | **110/111** | **110/111** | 106/111 |

**Finding:** The extended relational system beats the earlier depth-3 CART in multiple settings, especially under Wine random acquisition (257 vs 242 exploratory; 110 vs 104 audit). Some of that gain is attributable to **choosing stronger classical estimators**, not the relational features. It only *slightly* outperforms the matched raw classical portfolio on exploratory sets, and **does not win against that stronger portfolio on the frozen-audit cohort** (Iris active +1, Wine active -1, remaining two tie). Both methods still use classical ML machinery.

On the audit, the selected-estimator-without-relations ablation **ties** relational results for Iris and performs better on Wine active (109 vs 108); relationships help substantially in Wine random (110 vs 106). Thus **a general relational advantage is not established**. No effect size confidence claims are warranted for the overlapping resplits. A stronger separate-source study is needed.

## Reproduction

Python 3.11; local versions: NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0. All inherited FIELD-003 CSV files must remain source-hash pinned.

```sh
python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0
cd experiments/field004
python -m unittest -v test_field004.py
python verify.py # validate saved summary conservation and source scopes
python verify.py --dataset iris --mode active --out iris-active-proof.json
# Repeat verify.py for iris/random, wine/active, wine/random.
```

The four-shard CI workflow reproduces **every case** individually, compares every stored digest, chosen program, exact CV score, audit cohort and test score, and saves detailed proof artifacts. The checked-in `experiment-results.json` is a compact exact ledger; `field004.py --case <dataset> <seed> <mode>` reproduces full source receipts, provenance and scores for any single case. `python field004.py` attempts a full local recomputation, but the sharded route is preferred on resource-limited machines.

## Next falsifier

To **beat a genuinely strong classical learner in a credible way**, freeze the whole operator-discovery and query policy; test **new, separately authored datasets** with controlled compute, labels and training splits; include tuned raw RBF-SVM, XGBoost and calibrated forest/rule/oblique baselines; study true active-question cost and honest HOLD under shifts. Report all families, wins and losses. No automatic merge, deployment, cross-project integrations or real-world actions.
