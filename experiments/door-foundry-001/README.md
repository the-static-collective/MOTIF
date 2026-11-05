# DOOR-FOUNDRY-001 — The First Self-Composing Door

**Status:** experimental implementation on an isolated review branch. **Scope:** offline synthetic planning only, no internet, credentials, people matching, external writes, implicit consent or actual task completion.

## What is actually new

A small, general **data-only capability registry**, a bounded typed Dijkstra composer, an explicit **Door Contract**, and a reproducible cross-experiment evaluator. The composer decides the execution ordering from required/produced artifact types; it does not call a fixed five-step script. The handlers execute actual, unchanged owner modules:

- **MOTIF-002:** learn graph verbs from original synthetic lessons.
- **MOTIF-003:** compare immediate and downstream affordances in the original hypothetical graph.
- **MOTIF-006:** induce nested macro candidates from multiple synthetic traces and recheck their original primitive guards in an unfamiliar renamed graph.

Each original source is checked against its exact Git blob SHA before it can be loaded. The experiment assembles a *proposal* that contains both an affordance analysis and independently replayed, multi-step candidate macro. Neither component alone produces this joint audit record.

The new registry contains **MAIN_VERIFIED** and **EXPERIMENTAL_VERIFIED** capabilities. The state describes available test evidence, **not** a value judgment based on whether the code lives on `main`. A candidate from another branch may become eligible only when code and local contract are actually installed, source-pinned, tested and reviewed. Unmerged branches are **not silently imported** by this experiment.

## Run

```sh
python experiments/door-foundry-001/door_foundry.py
python experiments/door-foundry-001/door_foundry.py --deny-synthetic-permission
cd experiments/door-foundry-001
python -m unittest -v test_door_foundry.py
```

The default program prints JSON with `stage: PROPOSED`, a hypothetical graph delta, a reviewed-by-code simulation trace, source/registry attribution, declared planning cost, explicit non-authority flags, a comparison against the original MOTIF-002 fixed planner, and a content digest. The denied-fixture path prints `stage: HOLD`.

## Door Contract — a staged claim, not an automatic state machine

```
UNIMAGINED -> PROPOSED -> TESTED -> AVAILABLE -> AUTHORIZED -> ACTED -> OBSERVED -> REUSABLE
```

**Only PROPOSED is implemented here.** No stage transition is inferred from a checksum, synthetic `permits` fact, or test pass. Future door stages require independent owner-defined evidence and explicit authority for each new effect surface. `HOLD` is a valid terminal result. Actual adoption must not be triggered by a hypothetical prediction.

The present goal is declared by the experiment fixture: teach a simulated person to repair and make two simulated bikes usable. These synthetic facts do **not** represent real humans or physical repairs.

## Controls / what the test cannot prove

- The original **MOTIF-002 classical breadth-first planner can already achieve the synthetic world goal**. No planning superiority, new real-world capability, or general intelligence is claimed.
- The joint typed report combines 002/003/006 functionality; the added requirement for all organs is a *contract for the report*, not proof that all are necessary to achieve the underlying bike repair.
- Missing source, altered source, missing synthetic consent, absent organ, invalid registry, false scope/outputs, duplicate handler, impossible goal or a planning-depth limit must `HOLD`.
- A pinned source digest is a content identity, **not identity authentication**.
- Planning cost is a manually declared integer. We have **not** measured CPU Joules, runtime, monetary cost or human outcomes.
- The original 006 macro is a compressed *representation*, not fewer required underlying primitive operations.
- The 003 selected first move and 006 candidate macro are **different proposed instruments**; they are not represented as a single sequential plan.

## What to build next

1. A second, **independently implemented** fixed-workflow control with matched outputs and measured wall-clock/CPU costs; do not treat a DAG composition as inherently novel.
2. A portable, strictly data-only adapter contract and owner-reviewed installation flow that allows source-pinned experimental branches to be used without merging them.
3. A local operator-defined *Fellowship coordination workroom*: only drafts and reversible work artifacts until consented actions are separately supported and observed.
4. Field receipts proving actual human use, successful coordination, failure modes and costs. An application preview is not evidence of a successful event.

This is the first compositional *testbed*, not yet the self-improving, real-world Door Foundry.
