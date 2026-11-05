# WAKE SIGNAL 001 — Voluntary Agency Invitation Experiment

**Status:** self-contained local research prototype, not live outreach. Python standard library only. No notification API, contact search, surveillance, profiling, automatic follow-up or live matching.

## Question

For a **confirmed, genuinely useful opportunity**, do voluntary invitations emphasizing a tiny first step, an open-ended creative contribution, or a bounded self-directed role lead to different **operator-attested real-world actions**? Can invitations yield useful **unplanned** actions?

The unit of analysis is an *invitation opportunity*, **never the person's intrinsic intelligence, consciousness, character, value or permanent "online/AFK" state**. Silence is unknown. Nonparticipation is legitimate. "Two in ten thousand" is a metaphor, not an estimated population prevalence.

## The three arms

- **SMALL:** one low-effort concrete action.
- **CREATIVE:** suggest an unexpected improvement.
- **AUTONOMOUS:** volunteer to define and carry out a small, bounded piece.

All arms share the same opportunity title, context, opt-out language and verified underlying task. Invitation copy is generated deterministically from operator-authored actions. Randomized assignment is balanced over 100 slots (34/33/33), seeded and reproducible. The experiment does **not** pretend a "best" arm before observation.

## How to run a dry pilot

From the repository root:

    python -m unittest discover -s experiments/wake-signal -p 'test_*.py' -v
    python experiments/wake-signal/wake.py plan --out /tmp/wake-draft.json --title 'Fellowship welcome table (EXAMPLE)' --context 'Illustrative only; no event promise.' --small 'Would you set one chair?' --creative 'What is one unexpected way to welcome someone?' --autonomous 'Would you propose a ten-minute welcome task?' --count 100 --seed 2026
    python experiments/wake-signal/wake.py report --plan /tmp/wake-draft.json --events /tmp/wake-no-events.jsonl

The generated file contains 100 **draft messages**, NOT 100 real invitations. It stores **no recipients**. It makes no network requests. It does not transmit, deliver, observe or collect a response.

For a future, consented, real-world pilot, the operator must confirm the opportunity actually exists and rerun the same plan command with \`--verified-opportunity\` into a new file. **This flag is an operator assertion, not independent verification.** Offer invitations manually only through permitted channels to willing recipients; decide outside this software whether follow-up is appropriate. Do not post identifying data or unconfirmed needs.

The local event ledger requires explicitly recording contact permission before \`offered\`:

    python experiments/wake-signal/wake.py record --plan /tmp/wake-real.json --events /tmp/wake-events.jsonl --slot P001 --event offered --consent-confirmed
    python experiments/wake-signal/wake.py record --plan /tmp/wake-real.json --events /tmp/wake-events.jsonl --slot P001 --event replied
    python experiments/wake-signal/wake.py record --plan /tmp/wake-real.json --events /tmp/wake-events.jsonl --slot P001 --event action --attested --receipt R001
    python experiments/wake-signal/wake.py record --plan /tmp/wake-real.json --events /tmp/wake-events.jsonl --slot P001 --event novel_action --attested --receipt R002
    python experiments/wake-signal/wake.py report --plan /tmp/wake-real.json --events /tmp/wake-events.jsonl

Record \`declined\` or \`opted_out\` when appropriate; these are terminal dispositions. \`opted_out\` can be logged before any offer. Receipts are pseudonymous *references to separately held evidence*, not names, stories or personal data. **Never put people's contact details into the plan, events or receipts.** The event is operator-reported; it is not independently authenticated evidence of a completed activity. Protect local files accordingly.

## Predeclared interpretation

- **Primary:** per arm, count of invitations with an operator-attested useful action. Report ratio per actually offered invitation **descriptively**. If not all assigned invitations were offered, comparisons are selection-biased; the study marks \`offerings_complete=false\`.
- **Exploratory:** operator-attested unplanned action following a recorded action, and reply/decline/opt-out counts. The operator should use the same evidence standard across arms.
- **Missingness:** unoffered is *not sent*, no reply is *unknown*, no attestation is *unverified*; none establishes inactivity or deficit of agency.
- **No winner declaration:** 100 invitations across three arms is a feasibility pilot, likely underpowered for small effects. Effects may reflect channel, situation, timing, personal bandwidth, opportunity quality, and selection, not message wording.
- **No ranking people:** reporting is arm aggregate only; slots facilitate operational bookkeeping but no human profile, leader board or targeting algorithm is built.
- **No autonomy claim:** MOTIF drafts options; a human owns verification, contact permission, delivery, response interpretation and any follow-through.

## Falsification / failure tests

The test suite rejects: unconsented offering, offering an unverified draft, fake action without reply, action without receipt/attestation, duplicate transitions, post-opt-out follow-up, changed plan, corrupt event record, cross-campaign event mixing and unverified evidence. The report starts empty, with all absent responses unknown.

## Future integration boundary

An integration with Garden/Coalition/Fellowship could import **approved, source-owned opportunities**, not search for "awake" people. reLATTE may later carry explicitly authorized crossings and auditable dispositions. No matching, consent transport, notifications, networked ledger or live integration exists in this prototype. The next valid milestone is one human-reviewable invitation set and **actual consented observation**; only then can a new analysis claim any field result.
