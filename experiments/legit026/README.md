# MOTIF-LEGIT-026 — THE METHOD MIRROR

## Can a research machine improve how it discovers questions?

**Status: RESEARCH HOLD. Stacked draft, not merged.**

LEGIT-025 demonstrated selecting a five-node homomorphism-source question
after all old four-node sources proved observationally insufficient. It
also preserved the actual parent/extension recipe, rather than falsely
claiming new mathematical graph theory.

LEGIT-026 changes what is being modified: instead of selecting one
source graph, it modifies the **program that selects source-graph
questions**, validates candidate programs on several training worlds,
and then freezes the best supported program for future challenges.

### 1. The actual self-critique

Inherited method:
`LEAF_FIRST` (favor four-node sources extended by one pendant vertex).
Problem: the rule may accidentally overfit and fail to prioritize probes
that generalize to graphs from a different population.

Research question:

> Would removing or changing the leaf bias, priority score or
> residual-feedback rule give a more transferable research procedure,
> rather than just a better answer to the original graph pair?

### 2. A typed rewrite grammar

The controller can propose exactly 24 source-selection programs, with
three separately editable parts:

| Subprogram | Choices | Interpretation |
| --- | --- | --- |
| Operator gate | Leaf-first, all sources, nonleaf-first, tree-first | Which kinds of candidate graph extensions deserve early inspection? |
| Evaluation of a question | Total distinguishable training pairs, world-balanced distinguishability, diversity of observed target hom counts | What makes a question likely to reveal structure? |
| Updating after a result | Static ranking, residual-learning greedy | Do unsuccessful/solved questions change later priorities? |

Every competing program still has access to **all 21 connected
five-vertex source patterns**. No method has a stronger final grammar.
Unused sources are included as fallback. No arbitrary generated code,
`eval`, network connection or unrelated project authority is involved.

The candidate programs and their mutations are engineer-defined
search hypotheses. This is **not** the autonomous invention of a new
algorithm language. All experiments and limitations are inspectable.

### 3. Training environments and internal validation

Use only known or newly generated **training** graph pairs where every
old four-node source probe fails:

- Four external Atlas carrier pairs from LEGIT-025's prior training set.
- Eight previously inspected LEGIT-025 seeded 8-node pairs (seed 25025).
- New G(8,1/2) worlds with fixed training seeds **26001** and **26002**,
  each generated from 1,000 labeled graphs and filtered using *only*
  the old four-node source outputs.

The 24 policy programs undergo **leave-one-training-world-out** testing.
Each time, a method is fitted on three worlds and evaluated on the
fourth. Selection uses averaged per-world query counts plus a tiny
fixed complexity penalty (0.02 per program edit).

If the selected rewrite fails to beat the parent *on training-world CV*,
the controller refuses the change and retains the original program.
The selected policy is then fitted on all four training worlds.

The same research corpus is available to a strong tuned conventional
all-source greedy planner and an **exact finite training question-order
dynamic-programming optimizer**. Their objective is limited to these
known finite training cases; they are not claimed to dominate future
research.

### 4. Freeze before future evaluation

All five matched methods use exactly the same 21 sources:

1. Prior LEGIT-025 frozen operator-first method.
2. Classical greedy method trained on all four worlds.
3. The method-mirror's CV-selected and (if justified) adopted policy.
4. Canonical complete five-source ordering.
5. Exact training-optimal classical DP question ordering.

A SHA-256 digest freezes all five orders before any future-seed data
are accessed.

### 5. Different future research worlds

- Previously known Atlas six-pair heldout serves **regression only**,
  *not* independent evidence.
- Two graph populations with previously unused fixed seeds **26003**
  and **26004** are generated *after* training/freeze; each draws 1,000
  new labeled 8-vertex random graphs and chooses up to eight pairs
  conditioned on the same old four-node blind spot.

