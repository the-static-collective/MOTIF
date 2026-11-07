# THOUGHT-019 — MOTIF directly invokes an LLM, without a conversation relay

**Status:** Bounded executable integration. A real open-weight generative model can run inside a GitHub Actions CPU runner (`qwen2.5:1.5b`) or the operator's local Ollama daemon. The standard unit tests are transport fakes and **do not prove LLM inference**. The separate `direct-real-generative-model` job is the actual inference test; do not claim success until its CI result and raw receipts are inspected. Initial third-party setup action failed downloading a 9-byte 404 archive; replaced by the documented official Linux installer, still pending verification.

## Change since THOUGHT-018

THOUGHT-018 had a `GPT6ConversationRelay` whose two typed proposals were manually moved from chat into a JSON file. THOUGHT-019 eliminates that relay. MOTIF's `ResearchDirector` directly calls `DirectLocalLLM.propose` each development round. That implementation itself makes an HTTP POST to a **fixed `127.0.0.1:11434` Ollama endpoint**, receives model-generated text, validates its JSON and typed program expression, and returns it to the original THOUGHT-018 director. After a developer probe the next model request contains the actual developer-only feedback, not audit/stress labels. The independent THOUGHT-017 evaluator and its fixed-template Python compiler remain unchanged.

```text
MOTIF director
    -> verify operator-selected installed local model and daemon-reported digest
    -> HTTP request to actual generative model (no tools, no external URLs)
    -> model proposes constrained JSON AST plus one candidate test
    -> source-owned strict schema validation
    -> MOTIF chooses a discriminating development test
    -> independent bitmask oracle grades proposal
    -> development-only feedback returns to model for next round
    -> freeze selected mechanism
    -> independent graph validator / held-out audit / stress
    -> HOLD or review-only patch; never install, merge, deploy or commit PEN
```

The known 018 benchmark uses small synthetic set-state transition tasks. Its evaluator has five known mechanism families (`KEEP, GROW, DRAIN, REPLACE, FLIP`). This is **not** proof of discovering new computer science, novel mathematics, model self-improvement, or general language comprehension. A competent model may propose a known mechanism directly; no improvement should be claimed solely from a pass.

## Reproduce on a host with Ollama

```sh
# Manually install Ollama and download an appropriate small model first.
# Only an explicitly selected, already-installed model may be used.
cd experiments/thought-019
python -m unittest -v test_direct_model.py
python run.py --model qwen2.5:1.5b --rounds 3 \
    --timeout 120 --output direct-llm-results.json --allow-held-reply
```

`--allow-held-reply` allows a run to finish even if the model's proposal fails the grammar or evaluator; **it does not fabricate a successful experiment**. An absent model or no actual HTTP inference still returns a failure exit code. The model may return an invalid typed reply; that outcome is interesting negative evidence and must remain HOLD. Our first real CI run used a smaller `qwen2:0.5b`: it made one verified model HTTP generation but returned an invalid typed proposal, so the director correctly held the result. A follow-up experiment with `qwen2.5:1.5b` and a JSON-envelope check first hit a minimum-rationale validation failure; after adding minimum-length constraints, its real CI run **42316438225** made two actual generative inference calls and produced two valid typed proposals (GROW and DRAIN). MOTIF independently refuted GROW and inspected DRAIN but could not verify a final mechanism; it correctly returned HOLD with two development probes. The current follow-up also passes the director's surviving dev hypotheses back to the LLM and permits three bounded rounds, without revealing any frozen audit labels.

## Boundaries and audit criteria

- The model name is explicitly operator selected and checked against `GET /api/tags`. Model tags ending in `:cloud` are refused; the service URL cannot be set through CLI, model output, environment or prompt. No remote provider, secret, source mutation, automatic downloads or contact system is used by the research process.
- The daemon's SHA-256 digest is *self-reported metadata*, not cryptographically authenticated to an independent registry or a signature. Receipt tracks round, model tag/digest, prompt and reply digests, elapsed time and token counts. The complete input/reply text is not written into the public receipt.
- The exact typed AST, bounded colors, source-owned independent oracle, hardcoded developer probes, frozen audit, and zero-authority constraints are preserved from 017 and 018. No arbitrary model-generated Python execution.
- Any invalid model response is HOLD; a real HTTP generation is still recorded separately from *passing validation*. No silent fallback to tiny Naive Bayes or hard-coded FLIP JSON.
- The local runtime uses the existing source-owned trusted Python compiler. `python -I` is not an OS security sandbox, but generated Python cannot be controlled except through the checked, code-free DSL.
- The real LLM is run only in an **ephemeral GitHub Actions runner** and the operator's optional local Ollama. The workflow obtains Ollama from the current official Linux install script; this unpinned installation is a CI supply-chain risk and must be version-pinned/reviewed before any trusted production process.
- The public fixture brief must contain no personal data or private accounts. The workflow uploads only synthetic development receipts. It requests read-only GitHub permissions.
- Results depend on chosen model weights, daemon version, prompt, hardware and random variation, so inference pass/fail may vary between model versions. Repeated model calls, counters and validity flags are measured directly instead of guessed.

## Next research frontier

Once the real CPU-model workflow actually succeeds, record one independent multi-turn model run with two distinct valid suggestions and developer feedback. Compare with previously fixed scripted/Naive Bayes/replay routes at equal query and CPU budget on a *blind* new task family, preferably with external human-authored outcomes. Do not call the current finite switch-state demo a general autonomous reasoner.
