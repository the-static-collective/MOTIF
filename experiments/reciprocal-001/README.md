# RECIPROCAL-001 — The Reciprocal Apprentice

**Status:** Experimental, local, finite, source-correctable, **not deployed**. Implemented November 12, 2026. Research continuation of MOTIF's REASON-020/021 two-circle learning and REASON-023 testimony work, but this module is independent and has **no production JAR;VIS bridge**.

## Question

Can a person and a bounded machine **improve each other's reasoning practices** without hiding source disagreements, mistaking assent for learning, or retaining a human profile?

Two-direction specimen:

1. **Human → machine:** A person with an explicitly selected fictional Boolean rule gives individual observed yes/no examples. A finite candidate learner picks its next question using an inspectable classical expected-remaining-candidates calculation. It updates only from submitted answers, preserves contested versions, HOLDS outside its vocabulary, and accepts an additional typed four-row operator only when the person explicitly provides it.
2. **Machine → human:** The person chooses a baseline inquiry *before* explanation. The room teaches one classical query-selection heuristic, then asks a different five-rule inquiry *without hints* after at least two machine-teaching observations. It shows both independent choices, not an invented IQ measurement.

Both directions meet in an inspectable local event field. Neither is granted authority over the other.

## Actual executable

- [reciprocal.js](reciprocal.js): finite, transparent learner, classical information-gain question selection, append-only observation/contest/replacement event trace, human-authored operator extension, and explicit HOLD.
- [demo.html](demo.html): phone-sized, keyboard-accessible two-way offline teaching room. Open together with `reciprocal.js` in the same folder; no build step or account. GitHub Actions also packages an **inline one-file HTML** artifact for phone users.
- [test_reciprocal.cjs](test_reciprocal.cjs): headless exhaustive deterministic tests covering both directions, conflict, correction, unmodeled rule, user-defined operator and zero external execution.
- [../../.github/workflows/reciprocal-001.yml](../../.github/workflows/reciprocal-001.yml): isolated Node 20 CI with deterministic comparison and source audit.

## What the initial synthetic test can legitimately establish

Eight independently scripted rule targets are drawn from eight author-declared Boolean functions. For each, ask source questions until exactly one candidate remains, and verify predictions on *unasked* four-row inputs when available.

| Local finite simulation | Eight target rules |
|---|---:|
| Adaptive, classical expected-remaining rule selection | 24 observations total |
| Fixed classical query order 00, 01, 10, 11 | 27 observations total |
| Both identify all eight targets | 8/8 |
| Strong matched information-gain controller | **Ties adaptive exactly** |

The adaptive approach saves 3 questions across these tiny authored tasks compared to a weak fixed-order method. **This is not a victory over strong classical reasoning.** The controller is itself ordinary classical active learning.

Human baseline candidate pool `ZERO,A,AND,XNOR,IMPLIES`: unique best row 00. Post candidate pool `ZERO,A,B,AND,NOR`: unique best row 11. The equal-probability expected remainder is 2.6 in each case. Actual human participants have **not been evaluated**. The local page simply makes human teaching/learning *possible*; no user response is captured remotely.

## Epistemic and human boundaries

- Selecting a synthetic secret rule does **not** supply it to the `Learner` API. It lives in the same web page, so this is an architectural boundary by convention, **not security isolation** or a blind human experiment.
- The machine's source labels are locally entered and **not authenticated**; a mistaken answer can mislead it. Duplicated contradictory evidence triggers `HOLD_CONFLICT`; correction requires an explicit distinct `REPLACE` event. Unsupported all-four outputs trigger `HOLD_OUT_OF_FAMILY`.
- User-defined operators are only four typed bits: no executable code, unlimited free-form grammar, general conceptual invention or learned model weights.
- No personal identity, background tracking, remote invocation, storage, upload, silent model retraining, or permission granted by success. Refresh discards state. A participant can stop immediately.
- The human before/after questions share a narrow Boolean vocabulary, use engineered exercises, and have no randomized control group. A correct post response is **not proof** of lasting understanding or broader transfer. Users are not required to continue.
- The upstream REASON-021/023 experiments remain separate research with synthetic recipients and unmerged branches. This draft does not confer their claimed permissions or silently integrate data.

## Reproduce

```sh
node experiments/reciprocal-001/test_reciprocal.cjs
```

For an offline browser experience, download `demo.html` and `reciprocal.js` to the same directory and open `demo.html`, or download the one-file `reciprocal-apprentice-offline.html` generated in the successful CI artifact.

## Next falsifiers (not yet run)

1. **Independent humans with consent:** Randomize equal-difficulty problem families, measure unaided transfer after delay, record refusals and ambiguous responses. Do not optimize for engagement or usage minutes.
2. **Fair machine comparison:** Compare against equal-information classical active learners, version-space elimination, Bayesian inquiry and optional computationally constrained models. Report whole-system resource cost and number of *distinct new capabilities*, not flattering search-step savings.
3. **Rich concepts:** Replace tiny Boolean truth tables with typed temporal, spatial, social or probabilistic transformation operators supplied by independent source owners. Source consent for real data must be explicit; support withdrawal and review.
4. **Human agency:** Measure whether users can recognize bad questions, correct erroneous suggestions, work independently *without MOTIF*, and teach MOTIF a method it does not already contain.
5. **Architectural adaptation:** Test whether reviewed findings can guide the MOTIF Reasoning Governor or GRAFT cartridges without converting evidence into authority.

**Research goal:** The human and machine may each learn a transferable *method*; if the human later needs the machine less, that is a positive possible outcome, not a retention failure.
