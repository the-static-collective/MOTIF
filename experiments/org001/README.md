# ORG-001 — The Waiting Room: throughput of help

**Question:** Can MOTIF reduce the time between an organization's good intention and a real, verified benefit *without treating a human being, safeguard, or consent requirement as disposable friction?*

**Status:** Local-only deterministic research specimen. Human-authored, synthetic scenario. No connected organizations or records have been assessed, no real outcome has been predicted, and no action or cross-repository import has occurred. This is not a general organizational performance score.

## Why

Ordinary project tools ask "Who is doing what?" ORG-001 instead asks "What is preventing the intended benefit from occurring, what can be done under whose authority, and which change would actually shorten the time until it occurs?"

Busy activity is not delivery. Waiting and approvals can be genuine system constraints, but apparent delays may also be rightful consent, care, safety, staffing limits, privacy, or regulatory obligations. The planner must distinguish these before proposing a change.

### A conversational operator workflow

1. **Name one actual outcome and beneficiary** ("A meal is served," not "the committee meets").
2. **Make one local, consented field snapshot.** What is done, in progress, waiting, unknown? Record dated source references, dependency edges, the owner of each decision, explicit boundaries, and estimated *remaining* days. Never infer that an organization or person agreed merely because they were mentioned.
3. **Ask MOTIF to reveal the real limiting path.** Estimate end-to-end time from a directed acyclic step graph. Separately show work-in-progress, recorded past waiting, bottleneck categories, missing ownership, and stale or unverified claims.
4. **Invent competing moves.** Include (a) ask for one specific yes/no, (b) prepare whatever can legally proceed independently, (c) recruit voluntary capacity, (d) seek a separately authorized alternate route, (e) preserve a non-negotiable safeguard. Each move is a *hypothesis*, with evidence required to verify it.
5. **Try the moves in pencil.** Recompute the critical path under each declared change. The question is *not* "Which activity became faster?" but "Did the modeled benefit arrive sooner?" The bottleneck may shift. Couple independent moves if their joint effect is larger. Reject shortcuts that zero out a non-negotiable gate.
6. **Produce reviewable cards.** A MOTIF card may go to JAR;VIS, planZ, or reLATTE only as a LOCAL/HOLD draft. A receiver must separately assess provenance, privacy, authorization, disclosure and admission. No automatic email, organization CRM change, ticket, resource commitment, or Garden post.
7. **Return with real receipts.** On the next observation, distinguish: requested action, reported action, independently accepted result, refusal, disappearance, and genuine field result. Compare outcome time and human burden with the prior plan. Do not celebrate "days saved" until actual benefit is witnessed.

## Executable local slice

Python 3.11+; standard library only:

    cd experiments/org001
    python -m unittest -v test_flow.py
    python flow.py example.json

The JSON example is **FICTIONAL_BASEMENT_SUPPER** with six steps and four intervention hypotheses. No names or live relationships are represented. The timeline is hypothetical. A local reviewer must enter their own future estimates; these are neither independent evidence nor calibrated causal forecasts.

### Demonstration (deterministic arithmetic, *not* observed time savings)

| Candidate | Assumed remaining-time edits | Modeled end-to-end days saved |
| --- | --- | ---: |
| Seek explicit budget answer | Budget 6 → 2 | 4 |
| Recruit volunteers alone | Volunteers 4 → 1 | 0 |
| Budget + food preparation + volunteers | Budget 6 → 2; food 2 → 1; volunteers 4 → 1 | 5 |
| Ask to expedite safeguarding review | Safeguarding 3 → 2, without bypass | 0 |

Baseline is 9 hypothetical days to meal. "Saving 0" does not mean a person's participation is worthless: it means the *modeled current limiting path* is elsewhere. Neither action nor outcome occurs merely because the calculator emitted a number.

The tool returns an explicit provenance separation: recorded inputs, derived critical-path math, conditional intervention hypotheses, verification gaps and HOLD-only handoff drafts. It declines cyclic graphs, unknown dependencies, historically overwritten completed work, and interventions that model removal of mandatory gates. No unattended external process is called.

## Crosswise interfaces — proposed, NOT connected

| Owner | Proposed local crossing | What the crossing must never claim |
| --- | --- | --- |
| **MOTIF** | Diagnosis, alternative hypotheses, critical-path counterfactuals, recheck triggers | That a projection is a verified outcome or that a person is obstructive |
| **JAR;VIS** | Operator-facing "What can I prepare now?" card, consented follow-up draft | That a card sends messages, confers roles, or approves spending |
| **planZ** | Maintain multiple contingent routes and expiry triggers | That a plan is authorized to run |
| **reLATTE** | Carry a locally reviewed attributed proposal and eventual separately verified receipt | That transported testimony equals locally admitted fact |
| **Project0** | Preserve typed relations: source / claim / interpretation / permission / receipt | That a source, signature, or recipient grants universal authority |
| **Garden / BananaSpork Porchlight** | Optional partner-desk or Help Slip view where adopted by that owner | That organizations or individuals have enrolled automatically |
| **GRAFT** | Candidate reusable "organizational lag" cartridge after independent review | That a single fictional example validates generalized performance |
| **ALEX.2** | Evidence packet for historical delay assumptions and subsequent observations | That rephrasing the same claim creates independent confirmation |

No runtime imports or HTTP endpoints are established by the current implementation. Crossing contracts must be negotiated with the receiving project's own APIs, privacy policy and human steward. A no-response route is never an approval route. A private intake should never be published as an example without consent.

## Future experimental falsifiers

- **Baseline**: compare with simple FIFO follow-up, earliest-due-date, ordinary Kanban WIP limits, and classical critical-path scheduling on externally-authored, consented cases. ORG-001 is currently a classical critical-path prototype, **not** a newly invented optimization algorithm.
- **Truth gap**: freeze projected gains, then collect dated outcomes and record prediction error, service quality, volunteer fatigue, participant consent, safety failures, and beneficiary-perceived value.
- **Noncooperation**: silence, refusal, ambiguous authority and partially completed commitments must retain HOLD and permit a genuinely independent, lawful alternative if one exists.
- **Queueing**: add arrival rate, throughput, WIP and aging only when a stable, comparable observation window exists. Little's Law is not a causal shortcut for nonstationary one-off events.
- **Self-revision**: adapt a suggestion strategy only after independent outcome receipts. Preserve unsuccessful trials and compare against elementary baselines.
- **Cross-organizational fairness**: evaluate whether the optimization helps recipients rather than shifting workload, excluding harder cases, or increasing uncompensated labor.

## Sources informing the *design*, not proof of this implementation

- [Kanban Guide, May 2025](https://kanbanguides.org/the-kanban-guide/2025.5/pdf/kanban-guide.v2025.5.en.pdf): explicit definition of workflow, WIP policies and service-level expectations.
- [Scrum.org — Kanban Guide for Scrum Teams](https://www.scrum.org/resources/online-kanban-guide-scrum-teams): WIP, age, cycle time, throughput and Little's Law.
- [GovWebworks — Applying Theory of Constraints, June 2025](https://www.govwebworks.com/2025/06/30/applying-theory-of-constraints/): focus on the actual system constraint; avoid reducing human capacity to machine utilization.

**Boundary:** This is a tool for the concerned people to make their own cooperation more legible and effective, not a way to pressure unconsenting organizations or rank people by "efficiency."