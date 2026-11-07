# FIR-001 — Before the Arrow

**Status:** experimental reasoning cartridge; local simulation only. This is a small executable implementation of the user-authored **nunuMATH** / **nuMATHELOLOGY** ideas, **not** a new foundation of mathematics and **not** a proof assistant.

## Purpose

Provide MOTIF with a typed, receipt-bearing gate between **proposal (I)**, **locally admitted fact (F)**, and **typed relation (R)**. No relation inherits truth from its endpoints. No finite computation proves a wider statement than its declared scope. A carrier switch suspends old admissions rather than transferring them silently. Rejected promotions leave a receipt. Path histories remain distinct even when endpoints agree.

The prototype also exposes `Crossing`, `compose` (typed interfaces), and `relation_between_transitions` (second-order comparison). **`same_mechanism` is always a proposal (I)** in this first version; matching invariant labels are screening signals, not independently validated mechanisms. No code or generator may turn a *proposed* relation into admitted truth without external warrant.

## Run

```bash
cd experiments/fir001
python -m unittest -v test_fir.py
```

Twelve tests adapt **nunuMATH Field Book 001 — Twelve Worlds Before the Arrow** into executable behavioral expectations: changed carriers; addressability without role; independent relation warrants; bounded computation; changed rings; failed universal promotion; nontrivial round trip; decoder collision; cardinal index vs mechanism; reification; compositional typing; self-ablation.

## Intentional limitations

- A `Warrant` records provenance and scope; it **does not verify proof objects** or authenticity of externally supplied evidence. Only the finite-computation scope mismatch is enforced directly.
- `Claim.scope` is an exact string contract, **not** a general logical implication checker; future versions should use typed domains and proof/SMT adapters.
- The caller supplies decoder functions. The engine stores the observation receipt but cannot establish a full decoder-refinement lattice.
- `change_carrier` conservatively reopens *all* claims instead of transporting proved invariant facts through verified maps.
- `same_index` records equality of labels; `same_mechanism` always remains an unadmitted hypothesis, even when invariant labels match.
- This does not yet wire into MOTIF's broader cartridge router, autonomous search, GitHub actions, or agent actuation.

## Sources and lineage

- **nuMATHELOLOGY — Second Edition**, Lemon Press LP-NM-002, chapters 1–10. Source in the owner's Google Drive.
- **nunuMath v0.2 — Primitive Corrections to First-Generation Mathelology**, especially sections 2, 5–10, 17, 19. Source in the owner's Google Drive.
- **nunuMATH — First Course in FIR Systems**, especially chapters 1–14. Source in the owner's Google Drive.
- **nunuMATH Field Book 001 — Twelve Worlds Before the Arrow**. Source in the owner's Google Drive.

This cartridge is a **local executable translation** of those sources, not an implementation claim on behalf of the original books. Future work: structured claims and typed warrants; proof checker; full 12-world evaluation against baseline; adversarial mutation tests; audited integration with MOTIF's inference and composition loops.