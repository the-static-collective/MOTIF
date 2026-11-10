# LEGIT-029 — THE SHIFT-AWARE RESEARCH GATE
## Can MOTIF distrust a research rule **before** it makes a wrong decision?

**Status: RESEARCH HOLD. Stacked DRAFT. Main unchanged.**

LEGIT-028 compared eight theories of mathematical information value.
A crossvalidated domain router selected different scoring rules for
graphs, algebra and Boolean constraint problems but required **382**
questions across 80 fresh engineered cases versus **375** for
conventional classical residual greedy. The winner in training is
not necessarily the winner in a new research environment.

This experiment asks whether MOTIF can detect the **risk of method
transfer** before seeing the answers to new research questions.

## Shoulders of giants — what is actually borrowed

- **Worst-group / distributionally robust evaluation:** measure
  performance in every known training environment, not just an
  average. Related to Sagawa et al., ICLR 2020,
  https://openreview.net/references/pdf?id=ED0XTrKrfp
- **Selective prediction and risk-aware refusal:** decline a risky
  learned method and defer to an established alternative. Inspired
  by Angelopoulos et al., ICLR 2024,
  https://proceedings.iclr.cc/paper_files/paper/2024/hash/f3549ef9b5ff520a7e41ff3cc306ab2b-Abstract-Conference.html
- **Distribution shift breaks calibration assumptions:** Barber et
  al., Annals of Statistics 2023,
  https://doi.org/10.1214/23-AOS2276

**Critical caveat:** This code does **not** implement conformal risk
control, a formal group-DRO optimization theorem, a confidence
distribution, a valid OOD p-value or a distribution-free risk bound.
The techniques are transparent *finite empirical heuristics*, not
those papers' formal guarantees. Training folds have dependent task
generators and the authored shift regimes are nonexchangeable.

## Actual research rules

1. **Plain training-world CV** — the LEGIT-028 average-question rule:
   choose the best information policy when its average across
   training-heldout worlds beats classical greedy by more than 0.025
   questions/case, otherwise use classical greedy.
2. **Worst-world empirical regret gate** — a novel method may be
   adopted only when it improves macro-regret by at least 0.1
   questions/case *and* has no worse query efficiency in any
   held-out training world compared with the identically trained
   classical residual greedy method.
3. **Metadata shift gate** — the above robust decision may be
   overridden by an input-novelty detector that looks only at
   the provided task's observable input-shape metadata, without
   executing a candidate question. Novel inputs route back to
   classical greedy.
4. **Mean-CV plus metadata shift gate** — a second, less
   conservative ablation demonstrating whether the shift detector
   can avert errors even when a mean-CV selection was optimistic.
5. **Strong classical-only** — conservative fallback baseline.

Additional matched complete candidate-question controls:
classical residual greedy, raw diversity, joint Shannon entropy,
and the LEGIT-028 conditional information-value heuristic proxy.

All full methods have the same 21 graph, 35 polynomial, or 36
integer-constraint candidate questions and can only produce
**independently verified exact counterexample witnesses**.

A query is counted whenever a method actually asks its exact
mathematical question, including when the answer is negative.
Input metadata are considered free within this benchmark and do
not consult unasked question values. This is a specific task
interface, not an estimate of real-world evidence-collection cost.
In fact, coefficient inequality provides a direct zero-query proof
of polynomial nonidentity under a less restricted proof goal, so
this benchmark tests *query-selection efficiency*, not whether
querying is the globally optimal way to solve these problems.

## Training and genuinely future episodes

Training-only inputs:
- Four previously recognized LEGIT-028 graph training environments,
  plus two **new** eight-node graph environments with fixed
  seeds 29001/29002. Each graph sampler draws 3,000 labeled graphs.
- Two original LEGIT-027 algebra/constraint training worlds, plus two
  additional moderate-shift polynomial/constraint worlds with
  seeds 29011/29012.

