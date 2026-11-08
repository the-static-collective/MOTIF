# QC-008 — THE AFFORDANCE RECOVERY FRONTIER
## No route to the goal ≠ no useful next action

**State:** source-reviewed, publicly evidenced **general navigation** research; finite typed prototype, not live local service search, not a clinician, not a production agent. Stacked on QC-007 and preceding MOTIF experiment drafts. All demonstrations are synthetic. No changes to production MOTIF, no calls, no outreach, no real meals supplied, no location data, and no real-world assistance independently verified.

## The user correction

The preceding [QC-007](https://github.com/the-static-collective/MOTIF/pull/197) intentionally refused to claim a food solution in a scenario with no food, motor transport or phone. That is correct about **the existing food-route inventory**, but an insufficient response for **a general problem-solving agent**. Even with no known route to nourishment, an agent should ask:

1. What important **capability**, **observation**, or **condition** is missing?
2. What **safe, reachable action** could create or reveal that missing condition?
3. What can be done **without** assuming food, transportation, phones, a staffed location, another person, or mobility is actually available?
4. Can the newly observed conditions reopen a previously blocked route?
5. How can the person move toward **dependable recurring access**, rather than only one meal?

The user's example was that *presence, awareness, focus and a sound mind may be the next useful move when no direct nourishment route is currently reachable*. We preserve that insight as **optional attention- and inquiry-supporting actions**, not as a claim that breathing, meditation or fasting creates nutritional energy or is medically suitable for anyone.

### Precise architecture

```text
UNMET GOAL
     |
KNOWN ROUTES -> NONE CURRENTLY VERIFIED / FEASIBLE
     |
FIND BLOCKED PRECONDITIONS + UNKNOWN CONDITIONS
     |
BROADEN SEARCH TO SAFE META-ACTIONS
     ├── situational awareness / optional comfortable breathing
     ├── notice urgent symptoms or water availability
     ├── ask whether safe walking is possible
     ├── identify a safe, actually known staffed destination
     ├── ask whether a safe person is present
     ├── ask whether a borrowed call / connection is possible
     └── observe human and environmental constraints
     |
RECEIVE AN ACTUAL EXPLICIT OBSERVATION (not guessed)
     |
RECOMPUTE ROUTE FIELD
     |
POSSIBLE REFERRAL / CONTACT / SAFE TRAVEL
     |
MUST VERIFY LOCAL PROVIDER AND AVAILABILITY
     |
ACTUAL ASSISTANCE ONLY WITH HUMAN WITNESS AND PERMISSION
     |
FURTHER RECURRENCE AND ACCESS WORK
```

**A conditional route is not a verified route; a referral route is not a meal; a mental-regulation technique is not nourishment.**

This is an application of the Golden Compass [*The Needle May Be a Fiber*](https://github.com/the-static-collective/the-daily-slice/blob/main/slices/2026/08/2026-08-29/the-needle-may-be-a-fiber.md): when multiple next observations remain equally relevant, preserve a **question fiber**, rather than forcing one invented winner.

## New typed source-backed subsystem

### Evidence and timestamp cuts

`recover.py` contains a manually verified **general public resource-navigation evidence registry** with immutable claim digests and a frozen **2026-11-07** capture date. The source digest is a hash of our **manually recorded claim, URL, scope and date**, **not** a downloaded or independently authenticated hash of the original web page. That distinction matters.

- **[United Way 211 — Food Programs and Benefits](https://211.org/get-help/food-programs-food-benefits)**: 211 describes finding food resource information through local 211 agencies, telephone and other channels; *local actual assistance varies*.
- **[Feeding America — Find Free Food and Groceries](https://www.feedingamerica.org/need-help-find-food)**: ZIP search points toward area food banks and distribution partners; not a promise that a pantry is open or can serve this person today.
- **[USAGov — Emergency Food Assistance](https://www.usa.gov/emergency-food-assistance)**: lists 211 and asking community or faith organizations as general resource pathways; not a source of verified local hours, eligibility or free transportation.

The engine does not read these URLs during a GitHub Actions run, contact any service, use personal GPS, or prove real availability.

### Typed action-affordance compilation

`source_routes.py` independently records **human-reviewed source-to-route mechanisms** (contact 211 with a phone, use a ZIP lookup with internet, or seek a community referral if walking and safety and a real staffed destination are confirmed).

`compile_public_routes()` builds the current navigation action inventory from these typed source-linked mechanisms without adding any new code branch for each organization. New evidence alone does **not** invent a route: a reviewed mechanism plus a source is required. The compiler rejects duplicates, unbacked source IDs, unsafe unguarded person/foot routes, and any attempt to assign **guaranteed food** or **locally verified** status to a general page.

This is **source-pinned route candidate compilation**. It is NOT arbitrary unsupervised extraction of actions from open web text, nor real-time local discovery.

### Three-valued, source-append-only reality

Every decision-relevant predicate has **YES / NO / UNKNOWN**.

Knowing no phone and no car does **not** imply the person cannot walk. Knowing someone is nearby does **not** mean they can safely be approached. Knowing a nearby institution exists is **not** proof that it is staffed, accessible or serving food.

Person-reported observations are appended with a type, source ref and increasing historical step. The historical cut can be replayed. For example:

```text
has_phone = NO
motor_transport = NO
has_food = NO
can_walk = UNKNOWN
safe_to_walk = UNKNOWN
safe_public_destination_known = UNKNOWN
someone_nearby = UNKNOWN
safe_person_to_approach = UNKNOWN
medical_red_flags = UNKNOWN
```

The correct immediate result is:

```text
NO_FOOD_ROUTE_YET__NEXT_CAPABILITY
```

with safe question and preparation options. It is **not** `NO_ACTIONS_EXIST`.

If the person later reports they can physically walk, that the walk is safe, that no urgent symptoms are present, and that a specific staffed destination is actually known, the conditional *in-person referral* route can open. It remains labeled:

```text
REFERRAL_PATH_POSSIBLE_NOT_FOOD
```

If symptoms such as severe weakness/faintness are reported, **urgent human assistance takes priority** and even earlier walking observations do not authorize the engine to recommend travel.

### New classes of next move

The `Bridge` objects preserve non-nourishment action types separately:

| Kind | Examples | What it can establish | What it cannot assert |
|---|---|---|---|
| ORIENTATION | Calm, comfortable breathing; notice immediate surroundings | An optional attention-supporting step | Calories, safety, a meal, physiological recovery |
| INQUIRY | Assess mobility, weather, safe walking, other people, water, symptoms | A question the person may answer | A fictitious YES answer |
| CAPABILITY | Ask whether a shared phone or internet access may be available | An affordance requiring further verification | That a phone, provider or volunteer exists |
| HUMAN_HELP | Ask a safe, actual nearby person for support | A possible social request | Consent, eligibility or delivery of food |
| ASSISTANCE ROUTING | Contact 211 / identify food bank partner / inquire about recurring access | Information or a referral, possibly | That an actual meal or recurring supply was secured |

There are **no outward actions**. A `Bridge` has `automatically_changes_world=False` and `claimed_nutrition=0`. An unanswered question remains UNKNOWN; it does not turn into a guessed positive state.

### Fasting — a meaningful distinction, not a binary blacklist

The user correctly pushed back on a false dichotomy: **planned fasting in some people and some medical/spiritual contexts is not identical to involuntary food deprivation.** A person may go without food for some time, and time-limited elective fasting is an active area of research. It remains inappropriate to infer from the ability to endure hunger that sufficient nourishment or continuing access has been obtained.

`practice.py` models contexts separately:
- **Food unavailable**: `RESOURCE_GAP_REMAINS`. The engine cannot recast forced deprivation as therapeutic fasting.
- **Food available + deliberate choice + no known individual risk or distress**: `POSSIBLE_VOLUNTARY_PRACTICE_NOT_NUTRITION`, preserving fasting as one elective possibility, not a medical prescription or a food solution.
- **Relevant medical risk/distress**: `HOLD_HEALTH_CONTRAINDICATION` with individualized medical review.
- **Unknown choice/risk**: `HOLD_NEED_HEALTH_AND_CHOICE_CONTEXT`.
- Optional comfortable breathing remains `OPTIONAL_SUPPORT_NOT_NOURISHMENT`.

Scientific context:
- [2026 Cochrane review](https://www.cochrane.org/evidence/CD015610_intermittent-fasting-traditional-dietary-advice-or-no-treatment-which-works-better-help-adults) across adults with overweight/obesity found little or no difference on some measured outcomes versus other dietary advice, with significant uncertainty around adverse effects and longer-term outcomes.
- [Mayo Clinic patient guidance](https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/expert-answers/intermittent-fasting/faq-20441303) notes intermittent fasting is not appropriate for everyone, including certain medical and life circumstances.

Neither source proves any particular fast is medically indicated or that an individual lacking food has enough nutritional reserve to continue without care.

## Reproducible regression against actual QC-007 HOLD

`qc007_bridge.py` imports the earlier actual `living_field.py` experiment, runs the exact `scenario("isolated")` and preserves:

```text
QC-007: HOLD_NO_SAFE_COMPLETE_PATH
        0 direct goal-reaching paths
        original world receipt preserved
```

It then projects the known facts into a **new** typed observational situation, without assigning walking safety or the existence of a nearby person:

```text
QC-008: NO_FOOD_ROUTE_YET__NEXT_CAPABILITY
        several safe, contingent next questions/actions
        0 confirmed food units
        0 external acts
```

This is a real **repair of the planning framework's epistemic termination behavior**, while respecting QC-007's finding that its original inventory could not produce food.

## Test and evaluation contract

The workflow tests include:
- no-contact/no-car/no-food now yields **next safe options**, not a dead end;
- source-pinned general guidance, with no claim of availability or direct food provision;
- factual YES/NO/UNKNOWN distinctions, questioning and source provenance;
- no assumed walking ability, safe person or staffed destination;
- later user observations can reopen a referral without backdating earlier state;
- urgent symptoms override previously plausible walking;
- optional grounding can support attention without being modeled as calories;
- intentional fasting is permitted as a context-dependent personal practice but prohibited from masquerading as a fix for involuntary deprivation;
- dynamic addition of a new source-linked, reviewed mechanism produces a new route without modifying the action engine, but never confers actual food;
- exact import of the earlier QC-007 no-route regression and repair into a field of potential next moves.

**All publicly sourced claims are general guidance. All person-state examples are fabricated fixtures. This is not a completed live intervention and not a strong classical planning benchmark.**

## Reproduction

Python 3.11, standard library only, no external credentials:

```sh
cd experiments/quantumcode008
python -m unittest -v test_recover.py test_practice.py test_qc007_bridge.py test_source_routes.py
python recover.py
python source_routes.py
python practice.py
python qc007_bridge.py
```

CI: `.github/workflows/quantum-code-008.yml`.

## Next real pressure

**QC-009 — Evidence-to-Execution Bridge.** The next step needs source-specific live queries, independent confirmation of local availability and eligibility, user-supplied safe-mobility/health constraints, the option to ask necessary questions, explicit permission to contact services or take an external action, and a witnessed outcome record. Test with another domain such as equipment diagnosis and event logistics. Failure cases should preserve the **reason for blocked action**, not bury it in a generic "no solution". Compare against existing multi-objective planning under equal information and effort budgets.

There is no pretense that this symbolic system can already deliver food, substitute for human care, know individual health status, or autonomously solve poverty. Its new narrow technical achievement is to stop treating a **missing goal-reaching route** as the end of useful reasoning.
