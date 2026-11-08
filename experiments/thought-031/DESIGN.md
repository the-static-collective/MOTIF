# THOUGHT-031 — Evidence relay and parameterized pidgin

## Why

In real THOUGHT-030 local Ollama Qwen2.5:3B run [42440979322](https://github.com/the-static-collective/MOTIF/actions/runs/42440979322), **16 genuine inference calls** ended without an independently checkable final interpretation. Both navigation arms used one retrieved file each, and the model chose to coin **zero** words. The GitHub workflow succeeded because it correctly recorded negative outcomes, not because the language model solved the problem.

Two distinct hypotheses emerge:

1. The model could benefit from a **source-owned evidence relay** that actually retrieves compact, typed, varied graph and proof artifacts before inference instead of merely ranking file names.
2. THOUGHT-030's pidgin symbol was a rigid alias for a single file read; repeat reads were deliberately suppressed, giving a word virtually no meaningful reuse opportunity. A model-invented word with typed parameters can communicate **new read targets using one shared term** while retaining a transparent, exact backtranslation. It remains optional, not preseeded with an invented word.

## Design

- `relay.py`: deterministic read-only selection from approved MOTIF public source, with actual proof/source and native graph-node/edge previews. The model receives the exact retrieved source IDs, provenance labels, hashes, and a small excerpt, not a claim that those snippets establish truth. Prefetch excludes the experiment's evaluator task specs and historical model-answer results by filename. This does **not** make the study independently blind: its synthetic task family is public in repository code and nearby experiments have overlapping descriptions.
- `pidgin2.py`: the model can **coin any valid term**, assign a short human-readable gloss and a parameterized template for one of the existing read-only queries. Example: `gobbo = read($artifact)`, followed by `gobbo(experiments/thought-023/grammar.py)`. The typed slot is validated through the exact same source-owned portal validator as a direct read. No new tools, programs, raw URLs, secret tokens or external authority. Definitions and uses are measured. Net communication bytes include definition overhead; token counts are measured separately. Non-use is an equally valid observation.
- `relay_session.py`: two optional research model calls, followed by **one reserved genuine final LLM inference**, whether the model used pidgin or not. A rejected model retrieval does not consume the final slot. Only actual read artifacts may be cited. A model's final typed role map and relation undergo development witnesses, the frozen 64-case task-owner evaluator, and the trusted source-owned Python check. Failed interpretations HOLD.
- `relay_llm.py`: local Ollama transport, no model substitutes, records actual HTTP inference receipts/tokens/phase; model responses remain completely untrusted JSON.
- `relay_run.py`: parallel control arms with pidgin disabled/enabled; identical maximum model calls per arm but **different prompts, not matched inference tokens or wall time**.

## Reproduce

```
cd experiments/thought-031
python -m unittest -v test_relay.py test_relay_http.py
python relay_run.py --backend offline --output offline-results.json
# real Ollama must be installed, and the requested model locally available:
python relay_run.py --backend ollama --model qwen2.5:3b --tasks food_safe,food_recalled_elsewhere --output real-results.json
```

## Epistemic and engineering boundaries

- **Offline fixtures are scripted.** Their known answers must not be called an LLM improvement; HTTP format tests use a fake server, not a pretrained model.
- On real Qwen, there is no requirement that a pidgin word emerges. If none emerges, record zero. If a word emerges but is unused, it does not count as a functioning communication channel.
- A model's correct mathematical answer on a three-feature synthetic task doesn't establish general-language comprehension, independence from training artifacts, or meaningful gains in a larger real project.
- Repository graph nodes and coordinates are not facts, causation or human authority. Source labels and SHA hashes establish provenance as declared or artifact integrity, not world truth.
- No arbitrary LLM-authored code executed, no public/private connector access, no filesystem mutation, no PEN or production promotion. No unpinned shell commands from model output. The GitHub research CI still installs Ollama via its unpinned upstream script (supply-chain limitation).
- This experiment depends on unmerged THOUGHT-017–030 branches. Draft stacked PR only.

## Falsification and next steps

If independent review finds the retrieved packets leak task policy, invalidate those tasks. If model-selected words never get used, the open option was not spontaneously adopted. If no final answers pass independent audits, evidence was delivered but **successful interpretation was not established**. A genuinely stronger study needs independently authored, held-out tasks, multiple seeds and compute-matched prompting, plus a source audit for all candidate files.
