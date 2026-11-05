# MOTIF-005 — THE IMPOSSIBILITY FOUNDRY

This is a deliberately **bounded, falsifiable step** toward MOTIF inventing a missing operation family rather than only choosing among its existing tools.

## The actual problem and proof

The **original** unchanged MOTIF-002 symbolic learner at exact owner commit `5ee9207f04af2826750863526af7f92b31ef8578` has two induced synthetic verbs: teaching a repair skill and using a repair skill. Neither adds the predicate `inspected`. The original synthetic scene contains no such predicate. This establishes an inductive invariant:

> If a fact is absent initially and no available transformation can introduce its predicate, no finite composition of the fixed transformations can introduce it.

The experimental target is `('inspected','bike1')`. Consequently the goal is **provably unreachable under that frozen verb set at any depth**, independent of a search budget. This says nothing about the actual inspectability of a bicycle or the reachability of an expanded algorithm.

The original source-owned `impossibility.py` checks the exact MOTIF commit and byte hash before issuing `motif.missing-operator.v0`. In the **no synthetic permission** control it refuses to request a candidate.

## Original code crosses three independently owned histories

1. **MOTIF** discovers the unreachable declared graph goal and issues a content-digested missing-operator contract.
2. **GRAFT-029** ([GRAFT PR #25](https://github.com/the-static-collective/GRAFT/pull/25)) at exact commit `5023b594b0daa4f0328d01643a7f258b71f60bb9` actually generates **three different executable graph-rewrite programs** using its new **typed guarded-addition grammar**. Positive, selection, and negative fictional graph episodes distinguish `broken`, `permits`, and combined guards; only `broken + permits` survives. This is a different generated-program family from GRAFT-027's JSON field extraction.
3. **CANNON-094** ([CANNON PR #94](https://github.com/the-static-collective/CANNON/pull/94)) at exact commit `03f8c012b3d6eb48ed821a2be25aa5fd6a48970c` verifies original GRAFT and original MOTIF source, executes the actual generated code on **six completely separate synthetic final cases**, and returns an unsigned **HOLD** receipt. The review also invokes the **actual original classical MOTIF-002 learner** with the same two newly labeled positive training demonstrations.
4. **MOTIF** independently checks that receipt, recompiles the generated JS with the exact original GRAFT-029 code, and packages a **new runnable MOTIF graph-search build** with unchanged original MOTIF-002 Python and a local-only generated JS operator.
5. That new build does source-native graph planning, including a newly generated `('inspected','bike1')` transition in a simulated permitted world. It separately checks a synthetic permission-denied world, which must remain unreachable.
6. Both the original question and all three original-owner proofs, the source-native new executable, classical controls, tests and outputs are archived in the GitHub Actions artifact.

## Experimental claim table

| Claim | Observation |
|---|---|
| Fixed original MOTIF-002 grammar cannot add `inspected` | Inductive source-code invariant and bounded native replay |
| GRAFT-029 generates genuinely new executable source | New original source-owned guarded-addition JS, not old copied code |
| Source and evidence independently verified | CANNON-094 source pins, native owner tests, six separate held-out cases |
| New MOTIF build makes previous synthetic goal reachable | Compiled GRAFT program creates proposed graph fact in bounded planner |
| Synthetic permission denial is respected | Unauthorized branch remains unreachable |
| General reasoning superiority | **Not established**; original classical MOTIF-002 can learn a comparable operator given the **same additional labeled examples** |
| Real-world activity | **None**: no actual inspection, identities, contacts, API connection, Git write, deployment, auto-selection or production admission |

This is **new operator grammar plus new generated code**, but the grammar is deliberately finite, human-designed, and receives hand-labeled synthetic examples. A source checksum is not a signature; a fixture `permits` fact is not real permission. This project has not automatically selected which goals matter to a human, invented arbitrary mathematical primitives, or become an unrestricted self-updating general agent.

## Reproduce

Use the dedicated [GitHub Actions workflow](../../.github/workflows/door-foundry-005.yml), which pulls all three independently pinned source owners, checks the source-native invariant **before** calling GRAFT, independently tests GRAFT/CANNON, and preserves the build as a downloadable workflow artifact.

The local protocol, after those exact checkouts exist, is:

```sh
mkdir -p evidence
python experiments/door-foundry-005/impossibility.py \
  --original motif-original --out evidence/motif-impossibility.json

node graft-source/scripts/run-forge-029.mjs \
  --gap evidence/motif-impossibility.json \
  --output evidence/graft-native-generated.json

node cannon-source/experiments/cannon-094/verify.mjs \
  --graft graft-source --original motif-original \
  --gap evidence/motif-impossibility.json \
  --output evidence/cannon-reviewed-operator.json

python experiments/door-foundry-005/build.py \
  --original motif-original --graft graft-source \
  --question evidence/motif-impossibility.json \
  --review evidence/cannon-reviewed-operator.json \
  --out generated-motif-new-grammar

python generated-motif-new-grammar/run.py
```

## The next honest frontier

Test **unseen predicate relations and substantially different operator families** (not just new predicate names inside one fixed guarded-addition template) with independent source-owner evidence. Require a calibrated cost comparison to a matched-budget classical program synthesizer or original MOTIF-002 learner. A genuine improvement would have to survive unfamiliar schemas and future tasks that were **not** hand-selected to showcase the newly compiled guard.

**Originally impossible within one grammar ≠ mathematically impossible generally. Generated code ≠ field authority.**
