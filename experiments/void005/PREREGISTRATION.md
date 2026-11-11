# VOID-005 — Learning Adversary: frozen protocol (2026-11-11)

**Research HOLD. Frozen before heldout evaluation.** VOID-004's 24-wave fortress always repeated identical attack directions. VOID-005 tests a defender with persistent historical memory against a fortress that changes in response to the defender's prior successful blocks. Its relay may also return internally sealed, but false, reports. This is a programmer-authored deterministic adversary, not a trained opponent, not a third-party benchmark, and not real-world survival.

## Source and mechanics

- Preserve the original public 11×9 VOID-004 maze, four relays, each providing three wave facts, 24 waves, one shared intelligence charge per attempt (relay OR live sonar), and a 14-attempt ceiling. One wrong defense ends an attempt and reveals the actual gate through a source-owned outcome receipt.
- Initial hidden wave directions generated from a new independent SHA256-derived fixture domain `void005-private`; no policy receives the hidden values, seed-to-gate table, or a privileged world state. The formula is an engineering fixture, not cryptographically secure secrecy.
- `stable`: no changes. `reactive`: when prior *cumulative successful defenses* cross 14, then 55, respectively rotate one previously hidden wave direction at the next attempt boundary, at most two single-wave changes. The engine reveals a version counter but not the changed wave. `reactive_deceptive`: same changes, plus a deliberately incorrect, locally resealed claim for one wave at any relay visited in attempts 1–5. A valid checksum proves integrity of a source claim, NOT that it is correct.
- Every policy may use the same observations, source version notices, public relay coverage, movement routes, action and time budget, defense feedback and read-only native MOTIF-003 interface. An attempted action is not a witnessed win; the gate defender's actual receipt is required.
- Trajectories influence when the adversary crosses its change thresholds. Identical seed across policies does not imply identical post-action enemy histories; report these differences.

## Controllers

1. `motif_native`: actually imports original canonical MOTIF-003 and proposes hypothetical new evidence-reading affordances; it scores them through the same conventional expected-survival/VOI calculation as classical plus **authored, bounded** novelty bonuses: 0.025 per new affordance and 0.01 per new skill fact. All modeled outcomes are PENCIL, not observed directions.
2. `classical_voi`: same time-stamped, reliability-aware evidence ledger and conventional expected-progress/discounted future-information evaluation, without the MOTIF affordance bonus. **Primary competitive control**. Not an exact globally optimal POMDP and not CPU-matched.
3. `classical_stale`: deliberately overconfident pre-shift memory with no recency penalty; diagnostic ablation ONLY. Fresh defense receipts can still correct its belief.

All ledgers preserve history, accept contradictory source claims as distinct observations, downgrade fallible relays after independently witnessed disagreement, and distinguish historical INK from present PENCIL. Epoch change does not imply every old claim is false.

## Evaluation frozen before heldout score

The four development seeds `51001, 51019, 51031, 51047` were examined for pure correctness and exploratory design calibration (including the novelty-value blend) before freezing this document. They are **NOT** confirmatory.

The fresh *heldout* population is **16 seeds** `93001 + 29*i`, for `i=0..15`, and 3 regimes × 3 policies = **144 independent policy cases**. These are researcher-chosen and not blind task-server benchmarks.

**Primary outcome:** restricted first-success attempt per seed/regime, treating failure through attempt 14 as **15**, and reporting for each regime separately the paired mean difference `motif_native − classical_voi` (lower is better). Secondary measures: clears by 10, clears by 14, contradiction detection, source epoch changes, false relay corrections, sonar cost and full defense traces. All wins must survive all 24 actual defenses. No post-hoc change to the primary metric, seed cohort, policy weights, or scoring. Publish losses, ties, failures and historical records without revision.

The experiment is intentionally a falsifier. Neither a source hash nor a relay attestation establishes ground truth. Nothing can deploy, contact external services, write to human resources, train a model, or claim artificial general intelligence.