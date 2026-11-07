# SELF-MIRROR-001 — MOTIF studies its own selection rule

**Status:** experimental, synthetic, **proposal only**. Stacked on `FIR-001` and `MATHAL-001 / NUNUMATHAL-001`; no production model, real-world action, permission, or broad self-modification.

## What is actually executable

The existing `MOTIF-003` experiment ranks candidate graph rewrites by immediate reward, reachable possibilities, and reachable futures. This experiment makes the **policy selecting among these proposed rewrites** into an inspectable object and asks whether small typed revisions help. It does not alter `MOTIF-003` or learn new world dynamics.

- **Observe** training failures against independently computed synthetic option values, recording individual counterexamples and feature contrasts.
- **Propose** within a declared, frozen two-parameter linear grammar: `immediate + w_frontier * new_affordances + w_reach * reachable_states`. Each revision has a source policy, target policy, rationale, and FIR **I** receipt through the actual `mathal001` executable.
- **Select** candidates with a separate validation split, without exposing test/shift examples during proposal or selection.
- **Audit** against untouched IID and adversarial changed-mechanism (OOD) cases. Exact finite result can receive a `Warrant(finite_computation)` with the **full fixture digest in its scope**, but any universal benefit remains unadmitted.
- **Compare** to a classical exhaustive two-dimensional weight grid, including an equal-budget control, and explicitly report if the classical grid is stronger.
- **Preview** actual `MOTIF-003` rows in `preview_motif003` with status `I` (hypothetical), or `HOLD_INCOMPLETE_FRONTIER` when exploration was truncated. This bridge **does not** assume the reported candidate outcomes are real.

The test's synthetic target rewards are `immediate + 3*affordances + reach + noise` for the IID world; the deliberately shifted world instead uses `immediate - 4*affordances + reach + noise`. The shift makes previously useful new affordances into misleading proxies. All four splits have distinct frozen deterministic seeds. All outcomes are exposed only to evaluation code; the policy sees action features alone.

## Run

```bash
cd experiments/selfmirror001
python -m unittest -v test_selfmirror.py
python selfmirror.py
```

Python 3.10+, standard library only. In a local source bundle without `MOTIF-002`/`003`, the single repository-integration test skips; CI runs it using the actual files.

## Interpretation

If this version reduces regret on held-out IID examples, it demonstrates **bounded selection-rule revision inside the specified synthetic grammar**, not autonomous invention of mathematics, a generally better agent, or proof of a causal world model. The hostile shift and the classical grid are part of the report rather than optional success-story filters. There is no continual update, deployed intervention, online feedback, access to external services, or automatic change to any installed MOTIF cartridge. A candidate is not promoted merely because it is selected by its own validation procedure.

## Source lineage

- `experiments/003/affordance.py` — original hypothetical-action interface; read-only integration.
- `experiments/mathal001/mathal.py` — typed FIR crossings with receipts, used for each policy proposal.
- `experiments/fir001/fir.py` — F/I/R status and local finite warrants.
- `nunuMATH: First Course in FIR Systems`, especially chapters 6–10, 12–15 and Problems C.8, C.11–C.12; `nuMATHELOLOGY` 2nd ed.; `Twelve Worlds Before the Arrow` (user-authored Google Drive texts). These are conceptual sources, not independent empirical proof of the new program.