The new task carrier populations are separately generated and not
derivatives of the Atlas carriers, but they are **engineer-authored
under the same generator**, not independent authorship, a truly blind
study, an unconditioned random task distribution, or a new mathematics
domain.

During evaluation, every attempted graph-hom question, including each
negative one, is independently recalculated using the exhaustive
vertex-assignment oracle from LEGIT-021. We record all questions,
per-case traces, successes/holds, and CPU including verification costs.

### Measured result: first verified meta-policy rewrite

From the original 24 engine-authored policy programs, leave-one-training-
world-out validation selected a **one-component edit**:

`LEAF_FIRST + GAIN_ALL + STATIC`
→ **`LEAF_FIRST + COUNT_DIVERSITY + STATIC`**.

That changes how MOTIF judges the usefulness of a proposed mathematical
question: instead of prioritizing how many already-labeled training
pairs it separates, it prioritizes how many distinct exact count values
it reveals among training graphs. The source construction rules and
eligible source graphs remain unchanged.

The CV mean fell from **1.25 to 1.21875 questions/case** over the four
training-world folds. The predeclared 0.02 per-edit complexity penalty
still permits promotion (1.25 vs 1.23875). This is a tiny gain, not
reliable proof of a broad improvement.

**New preselected eight-vertex worlds (not Atlas derivatives):**

| Method | 26003 (8 pairs) | 26004 (8 pairs) | Combined |
| --- | ---: | ---: | ---: |
| Frozen LEGIT-025 method | 18 | 14 | 32 |
| Canonical classical enumeration | 24 | 24 | 48 |
| Strong trained classical greedy | 10 | 9 | 19 |
| Exact finite train-optimal classical DP | 10 | 9 | 19 |
| **LEGIT-026 question-policy rewrite** | **10** | **9** | **19** |

Every method solved all 16 tasks with independently checked exact
homomorphism-count witnesses. The new meta-policy required **13 fewer
queries than the previous MOTIF strategy (32→19)**, but **did not beat
either strong classical comparator**. That is the correct scientific
boundary. CPU measurements are very small and affected by verification
overhead; don't interpret this table as a general speed benchmark.

The six previously inspected Atlas holdout pairs are regression cases
only. All strong trained policies and both MOTIF policies solved them
with six questions.

**Durable artifact:** `generated/selected_meta_cartridge.json` records
the precise edit, its training-world selection, frozen SHA-256 of all
five method orders, previous/future measurements, source CI run and
full raw artifact digest. An automated test recomputes and checks its
contents against actual training.

**Verification:** 9 original adversarial tests, plus cartridge-replay
test in final revision. Green parent run was GitHub Actions
`42746241643`; refer to the final branch run for the extra test.

**Important naming distinction:** the abstract CV "parent program" uses
a typed leaf-first policy with a global training score for all probes.
The **actual** legacy strategy from LEGIT-025 is independently loaded as
`PRIOR_025_FROZEN` and benchmarked separately. These are not identical
ordering programs, and their results must not be conflated.

### Interpretation rules

A verified result can establish that a frozen policy learned from
several training worlds transfers better or worse than its predecessors
on this particular graph population. It cannot establish autonomous
general math invention, statistically reliable wins from two seeds,
multi-generation improvement, or a historically new theorem.

An effective mathematical **method of asking questions** must itself
be open to revision; a refusal to promote an unsupported revision
counts as a valid experimental outcome.

### Reproduce

```sh
python -m pip install --only-binary=:all: networkx==3.4.2
python -m unittest discover -s experiments/legit026 -p 'test_*.py' -v
python experiments/legit026/meta.py --emit > /tmp/motif-legit026-method-mirror.json
```

GitHub Actions retains a downloadable audit artifact containing the
full training matrix, all 24 candidate-program cross-validation folds,
the frozen program hash and all independent future-question receipts.

**RESEARCH_HOLD_NO_GENERAL_AUTONOMOUS_SELF_IMPROVEMENT**
