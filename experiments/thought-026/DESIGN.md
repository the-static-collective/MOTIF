# THOUGHT-026 — Staged abstraction and partial-understanding retention

## Question

Can an actually invoked generative model map unfamiliar human stories to typed mathematics more reliably when **field grounding**, **relationship identification** and **mathematical composition** are separately represented and investigated, rather than requested as a single AST response? Can a failed step retain validated partial hypotheses and be repaired with *only developer-observed counterexamples*?

## Mechanics

1. **Ground**: A real model proposes which of two opaque fields represents the primary/current and comparison/event sets. Only contract validity is checked at this point; this is a **hypothesis**, not verified semantic understanding.
2. **Relate**: The same model chooses one of six source-owned semantic relations: difference, intersection, union, use-second, complement, symmetric difference. The model does **not** submit Python or a core AST. The relationship also remains an unverified hypothesis.
3. **Math**: A deterministic, source-owned compiler lowers the relationship and proposed role map into THOUGHT-025's strict AST, then THOUGHT-023's set interpreter.
4. **Development probe**: Four evaluator-owned, nonsecret synthetic probes are compared against THOUGHT-025's independent integer-bitmask task oracle. Stage-wise failures remain visible in the report.
5. **Diagnose and repair**: Counterfactual role/relationship possibilities are tested **only against existing development witnesses**, not frozen examples. One optional real model call proposes a revised pair. The system compiles and retests against the **same four observations**, charging zero extra distinct oracle queries.
6. **Frozen stage**: Only a candidate surviving every development example is independently checked on the full 64-case synthetic domain, and in the source-owned fixed-template executable Python. Any failed frozen check HOLDS, with no repair or tuning after the frozen data is examined.

`stage_fixtures.py` contains deterministic test fixtures only. It is never used by `DirectStageLLM`. A *real* Ollama execution must be separately identified by HTTP generation receipts, not by unit tests. All development prompts exclude the policy label, intended role names and frozen cases; evaluator-owned ambiguous/ternary tasks are HELD before any model invocation. No automatic source changes, PEN authority, external system actions or source installation.

## Correct interpretation

- Passing the source-owned, label-based fixture tests shows the **staged harness is internally correct**, not that a generative LLM understands language.
- The model can retain valid **structures** independently from correctness. In this experiment a stage is not certified correct until its assembled program survives developer examples and the frozen evaluator.
- A commutative operation cannot determine unique operand roles from input-output behavior; report equivalent role bindings as observational ambiguity rather than a discovered semantic identity.
- Four development examples plus a 64-input frozen audit are not independently blind; tasks are synthetic and constructed by the same research author.
- The staged model gets 2–3 model calls and four dev observations; the THOUGHT-025 monolithic comparator gets up to two model calls and two-to-four tests. **Compute, token and call budgets are not matched**. Do not claim stagewise superiority from unadjusted totals. The main result is introspection and partial-preservation, with comparative task successes described as exploratory.
- No cryptographic verification of model identity; model SHA is self-reported by Ollama. The GitHub Actions Ollama installer is **unpinned** and should not be treated as production-secure. Python `-I` is not an OS-level sandbox; only fixed-template Python executes.

## Reproduce source-only

```sh
cd experiments/thought-026
python -m unittest -v test_stages.py
python stage_cli.py --backend offline --output offline-results.json
cd ../thought-025 && python -m unittest -v test_abstraction.py
```

## Reproduce direct generation (requires preinstalled Ollama)

```sh
cd experiments/thought-026
python stage_cli.py --backend ollama --model qwen2.5:3b \
    --tasks food_safe,food_recalled_elsewhere,volunteer_eligible,not_on_shelf,vague_access,unknown_beliefs \
    --compare-monolithic --output real-model-results.json
```

Read the **actual model's outcomes** from `real-model-results.json`: do not infer them from fixture results or workflow passing. If the model fails a stage, HOLDS remain valid data. If model errors prevent generation, record it, never fabricate a valid response.
