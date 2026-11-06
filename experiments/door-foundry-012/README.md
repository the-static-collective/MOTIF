# MOTIF-012 — THE HIDDEN SOURCE

A test of **hidden common-origin inference under uncertainty**, continuing [MOTIF-011 #94](https://github.com/the-static-collective/MOTIF/pull/94) and its independently reviewed CANNON-096 source graph.

**Question:** When five reports *claim* to be independent but use the same unusual language and appear close together in time, is this five independent observations, two upstream clusters, or a single hidden upstream source? Can MOTIF avoid falsely dismissing genuine independent corroboration and select the next most valuable provenance question?

## What actually runs

The original MOTIF-009 source-owned bounded text-to-image flow produces **four actual synthetic PNG world hypotheses** (red crate left/right × partial/full wall). The original GRAFT-030 generated visual operator and CANNON-095 review are rebuilt and replayed as before. The source-pinned CANNON-096 independent review remains active for the earlier MOTIF-011 source-dependency experiment.

**MOTIF-012** introduces a new *latent* provenance dimension on top of the existing world uncertainty:

| Hypothesis | Effective independent roots | Hidden root structure |
| --- | ---: | --- |
| ONE_ORIGIN | 1 | All five reports share one upstream measurement |
| TWO_CLUSTERS | 2 | Two groups of shared origin |
| INDEPENDENT_FIVE | 5 | Five original independent measurements |

All five synthetic report records explicitly **claim independence**, share the same synthetic distinctive phrase and closely spaced timestamps. **None is authenticated.** Rather than treating the self-declared source IDs as proof, MOTIF retains all three explanations and calculates an exact rational Bayesian posterior over source-partition × PNG-world hypotheses.

The sensor model assumes 80% accuracy per *true original root*: five reports sharing one root contribute one likelihood, five independent reports contribute five, and the two-cluster case contributes two. Original picture priors are those of MOTIF-009. **These probabilities are authored fictional assumptions.**

### Evidence bundling, not double counting

Distinctive phrasing, temporal coincidence and apparent source artifacts are correlated indicators. MOTIF combines them into a **single simulated cue bundle** with a declared likelihood conditional on origin structure, instead of pretending each is an independent scientific measurement. Any cue model that claims real source authentication or quietly replaces the likelihoods is held.

The five test cases include explicit opposite-direction controls:

| Synthetic fixture | Joint cue | Intended falsification |
| --- | --- | --- |
| HIDDEN_SHARED | Shared upstream token (hypothetical) | Five apparently distinct reports may actually be one source |
| INDEPENDENT_CONVERGENCE | Independently captured originals (hypothetical) | Identical words and timing must **not automatically be dismissed** as copying |
| TWO_ACTUAL_CLUSTERS | Two upstream receipts (hypothetical) | Two correlated clusters rather than one or five |
| SIMILAR_WORDING_ONLY | Unusual phrasing alone | Do not claim provenance certainty; **HOLD** |
| NO_ORIGIN_EVIDENCE | No additional useful cue | Do not manufacture a source attribution |

In the authored likelihood model, posterior mass for the designated hidden source hypothesis is approximately **95.9%** for HIDDEN_SHARED, **97.6%** for truly independent convergence, and **96.1%** for TWO_ACTUAL_CLUSTERS. These values reflect **the invented conditional cue likelihoods**, not a measured origin classifier or proof about people. All alternative hypotheses retain nonzero probability.

The model's output also includes a **mixture posterior for each original actual PNG world**, because treating five reports as independent or as one source changes what those reports imply about whether the wall is passable. A naive five-independent-report posterior is retained as a counterexample to inappropriate confidence.

## Questions instead of invented certainties

When only shared wording is available, MOTIF does not assert one upstream source. It computes which **proposed question** is worth asking under a declared loss model:

- Ask for original upstream artifacts / source receipts.
- Ask how, when, and through which capture paths the accounts first arose.

An exact 0/1/2-question **adaptive cost-sensitive tree** considers the cost of questions, expected wrong dependence attribution, the cost of dismissing genuinely independent reports, and the option to stop and explicitly **HOLD**. A separate exhaustive classical enumeration confirms every computed expected loss.

No question is actually sent. Answers are **synthetic conditional response distributions**; the modal-answer trace is for readable test explanation only, not an observation.

## Provenance controls

The original MOTIF-009 question packet and all four original PNGs are verified through source-owned `world_model.verify_original`. The older MOTIF-011 graph mechanism is source-exercised. Five synthetic claim receipts, the joint cue receipt, and every report's append-only chain are separately content-addressed.

All **28** new regression tests cover hidden source controls, false-positive genuine independent agreement, two-cluster inference, ambiguous phrasing, exact Bayes reference, closed-world assumptions, question cost and stopping, unknown question refusal, forged authority, altered source PNGs, cue likelihood tampering, and immutable ledger history. The hosted workflow also reruns the original 23-test MOTIF-010 suite, 25-test MOTIF-011 suite, original GRAFT source-owned tests, CANNON-095 and CANNON-096 reviewer.

## Critical limitation

**This does not identify real hidden source connections.** The available cue types and likelihoods are hand-authored; the source identities and their apparent capture paths are fabricated for a finite test. The code proves how to *evaluate competing common-origin explanations if a meaningful cue is available*, not how to obtain genuine source attestations, evaluate real writing similarities or timestamps, resolve account identities, or detect hidden collusion without evidence.

Even a high model posterior is conditional on the artificial **one/two/five** hypothesis family. Genuine origin structure could differ. CANNON-096 verifies a declared source-dependency graph **only** and does not authenticate witnesses. Exact hashes establish byte integrity, not truth. The source-native and independently enumerated classical methods **tie**; no superiority over established Bayesian latent-variable or active-learning techniques is claimed.

No real people were identified/contacted; no images were observed in reality; no APIs, T5 nodes or external services were called; no deployment, automatic merge, or code admission occurred.

## Reproduction

The read-only GitHub Actions workflow `.github/workflows/door-foundry-012.yml` regenerates the original MOTIF-009 / MOTIF-010 / MOTIF-011 evidence and independent CANNON-096 held review before running:

```sh
python experiments/door-foundry-012/hidden_source.py \
  --question-dir evidence/original-active-question \
  --out evidence/hidden-sources

MOTIF009_QUESTION_DIR=evidence/original-active-question \
  python -m unittest discover \
    -s experiments/door-foundry-012 \
    -p 'test_hidden_source.py' -v
```

The artifact contains genuine (synthetic) original PNGs, GRAFT/CANNON owner evidence, original Bayesian and provenance ledgers, five new latent-source scenario packets, new append-only source-claim chains, closed-world questions, and all test output.

**MAIN ≠ CANON. MERGED ≠ ADMITTED. TESTED ≠ SELECTED. SELECTION ≠ EXECUTION.**

### Next falsifiable boundary

Test on *novel* undisclosed source-partition shapes, correlated/misleading forensic cues, out-of-support origins, and real user-consented provenance metadata **without identifying people from stylometry**. Benchmark false positives and uncertainty calibration against classical dependency and Bayesian source-discovery baselines. The principled next job is an evidence acquisition interface that keeps source consent and original-identity authority separate from AI inference.

## Independent CANNON-097 reviewer added

[CANNON-097 draft PR #97](https://github.com/the-static-collective/CANNON/pull/97) now independently verifies this exact original source and the five newly generated MOTIF-012 packets. Its source code is pinned at immutable CANNON commit `788739025352b89d57928bf145953befe3db6a37`.

The reviewer **does not import MOTIF's Bayesian or question-selection code**: it recomputes the latent 3×4 source/world posterior with exact BigInt rational arithmetic in JavaScript, independently replays the optimal 0/1/2-question policies and checks all original synthetic reports, their content hashes, the four original PNG hashes, and the explicit no-witness-authentication boundaries. Original canonical Python JSON SHA-256 records are checked using a separate standard-library script rather than MOTIF application code.

The standalone CANNON-097 experiment has **14 independent tests**, including forged-human-attestation and false-independence controls. Its own read-only workflow passed at its final documentation head. The MOTIF-012 native workflow checks the actual emitted MOTIF-012 evidence against this independent CANNON reviewer as a required test, recording a separate unsigned `HOLD_LATENT_ORIGIN_MATH_REPLAYED_WITNESSES_UNAUTHENTICATED` receipt. **No source identities have been authenticated.**
