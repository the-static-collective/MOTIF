# MOTIF-024F — Native-Made Shortlist × Real T5 Reranking

## What we actually tried

Could the small FLAN-T5 language model contribute something after classical MOTIF has already developed, independently checked and shortlisted the candidate questions?

**Implementation:** A new 024F experiment that uses the real MOTIF-016 LivingForest planner and MOTIF-022F registered-question calibration, source and permission gates. The native planner evaluates each operator-supplied test against the same finite model, admits only tests that improve its decision, and produces a native-only baseline choice. **The model never invents a physical sensor or overrides that choice.** When there is no useful tie, the sidecar is bypassed.

For a genuine two-option tie, Google's **actual** FLAN-T5-small (~77 million parameters) gets unverified *synthetic* maintenance notes about both already approved instruments. It ranks one of the two by constrained next-token generation. We check a second pass with the **order of candidate display reversed**. Independent simulated post-review source drift then determines whether the chosen test yielded the correct answer.

This is explicitly **shadow evaluation**. No model-generated message is written into the native decision, real-world evidence, the PlanZ index, event arrangements, a grant application, any permission state, or any human-facing contact.

## Runtime provenance

Dedicated GitHub Actions run: https://github.com/the-static-collective/MOTIF/actions/runs/42050898527

- Successfully ran the deterministic tests, downloaded a public checkpoint, and ran **real** model inference on GitHub-hosted CPU.
- Checkpoint pinned: **google/flan-t5-small revision 0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab**, downloaded only into the ephemeral runner.
- Model inference runs with HF_HUB_OFFLINE=1, TRANSFORMERS_OFFLINE=1 and local_files_only=True.
- Python 3.11, PyTorch 2.6.0+cpu, Transformers 4.57.1, SentencePiece 0.2.1. No paid inference or API keys.
- One checkpoint load took **1.6077 seconds**. Total model generation time for **40 selection calls** was **10.5819 seconds** on the runner. Neither number is a benchmark of the user's older Mac.
- Machine receipt is uploaded as a GitHub Actions artifact. Model weights are not stored in Git history.

## Frozen experiment and genuine comparison

There are 20 deliberately invented test cases. Each offers **PROBE_ALPHA and PROBE_BETA**, two distinct-source synthetic food readiness probes with the same cost, the same calibration evidence, and the same modeled information gain. Both are independently calibrated using the original MOTIF-022F rules. Each can increase the native four-world model's expected state-classification accuracy from 0.50 to **1.00** if the simulated source remains reliable.

The model gets only two short fictional maintenance descriptions; the hidden future truth and which source later drifts remain separated inside an independent RUN evaluator. All scoring is synthetic. The 20 cases include **12 conventional simulated drift narratives, 4 adversarially misleading narratives and 4 no-drift controls**. Eight drifted sources are alpha and eight are beta. Candidate order is reversed for a second model run in each case.

**Observed results, 20 cases:**

| Strategy | Correct simulated final classifications | Accuracy |
| --- | ---: | ---: |
| Native MOTIF alone: deterministic tie-break PROBE_ALPHA | **12 / 20** | **60%** |
| **Actual T5 shadow ranking** | **12 / 20** | **60%** |
| Actual T5 with candidate display order reversed | **12 / 20** | **60%** |
| Seeded random registered source | 10 / 20 | 50% |
| Hand-written classical lexical risk heuristic, with the same notes | **20 / 20** | **100%** |
| Hindsight source-truth oracle — scoring ceiling, never a deployable policy | 20 / 20 | 100% |

**Unambiguous negative finding:** The real small T5 selected **PROBE_BETA in all 20 original cases** and all 20 order-reversed cases. It gave *zero* incremental classification gain over the native baseline, despite consuming extra CPU. It did not meaningfully use the maintenance-note distinctions in this test. The stable behavior under display reversal is not evidence of semantic reliability; it is consistent with a source-ID / decoder preference. A fixed always-beta rule would tie its outcomes. **No language-model advantage is established.**

The hand-written lexical comparator recognizes phrases like intermittent interference, mismatch, resets, missing verification and stable recent checks. It correctly sorts all fabricated cases, but the comparator vocabulary and benchmark notes were designed together. **Its 100% is not out-of-distribution validation**, and does not establish general natural-language inference either. Both it and T5 received the same notes, whereas the native finite planner did not model these extra unverified cues. All participants saw the same two valid native candidates.

### What is actually learned

1. **Native filtering works independently of the language model.** Both candidates satisfy their original synthetic source and planner checks; no model output changes the permission boundary.
2. **The typed decoder works.** The model can produce one of two whitelisted operator identifiers using real CPU inference; it cannot hallucinate an unregistered action through this interface.
3. **A choice being syntactically valid does not make it intelligent.** Always selecting beta was no better than the native deterministic alpha tie-break on a balanced synthetic drift set.
4. **Candidate display order was not the cause in these tests.** Reversing the textual order did not change the selected ID. The result may still stem from model priors or tokenization, so one should test equal-length anonymous labels on a *fresh*, independently frozen corpus rather than tuning on these same outcomes.
5. **Independent outcome receipts matter.** When a formerly calibrated source drifts after review, the native classification can be confidently wrong despite every source admission test having passed. A textual critic does not authenticate the physical world.
6. **Cost of deliberation is real.** This study measures inference latency but has NO real verified consequence model for time spent waiting; spending ~10.6 seconds to produce 40 tokenized choices did not buy additional modeled classification accuracy. It would be inappropriate to infer that a deadline has been preserved or lost without task-specific time and value evidence.

## Strong limitations and scientific hygiene

- This is a **hand-constructed, small, synthetic pairwise classification exercise**, not a human study or a real Fellowship field trial.
- Proposed sensor programs came from an operator-declared finite capability catalog, which native MOTIF independently screened. No open-world instrument invention or new physical action is demonstrated.
- The descriptions are artificial, partly adversarial and unverified. The lexical reference was built alongside the cases and is therefore not an untouched independently frozen comparator.
- The FLAN-T5 model was NOT fine-tuned or trained for the task. Small-model input interpretation and use of token aliases may limit performance; the precise mechanism behind its beta preference is unknown.
- Exactly modeled finite classical planning with the same information is still an appropriate strong comparator. A hybrid is worth deploying only if it beats native-plus-classical alternatives at matched information, effort, and risk.
- No client calls, outreach, payments, event announcements, permission grants, or grant applications have been made.

## Reproduce

- Deterministic: from experiments/024f run python -m unittest -v test_native.py (no weights needed).
- Genuine model: .github/workflows/motif024f-rerank.yml (public weight download, pinned revision, real local CPU inference, independent synthetic scoring, artifact receipt).

The frozen 20 cases are in heldout.py; native screening and independent synthetic evaluator in native.py; model choice and lexical comparator in rerank.py; actual benchmarks in benchmark.py.

**The next honest question:** If a 77M model cannot use tiny source-risk notes more effectively than a fixed choice, should MOTIF's next text-sidecar job be *explaining and flagging uncertainty* instead of reranking? Test that on independently prepared new cases with explicit human-legibility and error-detection controls, without assuming language fluency equals reasoning.
