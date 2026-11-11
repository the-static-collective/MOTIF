# VOID-004 — Frozen heldout result (post-score report)

**Classification:** research HOLD; researcher-authored deterministic wave simulator, no independent-world validity or superiority over competent classical planning. The implementation and preregistration were committed to draft PR #291 before the 24-seed heldout evaluation. The original preregistration SHA-256 is `aaa0c573fa9c7e64a251c4f0b6d2e9fe4b3126863cedd03f6cf1ccb5d17aae72`; GitHub Actions verified the file byte-for-byte prior to scoring.

## Reproducibility

- Original green full Actions run: `https://github.com/the-static-collective/MOTIF/actions/runs/43081988873` (workflow `VOID-004 repeat-until-clear 24-wave fortress`, head `bc13a5700670809cb74514858504ae2fae6af660`).
- The 11 unit tests, 4 development cases × 4 policies, 24 heldout cases × 4 policies, integrity and authorization checks all passed. All 96 heldout policy cases ran in Python stdlib with the actual canonical repository MOTIF-003 module.
- Actual full source/event receipt artifact: `https://github.com/the-static-collective/MOTIF/actions/runs/43081988873/artifacts/13885790108` (archive artifact SHA256 `24ccc0a97b4901cddd08d5d6137760e9ee782725883a8ac5d63f40a12aa22844`).
- Per-report source seal `c9f350b8a6b4f3dfbc4646955b56672ba7cd672e7ea956411850f8fd7b1a5cfb` for full locally repeated, identical deterministic heldout output.

## Frozen 24-seed heldout outcome

| Policy | Clears within 10 | Clears within 14 | Mean attempts to first clear | Observed distribution |
|---|---:|---:|---:|---|
| MOTIF-003 iteration-aware | **24/24** | **24/24** | **9.04167** | 7 attempts: 1; 8: 4; 9: 12; 10: 7 |
| Classical iteration-aware (strong scoped comparator) | **24/24** | **24/24** | **9.04167** | Identical |
| Classical immediate sonar (short-horizon ablation) | **6/24** | **24/24** | **11.00000** | 10 attempts: 6; 11: 12; 12: 6 |
| Classical without cross-attempt memory (ablation) | **0/24** | **0/24** | **unfinished after 14** | Restricted score: 15 attempts per case |

- **Primary finding: exact tie.** For every one of the 24 heldout maps, MOTIF and the iteration-aware classical controller first cleared the fortress on exactly the same attempt. This does not establish MOTIF's superiority, special general intelligence, or learned optimal planning.
- **Experimentally useful mechanism:** retaining learned wave directions and selecting advance relay reconnaissance allowed both iteration-aware controllers to clear all 24 waves by ten attempts, compared with only six clears by ten for a deliberately short-horizon classical diagnostic. The absolute descriptive difference in mean attempts was 1.95833 (9.04167 vs 11). This is not evidence against a strong full-horizon classical policy—it tied MOTIF.
- The memoryless classical ablation repeated its initial defeat and never learned across resets; it was a mechanism control, not a strong comparator.
- Average prep movement for MOTIF and the strong classical arm was 13.5 across their attempts, compared to zero for the immediate sonar arm; wave-clear attempts are *not* a budget-adjusted total-cost comparison.
- Complete completion requires full 24 correct defended waves, not merely exploration, conjecture, code execution or a final assertion. Every actual defense/sonar/relay/reset observation carries a locally checked source seal.

## Example trace: seed 81001 (both iteration-aware controllers)

| Attempt | Relay scouted | Waves successfully defended before defeat | First breach |
|---|---|---:|---:|
| 1 | A | 1 | 2 |
| 2 | C | 3 | 4 |
| 3 | B | 11 | 12 |
| 4 | none (save sonar) | 14 | 15 |
| 5 | none | 16 | 17 |
| 6 | none | 18 | 19 |
| 7 | none | 20 | 21 |
| 8 | none | 22 | 23 |
| 9 | none | **24** | **none — cleared** |

This is exactly the intended retry behavior: feedback from failed defense becomes verified knowledge retained on the next reset; relay knowledge can be banked for future waves. Both strong controllers chose this same trajectory. A different hidden-wave mechanism or changing threats could invalidate learned memory; such regimes have not yet been tested.

## Scientific boundary

This is deliberately an **author-built deterministic source-owner sandbox**, not Crafter gameplay, not a live survival scenario, and not third-party independent evaluation. The fixed 24 hidden gate directions repeat identically on every attempt. The agent's public map includes relay wave-number coverage; each relay gives accurate true directions when visited. The gate schedule has no drifting or adversarial signals. Only the mathematical affordance module is native MOTIF code; all other controls and owner mechanics are researcher authored. SHA-256 proves local byte integrity, **not third-party authenticity**. No LLM calls, autonomous model retraining, real-person actions, real-world survival implications or trained general reasoning. The earlier 16-wave pilot motivated the 24-wave revision, openly documented in preregistration; the 24 heldout seeds were not used in that pilot.

## Next honest challenge

Unfamiliar source-owned wave patterns, drift or false relay reports, concurrent survival resources, action costs, and a genuinely strong dynamic-programming/POMDP iterative controller. Keep the 24 scored seeds development-only for all follow-ons. Report future negative results without rewriting this archive.
