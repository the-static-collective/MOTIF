# LLM-001 — Proof-Carrying Branch Compiler

STATUS: Executable offline protocol only. No trained model, real LLM call, native field scene reconstruction, deployed JAR;VIS adapter, or engineering safety certification.

## Architectural bet
Instead of asking a model to write an authoritative answer using all historical context, compile a typed, source-scoped *action frontier*. The model proposes one source-cited hypothesis in JSON; a separate verifier must TEST it and return a receipt before the world changes. Select prompt context in proportion to what could change reachable future actions rather than merely semantic similarity. Unknowns and permission gates stay explicit; imagined states remain separate from observed history. This is a testable combination of established methods, not a proven new LLM architecture.

## Source-owned convergence
- COGNITION-010 is the stacked research base, but this test does NOT call original NovelGym code; its blocked-action fixture is invented.
- MOTIF-003 and CONFLUENCE-003 code exist upstream in the branch. The JS runtime is an adapter. A separate CI bridge *actually invokes original Python MOTIF-003* through its graph ABI and checks first-move parity on one authored case; this does not imply the runtime calls native 003 on every request.
- FIELD-014 PR #310 at 5f1f0ddca303616a4fd1805522c58a45baff934e is a separate unmerged owner. The adapter reads only its public export shape and refuses to infer physical safety, photo registration, or material fit.
- UNDERSTORY private MEMENTO is not imported. Root deduplication means an echoed claim is one source, not multiple witnesses.
- JAR;VIS is a future caller, NOT presently wired to this model envelope.

## Run (Node.js 20+, no external network, keys, or packages)

    node --test experiments/llm001/test.mjs experiments/llm001/local-model.test.mjs experiments/llm001/native-bridge.test.mjs

Exports: valid, available, imagined, search, rank, compile, gate, ownerTest, field014Aperture, keyOf.

Protocol: compile(world) -> optional model JSON {action_id,cite,hypothesis} -> gate(world,compiled,proposal) returns PENCIL only -> separate trusted owner simulation receipts -> ownerTest(world,held,receipt). Do not connect client-submitted receipts to ownerTest: its synthetic authority string is a **test fixture**, not authentication. The cache key is not cryptographic.

## Optional actual local language-model proposal
The loopback-only local-model.mjs module can POST a synthetic source-bound prompt packet to an explicitly consented local Ollama chat endpoint and pass its strict JSON response through the no-act gate. Its eight tests use a mock transport. Neither this CI nor the present runtime has executed genuine model weights. Do not confuse a valid JSON hypothesis with a correct prediction, an authenticated owner receipt, or an action. Keep source data and personal photos out of model inputs until separate consent/privacy designs exist.

## What this tests and does not test
Tests check deterministic schema validation, branch isolation, allowed action ranking, strong bounded classical BFS, evidence-root deduplication, a budget-aware HOLD, model proposal refusal, test-only owner receipt requirements, and a FIELD-014 geometry caution boundary. Success is structural protocol correctness, NOT improved LLM accuracy. A topological classical solver should tie or beat the heuristic on sufficiently short invented worlds. The evidence ranking now computes each fact's two-step action-frontier difference under a one-fact counterfactual, rather than merely checking topical word overlap.

## Next real-model phase
Preregister a withheld independent set of real source tasks and run a single locally provisioned open-weight model with identical generation settings on flat RAG vs full graph vs affordance-compiled packets, with strong classical and planner controls. Actually invoke native MOTIF-003 and the separate FIELD-014 scene code through pinned project-owned contracts. Measure verified task completion, false action rate, tokens, latency, compute/cost, retries, human corrections, and review refusals. This branch contains no personal photos or private credentials.

## Research provenance
Preregistration is committed before the code (29f64d1d647b6079b076a3c889861bc2216d979f). Existing prior art includes graph RAG/context engineering, structured verification, speculative reasoning and inference-time adaptive search; no blanket novelty or performance claim is made.