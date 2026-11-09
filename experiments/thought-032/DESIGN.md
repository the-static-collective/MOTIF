# THOUGHT-032 — Shared Concept Language (optional co-invented, proof-aware)

## Research question

Given MOTIF's earlier verified mathematical kernels, symbol/graph artifacts, and proof cards, can a language model **choose** to coin a reusable conceptual term and later apply it correctly to different human stories? Does offering the shared term affect independently measured success compared with canonical mathematical vocabulary?

## What is implemented

- `concept_language.py`: A session-local codebook for optional model-coined words. A definition is a **transparent and inspectable typed bundle** of one existing finite set relation, one source-owned graph query pattern, the source-owned full-audit requirement, an explicit unresolved-transfer tag, and a next-development-probe strategy. Codebook labels are not learned new mathematics, permission, source of truth, or arbitrary code.
- `graph_match`: Deterministic graph motif inspection for directed dependency chains, observed contradiction edges, and corroborated shared-neighbor association **questions**. It distinguishes synthetic structural patterns from evidence or causal entailment; it never concludes a real-world link from visual coordinates or string similarity.
- `experiment.py`: Imports a **scripted-source-owner** proof of the difference kernel and independently verifies the scoped finite task before summarizing that prior evidence. The model gets the identical prior proof/graph context in both arms, not hidden target policies or target oracle answers. Model selects word or canonical relation and exact opaque field bindings for two *different* source-authored tasks. Source-owned 4 development cases, frozen 64-case audit and separate trusted-template executable check decide results.
- `model.py`: Actual direct local Ollama protocol with three requests per arm: preparation and two target applications. In the optional-language arm the first response may be `coin` or `decline`. The baseline arm receives the same context and warmup but does not receive invented words. The model may ignore a coined word later. All real HTTP generations report token/call counters.
- `run.py`: Source-only scripted fixture (NOT generative intelligence) or genuine opt-in Ollama comparison. Measured dependent metrics: terms coined, actual model uses, semantic correctness on fresh tasks, invalid/HOLD claims and model resource usage.

## Experimental cautions

The held-out tasks are still developer-authored finite 3-bit Boolean set problems, not independently blind real-world tasks. The prior proof is **from a scripted fixture** and only certifies source-owned behavior, never that the model discovered its meaning. A new model-created term expands only into an **already defined** operation; the experiment tests coining, transmission, binding, reuse and error containment—not historical mathematical invention or a free-form private communication system. The graph pattern does not imply the mathematical operation is semantically related. Total inference calls are matched across arms (3 each) but token costs and time are not. The prompt enumerates the valid operations and words are optional: there is no evidence of a spontaneous emergent language unless the real model actually coins and reuses one. Any failure or decline remains evidence. Local Ollama installation in CI is unpinned research-only supply chain. No automatic merges, vocabulary persistence, external account access, live permissions, PEN authority, deployment or arbitrary model-written code execution.

## Reproduce

```sh
cd experiments/thought-032
python -m unittest -v test_concept.py
python concept_run.py --backend offline --output offline-results.json
# With installed, running Ollama and qwen2.5:3b available:
python concept_run.py --backend ollama --model qwen2.5:3b --output real-model-results.json
```

Only source-owned, reviewed typed operations execute. Full finite audit occurs after a submitted model interpretation; failed audits do not inform later proposals in the same trial. The two synthetic tasks are scored independently with explicit status receipts; concept-card hashes establish accidental-change detection, not cryptographic authorship.
