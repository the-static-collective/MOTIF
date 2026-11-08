# THOUGHT-030 — Evidence navigation + experimental, model-coined pidgin

**Experimental research only; nothing merges, installs, publishes a graph edge, or changes PEN.**

## Two user-approved experiments

### 1. Source-owned evidence navigator

An approved `ArtifactPortal` already exposes symbolic graphs, ASTs, hyperedges, proof memory and source documents. THOUGHT-029 let a small LLM inspect it but observed repeated reads and unsupported final citations. `navigation.EvidenceNavigator` now ranks real indexed artifact **IDs** against words in the human problem, diversifies among artifact types, de-prioritizes already-inspected documents and lists relevant structured graph IDs. It exposes hints, not task answers, new graph truths, or a compulsory model plan. Actual model actions remain typed and read-only. Duplicate exact requests are suppressed in the guided session. The final interpretation needs a citation to a source **actually read**, rather than one merely surfaced by search.

### 2. Optional model-designed pidgin

A model may, but need not, invent a **new word** (e.g. `mowie`) and publicly define its meaning as a single typed, approved read-only portal request:

```json
{"action":"define","symbol":"mowie","meaning":{"tool":"read","artifact_id":"experiments/thought-027/reuse.py"},"gloss":"Read reusable proof mechanisms"}
```

MOTIF checks the word for ambiguity and the meaning against its existing typed portal contract. A later model response may say `{"action":"speak","symbol":"mowie"}`. MOTIF expands that into the exact canonical tool request, executes only the existing read-only tool, and returns the ordinary JSON result. A word never confers an external capability or makes a natural-language claim true. The glossary and the round-trip translation are included in transparent receipts. The model may ignore the option; **zero invented words and zero uses are meaningful possible outcomes**. No pre-scripted special word is included in the actual model prompt.

This is a **bounded experimental negotiated lexicon**, not a secret language, universal language invention, learned neural codec, or independently validated shared semantics. Aliases cost a generation to define, so they can make communication *less* efficient unless reused. Model-chosen symbols are permitted only inside the currently approved research session; no automatic persistent glossary is installed.

## Three-arm comparison

A) THOUGHT-029 unguided direct artifact browsing; B) evidence-router guidance with conventional JSON actions, no pidgin; C) the same evidence route with optional negotiated pidgin. All use the same target task, same explicit Qwen tag, same maximum model generations, same independent developer probes and frozen validator. The one-time model connection does not count as inference. **Prompt sizes, tool results, actual model calls, output token counts and wall time are not matched**; they are separately recorded. Task is synthetic and author-designed; earlier repo files also mention these tasks and can be inspected, so this is **not a blind, withheld benchmark**.

Success signals: completed real model inference, number of useful distinct artifact reads, repeated-request rate, invented words (if any), words actually used, correct citations to actual reads, typed final interpretation passing development and full independent 64-case finite truth-table/fixed-template Python checks, token/elapsed totals. A `HOLD` is a valid, honest result. An invented word is not itself improvement.

## Source-owned safeguards

- Model sees permitted public project artifacts only, not account data or automatically connected external corpora. Read-only source indexing and runtime snapshot controls remain in THOUGHT-029.
- Contents of documents are untrusted data; model-directed code/shell/URL operations have no executor. Every pidgin utterance is backtranslated into the same read-only contract.
- Model cannot create true observed graph edges, assert proofs, run its own generated code, mark author-designed oracles correct, or install new language syntax.
- No prompt from the target evaluator sends actual expected outputs, frozen cases or task policy to the model. Note that this repo contains **public synthetic examples and evaluator source**, so the trial cannot establish blind general-language understanding.
- A proof card reuses only the previously certified finite semantics; it does not transfer real-world factual authority.
- Existing Ollama installer in the disposable GH research runner is unpinned; it is not production-safe or model-origin cryptographic attestation.

## Reproduce

```bash
cd experiments/thought-030
python -m unittest -v test_router.py test_pidgin_http.py
python experiment.py --backend offline --tasks food_safe,food_recalled_elsewhere \
  --output offline-results.json

# For a real model: manually provision a *local* Ollama model first
python experiment.py --backend ollama --model qwen2.5:3b --steps 6 \
  --tasks food_recalled_elsewhere --output real-llm-results.json
```

`test_pidgin_http.py` operates an HTTP **stub**. It does not demonstrate real generative inference. The dedicated push CI job downloads and operates actual Qwen2.5:3B through Ollama and saves its receipts. No claims of actual model coining/use or improved grounding until the job's raw results are inspected. The research change is a draft stacked on THOUGHT-029, not a production deployment.
