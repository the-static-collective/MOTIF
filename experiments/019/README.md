# MOTIF-019 — Native MEMENTO × UNDERSTORY Grammar Bridge

**Status:** private-source runtime interop, synthetic bounded experiment, noncanonical.
This branch is stacked on MOTIF-018; it is NOT merged, deployed, or granted
external-world authority.

## What is genuinely wired

This experiment **imports the real modules from the owner's MEMENTO
checkout at runtime**. It does not clone their algorithms into an imitation,
copy any MEMENTO source code to MOTIF, or export private UNDERSTORY content.

- **MEMENTO Relational Fractal Affordance** constructs 16 individually
  receipted synthetic worlds using `registerParticular`, `relate`, and
  `recordWitnessedAct`. The bridge extracts graph edges from the actual
  registered MEMENTO relations, checking their native event receipts.
- **MEMENTO Interaction Grammar** reads two genuine local RFA act records
  through `deriveRuleFromWitnessedAct` and produces two candidate rules.
- **MEMENTO Role Nursery** reads those exact rules via
  `proposeRoleCandidateFromGrammar`, creates two provisional role profiles,
  and runs the native `probeRoleCandidates` selector. A coarse probe collides;
  an added `reaches` probe separates. No role becomes admitted or powered.
- **MOTIF-018** consumes a deliberately narrow JSON structural packet through
  `interop_stdio.py`. It proposes a two-hop relation based on training and
  validation only, returning original vs expanded vs exhaustive classical
  holdout accuracy, candidate receipts and a non-authoritative cartridge.
- **MEMENTO UNDERSTORY** uses the *real*
  `scripts/lib/understory.mjs::validateUnderstoryRecords` implementation to
  validate a six-family **synthetic in-memory** continuity sequence:
  contact → attention → decoder → stance(HOLD) → association(unresolved) →
  activation(new later occurrence).
  This does not claim an actual human encounter or write MEMENTO history.

### Tests: verified vs outstanding

- The underlying MEMENTO branch's own native GitHub Actions validate job
  passed at `e9754bd5f16993b5eddd8071219756fbfd4780ed`.
- MOTIF's separate Python `test_interop_stdio.py` checks isolation,
  type limits, schema rejection, holdout blindness and negative transfer.
- The public end-to-end **snapshot roundtrip** (see \`fixtures/PROVENANCE.md\`)
  processes structurally synthetic data actually derived from the pinned
  MEMENTO code bodies through the native MEMENTO functions in a V8 adapter.
  Real Python MOTIF selects \`path2(carries,reaches)\`; the real 019 policy
  then chooses \`reaches\`, not a pre-authored probe. Sealed holdout reversal
  retains the selection but drops accuracy to zero.
- The public pure-policy tests confirm the new probe is selected **because of
  MOTIF's chosen program**: \`path2(carries,reaches)\` selects \`reaches\`,
  while a distinct reviewable \`direct(marked)\` would select \`marked\`.
  Unsupported or uninformative programs, rival models, unauthenticated
  source flags and missing permission HOLD rather than executing.
- The new JavaScript bridge contains a cross-repository **native execution
  test**. This test **skips unless MEMENTO_ROOT is supplied**. Public MOTIF
  Actions cannot access the private MEMENTO repo using the default token.
  A green public syntax/contract workflow is *not evidence that the native
  private interop integration executed*. Run the native test with a private
  owner-authorized checkout as described below.

## Reproduce directly from the two project repositories

Prepare sibling checkouts of the actual repositories, including the two
experiment branches. The experiment inherits MEMENTO's stacked branch
ancestry: the selected HEAD contains UNDERSTORY, RFA, Interaction Grammar,
Role Nursery and their imports.

```sh
# In an owner-authorized workspace with both checkouts:
git -C MEMENTO checkout e9754bd5f16993b5eddd8071219756fbfd4780ed
git -C MOTIF checkout experiments/019-memento-native-understory
cd MOTIF

# Existing MEMENTO tests, independent of MOTIF:
(cd ../MEMENTO && node --test && node scripts/validate.mjs)

# The new exact-source integration:
MEMENTO_ROOT="$(cd ../MEMENTO && pwd)" node --test experiments/019/bridge.test.mjs
MEMENTO_ROOT="$(cd ../MEMENTO && pwd)" node experiments/019/runner.mjs
```

Requires **Node.js 22+** and Python 3.11+; no pip/npm dependency installation
for these selected modules. MEMENTO's full `node --test` suite may include
other, unrelated branches' requirements; the selected RFA/grammar/role
tests can be run individually if necessary.

The fixture author knows outcomes and relation rules: this is not a live,
unknown or independent world. The `train`/validation/holdout split is frozen.
A hostile test inverts holdout outcomes and requires the *selected cartridge*
to remain identical while accuracy collapses to zero.

## Security and evidence boundaries

1. **Public MOTIF does not fetch private MEMENTO data.** Only the owner's
   local process imports specifically named native JS modules; it does not
   read `MEMENTO/understory`, `sources`, `ledger`, `crossings`, or
   `materials`.
2. The MOTIF subprocess receives only synthetic IDs, binary observations,
   boolean toy permissions and synthetic typed graph edges. Its strict schema
   rejects additional metadata. No strings resembling owner testimony,
   names or project files are permitted by that API.
3. `UNDERSTORY contact` is **synthetic simulated contact**; no real person
   witnessed an event in this test.
4. A checksum does not authenticate real-world source identity. Distinct
   evidence IDs do not establish independent human witnesses.
5. Candidate role ≠ admitted role ≠ granted power ≠ reachable action.
   Predicted outcome ≠ verified effect. HOLD is meaningful, never an implicit
   permanent refusal or a concealed answer.
6. The current integration is a **research sidecar**, not an always-on agent,
   autonomous governance, JAR;VIS deployment, consciousness detector or
   authorization to change MEMENTO's private state.

## Likely next experiment

Let the Role Nursery *request* an additional discriminator instead of being
given `reaches`. Give MOTIF costs for: searching for a concept, asking for a
new observation, testing a proposed action, or retaining uncertainty. Compare
with conventional experimental design and program synthesis on the identical
observation budget. Only a separate reviewed threshold should install a
learned route, grant power, or write persistent UNDERSTORY records.

## Closed-loop result and limitations (019 follow-up)

The initial bridge merely ran a **preselected** additional Role Nursery probe.
That has now been removed. The current chain is:

\`RFA witnesses → Role Nursery coarse collision → MOTIF training/validation concept → dynamic candidate probe → expected collision reduction → gated native MEMENTO probe → UNDERSTORY six-family HOLD/activation trace\`.

**What is measured:** MOTIF chooses a probe *name* from its validated
\`direct\` or \`path2\` program; a finite, already-defined Role Nursery
profile supplies values for that probe. This is **not** invention of a
physical sensor or independent measurement of the outside world. The
probe-selection policy's public tests are actual executed tests; the private
MEMENTO native end-to-end tests still require an owner checkout.

**Falsifier:** A competing concept that fits training but fails validation
must not be offered; if a valid concept's named fields do not distinguish
MEMENTO's roles, the policy returns HOLD. Inverting sealed holdout outcomes
must not alter which probe was selected, but must collapse predictive
accuracy. The native integration test covers that once a private checkout is
available. No private source is published here.

Latest public CI on the source-derived snapshot: **7 Python interop,
37 MOTIF/Green Grammar, and 14 JavaScript tests passed; 2 private native
runtime tests skipped**. The standalone source-derived V8 inspection exercised
actual MEMENTO function bodies with an adapted import and digest shim; it is
not a substitute for an actual pinned private Node.js checkout.
