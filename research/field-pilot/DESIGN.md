# FIELD-001 — THE FIRST REAL WITNESS
## From hypothetical cooperation to prospectively recorded field observations

**Status:** offline operator-led research pilot. Runnable, tested, not deployed
as a public exchange, not a verified matchmaking service, and not a causal
learning system. No real individuals or offerings have been supplied by MOTIF.

### The research question

BRIDGE-001 can invent recipient-specific hypothetical cooperation moves and
regenerate those moves as a fictional world's capabilities change. The next
boundary is **actual observation**.

A simulator may know hidden truths. A field system does not. It must preserve
what was reported, what was proposed, what was attempted, what was later
reported to have happened, and what remains unanswered.

FIELD-001 deliberately does not apply BRIDGE-001's imagined permissions or
resource capacities to a real person. Its real-world adapter instead makes
the smallest warranted suggestion:

> An unexpired OFFER and NEED share an exact topic and broad area. The
> operator reports that both owners allowed their record to be considered
> for introduction. **Ask both again directly** whether an introduction is
> currently wanted, safe and possible.

No actual agreement, availability or successful exchange is inferred.

### Working operator flow

1. Open Field Witness offline. It starts with an **empty** log.
2. Enter a real offer or need using a pseudonym, short matching topic,
   broad area, expiry, reporting origin, and optional short note.
3. Explicitly mark whether the person *reportedly* allowed that card to
   be considered for introduction. Unverified third-party information
   cannot claim sharing permission.
4. Once complementary cards exist, the browser generates a proposed
   pair. The model only uses exact topic + broad area (a classical
   matching baseline), record freshness, different aliases and reported
   willingness from both card owners.
5. **Before contacting anybody**, choose **Record prospective candidate**.
   This freezes a candidate ID and timestamp in the append-only field
   log. It is rejected if outcome reports for the same pair already exist.
6. Prepare an introduction draft for **manual operator review only**.
   No phone, email, web request, notification or contact information is
   exchanged automatically.
7. After a real conversation or event, the operator can append distinct
   reports: provider says yes/no, requester says yes/no, handoff reported,
   benefit reported, no benefit reported, or outcome unknown.
8. Export the JSON log explicitly. Import it later to continue the
   journal. There is no automatic saving to a server or browser storage.

A withdrawn card is represented by an additional report; its original
entry is not erased or revised. Expired pairs can still receive later
follow-up reports. Timestamps use the local device clock and are not
authoritative time attestations.

### Actual measurement boundary

The pilot counts candidate pairings, prospective proposal records,
reported follow-ups, handoffs, benefit reports, no-benefit reports and
unknown reports.

These counts **do not** measure causal impact or the success of a proposed
intervention. There is no counterfactual comparison, independent
verification, authenticated reporter identity, or randomized assignment.
No response is not treated as failure. Conflicting benefit and no-benefit
reports remain conflicting.

The suggestions are **not** calibrated AI predictions: they are
deterministic equal-tag/equal-area matches. A performance claim requires
independent outcome evidence, baseline comparison and missingness
accounting.

### Privacy and consent

- Use aliases and broad areas; avoid full names, street addresses, phone
  numbers, medical details, children, personal secrets and sensitive data.
- The file contains whatever the operator types and is **unencrypted**.
  It lives only in browser memory until explicit plaintext JSON export.
  Do not hand it to third parties without participant permission.
- A share flag means *reported willingness to be considered for an
  introduction*, **not** verified ongoing authorization to contact or
  share personal details.
- A third-party report can be retained as context, but cannot establish
  sharing permission or become a match.
- A pair of reported yes responses remains explicitly unverified.
- Every real-world handoff requires direct confirmation of consent,
  safety, timing, suitability, cost and relevant local rules.

### What's coded

- **field_protocol.py**: size-bounded typed field-log validator, append-only
  chronology, expiring card matcher and noncausal summaries.
- **field_pilot.js**: equivalent local browser matcher and validator.
- **field_app.js**: intake, manual drafts, prospective proposal freeze,
  reports, withdrawals, export/import and fictional example.
- **build_field_desk.py**: single HTML document with all code embedded,
  no external dependencies or automatic network calls.
- **Tests:** expiry, areas, refused sharing, hearsay, withdrawal,
  contradictory outcomes, proposal timing, postdiction refusal, and
  no consent or causal promotion.

Dogram continues to calculate bounded hypothetical differences through
BRIDGE-001; FIELD-001 does **not** upload real reports to Dogram, MEMENTO,
3rdi, ALEX, Free Graph, GitHub, Supabase or any other service.

### Reproduce

In research/field-pilot:

    python -m unittest -v test_field_protocol.py test_build_field_desk.py
    node --check field_pilot.js
    node --check field_app.js
    node test_field_pilot.js
    python build_field_desk.py --output field-witness.html

Open the generated HTML in a browser. To analyze an **exported** local
field log without uploading any data:

    python field_protocol.py /path/to/exported-log.json --as-of 2026-11-05T02:00:00Z

GitHub Actions builds a downloadable motif-field-witness-offline artifact
containing only static application code, **not actual field data**.

### Where empirical research starts

A properly consented first trial could be simple: separately record one
genuine offer and one genuine need, freeze the proposed introduction
**before** contacting either person, ask both people directly whether
they agree to an introduction, and record what actually gets reported
afterward—or explicitly mark the result unknown.

Successful code execution is not a successful field trial. Until real
participants supply observations, there are **zero empirical encounters**,
benefits or demonstrated causal effects.

Next benchmark: compare more complex, auditable cooperation proposals
against the simple exact-match baseline under identical consent, time,
cost and prospective recording requirements.

**Reality must enter as a witness, not as a simulator pretending to know.**
