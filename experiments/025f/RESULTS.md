# MOTIF-025F — RESULT: Don't hire T5 as a decision-maker; test its encoder as a semantic sensor

The user asked MOTIF to investigate the best use of the tiny T5 language model, including **none**. The original plan and test policy were precommitted in PRECOMMIT.md. This report records two **actual CPU model-weight experiments**, not a scripted stand-in.

## Independent model execution

Successful combined real CPU run: https://github.com/the-static-collective/MOTIF/actions/runs/42059181231

Public model: google/flan-t5-small, pinned source revision **0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab**, downloaded only into the ephemeral runner and subsequently used offline. Real CPU PyTorch inference, no provider credits or external agent actions. All examples artificial; no private human or grant content used.

### Experiment A — Can T5 earn a full job as Observer, Critic or Hypeman?

36 synthetic examples: 12 per role, with 72 actual model classifications to check reversed label order. All model choices were constrained to a finite known label grammar. Same-input native hand-written rules were frozen before the model ran.

| Candidate job | Native classical correct | Real T5 decoder correct | Real T5 improvement |
| --- | ---: | ---: | ---: |
| STATUS_TRIAGE / Observer (permission status) | 12/12 | **3/12** | -9 |
| MISSING_GATE / Critic (missing dependency) | 12/12 | **2/12** | -10 |
| NEXT_SAFE_STEP / Hypeman (minimal safe next step) | 12/12 | **3/12** | -9 |

**T5 gave a constant label across all twelve examples of each job:** REFUSED for permission status, STAFF for dependency, and CONFIRM for next step. Reversing the label display order changed **zero of 36** decisions. It made no fabricated GRANTED or unauthorized INVITE claims, but often ignored actual information and lost severely on classification. Real inference for 72 choices took **21.1447 seconds**. The native method had no incremental CPU model calls.

**MOTIF's actual job-selection verdict: NO_T5** for any of these three text-decoder/decision-making roles. That is not a claim that all T5 functionality is useless. Native rules and example vocabulary were deliberately authored together, which makes the 12/12 reference scores too easy; they are not independent linguistic generalization.

### Experiment B — Could the model's ENCODER do something its decoder cannot?

Rather than ask the small decoder to generate a label or choose a question, we reused the **real T5 encoder as a passive sentence feature extractor**, mean-pooling the encoder hidden states and doing nearest-neighbor retrieval over the 36 frozen labeled examples. No decoder output and no generated command. Separately froze **24 alternative-vocabulary synthetic paraphrases** (8 per job) *before* the encoder test, and compared against:
- unchanged native handwritten rules from experiment A;
- a classical word/bigram/character TF-IDF 1-nearest-neighbor retriever with the **same 36 reference examples**;
- classical TF-IDF weighted 3-nearest-neighbor;
- actual FLAN-T5 encoder 1-nearest-neighbor;
- actual FLAN-T5 encoder weighted 3-nearest-neighbor.

**Observed raw results, 24 fabricated paraphrases:**

| Method | Correct | False grants/publicity advice |
| --- | ---: | ---: |
| Unchanged native hand-written rules | 5/24 | **0** |
| Classical TF-IDF 1-nearest-neighbor | 7/24 | 5 |
| Classical TF-IDF 3-nearest-neighbor | 6/24 | 5 |
| **Actual T5 encoder 1-nearest-neighbor** | **16/24** | **4** |
| **Actual T5 encoder 3-nearest-neighbor** | **16/24** | **4** |

Encoder time for all 60 source+query texts: **0.2995 seconds**, plus model load time, on the GitHub CPU. Classical TF-IDF computation for the same example set: **0.0042 seconds**. This is **not** a benchmark on the user's Mac, nor an energy estimate.

**The revealing task split:**

| Task | T5 encoder | Native hand rules | Classical TF-IDF 1NN |
| --- | ---: | ---: | ---: |
| STATUS_TRIAGE / Observer | 3/8 | 2/8 | 0/8 |
| **MISSING_GATE / Critic** | **7/8** | 1/8 | 3/8 |
| NEXT_SAFE_STEP / Hypeman | 6/8 | 2/8 | 4/8 |

**MOTIF's candidate best use is NOT a general autonomous Critic or Hypeman. It is a PASSIVE SEMANTIC MISSING-DEPENDENCY SENSOR**: use the real T5 encoder to find resemblance between an unfamiliar ordinary-language note and a human-reviewed catalog of missing practical assumptions. Then create a reviewable *question* for MOTIF's native verified question machinery to consider. It cannot assert that a blocker exists or automatically change a planning fact, permission, external action or announcement.

**Why avoid the other two roles?** The encoder made **four false permission/publicity classifications** across the 24 queries. Its apparent 16/24 overall accuracy must not obscure these high-consequence false positives. Gate identification is lower authority when phrased as a *candidate question that must be independently checked*, though a wrong gate suggestion still wastes time and requires oversight.

### Validity cautions — very important

1. The corpus, task definitions, labels and original native rules were all authored within this research. The secondary paraphrases use alternative vocabulary, but are **not independently collected natural human messages**. This 7/8 versus 3/8 result is **promising synthetic evidence**, not a validated transfer advantage or production readiness.
2. Encoder method is a nearest-neighbor *text similarity* classifier. It can return plausible but false labels. A similarity score is **not a probability or authenticated evidence**.
3. T5 was not fine-tuned. The fact that encoder features may be useful while constrained text generation collapses is an important empirical distinction, not a new intelligence claim.
4. No future welfare, opportunity cost, permission from the space owner or grant eligibility is inferred. Model results were never offered as instructions to contact any person.
5. Stronger embedding baselines, human-written source diversity, paraphrase shift, privacy review and independent holdout scoring are needed before even a narrowly deployed silent sensor is justified.

## MOTIF's revised division of labor

- **Native MOTIF** generates plan structure, admissible questions, evidence gates, source custody, executable human-reviewed actions, and expiry/inaction calculations.
- **T5 decoder** is NOT hired for source status, autonomous criticism, deciding what to do, or test reranking: it failed the direct job interview.
- **T5 encoder** earns a provisional research role as a **low-authority silent semantic hint generator for missing-dependency questions**. Its output is only a review offer. Native 022F source/permission gates and actual human confirmation still govern whether a question may be acted upon.
- **NO_T5** remains the default for decisions, latency-sensitive action, and any task lacking a verified semantic improvement.

The actual engine chose **NO_T5** under the precommitted direct role rubric. The **encoder** is a *separately introduced, experimentally promising* role for prospective work; it has NOT passed the original hiring criterion and is not automatically deployed. The correct conclusion is **"no proven use yet; the best current lead is low-authority semantic missing-gate detection."**

All source files and raw JSON receipts are inspectable under experiments/025f and the GitHub Actions artifact; no weights are distributed.
