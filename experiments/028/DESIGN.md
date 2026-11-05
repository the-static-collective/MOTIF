# MOTIF-028 — THE MEMORY OF FAILURE

**A real persistent, inspectable research-memory experiment**, not merely an account conversation summary or temporary process cache.

## What MOTIF now does

1. Calls original source-owned **GRAFT-028** to capture a documented *successful* and a deliberately *failed* GRAFT-027 experiment with original ALEX source-proposal receipts, labeled synthetic training/holdout/negative inputs, rejected code candidates, and exact executed results.
2. Saves a research episode only after **separate explicit synthetic capture and persistent-save approvals**, using an owner-private local directory and append-only newline-delimited JSON ledger. Every entry points to the preceding entry's SHA-256, preserving sequence and detecting accidental changes/corrupt tails. Disk writes are fsynced; a single-writer lock rejects conflicting writers. A symlink, publicly readable directory, damaged sequence, partial line, duplicate or oversized ledger is refused.
3. In a **new Node process**, opens the saved file; verifies original source-owned code Git blobs and every recorded event; ranks previous experiments using measured JSON-path/type structure rather than just prose similarity; **reruns GRAFT's original evaluator** for matched records. Altered cases with recomputed local checksums produce a replay failure.
4. Uses original **planZ Dijkstra/STRIPS** to choose a bounded next inquiry based on actual historical outcomes. A remembered failure proposes **recreate the failure as a new counterexample**. A remembered success proposes fresh independent revalidation. No close structural precedent starts with a baseline fixture, not invented experience.

## Run it

```sh
node --test experiments/028/test_ledger.mjs
mkdir -p .local/research-memory
chmod 700 .local/research-memory
node experiments/028/cli.mjs seed "$PWD/.local/research-memory"
# Exit Node and launch a separate process:
node experiments/028/cli.mjs replay "$PWD/.local/research-memory"
```

`seed` is an **explicit request** to persist **synthetic examples**, not a hidden background logger. It creates two retained synthetic records: one passing and one failing. `replay` reopens the same file in a fresh runtime, matches structurally similar cases, actually executes the remembered GRAFT code, then creates a new original planZ review plan. It makes **no external requests**.

GitHub Actions automates this two-process reproduction and stores the synthetic JSONL ledger plus a replay summary as an inspectable artifact.

## Source custody

Five original GRAFT source blobs are imported byte-for-byte from `graft/028-experience-memory` and earlier GRAFT owner branches, and all previously inherited MOTIF-027/026/023 source-owner verifications still execute. Nothing is written to the GRAFT or ALEX source repositories during a memory replay.

## Important boundaries

- **Synthetic labeled research only**—not personal memory, user conversation storage, unrestricted life-long context or real-world source authentication.
- Locally durable across **restarts with the same private directory**; **not synchronized across machines** and not automatically copied into any cloud account. CI artifacts have a limited retention window.
- Structural similarity produces a potential precedent, **not causal certainty**. Every recalled candidate is **replayed before its result can inform a new plan**.
- SHA-256 hash chains detect modifications but are **not signatures**; a malicious file editor could rewrite and rehash history. A writer lock is local-process coordination, not a distributed consensus.
- No automatic source crawler, private data capture, credentials, autonomous code installation or external effect. A production migration or replication design would require additional review.

**The measurable step is:** a previous actual failure survives termination of its creator process, is recovered, rerun, and changes a later classical plan.
