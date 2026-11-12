# RECIPROCAL-002 — Two Doors: Purpose-Gated Active Inquiry

**Research status:** working local-first web application, **not a deployed network, collective opinion survey, authenticated sampling system, human learning measurement, or autonomous outreach**. Built November 12, 2026; stacked on draft RECIPROCAL-001 (#322). The source-correctable previous experiment and the present two-door app remain distinct.

## The two actual doors

1. **Ask MOTIF** — A human states their question, why it matters, and which decision new evidence could change. To enter the inquiry queue, the card must include 2–5 distinct, bounded answers, volunteered source roles, relative priority, at least 2 claimed independent source roots, an absolute questioning deadline, and a hard maximum asking budget. Unstructured free-form language remains a separate, unimplemented language-understanding problem.
2. **Let MOTIF ask** — A visitor supplies a *local pseudonym* and voluntary role(s), actively opts in, and requests **one** question. MOTIF selects an eligible inquiry from current evidence gaps, the importance of the named decision, time remaining, and the participant's self-described experience. No automatic contact is made, and refusal is supported.

The person answering can label the basis of their statement (experience, observation, experiment, reasoning), share an optional short explanation, decline entirely, and explicitly revise their previous answer. Both earlier and revised observations remain in the inspectable event ledger. The visitor may see the current distribution; no option is promoted into established truth.

## Implemented decision engine

| User's question about MOTIF's asking | Executable answer |
|---|---|
| **Why ask?** | Every card must name a potentially changed decision. No utility, no admission to queue. |
| **Which question?** | Rank open, incomplete cards by declared importance, remaining independent-root gap, urgency and uncertainty. It is a **transparent authored classical heuristic**, not an AI-learned optimal policy. |
| **Who to ask?** | Only willing visitors who choose an applicable experience role. Do not infer an identity, vulnerable demographic, location or psychological type; do not contact anyone. |
| **When to ask?** | Explicit open/close dates plus live opt-in and incomplete evidence status. No background notifications or scheduled outreach. |
| **How long?** | Hard min/max independently claimed pseudonymous sources and 1–30 day windows. Stop early on reasonable evidence-convergence or irreducible disagreement, or HOLD at expiry/cap. |
| **How to compare?** | Count at most one current answer per *claimed source root*, preserve corrections and conflicts, retain distributions and method labels. The roots are **not authenticated**; a pseudonym is not proof of independent witnesses. |
| **What makes an answer useful?** | If there are enough roots, a dominant option (≥75%), enough voluntary role diversity, and no role conflict, mark **READY_FOR_REVIEW**, **not TRUE**. Mark **NEEDS_REFRAME** if disagreement remains severe after ~75% of the inquiry budget, instead of asking indefinitely. |
| **When is asking wrong?** | Never solicit without explicit participation, when the source already answered/declined, when the window is closed, the budget is exhausted, or source events are contested. |
| **How can someone leave?** | They can refuse without explanation; their local session can be erased. Exported files elsewhere are not controlled by erasing a device. |

### Important scientific caveats

- Decision-impact importance is **declared by the human**, not independently established by MOTIF. The scheduling heuristic is deliberately simple and cannot determine whether a stated question is objectively useful.
- Survey-style option counts can estimate *self-reported experience or preference*, but not externally verified causal or factual truth. Convergence only triggers human **review**, never automatic action.
- Different aliases are not necessarily different people; no authentication, no secure origin signatures, and no adversarial respondent protection. **Import files can be forged.** A fixed pseudonym prevents accidental double counting in a local exchange, not Sybil attacks.
- Role diversity is not necessarily representativeness. The system's role match is opt-in and categorical; no covert personalization, targeted invitations or hidden profiling.
- Some disagreement is evidence that the question is ill-posed, that participants inhabit different contexts, or that a better experiment is needed. REFRAME is a recommended next human decision, not a model-discovered correct semantic split.
- Confidence intervals, statistical power, causal validity, resource usage (CPU/tokens), conversational intent parsing, true independent human learning and improvement of MOTIF's reasoning algorithms **are not yet demonstrated**.
- No server, no live Supabase queue, no cross-device synchronization, no JAR;VIS integration, no automated social outreach. This static artifact is a **local-first demonstrator**, not a public production web app.
- Browser session by default; localStorage only with an explicit checkbox. Optional JSON export and manual import. The screen warns about sensitive information and external copies. This is a convenience boundary, not a secure encrypted vault.

## Reproduce and use

Open [app.html](app.html) next to [two_doors.js](two_doors.js) in a browser. The independent CI workflow compiles a **one-file HTML artifact** for mobile/offline use.

\`\`\`sh
node experiments/reciprocal-002/test_engine.cjs
\`\`\`

Example data are *author-created question cards with zero response records*. You can also create a question and answer it through the second door. To combine voluntary data from different devices, participants export JSON, then the organizer chooses to import those files. Imports are validated and deduplicated, while source independence still is not authenticated.

## Next falsification phases

1. **Meaningful question design:** Test independently written human questions. Measure how many cannot be fairly reduced to 2–5 options, whether explanations remain useful, and whether proposed clarification outperforms bad forced alternatives.
2. **Fair routing experiments:** Compare MOTIF's deterministic policy against transparent randomized scheduling, cost-aware classical active-learning policies, and stronger source-dependence-aware Bayesian strategies under identical evidence and participation budgets.
3. **Real learning, not clicks:** Integrate RECIPROCAL-001's pre/post teaching tests using consent-based, blinded, independent task families and delayed unaided probes; test whether people's reasoning ability improves *without* MOTIF.
4. **Volunteer question economy:** Only with reviewed consent, a deployed protected intake could allow true asynchronous cross-device participation, revocation, privacy-preserving aggregation and provenance checks. Storage/source authentication/permission policy must be designed before any public submission endpoint.
5. **Algorithmic growth:** Feed independently verified patterns into a separate, reviewed Reason Hypermap/Algorithm Foundry cartridge. No auto-install based on anonymous survey votes.

## Status boundary

This research PR is **draft and stacked**, not merged to \`main\`, not deployed, and not a claim of novel artificial general intelligence. It constitutes an executable proof of the two distinct doors and of reason-controlled *asking* in a tiny finite setting. Progress to actual machine and human reasoning improvement still requires independent tests.
