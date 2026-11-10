# FIELD-006 — The Counterexample Question: proof-preserving selective retraction

**Research question.** Can MOTIF target its next archived observation toward a disagreement likely to **falsify a specific unsupported local prediction** while retaining independent, still-compatible explanations? Does that selection beat strong classical active-learning methods with the same label budget?

**Status: RESEARCH HOLD.** Implemented and executed with the original archived Iris and Wine data. No live source connection, no new scientific experiment, no universal relational-law refutation, no nonclassical algorithm, no reliable general superiority claim. This study stacks on unmerged FIELD-005/004/003/002/001.

## Connection to the original idea

One archived fact does not automatically become an entire true universe. A verified source observation can support multiple *possible* explanations. Those explanations imply testable local predictions. A contradictory source observation can refute one local prediction without erasing another independently supported route. This is selective truth maintenance, not global truth by consensus.

```
archived source fact(s) → six competing frozen local predictions
                               ↓
            search unlabeled training measurements for disagreement
                               ↓
                   propose next source-row question
                               ↓
             original FIELD-003 Owner.query + Owner.verify
                               ↓
             OBSERVED_MATCH or REFUTED_LOCAL_PREDICTION
                               ↓
                preserve alternative valid evidence routes
```

## Exact boundaries and inherited data

- Historical Iris (Fisher/UCI, DOI 10.24432/C56C76) and Wine (Aeberhard/Forina/UCI, DOI 10.24432/C5PC7J) source snapshots are inherited **unchanged**, with bytewise SHA-256 source checks in FIELD-003. The loader and label owner are the **unmodified original FIELD-003 source files**. These are repeatedly used, public ML benchmarks, not independently blinded 2026 records.
- Row-ID-only 60% query pool, 20% untouched tuning, 20% heldout test, as in FIELD-003. Each learner receives the *entire unlabeled query-pool measurement table* and queried labels, not literally one datum. Only the `Owner` gives labels and rechecks source claims; no source test/tuning label is provided to the query selector or fit routine.
- New audit split IDs **157, 163, 167** were declared in code before running this particular FIELD-006 scoring protocol. The underlying datasets and their difficulty had been inspected in past experiments; this is **not** a new independently sourced prospective trial. Each audit reuses overlapping individuals; 90 Iris / 111 Wine heldout predictions are **not independent specimens**.
- Every acquisition strategy gets the **same 12-label geometry-first bootstrap** and exactly **40** source-label queries per run. Score final models both at query **25** and **40**. The same FIELD-005 5-model raw and 3-model relational training-CV portfolios are fitted after acquisition for every policy. The 25-label checkpoint model is frozen and subsequently scored on heldout data; no test/tuning label guides selection.

## The new query policy and fairer classical controls

1. `counterexample_relational`: six trained model views (raw SVM, raw forest, signed relational SVM, interaction relational SVM, signed relational tree, interaction relational tree). At every third new label from query 12 onward, freeze the six candidates. Each prospective source query is scored using weighted two-way disagreement: an entropy estimate over votes, minimum opposing evidential weight, unlabeled density, coverage and deterministic tie breaks. A relational-vs-raw contradiction is prioritized when it exists. The weights use **observed past prospective prediction successes/failures** with Beta(2,2)-style smoothing; these adaptively selected observations are **not an unbiased reliability calibration**.
2. `counterexample_raw`: the **same six-member committee size**, score calculus, query budget, and bootstrap, but with only raw-feature SVMs, tree, logistic regression, forest and ExtraTrees. This isolates whether adding relational predictions helps versus an equally sized classical version-space-like committee. Raw and relational fits may still have different runtime costs; no measured compute parity is claimed.
3. Existing FIELD-005 conventional comparators: `raw_margin` (RBF-SVM uncertainty), `raw_committee` (SVM/forest disagreement), `relation_frontier` (earlier three-view relational-disagreement strategy), and `geometry` (farthest-first). All receive the same data, labels budget, and final prediction candidates.

The evaluation metric is the number of correct historical binary classifications at the two predeclared label checkpoints. Success against a particular baseline is not victory against classical active learning generally, and failure is retained rather than optimized away. Each `BEFORE_OBSERVATION` packet contains the row, source scope, competing proposed predictions, normalized selection evidence and a frozen SHA-256 digest. The original source reply comes **after** proposal and is independently checked against the archived dataset. Every frozen local prediction is recorded as matched or refuted; no entire model or global causal relationship is declared disproven by a single error.

## Truth-maintenance witness

