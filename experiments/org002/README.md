# ORG-002 — THE IMPASSE FRONTIER
## When the institution itself becomes a changing constraint

**Research status:** Synthetic, local-only, **stacked on the unmerged ORG-001 draft**. The algorithm is ordinary critical-path scenario arithmetic with structured epistemic HOLDs. This is **not** an AI trained on shutdowns or proof of the motives, efficiency, or failure of a specific official or institution.

### Hypothesis

Institutions sometimes fail to deliver promptly because of resource shortage, legal limits, coordination difficulty, negotiated positions, veto points or unresolved evidence. Some actors openly condition consent on other decisions; this is a **documented bargaining position**, not proof of malicious intent. A useful coordinator needs to model all these mechanisms **without assuming they are morally equivalent**.

**Target:** "Time to verified beneficial outcome without bypassing legal/ethical boundaries," not the speed of politicians, number of organizational emails, or a score assigned to an institution.

### Why U.S. shutdowns are useful structural analogues (publicly documented, historical)

| Case | Documented chronology / structure | Mechanism MOTIF should distinguish | Grounded evidence |
| --- | --- | --- | --- |
| **FY2014 federal shutdown (2013)** | October 1–17, 2013; 16 **full** days without funding. The House attempted to attach provisions defunding/delaying ACA implementation to a continuing resolution; Senate rejected those provisions. | An appropriations vote coupled to a separate major policy condition; a recorded legislative strategy, not a determination of anyone's hidden motives. | CRS [Use of the Annual Appropriations Process to Block Implementation of the ACA](https://www.everycrsreport.com/reports/R44100.html); [House historical list](https://history.house.gov/Institution/Shutdown/Government-Shutdowns/). |
| **FY2019 partial shutdown (2018–19)** | December 22, 2018–January 25, 2019; 34 **full** days. Trump publicly conditioned reopening on border-wall funding while Democrats opposed the demand. | An explicit public bargaining condition interacting with a statutory appropriations deadline. | [Reuters Dec. 25, 2018](https://www.investing.com/news/politics-news/trump-says-partial-us-govt-shutdown-to-last-until-agreement-on-border-wall-1730519); [CRS funding gaps](https://www.everycrsreport.com/reports/RS20348.html). |
| **FY2026 government-wide shutdown (2025)** | October 1–November 12, 2025; 42 **full** days (43 calendar dates in some reporting). Democrats sought health-policy provisions, including extension of enhanced ACA subsidies, in funding negotiations; Republicans argued the subsidy discussion could follow a temporary funding extension. | Competing public negotiating positions; preserve both sides' documented claims rather than silently inferring an actor's hidden intent. | [FactCheck.org Oct. 1, 2025](https://www.factcheck.org/2025/10/lawmakers-health-care-government-shutdown-claims/); [CRS May 2026](https://www.everycrsreport.com/reports/RS20348.html). |
| **FY2026 DHS-specific funding gap (2026)** | February 14–April 30, 2026; 75 **full** days. Other appropriations had been funded separately. | A partial agency-specific disruption, **not** permission to model all government activity as stopped. | [CRS May 26, 2026](https://www.everycrsreport.com/reports/RS20348.html); [House history](https://history.house.gov/Institution/Shutdown/Government-Shutdowns/). |

**Key legal control:** Under the Antideficiency Act, unfunded agency operations generally must stop except where legally authorized to continue. An outside volunteer, private nonprofit, donor or digital agent cannot simply perform a restricted federal function, spend lapsed appropriations, impersonate an agency, or treat an entitlement as interchangeable with charity. Ask the competent entity for scope and authority. [GAO: Shutdowns/Lapses in Appropriations](https://www.gao.gov/legal/appropriations-law/lapses-in-appropriations); [CRS: Applying the Antideficiency Act (May 2026)](https://www.everycrsreport.com/reports/R48930.html).

**Observed impacts, not moral verdicts:** GAO documents delayed grants and contracts, interrupted services and higher management costs in earlier CR/shutdown episodes. CBO estimated $18B in delayed discretionary spending during the 2018–19 shutdown and that about $3B of real GDP would not be recovered (2019 dollars). These estimates concern distinct historical periods and should not be casually transported to 2026 or to a local volunteer event. [GAO-18-368T](https://www.gao.gov/products/gao-18-368t); [CBO 2019 summary](https://www.cbo.gov/publication/54943).

### Reusable failure mechanisms (NOT rankings of public officials or organizations)

1. **Veto-point coupling:** One resource or lawful authority is contingent on a separate contested proposition.
2. **Calendar cliff:** A previously authorized activity reaches an expiry date before renewed authority exists.
3. **Partial operating topology:** Some offices, budgets and legal exceptions remain active while others stop.
4. **Voluntary capacity shock:** A legitimate plan has too few people with time, appropriate consent or training.
5. **Ambiguous custody:** Nobody can reliably state who is able to make the next authorized decision.
6. **Strategic public condition:** A party explicitly states a condition for a decision; record the condition and its source, not an unobservable motive.
7. **Unverified explanation:** Several plausible causes compete; ask which observation discriminates among them.

Counterfactual response palette: **VERIFY_SCOPE**, **SEEK_EXPLICIT_DECISION**, **PREPARE_NO_COMMITMENT_MATERIAL**, **PARALLELIZE_INDEPENDENT_WORK**, **REQUEST_ALTERNATIVE_AUTHORIZED_ROUTE**, **RECHECK_ON_CHANGE**, **HOLD_FOR_LEGAL_OR_SAFETY_REVIEW**.

### Current local experiment

Run with Python 3.11+:

    cd experiments/org002
    python -m unittest -v test_resilience.py
    python resilience.py fictional-case.json

The case is **FICTIONAL_BASEMENT_SUPPER**, not a real shutdown and not a real church event. Funding delays are arbitrary test assumptions, not historical effect sizes:

| Condition | Synthetic time to meal |
| --- | ---: |
| Baseline original task path | 9 days |
| Fictional 21-day funding pause hitting budget dependency | 30 days |
| Independently resourced local meal route, conditional on review and consent | 5 days |
| Apparent contingent difference | 25 modeled days, **not saved in reality** |

Two negative controls:
- A nominally "local" route that actually still relies on paused grant funds is **INDEPENDENCE_UNVERIFIED**: no comparison or automatic recommendation.
- Handing out an information sheet instead of a needed meal is **NOT_COMPARABLE_DIFFERENT_BENEFIT**: no false equivalence.

The independent route has its own venue authorization and non-negotiable safety gate; the planner **does not authenticate either** and keeps all candidates at HOLD. No real person, church, application, government agency, resource or event is enrolled.

### Assumptions / epistemic conditions

- The source of the event and the political positions must be attributable and dated, but the public record cannot establish hidden intent. The strict fields for intent are ONLY: none, documented_public_position, documented_action, attributed_claim. "Malicious" is not an allowed inferred classification.
- A sourced position must not be mistaken for a statutory authority, a claim of legal exemption, or ground truth. The loader checks *presence* of source references, not the references' authenticity.
- All durations are hypothetical additional days. No probabilistic calibration, throughput estimate, legislative forecast, coalition prediction, or automatic legal interpretation is implemented.
- A graph route cannot be compared as a substitute if beneficiary benefit differs, it still uses affected funding, or the proposed safety/authority path is not explicit.
- Conditions should be tracked with two clocks: **institutional permission** and **human preparations that are independently permitted**. Neither clock overwrites the other.

### Field pilot protocol (needs real permission, not done here)

Choose **one** voluntary human outcome ("actual meal served" or "specific resource delivered") from a cooperating local team. In private, collect:
- One consenting steward who can confirm ownership and process scope.
- A dated, minimal, non-sensitive list of outstanding tasks, funding/permission requirements, and dependencies.
- A clear list of what may be prepared now without committing others or spending external money.
- A protected boundary list: food safety, insurance, child safety, privacy, permissions, participant opt-out.
- On each check: dated outcome receipt, actual elapsed time, burden shifted onto volunteers, and beneficiary confirmation.

Run ORG-001 without shocks first; then ORG-002 with two or three *stated* plausible shocks. Freeze projections before seeking real results. If no independently permitted alternate route exists, return HOLD rather than invent one.

Success metric: **verified service delivered**, with a shorter decision-to-benefit interval **and no decline in safeguards, quality, consent, or unpaid-work equity**. Compare against plain human scheduling and naive wait/until-reply; test on additional independently authored cases before calling the cartridge reusable.

### Proposed crosswise seams (not yet automatically connected)

- MOTIF-ORG002 extends MOTIF-ORG001's graph and evidence boundaries.
- JAR;VIS: an independent receiver may render *conditional* resilience questions and operator-only drafts; its existing ORG-001 receiver is not a native ORG-002 parser.
- planZ: multiple contingent plans with recheck triggers.
- ALEX.2: source and dated testimony packet rather than invented motive score.
- Project0 / reLATTE: claims, witnesses, permissions and consequences remain distinct; local admission after separate review.
- Garden/Porchlight: only a cooperating organization's own approved task, without publishing private contacts or implied agreement.
- GRAFT: only after independently validated transfer tests.

**What not to build:** an automation for coercing officials or counterparties, circumventing public funds controls, manipulating elections, inferring political ideology of individuals, or declaring an institution/official "bad" from a single dispute. Organizational resilience can be evaluated without such tactics.
