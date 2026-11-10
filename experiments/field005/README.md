# FIELD-005 — THE RELATIONAL QUESTION DIVIDEND

**Goal.** When a newly constructed relationship raises a disagreement between competing explanations, can querying the specific archived fact that distinguishes them reduce labeling cost relative to strong, conventional active learning? Work builds directly on the open, unmerged FIELD-003/004 experiment stack. **Research HOLD:** this is not deployment, live physical investigation, scientific causation, novel mathematics or a nonclassical algorithm.

## Frozen study design

Historical source-owned snapshots and source revision guards are inherited from FIELD-003: UCI Fisher Iris measurements (DOI 10.24432/C56C76, 150 specimens) and UCI Wine measurements (DOI 10.24432/C5PC7J, 178 chemical records), via scikit-learn CSV snapshots. Those datasets were previously used for FIELD-003 and FIELD-004. They cannot be considered truly unseen external tasks. Source checksums check content identity, not source authentication.

Per dataset and split seed, an original FIELD-003 row-ID-only partition produces a 60% query pool, 20% tuning and 20% heldout testing. The learner receives **all unlabeled query-pool measurements**, which is substantially more information than just one fact; only the first training label and its subsequent queried labels are revealed through the original `Owner.query()` and checked with `Owner.verify()`. Each query is entered into a **before-answer** proposal record containing its supporting model predictions when available, an ordered source-query counter, original source record digest and an immutable frozen model-selection packet. The historical test/tuning labels are excluded from query selection, feature selection, and training CV. There are no real plant/wine measurements performed here.

**Frozen comparison:** five query strategies, equal source-label budgets (Iris 60, Wine 75), same unlabeled training pool, same final model menu, same test samples and per-seed partitions:

1. `random`: deterministic hash-ranked uniform sampling without replacement.
2. `geometry`: farthest-first sampling over standardized unlabeled training features.
3. `raw_margin`: uncertainty sampling using an RBF-SVM fitted to previously acquired labels.
4. `raw_committee`: raw-feature RBF-SVM / random-forest disagreement, then margin.
5. `relation_frontier`: among every available unlabeled measurement, prioritize predictions where the raw RBF-SVM, a signed-sum/difference relational SVM, and a product-interaction relational SVM **disagree**; tie-break by smallest composed-model uncertainty, feature novelty and unlabeled density. Relational features are constructed using FIELD-004's existing `RelationGrammar` on acquired training labels only, not invented math.

All five start with the same geometry-only 12-label bootstrap except `random` which always uses its own sequence; the geometry policy remains geometry-only. Predictions only become queries when an authorized pool row is selected. Updates are refitted every three queried labels; these settings were authored before FIELD-005 audit evaluation.

For each policy, the final classifier is separately selected using **training-only stratified CV** from the **same** fixed raw portfolio (RBF/linear SVM, RF, ExtraTrees, logistic) and the same relational portfolio (signed RBF, interaction RBF, interaction forest). Both are scored, not just the most convenient winning family. An identical model-training and selection routine is applied across all acquisition policies. At budgets 12/25/40/full, model names, CV scores and immutable selected-ID/source-record ancestry are frozen before any test scores are produced; test learning curves are scored *after* each full acquisition trajectory is completed. **Primary comparison:** for each dataset and classifier family, at the full label budget, compare relation-frontier acquisition against the best performing *individually specified* classical acquisition baselines on the same audit seed cohort. **Secondary:** accuracy-versus-label-budget curve (12/25/40/full), and any cost-saving breakthrough must win with fewer observations, not just equal maximum accuracy. Neither finding may be interpreted as statistically independent across repeated splits.

## Development vs audit boundary

Prior FIELD experiments exposed splits 11 and 23. Seed 131 was inspected during FIELD-005 implementation and is thus **development**. Frozen *additional* audit seeds are **137, 139, 149**, selected before their FIELD-005 test scores were inspected. These remain known public datasets and overlapping resamples, not truly external blinded examinations. Do not change the policy after looking at audit outcomes and relabel those outcomes as prospective. A better next test would use new owner-held datasets with a signed, independent evaluation.

## Disproof conditions and privacy/safety

- If a strong classical active policy matches or exceeds `relation_frontier` at the same label budget, **record the tie/loss**. A weak baseline victory is insufficient.
- If `relation_frontier` does not reduce labels needed for a fixed accuracy level, **no active-inquiry dividend** is established.
- Any cached/rehashed forged source label is rejected against the original historical source value. Predictions, query plans and model associations are not observations.
- Repeated split holdouts are correlated and cannot support independent-sample statistical claims; model/candidate menus and heuristics are conventional classical methods. No live network access, inter-project write authority or model deployment.

## Reproduce

Python 3.13, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0; inherited source snapshot files from `experiments/field003`:

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0
cd experiments/field005
python -m unittest -v test_field005.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python field005.py --dataset iris --seed 137 --policy relation_frontier
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python benchmark.py --cohort audit --workers 2 --output audit-results.json
python verify.py --dataset iris --seed 137 --ledger experiment-results.json
```

The separate GitHub Actions matrix independently replays all audit cases, checks data provenance and frozen-model evidence and retains detailed per-run proof artifacts. The checked-in `experiment-results.json` is a compact audited ledger; individual query-level receipts can be reproduced from the pinned code and original source.

## Frozen audit result — 3 additional seeds; 30 audited cases

The above methodology and fixed candidate policy were completed **before** auditing seeds 137, 139 and 149. The model and query selection policies were not changed in response to the audit. All 30 cases are saved in `experiment-results.json` with exact source identity, ordered queries, frozen proof digests, model choices, and evaluation outcomes. Query-level proposal and receipt chains can be reconstructed by `verify.py` using the original owner adapter.

**Full-budget audit (correct labels across the three repeated, overlapping historical test splits):**

| Query policy | Iris raw /90 | Iris relations /90 | Wine raw /111 | Wine relations /111 |
|---|---:|---:|---:|---:|
| random | 88 | 88 | 109 | 108 |
| geometry | 88 | 88 | 110 | **110** |
| raw_margin | 88 | 88 | 110 | **110** |
| raw_committee | 88 | 88 | 109 | 109 |
| relation_frontier | 88 | 88 | 110 | 109 |

**At 25 label queries**, the Wine `relation_frontier` acquired labels yielded **111/111** with the selected raw classical estimator, compared with raw margin 108/111, raw committee 110/111, geometry 109/111 and random 104/111. But *using the relational estimator on those same relation-frontier labels* yielded 108/111, versus 110/111 for raw-margin's relational classifier. At full Wine budget, relation-frontier raw ties raw-margin and geometry (110/111), while its relational classifier loses by one. At Iris query 25, relation-frontier raw ties raw margin (89/90), and at query 40 it loses to geometry by one. The 12-label bootstrap scores should not be attributed to relational learning: the three active policies and geometry start identically.

**Verdict: no general advantage over strong classical active learning.** A small conditional 25-query Wine acquisition benefit exists for the raw model on these particular repeated splits. It is not a superiority result for the relational classifier or a robust, new active-learning algorithm. The datasets are old and likely familiar; audit seeds reuse the same individuals across splits. The result favors a future independently sourced, genuinely blind trial rather than further post-hoc tuning of these holdouts. The concrete failure is now inspectable: our relation-disagreement acquisition heuristic is competitive but insufficient to dominate a classical uncertainty/geometry baseline.
