# Synthetic MEMENTO → MOTIF fixture provenance

**Source repository:** private `the-static-collective/MEMENTO`
**Source commit:** `e9754bd5f16993b5eddd8071219756fbfd4780ed` (experimental stacked branch `experiment/cultural-lineage-graph-001`)
**Consuming repository:** `the-static-collective/MOTIF` / `experiments/019-memento-native-understory`.

The two JSON files in this directory contain **only 16 invented binary
episodes and two invented functional-role profiles**. No source narrative,
personal UNDERSTORY entry, hidden testimony, or private MEMENTO code appears
in the public fixture.

## Method

The owner-connected GitHub tool read the following **real MEMENTO JavaScript
module bodies** at the exact source SHA:

- `relational-fractal-affordance.mjs`
- `distinction-runtime.mjs`
- `distinction-reachability.mjs`
- `interaction-grammar.mjs`
- `role-nursery.mjs`
- `scripts/lib/understory.mjs`

The actual function bodies were evaluated in a **sandboxed V8 test adapter**
with their static ESM import/export declarations adapted to function
injections. `node:crypto` was unavailable in that adapter, so it used a
deterministic **noncryptographic stand-in only for the transient candidate
digest**. Those digests are **not included in the published fixtures and are
not security evidence**. All synthetic episode and probe-profile values
were produced through the corresponding MEMENTO function bodies.

The adapter observed:

- 16 individual `recordWitnessedAct` events from native MEMENTO RFA
  fixtures: training 4, validation 4, holdout 8.
- 2 candidate native MEMENTO Interaction Grammar rules.
- 2 native Role Nursery candidates.
- `probeRoleCandidates` on coarse `['carries']` retained a collision.
- After MOTIF selected `path2(carries,reaches)`, running
  `probeRoleCandidates` with `['carries','reaches']` separated
  the two synthetic role candidates; neither was admitted.
- The native UNDERSTORY `validateUnderstoryRecords` function validated
  6 **in-memory synthetic** records: contact, attention, decoder, stance,
  association, activation.

This is **an adapted in-memory execution of source functions**, not a complete
native Node ESM checkout test. It does not establish cryptographic digest
correctness or a private repository deployment.

## Public reproducibility

The CI test `fixture_roundtrip.test.mjs` uses the snapshot files to run the
**real Python MOTIF 018** implementation via `interop_stdio.py`, then the
**actual MOTIF 019 probe-selection policy**. It proves the old manually
selected `reaches` field is no longer hardcoded in the runner's experiment
path, and tests negative holdout reversal.

Only a private owner-authorized MEMENTO checkout can complete the native
end-to-end ESM imports, genuine Node SHA-256 receipts and actual UNDERSTORY
validator replay via `node --test experiments/019/bridge.test.mjs` with
`MEMENTO_ROOT`. This remains an explicit outstanding review gate.

## Scope

All data are synthetic; no human observer or independent physical sensor
is authenticated. The selected next probe is a **previously available**
profile field, not a newly invented sensor. Role-profile disagreement is
not evidence of true causality, identity or real-world effects.
