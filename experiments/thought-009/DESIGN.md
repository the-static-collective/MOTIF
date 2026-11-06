# MOTIF THOUGHT-009 — Choose Thinking Instruments

**Stage:** executable, isolated synthetic development experiment, Python 3.10+ stdlib, stacked on THOUGHT-008. No deployment, no learned model or authenticated external evidence. **PENCIL/PEN commitments remain unchanged; authority always NONE.**

## The question

Can a task-conditioned system select **zero, one or several** different geometric thought-space lenses, explain why it spent the visualization budget, explicitly decline pictures when evidence is insufficient, and reconsider an unhelpful view without treating its coordinates as truth?

This builds on the existing [THOUGHT-006/010 RFC](../../docs/THOUGHT-FIELDS-006-010-FULL-STACK-RFC.md) and THOUGHT-008's source-only graph primitives. It does not add a neural network or open-ended natural-language thought recognition.

## Implemented interfaces

`Task(goals=(...), anchor=None, max_views=2, show_geometry=True, phase='ABSTRACT_PENCIL', seed=0)` accepts **typed operator-supplied goals** from `association`, `dependency`, `tension`, `affordance`, and `inventory`. The phase is one of `ABSTRACT_PENCIL`, `CONCRETE_PENCIL`, `PEN_REVIEW`. All fields are validated and bounded.

`ViewRouter(ThoughtViews(field_snapshot, attributed_relations)).run(task, previous=None)` returns a deterministic **source-only answer**, a set of evidence-grounded `QUESTION_ONLY` prompts, scoring and abstention decisions, and at most `max_views` visual projections. Available visualization lenses: association, dependency, tension, affordance, plus NONE through inventory/abstention. The flower-hex view remains available in THOUGHT-008 as an explicit experimental display choice; it is **not prioritized by this evidence-driven router** because it provides no independent relation evidence.

`ViewRouter.reconsider(task, previous, unhelpful_lenses, reason)` lets an operator or external validator mark one or more previously selected lenses as unhelpful and **switch to the next eligible lens**. This does not learn a model or infer an objective outcome. It records declared feedback with the prior receipt digest. If underlying source evidence changed, previous feedback cannot silently be reused; the router requires new review. The idea of automatically assessing its own utility is not implemented.

## Selection policy (transparent classical heuristic)

1. Read the same **typed source evidence index** THOUGHT-008 already provides with no geometry. Preserve IDs, originating relation strings and source digest.
2. For each requested goal compute an *inspection signal*: authored association bridge-question count; dependency authored-edge count; contradiction count; or conditional reachability count from an explicit anchor. Signal **does not measure truth, confidence, or importance**.
3. Rank eligible lenses by capped signal count (max 4), then by requested goal order; spend the maximum number of view units permitted, and record which candidates were deferred. A visual view costs **one abstract view unit**; this is not a measured CPU time or a claim about user benefit.
4. **Abstain** on inventory, absent evidence signals, `max_views=0`, `show_geometry=False`, or `PEN_REVIEW`. The latter is an *inspection phase label*, not a call to THOUGHT-006 `.commit()`.
5. Generate question prompts directly from authored common-neighbor paths, prerequisite cycles, contradictory claims, and conditional affordance requirements. They are always `QUESTION_ONLY`; **the exact same questions are available in the no-map control**. Positions do not enter the question generator.
6. Never insert new relationships, alter THOUGHT-007 source logs, update PEN, certify independent roots or trigger outside actions.

### Sample cycle

- ABSTRACT_PENCIL, visual budget zero: same typed answers, zero projected geometry.
- ABSTRACT_PENCIL, budget three: association, dependency, tension selected; affordance deferred when its inspection signal ranks lower.
- PEN_REVIEW: no geometry, same source and questions; **no commitment performed**.
- On declared operator feedback, one unhelpful lens may be replaced with another that already had a typed signal; the underlying evidence stays unchanged.
- A later input digest change requires revalidation of prior-cycle conclusions.

## Scientific controls / what would falsify this

The **no-map comparator** runs the same source index and question generator with `max_views=0`. Other possible controls are fixed association/spring, fixed flower-hex, and always-all geometry, but **no claim of superior answer accuracy** is made here: in this prototype, every mode produces exactly the same evidence-grounded answers. The only demonstrated resource distinction is **how many projections were constructed**. Counting view units is not runtime/energy benchmarking.

`benchmark.py` defines 11 synthetic development cases including evidence-free abstention, target-specific visualization, mixed-task routing, budget exhaustion and no-anchor affordances. These cases were authored alongside the heuristic (not blind or preregistered). They compare selected lenses, projections constructed, source parity and zero invented graph edges, and report limitations. A failed case exits non-zero. The 17 unit tests check replay/source invariance, operator opt-out, feedback rerouting, invalid input, PEN separation, and stable questions after layout change.

**Mandatory falsifiers:** any geometric closeness creates a supported relationship, a `HYPOTHESIS_ONLY` input counts as source proof, a contradictory statement is silently resolved, two manifests with the same label collapse, PEN changes from rendering, or no-map answers differ from multi-map answers. If the router offers no utility relative to the no-map alternative in human-judged trials, keep no-map as default.

**Unverified:** Whether any representation improves the user's comprehension or increases quality/coverage of reasoning; an open-ended agent's ability to classify natural-language tasks; adaptive learning from real feedback; reliable utility/cost prediction; robust behavior on real evidence; proof of source independence. These demand held-out, externally judged tasks and real cost measurement.

## Reproduction

From repository root:

```sh
cd experiments/thought-009
python -m unittest -v test_router.py
python benchmark.py
python demo.py
```

The workflow also runs THOUGHT-008 and THOUGHT-007 regression tests and uploads machine-readable benchmark/demo receipts.

## Next door: THOUGHT-010

A versioned, read-only JSON interface for optional JAR;VIS/Free Graph querying and reviewing thought fields, with explicit identity binding, permission checks, receipts, privacy constraints and no live writes by default. Real multi-turn interaction must distinguish task intent from evidence, track source changes, and require human authorization for any external system effects.
