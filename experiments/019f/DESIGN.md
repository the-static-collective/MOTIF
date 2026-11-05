# MOTIF-019F — THE PLANNER FOUNDRY
## Native Question Box × Dogram × online classical STRIPS planning

**Research question:** Can MOTIF recognize that its existing representation lacks a necessary question, use independent validation to propose a new relational guard, and dynamically generate and reselect classical planning methods after observed action failures?

**Status:** Executable, fully synthetic research (Python 3.10+, Node 20+, standard libraries only). This experiment is stacked on the draft MOTIF-015 Many Roads, MOTIF-016 Living Forest and MOTIF-017F Self-Growing Diagnostic branches. Separate MOTIF-017 and MOTIF-018 research branches also exist; this experiment uses the suffix **019F** to avoid collisions. No production JAR;VIS binding or external action.

## 1. Native original organs — SHA-pinned, not simulated

The two sources in the upstream directory are **byte-identical originals**, copied from the existing MOTIF-014 Organ Gardener research. Their Git blobs are verified before every call:

| Donor | Exact upstream Git blob | Native entry |
| --- | --- | --- |
| National Treasure Question Box (source commit 28fbf9b10d003f7c577143550d17cc17f8109cb1, unmerged PR #70) | 83574ed0a927fdefe1a53b3ece0960f011b875d0 | Node.js buildQuestionFrontier |
| Dogram partition-refinement (source commit 551b5f9df18f17ec69b452ddcdff01718e0ff771) | c201ce28ff7bb18a28496c0a2eefe2f9451526cc | Python analyze_probe_family |

The National Treasure engine produces a question and an aperture, **not an answer**. Its source, chronology, counterevidence, falsifier, competing-explanations and source-family checks are preserved. If its selected aperture is anything other than discriminator, the original Dogram algorithm is never invoked. If fully gated, Dogram computes the real finite probe partitions, refinements and separators. The bridges fail closed on donor-source drift. These are not tool grants or authenticated external information.

## 2. The proposed question can change the action grammar

The planning model incorrectly predicts that an agent carrying a parcel may open a gate immediately. A separate synthetic actuator reports failure, without revealing its hidden precondition.

A tiny typed graph-expression compiler examines TRAIN observations containing actor/relation/target triples and proposes two rival **types of questions**, not predetermined complete answer trees:

- A direct relation: does the actor wear a badge?
- A two-edge path: does actor →carries→ token →opens→ gate exist?

Both are perfectly correlated with success on TRAIN. Extra *unlabeled* DISCOVERY scenes break their equivalence as finite probes without revealing outcome labels. Native Dogram recognizes their different partitions. Separate labeled REVIEW scenes then **falsify the badge explanation** and provisionally admit the two-edge token relation. The resulting guard is allowed only if the existing typed action model includes an operator capable of producing its required fact. Missing sources, ambiguous rivals, inconsistent validation and unexpressible guards lead to HOLD, not fictional sensors or permissions.

This is ordinary bounded feature construction and independent synthetic validation. It does not demonstrate autonomous discovery of new physical causes.

## 3. Classical planning is a method, not a comparator frozen in amber

The classical.py module implements **real, bounded search** for STRIPS-style facts, goals, positive-cost precondition/add/delete operators:

1. **BFS:** minimum action count, not necessarily minimum weighted cost.
2. **UCS / Dijkstra:** strong optimal positive-cost planning comparator in the declared finite model.
3. **A-star with h_max:** admissible delete-relaxed maximum-fact-cost lower-bound heuristic, also optimal if complete.

The method foundry enumerates these search recipes **when invoked**, generates actual plans from task operators rather than fixed route tables, replays candidate plans independently, compares their cost with UCS and emits versioned, checksummed, explicit-review-only MethodCartridges. It excludes a more expensive BFS plan from promotion. Search expansions are tracked; h_max calculation expense is not fully accounted for, so expansions do not establish wall-clock speed improvements.

The online engine receives actual independent *synthetic* action receipts. On failure it invokes the native question and Dogram gates, proposes an evidence-reviewed guard and revises the sandbox operator's preconditions. It then regenerates classical method candidates and replans from the newly observed state. This is **online replanning and strategy compilation for the synthetic environment**, not live code self-modification or general algorithm invention.

## 4. Falsifiable controls and negative transfer

**Weighted control:** the one-action route costs 7; the two-action route costs 2. BFS prefers the shorter route, while UCS and A-star find the lower-cost route. The method foundry must detect BFS's extra cost.

**Gate world:** the first naive gate action fails because the unseen world requires a token. With the separately validated new graph guard, the agent can collect a token, open the gate, and deliver. A fixed fallback that does not learn takes a costly detour.

The comparison includes:
- Historical fixed fallback, intentionally lacking the new question-learning procedure.
- Generated classical planning methods with evidence-conditioned replanning.
- **A strong classical UCS with the identical new guard and identical evidence**, expected to tie the foundry on action cost.
- A **changed hidden world** whose gate actually requires a badge, where the previously reviewed token explanation fails again. The engine records the regression, excludes the failed action and takes the detour. All failed actions are charged and retained.

All task rules, labels and source family strings are invented fixtures. Independent train/discovery/review phases mean source-code separated samples, **not independently witnessed reality**. The shifted family demonstrates how a once-validated question can become harmful if incorrectly transferred.

## 5. Reproduce

Run locally with Python and Node installed:

    cd experiments/019f
    python -m unittest -v test_planner.py
    python benchmark.py

The CI workflow also runs these tests and emits complete deterministic JSON, including both original source hashes, native question and Dogram receipts, method candidates, each attempted action, incurred costs, held questions and failure under mechanism shift. No API keys, network or paid compute are required.

## 6. Explicit limits

- The question-feature grammar is limited to direct relations and selected two-edge paths discovered in observed graph triples; it does not invent arbitrary physical measurements.
- Typed operators, action effects and action costs are supplied. No system can plan with an unavailable physical action unless its capability is separately provided and permitted.
- Classical search's optimality is relative to **the stated model**, which can be wrong. An informed classical planner with the same new evidence is not weaker than MOTIF.
- A model guard selected by clean synthetic validation can fail under new hidden causes or drift. Integrating uncertain witness/compliance evidence from MOTIF-014W is a future step.
- No source hash validates truth, consent, origin or safety. No plan, question receipt or method cartridge grants real-world action authority. No automatic upstream deployment or external call occurs.

**Research claim:** A bounded research controller can actually execute the original question-framing and partition organs, discover a new *typed relational question* from its observed finite graph vocabulary, falsify a tempting rival using a separate synthetic review, and recompile classical planning methods after independent simulated action feedback. Neither general autonomous science nor superiority over optimal classical planning is established.
