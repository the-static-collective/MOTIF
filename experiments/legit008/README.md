# MOTIF LEGIT-008 — THE PROOF-CARRYING METAREASONER

**Research status:** DRAFT / RESEARCH HOLD, not \`main\`, not production.
**Question:** Can MOTIF construct a better *way to reason* than one fixed
classical procedure, without compromising classical proof correctness?

**Answer in this narrow experiment: YES, relative to two specific fixed
classical policies under a declared cost model. NO, not beyond mathematics
or the strongest adaptive classical method.** The new policy matches exact
two-step classical decision quality with fewer counted reasoning states.

## Why this is a serious new vertical

A mathematical theorem remains true regardless of which procedure finds it.
There is no coherent notion of "beating mathematics" as a standard of truth.
There **is** a concrete, testable problem of outperforming a fixed
mathematical strategy on new workloads: choose the right abstraction,
search depth or algorithm using observable properties, while emitting
a checkable proof/decision certificate.

Established research to build upon:
- CEGIS counterexample-guided program synthesis:
  https://people.csail.mit.edu/asolar/SynthesisCourse2020/Lecture10.htm
- SyGuS syntax-guided program synthesis:
  https://www.microsoft.com/en-us/research/publication/syntax-guided-synthesis-2/
- E-graphs and equality saturation as ways of searching many equivalent
  representations rather than committing prematurely:
  https://doi.org/10.1145/3815481

**This particular experiment does not implement CEGIS or equality
saturation.** It implements a much smaller strategy search and documents
the exact baseline. Counterexample-driven *invention of new operators* is
the proposed next gate, not an achieved feature.

## Mechanism A — source custody with explicit trust limitations

\`custody.py\` adds commitments over original source claims, their
declared origin, calibration evidence and hypothetical audit specifications.
A synthetic evaluator holds the expected hashes in a **separate pinned
manifest**. The new procedure refuses forged additional roots,
changes to pinned claims, modified source calibration and altered
hypothetical sensor accuracy. It also rechecks all multi-hop copy
structures using LEGIT-007.

**Crucial distinction:** these hashes prove correspondence to the
*locally supplied manifest*, not who wrote a report, whether the
statement is true, or whether an external signature authenticated
anything. An adversary controlling **both the evidence and the pins**
can still re-seal a fake packet. This precise attack is in the tests.

No live key store, trusted certificate, authenticated identity or
real-world custody is claimed. The manifest is from a synthetic
evaluator, not an authenticated independent institution.

## Mechanism B — invent better procedures from a bounded recipe grammar

\`planner.py\` implements an **exact two-stage adaptive Bellman backup**:
at each stage it may stop, abstain, or propose a hypothetical audit.
Depending on the first answer, it may make a DIFFERENT second-stage
decision. Repeated audits and unbounded search are forbidden.

\`strong_reference.py\` independently enumerates all allowed contingent
two-stage policies, using LEGIT-007's *separately implemented* source
posterior reference. The candidate must tie the strong exact classical
reference to numerical precision. If not, the benchmark fails.

\`synthesis.py\` takes **160 public-only source cases** and searches a
fixed candidate grammar of **15** higher-level strategies:

- Always run one-step exact reasoning.
- Always run two-step exact reasoning.
- Use deeper reasoning only when the source-calibrated posterior is
  sufficiently close to 0.5 (several thresholds).
- Use deeper reasoning only when the declared proportion of copied
  reports exceeds a threshold.

This is **bounded strategy synthesis using already known procedures**.
It does not invent a new theorem, logical primitive, Bayesian update
law, or unrestricted executable code.

The trainer sees no true world states, no future audit results, and
no held-out labels. It optimizes an explicitly chosen training objective:

> expected decision loss + (0.0006 × number of recursive search states)

The compute price is a **synthetic research preference**. A counted
recursive state is not wall time, CPU energy or a general unit of
computation. Changing the price can change the winning strategy.

## Genuine held-out test (completed GitHub Actions)

**Training**: frozen synthetic trials 0–159, public inputs only.
**Held-out test**: frozen trials 160–319, with hidden world and
hypothetical audit outcomes visible only to the evaluator.

The selected trained strategy was:

> \`POSTERIOR_MARGIN(0.35)\`

It chooses depth 2 if the initial conditional P(TRUE) lies within
0.35 of 0.5, otherwise depth 1. It selected depth 2 on **105/160**
held-out cases and depth 1 on the other **55/160**.

| Procedure, same 160 test cases | Mean realized decision loss | Mean conditional expected decision risk | Mean counted search states | Declared decision+compute objective |
| --- | ---: | ---: | ---: | ---: |
| Fixed exact **one-step** classical audit | 0.1819375 | 0.16948921 | 5.00 | 0.17248921 |
| Fixed exact **two-step** classical audit | 0.16834375 | 0.16477979 | 13.00 | 0.17257979 |
| **MOTIF's synthesized metastrategy** | **0.16834375** | **0.16477979** | **10.25** | **0.17092979** |
| **Independent exact classical two-step** | **0.16834375** | **0.16477979** | [not instrumented] | [not instrumented] |

**Measured result:** the new selected *meta-procedure* matches the exact
two-step classical policy's realized decisions and conditional
expected risk on these held-out cases, with **21.15% fewer counted search
states** than the fixed two-step implementation. Under the specified
synthetic compute-price objective, it also beats the two **fixed**
baselines. Importantly, it does **not** beat the strongest exact
classical policy on inferential quality. An optimized classical adaptive
scheduler could reproduce the same savings or do better.

The prior one-step baseline is a strong mathematical procedure but is
not the exact optimum for a two-question horizon. Solving a larger
decision tree using Bellman recursion is not novel mathematics.

## What is kept separate

- \`custody.py\` — integrity relative to separately supplied synthetic
  pinned claims, NOT real source identity authentication.
- \`planner.py\` — exact adaptive two-stage planning, no execution.
- \`strong_reference.py\` — independent exhaustive classical optimizer.
- \`synthesis.py\` — explicit finite recipe generator and train-only selector.
- \`benchmark.py\` — hidden-world evaluation on 160 untrained synthetic
  cases, with real decision/abstention/test cost and measured search states.
- \`test_meta.py\` — proof-pin forgery, re-sealing attack, answer-leak
  rejection, benchmark parity, out-of-order provenance and no-action tests.
- Dedicated CI — archives the actual source/evaluation JSON receipt.
- The earlier MOTIF-013 existing witness likelihood remains wired and
  regression-tested via LEGIT-007.

## How to reproduce

\`\`\`bash
python -m unittest discover -s experiments/legit008 -p 'test_*.py' -v
python experiments/legit008/benchmark.py
\`\`\`

Python 3.11 standard library, no credentials, no external calls.

## What is NOT proven

1. No new mathematical principle or general algorithm was discovered.
2. No stronger correctness result than independent exact classical logic.
3. No externally blinded, third-party-generated evaluation.
4. No authenticated live chain of custody; evidence pins are simulated.
5. No real-world calibration of source reliability or audit accuracy.
6. No unrestricted instrument selection, algorithm synthesis or code
   execution. Every executable primitive was handwritten in advance.
7. No claim that the selected meta-strategy beats all classical schedulers.
8. No outcome is applied to any patient, legal proceeding, real source
   assessment, human participant or connected production service.

## Next legitimate gate: CEGIS-style algorithm invention

Give MOTIF a typed grammar of strategy **transformations**, e.g. exact
subproblem factoring, early dominance elimination, reuse of proof
certificates, alternative uncertainty representations, and controlled
composition. Generate candidate procedures on a **training-only**
corpus, request exact verifier counterexamples for candidate failures,
and revise the grammar or procedure using those counterexamples.
Evaluate only afterward on a separately authored, frozen test suite
with matched compute and strong tuned classical portfolio solvers.

Require a verification certificate and human review before any generated
algorithm is usable outside a research sandbox.

The objective is not to abandon mathematics. It is to make the **choice
and construction of mathematical methods** itself an object of reasoning.
