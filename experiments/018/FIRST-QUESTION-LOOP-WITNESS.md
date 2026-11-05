# MOTIF-018: The instrument asked whether asking is worth it

**First physical-source trial, November 5, 2026.** Source-owned instrument `experiments/018/question_loop.py`. The bounded reasoning loop and later heldout run actually executed with USGS published river reports. This is a retrospective instrument evaluating which optional measurements to acquire, not an autonomous agent with a newly learned hydrologic model.

**Real GitHub Actions run:** https://github.com/the-static-collective/MOTIF/actions/runs/42037444582

**Preserved first results:** [loop summary](evidence/first-live-loop-2026-11-05.json) and [locked-year test scores](evidence/first-heldout-2026-11-05.json). The full upstream USGS raw response evidence and model coefficients appear in the temporary GitHub Actions source artifact (retained 30 days), not in these summary cards.

## The baffling initial question

> How can an intelligence know which **additional question** is worth asking if the sensor that would answer might be silent precisely when it matters?

Previous experiments taught us that (1) a validation winner can lose later, (2) a cautious fallback can be worse than acting, and (3) missing river-gauge readings can bias the entire evaluation.

We therefore made an executable five-revision question-selection loop. It changed a bounded, JSON-declared **criterion for choosing what information to request**, not the Python program, model parameters or action permissions.

- QUESTION-0: Do added sources help even at zero imagined cost?
- QUESTION-1: What happens when each upstream stream carries an information credit cost?
- QUESTION-2: What happens when some questions go unanswered?
- QUESTION-3: Are gains stable across earlier/later halves of development?
- QUESTION-4: What if extra sources are asked only when the downstream local trend warrants it?

The loop fit conventional train-only regression models on May 2023 records; evaluated and revised policy *selection* on early June 2024 records; and froze the final policy before reading September 12–22, 2025 measurement outcomes. The frozen cartridge's SHA-256: `5c1e3842bb064faf5bf9bab90d00c561705615442fe47313cd9587a18afc615a`.

**The selected policy stayed `ask_sueur` across all five revisions.** This is important: the diagnostic's scoring rules changed, but the selected question did **not**. The loop must not claim discovery of a new policy for each revision.

## The 2025 source-backed physical outcome

The later-year challenge had **228 complete downstream Mankato target/history records**. Le Sueur historical origin features were available for all 228; Blue Earth origin features for only 147 (81 unavailable).

| Locked policy or posthoc alternative | Test MAE (cfs) | Declared research objective (cfs equivalents) | Unanswered upstream questions |
| --- | ---: | ---: | ---: |
| No extra sources: last downstream reading | 126.4364 | 133.0482 | 0 |
| **Frozen development winner: ask Le Sueur** | **109.2406** | **127.5870** | **0** |
| Local downstream trend only | 120.4527 | 125.4759 | 0 |
| Ask Blue Earth | 93.9311 | 121.3121 | 81 |
| Ask both rivers | **64.1931** | **115.8954** | 81 |

The chosen `ask_sueur` method beat the simplest downstream persistence by **17.1958 cfs MAE** (~13.6%) and **5.4612 cfs-equivalent** on the predeclared weighted objective for this later-year test. Under the fixed development cost scheme, it merits **HELD_CANDIDATE_NEEDS_MORE_EVENTS**, not automatic promotion. This is an observed retrospective comparison, not a time-of-issue real forecast.

The *posthoc* `ask_both` method produced a lower 2025 error (64.1931 cfs), **despite 81 unavailable Blue Earth replies**. That is a compelling new question, not evidence that we may switch to `ask_both` after inspecting the heldout answers. Doing that would leak test labels into policy selection and invalidate the next independent evaluation.

## The next best question produced by the counterexample

> **What if asking whether Blue Earth can answer is more valuable than immediately asking Blue Earth for its measurement?**

That changes the subject of intelligence from just *the data point* to *the availability and expected value of asking for it*.

A proposed next-generation strategy should independently test three avenues: (a) continue asking Le Sueur alone, (b) ask Blue Earth too when a separately observable, origin-time source-health signal says it is available, and (c) abstain or request a fresh sample when it is not. **A source-health probe has a cost and can itself be stale or wrong.** Every branch must carry explicit information/latency/inaction costs and keep all downstream target hours in the denominator.

To avoid optimistic selection bias, **freeze that new policy first and evaluate on another not-yet-used year/event.** The newly added post-test question diagnostic is explicitly marked `posthoc_question_generation_only`; it cannot change the selected 2025 model, and it does not rebrand the already-viewed 2025 labels as untouched.

## What we did not accomplish

- No open-ended autonomous source-code modification, self-training, novel physical hydrology, or proof of general intelligence.
- No prospective 2025 forecast was actually issued; source measurements and revisions were retrieved in 2026.
- Historical telemetry reporting delays, provisional rating changes, and official gauge completeness haven't been independently verified.
- The "cost of asking" is a declared **research utility proxy**, not actual money, flood damage, or a scientifically calibrated cost of non-action.
- Five predeclared revisions reused development observations, making them susceptible to development-data overfitting; the holdout matters.
- The 2025 test was already inspected by humans when writing the *posthoc next-question generator*; the extension is not a fresh independent accuracy result.

**Source boundary:** read-only USGS Modern OGC Continuous Values API (https://api.waterdata.usgs.gov/docs/ogcapi/). No public flood alerts, physical-world dispatch, autonomous admission or code execution.
