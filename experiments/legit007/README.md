# LEGIT-007 — THE ADVERSARIAL WITNESS

**November 6, 2026.** An experimental branch, not a production knowledge system.
**Status:** REVIEW / RESEARCH HOLD. No real-world source is authenticated, no
user or patient is classified, no audit or query is actually performed.

## The question

> Nine people repeat a finding. Two independent investigators disagree.
> What if the first nine reports came from the same erroneous original?

Counting messages treats nine repetitions as nine independent witnesses.
Counting **upstream origins** instead of impressions can change the answer.

This project uses existing MOTIF-013 ideas, particularly source accuracy
calibration, forwarded testimony and plug-in Bayesian inference, and extends
LEGIT-006's simple root deduplication to **multi-hop directed provenance
chains**. It then adds an **exact one-question value-of-information router**
that can compare the expected consequence of doing nothing with the cost
and expected consequence of a *hypothetical* independent synthetic audit.

No new statistical theory is claimed: this is finite classical Bayesian
evidence aggregation and a conventional decision-theoretic inspection plan.

## Actual implementation

- **provenance.py** — strict typed \`ROOT\`, \`COPY\`, and
  \`LINEAGE_UNKNOWN\` nodes. Reports can appear in any order; the solver
  traces arbitrary bounded copy chains back to original sources, detects
  cycles, edited copies, missing ancestors, conflicting aliases and repeated
  source roots. It counts one likelihood contribution per **declared**
  upstream origin. Unknown lineage or inconsistent records **HOLD** and
  propose **UNSENT** investigation of lineage/source records.
- **source reliability** — independently simulated adjudication counts are
  converted to Beta(2,2) posterior means. An empirically unreliable
  *synthetic* channel can have accuracy <50%; its report is then correctly
  inverted in the likelihood. Source-level independence is assumed
  conditional on hidden truth and not proven for real-world sources.
- **audit planning** — a calibrated hypothetical positive/negative test
  generates two posterior branches. For each candidate, compute
  \`audit price + expected minimum terminal loss\` and compare against
  immediate decision/error/abstention risk. No question or observation is
  dispatched. Exact one-step planning, not a learned metareasoning policy.
- **simulator.py** — 320 seeded worlds: \`COPY_SWARM\` (nine apparent
  positives from one root), \`DEEP_CHAIN\` (multi-hop forwards),
  \`CONTRARIAN\` (sources whose reports are anticorrelated with truth), and
  \`SPARSE\` (difficult low-information decisions). Separate hidden-world
  outcomes, adjudicated calibration and audit responses. Hidden truths and
  audit results **never enter** the router's public packet.
- **exact_reference.py** — an **independently written classical exact
  Bayes+one-step-audit solver**, reconstructing roots and exhaustive
  two-way audit contingencies without importing the candidate routing code.
  This is the strongest matched-baseline control. It is *expected to tie*,
  and failure to tie must fail the benchmark.
- **bridge_013.py** — calls the actual existing
  \`experiments/013/witness_model.py::_witness_likelihood\`, rather than
  copying its code, and checks the new provenance pipeline yields the
  same plug-in likelihood on unique upstream origins. This is a
  regression crosswire, **not an independent methodological control**.
- **benchmark.py** — compares raw-report majority, distinct-root majority,
  calibrated-root Bayes with no audit, candidate provenance router with
  simulated one-step audit, and independent exact Bayes plus matched audit.
  The researcher-chosen loss is 1 for a wrong final choice, 0 for a
  correct choice, 0.27 for abstaining, plus the audit price if chosen.

### Demonstration: 11 reports from only 3 sources

Nine reports support proposition TRUE, but eight are copies of a single
upstream TRUE claim. Two independent origins report FALSE. Actual declared
roots total **3**.

- Raw message majority: TRUE.
- Distinct-origin majority: FALSE.
- Source-calibrated conditional posterior: about **0.277** for TRUE.
- The router proposes an independent synthetic audit if the declared
  value-of-information exceeds its price; this **does not perform an audit**.
- These are synthetic *declarations* and generated conditional numbers,
  not a judgment about any public dispute.

### Frozen 320-case results

| Method | Mean realized loss |
|---|---:|
| Naive vote over all visible reports | 0.479187 |
| Majority vote over distinct upstream origins | 0.237750 |
| Calibrated independent origins, no new investigation | 0.203438 |
| Provenance router + allowed one-step synthetic audit | **0.176125** |
| **Independent exact classical Bayesian audit optimizer** | **0.176125** |

All five strategies receive the same public source reports and reference
assumptions. The simulator reveals audit results only to the **evaluation**
once a proposed query is frozen; no actual operation takes place.

The 320 cases were constructed by this assistant. They are **not an
independent external blind challenge**, and the apparent gains over raw
majority are partly due to the deliberately adversarial copied-source
distribution. Do not extrapolate numerical gains into the real world.

The exact classical reference **ties the candidate exactly**, so no
inference superiority is demonstrated. The meaningful *integration* is
strict source-lineage checking + cost-sensitive audit planning, now
crosswired to prior MOTIF-013 witness likelihood behavior.

### An intentionally retained serious failure

If an adversary **lies about the source lineage** and rebrands one copied
report as an independently originated report, the current algorithm's
posterior *changes*. Without cryptographically authenticated origin
identities, an immutable witness record, or an independent custody proof,
there is no way to certify the edges from their self-reported identifiers.

The test suite demonstrates this weakness rather than pretending it was
solved. This is an important unsolved engineering frontier.

### Reproduce

From the repo root using Python 3.11:

\`\`\`bash
python -m unittest discover -s experiments/legit007 -p 'test_*.py' -v
python experiments/legit007/bridge_013.py
python experiments/legit007/benchmark.py
\`\`\`

Dedicated GitHub Actions archives source-regression and entire
synthetic-evaluation JSON receipts under a research HOLD. No secrets,
API/network calls, simulated audit execution or operational authorization.

### Next genuinely independent gate

Freeze a third-party-authored set of **raw source documents and custody
links**, containing deliberate quotations, unattributed copying, conflicting
timestamps and misrepresented provenance. The evidence compiler must
distinguish lineage it can attest from merely *claimed* lineage. Match a
conventional provenance graph solver plus calibrated Bayesian audit policy.
Score error, coverage, cost, adversarial spoofing, ability to decline and
actual audited-source attribution. Do not infer independence from a new URL,
different filename or copied language alone.

Until externally verified provenance and calibration are demonstrated:
**RESEARCH HOLD, not a trusted witness engine.**
