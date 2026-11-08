# THOUGHT-028 — Proof Weave: evidence-bearing reuse and active composition

**Status:** Synthetic, offline, reproducible research; review-only. Not a production capability, ChatGPT skill, autonomous natural-language interpreter, or model inference run.

## Research question

Can previously verified finite-set behaviors be remembered as evidence-bearing fragments, composed without hard-coding a target algorithm, and transferred into another synthetic task **only after new independent evaluation**?

## Method

1. **Admit sources.** Start with THOUGHT-027's two independently recertified source-owner cards, `food_safe` (DIFFERENCE) and `food_donations` (UNION), created from explicit scripted fixtures. Each card passes 64 independent Boolean cases and 64 fixed-template executable cases in its own author-designed task. Card SHA-256 hashes are integrity checks, **not provenance signatures**.
2. **License operations from evidence.** Only a certified DIFFERENCE fragment licenses the `difference` syntax for composition, and only a certified UNION fragment licenses `union`. The source-owned semantics of those operations are never supplied by the LLM and do not change. Input references are source-owned operands. A separately certified COMPLEMENT card would license the universe constant; this benchmark does **not** introduce it.
3. **Generate candidate mathematical behavior.** Enumerate bounded source-owned typed ASTs up to depth 3 and 15 nodes; collapse by complete **candidate** behavior over the 3-bit input space. In this fixture, the licensed grammar has eight distinct possible functions. This enumeration uses the definitions of the primitive operations, never the new task's target oracle.
4. **Choose informative questions.** Active-query policy ranks as-yet-unasked `(a,b)` probes by how strongly they partition the candidate signatures. Only after selection does the **task-owner's independent integer oracle** reveal an expected answer. A bounded 2–4 development queries selects a candidate or returns HOLD. The selection policy does not inspect target truth values or the frozen 64-case audit beforehand.
5. **Freeze, check, retain.** A selected candidate must pass the new task's full independent 64-case evaluator and a separately executed reviewed Python template. On failure, HOLD; **never repair using frozen labels**. On success, an explicitly called `add_derived` function independently reruns checks and stores a derived certificate with its parent proof hashes, full source-task scope, actual program, role binding, and signed-off limitations. No automatic persistent write outside the operator's exported JSON.
6. **Reload and reuse.** `EvidenceStore.load` verifies every source card and new derived card against the task owner's oracle and runtime before use. New tasks still require new development examples; a prior proof is a **candidate**, not authority about the meaning of the new task.

## Actual offline results

Using source-owner-aware **scripted seed fixtures, NOT actual Qwen/Ollama calls**:

| Test | Queries | Frozen score | Result |
| --- | ---: | ---: | --- |
| Reuse a single old operator on `cancel_or_add` | 2 | **27/64** | **HOLD**: favorable development examples overfit |
| Compose licensed operators on same task, independent arm | 2 | **64/64** | REVIEW: symmetric difference constructed |
| Reuse saved new derived proof on `toggle_equipment` (different field names/story) | 2 | **64/64** | REVIEW: new task independently checked |
| Reuse a difference proof on `reverse_recall` (reversed role order) | 2 | **64/64** | REVIEW: role order rechecked |
| Boolean coercion of unknown truth values | 0 | Not evaluated | HOLD |
| Majority threshold operator (not expressible) | Not queried | Not evaluated | NEGATIVE grammar-closure control |

All positive candidates independently passed 64/64 fixed-template executed Python checks. `EvidenceStore` revalidated **two source cards plus one derived card** after JSON serialization and reload. `installed=false`, `external_authority=NONE` throughout.

This is **not a fair comparison of general compute efficiency**, an independently blind language task, or proof of self-improving intelligence. The target semantics and each synthetic task are source-owner authored. The experiment compares candidate sets in separate research arms; observations and frozen outcomes from one arm are **not fed into the other**.

## Reproduce

```bash
cd experiments/thought-028
python -m unittest -v test_weave.py
python memory_benchmark.py
```

Run the parent verification independently:

```bash
cd ../thought-027
python -m unittest -v test_proof_memory.py
```

`offline-results.json` includes complete development receipts, fresh audit result, derived certificate, serialized proof store, and explicit zero-LLM report. A new CI workflow checks core scenarios. The experiment never downloads Ollama or any model.

## Boundaries and next falsifier

- The mathematical behaviors and closed-world three-category sets are source-owner fixed; the software does **not** independently discover domain semantics from arbitrary human language or import private user data.
- Proof certificates are task-scoped. They do not say an actual pantry, access register, or person's beliefs operate according to these toy semantics.
- Model-authored Python is never executed. Only validated expressions in a fixed source-owned interpreter are used. Python `-I` is not an OS sandbox.
- No automatically merged PRs, installed capabilities, external permissions, user-data ingestion, PEN changes, or production modifications.
- The prior experiment branches are stacked and not merged into main. All source claims should refer to their exact branch/CI receipt.
- Stronger future trial: use independently authored, hidden semantic tasks, matched CPU/inference budgets, and a direct LLM query that attempts **story-to-evidence retrieval**; compare with an oracle-assisted classical search and an unverified-memory control. Do not claim that this trial demonstrates those capabilities.
