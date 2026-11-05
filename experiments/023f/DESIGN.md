# MOTIF-023F — REAL TINY MODEL, REAL CRITIC, REAL NEGATIVE RESULTS

**Question:** Now that 022F can turn an untrusted critique into a reviewable test, does the actual 77-million-parameter Google FLAN-T5-small improve question nominations over a frozen operator-catalog baseline? Does token-level constrained decoding help a very small text-to-text model participate without inventing tools or evidence?

**Status:** The CPU GitHub Actions experiment has executed real model weights and real model generation. The normal local-only adapter is unchanged. The model is **not fine-tuned**, no training labels are supplied in prompts, and the inference worker cannot perform external actions. This stacked 023F branch builds on MOTIF-022F #39 and all its dependencies.

## Model and execution provenance

- Public model: **google/flan-t5-small**, Apache-2.0, approximately **77M parameters**. Model card: https://huggingface.co/google/flan-t5-small .
- Full CPU model checkpoint and tokenizer intentionally downloaded to the **ephemeral GitHub Actions** cache in a separate explicit setup step; verified model.safetensors exists.
- The original smoke run verified **actual** model logits and CPU generation, NOT scripted text. The reported Hugging Face snapshot revision for a benchmark run was **0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab** (observed, not a signed witness identity).
- Inference steps run with HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1, `local_files_only=True`, `use_safetensors=True`. No API keys, access to private user data, vendor-paid inference, GitHub write permission, or live JAR;VIS deployment.
- Python 3.11 / PyTorch 2.6.0+cpu / Transformers 4.57.1 / SentencePiece 0.2.1; deterministic CPU generation with two beams. Runs are small and on public GitHub-hosted CPU hardware.
- A runtime/model checkpoint SHA in an arbitrary log is not authenticity proof. Model revision may change unless a subsequent experiment pins it explicitly.

## The three real model conditions

**1. RAW_GENERATION.** Take 022F's actual lengthy `QuestionAwareBackend` critic instruction and ask the model to print `TEST_ID=NAME`. Check text exactly, never autocorrect hallucinated substrings.

**2. CONSTRAINED_IDS.** Present a shorter decision context and use **real model next-token logits** to select one of the operator-owned IDs **or** `NO_TEST`. Generate is limited with a tokenizer-aware next-token trie; arbitrary strings are impossible. The decoder does not get to invent a new sensor or modify PlanZ. For the bench this tiny model exhibited an always-abstain behavior.

**3. CONSTRAINED_ID_ONLY.** Same token-level technique and registered IDs, but no `NO_TEST` option: the model must nominate **one** currently registered test. This does NOT force the system to ask it: independent calibration, actual 016 Living Forest plan improvement checks, latency/inaction holds, duplicate-source checks and the human-authority boundary still may refuse. With an empty catalog the decoder itself refuses.

**Caution about comparison:** These three arms differ in the prompt, constrained decoding, and the availability of abstention, not just decoding alone. They establish performance of the complete evaluated pipelines, not an isolated causal estimate of any single technique.

For 16 benchmark cases, OBSERVER and HYPEMAN text is **scripted and openly labeled**, so only the real CRITIC is scored. A separate optional three-role harness exercises all three actual model roles against native 020F Fellowship planning with bounded grace and a safe join of a lingering CPU worker before interpreter teardown.

## Frozen 16-case experiment (synthetic, not real Fellowship outcomes)

Eight-style/16 variations of a four-state audio/meal toy task provide cases where: an extra meal test is beneficial; food is already resolved; an offered source is duplicate or uninformative; a test has independent falsifiers; a human-only question lacks authority; an inquiry carries an uncalibrated cost of waiting; or a reviewed source later drifts. These are **artificial worlds**, never field measurements.

The model sees operator-curated facts, uncertainties and registered test names. The hidden synthetic world and independent calibration receipts are evaluator-owned. The native 016 finite exact planner independently decides if a suggested sensor improves the modeled state classification.

One fully reviewed extra test can improve an ordinary four-state toy decision from 0.5 to 1.0 expected accuracy. A refitted classical planner given the same expanded catalog ties. Seven of the sixteen cases have at least one eligible improving test under their declared calibration and source/time assumptions; total possible accuracy gain from exhaustive **same-catalog** enumeration is 3.5 case-summed points. That upper bound includes one source which passes calibration but becomes misleading in a held-out RUN world.

