# LLM-006 — Real pretrained SmolLM2 inside an 879+-step ODYSSEY marathon

**Status: DRAFT, experimental, not merged or deployed.** Stacked on LLM-005 PR #319 → LLM-004 PR #318 → preceding unmerged neural work. Source-only synthetic tasks; no private user data or live JAR;VIS actions.

## The result in one paragraph

An actual frozen pretrained **HuggingFaceTB/SmolLM2-135M-Instruct** model (pinned revision `ee72e5415c002e8fc0566a191a07c0b2b708875a`, CPU fp32) was plugged into **every uncalibrated decision gate** of a long, source-verified ODYSSEY marathon. The model's unsupported memory-only and calibration-only approaches **failed the first of four linked 96-decision worlds** because costly mistakes exhausted the fixed sub-world budget. A version that paid for **independent verification before risky commitments** completed all **384 fictional decisions across 48 sectors, 96 evidence audits, 12 relays and 3 mandatory inter-world handoffs**, executing **1,196 causally dependent simulation actions with 336 genuine neural forward passes**. It succeeded through **271 paid independent probes**, not because the model learned the hidden rules well. The strong classical Bayes+verification control beat it substantially on cost and action count. This is a meaningful verified integration and an explicit **negative result** for the small model's unsupported long-horizon reasoning ability, not evidence of AGI or algorithmic novelty.

## Preregistered protocol

See [PREREGISTRATION.md](PREREGISTRATION.md), frozen before implementation at commit `1d8ca7d029b950943822256fd450379212b43d58`. Only the initial registered ODYSSEY marathon group `[8001,8002,8003,8004]` was tested with real model weights. Its 4 serial subchains contain 12 changing source-owner contexts apiece; 8 ordered tasks each; strict mandatory surveys, independent owner receipt, repair+retry, half and terminal audits and three cross-group digest handoffs. Minimum successful chain is 879 serial simulation actions; actual lengths increase with mistakes and independent probes. The model may see only the initial sector calibration and earlier unique independently verified source reports from the SAME sector, never the hidden owner rule, a future label, repeated-root rumor, or an unsourced model prediction.

