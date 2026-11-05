# MOTIF-018 — THE QUESTION THAT MAY NOT BE WORTH ASKING

> How can an intelligence know **which measurement to ask for next** when instruments may be missing, the situation changes, and asking a question has a cost?

This is the exact question that baffled the development of MOTIF-017: refusing to extrapolate may discard useful evidence, yet the available physical witnesses are incomplete. **Our diagnostic could be wrong about which next question is useful.**

## Implemented research loop — genuine local changes, bounded influence

A new development-only loop modifies its **own question-choice cartridge** five times during one execution. Each revision changes the score function or available question grammar, evaluates candidates on previously observed real hydrology, prints a testable counterhypothesis, and records which question it selected. Code changes are **not** autonomously executed: the evolving part is a limited, JSON-serializable policy grammar. It can decide which available *question* has highest observed development value, rather than merely returning the longest route.

First and final question are explicit:
- Initial `QUESTION-0`: Is more input always beneficial if its acquisition is free?
- `QUESTION-1`: Does asking another sensor justify its cost in transparent research credits?
- `QUESTION-2`: Does the same question still pay when sensors may not answer?
- `QUESTION-3`: Does the answer survive temporal disagreement within development data?
- `QUESTION-4`: Should extra observations be conditional on known local behavior?

The question grammar is:
- Use latest downstream Mankato observation (no additional source).
- Use local downstream trend (known historical downstream information).
- Ask Blue Earth station for two historical origin-time points.
- Ask Le Sueur station for its origin-time points.
- Ask both (two additional sources).
- Ask Blue Earth or both only when downstream's already-known six-hour trend magnitude exceeds 3.5%.

Queries in this replay mean **hypothetical access to public station values** at the predicted issue-time, not actual financial charges or real-world instant sensor requests. All rates, eligibility, and absent answers are scored on the *full downstream base denominator*. If an upstream sensor does not have usable measurements, the question is counted unanswered, a declared opportunity credit is charged and the estimate falls back to persistence. Thus the loop cannot become "smart" by dropping inconvenient observations.

**Costs:** 3% of train-only persistence MAE per requested station, in `cfs-equivalent research credits`; unanswered questions carry an additional 2× penalty in the final scoring objective. A 30% penalty on first/second development-half error discrepancy discourages temporal instability. Those weights are arbitrary declared research hypotheses, **not** real economic costs, safety thresholds, calibrated flood risks or naturally optimal preferences.

## Source windows and test isolation

**Predeclare before any fetch:**
- Training: May 4–13, 2023 (three USGS continuous gauges)
- Development/revision: June 1–10, 2024 (same public station IDs)
- A separate, untouched by the loop, later year: **September 12–22, 2025**.

Run `develop` first, save `frozen.json` and its SHA256 fingerprint, and only then fetch the 2025 data to `challenge` the plan.

```sh
python3 -m unittest discover -s experiments/018 -p "test_*.py" -v
python3 experiments/018/question_loop.py develop --out-dir /tmp/motif018
python3 experiments/018/question_loop.py challenge --out-dir /tmp/motif018
```

GitHub CI performs this order and checks that no sealed event file existed before plan freeze. Offline reproduction works from the archived raw public JSON responses by supplying `--offline`. This is not actual telemetry replay: report transmission timestamps are not reconstructed, and historical values may be revised. The later 2025 selection is a *design-time* holdout not guaranteed to be independent of what the developer generally knew about rivers.

## Crucial experimental safeguards

- The loop's proposed strategies train on 2023 and revise their selection on 2024 only. The 2025 labels may score, but cannot modify the frozen policy. A separate test year is necessary because 017 already looked at June 2024 flood test labels.
- Every version shows which candidate won, its observed forecast MAE, extra source counts, unanswered counts, and normalized declared research utility. A lower utility with *changed weights* isn't a valid comparison across versions; compare each version's candidate against persistence under the *same* version's objective.
- The concept of a "next question" is testable only when an answer can be sourced and held-out compared. This is not proof of broad intelligence, general machine self-improvement, or a genuinely autonomous code-writing agent.
- No direct filesystem modification outside its selected output dir; no code exec; source hosts/USGS IDs fixed; max 5 revisions; no network writes; no public alerts, evacuation guidance, threat model predictions, or safety-relevant decisions.
- Live public data may be missing or revised; missingness can cause HOLD rather than a fabricated result. USGS continuous discharge is computed/derived and can be provisional.
- The model considers only real source-reported discharge and simple regression. Strong forecasting, physical models, hydrologic travel-time analysis, and original time-of-report availability must come before applying it.

## Success is a question, not a compliment

If a selected question improves heldout utility **and** absolute forecast error with a tolerable percentage of unanswered sensor requests, the next experiment is replication in a different future period with actual issue-time availability. If it loses, the result itself supplies a better question: which missing observations or regime assumptions broke the inferred value?

The loop can therefore return either a held policy candidate or a new discriminating question. It must not certify itself superior simply because it generated more ideas.

USGS modern OGC continuous API: https://api.waterdata.usgs.gov/docs/ogcapi/ .

## After test: learning to ask about answer availability (post-hoc only)

The initial real execution selected `ask_sueur` in all five development stages and observed a 2025 holdout improvement against downstream persistence. On the same 2025 holdout, the never-selected `ask_both` policy had a *lower* retrospective error, despite 81 missing Blue Earth answers. This is **not** evidence that we may change the selected policy after opening its heldout target labels. Instead, 018 now explicitly distinguishes **a hypothesis about the next question** from an admitted improved choice.

The new machine-readable field `posthoc_question_generation_only` can therefore identify a concrete follow-up: *is learning whether a sensor is available (before paying for its value) itself worth asking?* This availability-probe question must be developed on a new training/development block and evaluated against another event not already opened. The existing final frozen policy remains unchanged.

A "best model" computed after seeing test labels is **optimistic selection bias**, even if other candidates were originally predeclared. These values inform investigation only, never retroactive model ranking.
