# MOTIF-021F — THE CHORUS (Observer / Critic / Hypeman)

**Research question:** What changes when a very small, strictly advisory language model observes MOTIF's native reasoning **in parallel**, instead of becoming the reasoning engine or interrupting its decisions?

**Prototype implemented.** This stacked experiment extends 020F (PlanZ × cost of inaction), 019F (classical planner) and 017F/016/015. The prototype's default CI mode runs one injected **SCRIPTED** text fixture (not an LLM). An **actual FLAN-T5-small adapter is implemented but has not been weight-loaded or benchmarked** in CI. Using it requires separate opt-in and already locally cached model weights on compatible equipment.

## Architecture

    PUBLIC-SAFE OPERATOR PROJECTION
           |                     |
           v                     v
    NATIVE MOTIF PLANNER     ONE LOCAL TEXT SIDECAR
    deterministic model      one shared FLAN-T5-small checkpoint
    evidence and gates       3 short SEQUENTIAL prompts
           |                     |
           |                   observer → critic → hypeman
           v                     v
    NATIVE PLAN RECEIPT      UNVERIFIED COMMENTS ONLY
           |                     |
           +-----> result -------+

The model worker starts before the native planner; both run **concurrently**. Only one model instance runs inside one daemon worker; its three roles execute sequentially inside that worker to avoid 3× RAM usage. The native planner never waits *more than the declared post-planner grace period* for comments. A model still executing after that limit returns `DEFERRED_NOT_READY` for unfinished roles; the worker cannot be forcibly interrupted during one inference and should be isolated in a separate cancellable process for production.

**Hard rule:** sidecar text has NO ability to alter a known fact, force an action, update planZ, grant permission, declare a deadline, submit an application, call a person, increase an evidence rating or modify MOTIF's native result. This is enforced structurally: native planning never reads the model output; the result stores the native object separately from all sidecar notes.

## Roles

- **OBSERVER — “What changed?”** One newly known fact and one still missing fact, as text. It may misread the source; the answer is unverified.
- **CRITIC — “What breaks?”** One unsupported assumption, a likely failure mode, and one small reversible test. Its objections can be offered to the operator, but are NOT formal counterexamples until separately tested.
- **HYPEMAN — “What is already possible?”** One earned capability and the next small feasible task, without false confidence, invented commitments or permission. Encouragement cannot be treated as evidence.

One small model with three distinct jobs is cheaper to test than three independent language-model processes, and provides contrasting perspectives without giving the model a veto.

## Choice of model

**Google FLAN-T5-small**, `google/flan-t5-small`, approximately **77M parameters**, Apache-2.0 license. The published model card labels it a T5 text-to-text model and warns about model limitations. This is **not** a chat model or a deeply capable autonomous critic. It can be asked to produce short summaries and specific next-step suggestions, but factual judgment stays with deterministic checks and independently verified sources. Model source: https://huggingface.co/google/flan-t5-small

The optional adapter uses Hugging Face Transformers with PyTorch in CPU mode and lazy loading. It will NEVER download weights as part of this pipeline: both `AutoTokenizer.from_pretrained` and `AutoModelForSeq2SeqLM.from_pretrained` are called with `local_files_only=True`. Missing cache, optional dependencies or an incompatible environment produce a held sidecar note, not an implicit network call or a failed native plan.

A modern Python/PyTorch setup is required; do **not** assume a 2012 Mojave Mac can install current packages. CPU inference latency and memory have NOT been measured on the user's equipment. We deliberately do not vendor model weights.

## Run

For **test mode only**, no extra packages or network:

    cd experiments/021f
    python -m unittest -v test_chorus.py
    python demo.py

This invokes the existing **real** 020F Fellowship user-update planner as the native decision, and feeds a public-safe projection into deterministic text snippets explicitly labeled SCRIPTED_FIXTURE_NOT_AN_LLM. GitHub Actions exercises native isolation, real concurrent scheduling, bounded output, privacy rejection, deferred responses, native errors, and refusal to grant authority.

To opt into **actual** local inference, first acquire the model checkpoint by an explicit separate action, and install compatible `torch`, `transformers`, and `sentencepiece` packages on your own supported platform. Only then run:

    python demo.py --local-t5 --grace 2

If the weights are not cached, the native planner still returns a decision and the sidecar yields HOLD_BACKEND_<ERROR> or DEFERRED_NOT_READY. This pipeline does not install dependencies or contact Hugging Face automatically.

## Boundaries and negative controls

1. **Source privacy:** `PublicProjection` is a short, operator-curated public-safe excerpt. Simple checks reject oversized data, email-like addresses, phone-like numbers and some credentials. **Regex checks do not guarantee privacy; never feed actual private field notes or intimate records to the model without an independent approval/redaction procedure.**
2. **Native correctness:** pure language output is neither a proof nor a decision. Model answers may be false, overconfident, sensitive, or prompt-injected. A text-only "I authorized" statement is always untrusted.
3. **Latency:** true overlap with native planning is tested using synchronization events; the tiny model's real-world throughput, threading/GIL effects, and CPU load are not measured. A slow model may consume CPU even after its result is deferred; hard timeouts need process isolation.
4. **Cost of inaction:** critiques arrive after the native plan or get deferred; they cannot block a genuinely expiring opportunity while someone waits for hype or a second opinion. Operator review of a critique is a separate decision requiring its own temporal accounting.
5. **Ground truth:** there is no independently scored corpus of better outcomes from T5 in this PR. Future evaluation must compare native-only vs native+roles against sealed evidence, real operator review decisions, hallucination rate, action reversibility, latency, and the degree to which useful failures are surfaced—**not how inspiring the text sounds**.
6. **No external side effects:** code does not contact any human, issue, calendar, grant, or website; no action dispatch, background agents, recursive uncontrolled learning, or silent permission transfer.

**One-sentence design law:** *The deterministic planner does the work; the little language model watches, questions, and encourages—but never gets to rewrite what happened.*
