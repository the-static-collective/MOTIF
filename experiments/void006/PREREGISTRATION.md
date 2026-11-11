# VOID-006 — Procedural Memory / Reflex Compilation — frozen protocol

**Frozen before method implementation and before evaluating the 20 designated test seeds.** Research HOLD. This is an explicitly authored deterministic fortress simulator; it is not a biological subconscious, an independently trained adversary, real-world survival, or a new RL theorem. The predecessor VOID-005 results and its 16 seeds are development history, not fresh evaluation data.

## Question

When repeated, verified defenses permit a policy to become automatic, can MOTIF compile a **source-witnessed, interruptible behavioral chunk** and spend less deliberative work than an equally informed classical controller while preserving or improving actual 24-wave survival under sparse adversarial drift and deceptive relay reports?

This directly tests the user's procedural-vs-deliberative hypothesis. Merely trusting old gates is not automatically evidence of learning a skill. The primary outcome remains actual repeated-game performance, not a self-reported feeling of intuition.

## Environment and source

- Exactly the inherited VOID-005 `DynamicOwner`, unchanged 24-wave environment, 14-attempt maximum, four relays, one battery per attempt, change events at cumulative successful defenses 14/55, three regimes `stable`, `reactive`, `reactive_deceptive`.
- Same source-pinned *original* MOTIF-003 affordance module and inherited VOID-005 evidence ledger.
- All policies receive identical declared possible changes, public epoch notices, relays, allowed action/observation primitives, and attempt budget; they have no access to the simulator's hidden per-wave direction schedule or evaluator-only change records.
- Each actual defense remains an individual simulator action and must produce a verified success/failure receipt; compilation never allows skipping an environmental transition.
- Each repeated run starts at the fortress hub, retaining only evidence/habit history; the game does not expose real-world permissions.

## Four prespecified policies

1. `muscle_compiled`: a bounded source-witnessed habit cache trained from verified successful `DEFEND` receipts only. At least **two independently attempted successful defenses of the same gate at a wave** establish a reflex candidate. Adjacent certified wave reactions form guarded chunks of length >=3. A chunk is a cached `wave -> gate` policy; it can propose the next primitive defense only for the matching wave and must be interrupted immediately on conflicting sonar/defense receipt. Historical information is provisional after epoch changes. A real source-confirmed contradictory defense invalidates the affected cached gate and any overlapping chunks. A fresh relay's unsupervised claim cannot overwrite a verified habit. It uses the same sparse source-drift and relay-selection scoring as the `classical_sparse` policy.
2. `classical_sparse`: **strong matched control** with the exact same source and wave-local reliability estimates and relay/sonar decisions, but it makes an explicit per-wave lookup from the evidential controller rather than executing a cached chunk. If its behavior ties `muscle_compiled`, claim only procedural cache / modeled computation benefits, **not better survival intelligence**.
3. `classical_voi`: inherits VOID-005's change-aware VOI controller and its coarse stale-confidence semantics, as a direct historical baseline.
4. `classical_stale`: inherits VOID-005's overly certain memorized gate controller, as a diagnostic unsafe-trust ablation, not a generally optimal strategy.

Both sparse methods use the same conservative *local* change model for historical owner-confirmed gates: one epoch difference -> 0.955 confidence, two or more -> at least 0.91; known current-epoch owner evidence -> 1.0, unconfirmed relay -> 0.70–0.86, unknown -> 0.25. The source-change epoch signals that *somewhere* may have changed, not that every older fact is false. This heuristic is authored, not learned Bayes or a calibrated posterior. A conflicting true sonar or actual defense overrides provisional history.

## Freeze, metrics, and validation

Development seeds: **61001, 61007, 61019, 61031** (can be inspected/tuned before heldout evaluation). New fixed heldout seeds: **96001 + 37*i, for i=0..19**, twenty new seeds, across three regimes and four controllers = **240 evaluation cases**. These are author-chosen seeds, not independently blinded.

**Primary outcome:** restricted attempt at first full 24-wave victory, failure through 14 scored 15, with paired `muscle_compiled - classical_sparse` and `muscle_compiled - classical_voi` differences by regime, alongside raw win counts by 10 and 14. Report ties and failures.

**Secondary outcomes:** `deliberative_gate_lookups`, verified cached reflex executions, compiled chunk executions, mean chunk length, sonar uses, invalidations and surprise-triggered interruptions, true positive and false positive change reactions, wrongly trusted relay claims, cumulative total attempts/defense actions. Deliberative lookup counts are an **instrumented policy-operation proxy**, not measured human cognitive effort, neural processing, or CPU timing. An uncompensated speed claim is forbidden. Historical receipts must be retained, hashes only attest local integrity.

**Predeclared falsifiers:** fabricated false relay cannot certify reflex; 1 success cannot certify habit; a contradicted wave must not silently continue a chunk; after a source epoch changes, other unchallenged habits remain provisional, not globally erased; no forgotten 24-wave failure masquerades as victory; identical seed and regime do not imply identical adaptive adversary timelines across policies. All arms must be run under the same source, regime, and permitted observations.

**No post-hoc test-set tuning.** If the experiment runs fail tests/CI, record the failure and repair transparently; separate confirmatory from regression scores. No model/LLM calls, no external actuators, no production deployment, no private data.
