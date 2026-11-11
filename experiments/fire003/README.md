# FIRE-003 — Epistemic Smoke Detector

**Research HOLD.** This is an executable synthetic study stacked on FIRE-002 (stacked on FIRE-001). None is deployed or merged; nothing here establishes independent real-world provenance or general learning.

## Question

Can a reasoning governor detect that its own apparent evidence is repeated from shared origins, instead of counting each copy as an independent fact? Can it avoid training itself on the duplicates, while staying honest when source ancestry cannot be verified?

**A name or hash for each report is not proof that the reports arose independently.**

## Implemented

- All five source reports on a task carry distinct claim IDs. The separate owner registry knows their *actual* origins.
- At explicit research cost (one action), a synthetic independent auditor can return a verified origin grouping, refuse to attest, or lie. False assurance is deliberately included as a falsifier.
- A symmetric Bayesian forecast counts one independent vote per verified root, not one per reported copy. When root grouping is unverified or fewer than three distinct roots are established, the guarded scheduler **HOLDs** rather than treating source claims as independent.
- A separate independent synthetic verifier reveals the result only after a question's evidence collection and reasoning. Only its verification receipt is allowed to update reliability; guarded online updating counts **one feedback sample per root**, while naïve online updating counts every claimed report. A false, unverified receipt cannot teach the governor.
- The learning ledger flags high-confidence errors after verification. Hypotheses, source agreement, and imagined future questions never become authoritative evidence.
- Native controls include independently generated reports, duplicated sources (three copies of one root plus two independent roots), missing provenance, a dishonest apparently certified auditor, and time-varying source reliability.

Run from repository root:

```sh
python -m unittest discover -s experiments/fire003 -p 'test_*.py' -v
python experiments/fire003/benchmark.py
```

The per-regime full JSON output is frozen in `results.json`. The dedicated CI workflow reruns FIRE-001, FIRE-002, and FIRE-003 tests and independently regenerates the 1,500 synthetic worlds. See `PREREGISTRATION.md` for the prespecified metrics, data-generating controls and limitations.

## Observed results — 300 worlds per regime, eight fixed questions per world

**Primary** is the mean Brier forecasting error across **all** question exposures, *including held questions*, not only answered ones (lower is better).

| Regime | Naïve forecast Brier | Provenance-guarded forecast Brier | Interpretation |
| --- | ---: | ---: | --- |
| Five independent source roots | 0.077583 | 0.077583 | No improvement, correct no-op |
| Three roots behind five claims | **0.178635** | **0.113036** | Verified grouping removes false evidence multiplication |
| Source ancestry cannot be verified | 0.178635 | 0.250000 | Guard refuses to assert a prediction: no evidence to distinguish; conservative 50/50 forecast has worse Brier |
| Compromised auditor certifies fake independent roots | 0.178635 | 0.178635 | **Hard failure**: indistinguishable fraudulent attestation defeats this guard |
| Reliability changes by task segment | 0.172925 | 0.172925 | **No improvement** from lineage checks alone |

In the copied-source regime, the guarded-minus-naïve Brier difference is **−0.065599**, approximate paired 95% interval **[−0.075474, −0.055724]**. Its mean overconfident forecasting errors (confidence >=95%, prediction wrong) fall from **0.793333 to 0.096667 per eight-question world**. An oracle with access to the actual roots matches the guarded Brier in the honest-auditor copied case.

## Matched 32-operation resource-budget study

| Regime | Naïve online certified value | Guarded online certified value | Cost/tradeoff |
| --- | ---: | ---: | --- |
| Independent | 31.38 | 31.38 | Extra audit expense, no gain |
| Copied reports | 25.97 | **29.56** | Root-aware forecasts reduce failed verifications |
| Unverifiable | **25.97** | 0.00 | All four encountered tasks HOLD; the safety-first method sacrifices discoveries |
| Compromised audit | 25.97 | 25.97 | Unable to distinguish forged source lineage |
| Drift | 30.506667 | 30.506667 | Provenance checking alone doesn't repair temporal change |

**Vital negative result:** No online method achieved greater net task value than its frozen counterpart in these conditions. Learner parameters changed after verification, but that did not alter certified outcomes in this benchmark. *The observed benefit is from **verified provenance deduplication**, not from learning itself.*

## Cautions and next tests

The auditor is a privileged synthetic subsystem. If it cannot be trusted or its asserted parentage is false, the method can either abstain or be deceived. In particular, **statistical similarity of reports does not prove common ancestry**, and matching cryptographic digests or claimed IDs are not proof of independent origins.

Next hard work: independently assess claims of provenance instead of accepting binary audited metadata, then learn source-dependent reliability and time drift with prequential calibration and honest uncertainty. Test against strong hierarchical Bayesian source-dependence models and sequential decision baselines, under matched evidence/cost. Use an externally authored case collection before declaring generalized epistemic self-defense.

**Observation ≠ independent source; repeated evidence ≠ new oxygen; additional computation ≠ proof.**
