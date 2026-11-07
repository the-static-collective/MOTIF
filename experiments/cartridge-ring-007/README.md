# MOTIF RING-007 — Investigate Before Abstaining

**Stage:** source-native experiment on a review branch stacked on RING-006. Not in `main`, not production, no uncontrolled network or real-world authority.

RING-006 demonstrated an uncomfortable tradeoff: blanket quarantine eliminated 10 unsafe/invalid decisive answers on an authored synthetic batch, but reduced benign decisive coverage from 14 to 8. RING-007 tests a third path, a **bounded three-state language investigation**:

```text
UNFAMILIAR USER PHRASE + SAME PINNED SYNTHETIC GRAPH EVIDENCE
                 │
     ┌───────────┼───────────────────┐
     ▼           ▼                   ▼
  KNOWN        REVIEWABLE          UNCERTAIN /
  FRAMING      READ-ONLY           EFFECTFUL
     │          GRAPH QUESTION        │
     ▼            │                   ▼
 RING-005         ▼                  HOLD
 SELECTIVE    THOUGHT-014 RAW       preserve
  ROUTE        LANGUAGE PROBE       question
                  │
       independent fixed frame
       checks allowable scope
                  │
                  ▼
      canonical *hypothesis* in
      tiny original S→A→T world
                  │
                  ▼
     original THOUGHT-014,
     GEOM-013 and optional
     REASON-006 source-owned
     selective execution
```

The engine **never** treats its native language model as an authorization source. It preserves the raw utterance's SHA256, calls the original source-pinned THOUGHT-014 language interpreter/model as a **PENCIL-only non-authoritative hypothesis**, then uses only explicitly reviewed literal/compositional grammar matches to map a tiny family of benign path questions to one canonical read-only graph inquiry. Any effect/distribution language or unmatched ambiguity yields HOLD. Nothing is published, sent, or executed externally.

**Critical epistemic limitation:** mapping `does another route survive` to `what if these are connected` is valid only under our intentionally narrow synthetic route-reachability task. We have **not** developed a general translator of English intent, nor proved the original model interpreted the raw utterance correctly. The mapping rules and risk words were preauthored by us.

## Actual learned choice from past errors (not secretly trained on test labels)

`arbitration.py` freezes the earlier RING-005 source-native router on 64 familiar authored cases and the frozen language profile. It then processes the **already observed RING-006 historical failure packet** (32 cases, previously measured with the original pinned source methods and labeled under the author-defined rubric).

It compares three **preauthored** candidate policies:

- **BLANKET:** any unknown utterance HOLD; safe, high benign coverage cost.
- **PERMISSIVE:** treat every novel phrase as a benign path inquiry; recovers useful questions but risks approving novel effect requests.
- **TRIAGE:** strict reviewed safe-question frame + separate action-risk frame + unresolved default HOLD.

The selection constraint requires **zero training unsafe/invalid decisive eligibility**; among acceptable candidates, it prioritizes potential benign coverage. Only BLANKET/TRIAGE can be admitted. The resulting frozen policy and case-specific route manifests are SHA256-bound before any new native inference. Candidate scores are structural/lexical **forecasts** on old author-supplied labels, **not** actual source-native runs of all candidate strategies.

No evaluation labels from the two later trial packets enter this selection.

## Source-owned native execution

`review_worker.py` runs inside a no-network, read-only, non-root Docker sandbox, whose original GEOM-013, THOUGHT-014 and REASON-006 source trees were extracted at their exact independent pinned Git commits. It independently rechecks the host's training language profile, public input digest, raw utterance, source-route types, proof requirements and reviewed semantic-frame verdict.

For a novel valid benign question only:

1. **THOUGHT-014** inspects the **original raw wording**, preserving its model guess as uncertain provenance, not an authoritative decision.
2. The strict reviewed frame permits a separate **canonical read-only question** on the toy graph, while leaving the source graph, observations, manifestation identities and event records unchanged.
3. The already-admitted original **THOUGHT-014 + GEOM-013** code executes the canonical query; **REASON-006** is recruited only if the synthetic task explicitly requires a proof receipt.
4. The controller receives the decision and source-call receipts, and only then consults the withheld author-generated label.

