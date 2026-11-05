# DOOR-FOUNDRY-003 — GRAFT-Born New MOTIF Organ

**A newly generated executable capability now crosses GRAFT → CANNON → MOTIF.**

Unlike DOOR-FOUNDRY-002's three arrangements of existing code, this experiment receives *actual new JavaScript source code* produced by the original, unmerged **GRAFT-027 Capability Gardener** (`6ff59aead0296081e1547d8107e4b6f06ea2381e`). This isn't generic code synthesis: it is a **bounded field-path grammar** that GRAFT applies to independently labeled synthetic JSON examples. The generated source is a different executable module than any original MOTIF organ.

The independent CANNON reviewer ([CANNON #93](https://github.com/the-static-collective/CANNON/pull/93)) checks original owner bytes, tests and all generated finalists; preserves the generated source, its sha256, and rejected alternatives in an unsigned **HOLD** receipt. MOTIF independently source-pins both owners and **reruns the original GRAFT compiler** at that same revision to ensure the transferred source is exactly what GRAFT could generate. It does not merely trust the CANNON digest as a signature.

## What the generated MOTIF build really does

1. A new source-owned GRAFT operator `execute(input)` observes a numeric value at **`observed.reachable_actions`**, extracted from a synthetic JSON witness. GRAFT learned that selector by source-native finite candidate compilation plus labeled training/holdout/negative trials; CANNON independently tested the resulting executable on a further four previously unseen fixtures.
2. The generated `generated_sensor.mjs` runs as a fresh Node program through a fixed, audited stdin/stdout adapter (`observe.mjs`). The value it reads is fed into a **real existing original MOTIF-003 decision policy**: values 2+ choose the declared **new-choices** policy; lower values choose **immediate**.
3. On four final fixtures, this changes which **original MOTIF operator** is recommended relative to a train-only naive decoy field. The Python runner calls **original unchanged MOTIF-002 and 003** source, not an invented recommendation function.
4. Original GRAFT source code, original MOTIF 002/003 code, CANNON independent review commit and generated module bytes are recorded as exact Git and SHA256 pins. New build's manifest, runner, generated JS and fixed adapter are all self-checked. Forged permission, source mutation and changed evidence must **HOLD**.

This generates **one new runnable local MOTIF build** with a genuinely generated *sensor component* influencing existing reasoning.

## Evidence and controls

The training-only shortcut picks `advertised.reachable_actions`, because the decoy matches all training labels. It scores **0/4** on fresh final cases. The generated original GRAFT sensor scores **4/4**, and the native MOTIF policy differs on all four. But GRAFT used independently labeled selection-holdout examples to choose its sensor. A fair **classical exhaustive selector using those same holdout labels also gets 4/4**. No algorithmic superiority is claimed.

The data is **fully synthetic**. The source-shaped ALEX discovery receipt is explicitly a *fictional interface fixture* — not a genuine API discovery or provider connection. The numeric value and recommended original MOTIF action are hypothetical, not observed real-world agency, permissions, or physical work.

No actor is contacted. No external network is used by the generated program. No repo is modified by the new build. No source owner has selected a canon admission, no commit to `main` is performed, and no automated deployment is attempted.

## Reproduction

In the code's dedicated GitHub Actions workflow, three independently pinned checkouts run alongside this branch:

- GRAFT-027 original @ `6ff59aead0296081e1547d8107e4b6f06ea2381e`
- CANNON #93 @ `0fd326c1bb6f222dc572a4877818d63881828801`
- MOTIF #66 original @ `5ee9207f04af2826750863526af7f92b31ef8578`

The workflow runs GRAFT native tests, the original CANNON reviewer, the MOTIF builder, adversarial tests, a fresh execution of the new program, and exports a build artifact.

```bash
node cannon-source/experiments/cannon-graft-motif-001/review.mjs \
  --graft graft-source --output evidence/cannon-graft-sensor.json
python experiments/door-foundry-003/graft_backloop.py \
  --cannon-receipt evidence/cannon-graft-sensor.json \
  --graft-source graft-source \
  --motif-original motif-original \
  --output generated-motif-new-sensor
python generated-motif-new-sensor/run.py
```

## Next falsifiable frontier

Give MOTIF **multiple genuinely different candidate operator families** from GRAFT and test whether it can infer which missing capability is needed before the user defines a particular new source field. Compare under *matched training, selection and evaluation budgets* to a conventional program synthesis/search baseline. Then attempt a separately authorized real-world read, with proper observed-outcome custody, rather than extrapolate a synthetic experiment into a general-agent claim.

**Actual generated new module: YES. Autonomous general intelligence/self-modification: NOT YET.**
