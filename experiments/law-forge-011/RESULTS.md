# LAW-FORGE-011 — Signed Counterfactual Critic: Measured Results

**Date:** November 5, 2026 (US Central). **Standalone CI source SHA:** `cc3412f7986b7b82f36fd7f37b05e2e9a62b7af3`.

**[Successful original 197-test GitHub Actions workflow](https://github.com/the-static-collective/MOTIF/actions/runs/42133488597).** All 180 inherited LAW-FORGE-001–010 automated tests and 17 new 011 adversarial tests passed. A complete frozen benchmark and the actual serialized **signed reason cartridge + source-only question proposal** were emitted to the [inspectable CI artifact](https://github.com/the-static-collective/MOTIF/actions/runs/42133488597/artifacts/13464323829), retained through Dec. 6, 2026.

## Did the repaired critic actually exist?

Yes. The 010 'positive-only AND' critic was vacuous because the all-ones initial observation killed every mutation, forcing classical diversity fallback. LAW-FORGE-011 changed the *predeclared* critic grammar to **1,452 mixed-polarity Boolean conjunctions**, each requiring at least one positive and one negative literal. Every such term is false on both all-zero and all-one anchors, so neither anchor automatically excludes it.

New tests showed the signed critic exists, survives initial evidence, proposes owner-approved distinguishing questions, roundtrips in a versioned source-bound data-only cartridge, rejects forged/unauthorized mutations and retains independent reviewer/test partitions.

Across 24 development worlds, an average **438.33** signed critics survived the learning phase. Across 48 final worlds, **456.42** survived on average. **The critic now genuinely participates in inquiry; unlike 010, it is not an entirely disguised classical diversity fallback.**

## Frozen development: 12 source mechanism families × 2 seeds = 24 worlds

| Audit policy | Source-witness grammar gaps | Audit cost | Total inquiry cost | Independent review eligible | Approved heldout coverage | Wrong covered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Signed counterfactual** | **12** | 174 | 340 | 8/24 | 2,048 | 0 |
| **Classical diversity** | **12** | **167** | **333** | 8/24 | 2,048 | 0 |
| Classical nearest-observation boundary | 11 | 203 | 369 | 8/24 | 2,048 | 0 |
| Classical fixed order | 12 | 180 | 346 | 8/24 | 2,048 | 0 |
| Classical seeded random | 11 | 182 | 348 | 8/24 | 2,048 | 0 |
| No audit | 0 | 0 | 166 | 8/24 | 2,048 | 0 |

**Frozen method decision:** `NO_METHOD_PROMOTION`. Our signed method tied classical diversity in witnessed grammar contradictions while costing **7 more source-cost units** on development. The prespecified +2 discoveries/no-more-cost condition failed.

## Frozen separate evaluation: new seeds 7–10 × 12 families = 48 worlds

| Audit policy | Source-witness grammar gaps | Audit cost | Total inquiry cost | Independent review eligible | Approved heldout coverage | Wrong covered |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **Signed counterfactual** | **24** | 342 | 661 | 16/48 | 4,096 | 0 |
| **Classical diversity** | **24** | **338** | **657** | 16/48 | 4,096 | 0 |
| Classical nearest-observation boundary | 21 | 437 | 756 | 16/48 | 4,096 | 0 |
| Classical fixed order | 23 | 375 | 694 | 16/48 | 4,096 | 0 |
| Classical seeded random | 24 | 350 | 669 | 16/48 | 4,096 | 0 |
| No audit | 0 | 0 | 319 | 16/48 | 4,096 | 0 |

**The counterfactual critic is now nonvacuous, but classical diversity STILL wins on inquiry cost at identical discovered contradictions.** Do not label this a new superior algorithm.

A separately funded audit exposed *24* contradictory source-witness sets relative to the original 650-rule language across the 48 evaluation worlds, compared with *zero* under an entropy-only early-stop policy. The gain from continued auditing was already demonstrated in 010; it is reproduced here on new source mechanisms and input partitions.

Only **16/48** test worlds passed independent review and supplied **4,096 covered heldout predictions with no covered errors**. Thirty-two worlds HELD. Zero wrong covered predictions is not 100% correctness across the 48 worlds; the model abstained/review blocked where its explanation was inadequate. Review/test inputs were disjoint from all source inquiry configurations.

The new result demonstrates a more complete **reusable typed critic cartridge**, not superior falsification accuracy or new physics. Evidence digests are not independent signatures. The owners, input risks, costs and hidden worlds are researcher-authored synthetic fixtures.

## The Grok Build donor supplied in this conversation

The attached `grok-workspace-2.zip` did contain real research, especially **MOTIF-015C “The Forged Choir”**. The nested patch's 11/11 Python tests and full 512-forecast synthetic benchmark were reproduced in a local isolated environment. The broader **classical two-rumor Bayesian grid (Brier 0.198766) beat MOTIF's one-rumor grid (0.201929); an independence-only control was worse (0.271547)**.

This is useful for challenging witness-origin assumptions and correlated evidence. It is an **adjacent source donor**, not a piece of signed-Boolean control logic; the donor code was not silently imported into 011 or promoted to GitHub main. [Full pinned local intake](GROK-015C-INTAKE.md) lists the ZIP artifact SHA-256s and appropriate separate research branch/CI procedure. General Grok workspace app scaffolding should not be mistaken for MOTIF's executable research components.

## Next scientifically meaningful frontier

Do not keep widening arbitrary mutant grammars without comparative evidence. Review **cost-aware active coverage/diversity** as the default now. Introduce a genuinely independent signed/source-authorized challenge and test whether the critic can propose *new explanatory features* whose owner-approved primitives can be compiled and independently verified. Separate mechanism discovery from question selection, and ensure provenance for claimed witness-origin independence, as the 015C donor warns.

**No automerge, deployed runtime, native GRAFT/ALEX wiring or real-world permission was asserted.**
