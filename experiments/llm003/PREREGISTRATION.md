# LLM-003 — The Error Dividend × Real Pretrained-Model Crossing
Frozen before implementation, 2026-11-12. Stacked on unmerged LLM-002 (#314). No model weights, personal data, private MEMENTO, or provider credentials are committed.

## QUESTIONS (separate; do not conflate)
H1 real-model correctness: Can a genuine pretrained open-weight causal language model compute a common prefix once and reuse exact KV states while each hypothesis gets a different graph-conditioned suffix embedding, with logits matching full independent recomputation? Demonstrates correctness and prefill reuse, NOT superior reasoning.
H2 wrong-answer usefulness: Under what circumstances can an initially wrong, explicitly PENCIL hypothesis yield a higher next-step decision value through an independently verified counterexample than a policy that merely tries to avoid being wrong? Error is useful only if discovering it teaches a model something that improves subsequent decisions NET OF the failed attempt cost. A wrong factual assertion without feedback is not a reward. Wrong output presented as fact is failure.
H3 interaction: Does allocating some of the model's parallel futures to plausible rival hypotheses and independently testing improve later decisions per probe and inference cost? Classical baseline can tie or win.

## Part A: pretrained open-weights crossing
- Target public pretrained model: HuggingFaceTB/SmolLM2-135M-Instruct, Apache 2.0. Record resolved revision before execution, download ephemeral weights in explicitly opt-in bounded CI. No private user prompt data.
- Frozen model/tokenizer/weights; compare 3 suffix graph conditions on an identical token prefix; full forward vs shared prefix past_key_values. Graph-conditioned suffix inputs_embeds via bounded rank-2 fixed projection, NOT changed prefix embeddings. Assert max absolute final logits difference < 1e-3 on float32 CPU. Record actual observed differences.
- Compare unconditioned, source-feature-derived bounded injection, and shuffled features at equal norm. Unless an adapter is trained/tested on independent tasks, do NOT claim graph improves pretrained accuracy.
- Record load/setup time separately, numeric inference time, actual tokenizer tokens, cache shapes, logits/proposals. Fail closed if checkpoint download unavailable; never fake weights.
- No model output is an independent verifier, authorized act, or certified source.

## Part B: preregistered wrong-hypothesis oracle test
- Independently seeded held-out hidden owner Boolean programs over three binary inputs. Owner's true mapping is not available to policies; prior hypothesis library + identical one-observation starting evidence.
- Matched policies: random query, strong classical maximum expected information gain, leading-hypothesis disconfirmation, direct confident answer (no probes), and a one-error-repair comparator with same verification information. Same source access, test budgets 0/1/2/3. Report ties and classical wins.
- Score held-out prediction accuracy across all eight input combinations, posterior log loss, number verified wrong provisional guesses, marginal decision improvement conditioned on wrong/right candidate, and probe cost.
- Regimes: reliable owner, 20% noisy reply, echoed/redundant source reports, and absent verification. Missing verification must HOLD rather than promote a prediction.
- A wrong hypothesis is useful only where independently verified counterexample improves a later choice NET of an explicit 0.04 accuracy-equivalent per attempted probe. Measure cases where wrong provokes no learning, false-audit contamination, and correct-to-wrong regressions. Do not reward proposing more wrong guesses.
- Source owner truth is separate from policy. Common rules / authored generators are NOT external benchmarks. Freeze seeds and score rules; don't revise after test to rescue result.

## Literature and scientific limits
Negative examples, active learning, error-driven training, intrinsic revision and feedback loops are prior art. External verification helps; intrinsic self-correction can also degrade correct answers. See Kamoi et al 2024 https://arxiv.org/abs/2406.01297 ; Hamdan & Yuret 2025 https://arxiv.org/abs/2503.14391 ; Zhang 2026 https://arxiv.org/abs/2609.35832 .
Public experiments only, proposal/PENCIL status, no merge/deployment authority. Honest negative results and classical ties expected.