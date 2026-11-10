# GENIUS-004 empirical witness — first trial, including the failure

**Original CI:** GitHub Actions run 42771289347 (successful; 13 tests before the conservative self-critique gate). Research branch is a draft, not merged and not deployed.

The pre-future validation procedure selected:
- revise gap = 0.12
- release gap = 0.60
- ask margin = 0.00
- reframe when >=2 topics exhibit source-history conflict
- original frozen plan SHA-256 = 84a026196fd1ec2f45bd34fe96400243c531d627d5328f34c3dea5602017f0fb

**Mean costed Brier across 2 synthetic heldout seeds (lower better; deferral costs 0.25):**

| Scenario | HUMILITY | Strongest classical comparator | Comparator score | Result |
| --- | ---: | --- | ---: | --- |
| STABLE | 0.160799 | CUMULATIVE | **0.145221** | HUMILITY loses |
| ABRUPT reversal | 0.235809 | WINDOW4 | **0.219283** | HUMILITY loses |
| LOCAL topic reversal | 0.165150 | HEDGE | **0.159336** | HUMILITY loses |
| GRADUAL reversal | 0.263203 | GLOBAL | **0.251158** | HUMILITY loses |
| STABLE_NOISY | 0.282842 | GLOBAL | **0.249800** | HUMILITY loses |

The original 18-policy grid found an intuitive controller which was **not more effective than standard online methods**. This is an important negative result, not a success to advertise as superhuman metacognition.

**False evidence of a shift:** the naive rule flagged 253 and 270 events in two STABLE worlds (out of 711 public reports per world), plus 388 and 362 events in STABLE_NOISY. REFRA ME and REVISE can be triggered by random variation rather than genuine change. A fast reaction to recent evidence is not automatically intellectual humility.

### Explicit self-critique revision (post-hoc)

After those heldouts were inspected, a new **validation-only adoption guard** was added to GENIUS-004. This compares the candidate with *all* matched conventional arms across the predeclared training/validation worlds; the candidate can only earn a **proposal for further independent review** if it improves macro-average costed Brier by >0.005 and stays within 0.005 of its chosen classical comparator in every validation regime. Otherwise it returns RESEARCH_ONLY_NO_PROMOTION with the strongest validation classical fallback.

This extra rule was created **after examining the initial heldout results**, so it is a *post-hoc engineering correction* and is not an independently prespecified or blinded result. The old test worlds cannot be rebranded as new clean holdouts for the amended guard. Its value is a transparent refusal to silently install an underperforming experiment, not proof that MOTIF autonomously discovered a novel method.

The complete synthetic event receipts (forecasts before answers, source pointers, actions, misses, losses, coverage and withheld counts) are archived by CI; no real participants, private accounts, remote data, or external actions were involved.

### Succeeding research question

Can a calibrated, independent change detector (e.g. exact likelihood ratios / appropriately validated CUSUM or ADWIN) identify **genuine persistent shift without repeatedly mistaking stochastic noise for conceptual change**, while preserving opt-in and costed rejection? Require new externally authored problem families, strong preregistration, and public comparison against classical detectors and adaptive experts. The next viable move is not to increase the nameplate number of cognitive modes; it is to reduce error.
