# BRIDGE-001 — THE FIRST DOOR FOUNDRY
## MOTIF learns to propose the *missing* cooperation move

**Status: executable, offline synthetic research slice.**
This experimental branch does not alter official MOTIF-006 / MOTIF-007,
the unmerged Q-001 / SK-001 research, any other organ, or any real person.

### Why this exists

The earlier Smallest Key study could find an optimal path **after somebody
had already supplied a list of candidate interventions**. This study removes
that crutch. The input contains only a typed situation, existing capabilities,
declared provider offers, recipient acceptances and a goal. The missing
action bindings must be constructed by the learner's bounded grammar.

The question is more consequential than "Which listed button do I press?":

> Whose existing ability, offered help, available resource or missing
> information would make a presently impossible action possible—and what
> do we still need permission to attempt?

### What actually happens

The generator identifies a target actor and task, then considers four
**supplied primitive families**, not invented physics:

- teach a task where a source already has the skill;
- inform an actor where a source already knows the task/availability;
- lend an existing item of the required type;
- make a new item **only where a maker has separately declared an offer**.

It constructs recipient-specific candidates that were **not prelisted as
actions**, binds each to a specific offer and acceptance where available,
and labels unavailable permissions \`HOLD_OFFER\` or \`HOLD_ACCEPTANCE\`.

After every hypothetical step, the engine **regenerates the candidates**.
A person who just learned a skill can become a teacher on the next step.
It can therefore find a two-step social relay that was unavailable as an
initial executable sequence. The initial provider cannot silently claim
authority over the next provider.

No human agreement is inferred from matching. A hypothetical agreement
can be explored only through the explicit \`counterfactual=True\` simulation
path. The ordinary transition API refuses held actions.

The planner uses a finite, bounded search with a lexicographic preference:

1. fewer held agreements;
2. fewer completely unoffered agreements (an existing offer pending consent
   outranks a speculative new offer);
3. lower **known** declared cost;
4. fewer steps;
5. stable action identity.

A held action's unprovided cost and duration are **unknown**, never
asserted to be zero in the real world. No held plan is declared deadline
feasible. The \`known_cost\` figure is only the sum of supplied figures.

The planner can reject any step that removes an existing actor-relative
option in the simulated world, including **intermediate** losses. It
distinguishes physical possibility, world/site admission and observer
knowledge. These are model facts, not actual legal permission.

### Reproduced fictional worlds

| World | What was **not** supplied | What the code finds |
|---|---|---|
| Repair workshop | No full proposed action sequence | Teach Ben plus inform Ben; cost 3 without taking Ben's only kit |
| Workshop without offers | No teaching or informing offer | HELD candidate bridge, with exact missing provider commitments |
| Workshop with no preservation | Constraint removed | A cost-1 loan opens Ada's door but closes Ben's bike repair |
| Perishable relay | No composed courier plan | Route information plus a separate cooler; 14 declared minutes |
| 10-minute food clock | Required time unavailable | Abstains rather than promising the impossible |
| Second teacher | Teacher Bea lacks the skill at initial cut | Ari teaches Bea; **then Bea can teach Cy** |
| Missing yes | Bea has not accepted Ari's offer | One pending acceptance remains HELD; no implied consent |

The tools, actors, costs, deadlines, outcomes and offers are invented.
This is not empirical food logistics, pedagogy, community consent or causal
discovery. It is **synthetic operator binding and finite search**. A simple
rule-based generator plus standard planning is the appropriate baseline.

### Dogram's exact role

The native, pinned Dogram bridge (\`551b5f9d...\`) consumes a two-axis
synthetic specimen derived from actions the generator **constructed**:

- no teaching / no informing;
- teaching only;
- informing only;
- both teaching and informing.

The target-visible effect is \`0, 0, 0, 1\`; Dogram's rectangle computes
a mixed difference of **+1**. Anti-collapse separately records the state
distinctions lost when the four rich worlds are projected only to visible
opportunities. Dogram calculates; it does not grant the plan, score human
values or attest that anyone learned a skill.

### The human door

\`field_desk.py\` renders one complete **offline HTML** page with seven
side-by-side-selectable fictional cases, the proposed first concrete step,
visible gains/losses, known timing, uncertainty and inspectable receipts.
It loads no remote assets or libraries, makes no requests and retains no
user history. CI builds the page and publishes it as a downloadable
GitHub Actions artifact.

Each case can export \`motif.held-bridge-packet/v0\`, a JSON **HOLD**
handoff that records:

- what is proposed and which agreements remain unresolved;
- the declared fictional source boundary;
- the human-facing first step;
- a SHA-256 content checksum;
- explicit \`no_execution_permission\`, \`no_automatic_delivery\` and
  \`requires_receiver_local_review\` flags.

The checksum is not a signature. The packet cannot prove source identity,
absence of private data or real-world authority. A future JAR;VIS /
reLATTE receiver would need its own authentic evidence, local review,
privacy/consent, scope, expiry and operator approval before anything happened.

### Run in a local checkout

\`\`\`sh
cd research/missing-bridge
python bridge.py
python -m unittest -v test_bridge.py
python -m unittest -v test_field_desk.py
python field_desk.py --output field-desk.html

# With an explicitly selected, trusted Dogram checkout:
python dogram_bridge.py --dogram-root /path/to/Dogram
\`\`\`

### What would actually falsify the ambition?

The current generator cannot discover a genuinely new physical primitive;
it constructs bindings in an author-supplied grammar. It also does not
learn the relation between reported actions and actual outcomes.

For a serious next experiment, compare this system with a simple
backward-chaining rule planner with the **same four primitives**, explicit
consent/capability constraints, time budgets and non-loss requirements.

Generate held-out relational structures—not just renamed nouns. Test novel
relay topology, misleading descriptions, withdrawn consent, untrusted
offers, delayed observations, new bottleneck kinds, time/resource contention
and unrecoverable ambiguity.

If a straightforward backward-chaining planner performs as well, the
*intelligence* claim fails. The field-card UX, permission-boundary discipline
and provenance-preserving calculator bridge may still be worthwhile
engineering.

**The model may propose a door. Only real people can open it.**
