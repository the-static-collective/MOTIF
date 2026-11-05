# MOTIF-027F: actual three-specialist T5 job experiment, relevance first

## Research question and execution

User asked to wire an **independent source-to-question relevance check** before the existing MOTIF-022F and MOTIF-016 reasoning modules, then ask MOTIF whether **three specialized tiny T5 nodes would help it think better**.

Implementation is complete in an isolated research branch; it does not change production JAR;VIS. The three specialized nodes are three **separate encoder roles using the SAME public FLAN-T5-small checkpoint**: (1) SCOUT nearest reviewed gate; (2) SKEPTIC task-framed 3-neighbor retrieval; (3) CARTRIDGE_FINDER matching operator-written question-purpose examples. This is not three independently trained models or three independent witnesses. They can agree for the same erroneous reason.

The new relevance guard requires a literal quoted note subject and a problem/unresolved-language span **before** sending any nominated category to the existing actual 022F typed source-calibration gate and actual 016 Living Forest. No category, quorum or source similarity can certify note authorship, truth, food permission or real action authorization. The SAME guard is also run independently as a **source-anchor-only classical baseline**.

The trial uses the **real local 77M checkpoint**, pinned public model revision 0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab, downloaded to a temporary GitHub Actions CPU runner and exercised offline. No API inference costs, real participant data or external actions. Full machine JSON receipts are archived in GitHub Actions.

## Prospective 50-case frozen synthetic study

Frozen before reading model results: experiments/027f/frozen_cases.py Git blob 6b36dd47c9cc3e260ddb91d4e9900cad61a1245e. 50 artificial operator notes, 10 each FOOD/AUDIO/ACCESS/STAFF/NONE, with intentionally resolved/negated statements in the NONE category. Research-author curated, not an external blinded human dataset. Original native rule, literal relevance lexicon and three role contracts were also frozen before CPU execution.

**Observed results from successful genuine model run 42067347676:**

| Strategy | Correct raw category (out of 50) | Relevant grounded review offers | Misleading grounded offers | Fictional utility after CPU charge |
| --- | ---: | ---: | ---: | ---: |
| Original native fixed rule, no model | 13 | 7 | 2 | -27 |
| **Independent anchored native rule alone, no model** | **37** | **31** | 4 | **37** |
| Same-source classical TF-IDF + relevance guard | 23 | 16 | 3 | -4 |
| Single actual T5 encoder + relevance guard | 25 | 16 | 3 | -4.04076 |
| **Three actual T5 nodes, 2-of-3 vote** | **24** | **15** | **3** | **-7.12192** |
| Three actual T5 nodes, unanimous 3-of-3 | 17 | 10 | 2 | -18.12192 |

The test's artificial utility is +2 correct human-held review offers, -4 misleading human-held offers, -1 missed synthetic gate, -0.1 for each measured model encoder second. This is **not** measured human welfare, real energy cost, opportunity cost of waiting or event success.

The source-anchored native rule substantially outperformed model or ensemble methods on THIS investigator-authored corpus. That source lexicon may be too specially suited to the examples and is not externally validated. It also generated four misleading offers; it cannot be used without independent source-specific verification.

The ONE actual T5 method made 16 correct grounded proposals, 3 misleading, identical to the classical TF-IDF on these metrics. The three-node 2/3 ensemble made 15 correct, 3 misleading; unanimity reduced both errors and useful recall. The ensemble was not a positive complementarity win.

The benchmark called the real T5 encoder **148 times** in total across one-node and three-node comparisons, including building the separate role reference banks. The logged one-node work used approximately **0.4076 seconds**, compared to approximately **1.40086 seconds** for the three-node design, including reference embeddings, on the GitHub CPU. Neither is a benchmark on the user's older Mac.

### Source-to-question relevance boundary passed a concrete failure test

The previous 026F false relevance example, 'We are just revising the invitation artwork,' is now held **before** the question registry is invoked, despite a synthetic T5 classifier suggesting FOOD. A real 022F source review can no longer independently validate an unrelated measurement just because the measurement is otherwise valid in a toy world.

However, the literal subject+problem matching still gets **negation scope wrong** in cases like 'We are not planning to serve a meal.' The word NOT plus the topic meal can misleadingly look like a missing meal authorization. Source spans are independent of encoder output, **not independent proofs of actual unmet needs**.

The full three-node PIPELINE produced misleading source-grounded offers on synthetic NONE situations N07, N08 and N10. **N07 and N08 were native-first short-circuit decisions; T5 was not consulted for those examples. Only N10 was an actual three-head inference error.** This matters because errors must be attributed to the component that made the proposal, not automatically blamed on T5. The same reason makes quorum incapable of granting source authority.

## MOTIF's second-order answer

MOTIF evaluated NO_T5, standalone lexical anchors, classical TF-IDF, single T5 and three-specialist 2/3 or 3/3 consensus, with the same downstream native question review. By the preregistered artificial utility, the best non-model method was **SOURCE_ANCHOR_ONLY** and the best T5 method was **SINGLE_T5_ANCHORED**, which was **41.04076 utility units behind** the strongest no-model method.

**Native automated assignment: NO_T5. Provisional model research hire: NO_T5.** This does not mean all uses of three small nodes are impossible. It means three correlated votes over the same gate question were not helpful here.

The proposed next question is more specific than 'more T5':

**Could three nodes performing different steps — semantic synonym scout, literal quotation locator and contradiction/negation challenger — improve reliable human-held questions, compared against the same three functions implemented by native symbolic code on a fresh independently prepared domain?**

This is an untested new hypothesis, *not* a result proved by the present experiment. Any new trial must preserve source authority, count extra computation and rejected/missed questions, and explicitly quantify consequence of delay before claiming a good real-world 'thinking' improvement.

## Posthoc specialist diversity audit

A separately labeled, posthoc diagnostic (NOT a new prospective success claim) examined which head contributed complementary labels: among cases where the actual three-node encoder ran, the CARTRIDGE_FINDER got the label right on **six** instances where SCOUT was wrong, while SKEPTIC did so on **two**. The heads disagreed on **29** of those cases and all three agreed in only **eight**. The hindsight oracle could select an accurate node for **25** called cases, but there is no executable selection rule with access to that oracle. These disagreements suggest useful *latent diversity*, not that majority voting improved decisions. The more grounded follow-up hypothesis is a sequence of genuinely different jobs (synonym scout → quote locator → negation challenger), with a native-only implementation of the same three jobs as the essential strong comparator.

## Honest constraints

No actual grant, fellowship event decision, venue approval, contact, outreach or production JAR;VIS feature was modified. All permissions remain human owned. The 022F and 016 records are simulated worlds with artificial priors and calibration, so their modeled 50%-to-100% classification gains never mean real-world correctness. The experimental source-note check is heuristic and not a privacy certification; do not feed it genuine sensitive personal information. No model is assigned authority to act. Full repo suites may be running after the successful dedicated model experiment.

## Reproduction

Standard library: from experiments/027f run python -m unittest -v test_nodes.py and python -m unittest -v test_postmortem.py. The dedicated workflow .github/workflows/motif027f-three-nodes.yml downloads the pinned public model once to an ephemeral CPU runner and saves only a JSON receipt. Successful baseline actual run: https://github.com/the-static-collective/MOTIF/actions/runs/42067347676 . Method contracts, synthetic source examples, and native reference guard are inspectable in this directory.
