# MOTIF-020 — THE INSTRUMENT GARDEN
## First seeded composition: reLATTE × Official Minecraft Riff-Raft

**Status:** standalone, bounded research candidate. No general recursive agent, real-world actuator, persistent UNDERSTORY write, or automatic Minecraft server action.

## New ability

MOTIF-019 could identify the next useful **already known** role probe. MOTIF-020 asks a harder question: **what measurement should be commissioned when the answer has never been observed?** Its finite domain grammar composes:

`unresolved rival explanations → unseen world/position target → inferred threshold decoder → candidate measurement → expected information → costs + cost of inaction → propose or HOLD`.

The instrument is a deliberately *new question addressed to a Minecraft game world*: count the powered redstone lamps with the repeater removed at a **previously unmeasured world+position pair**. A hypothesis is not a sensor, and the predicted lamp counts are NOT observations.

### Source evidence

The first seed is grounded in an already archived, independently cryptographically replayable reLATTE Minecraft 004+005 history: original signed World A at repeater x=-13 yielded 3 powered lamps and later World A at x=2 yielded 5; World B at x=17 yielded 6 and later World B at x=-28 yielded 2. See reLATTE `experiment/riff-raft-minecraft-007-two-custodians` and its exact fixture SHA256 `da6c556051f197e1d07578b5e435ae3b7132538c7c098a4add9e4acfd4572d42`.

The **actual reLATTE adapter** replays those native original P-256 signatures, source envelopes and raw game states. The publicly visible `seeded_minecraft.json` is an illustrative toy and contains a claimed source classification; by itself it does **not** authenticate the signed Minecraft source. reLATTE's adapter must verify the underlying source *before* minting its verified-input envelope.

### Hypotheses

Two deliberately *seeded*, not automatically discovered, toy causal models agree on all four prior game observations:

- **position-invariant-prefix** predicts 3 lamps in world B at x=-13.
- **world-local-hidden-relay** predicts 4 lamps in world B at x=-13.

These models also predict distinguishable counts at another novel target, but that candidate is more costly. They are constructed to test the instrument mechanism, not presented as credible new physics.

MOTIF enumerates unseen targets, derives count thresholds from disagreements in rival predictions, estimates expected Shannon mutual information (using stipulated sensor reliability), ranks by value of information + avoided delay loss - action/latency cost, and compares with a **HOLD** baseline. With this seed, it proposes:

`World B (seed 918273645): remove repeater x=-13 y=66 z=46; after game ticks, count nine lamps and test whether count ≥ 4; restore and independently read all nine.`

The same position had previously been measured in World A, but not in World B. This deliberately tests whether that observational pattern transfers between worlds. Neither forecast is made true by the planner.

### Actual reLATTE composition

See `the-static-collective/reLATTE` branch `experiment/motif-instrument-garden-minecraft-008`:

1. Verifies the byte-exact archived reLATTE 005 bundle, original 004 ancestor, P-256 signed crossings, receipts and both separately observed Minecraft game histories with reLATTE's **native 007 custody auditor**.
2. Imports MOTIF-020's actual `designInstrument` at runtime, rather than independently reimplementing it.
3. Invokes reLATTE's existing `buildRiffRaftRedstonePlan` and `validateWorldPlan` to compile a **buildable vanilla 26.1.1 datapack**: `setup`, `trigger`, `fault`, `reset`, `repair`, `read_lamps`, `restored`.
4. Creates a **new native, ephemeral P-256 signed reLATTE crossing** referencing the old 005 parent and a separately signed receiver-local `R3_HOLD`. This is a cryptographic receipt **of the proposal**, not a game outcome.
5. Preserves a proposed measurement with explicit independent fresh non-OP game observer requirement and no game/physical actuation claim.

This is a **composed executable test asset**, not yet a verified new Minecraft game observation. No 020 result should be counted as a successful or failed hypothesis until a new official server run actually measures the lamps and a separate source verifier independently checks the new game trace.

### Tests and falsification

`node --test experiments/020/instrument_garden.test.mjs` checks cost-of-inaction, constrained budget, non-discriminating models, stale observations, source escalation, withheld permission, impossible targets, hypothetical posterior splits, and source-data corruption.

`node experiments/020/seed.mjs` prints the deterministic next measurement proposal.

The companion reLATTE branch additionally checks native signed 004+005 replay, the actual MOTIF-imported decision, reLATTE native Minecraft world/Redstone construction, emitted game datapack functions, and a new verified **signed HOLD** crossing. A manipulated byte of the old evidence must be rejected.

### Anti-overclaim boundaries

- The *search grammar* (allowed repeaters, target worlds, game-only readout, hypothesis vocabulary) is hand-supplied. This does not invent an unbounded measurement primitive or a physical instrument.
- Seeded rival predictions and reliability numbers are assumptions; no machine learned them from game observations.
- Existing signed game history is not a new game experiment. A script or datapack is not an executed server effect. P-256 signatures are not proof of human identity, consent, physical authority, or reliable science.
- CONDITIONAL posterior is not an observed posterior; requires independent new game evidence.
- Proposed new capability is not installed in any private MEMENTO, JAR;VIS, reLATTE remote system, or world.
- No private MEMENTO/UNDERSTORY source data is copied.

## Next frontier

Run the new datapack on **separately provisioned official Minecraft servers**, require server-owned block-state observations and a fresh nonoperator observer, then independently reverify two contrasting signed outcomes. Feed those *new* verified consequences to MOTIF's posterior updater, emit a fresh UNDERSTORY contact and activation only for an actually witnessed event, and re-plan the next high-value unknown rather than recycling the same question.
