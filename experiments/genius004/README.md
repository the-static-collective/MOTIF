# MOTIF GENIUS-004 — THE HUMILITY APERTURE

**RESEARCH HOLD.** Experimental code stacked on GENIUS-003 (itself unmerged). No live Trench nodes, MCP, phones, human participants, external actions, or recursive self-improvement claim.

## Why

GENIUS-003 showed: individualized predictions beat the global average on its stationary, synthetic population, then performed much worse under deliberately inverted preferences. Knowing yesterday's perspective can become actively misleading. This trial tests when a model should **RETAIN, REVISE, REFRAME, RELEASE, ASK, or HOLD** based only on observations already shared.

This is **epistemic routing**, not a simulation of genius or human minds.

## Shoulders of giants (not misattributed implementations)

- Page/CUSUM change detection inspired monitoring shifts in streaming evidence. The gap heuristic here is NOT Page–Hinkley, a formal change-point test, ADWIN, or a statistical significance guarantee. Background: https://doi.org/10.1016/j.jksuci.2021.11.006
- Selective prediction/reject-option learning motivates reporting accepted-case risk, coverage and cost of abstention together: https://pmc.ncbi.nlm.nih.gov/articles/PMC7785732/ . This prototype makes NO calibrated coverage or distribution-free risk claim.
- Brier's proper scoring rule (1950), DOI https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2, evaluates a forecast **before** its outcome is observed.
- Windowed estimates, exponential recency weighting, smoothed frequencies and multiplicative-weights expert portfolios are conventional algorithms. No new mathematical method is claimed.

## Operation grammar

| Action | Trigger | Actual outcome |
| --- | --- | --- |
| RETAIN | Recent and accumulated public observations approximately agree | Emit the cumulative estimate |
| REVISE | Recent four-report history diverges from cumulative estimate | Use four-report estimate |
| REFRAME | At least two topics for one synthetic node have conflicting recent histories | Use a predeclared short-memory, topic-specific representation |
| RELEASE | Large conflict between recent and cumulative evidence | Abstain with a nonzero review cost |
| ASK | Prediction unknown or equivocal **and explicit synthetic opt-in** | Return an optional clarifying question; send nothing |
| HOLD | Insufficient history and no opt-in | Refuse to invent another's belief |

These are **machine decisions about its own forecasts**, NOT judgments about human motivation or worth. REFRA ME is a prewritten model switch, not an autonomously invented ontology. RELEASE is forecast abstention, not removal of evidence. Consent to a draft or disclosure is not consent to external action.

## Benchmarked against strong classical controls

All methods see exactly the same past publicly shared per-node/topic binary self-reports:

- FROZEN training-only Beta-smoothed frequency.
- CUMULATIVE conventional always-updating frequency.
- WINDOW4 and WINDOW8 exact recent sliding histories.
- EWMA exponential recency-weighted model.
- HEDGE conventional online exponentiated-loss mixture of cumulative, window4, window8 and EWMA.
- GLOBAL cumulative global probability, but only if the specific node-topic is previously seen.
- HUMILITY finite policy selector over the same conventional methods.

A prediction is made **before** the current self-reported answer is revealed, then optionally corrected by that answer. Withheld reports are never read by the learner and private fields are stripped at the projection boundary. Unknown node-topic combinations abstain instead of being profiled.

Scoring uses mean Brier error over accepted responses AND overall costed Brier with **0.25 cost per abstention** (arbitrary prespecified simulation proxy, not calibrated real-world cost), plus coverage, action counts and stable-world false alarms. Abstaining on every problem does not get rewarded with zero loss.

## Training and future boundaries

The policy grammar is predeclared:
- REVISE gap: 0.12, 0.20, 0.30.
- RELEASE gap: 0.35, 0.48, 0.60.
- ASK margin: 0 or 0.06.
- REFRAME: >=2 context discrepancies.

18 candidate policies are compared by macro-average costed Brier on **10 training-only validation worlds**: 2 seeds 40401/40402 × 5 scenarios. The chosen policy and evaluation rules are SHA-256 frozen *before* materializing the 10 held-out synthetic worlds from seeds **40421/40422**.

The five scenarios: STABLE, ABRUPT inversion after round five, LOCAL safety-only inversion for selected nodes, GRADUAL inversion, and STABLE_NOISY (nonstationary-looking sample fluctuations from persistent near-50/50 preferences).

Each world has 12 simulated nodes × 4 topics, 18 training rounds and 16 chronological future rounds, plus an unseen visitor. Some events are deliberately unshared. The private simulator rates never reach a predictor.

The holdouts are **not independently authored or blinded**: a single engineer wrote the full generator and evaluation setup and knows the families. This is a meaningful guard against direct future-outcome tuning, not external validation. A test victory is conditional on these exact synthetic assumptions.

## Execute

From the repository root:

~~~sh
python -m unittest discover -s experiments/genius004 -p 'test_*.py' -v
python experiments/genius004/humility.py > /tmp/motif-genius004-trial.json
python -m json.tool /tmp/motif-genius004-trial.json > /dev/null
~~~

CI retains all synthetic event-level receipts: forecast (or HOLD), public self-report, source pointer, selected action, Brier cost and explicit pre-update status. No raw local observations or private notes enter output. Tests cover every action, privacy, replay prevention, unknown perspective, opt-in gating, temporal leakage and nonzero abstention penalty.

## Scientific limits and next steps

1. Compare **all** errors, costed Brier, coverage and false alarms to the strongest classical online arm, not merely the weak frozen control. If HEDGE or a sliding window wins, report the negative result.
2. Replace the elementary discrepancy rule with stronger Page–Hinkley, ADWIN or calibrated change detection and cost-aware selective prediction, implemented faithfully and tested prospectively.
3. Test independently authored and blinded datasets across different kinds of distribution shifts and new domains. Do not tune on these heldouts after opening results and still describe them as blind.
4. Authenticate the ownership of voluntary reports and approvals before connecting any real Trench node; add withdrawal, source evidence verification and noncoercive opt-in.
5. Investigate whether reframing can propose and verify a *new context representation* instead of merely choosing a prewritten classifier, again matched against conventional methods.

**Frontier:** can MOTIF recognize when acquired understanding is becoming an obstacle and select a better epistemic action *before* observing the next answer, without pretending to know someone else's mind?