Each information policy gets the identical training source
question grammar. A leave-one-TRAINING-world-out experiment fits the
same policy on the other training worlds, then records exact per-case
question costs on the omitted training world. We log its **macro
regret and worst-environment regret** relative to conventional
greedy. Selection is strictly training-only. We freeze a digest of
all method plans and the input-novelty threshold before requesting
new worlds.

**Protocol revision recorded:** the initial CI attempt with 1,000 graph\nsamples per future seed could not assemble eight qualifying graph pairs\nfor one future seed and stopped **before evaluating any new question\npolicies**. The sampler was increased to 3,000 draws and the future\nseeds were changed to 29005/29006 before outcome evaluation. This\nrevision is transparent; it means the original proposed experiment was\nnot strictly preregistered unchanged.\n\nFuture-only inputs:
- Two new independently seeded graph sets 29005/29006, eight
  old-probe-blind source pairs each.
- Two graph complement sets using those same sampled graph targets:
  **dependent transformations**, NOT independently sourced results.
- For each of the two non-graph domains, fresh mixed-regime seeds
  29013/29014, plus deliberately far-shifted regimes
  29015/29016 (16 cases each).

All challenge generators are **engineer-authored**, conditioned on
old candidate-grammar failures and (for math) the existence of a
witness. The far-shifted problems are not drawn from an external
blinded researcher; success here cannot prove deployment safety.

## Pure input-novelty detector

The router can inspect **only four typed descriptors already
present in the task**:
- Graphs: order, mean edge density and degree summaries.
- Polynomials: coefficient-difference magnitudes and shape.
- Integer constraints: coefficient/bound magnitudes and sparsity.

On training tasks only, fit per-feature scales, compute nearest
neighbor distance to *other training worlds* and freeze a 90th
empirical percentile plus a fixed buffer 0.05. At execution,
a new task with above-threshold novelty is routed to classical
greedy **before asking any mathematical source question**. Both
the score and the decision are recorded.

This is not conformal calibration and does not assign a statistical
risk level to a specific query. The threshold can be wrong under
out-of-distribution samples, adversarial construction, covariate
shift invisible to the descriptors, or label-relevant drift.

## Verifiability and falsification

Adversarial tests cover:
- Strict no-future-world access until SHA-256 freeze.
- No test-world math answers from the input novelty computation.
- Explicit rejection of a fabricated exact oracle response.
- Matched complete query vocabularies and independent reference
  checks on **every** actually asked question, including negatives.
- Refusal of unregistered seeds or domain-generating regimes.
- Exact crossworld regret receipts and conservative rejection rules.
- Graph complement provenance: dependent, not fresh source samples.
- Post-evaluation hindsight may ask another research question but
  cannot be fed back into the same held-out results.

All failed candidate policies, withheld new worlds and exact
per-question evidence remain archived for review.

## Interpretation

A method does not become safe merely because an average CV metric
improves. A robust empirical guard can abstain and fall back to
classical planning, but **the fallback itself must be evaluated**.
Strong classical baselines remain visible. Neither empirical
regret nor novelty detection is a formal probability guarantee.

A positive result would establish bounded, independently verified,
training-frozen method-selection performance on **engineer-generated**
counterexample tasks with deliberate shifts. A negative result
would show which guard has failed, not invalidate scientific
skepticism or permit retroactive promotion.

This work does not establish autonomous novel mathematical theory,
general reasoning dominance, or recursively self-improving systems.

## Reproduction

```sh
python -m pip install --only-binary=:all: networkx==3.4.2
python -m unittest discover -s experiments/legit029 -p 'test_*.py' -v
python experiments/legit029/meta_guard.py --emit > /tmp/motif-legit029-evidence.json
```

The experiment's GitHub Actions artifact retains the full raw
JSON including every training-world CV receipt, risk selection,
per-world shift score, each future exact observation, and
retrospective diagnosis (explicitly marked posthoc).

`RESEARCH_HOLD_NO_STATISTICALLY_VALID_SHIFT_GUARANTEE`
