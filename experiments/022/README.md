# MOTIF-022 — CRATER: The Minimum Causal Witness

**Problem:** A real Minecraft experiment produced a signed nine-lamp observation, and MOTIF-021 updated two rival hypotheses. The next discriminating target was out of budget under the original full-census cost assumptions. Can MOTIF propose a *different, less expensive way to tell the hypotheses apart*, rather than simply requesting more money?

## What the experiment actually composes

The original independently reverified reLATTE-009 World B result was **3 of 9 powered redstone lamps** at fault repeater x=-13. The full source trace contained the actual ordered bitstates, not just the total.

MOTIF-022 inspects the **observed prefix pattern** (first three lamps lit, six unlit) and introduces a falsifiable hypothesis: maybe, for the bounded single-lane circuit, the powered lamps form a contiguous prefix. This is not assumed to be a universal physical law or a source-verified invariant.

The two previously seeded hypotheses for **World A**, repeater fault **x=-28**, predict total counts of **2** versus **3**. Under the prefix assumption, the *third lamp* distinguishes them:

- Lamp 3 at x=-20, y=65, z=46: **off** predicts a two-lamp prefix; **on** predicts a three-lamp prefix.
- Lamp 4 at x=-10, y=65, z=46: **sentinel** measuring whether power extends unexpectedly downstream.

This replaces the *primary* nine-lamp measurement with **two direct lamp reads**, plus a required independent **full nine-lamp server and fresh non-operator Minecraft-client audit** afterward. The audit may falsify the assumed prefix and must never be counted as input to the micro-instrument's predeclared decision.

**The new instrument targets an unobserved World A condition.** The original 009 game observed World B at x=-13; original 004/005 histories tested other world+fault combinations.

## Ranking and costs

MOTIF evaluates what a particular pair of binary lamp observations would distinguish under the seeded model predictions and conditional posterior from MOTIF-021. It estimates expected information under an *assumed* 95% readout reliability.

Original full nine-lamp target A:-28 was assigned **5.5 cost units** against a budget of **4**. The newly declared micro-instrument costs (1.8+2\times0.18+0.2=2.36) model units and fits the budget. These are **illustrative planning-unit estimates, not measured CPU energy, walltime, gameplay resource expense, or actual total-run cost**. Since the full nine-lamp audit is still required, it would be misleading to claim the end-to-end run is necessarily cheaper.

Unlike an earlier scoring draft, the code compares expected action value **minus cost** against the *negative cost of inaction*, so the same forgone opportunity is not counted twice.

If source authenticity is absent, earlier actual bitstates violate the prefix assumption, the cost assumptions exceed budget, the rival hypotheses agree, or no distinguishable candidate exists, the engine **HOLDS**.

## Native Minecraft implementation

Connected reLATTE branch `experiment/minecraft-010-compressed-sensor` independently verifies the exact signed 009 game carrier and prior 004/005 history, imports the real `forgeMinimalWitness` function, builds World A's apparatus with the existing native reLATTE Riff-Raft redstone planner and emits a new vanilla datapack with `motif022:read_micro`.

The composer P-256 signs a **proposal**, directly descending from the actual reLATTE-009 game crossing, and issues R3_HOLD. It does not claim a new game observation until an actual official Java/Mojang runtime is run.

An execution experiment is defined to run the **two micro reads first**, then conduct a nine-lamp census and independent non-operator game-client verification, repair the circuit, and separately sign/verify the new result. No authority is granted over public game servers, physical ecology, trusted institutions, or permanent MEMENTO memory.

## Test

```sh
node --test experiments/022/minimal_witness.test.mjs
```

The dedicated GitHub workflow also reruns the existing 020 and 021 regressions. This is a bounded two-hypothesis, two-world experiment. It does not establish general self-improvement, learned game physics, calibrated cost savings or entirely self-invented sensors.
