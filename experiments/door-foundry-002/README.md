# DOOR-FOUNDRY-002 — CANNON → MOTIF → NEW MOTIF BUILDS

**Implemented research direction:** consume an independently replayed, explicitly **held**, source-selected CANNON packet and have MOTIF's existing typed planner construct multiple genuinely runnable *local configurations* from the original, unmodified owner code. **Not** arbitrary code invention, deployment, remote updates, auto-selection of canon, or permission to act on people.

## Why this is a new crossing

DOOR-FOUNDRY-001 [MOTIF #66](https://github.com/the-static-collective/MOTIF/pull/66) demonstrated an exact-source typed five-capability composition. CANNON independently selected and replayed that **unmerged MOTIF commit** in [CANNON #92](https://github.com/the-static-collective/CANNON/pull/92), without promoting it.

Here MOTIF builds the **return edge**:

```
MOTIF original candidate, at exact unmerged commit
    ↓  (CANNON independently executes native source-owned code)
CANNON held, content-digested evidence packet
    ↓  (MOTIF verifies receipt, source, scope, and native registry)
MOTIF native typed composition targeting different outputs
    ↓
Three new offline, runnable MOTIF build directories
    ↓  (fresh Python processes, original owner modules and data)
Reproducible evidence + held candidate manifests
    ↓
Separate operator/owner review before any real-world adoption
```

## What gets built

MOTIF derives three distinct recipes from the actual source-native typed registry, using original DOOR-FOUNDRY-001's **bounded Dijkstra composer**, not a hardcoded sequence:

| Output target | Original typed handlers executed | Distinct capabilities |
|---|---|---:|
| `frontier` | 002 induction, 003 affordance frontier | 2 |
| `macro_replay` | 002 induction, 006 compile and replay | 3 |
| `door` | 002, 003, 006 compile/replay, Door assembly | 5 |

Each generated folder is a *runnable* `run.py`, `manifest.json` and exact byte-for-byte source-owned Python modules/data. These are **new build compositions and packaged local executables**, **not** novel algorithms learned from new observations. No arbitrary Python code is accepted from CANNON packets, no hidden `eval`, no subprocess external action, and no "self-merge". The copied runner is a fixed, reviewed template whose bytes are pinned in the manifest.

The whole run uses **GitHub Actions with read-only repository permissions** and stores the generated candidate build folders as a downloadable artifact, not new commits in either owner's `main`.

## Actual evidence and limits

- CANNON has selected the exact MOTIF #66 donor SHA `5ee9207f04af2826750863526af7f92b31ef8578`, and CANNON reviewer source is pinned at `ce54c67f5e830b32a6e754c22da4a1acd51418c0`.
- On every CI run, CANNON is run first against the exact original donor checkout, producing a fresh held evidence packet; MOTIF then receives *those actual bytes*, not an invented wrapper.
- MOTIF independently validates the packet's digest, source selection, six original Git blob pins, original native registry and exact local checkout commit. The hash alone does **not** authenticate CANNON as an identity.
- The new builds run with no network calls or third-party credentials. Their default world is the original synthetic person/bicycle fixture.
- The fully composed `door` build **ties** the original fixed classical planner on the underlying simulated outcome. No measured general reasoning improvement or field benefit is claimed.
- `HOLD` is honored as a **no-admission** state; it does not make local read-only synthetic evaluation forbidden. External actions remain prohibited in these builds.
- This is **not recursive self-modifying software** yet: generation is restricted to a known finite interface library and a finite list of local goals. We have demonstrated reliable new *assemblies*, not invented new operators from the wider network.

## Reproduce

Clone this experimental branch, the original MOTIF donor commit and CANNON reviewer commit into sibling directories named `motif-source` and `cannon-source`. With Python 3.11+, Node 22+:

```sh
mkdir -p cannon-return
node cannon-source/experiments/motif-door-selection-001/cannon-door.mjs \
  --source motif-source --output cannon-return/receipt.json
python experiments/door-foundry-002/feedback_builder.py \
  --cannon-receipt cannon-return/receipt.json \
  --cannon-selection cannon-source/experiments/motif-door-selection-001/selection.json \
  --source-root motif-source --output generated-builds
python generated-builds/motif-build-frontier/run.py
python generated-builds/motif-build-macro-replay/run.py
python generated-builds/motif-build-door/run.py
```

The bundled GitHub workflow runs this, adversarial tests, and archives the resulting runnable packages.

## The next scientifically meaningful question

Can a selected original external method (e.g. ALEX's evidence assembler, Dogram's instrument, or GRAFT's generated operator) be **adapted and verified under a new typed contract** rather than only changing which native MOTIF organs participate? Then can the new candidate be outperformed or falsified by a strong fixed-workflow control on previously withheld tasks?

**CANNON may inform builds. It cannot grant permission to deploy them, and MOTIF cannot claim a new capability merely because it repackaged older ones.**