`lineage.py` implements typed source roots, PENCIL predictions, `OBSERVED_MATCH` vs `REFUTED_LOCAL_PREDICTION`, acyclic AND-of-supports / OR-of-alternative-supports and selective dependency retraction. A false supported route is withdrawn while independent valid alternatives remain. Unresolved predictions cannot bootstrap themselves into evidence. The local ledger checks rehashed forged source replies using the original `Owner`, and accepts no unknown source. Ledger checksums detect drift but are **not authentication**. The recorded audit rows contain source/ordering/evidence lineage digests; `verify.py` regenerates full per-query packets and the `Lineage` graph locally. This prototype does not separately publish every source fact in an authenticated external store.

## Audited outcomes (all three split seeds; overlapping historical records)

At **25 source queries**, selected raw / relational model correct labels:

| Query policy | Iris raw /90 | Iris relational /90 | Wine raw /111 | Wine relational /111 |
|---|---:|---:|---:|---:|
| Counterexample relational | 83 | 84 | 108 | 108 |
| Counterexample raw (six-member control) | 84 | 83 | **109** | 105 |
| Raw margin | 84 | 85 | 107 | 108 |
| Raw committee | **85** | **86** | 108 | 108 |
| Earlier relation frontier | 84 | **86** | 108 | 108 |
| Geometry | **85** | 83 | 107 | 107 |

At **40 source queries**:

| Query policy | Iris raw /90 | Iris relational /90 | Wine raw /111 | Wine relational /111 |
|---|---:|---:|---:|---:|
| **Counterexample relational** | **85** | **86** | **108** | **109** |
| Counterexample raw | 84 | 84 | 107 | 108 |
| Raw margin | 83 | **85** | **108** | 108 |
| Raw committee | 84 | **85** | **108** | **109** |
| Earlier relation frontier | 84 | **85** | 107 | 108 |
| Geometry | **85** | **85** | **108** | **109** |

**Finding:** The targeted relational query strategy produced a small conditional advantage over its **matched six-view raw committee** at 40 queries (Iris relational 86 vs 84, Wine relational 109 vs 108). It also beat conventional classical active acquisition by **one Iris label** with the relational classifier at query 40 (86 vs 85), while **tying** the strongest Wine classical control (109 vs 109). But at **25** queries, existing classical committees were better on Iris, and the raw committee won Wine raw (109 vs 108). This is *not a robust full-method classical victory*: tiny absolute differences on public, correlated resplits, multiple inspected prior experiments, differing model-fit costs and no independent dataset replication.

The experiment recorded **93 Iris and 66 Wine refuted model predictions** for `counterexample_relational` across the three repeated audit splits. These are *local, previously registered per-record forecasts* that disagreed with the archived source label—not disproven universal scientific propositions. The strong raw six-member control yielded 97 and 95 local disagreements on the same tasks, so mere disagreement/refutation counts do not establish superior science.

## Reproduction

Use the same interpreter and pinned dependencies as FIELD-005: Python 3.13, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0. Limit BLAS threads to avoid nondeterministic performance. SOURCE and CV code lives on this **stacked branch**; running these files standalone without the inherited parent paths will not work.

```bash
python -m pip install numpy==2.3.5 scipy==1.17.0 scikit-learn==1.8.0
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s experiments/field006 -p 'test_field006.py' -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/field006/benchmark.py --dataset iris
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/field006/benchmark.py --dataset wine
# Complete all source queries for one case and reenter:
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/field006/verify.py --dataset iris --seed 157 --policy counterexample_relational --save /tmp/field006-source-proof.json
```

The sharded GitHub Actions workflow runs both full dataset audits and the dedicated adversarial tests, uploading reproducible proof artifacts. `experiment-results.json` includes **all 36 cases**, frozen model/selection ancestry digests, source revisions, counterexample query counts, refutation counts and scores. The CI verification is not a substitute for an independent owner-controlled trial.

## Next falsifier

Freeze the architecture **before** receiving a separately owned, newly selected task family and independent blind test labels. Compare stronger cost-matched classical query policies (including balanced ensemble entropy, Bayesian expected-error-reduction and expected model change), report CPU/model-fit costs, confidence intervals from independent subjects where legitimate, and measure time-to-threshold rather than cherry-picking 25 or 40 observations. True support-weighted proof objects need independent source authentication, provenance DAGs for *model-generation assumptions* and calibrated error propagation; any method that fails should remain visible.

**No automatic merge, production inference, external observation, MCP deployment, human contact or irreversible action is permitted by this research branch.**
