# DECODER-INTEGRITY-001 — Can MOTIF notice an unreliable instrument?

**Status:** executable synthetic research cartridge, stacked on `CONTEXT-GATE-001`, `SELF-MIRROR-001`, `MATHAL-001`, and `FIR-001`. Not deployed, not autonomous, not a verified real-world sensor or auditor. Python 3.10+ standard library only.

## Research question

`CONTEXT-GATE-001` improved local synthetic routing but suffered when its primary context signal inverted. This experiment gives the router a second **fallible, delayed audit instrument**, asks whether *agreement with its original calibration* has degraded, and conservatively withdraws the working assumption supporting contextual routing. The monitor cannot infer why the instruments disagree or authenticate their declared independence.

This is a **classical sequential two-channel agreement test**, not a new mathematical theorem, general causal detector, or system for validating arbitrary claims.

## Executable protocol

1. A pre-existing context gate is trained using `train` outcomes and chosen using `validation` outcomes, exactly as in `CONTEXT-GATE-001`.
2. Separately calibrate the observed primary/audit agreement on 320 `train` pairs. The audit is generated using an independently sampled error, conditioned on the hidden synthetic regime, but the monitor only receives `WitnessPair(event_key, primary, audit, primary_origin, audit_origin)`. Its asserted origin metadata is **not authentication**.
3. Freeze `Calibration(agreement, one-sided lower bound, source digest)` using a Hoeffding-style confidence allowance. Freeze the rolling window length (48) and finite repeated-testing budget (300 checks, 1% cumulative alarm budget). The monitoring threshold subtracts another union-bound allowance from the calibration lower bound. Concentration arguments require independent samples; they are **simulation assumptions**, not guaranteed in real deployments.
4. For each event, make the next `I_PROPOSAL_ONLY` decision **before** reading that event's delayed second-channel audit. Update the monitor from the second-channel observation afterward. Neither `Gate.choose` nor `Monitor.decide` receives hidden regime or rewards.
5. If rolling agreement drops below the predeclared bound, admit **only** the exact finite agreement statistic, reopen the `ASSUMPTION` that the primary context decoder is currently adequate, and use the frozen immediate-weight `BASE` policy for later simulated proposals. This is a degraded proposal **not proven safe or optimal**. Unknown/incomplete actions still hold.
6. Missing audit beyond a configured streak, shared declared origin, exhausted statistical check budget, and duplicate feedback are explicitly handled; held states cannot self-certify recovery. A new externally reviewed calibration would be required for recovery.

## Tests and hostile controls

- **Clean:** detector remains `WATCH`; synthetic gate regret stays **2.8458**.
- **Primary inverted only:** alarm appears after event **47** (0-indexed), freezes contextual trust, and reduces mean regret from **5.3458** for the unguarded context gate to **4.0000** for the monitored fallback. Always using BASE would score **3.8292** on the same fixture; our detector does **not** beat that comparator.
- **Both sensors inverted:** detector stays `WATCH` and retains **5.3458** regret. Agreement alone cannot identify common-mode corruption. This is a fundamental blind spot of this experimental test.
- **Audit-only inverted:** detector also alarms, although the primary sensor remains correct; guarded regret becomes **3.4833** instead of **2.4583** for the unguarded gate on the same environment. An agreement alarm does not identify *which* witness became unreliable.
- **Single-sensor marginal frequency:** primary `amber` rate is 0.4542 before inversion and 0.5458 afterward in the balanced OOD fixture; a symmetric single-channel frequency statistic lacks an intrinsic orientation witness.
- **Correlated provenance / unaudited history:** a declared shared origin forces hold; falsely distinct metadata cannot reveal hidden dependence. Missing reference and an exhausted repeated-testing budget force hold.
- **FIR receipt:** the prior current-adequacy claim was explicitly an assumption; the finite measured agreement drop is an F_LOCAL observation; hypothesized causation remains I. Earlier calibration history is not erased.

All figures are deterministic seeded synthetic examples and are not out-of-sample claims about physical sensors, autonomous learning, or actual causal identification. The test threshold was designed before the synthetic held-out examples were inspected in this cartridge; the code and fixture construction remain public and transparent.

## Run

```bash
cd experiments/decoderintegrity001
python -m unittest -v test_decoderintegrity.py
python decoderintegrity.py
```

## Next research obligations

A rigorous future cartridge should add authenticated multi-source lineage, dependent-source modeling (e.g. correlated witnesses), delay-aware calibration, resets/review contracts, and matched-budget classical change-point tests (CUSUM, e-values, Bayesian online detection) across many prespecified seeds. **No autonomous retuning or operational action rights are granted by this result.**

### Mathematical ancestry

Owner-authored `nunuMATH — Foundations of Admissive and Relational Mathematics` (F/I/R admission, warrants, reopening, receipt history; Ch. 2, 8, 11, 13–14), `nuMATHELOLOGY` (decoder and carrier non-collapse), and the existing MOTIF branches cited above. This is a local engineering interpretation, not a proof of the new mathematical framework's minimality or superiority over established statistics.
