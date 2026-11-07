# THOUGHT-021 — Counterexample-Guided Language Model Development

**Stage:** experimental, typed and bounded. Stacked on THOUGHT-020. No repository installation, PEN promotion, deployment, arbitrary model-authored Python, or external permission.

## Question

THOUGHT-019's real Qwen2.5:1.5B model repeated the refuted GROW transition. THOUGHT-020's real LLM semantic critic vetoed one repeated function and got a different proposal, DRAIN, but not a verified solution. Can previously **witnessed development input/output behavior** constrain future model proposals more effectively than a simple semantic-duplicate veto?

THOUGHT-021 is a **finite counterexample-guided synthesis experiment (CEGIS-like)**: not an open-ended algorithm inventor. The model's grammar remains THOUGHT-017's set-expression DSL, the domain is finite (8 x 8 bitmask input pairs), and the independent target oracle is still owned by THOUGHT-018. A correct candidate is a known classical set operation; benchmark scores cannot demonstrate new computer science.

## Separated mechanism

1. The actual source-owned `ResearchDirector` selects a development probe, calls the independent bitmask oracle, and emits one observed transition. The critic receives **only** the bounded development feedback already returned by the director.
2. `WitnessLedger` stores an exact `(on_mask, toggles_mask, observed_next_mask)` triple, plus the three explicit bit observations (red, blue, green). It never extrapolates an unobserved universal rule, guesses a target, reads frozen audit labels, or treats duplicate observations as independent evidence.
3. A new model proposal must satisfy **every** previously witnessed triple. If it fails, the critic rejects it **without an additional oracle probe**. It still consumes a genuine LLM call and preserves an audit note. Distinct syntax that violates the same witnessed behavior also fails.
4. The model receives short, human-readable observed constraints, e.g. `red ON + TOGGLED -> OFF` and `green OFF + TOGGLED -> ON`. These are verified examples, not the correct expression or a label such as `FLIP`.
5. If a proposal survives those checks, the unmodified `ResearchDirector` still selects a new probe, evaluates it independently, and can return another observed example. A single development probe is not proof of general correctness.
6. Only after the director independently verifies the finite semantic space does it run the prior independent DEV/safety/frozen/stress graph checks. Successful candidates remain **review-only**.

### Comparison

- `control`: normal development feedback, no veto.
- `semantic`: THOUGHT-020-style veto of semantic repeats already refuted by the independent oracle.
- `constraint`: rejects **any** candidate that violates **any** previously witnessed development example, and frames those examples as explicit constraints in natural language.

All three arms receive the same model, task, temperature and maximum number of model calls. Real token expenditure, elapsed time, and model stochasticity may differ. They do **not** have equal token budgets; a one-run win is not proof of increased expected performance. Tests use scripted responders and HTTP stubs **only for unit regressions** and must never be reported as real model experiments.

## Reproduce offline

```sh
cd experiments/thought-021
python -m unittest -v test_constraints.py
```

Optional real Ollama test on operator-provisioned computer:

```sh
python run.py --model qwen2.5:1.5b --rounds 4 \
  --timeout 120 --output critic-vs-constraints.json
```

The dedicated GitHub Actions push job creates an ephemeral local Ollama daemon, downloads the selected open model, runs three arms, and uploads receipts whether the answer is HOLD or accepted. **Do not infer actual LLM inference from a passing mocked unit test; inspect real-model job receipts.** The Ollama official installer is currently unpinned and therefore a CI supply-chain risk; this is research only.

## Falsifiers

- If Qwen keeps repeating GROW, the constraint arm must return HOLD, not silently substitute FLIP or report success.
- If a new candidate violates even one witnessed example, no additional independent oracle call should occur for that candidate. Model calls still count.
- If the model proposes the correct expression, it passes through unchanged and must still face the original independent evaluator.
- Malformed feedback, false-types, audit-label injection, contradictory observed outcomes and replayed model text fail closed.
- If the source-owned director cannot produce an authenticated observation, the ledger has no independent authority: receipts are integrity digests, not proof of witness identity.
- No audit/stress labels in the LLM prompt. The evaluator cannot be rewritten or selected by the model.

## Next experiment

Avoid overfitting to one switch-state benchmark by testing *at least three independently authored grammars*, hold out tasks before prompting the model, and repeat across multiple seeds/model sizes while matching actual token/time budgets. Prefer falsification over an attractive single-run improvement claim.
