# THOUGHT-027 — Proof-carrying fragments of MOTIF's learned abstractions

## Answer to the central question

**Yes, some fragments are verified — but verification has a scope.** Earlier experiments certified that specific **composed typed programs** produce the source-owner's expected output over all 64 pairs in a finite, three-bit world and agree with a separate fixed-template Python executor. The `bind()` and `relate()` predictions in THOUGHT-026 were *not* individually verified merely because they were well-formed. No existing test proves the model's semantic interpretation of arbitrary human language.

THOUGHT-027 turns this distinction into executable evidence:

1. **Unverified hypothesis**: A syntactically valid role or relation, possibly useful for another experiment, but never allowed into the certified library.
2. **Scoped certified composition**: `certify()` reruns independent 64-case task evaluation *and* the trusted fixed-template implementation, checks the original result receipt, binds a fingerprint to the source-owner task definition, and records the actual expression, mapping, and provenance label. A hash detects accidental edits; a hash is **not** cryptographic attestation to model origin.
3. **Identifiability**: Enumerate both variable permutations and all six allowed relations against the *independent oracle*. Promote an individual relation or binding only when **all** compatible models agree. Intersection's operand ordering is underdetermined; it must not be hallucinated as a discovered unique entity mapping. These source-owner judgments are offline and do not go into the model prompt.
4. **Reusable proof fragment**: An audited mathematical relation can become a **candidate** for another synthetic problem, but its old binding and proof cannot be transferred as truth. Choose an information-rich development probe from candidate output signatures alone, ask the new task's independent oracle for outcomes, then freeze a candidate for full-domain and executable audit. Failed transfers return HOLD. This is **oracle-assisted** transfer, not independent natural-language comprehension.
5. **Composition**: Two separately certified kernel operations (difference and union) can form a new typed operation `(A−B) ∪ (B−A)`, but their proofs do not certify the composition. It must pass fresh task-specific development, 64-case frozen, and separately executed fixed-template evaluations.
6. **Import**: `ingest.py` admits an operator-supplied THOUGHT-026 results JSON only after recomputing certification; provenance claims in the file remain **unverified**. Thus a direct Qwen model result *can* eventually enter the library, but the model's claim of success cannot.

## Reproduced outcomes (source-only scripted fixtures, **not** a new LLM run)

Four synthetic, independently reverified seed cards: `food_safe` (DIFFERENCE), `volunteer_eligible` (INTERSECTION), `food_donations` (UNION), `not_on_shelf` (COMPLEMENT).

| New task | Development queries | Frozen audit | Status |
|---|---:|---:|---|
| `reverse_outreach` | 2 | 64/64 | REVIEW reusable candidate |
| `food_recalled_elsewhere` | 2 | 64/64 | REVIEW reusable candidate with *reversed* operand order |
| `cancel_or_add` (direct fragment selection) | 2 | **27/64** | **HOLD**; development overfit discovered |
| `cancel_or_add` (composition of verified DIFF and UNION kernels) | 4 | **64/64** | REVIEW candidate, NOT installed |
| `unknown_beliefs` (true/false/unknown) | 0 | not evaluated | HOLD before Booleanization |

The four seed cards originate from a **scripted fixture** that uses task-owner labels: this does not establish that an LLM autonomously discovered those fragments. The proofs of program behavior are genuine and independently re-executed on source-owner synthetic tasks. It measures a reusable candidate-library architecture, not an independently blind research breakthrough.

## Reproduce

```bash
cd experiments/thought-027
python -m unittest -v test_proof_memory.py
python benchmark.py

# Optionally import an actual locally obtained THOUGHT-026 real-LLM report.
# This command always independently rechecks any reported success.
python ingest.py --report ../thought-026/real-model-results.json --output verified-fragments.json
```

## Guarantees and limits

- **No arbitrary model-authored code** is executed. Only checked code-free expressions in source-owned fixed templates.
- Frozen tasks are used only for verification *after* candidate selection, not to feed the LLM or refine a failing solution.
- No semantic proof for real inventory, actual permissions, factual belief truth, or unseen natural-language prompts. Nothing here applies to actual individuals or systems.
- Previously verified fragments are **hypotheses** in new situations; a new source-owned test is mandatory. If no fresh independent reference exists, retain uncertainty.
- The experiment does not independently verify Qwen's model identity or the authenticity of a supplied LLM receipt. Operator-provided labels aren't signatures.
- **No automatic install, merge, deploy, GRAFT cartridge publication, ALEX export, PEN mutation or external authority.** The local JSON is a user-controlled artifact; no silent background memory writes.
- This is a stacked draft on THOUGHT-026 and inherits its unmerged dependency chain. Existing older Ollama CI installation remains unpinned; THOUGHT-027 does not install or call a model.
