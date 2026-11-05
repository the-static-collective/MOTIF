# LAW-FORGE-009 — THE STRANGER / CLASSICAL ENTROPY REASON CARTRIDGE

**Predeclared research question.** Can MOTIF assimilate a portable, **actual Shannon entropy-based active learning skill**, reuse the exact witnessed-memory and version-space layers already demonstrated in LAW-FORGE-008, and discover when unfamiliar observations falsify its finite explanatory language?

**Status:** research-only stacked draft on LAW-FORGE-008 PR #72, no merge, production authority or live integration.

## Why assimilate entropy?

LAW-FORGE-008's so-called `classical_entropy` selector used **binary vote disagreement** `p(1-p)`, proportional to binary Gini variance. This selected informative questions and beat fixed catalog ordering. It is often loosely referred to as entropy, but the actual score was *not* Shannon entropy.

Here the **portable reason cartridge implements genuine binary Shannon entropy**:

```text
H(Y) = -p log2(p) - (1-p) log2(1-p)
selection_score = H(Y) / source_declared_query_cost
```

where `p` is the fraction of current, equally weighted **surviving programs** predicting outcome 1 at that specific query. This is classical expected information gain for a uniform prior over the finite deterministic version space—not a calibrated probability over natural mechanisms.

The source catalog, budget and original observations are shared fairly with a **strong inherited Gini/disagreement active-learning control**, fixed catalog, depth-five CART-like tree, and the exact lookup-only conservative control.

## Actually assimilated, callable and portable

`entropy_cartridge.py` uses **the existing `law-forge-008/learner.py` classes and functions** (`SourceContract`, typed `Question`/`Observation`, `exact_lookup`, `fitted_indices`, `signature`, `make_desk`). This is not a rewrite of a novel mathematical discovery.

The new immutable, transportable `motif.reason-cartridge.shannon-entropy.v1` packet contains:

- Exact synthetic source name / revision / challenge ID, and SHA-256 content digest.
- Full typed source observations; every exact witnessed value takes precedence over a hypothesis.
- Fingerprint of the **actual frozen 650-rule hypothesis library**, plus a version marker and algorithm label.
- Strict source-query budget spent and maximum.
- An explicit `PROPOSE_ONLY_NOT_SOURCE_AUTHENTICATED` status, `owner_must_execute=true` and `real_world_authority=false`.

The local JSON-stdio desk `desk.py` has five actions: **create**, **propose**, **ingest**, **predict**, **diagnose**. `propose` only returns a typed owner-card proposal; it does not execute the experiment. `ingest` constructs a **new immutable cartridge**, verifies the response is tied to the selected question/current source contract, and refuses stale or changed requests. Source identity cannot be cryptographically authenticated by a JSON envelope; the packet explicitly says so.

`predict` uses **the native 008 exact-first desk**, returning exact witnessed lookup, all-survivors-consensus conditional hypothesis prediction, or HOLD for uncertainty and revision mismatches. Genuine uncertainty is never encoded as a third truth value.

Run locally with Python 3.11:

```sh
python experiments/law-forge-009/desk.py < input.json
```

GitHub Actions additionally emits a **real, inspectable cartridge** and a **data-only question proposal** without calling any live source.

## The Stranger

The new evaluator-owned `stranger_owner.py` is deliberately source-separated from `entropy_cartridge.py`; the learner never imports hidden rule labels, simulator answers, or review/test data. This source is **written by the same researchers**, however. Its isolated module does not imply genuinely independent human authorship.

The opaque source offers twelve Boolean channels (4,096 potential configurations), only four initial measurements, 128 candidate question cards and a maximum 24 budget units. Every source world provides **192 independent review inputs and 256 separately withheld test inputs**, disjoint from training and question catalogs.

Ten hand-authored mechanism classes (not available to the learner):

| Class | Relation to frozen 650-rule grammar |
| --- | --- |
| Single bit | In-grammar |
| XOR of two bits | In-grammar |
| OR of three bits | In-grammar |
| Conditional multiplexer | Outside grammar |
| XOR/parity of four bits | Outside grammar |
| At-least-three-of-four threshold | Outside grammar |
| XOR of two pairwise ANDs | Outside grammar |
| AND of four bits | Outside grammar |
| XOR of two bits changing to AND on review | Deliberate nonstationarity |
| Three-bit OR with a review-only hidden exception | Deliberate hidden context |

