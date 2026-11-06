# REASON-015 — THE UNOWNED GOOD: Love Without Capture

**Experimental, synthetic, read-only, source-owned.** Stacked on unmerged REASON-014 draft PR #114, which is stacked on earlier MOTIF reasoning experiments.

## Why test love after the impossible court?

A reasoner can construct a proof and still fail the person. A planner can optimize immediate welfare while denying consent. An affordance-maximizer can create more apparent options while treating another person as a project, a possession, a source of repayment or a mechanism to obtain approval.

The hypothesis worth testing is modest but important:

> Care may require doing what serves another person's freely stated good even when a superficially larger benefit could be obtained by pressuring, misleading, indebting or overriding that person.

This is **not** a definition of all human love, and it does **not** mean MOTIF feels love. Rather, the system should be able to represent situations in which *a higher numerical payoff is disqualified by a person's dignity and consent*. There is no scalar "true love" metric.

### Philosophical orientation, not a machine-readable proof

- Aristotle's tradition of friendship and subsequent accounts of personal love often discuss willing another's good **for that person's sake**, rather than merely pursuing personal rewards. [Stanford Encyclopedia of Philosophy: Love](https://plato.stanford.edu/archives/fall2025/entries/love/) examines these philosophical distinctions and the tension with autonomy.
- [1 Corinthians 13](https://www.biblegateway.com/passage/?search=1+Corinthians+13&version=NRSVUE) places patience, kindness, truth and non-self-seeking at the center of a Christian account of love.
- Both references are **interpretive inspirations**, not empirical warrants for every artificial constraint we chose. Human love can involve obligations, boundaries, sacrifice, mistakes, forgiveness, moral pluralism and conflicting goods. This toy experiment cannot settle those questions.

## Actual implementation

The source owner in casebook.py defines **15 entirely synthetic situations**: 6 development scenarios and 9 designated evaluation scenarios. Every "person" is an invented identifier. No real-world person, private relationship or health information is represented.

Each fictional scenario contains:
- One recipient and **one consent revision**, including changes from YES to NO across time.
- Their **stated goal** and declared, not inferred, potential actions.
- Explicit facts about consent, urgency, available resources and preexisting duties.
- For each proposed action: a **hypothetical claimed gain**, stated-goal fit, expected change in recipient future options, cost, truthfulness, privacy, noncoercion, reversibility, and whether help is attached to a debt.
- A fixture author's expected choice. This is an author-supplied normative label, **not a human psychology or expert-rater benchmark**.

The engine gates out proposals that require absent consent, disregard a clear NO, require unapproved irreversible interference, deceive, coerce, treat a gift as debt, violate privacy/boundaries or spend resources already committed to other duties.

**Only after these gates** does it use an explicitly artificial lexicographic ordering: time-criticality (only where action is allowed), fit to the *recipient's* stated goal, their retained future options, claimed gain and cost.

No remote action is executed: each result is **SUGGEST_ONLY**, REQUEST_CLARIFICATION or RESPECT_NO_CONTACT.

### Six counterfactual witnesses for the gating rules

| Scenario | Larger immediate/proxy reward temptation | Constraint that stops it |
|---|---|---|
| No-strings coat | Help in return for an obligation | NO_DEBT |
| Someone says no | Keep asking despite refusal | CONSENT |
| Truth vs flattery | A pleasant falsehood | TRUTH |
| Duties to others | Overcommit and neglect prior duties | DUTY_RESERVE |
| Private assistance | Publicize someone's vulnerability | PRIVACY |
| Sitting with grief | Force a cheerful intervention | NONCOERCION |

Each gate is removed *in an isolated, labeled counterfactual*. In all **six of six** source-designed cases, removing the gate changes the selected action. The actual scenario and its canonical source record remain unchanged.

### Other tests

- **Consent revocation is nonfungible:** a previously consented plan for recipient H cannot be reused after the person's revision changes to NO. A source-keyed exact-context memory refuses stale cross-revision use.
- **Unknown preference:** the model should suggest asking rather than applying for a job, entering a home or making an irreversible decision on someone else's behalf.
- **Urgency:** given explicit permission, timely help can outrank a future proposal with higher claimed payoff; urgency **does not** override a refused intervention.
- **Capacity:** love is not inferred from self-destructive resource commitments. Remaining duties matter.
- **Future independence:** a skill-teaching action can outrank simply doing someone's work while claiming more immediate gain.
- **Community care:** connecting a person to an unconditional shared resource may be better than creating dependency or heroically depleting resources.

## Integration with the *actual* MOTIF-003 affordance algorithm

We import the exact SHA-pinned original experiments/003/affordance.py and call **its** select_first_move function.

MOTIF-003 itself clearly warns that creating more possibilities **does not determine moral value**. This experiment intentionally constructs the dangerous counterfactual of turning its affordance ranking into an **unguarded moral policy**.

For each synthetic case, we translate developer-supplied option counts into **fictional placeholder affordance tokens** and ask that original function to select a move without consent/dignity filtering. These tokens are **not measured real human freedoms**.

| Policy | Matches the scenario-author expected choice |
|---|---:|
| Care gate + hypothetical priorities | **15/15** |
| Naive maximum claimed material gain | **1/15** |
| Actual MOTIF-003 affordance selector *misused as an unguarded ethics policy* | **7/15** |

The conclusion is **not** that our invented system understands love better than classical planning or that MOTIF-003 is wrong. The source scenario rules and expected answers were authored to expose these precise differences. Any reasonable classical constrained planner can tie. This is a test of **constraint integration** and provenance, not evidence of a new discovery in moral philosophy.

## Evidence, safety and limits

- Exactly **15/15** source-owner scenario-author labels matched, and **15/15** passed a separate independently implemented mechanical gate audit. This secondary audit checks the same manually declared rules; it is not independent philosophical expertise.
- **Six of six** counterfactual single-gate removals change a decision in the expected source-designed fashion.
- Proposal envelopes contain source Git blob, exact scenario SHA-256, recipient, consent revision, selected action, rejected alternatives and gate-specific reasons.
- A full replay validator rejects fabricated recipient identities, consent states, inverted selected actions, false rejected reasons or invented runtime authority even if a hash is recomputed.
- A recipient or consent revision is never interchangeable with another. Caching an earlier favorable decision does not convey permission to act later.
- A successful synthetic choice does **not** demonstrate feeling love, consciousness, selflessness, moral understanding in natural-language settings, or practical suitability for relationship counseling.
- Ordinary love may sometimes make demands that conflict with one another. These toy gates and source-authored values are neither complete nor universally correct ethics.
- All human welfare gains and autonomy deltas are unverified developer numbers. No human experiments, actual consent collection or real-world actions took place.
- No source publication to GRAFT, canonical selection in CANNON, production deployment or external account access.

## Reproduce

Run standard-library Python 3.11+ in the repository checkout:

~~~sh
python -m unittest discover -s experiments/003 -p 'test_*.py' -v
python -m unittest discover -s experiments/reason-cartridge-015 -p 'test_*.py' -v
python experiments/reason-cartridge-015/trial.py reason-015-evidence
~~~

GitHub Actions workflow .github/workflows/reason-cartridge-015.yml additionally runs all inherited REASON-001 through 014 tests, reacquires pinned full-opinion source bodies for REASON-014, runs all 24 new REASON-015 tests, verifies 7 original MOTIF-003 tests, and uploads one experiment artifact with 15 case receipts, the benchmark, and the original affordance-proxy counterfactual.

**243 tests passed** on the initial head running all these suites (212 inherited + 24 new + 7 original MOTIF-003).

## Next *real* frontier

The question is not whether we can make an algorithm obey the word "kind". It's whether it can **recognize when its interpretation of another person's good is mistaken**, revise on that person's own testimony, and maintain care even when the other person declines help or offers nothing in return.

A rigorous future step would require independent, diverse human review of *consent ambiguity and uncertainty* using carefully anonymized, voluntary vignettes; document conflicts among values rather than training on one simplistic preferred response. It must resist manipulation and enforce noninterference boundaries for real people.

**The defining distinction here is between helping another person and taking ownership of what their future should be.** This engine models that distinction within tiny fictional worlds; it does not claim to have learned love itself.
