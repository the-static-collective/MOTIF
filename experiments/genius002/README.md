# MOTIF-GENIUS-002 — PERSPECTIVE WITHOUT ERASURE

**Status: Research HOLD.** Executable local prototype on a stacked draft branch; not merged, not an installed phone app, and not a deployed Trench-node network.

## Hypothesis

Exceptionally useful social understanding may consist partly in accurately representing another participant's **reported perspective** while preserving that participant's independent authority to disagree, correct the representation, withhold information, and refuse a joint plan.

This turns the Rasputin/Mister Rogers contrast in GENIUS-001 into a **bounded, falsifiable collective-reasoning protocol**, not a simulation of either historical individual's mind.

### Shoulders of giants, and caveats

- **Lu Hong and Scott E. Page (2004)**, *Groups of diverse problem solvers can outperform groups of high-ability problem solvers*, PNAS 101(46):16385–16389, DOI https://doi.org/10.1073/pnas.0403723101. Their mathematical claim depends on specified diversity and problem assumptions; it does not establish that arbitrary AI agents improve groups.
- **Anita Woolley et al. (2010)**, *Evidence for a collective intelligence factor in the performance of human groups*, Science 330(6004):686–688, DOI https://doi.org/10.1126/science.1193147. Human group performance correlated with social sensitivity and conversational turn-taking; this does not validate software modeling of people.

We separate **functional diversity of perspectives** from **the social protocol that allows those perspectives to contribute**. Neither is reducible to a majority vote, charismatic influence, or knowing another person's inner motives.

## Executable architecture

~~~text
Trench Node A -- local information -- explicit SHAREABLE projection ---.
Trench Node B -- local information -- explicit SHAREABLE projection ----+--> source-owned evidence ledger
Trench Node C -- local information -- explicit SHAREABLE projection ---'         |
                                                   reviewed crosswalks and unresolved disagreements
                                                                              |
                                                   guesses tested against targets' shared reports
                                                                              |
                                               NO / HOLD / YES_TO_DRAFT consent gate
                                                                              |
                                       candidate joint draft + questions + evidence receipts
                                                                              |
                                                   HUMAN REVIEW ONLY; NO EXTERNAL ACTION
~~~

**perspective.py** uses only Python's standard library.

- **NodeState:** distinct local assertions, owner-reported option positions, and hypotheses about other *public* positions; raw local state is never serialized as an exchange packet.
- **Claim:** owner, exact proposition, polarity, evidence pointer (not verification), and explicit shareability.
- **Vote:** YES_TO_DRAFT, NO, HOLD, and optionally a declared 0..3 ordinal utility. A required stakeholder's silence does not imply consent.
- **PerspectiveGuess:** test a shareable hypothesis about another node's position *only against that node's voluntary public response*. Results are correction receipts, not mind reading.
- **Crosswalk:** owner-reviewed local term mapping with limits. Similar words across nodes do not automatically merge. The review boolean is **unverified local attestation**, not cryptographic authority.
- **Proposal:** candidate draft with explicit stakeholders. Even all stakeholders saying YES_TO_DRAFT does **not** authorize execution.

Each claim stays source-owned. Opposite polarities about an *identical proposition*, under an explicitly reviewed common concept, remain **CONTESTED_NOT_ADJUDICATED**. Disagreement is not voted away.

### Classical planning, not a new genius algorithm

The finite selector enumerates consent-eligible drafts, maximizing the minimum self-reported utility, then their sum, then applying a fixed tie break. Those utilities are *declared*, not inferred welfare.

A deliberately weak control selects the **first majority-supported proposal**, allowing a minority's refusal to be overridden. In the synthetic example, the first option gets two YES responses and one explicit NO; the protocol instead selects a second all-YES option. **A strong exact consent-filtering and max-min baseline would select the same option as the protocol.** No new algorithm or performance advantage over that baseline is claimed.

### Adversarial tests

Ten synthetic tests cover: veto preservation; correction of inaccurate predictions about another node; contradiction with source retention; withholding private text, votes and evidence pointers; refusing unreviewed term alignment; honest HOLD with no acceptable option; no leaking a withheld target response; rejecting forged source ownership, duplicate votes and invalid utilities; never executing an all-YES draft; and ensuring five assertions from one participant do not count as five independent witnesses.

From the repository root:

~~~sh
python -m unittest discover -s experiments/genius002 -p 'test_*.py' -v
python experiments/genius002/perspective.py > /tmp/motif-genius002-demo.json
python -m json.tool /tmp/motif-genius002-demo.json >/dev/null
~~~

The public-only JSON includes packets, source-owned claims, unresolved disagreements, predicted-versus-self-reported perspectives, draft choices, the weak baseline, and follow-up questions. CI retains an inspectable copy.

## Next research steps / essential boundaries

1. **Authentication:** signed node identity, capability-scoped disclosure, withdrawal, replay protection and proof of who approved crosswalks. A boolean is NOT authorization.
2. **Independent perspective tests:** externally written situations, with blind predictions about other participants' *voluntarily shared* choices and independently defined scoring; include guessing and null baselines.
3. **Ontology drift:** distinguish different concepts sharing the same label; measure invalid mergers and missing but potentially meaningful translations.
4. **Manipulation/adversarial tests:** sycophancy, information cascades, one prolific source mimicking many sources, fraudulent evidence pointers, and performative agreement.
5. **Strong classical baselines:** exact consent filtering, Pareto frontier, max-min fairness, fairness trade-offs and impossible collective decisions.
6. **Frozen cross-domain evaluation:** compare on independent holdouts at matched tool/compute/evidence budgets and with external review.
7. **Authority:** keep sharing, permission to draft, and permission to execute completely separate. All execution requires fresh authenticated authorization outside this prototype.

The local toy cases are **engineer authored**. No social-scale validity, real-world collective intelligence, learned method selection, mind-reading capacity, or novel mathematics is established. Do not infer real people's motives, diagnoses, or worth from this model.

### Proposed Trench / MCP handoff — not implemented

A future service might expose non-executing tools analogous to submit_shareable_packet, compare_source_bound_perspectives, draft_joint_options, and request_human_review. These must accept public packets, **never raw NodeState**. No Trench phone app or remote MCP endpoint is modified by this research branch.

**Invariant:** mutual understanding without compulsory agreement or inherited authority.
