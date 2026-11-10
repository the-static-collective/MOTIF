# MOTIF FIELD-003 — The Real-Data Aperture
## One witnessed sample, competing hypotheses, and bounded new predicates

**RESEARCH HOLD.** This is an offline, reproducible research prototype built against **independently collected, historical physical measurements**, not a live experimental source or a newly invented scientific law. The learner starts with one historical label query, *not* literally one piece of information: it also receives all **unlabeled measurements within a training pool** and a predefined arithmetic/decision-tree operator grammar. It never inspects validation/test labels until its queries and models are frozen.

## Source ownership and authenticity boundary

Two independent datasets (distinct domains, not newly collected for this experiment):

1. **Iris:** Fisher (1936), 150 flowers, four measured dimensions (sepal and petal lengths/widths), recorded by UCI at [DOI 10.24432/C56C76](https://doi.org/10.24432/C56C76). This is the **scikit-learn 1.8.0 `iris.csv` mirror** of the UCI data, not the corrected `bezdekIris.data` variant; UCI documents two historical differences. Predict historical `virginica` vs other recorded species.
2. **Wine:** Aeberhard and Forina, 178 wines from three cultivars, 13 chemical measurements, [DOI 10.24432/C5PC7J](https://doi.org/10.24432/C5PC7J); mirror from scikit-learn 1.8.0 `wine_data.csv`. Predict historical `class_2` vs other cultivars.

Both datasets are CC BY 4.0 according to UCI: original attribution and DOIs above; source byte snapshots are included for fully offline reruns. They are **well-known ML benchmarks with possible exposure in model development** and therefore do not constitute a truly blind external scientific assessment. SHA-256 file pins are hard-checked before any run. A hash is a byte-identity check, not proof of primary-owner authentication.

## Fixed protocol (authored before the first scored local run, not prospectively registered/blinded)

- Seeds: `11,23,37`; SHA-256 row-ID-only shuffle; per seed 60% training query pool, 20% untouched tuning and 20% untouched final test. The learner only receives unlabeled measurements of the training pool.
- Source queries: **60 Iris labels** or **75 Wine labels** per seed. Query budget is the same for active and passive selection. At time zero, exactly one training label is queried and retained with a source-linked checksum.
- Baseline grammar: a single feature threshold (`UNARY`/decision stump), optimized by classical CART/Gini.
- Active investigation: first 12 labels by geometry-only farthest sampling; subsequent labels by disagreement between current stump and composed classifier and/or proximity to current boundaries. The `random` control queries the same number of examples in fixed pseudorandom ID order. Both begin with one query.
- If 18+ labels have been queried, both target classes appeared and the stump has 3+ training mistakes, **propose** a grammar expansion: normalize features using *unlabeled pool data*, take six best observed unary features (from training labels), compose pairwise z-score additions/subtractions, then fit a depth-2 CART classifier on primitive and derived features. These derived arithmetic relations were **available as author-programmed operators**, not invented outside the supplied language.
- If no expansion is triggered, the learner stays within the unary grammar. Save each actual query's proposed row and source-query counter **before requesting its label**; store independently recomputable source receipts; record the 20-, 40-, and final-query model snapshots. No label claim is promoted into scientific causality.
- Freeze the final model, provenance and observation traces; then, and only then, compute untouched tuning and test scores. No tuning-driven model selection. A standard depth-3 CART on the *same acquired labels*, without composed features, is a strong classical comparator; a stump on the same labels is the ablation control.

The schema is `motif.field003.v1`. The separate source `Owner` class seals recorded labels against the learner's query-selection interface, but all logic runs in the same Python interpreter: this separation is **architectural, not a secure privacy boundary**.

## Measured local results (first recorded run)

**Total test predictions aggregate three fixed splits**, but their samples overlap; do **not** treat 90/111 as independent newly recruited individuals or claim statistical significance.

| Dataset | Query selection | Stump (initial grammar) | Composed depth-2 model | Classical depth-3 CART |
| --- | --- | ---: | ---: | ---: |
| Iris | Active | 81/90 | **81/90** | 82/90 |
| Iris | Passive random | 80/90 | **80/90** | 80/90 |
| Wine | Active | 105/111 | **110/111** | 109/111 |
| Wine | Passive random | 105/111 | **107/111** | 106/111 |

The active grammar expanded in **1/3 Iris** runs and **3/3 Wine** runs, generating a used computed relation in each triggered case. The random control expanded in **0/3 Iris** runs and **2/3 Wine** runs. For Wine, learned relation examples included normalized `flavanoids + hue` and `flavanoids - color intensity` in different splits. These are **predictive features of this dataset**, not new chemical truths or causal explanations.

**Learning curve highlights:** Iris active accuracy did not improve with more labels on these splits (28/30, 27/30, 26/30 by budget 60). Wine active at 20→40→75 observations was 33→35→37/37, 30→36→36/37, and 35→36→37/37 across seeds 11,23,37. Passive controls were competitive and sometimes better at earlier checkpoints. There is no robust proof of increasing investigative productivity.

**Verdict:** Real recorded measurements falsify some initial unary explanations, and a fixed classical generator supplies meaningful composed predicates used by the learner. On Wine, composition raised observed accuracy above the stump while the stronger classical CART performed similarly (within one correct label across overlapping splits). **No novel mathematical operator, external causal relationship, autonomous method invention, robust active-learning superiority, or recursively compounding intelligence is established.** No real plant or wine species determinations should rely on this proof of concept.

## Reproduce (Python 3.10+ standard library)

```bash
cd experiments/field003
python -m unittest -v test_field003.py
python field003.py > /tmp/field003.json
cmp /tmp/field003.json experiment-results.json
```

Exact data pins, all 12 result cases, selected feature names, evidence packet SHA-256 hashes, and all three query-budget checkpoints are in `experiment-results.json`. Ten adversarial/reproducibility tests include source drift, independently rehashed forgeries, illegal label requests, split leakage, proposal-before-response order, actual two-feature feature generation, and exact reentry.

## Honest next falsifier

Use a **newly obtained, preregistered, third-party-sealed** source where neither the task designer nor the investigator knows labels/patterns before test. Compare equal-budget raw-feature CART/RF and strong active-learning policies, assess statistical uncertainty over *independent* units, test noisy and misclassified outcomes, and require source-authenticated measurements. To test method transfer, allow only a previously learned operator with recorded provenance; freeze it *before* the new domain is selected. Failure to outperform must remain a first-class receipt.

**No automatic merge, new deployment, ChatGPT/MCP connection, or external action is authorized by this experiment.** FIELD-003 is a new stacked draft above FIELD-002 (which stacks on FIELD-001), not main.
