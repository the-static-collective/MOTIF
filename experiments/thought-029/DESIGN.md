# THOUGHT-029 — Evidence-guided interpreter and MOTIF artifact aperture

## User's request

Give the generative language model *controlled visibility* into **all types of artifacts and graphs that MOTIF actually has access to**. It should be able to traverse symbolic graphs, evidence, hyperedges, reasoning ASTs, geometry and thought spaces, source designs, decision cartridges, research receipts, proof-memory lineage, and existing program data. It should not require dumping the entire source corpus into a prompt.

## What is implemented

`ArtifactPortal` indexes readable artifacts from an explicitly selected local MOTIF checkout: `.json`, `.jsonl`, `.md`, `.py`, `.diff`, `.yml`, `.yaml`, `.csv`, `.svg`, `.dot`, `.graphml`, `.xml`, `.toml`, and `.txt`. It catalogs binary `.png`, `.jpg`, `.webp`, `.gif`, `.pdf`, `.zip`, and structured binary formats as **opaque metadata**; a text-only local LLM does not perceive the pixels or PDF contents. A file-size guard excludes oversized text files; no claim is made that excluded bytes are available to the model. Secrets/credentials and symlinks are excluded by defense-in-depth filename and path checks, but file content should still be inspected before admitting private repos.

It exposes five **read-only, JSON-typed, paginated** tool operations:

- `catalog`: all indexed artifacts, typed and fingerprinted, with stable cursors.
- `search`: text and filename search across indexed types, provenance-preserving excerpts.
- `graphs`: discovers stored `nodes/edges`, `nodes/links`, `nodes/hyperedges`, `manifestations/relations`, `sources/links`, `vertices/edges` plus typed nested expression ASTs, including inside research receipts.
- `read`: navigates arbitrarily nested JSON pointers or paginated text lines, with content previews instead of unbounded dumps.
- `neighbors`: inspects edges, their original relations, hypothetical/observed flags, hyperedge member lists and AST argument links. Geometry is **a view**, not proof of causality or fact.

`mount_runtime_snapshot()` allows the source-owning MOTIF process to deliberately expose a **live graph or other JSON-compatible memory object** which has not yet been serialized. It requires explicit `operator_approved=True`; the language model cannot invoke it. Runtime claims remain unverified, regardless of their origin.

The source tree is scanned at run time. The model can navigate the entire *approved indexed collection*, not only a static five-document shortlist. Pagination limits output per request, **not total available graph size**; external account connector data is **not** automatically imported. To expose a new connected corpus, an independently authorized owner-side adapter must supply a permitted local snapshot and provenance label. No network request is made by the portal itself.

`DirectArtifactLLM` uses the same fixed-loopback Ollama endpoint and model registry as THOUGHT-019. Model asks for one portal action per generation and can decide to inspect a proof, symbolic graph, AST, thought field, or source text; a separate final typed response nominates mathematical roles and a relationship. The model is **not** allowed to execute the retrieved code, create edges as facts, call external tools, or promote a proof. Search excerpts are explicitly labeled untrusted, preventing source-text instructions from gaining tool privileges.

`interpreter.trial()` demands at least one actual portal query before accepting a candidate interpretation; citations must reference artifacts observed through the portal. It then uses the **separate THOUGHT-025/026 evaluator** for development, held-out 64-case truth test, and fixed-template executable check. Provenance/citations are not independent support of human semantics. Reuse is a proposal, not an automatic authority grant.

## Reproduction

```sh
cd experiments/thought-029
python -m unittest -v test_portal.py test_transport.py
python run.py --backend offline --output offline-results.json

# Only after installing a model on the same host; no model download by this CLI
python run.py --backend ollama --model qwen2.5:3b --steps 4 \
  --tasks food_recalled_elsewhere --output live-results.json
```

**Do not confuse offline tests or mocked HTTP requests with actual generative model inference.** There is a separate push-only CI job for a genuine Ollama Qwen run. Results can be correct, held, or malformed. A passing workflow verifies execution—not guaranteed understanding.

## What it does *not* do

- No claim of **all connected data everywhere**. Only indexed files from the operator-approved repo and explicitly mounted runtime snapshots are accessible. Unmounted Free Graph/GRAFT/ALEX or other GitHub repositories, Google Drive, private apps, memory databases and real-time sources require separate approved adapters and permissions.
- Not an unrestricted internet browser, inference of facts from attractive geometry, or proof that a cited artifact is true.
- No self-authenticated LLM identity. Ollama reports its own digest. Prompt injection is *contained in this tool contract*; text read from a source must still be treated as adversarial.
- No auto merge/install, PEN updates, posting, external contacts or execution of model-generated code.
- Current benchmark uses developer-authored three-bit Boolean tasks and an evaluator-owned task oracle. Success does **not** establish general language understanding or independent mathematical discovery.

## Suggested next boundary

Add **owner-approved external corpus adapters** (Free Graph, GRAFT, geometry repos, prior project artifacts), complete graph projection APIs, and a larger blind benchmark with human-judged grounding, against a call/token-matched baseline. Keep all source IDs, observation status, uncertainty and authority scope in the retrieval context. Avoid content flooding: fetch only evidence that changes the decision.