Effect requests, contradictory/invalid records, and unknown language receive HOLD **without any selected native method calls**. A prior source route failing its mandatory proof contract is an explicit source-owned **HOLD/abort**, not 32 invented decisions.

## Measured evaluation — two unseen-to-selector authored phrase/evidence packets

The 32-case *historical* shift packet was used to select TRIAGE. Two distinct **evaluation** packets each contain 32 cases and are not supplied to the selector.

| Evaluation family | Blanket guard: safe decisive answers | Investigating guard: safe decisive answers | Guarded unsafe/invalid decisive classifications |
| --- | ---: | ---: | ---: |
| RING-006 phrase templates; new evidence seed | 8 | **14** | **0** |
| RING-007 **different preauthored phrase templates**; new evidence seed | 4 | **14** | **0** |
| **Total** | **12** | **28** | **0** |

**16 additional benign decisive answers** were recovered relative to blanket quarantine across 64 authored cases, with **zero unsafe/invalid decisive classifications** under the artificial labels. There were **16 original THOUGHT-014 raw-text probe calls** on reviewed novel cases, in addition to whatever canonical-case methods were needed. This is *not* an improvement in measured CPU cost or wall-clock latency.

The original unguarded RING-005 router still returned **10 unsafe/invalid decisive classifications** in the first evaluation family. On the alternate new phrase family, its source-native full-batch runner **aborted with a required-proof failure** for unfamiliar language; it is listed as **SOURCE_NATIVE_PROOF_REQUIREMENT_HOLD_ABORTED_BATCH**, not scored as a complete set of correct/wrong decisions.

The alternate phrase family is different from the prior attack wording but **still authored by the same experimenter** and follows the same small graph problem. Therefore this is *not* independently blind human input, robustness to arbitrarily phrased unsafe instructions, or evidence of transferable open-domain language competence.

## Many-to-many hypergraph evidence

`evidence_graph.py` turns each trial into a conditional evidence hyperedge with **three tails**: frozen old policy, selected triage policy, and exact synthetic source packet. Every resulting edge has multiple heads, including:

- More benign answered cases relative to the blanket quarantine.
- Zero observed unsafe/invalid decisive answers under the authored labels.
- Still-unresolved utterances preserved instead of fabricated interpretations.
- The additional native language-probe and source-method execution cost.

The same new capability can be simultaneously **useful, expensive, incomplete and restricted to a specific evidence scope**. These are measured *synthetic conditional* relations, not globally promoted causal relationships or universal capabilities. No future discovered branch was silently made executable.

## Reproduce

```bash
python -m unittest discover -s experiments/cartridge-ring-005 -p 'test_*.py' -v
python -m unittest discover -s experiments/cartridge-ring-006 -p 'test_*.py' -v
python -m unittest discover -s experiments/cartridge-ring-007 -p 'test_*.py' -v

docker pull python:3.11-slim
python experiments/cartridge-ring-007/bench.py \
    --count 32 --out /tmp/ring007-evidence.json
python experiments/cartridge-ring-007/evidence_graph.py \
    --trial /tmp/ring007-evidence.json \
    --out /tmp/ring007-hypergraph.json
```

Docker requires the exact original source revisions in the local Git object database; GitHub Actions fetches full history and runs a source-pinned no-network container. The Docker image is tagged in this research exercise and should be pinned by digest for a more rigorous replicated experiment.

## Unresolved next tests

This is now a concrete, working proof of **review-before-commit for unfamiliar inputs**, not an autonomous general language discovery system. The next valuable falsifiers are: independently authored unseen natural text and alternate graph topologies, adversarial semantic paraphrases that bypass the preauthored risk vocabulary, source authentication from conflicting witnesses, measured end-to-end latency including initialization, reviewable proof quality beyond yes/no accuracy, and a separate safe human correction path for UNKNOWN questions.

**All external authority remains NONE. The original executable registry, outside tools, and GitHub `main` remain unchanged.**
