# LAW-FORGE-008 — THE UNKNOWN WORLD
## Classical lookup remembers. The Question Machine asks where evidence matters.

**Hypothesis:** In a finite 12-channel synthetic world with **4,096 possible settings**, a source-owned, bounded inquiry desk can retain exact classical lookup and issue useful, discriminating membership questions without exhaustive measurement. On unseen inputs, a bounded classical version space predicts **only when surviving hypotheses agree**. Risk-weighted experiment selection is tested against a strong ordinary classical entropy selector, a fixed query policy, a classical CART-like decision-tree classifier, and exact lookup alone.

**Status:** a source-separated, offline synthetic investigation. This branch stacks on LAW-FORGE-007 draft PR #68. No GRAFT/CANNON/ALEX production integration, live probes, autonomous source credentials or automatic promotion.

## New capability: experimental inquiry under an incomplete source domain

LAW-FORGE-007 built a callable exact lookup skill with typed source revision and verified compact expression, but required complete measurement of small finite domains to obtain independently review-eligible models.

Here only **four source observations** are initially present. Each strategy receives a **160-card read-only source question catalog**, with at most **24 cost units** for additional questions. Costs are owner-declared synthetic units, either 1 or 2 per card; even 24 additional observations would sample less than **1%** of the 4,096-setting domain.

The learner `learner.py` directly reuses LAW-FORGE-007's native binary-vector validator, preserves exact witnessed lookup first, and adds a finite version-space hypothesis library of **650 predeclared classical rules** (single-bit, pairwise AND/OR/XOR, three-variable AND/OR). It never imports evaluator-owned `owner.py` or sees hidden laws/test labels during model selection.

After each approved simulator response, it eliminates hypotheses that disagree with witnessed results. For an unobserved input, it returns a value only if **all surviving hypotheses make the same prediction**; otherwise `HOLD_VERSION_SPACE_DISAGREEMENT` or `HOLD_NO_CONSISTENT_RULE`. A change to the source identity/revision returns `HOLD_SOURCE_REVISION_CHANGED`. Exact classical lookup always overrides model inference on witnessed cells.

This is a legitimate form of bounded **classical active learning**, not a new mathematical learning theory or a calibrated probability. Agreement of a limited candidate library is not proof the true world lies in that library. It must pass independent source review.

## User-cost and opportunity-cost experiment

A source-owned catalog declares two separate quantities:

- **Experiment expense:** one or two artificial inquiry units per question.
- **Cost of failing to know a result:** an externally declared 1 or 5 consequence units depending solely on the input's first two channels. This is known *before* measuring the answer. It is not learned from hidden labels, not personal financial/health costs, and not proven physical harm.

The experimental policy is a classical ensemble disagreement selector:

```text
score(question) =
    vote_disagreement_between_surviving_rules
    × declared_consequence_weight
    ÷ declared_query_cost
```

When risk weighting is disabled, this is the ordinary **classical entropy/disagreement active-learning baseline**. The exact same hypothesis grammar, source catalog, initial observations and budget are used for both.

The output records review-eligible worlds, approved heldout coverage, **risk-weighted coverage**, error, query expenses and **cost of abstention**. A query proposal doesn't dispatch itself. The source-owned evaluator alone may execute its own catalog entry.

### Five predeclared methods

| Strategy | Prediction language | Inquiry choice |
| --- | --- | --- |
| `motif_consequence` | Classical 650-rule version space plus exact memory | Max disagreement × declared cost-of-not-knowing ÷ probe expense |
| `classical_entropy` | **Same** classical version space plus exact memory | Max ordinary disagreement ÷ probe expense |
| `classical_fixed` | Same classical version space plus exact memory | Fixed owner-catalog order |
| `classical_tree` | Pure-Python, depth-5 greedy-Gini CART-like tree plus exact memory | Same fixed catalog order |
| `lookup_only` | LAW-FORGE-007-style witnessed cells only, using 007's binary validation | Same fixed catalog order; unknown inputs HOLD |

A strong comparison against *the same classical active learner without risk weights* is essential: improvement over a fixed random catalog alone would be insufficient evidence that our selection policy is special. Decision-tree and exact-lookup methods provide different model classes and conservative baselines, not new source permissions.

The classical decision tree only predicts from a sufficiently supported pure leaf. Version-space consensus and tree purity both require independent review and can be fooled by a true world outside their restricted grammars. No probability forecasts or formal calibration claim.

## Hidden evaluator families and falsifiers

