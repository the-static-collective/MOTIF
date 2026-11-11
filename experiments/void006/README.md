# VOID-006 — Reflex Forge: verified muscle-memory analog for a changing fortress

**STACKED DRAFT / RESEARCH HOLD on VOID-005 PR #292.** User proposal: should a practiced defense become an automatically executable policy instead of requiring a fresh conscious wave-by-wave decision every time?

## Mechanism actually implemented

A source-evidenced `HabitBook` receives individual simulator receipts. Two actual **successful** defenses of the same wave with the same gate compile a reflex `wave -> gate`. Three or more adjacent compiled reflexes form an options-style behavioral chunk. This is **source-witnessed proceduralization**, NOT training neural motor circuits, and NOT genuinely subconscious cognition. The defender still issues an individual primitive action at every wave; it verifies the external return before any subsequent step. A conflicting true sonar/defense receipt invalidates the relevant reflex and breaks overlapping chunks. Validly sealed *false relay reports do not create muscle memory*.

Deliberative source memory remains separate. The `muscle_compiled` arm and `classical_sparse` arm get exactly the same local, explicitly heuristic uncertainty handling and the same conventional future-information relay selector. Their only intended difference is whether an eligible gate is executed from a cached reflex instead of looked up in the evidence model. `classical_voi` and `classical_stale` are unmodified predecessor policies, retained for attribution.

### 4 design distinctions

- **Declarative:** "Wave 7 was N in epoch 1, observed by an authoritative defense."
- **Procedural:** "At wave 7, use the source-witnessed N reflex until interrupted."
- **Automatic chunk:** "Waves 5–9 are a continuously monitored practiced sequence." A chunk is *never* a single external action that skips checking intermediate consequences.
- **Interrupt:** Unexpected defense failure, or a real conflicting sonar reading, immediately decompiles the affected action. Unchallenged neighboring habits are not erased merely because an epoch notice says one unknown gate somewhere may have changed.

## Reproduction

From the `experiment/void006-procedural-muscle-memory-20261111` research branch:

```bash
python -m unittest discover -s experiments/void006 -p 'test_*.py' -v
python experiments/void006/procedural.py --split development > void006-development.json
python experiments/void006/procedural.py --split heldout --full > void006-heldout.json
```

No external game package or model key needed. The workflow runs a pure Python simulation; this remains an author-coded reactive fortress with invented threat dynamics. It compares independent source-verified **game outcomes** (not self-judged success), and archives every heldout owner's action and defense receipt. All game wins mean 24 actually correct defenses within a run.

## Scientific protocol

The frozen method and test cohort are in [PREREGISTRATION.md](PREREGISTRATION.md), committed separately at `55afb93c38a9adc4cb142b8fd4444c1d02ff71e0` before implementation. The previously examined VOID-005 seeds are excluded. New 20-seed experiment is a **researcher-controlled out-of-sample** study, not externally administered blind evaluation.

**Primary:** paired restricted attempt-to-first-clear against (a) exact same sparse controller with no cached reflex and (b) old VOID-005 conventional VOI. **Secondary:** count actual deliberative gate lookups, verified automatic primitive actions, chunk participation, surprise invalidations, sonar uses, and failures. A reduction in an instrumented code-operation proxy is not a proof of faster wall-clock inference, human cognitive load, novel AI architecture or higher success probability.

The no-LLM procedural cache can eventually become an executable motif cartridge with `trigger/guard/action/check/abort/relearn`, but production/real-person use would require separate consent, isolation, authenticated evidence and review.