### Observed actual model outcomes — experiment 42047326958

| Procedure | Strict typed responses | Tests actually admitted by MOTIF | Sum synthetic expected accuracy gain | Independent held RUN responses on admitted tests |
| --- | ---: | ---: | ---: | --- |
| Actual T5 raw text generation | **0/16** | 0 | 0.0 | none |
| Actual T5 token whitelist with `NO_TEST` | **16/16** | 0 (all abstained) | 0.0 | none |
| **Actual T5 forced registered-ID nomination + separate verifier** | **16/16** | **4** | **2.0** | **3 correct, 1 wrong** |
| Dumb fixed choice, always nominate `FOOD_SERVICE_GATE` (control) | n/a | **5** | **2.5** | not included in the model's scored held-RUN series |
| Fixed-seed random registered-or-abstain control | n/a | 4 | 2.0 | not included in the model's scored held-RUN series |
| Oracle: exhaustive classical catalog checks | n/a | up to 7 | 3.5 | conditional on calibration; includes one drifting source |

**Important:** The tiny model with a forced-ID output improved dramatically over its own raw generation but **did not beat the trivial fixed-choice baseline**. It tied the seeded random control on admitted cases / sum expected accuracy gain in this one small, artificial dataset. Zero evidence of a general reasoning advantage is claimed.

Its 4 admitted tests included **one source that was correctly calibrated but false after drift**: the resulting in-grammar modeled answer was wrong. This is exactly why T5 outputs, syntactic formats and prior validation cannot become proof of truth. In cases where it nominated an uninformative test or an unauthorized human action, the independent native gate refused and recorded the reason.

A high **gate-level safe-hold-or-useful** rate does NOT imply a high **language-model decision quality** rate; refusals are enforced by native code, not proof that T5 recognized the hazard. To keep this distinction visible, 023F additionally scores strict model selection separately from verifier-enforced safety.

### Full three-role real-model hazard

An initial direct `python demo.py --local-t5` exercise showed why a daemon worker that remains in PyTorch native inference when Python exits may crash at interpreter teardown (exit 134). It was not a successful three-role benchmark. The 023F `three_roles.py` harness prewarms the checkpoint, runs native 020F planning and three genuine T5 role prompts, freezes the bounded-grace result, then explicitly joins the model worker for safe interpreter shutdown. This is a **research teardown workaround**, not a hard inference cancellation or a production-safe worker architecture. Future durable deployment needs a bounded, cancellable subprocess with independent limits.

## What this proves / what it does not

**Proven for this constructed task:** We successfully downloaded public weights, executed real FLAN-T5-small CPU inference, restricted model output to explicitly approved symbolic test IDs at token level without fuzzy name repair, passed the selected ID through the actual 022F independent-calibration and 016 expectimax gates, and retained both helpful (3 correct held simulated outcomes) and damaging (1 wrong due to drift) results.

**Not proven:** that small T5 finds genuinely new physical questions; outperforms classic symbolic selection; is robust across real-world tasks; can guarantee true evidence; improves user wellbeing; respects live authority; or meets hard 80ms sidecar deadlines on the user's hardware. Costs and timings in this experiment are GitHub CPU measurements, not a guarantee of laptop RAM, network availability or model safety.

## Honest next frontier

The best current division of labor is **native MOTIF generates, verifies, and ranks question options; little T5 offers commentary or a proposed ranking within a finite read-only vocabulary; a native verifier retains veto and independent measurement custody.** Given this first benchmark, prefer the deterministic catalog check over letting the small model decide whether any question is needed. In the next experiment, compare a *native prefiltered shortlist + T5 reranking* against the same native shortlist without T5, using fresh held-out tasks and operational resource measurements. It may be that the small model adds useful wording/communication but **zero** decision gain; we should measure rather than assume.

Reproduce via `.github/workflows/motif023f-real-t5.yml`, which explicitly fetches the public checkpoint, runs deterministic reference tests, the actual smoke and the 16-case model trial, saves **receipts only**, and never downloads weights into Git history.

The foundational rule remains: **MOTIF thinks and checks; T5 may notice and suggest; independent evidence decides whether the question changes the world.**
