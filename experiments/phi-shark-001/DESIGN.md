# PHI SHARK 001 — Lucas inheritance

Status: bounded synthetic experiment; H1 remains open. Admission: none.

## Observe / hypothesize
The exact Lucas recurrence has roots phi and -1/phi. A pair of consecutive states is sufficient for reversible homogeneous growth. For vector states with innovations, x[t] = x[t-1] + x[t-2] + u[t]. Backward recovery requires the innovations, not merely the final pair. Hypothesis: where a chosen recurrence predicts a field well, retained residuals may permit economical exact replay. No assumption of special phi superiority.

## Probe / verify
Run `node experiments/phi-shark-001/experiment.js` and compare with receipt.json. Fixed seeded synthetic integer vectors (4 coordinates, 16 states, 40 cases per regime). Equal source histories for Lucas, constant-velocity second order, first-order delta, and snapshots. All four losslessly replay their own complete archives. Compare ASCII JSON lengths, not optimal compressed bytes. No real-world claims, hidden state, or external execution.

## Revise
Lucas wins on deliberately Lucas-shaped fixtures; linear wins on linear-shaped fixtures; raw snapshots win on both random-walk and independent fixtures. 800/800 round trips. Dropping a nonzero residual can generate a plausible but incorrect past. Single next state is ambiguous. Cassini is an exact scalar test, not an authentication mechanism. No evidence of special universal phi benefit. The controls were constructed for this experiment, not independently frozen real-world holdouts.

## Next
Use existing MOTIF-007 source-pinned operator inheritance and continuity-reentry branch as research neighbors, not imported dependencies. Compare residual-first replay on held-out typed graph histories with independently selected baselines and matched encoding budgets; include deletion, noninvertible projection, novel entities, contradictory observations, identity reassignments, and independently authenticated source receipts. Require exact ancestry, safe abstention, and genuinely new transferable operations as separate outcomes. Avoid publishing private historical evidence. No production activation or cross-project write.

Owner: MOTIF. Disposition: new narrow experimental remainder. Existing branch search found no phi/Lucas name; this is not exhaustive coverage. Evidence: experiment.js and receipt.json. Result: local V8 execution of the same experiment function; Node CI not run. Next: independent graph-domain evaluation. Admission: none.
