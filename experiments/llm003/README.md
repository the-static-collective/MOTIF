# LLM-003 — Real Open-Weights Crossing × The Error Dividend

**Research status: DRAFT / HOLD.** Stacked on LLM-002 PR #314 and LLM-001 PR #311; neither has been merged. This research is not JAR;VIS production integration.

Two questions were intentionally separated: (A) can a real pretrained language model reuse identical KV prefix states when a graph-conditioned latent change occurs exclusively after that prefix? (B) when does a *wrong provisional hypothesis* become useful as a way of learning from an independently verified counterexample? Getting an incorrect answer in front of a user is never itself considered success.

## Source evidence: Real model executed

Source: [LLM-003 actual model CI, initial](https://github.com/the-static-collective/MOTIF/actions/runs/43245827351) and [64-case replication](https://github.com/the-static-collective/MOTIF/actions/runs/43246416371). This is a real 134,515,008-parameter pretrained HuggingFaceTB/SmolLM2-135M-Instruct in float32 on CPU; not synthetic random weights. Model revision: ee72e5415c002e8fc0566a191a07c0b2b708875a. Dependency install and weights download were ephemeral in GitHub Actions, not committed.

- Four graph suffix forks shared one **67-token** prefix. Every cached fork was compared against full independent recomputation with the *same* frozen model, positions, attention mask, suffix hidden injection, and source inputs.
- Largest absolute final-vocabulary logit delta across the four branches: **0.00003529**, below the preregistered 0.001 acceptance tolerance.
- Four independent full forwards: 0.56147 seconds total on one run; one shared prefill plus four suffix continuations: 0.32673 seconds. About 41.8% lower measured Python-forward wall time **on this single short CPU trial**. No robust throughput, end-to-end serving, warm benchmark, or energy improvement is established.
- Graph latent adapter in this test is a **fixed untrained rank-two projection**. Its output is a numerical intervention, not evidence of improved task accuracy. Nothing about cache parity validates the correctness of the graph information.

## Error Dividend: same information, equal probe budgets

Original frozen plan: [PREREGISTRATION](PREREGISTRATION.md). Code: [error_dividend.py](error_dividend.py). CI: [independent simulated owner experiment](https://github.com/the-static-collective/MOTIF/actions/runs/43245687678). Source owner truth is hidden from the test policies and only reported on requested probes. Eight author-defined Boolean hypothesis families; eight input combinations; 160 independently seeded held-out author-simulator worlds. Classical information gain uses the same prior, owner feedback and budgets.

| Author-simulator regime | Policy | 0-probe baseline accuracy | 1-probe accuracy | 3-probe accuracy |
| --- | --- | ---: | ---: | ---: |
| Truthful independent feedback | Falsify / challenge favorite | 68.67% | 81.02% | 100% |
| Truthful independent feedback | Classical information gain | 68.67% | 80.86% | 100% |
| Truthful independent feedback | Random probe | 68.67% | 76.56% | 95.63% |
| Truthful independent feedback | Confirmation seeking | 68.67% | 70.16% | 84.69% |
| 20% false owner feedback | Falsify / challenge favorite | 68.67% | 76.33% | 87.03% |
| 20% false owner feedback | Classical information gain | 68.67% | 76.25% | 85.70% |
| Echoed existing source (not independent) | Any probe policy | 68.67% | 68.67% | 68.67% |
| No feedback | Any probe policy | 68.67% | 68.67% | 68.67% |

On truthful 3-probe runs, challenging the favorite generated 182 independently identified wrong provisional predictions; **98 of those individual false predictions were followed by an accuracy improvement exceeding the preregistered 0.04 accuracy-equivalent probe cost**. Other wrong predictions yielded zero or negative decision benefit. In noisy environments, wrong receipts can actively degrade the later answer. When no independent feedback exists or reports merely echo one origin, an attempted probe costs resources without improving knowledge.

### Does disconfirmation beat classical information gain?

Post-hoc paired seeded bootstrap (not preregistered): one-probe truthful advantage of challenging over classical IG was +0.001563 with 95% percentile interval **[-0.007031, +0.010156]**. At three truthful probes they tied exactly. At three probes with 20% report noise, the point advantage was +0.013281 with interval **[-0.007031, +0.032813]**. These intervals include zero; no established superiority. The test suite is authored and relatively small, with a fixed and known hypothesis family.

## Actual pretrained model: do verified counterexamples help?

Follow-up after reviewing the initial eight synthetic-model probes, explicitly exploratory rather than preregistered: 64 distinct-author-seed synthetic source puzzles. The real pretrained SmolLM2 was asked a binary target question, then given one separately verified, off-target example under either challenge-based or random selection. Same single-verification budget.

| Arm | Correct / 64 | Corrections from wrong to right | Regressions from right to wrong |
| --- | ---: | ---: | ---: |
| No additional observation | 40 | — | — |
| Verified challenge observation | **41** | 8 | 7 |
| Verified random observation | **40** | 7 | 7 |

Paired challenge-minus-random accuracy: +0.015625 (one case), exploratory paired percentile interval **[-0.09375, +0.10938]**. Far too uncertain to claim real-model advantage; importantly, revisions also made previously correct answers wrong. This is consistent with prior warnings about intrinsic correction and the importance of reliable external feedback.

## What this actually tells us

A wrong **hypothesis** can be valuable when it creates a *test that changes the posterior or action policy*. It is not valuable if untested, if the criticism merely echoes the same source, if verification is misleading, or if correction causes more regressions than recoveries. This is **not** an argument for producing knowingly wrong answers to people. A better engineering objective is *verified learning value per cost of falsification*, not 'maximize mistakes'.

## Second-stage post-hoc training

Before running it, we separately froze [PREREGISTRATION-TRAINING-ADDENDUM](PREREGISTRATION-TRAINING-ADDENDUM.md). It compares frozen pretrained weights + trained low-rank graph adapter under verified positive-and-negative examples, positive-only examples, and deliberately corrupted negative labels at identical update budgets. It also tests withheld synthetic prompt phrasings, feature shuffling and a 100%-accurate engineer-authored classical rule. The training attempt is not the same as the original numerical cache-equivalence test. Its results must be reported independently; no claim is made until its CI receipt has been inspected.

## Real pretrained learning tests: a shortcut found, then falsified

After the primary real KV experiment, two separately preregistered **post-hoc** follow-ups asked whether the graph actually *caused* the pretrained model's answers.

First ([LLM-003B](PREREGISTRATION-TRAINING-ADDENDUM.md)): with 48 held-out author-defined cases using 'probe/use/publish', the 48-update verified-labeled rank-2 adapter scored **44/48 (91.7%)** versus the unadapted pretrained model **28/48 (58.3%)**, positive-only training **20/48 (41.7%)**, and corrupted-negative training **31/48 (64.6%)**. HOWEVER, when the tool/permission graph bits were deliberately flipped, verified training STILL scored **44/48**. That positive-looking result was compatible with the model using action-word shortcuts, not the graph. Strong classical authored rule: 48/48.

The follow-up ([LLM-003C](PREREGISTRATION-GRAPH-CAUSALITY.md), [successful run](https://github.com/the-static-collective/MOTIF/actions/runs/43247789523)) removed that confound: **every prompt proposed exactly the same action word, 'use'**. Only the binary graph-provided tool and permission facts varied. The test owner labeled an action 1 only when both were present (AND). Training balanced true and false examples at 48 updates on the same frozen 135M-parameter model; four held-out phrasings × four source-graph cases = 16 tests.

| Graph-only author task | Correct / 16 | Accuracy |
| --- | ---: | ---: |
| Frozen pretrained model, no graph adapter | 12 | 75% |
| Trained rank-2 adapter, verified labels | **16** | **100%** |
| Same verified adapter, tool+permission graph bits flipped at inference | 8 | 50% |
| Same pretrained model, positive-only adapter training | 4 | 25% |
| Same model, 50%-corrupted negative reports during training | 4 | 25% |
| Exact engineer-authored classical AND rule | **16** | **100%** |

Unlike the first test, the graph-feature flip actually degraded predictions. This is **mechanistic evidence that the real pretrained model's suffix hidden-state response can be controlled by typed graph input** on this narrow toy task, not evidence of novel reasoning, generalization, or superiority to logic. Exact classical reasoning matched at 100%. The adverse corruption result supports investigating truthful negative feedback, but it is also consistent with ordinary supervised learning and is not proof of a new error-learning algorithm.

### Core synthesis / proposed decision rule

- Generate as many speculative alternatives as the available computation budget reasonably supports, but label them PENCIL.
- Prefer *discriminating tests* whose independent results would alter later action choices. An incorrect provisional candidate can have positive value **only if falsification changes the next decision**.
- Retain one immutable shared source prefix; branch-specific graph changes belong in suffix hidden states or require a new prefix KV computation.
- Return verified observations and their source lineage, never a language model's unverified claim. Unknown consent or physical fit stays HOLD.
- Score net verified progress per time, model tokens, oracle probes, and human correction cost; compare against strong exact logic/planning controls. Under absent or deceptive feedback, deliberate error-hunting can lose.

**No external-source, multi-model, or adversarial generalization result has yet been established.**

## Reproduce / read

- Dependency-free synthetic oracle: `python -m unittest discover -s experiments/llm003 -p test_error_dividend.py -v` and `python experiments/llm003/error_dividend.py`.
- Exploratory paired uncertainty: `python experiments/llm003/posthoc_ci.py`.
- Real pretrained model: `python experiments/llm003/real_pretrained.py` after explicit provision of the pinned public model and PyTorch/Transformers dependencies; uses only invented fixture inputs.
- Conditional real-model adapter study: `python experiments/llm003/train_pretrained_adapter.py`. Requires actual weights and far greater computation than the synthetic oracle.

Research background: [Kamoi et al. (2024)](https://arxiv.org/abs/2406.01297) on self-correction and external feedback; [Hamdan & Yuret (2025)](https://arxiv.org/abs/2503.14391) on negative examples; [Zhang (2026)](https://arxiv.org/abs/2609.35832) on correct-to-wrong regressions. None establishes MOTIF-specific novelty.
