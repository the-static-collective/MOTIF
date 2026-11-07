# CONTEXT-GATE-001 — MOTIF chooses a method for a fallibly observed world

**Status:** local synthetic research; no deployment, no general environment identification, no automatic code changes.

The prior `SELF-MIRROR-001` found a specialist that improved IID performance while regressing under changed rewards. This experiment asks a narrower, falsifiable question: **can a visible but unreliable observation justify selecting a different existing policy without seeing hidden world identity?**

## Executable contract

- **Declared world:** a two-regime synthetic task with the same action features (`immediate`, `new_affordances`, `reachable_after_first_move`) as `MOTIF-003`. Its hidden reward mechanism gives affordances a positive or negative marginal benefit. Observed `amber`/`blue` context tokens are noisy, opaque indicators. The policy interface receives *only* the observed token and proposed moves; it has no outcome labels or hidden-regime field.
- **Two frozen policies:** `BASE = Policy(0,0)` and the previously selected but not generally admissible `SELF-MIRROR-001` policy `SPECIALIST = Policy(2,1)`. No new policy weights are optimized here.
- **Finite learning:** use **training** outcomes to estimate conditional regret of each policy for each visible token. Choose small fixed support/gain thresholds on **validation**; freeze before opening `test` and `ood`.
- **Refusal:** unseen tokens, incomplete/truncated search, ambiguous/insufficient training evidence, or duplicate candidate identities do not choose an action. Holds count with a declared **20-unit penalty** so excluding hard cases cannot inflate reported performance.
- **Adversarial holdout:** invert the sensor while leaving the underlying task reward mechanism unchanged. This isolates a representation failure: the observation model becomes unreliable. An OOD failure is reported, never silently used to retune the gate.
- **FIR/mathal receipts:** the proposed gate is typed as **I** through the existing executable `FIR-001`/`MATHAL-001` code; an exact passing finite test may be recorded **F_LOCAL**, but no claim about new worlds or real people is promoted.
- **Strong controls:** globally fixed immediate and specialist policies; a privileged per-regime oracle **for offline comparison only**. The gate is a classical conditional lookup and makes no claim of architectural novelty.
- **Read-only MOTIF-003 adapter:** converts actual hypothetical action rows into `Move`s; returns a *proposal*, not an action/authority or a truth assignment. Observed context is a caller-supplied synthetic token, **not autonomously derived from the graph**. The new experiment does not modify `MOTIF-003` or the previously published self-mirror.

## Reproduce

```bash
cd experiments/contextgate001
python -m unittest -v test_contextgate.py
python contextgate.py
```

Requires Python 3.10+, standard library only, and the prerequisite stacked `experiments/fir001`, `experiments/mathal001`, and `experiments/selfmirror001` paths.

## Remaining frontier

The next challenge is not a bigger lookup: infer useful **typed structural** contexts from graph observations and track sensor reliability changes online, while preserving split isolation, rejection rights, provenance, and comparison against classical contextual bandits. This first gate **does not** achieve that.

## Source ancestry

`experiments/selfmirror001/selfmirror.py`; `experiments/003/affordance.py`; owner-authored *nunuMATH: First Course in FIR Systems* (declared worlds, decoder theory, receipts, hostile controls), *nuMATHELOLOGY* second edition. Earlier GitHub PRs are stacked and must not be mistaken for `main` integration.