Feature indices vary by deterministic seed but mechanism types are supplied by this research design. Development seeds 0/1, evaluation seeds 2–6. This is a **finite synthetic within-family challenge**, not true external open-world science.

## Detect a missing grammar — not just a missing answer

Classical lookup tells us whether a source observation exists. A finite hypothesis library additionally permits another meaningful distinction:

**No existing explanation fits all available evidence.**

`gap.py` uses the actual frozen 650-rule library and produces a **locally checkable, irreducible contradictory evidence core** if the model version space collapses to zero. It can prove:

> No rule in *this declared grammar* agrees with these witnessed observations.

It **cannot** prove the physical world is inconsistent, which unseen law is true, or that the system has discovered a new algorithm.

The gap packet has a source evidence digest, actual witnessed cases, relative grammar fingerprint, and `HOLD_NO_RULE_IN_DECLARED_GRAMMAR`. Its only proposed action is **`REQUEST_SOURCE_OWNED_GRAMMAR_REVIEW_ONLY`**. In particular, it cannot grant GRAFT admission or silently add a new rule after observing the heldout labels.

If at least one candidate fits training but independent review finds contradictions, the candidate still HOLDS. Do not edit the frozen library to explain away review failures.

## Controls and decision rule

All five methods get the **same four initial observations, 128-card source catalog and max-24 query budget**.

- `shannon_entropy_cartridge`: actual portable Shannon/cost skill.
- `classical_gini_008`: proven inherited score `p(1-p)/cost`, same hypothesis library.
- `fixed_catalog`: first available owner-owned query, same hypothesis library.
- `classical_tree`: inherited CART-like depth-five tree, fixed catalog.
- `lookup_only`: exact measured cells, fixed catalog, abstains on unobserved inputs.

All source owners, reviews and tests are simulated. Review must contain 128+ distinct non-duplicate source observations, cover at least sixteen predictions, and find **zero wrong covered predictions**. Only then test coverage is reported. HELD worlds never contribute zero-error successes by extrapolating unseen labels.

Frozen development selection: promote only to *human review* if the Shannon skill matches or exceeds Gini's eligible worlds and covered predictions with no extra errors **and strictly less query cost**. Otherwise: `NO_METHOD_PROMOTION`. No outcome changes the deployed method automatically.

The test is intentionally capable of demonstrating a classical **tie, failure, or gain**; the result cannot be predicted by attractive terminology alone.

## What would count as progress?

Success at this stage is a **reusable classical learning cartridge** with strict evidence lineage and action bounds, and an executable **grammar-gap certificate** that separates "I did not observe this configuration" from "no available rule can explain my observed evidence". A gain over classical Gini would be interesting; a tie or loss is still a useful result.

**Do not claim the external Question Machine, GRAFT, ALEX, Dogram, CANNON, reLATTE or live sensor integrations are accomplished.** These remain separate, review-required routes. The actual skill is a local Python JSON-stdio component plus an evidence packet in MOTIF's experimental branch.

## Reproduce

```sh
python -m unittest discover -s experiments/law-forge-009 -p 'test_*.py' -v
python experiments/law-forge-009/trial.py > law-forge-009-results.json
python -m json.tool law-forge-009-results.json > /dev/null
```

GitHub Actions runs inherited LAW-FORGE-001..008 tests, all new adversarial tests, frozen development/evaluation comparisons, and uploads inspectable cartridge / question / benchmark artifacts. **Verify actual CI before asserting the results or numbers.**

## Next genuine frontier

A third-party, independently authored source owner would need to provide an authenticated novel capability contract, its own actual query costs, disjoint unseen tests and permissioned execution. Challenge Shannon, Gini, Bayesian active learning, discriminative trees, and grammar-expansion proposals under a fixed budget. Without such source authentication or independent validation, "the machine discovers unknown physical instruments" is not established.
