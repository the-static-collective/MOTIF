# MOTIF-SK-001 — THE SMALLEST KEY
## Minimum-cost interventions, useful options, and the limits of compression

**Status:** standalone *synthetic* finite planner experiment. No participant,
physical-world intervention, model training, admission, contact, automation, or
world-state mutation outside the fixture.

### Question

Given a declared target and a small set of offered hypothetical interventions,
what is the least-cost path that opens a *new, actor-relative* opportunity
without destroying another actor's existing opportunities?

MOTIF-003 counted proposed grounded actions. MOTIF-Q-001 selected a hypothetical
question to resolve uncertainty. MOTIF-SK-001 now distinguishes:

1. **Physical** — an actor possesses both a skill and an appropriate tool.
2. **Admitted** — the toy world additionally includes an explicit access fact.
3. **Visible** — the actor also knows that the action is available.

None of these is actual legal authorization or an executable physical action.
An intervention's `admitted` flag is predeclared synthetic data, not learned
consent.

### The invented workshop

Ada has a well-repair skill but no kit. Ben has a kit, a bike-repair skill,
and an existing bike-repair opportunity. Ben is also granted well access,
but does not have the well skill or knowledge that this opening exists.

A loan of Ben's kit to Ada (cost **1**) makes Ada's well-repair action visible,
**but closes Ben's bike-repair action**.

Teaching Ben well repair (cost **2**) creates a physically feasible,
admitted well opportunity for Ben, but does not yet create awareness of the
site-access fact. Informing Ben of that fact (cost **1**) changes knowledge
but no physical capability.

**Together** teaching and informing create Ben's new visible well opportunity
for total declared cost **3**, without taking away Ben's bike capability.
An alternative duplicate kit (cost **4**) can give Ada the visible well
opportunity without depriving Ben.

Two policies run on the same explicitly constructed world:

| Policy | Lowest modeled cost | Toy first steps | Existing option lost? |
|---|---:|---|---|
| No protection constraint | 1 | Loan Ben's kit to Ada | Ben's bike repair |
| Protect every actor at every intermediate cut | 3 | Teach Ben, inform Ben | None |

These rankings follow from supplied costs, skills, tools and toy gate facts.
They are not ethical optimization, and no users or neighbors were involved.

### Algorithm

Bounded uniform-cost state search, with state deduplication and deterministic
tie-breaking. It minimizes cost within the declared budget and step horizon.
Identity of an opportunity is `(actor, task)` regardless of how many redundant
tools or paths support it. The search retains per-scope gain/loss reports,
rather than promoting an aggregate opportunity count into human desirability.

The protection constraint checks *every modeled intermediate state*, not
just the final proposal. A refusal yields no attempted transition. If search
hits a state cap, the result is `HOLD_TRUNCATED`, not an optimality claim.
No reachable modeled target results in `ABSTAIN_NO_PATH`.

### Dogram: calculate, do not decide

The native pinned Dogram `rectangle@1` calculation compares four cells:
neither intervention, teach only, inform only, both.

Target-visible counts are 0, 0, 0, 1. The mixed delta is **+1**.

The native `anti_collapse_reachability` calculation separately tests how
much information is erased when four rich world states are projected only
to their visible capabilities: three state pairs become indistinguishable.
This is finite representational loss, **not** a moral, causal, or semantic
score.

The optional bridge requires an explicit trusted Dogram checkout, and CI
pins upstream Dogram commit `551b5f9df18f17ec69b452ddcdff01718e0ff771`.
Neither Dogram calculation selects a plan or authorizes an outcome.

### Run

```sh
cd research/smallest-key
python smallest_key.py
python -m unittest -v test_smallest_key.py

# Optional with explicitly chosen local Dogram checkout
python dogram_bridge.py --dogram-root /path/to/Dogram

# 006's strong baseline alongside the prior toy active selector
cd ../first-question
python -m unittest -v test_baselines.py
```

Pure Python standard library. No secrets, paid compute, external actions or
plugins required to reproduce the standalone experiments.

### The honest benchmark result

The MOTIF-Q-001 active selector is now also compared to a conventional
finite hypothesis-pair elimination baseline, with the same probe pool,
hypothesis family and cost budget.

**They tie on the four deliberately constructed 006 cases:** both answer
all four cases correctly using one unit of query cost per case.

That tie is an important research result. The original comparison only
beat an intentionally weak redundant-query policy. Neither result
supports a claim that MOTIF is a novel general intelligence architecture.

For MOTIF-SK-001, shortest-cost search with the *same protection constraint*
will recover the same plan. The result demonstrates a precise affordance
specification and finite exhaustive search, **not a breakthrough over
standard optimal planning algorithms**.

### Hard next falsifiers

- Compare equivalent bounded dynamic-programming and graph-search baselines
  with identical constraints and budgets.
- Randomize actors, labels, relations, goal types and resource assignments;
  hold out new structures, not only new names.
- Distinguish separate actors' consent, revocation, delegated authority and
  actual human choices; the current model has only toy gate flags.
- Test noisy, delayed or contradictory reports, unknown causal mechanisms,
  and missing observations. These should trigger uncertainty, not confidence.
- Compare cost, duration, option losses, exposure, and target-specific
  sufficiency separately. Do not collapse them into one unexplained score.
- Develop a genuine capability-relevant learning loop only after the fixed
  synthetic planner and its simple baselines are fully characterized.

**A proposed key is not an action.
A simulated opportunity is not a right.
A Dogram delta is not evidence of causation.
A correct toy prediction is not general intelligence.**