The evaluator has **eleven** researcher-authored source mechanism classes, selecting the relevant features with seed variation:

- Six in-grammar rules: single bit, AND/OR/XOR of two, AND/OR of three.
- Three out-of-grammar stationary mechanisms: majority of three, XOR of three, and parity of all twelve.
- Two unstable mechanisms: a source that changes its rule between inquiry and review, and a source with a hidden context effect in a declared high-consequence region.

The new source has **disjoint query, review and test input configurations**. Four initial anchors, 160 cards, 192 review settings and 320 test settings are selected without overlap; there is no access to the labels of review or test configurations during inquiry. This is an important improvement over previous experiments that tested only the same exhaustive input configurations across synthetic phases.

The training and test mechanisms nevertheless come from the **same human-authored generator family**. Seeds alter hidden indices, not the set of possible rule classes; they are not independent external domains. The review gate examines predictions on its separate 192 cases and refuses any false covered prediction or fewer than 16 covered cases. A successful synthetic review admits only a **proposal-only** model for the separate 320-case test. It is not an external truth signature or production deployment.

## Fixed scoring and method decision

**Development seeds:** 0, 1 for each of the 11 families (22 worlds).

**Separate final evaluation:** seeds 2–6 (55 worlds).

Before inspecting the results, the method promotion gate is fixed: relative to `classical_entropy`, the consequence-weighted method must have no fewer eligible development worlds, no more covered wrong predictions, no greater total inquiry cost, and at least **10% greater source-risk-weighted heldout coverage** (minimum 32 extra units). If not, record `NO_METHOD_PROMOTION`.

Even if the gate passes, only `PROPOSE_FOR_HUMAN_REVIEW_ONLY` may be emitted; no code is automatically promoted.

Consequence-weighted *coverage* is the sum of declared weights among independently approved predictions. Cost of abstention is the remaining declared weight in the 320-case test sample. An incorrect high-consequence prediction would also be weighted separately but **held by independent review** before final testing. The method is not optimizing actual delayed human suffering or legal consequences.

## Real callable, proposal-only Question Machine doorway

The new `desk.py` accepts strict JSON over stdin and supports:

- `propose`: Given a typed current source contract, synthetic observation rows, a source-owned catalog and a remaining budget, return one inspectable `PROPOSE_ONLY_SYNTHETIC_QUESTION` or HOLD. It does not execute the question.
- `predict`: Return the exact witnessed lookup value, an explicitly conditional version-space consensus, or HOLD for unobserved/unsupported inputs.

```bash
python experiments/law-forge-008/desk.py < request.json
```

The input and outputs have strict schemas, bounded observation/catalog sizes, no arbitrary URLs or privileged instructions, and `real_world_authority=false`. The workflow produces an actual sample question packet without invoking an external service. It is a **MOTIF-owned protocol proposal**, not a native live Question Machine or a source-originated network endpoint.

## Verification

Python 3.11, standard library only:

```bash
python -m unittest discover -s experiments/law-forge-008 -p 'test_*.py' -v
python experiments/law-forge-008/trial.py > law-forge-008-results.json
python -m json.tool law-forge-008-results.json > /dev/null
```

The dedicated GitHub Actions workflow also reruns inherited experiments 001–007, runs adversarial source-security and abstention tests for 008, prints all method results and archives a complete JSON receipt plus one real, data-only question proposal.

**Do not claim benchmark outcomes or test success until inspecting successful CI.**

## Nonclaims and the next genuine frontier

- The version-space rule language is *supplied* and narrow; model-consensus is not universal truth.
- We have *not* invented new inference mathematics or demonstrated robust calibrated probability.
- Query catalog, financial-like risk tags and all outcome mechanisms are synthetic and researcher-authored.
- Sampled hidden test configurations are independent from training inputs, but **not** independent from the source mechanism family.
- No native ALEX, GRAFT, Dogram, reLATTE, CANNON or online Question Machine runtime was modified by this experiment.
- No credentials, third-party private evidence, physical measurements or real-world actions are permitted.
- This experiment has no calibrated guarantee when the true source mechanism lies outside the hypothesis grammar.

**Next falsifier:** make a trusted independent source owner furnish a previously unavailable capability contract and truly unseen function class, forbid the learner from editing its rule grammar after seeing withheld results, and measure selective risk under distribution shift and changing test costs. A source-aware decision tree, Bayesian active learner and baseline with matched compute/membership costs should challenge any purported gain. If uniform sampling wins, preserve that negative result.