Three matched model arms use the same actual pretrained weights, no fine-tuning: `llm_flat` (initial calibration only), `llm_memory` (all current-sector verified historical examples), `llm_verification` (same verified history and optional paid independent precommit oracle probes when the model's own two-digit normalized confidence implies expected simulated mistake/repair cost greater than probe cost). The comparison includes LLM-005's already documented classical Bayes and cost-aware Bayes controls. All model outputs are PENCIL until independently confirmed by the authored owner. Correct answers with already held calibration never require a redundant neural forward, which is why a complete 384-decision chain needs 336 genuine forward passes.

## Actual results — heldout authored first group only

See [successful actual-weight GitHub Actions receipt](https://github.com/the-static-collective/MOTIF/actions/runs/43264021769). The earlier first attempt failed on a *test audit* that assumed no inference could occur just before budget exhaustion; this was corrected to count and explicitly disclose such unmatched proposals rather than conceal the partial run.

| Policy | Source-verified gates completed /384 | Actual model forwards | Total serial simulation actions | Wrong committed answers | Independent precommit probes | Synthetic cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **REAL SmolLM2 calibration only** | **88** (failed first subchain) | 78 | 273 | 36 | 0 | 399.25 |
| **REAL SmolLM2 with source memory** | **84** (failed first subchain) | 74 | 266 | 37 | 0 | 399.75 |
| **REAL SmolLM2 with memory + paid verification** | **384** (complete) | **336** | **1,196** | **23** | **271** | **1,354.00** |
| CLASSICAL_BAYES (previous LLM-005 matched group) | **384** (complete) | **0** | **969** | **45** | **0** | **966.00** |
| CLASSICAL_BAYES + paid verification (previous LLM-005 matched group) | **384** (complete) | **0** | **969** | **6** | **78** | **849.00** |

The model's raw, independently graded PENCIL proposals in the completed verification-assisted run were **178 correct and 158 incorrect (53.0% accuracy)** on the 336 never-before-labeled checkpoints. Of these, 271 were independently verified before attempting commitment; another 23 incorrect proposals reached commitment and then required repair. The resulting full system completed because the evidence and repair gates remained intact, not because the pretrained model was a reliable rule learner.

The model's unsupported `llm_flat` first subchain produced 41 correct and 36 incorrect gate-event proposals (77 fully recorded calls) before the 400-cost subchain budget ended; the final 78th forward was executed immediately before the budget stopped the commitment. That attempt remains counted as uncommitted, never reported as an accepted action. Memory-only yielded 37 correct and 37 incorrect proposals (74 calls), and failed sooner. The first 74 common model targets showed **11 predictions wrong under flat but right under memory, versus 13 right under flat but wrong under memory**. This does not demonstrate a model-memory advantage; memory's outcome was slightly worse on that shared subset.

### Why the classical comparator is important

The **cost-aware classical control** completed the *same* first registered fictional 384-decision chain in **969 serial actions at cost 849**, compared with the genuine LLM's **1,196 actions at cost 1,354**. Classical Bayes without preverification also finished in 969 actions, cost 966. The classical cost-aware policy had access to the same independently reported synthetic owner facts, action costs and optional precommit verification. Its 78 probes were far fewer than the pretrained model's 271. There is **no evidence here that the neural component improves the task**; the system's robust overall completion derives from independent source verification and repair guards.

## Engineering additions

- `../llm005/odyssey.py` now accepts an explicitly source-bound optional decision adapter. It prepares a **closed evidence packet** from actual `ReasonHypermap` source receipts, never owner hidden truth. Only the registered real model policies accept adapters; the original classical arms and all old 879-step tests remain intact.
- `../llm005/marathon.py` supports model-containing policy arms while preserving 4 segment checks, 384 correct gates, source-root lineage, 3 actual dependency handoffs, immutable global hash chain, cost limits and fail-closed incomplete status.
- `real_marathon.py` really loads the pinned pretrained model through LLM-003 `load()`, performs numeric logits inference for digits 0 and 1, refuses >220-token prompts, records prompt SHA256 and receipt roots, counts forwards, input tokens and elapsed compute; it does **not** substitute a random model on failure. The status is explicitly `PENCIL_ONLY_NOT_A_WITNESS` until an independent synthetic owner report exists.
- `test_binding.py` adds 19 special source-disclosure/callback checks using an explicitly labeled **FAKE TEST STUB**. The runtime refuses to label stub-only results as genuine pretrained weights. Actual model execution requires the separate real-weight CI receipt.
- `build_real_viewer.py` assembles the three actual model traces and two strong classical controls into an **offline, interactive 48-sector source-event replay**. Each step is selectable, and each genuine neural proposal's confidence, prompt hash, source history and verifying owner result are inspectable. No private sources or network calls.

## Reproduce

Python 3.11, CPU, ephemeral public Hugging Face checkpoint download; dependencies pinned in `.github/workflows/llm-006.yml`. No API keys required:

```bash
PYTHONPATH=experiments/llm003:experiments/llm004:experiments/llm005:experiments/llm006 \
  python -m unittest discover -s experiments/llm006 -p 'test_binding.py' -v

PYTHONPATH=experiments/llm003:experiments/llm004:experiments/llm005:experiments/llm006 \
  python experiments/llm006/real_marathon.py --out /tmp/llm006

PYTHONPATH=experiments/llm003:experiments/llm004:experiments/llm005:experiments/llm006 \
  python experiments/llm006/build_real_viewer.py --out /tmp/llm006
```

Artifacts: `real-model-summary.json` (small complete source summary); `real-model-traces.json` (all actual numerical model decisions embedded in full serial chain); `real-model-marathon.html` (offline interactive real pretrained control comparison); `real-model-viewer-study.json` (classical comparison metadata). GitHub Actions attaches them to the reproducible job. Every partial or failed chain stays explicitly incomplete.

## Interpretation and next falsifier

**Failure was informative.** The pretrained 135M model alone made too many incorrect guesses and could not survive one 96-decision subchain under the existing budget. Its memory of past independently verified facts did not measurably improve that. The cost-aware source gate was strong enough to carry a weak model through all 384 decisions, at a substantial additional query cost. The experiment supports robust system design with independent verification, but not claims of new mathematics, long-context cognitive superiority, or effective language-model learning from mistakes.

To genuinely test MOTIF's neural-graph/error-dividend hypothesis next, use independently authored, open-ended tasks with latent dependencies, unknown hypothesis families and no direct single-bit owner oracle. Compare real model with and without precisely typed graph-state intervention against equally cost-aware classical planning; measure downstream accuracy, truth recovery, and model/verification cost. This toy run's error-dividend events are source-verified classical posterior changes, **not proof of real-model self-improvement**.

**No production merge. No real-life source permissions granted. No private content or irreversible actions.**