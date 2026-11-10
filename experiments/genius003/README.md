# MOTIF-GENIUS-003 — THE CORRECTABLE PERSPECTIVE / HIDDEN PROFILE TRIAL

**Status: RESEARCH HOLD.** Stacked exploratory branch on GENIUS-002, not merged. Pure Python standard library. No actual Trench devices, humans, MCP accounts, networks, live consent, autonomous messaging, or real-world decision execution.

**Research question:** Can a collection retain distinct, explicitly shared perspectives, make falsifiable predictions about *what each participant voluntarily reports*, correct those predictions on subsequent reports, and pool genuinely distinct information without treating disagreement as an error?

## Shoulders of giants (inspirations, not validations)

1. **Stasser & Titus (1985)**, *Pooling of Unshared Information in Group Decision Making*, JPSP 48(6), 1467–1478. DOI https://doi.org/10.1037/0022-3514.48.6.1467. Groups can fail to surface members' unique information even when pooling it would improve their choice.
2. **Brier (1950)**, *Verification of Forecasts Expressed in Terms of Probability*, Monthly Weather Review 78(1), 1–3. DOI https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2. Use squared-probability-error scoring to compare prospective forecasts, not retrospective explanations.
3. **Classical Bayesian frequency estimation and partial pooling**: pre-existing Beta–Bernoulli smoothing and shrinkage. The experiment uses these standard estimators, not a novel learning algorithm.

These studies do **not** validate inferences about anyone's motives, morality, welfare, or real-world needs. Historical genius names are research prompts, not simulations of particular individuals.

## Experiment A — correctable perspective prediction

The module perspective_learning.py imposes a strict observer boundary:

- Only voluntarily shared reports enter training. Withheld reports, simulator-private notes and future outcomes never enter estimators or training hashes.
- A report records a participant's public binary choice about a named topic, with a distinct case ID and evidence pointer. It is **a self-report, not proof of what was best**.
- Predictions are probabilistic and falsifiable. After the target voluntarily shares a future response, record the predicted probability and Brier loss **before** updating from that response.
- Unknown participant or topic → HOLD. No inferred personality or hidden intention.
- A potentially useful next question may be suggested only for an explicitly opted-in target. It is not sent.
- Duplicate case IDs from a source cannot be counted twice.

### Strong and weak classical comparators

All estimators get exactly the same reports:

| Arm | Estimator |
| --- | --- |
| GLOBAL | Beta-smoothed single yes-rate |
| TOPIC | Group yes-rate by topic |
| TARGET | Participant yes-rate across topics |
| TARGET_TOPIC | Participant-by-topic yes-rate |
| SHRINK | Participant-topic observations + a global-topic prior |

The experimental method **belongs to the same classical family as its strongest baseline**. The training-only selector picks the lowest Brier score on a distinct validation sample with small predeclared complexity penalties. The selected arm, training case IDs and outcomes are SHA-256 frozen *before* the future reports are generated.

### Synthetic prospective trials

Four topics: speed, safety, privacy, fairness. Fourteen synthetic participants have independently generated heterogeneous response probabilities. The simulator-only latent probabilities are never passed to the predictor. Each target/topic has 16 training + 8 validation observations; future challenge observations come from separate seeds.

- **STABLE**: 12 new samples per participant/topic, plus withheld items and one unknown visitor.
- **REVERSED PREFERENCES**: previously observed targets' response probabilities are intentionally inverted.
- **ONLINE CORRECTION**: score each prediction before incorporating its new voluntarily shared label; compare with each frozen comparator on the same future records.

Metrics: Brier error, 0.5-threshold accuracy, coverage, withheld exclusions, unknown-target abstentions, immutable freeze digest and per-report correction receipts. All output cases are **synthetic**, not real user data.

**Limits:** All benchmarks and their answer-generating processes are engineer-authored and not externally blind. This is an in-generator experiment; any measured gain is not evidence of human social intelligence or autonomous discovery. Under shift, a once-good personalized model may become significantly worse.

## Experiment B — hidden-profile evidence pooling

The module hidden_profile.py implements a modern illustrative signed-evidence toy inspired by information-pooling research.

Three synthetic nodes each have the same +3 pro-A fact. Node B also reveals a distinct -2 fact and node C a distinct -5 fact. A majority of local model preferences favors A; deduplicating repeated evidence IDs and adding unique shareable evidence gives -4 and instead conditionally favors B.

- Identical evidence IDs across sources count once. This is a very limited deduplication rule.
- Conflicting declared weights under one ID → HOLD; do not average the conflict away.
- Private facts are not read, published or silently used in the collective judgment.
- Evidence refs are **UNVERIFIED pointers**. Conditional arithmetic is not proof of external truth.
- A strong standard centralized deduplication-and-sum baseline gives the *same* answer. No novelty or advantage over this classical comparator.

## Reproduce

Run from repository root:

~~~sh
python -m unittest discover -s experiments/genius003 -p 'test_*.py' -v
python experiments/genius003/perspective_learning.py --emit > /tmp/motif-genius003-perspectives.json
python experiments/genius003/hidden_profile.py > /tmp/motif-genius003-pooling.json
python -m json.tool /tmp/motif-genius003-perspectives.json >/dev/null
~~~

Eleven tests cover withheld-data non-use, unknown-target HOLD, opt-in, frozen training digest, deliberate shift, correction, duplicate protections, hidden-profile majority reversal, conflicting weights, echo deduplication and source ownership. CI retains both synthetic JSON artifacts for inspection.

## What would genuinely move the frontier?

1. Externally authored, frozen cooperative cases with independently scored success criteria; meaningful consent before studying real participants.
2. Blind transfer beyond categorically described binary preferences, against hierarchical Bayesian baselines, calibration and strong active-learning controls.
3. Question-value learning: reduce uncertainty per unit of participant burden rather than maximizing entropy.
4. Drift detectors: detect when assumptions stop working, admit uncertainty, and let a participant correct the record without pressure.
5. Authenticated Trench/MCP membrane: signed node identity, publication/withdrawal, replay and sybil defense, separate privacy and authority scopes.
6. Novel externally verified joint solutions beyond what matched strong individual/classical algorithms could solve at identical budgets.

**Invariant:** a collective may gain information from an independent perspective without treating its owner as an object to manipulate, override or pressure.
