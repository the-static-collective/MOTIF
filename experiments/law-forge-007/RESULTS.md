# LAW-FORGE-007 — Measured classical lookup assimilation

**Date:** November 5, 2026.  
**Tested source revision:** `7d4ebb7602698ce12669465608037d4bfdef157a`.  
**Successful dedicated workflow:** [Classical Lookup Assimilation, run #5](https://github.com/the-static-collective/MOTIF/actions/runs/42087744203).  
**Portable cartridge + complete benchmark:** [GitHub Actions artifact `law-forge-007-lookup-assimilation-receipt`](https://github.com/the-static-collective/MOTIF/actions/runs/42087744203/artifacts/13443533197) (retention through December 5, 2026).

All **118 automated tests passed** across seven suites: inherited 14 + 18 + 16 + 16 + 18 + 17, and 19 new adversarial lookup-skill tests. The actual benchmark ran, produced inspectable JSON and a standalone source-revision-pinned lookup skill cartridge. The initial run exposed a literal escaped-newline syntax typo in the new synthetic source module; it was corrected. The above later complete run passed.

## Exact lookup is now a callable skill

`experiments/law-forge-007/desk.py` accepts strict JSON-stdio `assimilate` and `predict` requests. It returns a `motif.law-forge.lookup-skill.v1` data-only **proposal** containing the source contract, source revision, full observed truth table, snapshot digest and, if beneficial under the declared cost, a compact program and explicit correction cells.

The original `LAW-FORGE-006/inventor.py` program compiler is reused directly. A source-authoritative classical lookup is *never* replaced by a merely plausible symbolic formula. The optional compact formula is verified on every member of the source snapshot; in the closed six-input domain it carries exactly the same information as the classical table.

A source with seven channels cannot safely reuse the six-link grammar: the skill retains exact raw lookup rather than inventing an unsupported seven-channel program. A six-link domain with one exception to the normal three-path reachability rule can emit a compact three-path formula **plus an explicitly witnessed correction**. This demonstrates actual synthesis + classical residual patching.

**Absence is not false:** partial source tables return `HOLD_UNOBSERVED_CONFIGURATION` for unknown inputs. The entire partial source class is withheld at independent review, even when individual rows can be looked up. Source contract/revision changes return `HOLD_SOURCE_CONTRACT_CHANGED`. The skill never promotes itself or acquires real authority.

## Development — 13 authored mechanisms × 2 seeds = 26 synthetic worlds

| Predeclared method | Review eligible | HELD | Heldout predictions covered | Wrong covered |
| --- | ---: | ---: | ---: | ---: |
| Old four-channel projection | 2/26 | 24 | 128 | 0 |
| **Assimilated hybrid classical skill** | **20/26** | 6 | **1,664** | **0** |
| Strong complete classical lookup | **20/26** | 6 | **1,664** | **0** |
| Partial-table negative control | 0/26 | 26 | 0 | 0 |

## Frozen separate evaluation — 13 mechanisms × five unused seeds = 65 worlds

| Predeclared method | Review eligible | HELD | Heldout predictions covered | Wrong covered |
| --- | ---: | ---: | ---: | ---: |
| Old four-channel projection | 5/65 | 60 | 320 | 0 |
| **Assimilated hybrid classical skill** | **50/65** | **15** | **4,160** | **0** |
| Strong complete classical lookup | **50/65** | **15** | **4,160** | **0** |
| Partial-table negative control | 0/65 | 65 | 0 | 0 |

The hybrid created 65 proposal-only lookup cartridges in these final worlds:
- **25** compact exact programs (including some proposed programs later rejected for independent source behavior changes).
- **5** compact programs with small, explicitly witnessed exception ledgers.
- **35** classical raw lookup programs when compact synthesis was unsuitable or the source contract had seven channels.

Exactly **50** of the total 65 proposals were independently review-eligible. The other **15** HELD worlds included three deliberately shifting/hidden-context mechanism families across five seeds each. **No test predictions were approved for the HELD worlds.**

This experiment used all **64** controlled source configurations in each six-input world or all **128** in each seven-input world. Across the 65 final worlds there were **5,440 training observations per complete-table method**. Review and heldout test repeat the same finite configurations under separately generated simulator outcomes: **there is no demonstration of predicting a previously unseen configuration, no learnable physical dynamics, and no independent new-world generalization**.

The old four-channel method failed on many mechanisms whose outcomes depend on later channels, demonstrating why rigid previous observation schemas fail. The new source-width-bound lookup is a representation/transport improvement over that artificial restriction.

## Method promotion / classical comparison

`NO_METHOD_PROMOTION`.

The assimilated hybrid **ties an ordinary complete classical lookup** in review-eligible worlds, heldout prediction coverage and covered errors. It does not outperform classical retrieval, nor claim an unknown physical law, superior active inquiry, magical truth or consciousness. Symbolic compression may reduce *declared descriptive size* in particular worlds but no hardware storage, energy, processing speed, physical action cost or operational integration cost was measured.

The novel contribution for this prototype is architectural: the full-information control has been integrated as a strict, callable, source-versioned skill alongside verified symbolic representations and explicit exceptions, with abstention when evidence/contract fails.

## Runtime boundaries and inheritance

No production deployment, autonomous merge, real source authorization, private data access, native ALEX storage, native GRAFT compilation or CANNON admission occurred. Native original Dogram ablation was independently executed and verified in **LAW-FORGE-006** CI, not newly invoked by this 007 trial. The new skill remains a research program on a stacked draft branch.

Source hashes identify bytes, **not authentic witnesses**. The synthetic source owns the evaluator but is researcher-authored, not independently authored externally. Three is no more privileged than two; ternary is not baked into this lookup skill.

## Next falsifiable step

Try a source whose input-domain size is too large for exhaustive truth-table sampling. The exact lookup remains a conservative memory of measured points. Require the program constructor to propose bounded high-information experiments and verify predictive generalization *without being allowed to see heldout labels*. Compare against a strong classical nearest-neighbor/decision-tree/model-based baseline and account for time, source permissions, uncertainty and cost of inaction. Refuse if evidence cannot distinguish candidate mechanisms; do not silently promote a guessed rule.
