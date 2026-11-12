# LLM-002 — Forkweave: graph-conditioned hidden states × shared-prefix worlds

Status: bounded executable experimental prototype, NOT a pretrained LLM, production JAR;VIS model, reasoning breakthrough or permission engine. Stacked draft on LLM-001 PR #311 (itself stacked on COGNITION-010 PR #308).

## The intersecting idea

LLM-001 compiles a source-bound, verified-prefix view. A genuine numeric causal-attention model precomputes attention K/V states for a shared prefix **once**. Multiple hypothetical futures then fork as suffix tokens. A learned rank-2 graph-conditioned adapter modifies each suffix's hidden input **before the suffix Q/K/V calculation**, allowing different graph states without changing the previously computed prefix.

An independent source owner would have to verify real changes. The experiment produces only PENCIL scores; it does not implement an autonomous owner receipt service.

**Key correctness constraint:** If graph conditioning changes the prefix, its K/V states change too. We must NOT reuse the same cache. In LLM-002, graph control is restricted to suffixes after the fork boundary. A graph-conditioned prefix triggers HOLD. This is the central engineering intersection.

## Run (Python 3.11 and Node 20+, standard library only)

    python -m unittest discover -s experiments/llm002 -p 'test_*.py' -v
    node --test experiments/llm002/test_weave.mjs
    python experiments/llm002/engine.py

Files:
- engine.py implements real 8-dimensional single-head causal dot-product attention, Q/K/V and softmax, absolute positions, prefix KV caches, a rank-2 trainable graph-to-hidden adapter, and independently recomputed controls. The frozen backbone is randomly initialized. This is NOT a full language model.
- bridge_cli.py accepts only bounded synthetic scenario JSON and checks cached versus full-forward numerical agreement for every fork.
- weave.mjs calls the actual LLM-001 compile/available/rank functions, hashes the source evidence into a scoped fork identity, invokes the numeric model only with explicit opt-in and synthetic fixtures, verifies matching branch results, and never authorizes an action.
- test_engine.py and test_weave.mjs test numerical parity, altered position, changed source/tenant/model/tokenizer/adapter version, cache mutation, changed prefix, source nonpromotion, absent consent, disallowed external moves and forged engine responses.
- PREREGISTRATION.md was committed first at 61d88d49e61e2cd9d4360a27fcba5ad780b947ac.

## Initial measured results (2026-11-12, independent GitHub CI)

Engineer-authored synthetic tool/permission classification; 48 heldout cases with distinct synthetic prefix tokens:

| Arm | Correct / 48 | Accuracy |
| --- | ---: | ---: |
| Same frozen causal-attention backbone, no graph adapter | 20 | 41.7% |
| Same backbone + trained rank-2 graph control | 44 | 91.7% |
| Exact classical authored rule | 48 | 100% |

The graph-conditioned toy model learned to use provided graph features. It did NOT beat the classical owner, generalize to novel real tasks, or outperform a pretrained LLM.

For five suffix forks over a seven-token synthetic prefix: independent full recomputation used **180 QK dot products**; reuse used **68 QK dot products**, a **62.2% reduction in that measured arithmetic unit**, with numerically equivalent output. This does NOT imply a 62.2% reduction in measured latency/cost/total FLOPs, and does not accelerate autoregressive decoding.

The dedicated workflow includes 23 Python tests and 10 Node cross-language tests. Check the current commit's results: older green receipts cannot substitute for current source.

## Hard scientific boundaries

- Model: a tiny frozen randomly initialized causal-attention circuit, not pretrained weights or a real LLM.
- Training data, action set, and truth rule: all author-designed. Distinct heldout prefix token variants are not independent external benchmark tasks. Feature input makes the task much easier than raw natural language.
- Source-root hashes check consistency but are NOT signed evidence, verified user identity, a permission source or an access-control boundary. A synthetic fixture marker does not establish that arbitrary user data is public.
- Numeric scores cannot certify physical safety, personal consent, action success, or evidence independence. No user data, external APIs or live JAR;VIS were touched.
- Cached-prefix Q/K/V parity is exact only where the prefix model, tokenizer, model weights, attention mask, positions and graph controls are identical. Adapter changes and trust-scope changes are conservatively held.
- Modern prefix caching, low-rank adaptation and activation steering have substantial published prior art; architecture novelty is unproven. Strong classical reasoning performs better on our toy fixture.

## Next falsification

Run a genuinely local pretrained model on independently authored public/consented tasks, with pinned model/tokenizer/template and source-owned access checks. Compare flat prompts, graph prompts and learned hidden-state suffix steering under equal token/latency budgets, using separate owner grading and strong classical graph/planner controls. Separately enable/disable real KV caching to distinguish performance from memory/prefill benefits. Never share a graph-conditioned prefix KV state with a different branch or privacy tenant.

Background technology: https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/ ; https://docs.vllm.ai/en/latest/usage/security/ ; https://huggingface.co/docs/transformers/en/kv_cache .
