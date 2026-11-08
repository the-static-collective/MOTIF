# QC-009 — STREET SENSE / CONTINUITY UNDER INFRASTRUCTURE FAILURE

**Status:** RESEARCH_PREVIEW_ONLY. Stacked experimental branch following [QC-008 #200](https://github.com/the-static-collective/MOTIF/pull/200). No production deployment, no service contacts, no stored real individuals, no use of device GPS, no verified live local resources, no actual survival outcomes. The only scenes are researcher-authored synthetic conditions. The code is a constrained scenario engine, not a safety-certified field assistant.

## The user's correction

A competent real-world reasoning agent must be **street smart**, not only institution-smart. Human beings, including people who live without stable housing, sustain complex adaptive knowledge about exposure, location, relationships, informal and formal sources of help, timing, conserving limited resources and rebuilding a route when normal infrastructure fails. The agent should learn from voluntarily supplied first-person knowledge and repeatable external evidence, not portray people as passive recipients of institutional service referrals.

**Institutional infrastructure can be valuable while being too slow, closed, unavailable, unreachable or unreliable to answer an immediate need.**

The desired structure is:

```text
NEED / RISK + PHYSICAL FIELD
    |
    +-- self-care and on-site observation
    +-- actually available supplies and weather protection
    +-- physically reachable, safe nearby people and places
    +-- trusted informal network (with boundaries and consent)
    +-- formal services, online, phones, transit, future appointments
    |
CONFIRM WHICH CHANNELS REALLY EXIST RIGHT NOW
    |
CANDIDATE ACTION FIBER (not one arbitrary preferred route)
    |
SAFE, AUTHORISED ACTION + OBSERVED CONSEQUENCE
    |
LOCAL FIELD ATLAS + NEXT ACTION
```

When a service closes or the network disappears, discard **the failed live capability**, not the remaining knowledge, relationships or possible actions. Conversely, a path that is physically accessible but dangerous is not a valid shortcut. Retain the option to say **UNKNOWN**. Distinguish a *candidate lead* from delivered food, potable water, accepted help or confirmed shelter.

### Resilience is not a glamorous story about deprivation

The practical resource hierarchy needs to recognize risks and changing conditions: exposure, water and injury can become more urgent than a previously declared meal-finding task, while long-term stable housing and reliable food access remain important objectives. Survival under deprivation should not be confused with consent to deprivation or a guarantee of safety.

Safety boundary examples:
- [CDC: Preventing Hypothermia](https://www.cdc.gov/winter-weather/prevention/) — prolonged/wet cold can impair thinking and mobility; seek warmth and medical help when warning signs appear. No recommendation to experiment with unsafe heating or exposure.
- [CDC: Heat and People without Air Conditioning](https://www.cdc.gov/extreme-heat/risk-factors/extreme-heat-and-low-income.html) — shade/cooling, hydration and checking others are useful where safely possible; serious symptoms need medical attention.
- [CDC: How to Make Water Safe in an Emergency](https://www.cdc.gov/water-emergency/about/) and [How to Find Clean Water](https://www.cdc.gov/water-emergency/about/how-to-find-clean-water-in-an-emergency.html) — a visible water source is not automatically potable; chemical contamination is not solved by simple boiling or disinfection.
- [Center for Health Care Strategies: Street Medicine and Outreach](https://www.chcs.org/resource-center-item/street-medicine-and-outreach-bringing-care-to-people-where-they-are/) — care and outreach may meet people where they are; peer support and knowledge of practical barriers matter.

No claims about a specific individual are inferred from these general sources.

## What now runs

### 1. `street_sense.py` — On-site reasoning with infrastructure failure

A pure Python standard-library engine with explicit **YES/NO/UNKNOWN** observation history, researcher-declared typed candidate actions, risk guards and a non-singleton relevant action field.

Candidates span:
- **Immediate orientation:** comfortable brief pause, assess urgent symptoms, water quality, cold/wet/heat exposure.
- **On-site resource use:** dry layers only if actually available, safe drinking water only with both explicitly confirmed water and absence of suspected contamination, known safe food only if in hand.
- **Physical movement:** travel to a *real known* public place/shelter/shade only with explicitly confirmed mobility and safe route. Urgent symptom report blocks all foot options.
- **Safe human help:** asking an actual, safely approachable person; requesting a borrowed call without assuming consent or a phone will appear.
- **Network options:** online food search or calling for assistance only if working internet/phone exists. They disappear when the channel fails, while separate offline candidates remain.
- **Continuity:** a possible recurring support arrangement through a willing actual person, distinct from an immediate meal.

A hazard-aware **priority field** makes acute cold, heat, unsafe water, or urgent symptoms salient; it does not automatically guarantee resource effects or pretend to be medical triage. **The system does not decide that people can safely fast through an unmet nutritional need.** QC-008 separately preserved the distinction between medically conditional voluntary fasting and involuntary food deprivation.

The engine does not invent a nearby business, public shelter, edible plant, hunt, source of drinking water, unoccupied structure, government service, a volunteer or a person who is safe to approach. It never suggests breaking into facilities or consuming suspicious water or unknown plants.

### 2. `field_atlas.py` — Privacy- and freshness-aware locally learned leads

Infrastructure is not the whole world, but **a living offline atlas** still needs source attribution, consent and time-dependent validity.

A lead may be:
- first-hand reported and voluntarily shared;
- attributed to a known local partner;
- drawn from public generic guidance (which does **not** prove local availability);
- a speculative hypothesis requiring verification.

Each lead has a category (food, water, shelter, warmth, rest, human connection), access channel (on-site / in-person / phone / web), time-of-observation, **expiry/recheck window**, access safety, reported availability, context/source reference, and consent to retain.

The evaluation emits:
- `CANDIDATE_FRESH_REPORT` — an earlier reported route with source, explicitly **not** verified available now;
- `REVALIDATE` — stale, hearsay, unverified or access-unknown lead;
- `BLOCKED` — unsafe, previously unavailable, or channel currently down.

Network interruption can suppress phone/web leads without destroying *recent, locally observed, in-person* candidate information. Time passing causes previously fresh entries to require revalidation. Historic observations persist rather than being rewritten to assert an unsourced present truth.

**Privacy and ethics:** No actual addresses, people's names, encampment locations or user activity are entered. The synthetic sample uses invented neutral IDs. The runtime must not collect or retain lived-experience reports without affirmative consent. A person's reported survival knowledge is valuable while remaining context-specific; one person's tactic should not become unqualified universal advice.

### 3. Regression / tested exemplars

Eight synthetic situations in the street-sense engine:
1. No working phone/internet, no food/water — immediate offline inquiry remains possible, even though no real resources are confirmed.
2. Heat, offline, *explicitly observed accessible shade* — guarded shade option becomes a candidate.
3. Wet cold, no known dry clothing/shelter — prioritize cold exposure; don't manufacture dry gear.
4. Safe, consenting person reported nearby — ask-for-help or borrowed-call question can become feasible without granting a meal or phone.
5. Urgent symptoms — human medical assistance outranks walking paths, even if walking was previously reported safe.
6. Working phone/internet — digital leads appear alongside offline ones.
7. Water claimed available but chemical contamination suspected — **do not model as safe drinking water**.
8. Repeated unmet needs — continuing access remains a distinct goal.

Field Atlas tests:
- Recent first-hand locally observed lead can remain available for follow-up after internet/phone loss.
- Stale leads, unknown safety, and unsupported rumor require revalidation.
- People or facilities cannot be certified safe from generic web knowledge.
- Consent is mandatory for retaining personal experience.
- Time-pinned snapshots and provenance receipts can be replayed.

**No external resources actually delivered. No local site/price/hour is verified.** The test measures logical consistency of declared candidate availability, not on-the-street effectiveness.

### 4. Broader architecture fit

[LOADOUT](https://github.com/the-static-collective/LOADOUT) is the owner of permission-gated capability binding. This prototype is read-only and never crosses an authority boundary.

[planZ](https://github.com/the-static-collective/planZ) is a plan-census and continuity index, not a survival-dispatch authority. A future field action can preserve a proposal and its real receipts there without granting action rights.

QC-008 introduced the concept that a **missing goal route is not a missing useful action**. QC-009 adds: **a missing institutional route is not a missing *physical, local, social or observational* action field.** It also adds tests for temporal decay of once-useful leads rather than treating static web pages as permanent reality.

## Implementation and replication

- `experiments/quantumcode009/street_sense.py`
- `experiments/quantumcode009/test_street_sense.py`
- `experiments/quantumcode009/field_atlas.py`
- `experiments/quantumcode009/test_field_atlas.py`
- `.github/workflows/quantum-code-009.yml`

Python 3.11, standard library:

```sh
cd experiments/quantumcode009
python -m unittest -v test_street_sense.py test_field_atlas.py
python street_sense.py
python field_atlas.py
```

### Remaining gaps (falsifiable)

1. **Actually sourced fieldcraft**: the catalogued actions are researcher-authored, not generated from interviews with consenting people with lived expertise. Build a paid, privacy-preserving, opt-in expert-review process before making the atlas operational.
2. **Live environment sensing:** weather, walkability, shelter hours, legal accessibility, water quality, service acceptance and personal capacity are not present. Every scenario fact is synthetic.
3. **Cross-domain action discovery:** the system still searches a declared action inventory, not an open-ended physical environment. A future research agent should nominate safe unknown leads for validation, and compare against established planners/competent field practitioners.
4. **Reliable counterfactuals:** the engine does not compute probabilities or predict the real success of a walk, request, shelter or call. Paths are capability candidates, not guarantees.
5. **Real-world safeguards:** any external outreach, local data handling or real action must be separately authorized. No person should be asked to risk injury, trespass, dangerous exposure or unsafe water based on an unverified model.
6. **Sustainability vs immediacy:** a useful survival action does not end the larger problem of housing stability, food security or reliable community support.

**Proposed next frontier: QC-010 — LOCAL PROBE → WITNESSED RESOURCE → AUTHORIZED ACT → NEW PROBE.** Compare multiple failure and resource scenarios supplied by independent knowledgeable reviewers. Preserve no-network fallback, user dignity and uncertainty rather than rewarding only rapid routing to institutions.
