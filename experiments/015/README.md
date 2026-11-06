# MOTIF-015 — Observation witness (PostHog-compatible, offline)

**Status: experimental / review-only. Not installed in JAR;VIS.** No PostHog credentials, network calls, SDK instrumentation, production events, personal data, or autonomous actions. This branch is a pure evaluator for *operator-provided synthetic or verified, consented aggregate cohort counts*. The included example is entirely synthetic.

## Why this exists

MOTIF needs to distinguish its **prediction** from a **reported observation** and both from a **confirmed real-world outcome**. This small cartridge compares a previously recorded predicted completion rate against a same-cohort PostHog funnel aggregate and produces a HOLD or human-review receipt. It deliberately refuses to use unrelated event totals as an inferred conversion funnel.

`reason -> propose (HOLD) -> human-approved activity -> independent observation -> review -> update (separate future step)`

No automatic learning, provider connection, action, notification, or writing to PostHog occurs. Neither a favorable comparison nor an alert establishes causation or field benefit.

## Contract

`observer.py` takes a JSON packet containing only:

- `source`: provider, opaque query reference, timezone-aware window and export timestamps; verified same-cohort / unique actors; explicit opt-in collection; packet contains no personal data; operator declares a source-query review.
- `prediction`: predeclared metric, anticipated completion fraction, minimal sample.
- `observation`: entry cohort size and completion count for those **same actors**, not unrelated event totals.

All keys are allowlisted, and invalid packets fail closed. Observations with no independent query review, a stale export (default >72 hours), or too little data return HOLD. Reviewed observations return REVIEW_DEPARTURE when the hypothesis lies outside an approximate Wilson 95% binomial interval, otherwise REVIEW_NO_DEPARTURE. This is **diagnostic only**, not a calibrated causal experiment or a sequentially corrected statistical test. Human impact remains unverified.

The data-quality check in the connected PostHog environment currently lists only its three native tables, all `editable: false` to this connection. Its schema shows **no recorded events in the most recent 30 days** (snapshot Nov 6, 2026), so there is no real observation to import. Don't call this live or claim that any user behavior has been measured.

## Reproduction

```bash
cd experiments/015
python -m unittest -v test_observer.py
python observer.py example-observation.json --now 2026-11-06T09:00:00Z
```

## Next independent gates

1. Review the exact opt-in instrumentation contract in `webZ` / JAR;VIS before adding any SDK. Consider suppressing session recordings and autocapture; ensure consent is actually collected and withdrawal honored.
2. Define and audit a PostHog **same-cohort funnel query**, counting unique eligible participants and the same measurement window. Check whether the source is trustworthy; `source_reviewed` is only an operator attestation, not cryptographic proof.
3. Freeze a prediction **before** observing a future cohort. Do not use this example's 0.70 prediction as if it was genuinely preregistered.
4. Export **only aggregate counts** to MOTIF. Keep the raw telemetry in PostHog, subject to retention and permission controls.
5. Compare to a baseline/control and independently collect voluntary confirmation of useful work before any impact claims. Expect selection bias, tiny samples, instrumentation gaps, and correlated observations.
6. Require human approval of *any* resulting experiment or deployment. No automatic changes across GitHub, Vercel, Supabase, or user communications.

## ONE THING 007 — bounded cross-repository handoff

The separate webZ draft PR #257 instruments exactly two events **after explicit per-visit opt-in**: `one_thing_quest_prepared` and `one_thing_return_prepared`. A random ephemeral ID represents one journey, not a distinct human being. The server remains disabled until separately provisioned and approved. No event content is imported into MOTIF.

Run PostHog's verified two-step **same-ID** funnel over a frozen future time window, then have an operator review the query, consent conditions, duplicates, and cohort definition. The aggregator must provide only two counts, a query reference, and window timestamps; do not substitute event totals. `webz_bridge.py` turns that operator-provided count-only input into a MOTIF-015 packet, using metric `self_report_preparation_rate`. It is an offline adapter, **not an API connection or a verified impact estimate**.

```sh
cd experiments/015
python -m unittest -v test_observer.py test_webz_bridge.py
python webz_bridge.py reviewed-aggregate.json --now 2026-11-06T09:00:00Z --expected-rate 0.4 --minimum-n 30
```

The example CLI filename is a placeholder for a future operator-reviewed aggregate. None exists in this PR. A report being prepared is not evidence of completed physical work; provider acceptance is not evidence the event was indexed; one UUID is not a unique person. `source_reviewed` is an explicit, fallible human declaration, not independently authenticated proof. Keep the result at HOLD/REVIEW and preserve source provenance.
