# MOTIF RING-001 — The Cartridge Constellation

**Status:** isolated research branch stacked on `experiment/door-foundry-001-capability-composition`. Synthetic, local, read-only. This is **not** a merged runtime, a live reLATTE integration, autonomous deployment, or proof that 149 branch implementations are compatible.

## The proposed circle

At the GitHub snapshot of **2026-11-06**, the repo had **150 branches**, including `main`. This branch preserves the other **149** as `DISCOVERED_ONLY` entries with their observed commit SHAs in `branch_inventory.json`. This is a **census, not an executable registry**. Branches can move after snapshot. No branch is imported, evaluated, approved, or granted permissions because it appears in the census.

```
                       MOTIF's typed question / desired output
                                        |
                                  NEED ROUTER
                                   /    |   \
                         use none   one   many
                                        |
                       exact source-checked installed registry
                          |               |             |
                     002 graph verbs    003 affordance  006 macro
                          \               |             /
                           typed artifact dependency DAG
                                        |
                             independent execution waves
                                        |
                        receipts + uncertainty + HOLD
```

Unlike an always-on stack, `ring.py` selects the cheapest **declared** dependency closure for **zero, one, or several outputs**. When two installed operators have independent prerequisites, it actually dispatches them in one local thread-pool wave, using the same frozen prior-wave artifact snapshot. The parent DOOR-FOUNDRY's original source-pinned MOTIF-002, -003, and -006 Python modules do the work; no mimicry or placeholder return values.

- `--outputs` (no values): **IDLE**; no handlers execute.
- `--outputs verbs`: use **one** installed graph-induction operator.
- `--outputs frontier`: use 002 then 003; skip unnecessary macro creation.
- `--outputs frontier macro_replay`: use 002; in one independent wave compile the macro and analyze affordances; recheck macro; return both distinct proposal artifacts. **Four** installed operator calls, not all five.
- `--outputs door`: use all five existing typed operators to assemble a proposal. The affordance-selected first move is **not** claimed to equal the separate macro's first move.

The specific adapter registry remains the parent `door-foundry-001/registry.json`, whose `ALLOWED_HANDLERS` and `SOURCE_LOCK` are code-owned. `branch_inventory.json` is **never** a Python import path, callable handler, rule granting consent, or dependency declaration.

## Running the actual current proof

From repository root (Python 3.10+, stdlib only):

```sh
python -m unittest discover -s experiments/cartridge-ring-001 -p 'test_*.py' -v
python experiments/cartridge-ring-001/ring.py --outputs
python experiments/cartridge-ring-001/ring.py --outputs verbs
python experiments/cartridge-ring-001/ring.py --outputs frontier macro_replay
python experiments/cartridge-ring-001/ring.py --outputs door
python experiments/cartridge-ring-001/ring.py --outputs frontier macro_replay --serial
```

Compare the parallel and serial receipts: they should match exactly. CI separately runs the parent DOOR-FOUNDRY regression suite.

## What 'wrap every branch' would actually require

For each selected branch, promote it **individually**, not by assuming the census is installed:

1. **Locate:** pin commit SHA, exact source files, ancestry, owning review status, known CI results, declared limitations and effect surface. A branch name is not evidence of passing tests.
2. **Passport:** issue a data-only signed-or-explicitly-unverified declaration of required / provided artifact *schemas*, origin, expected computational cost, side effects, source revision and branch-specific tests. Content digests alone are not author authentication.
3. **Adapter:** install an explicit, code-reviewed handler from pinned source. A generic YAML/JSON file must **never** name arbitrary code to import or execute. Change the allowlist through review; run tests in a bounded sandbox.
4. **Admit:** independently verify outputs, type compatibility, refusal semantics, resource limits and actual owner permission for the requested use. `DISCOVERED_ONLY` must not become `INSTALLED` by self-declaration.
5. **Route:** select only necessary methods. Permit concurrent paths only when they use compatible snapshots and have no unsafe shared state; otherwise execute dependent waves sequentially.
6. **Compare:** retain baseline answers, negative transfer, contradictions, cost, failure and abstention receipts. Multiple algorithms agreeing is **not** multiple independent observations.
7. **Cross project only when needed:** MOTIF owns cognition and routing; GRAFT can build reviewed adapters; CANNON can construct test builds; ALEX / MEMENTO / Free Graph supply distinct **source-owned** packets when connected. reLATTE is best reserved for transport, permissions, exchange and reversible custody **between** independently governed organs, not for each internal function call.

### Intentional non-claims and next falsifier

This prototype does **not** execute code from those 149 inventoried branches, estimate their fitness, learn to pick unknown algorithms, control live third-party services, send communications or evaluate actual human outcomes. The local threads are not evidence of faster performance; the planner's integer costs are declared placeholders. The parent DOOR-FOUNDRY already achieved typed local composition; RING-001's measurable increment is **task-conditioned subset selection and parallel independent local execution, plus a complete unpromoted branch census**.

The next research test should admit **two genuinely independent, conflicting experimental branches** into a separate sandbox and compare (a) fixed one-method, (b) always-all, (c) routed method-set, and (d) classical multi-method DAG planning, with frozen unfamiliar tasks, matched measured budgets, contradiction handling, negative transfer and local human review. Until then, the visual circle is a discovery boundary, not demonstrated general branch compatibility.

**Authority: NONE.** Every artifact is a synthetic proposal. No contents of the census grants authority or access. `HOLD` is expected when requested capabilities or cost budgets are absent.
