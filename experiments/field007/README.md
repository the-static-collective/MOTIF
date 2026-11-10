# FIELD-007 — Independent-source transfer and the counterexample dividend

**Research status: HOLD, draft/unmerged.** A frozen protocol was committed **before the initial FIELD-007 test run** in [`PREREGISTRATION.md`](PREREGISTRATION.md), Git commit `dff01503ddd57492e49f29f7d1277fc10c2ad383`. We held the acquisition policies fixed when the new historical sources failed the preregistered performance threshold.

## Question

Does the FIELD-006 counterexample-and-proof-lineage active-query architecture **transfer beyond the repeatedly inspected Iris/Wine benchmarks**, and, if so, beat conventional active learning on unseen labels at the same source-query budget?

## Independent new-to-this-branch historical sources (not real blind evaluators)

1. **UCI Optical Recognition of Handwritten Digits**, via scikit-learn 1.8.0 `load_digits`. Source originally supplies 1,797 8×8 intensity-image records. This benchmark defines the prespecified two-class **3 vs 8** subset: 357 rows, 64 optical pixels. Metadata: [sklearn load_digits](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html). Exact float64/target int64 in-memory snapshot SHA-256 `41ea7cf6db2effc93950bc713ba9451755ed1787e71a9bd29032198c86a451e9`.
2. **UCI Breast Cancer Wisconsin (Diagnostic)**, via scikit-learn 1.8.0 `load_breast_cancer`, 569 existing measurements, 30 original measured features, and original two labels. [UCI DOI 10.24432/C5DW2B](https://doi.org/10.24432/C5DW2B). Dataset copy snapshot SHA-256 `25e2eb7b7a8745b1bde5ba18bc4969983d2e2f403291ecd5bde4a29ef30c3859`. **Purely a benchmarking exercise; no clinical diagnosis, medical use or action permitted.**

The SHA hash is calculated over the C-contiguous `float64` little-endian feature matrix followed by the little-endian `int64` labels, after the declared digits 3/8 restriction. This is a byte-identity assertion, **not historical origin authentication**. The original datasets were collected by third parties and differ from the FIELD-001–006 Iris/Wine benchmark, but **the evaluation owner is still a local simulation operating on known historical public data**, not an authenticated outside lab or prospective concealed dataset. No claim of independent human-subject validation is made.

## Frozen methods and source/holdout isolation

The original FIELD-006 [`lineage.py`](../field006/lineage.py) and original FIELD-004 [`RelationGrammar`](../field004/field004.py) are imported directly from the stacked parent branches. No new language or mathematical operator was invented; the new contribution is the **cross-source falsification test** of an earlier architectural idea. The protocol defines three row-ID-only seeds 211, 223, 227, each split 60% training query pool / 20% tuning / 20% heldout (rounding down for the first two). All five acquisition policies get the same 12-label geometry-only bootstrap and **50 total historical label queries**, scored at 20, 35 and 50 acquired labels.

An `ArchivedOwner` class has all original labels; its public adapter returns only the **unlabeled training-pool features**. The learner creates a `PROPOSED_BEFORE_SOURCE_QUERY` packet and corresponding local prediction supports before `Owner.query` supplies the label. After receiving a source receipt, it verifies the claimed record against its original row. Every refuted prediction is only **a local error**, not a global refutation of a scientific theory; independent successful prediction routes are retained in a typed, acyclic AND/OR graph with original source roots. The scorer is gated until all 50 queries finish; the *training-pool* StandardScaler is applied unchanged to heldout features.

The methods are: deterministic random, geometric farthest-first, raw RBF-SVM margin, a raw SVM/logistic/forest vote committee, and a six-model MOTIF committee with three raw plus signed/product relational predictions and source-feedback weighting. All policies get the same fixed final predictors: raw RBF-SVM C=2 (primary), signed relational RBF-SVM C=2, and 100-tree raw forest. The acquisition committees require varying numbers of model fits, which are reported rather than hidden. They are **not compute-cost matched**.

## What actually happened — preregistered primary endpoint

Mean heldout **balanced accuracy** over the three overlapping split seeds, at **50 source-label queries**, for the predeclared raw RBF-SVM final predictor:

| Newly challenged dataset | Best conventional active method | Best conventional score | MOTIF counterexample-relational | Gap |
|---|---|---:|---:|---:|
| Digits 3 vs 8 | Raw SVM margin | **0.989899** | 0.985269 | **−0.004630** |
| Wisconsin diagnostic measurements | Classical raw committee | **0.975831** | 0.972800 | **−0.003031** |

**Predeclared cross-domain win = FALSE.** The primary criterion was a strict win in both domains, plus ≥ 0.02 average balanced-accuracy advantage. MOTIF **lost both domains** against the strongest predeclared conventional acquisition comparator. Do not relabel the trial as a success simply because a different metric looks better.

Some secondary observations motivate new hypotheses but are *not* confirmation: On Wisconsin at 20 labels, MOTIF's signed-relational SVM averaged **0.953792**, ahead of the conventional committee's signed-relational score **0.944732**; at 35 labels it averaged **0.966813**, ahead of raw-margin's relational score **0.962666**. However, at 50 labels the conventional raw-committee relation model again exceeded MOTIF (0.963843 vs 0.961535). On digits, raw-margin's signed-relational final model scored 0.994949 at 50, versus MOTIF 0.989899. The repeated split scores share historical source rows and should not be given independent sample p-values.

The six-view counterexample method used **261 committee+scoring model fits across three splits per source**, compared to 144 for the raw-margin and raw-committee variants and 27 for random/geometry (final models still fitted for all). Computation was not equal. This is further reason the main result does not support efficiency superiority. Trial evidence is kept in [`experiment-results.json`](experiment-results.json). Its 30 source-sealed cases include digests of query order, source replies, proof lineage and frozen per-checkpoint metrics. Each case can be independently recomputed from the pinned source package with [`verify.py`](verify.py).

## Transparent scorer correction

A **first local evaluation run was invalid**: models were trained on standardized pool features but scored on unstandardized heldout features, producing uninformative 0.5 balanced accuracy for raw SVMs. This was identified before publication and repaired strictly at the heldout **evaluation adapter**, without changing the predeclared candidate models, acquisition strategies, query budgets, splits or winner criterion. **All 30 cases were rerun** using the correct predeclared pool-fitted scaler. A new regression test asserts this invariant. The invalid run is **not** used in the results above; its existence is documented to avoid implying a flawless preregistered execution.

## Reproduce

```sh
# Python 3.13, scikit-learn 1.8.0, numpy 2.3.5, scipy 1.17.0
python -m pip install 'numpy==2.3.5' 'scipy==1.17.0' 'scikit-learn==1.8.0'
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m unittest discover -s experiments/field007 -p 'test_field007.py' -v
python experiments/field007/verify.py --task digits_3_8 --seed 211 --policy counterexample_relational
python experiments/field007/verify.py --task breast_cancer --seed 227 --policy raw_committee
# Full benchmark (~30 reproducible cases):
python experiments/field007/benchmark.py --out /tmp/field007-full-results.json
```

**Tests:** 13 local passing unit/regression tests, covering dataset pins, forbidden source queries, split disjointness, malicious rehashed source labels and query ordering, owner no-test-until-freeze, shared bootstrap, independently supported alternatives, and the corrected heldout feature transform. CI independently replays the complete 30-case pinned ledger, in two source-family shards.

## Conclusion and next falsifier

The existing model composition and proof-lineage machinery **transfers operationally** to independently collected handwritten-digit and clinical-image measurements. **Its label-selection policy does not outperform the strongest classical active methods** on either fresh-to-MOTIF source family at the predeclared primary endpoint. The gain in some early secondary checkpoints is insufficient, and the computation budget is larger. This is a valuable falsification of the previous hope, not proof of model growth or autonomous scientific discovery.

A next legitimate study needs a genuinely third-party-held **prospective blinded assessment**, source-owner authenticated receipts, additional source families, cost/label-comparable classical oracles and immutable preregistration before model development. No evidence from this PR should be used for actual medical, financial, or physical decisions. **No merges, deployments or MCP connections.**
