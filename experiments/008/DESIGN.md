# MOTIF-008 — THE UNKNOWN WORLD
## Stop feeding the learner the answer. Freeze unfamiliar tests and find out what transfers.

**Research question:** Can a relational learner infer a useful structural condition from a limited number of unfamiliar synthetic before/after observations, including failed attempts, and predict the outcome of previously unseen graph configurations?

**Result type:** a **controlled symbolic learning benchmark** against three matched-information baselines. The benchmark does **not** prove a new neural architecture, open-world intelligence, cross-domain zero-shot transfer, physical causal understanding, or autonomous exploration.

## The laboratory boundary

The experiment has three files with distinct responsibilities.

- [oracle.py](oracle.py) creates simulated worlds using **six hidden outcome rules**. It alone knows the hidden rule family. Every world has a distinct opaque relation vocabulary, fresh entity identities per episode, and three nonoverlapping samples. The oracle's \`before\` and \`observed_after\` graphs are immutable.
- [learner.py](learner.py) imports **no oracle implementation**. It receives role bindings and synthetic graph snapshots only. It derives whether the attempted synthetic transformation changed the graph by comparing before/after; no direct success label or hidden flag is supplied.
- [benchmark.py](benchmark.py) is the evaluator. It alone combines oracle-created synthetic observations with the learner and can examine hidden-rule family names, frozen test examples, and scores.

Every learner trains **from scratch within each synthetic world**. This is a few-shot *within-world* adaptation study, **not** zero-shot inheritance of knowledge from one world to another. The shared program has a manually designed graph-motif grammar, and the entire experimental ontology remains two abstract roles: actor and target.

## Six unfamiliar simulated rule families

The oracle uses disjoint opaque relation names per world, rather than meaningful labels like \`ready\` or \`compatible\`. Across worlds the hidden success rule is one of:

| Family | Hidden synthetic relation condition | Model family coverage |
|---|---|---|
| direct | A direct actor-to-target edge exists | 1-edge features can express it |
| forward_join | Two edges share the **same** intermediary, actor → x → target | 2-edge structural motif |
| reverse_join | Two edges share x in the reversed path, target → x → actor | 2-edge structural motif |
| conjunction | Two independent relevant role facts are both present | conjunction of single edges |
| hybrid | A forward joined path **and** an actor condition both exist | conjunction of joined and single-edge motifs |
| xor | Exactly one of two conditions is present | deliberately outside the learner's positive-conjunction grammar |

False joined cases contain both source predicates and both edge halves, but **the wrong intermediary** is connected. This prevents the learner from solving joined tasks by recognizing that two relation names are present.

All families share the same generator and two-role ontology. This is **not six independent real-world domains**. The family names and their generating rules are known to the evaluator/developer, and the tests are synthetic by construction.

### The data split

Predeclared v2 synthetic protocol:

- 6 rule families × 5 world seeds (11, 23, 37, 41, 59) = **30 worlds**.
- Per world: **48 training episodes**, **24 validation episodes**, **80 test episodes**.
- Total 4,560 simulated attempts and 2,400 held-out outcome classifications.
- Every episode uses fresh entity names. Predicate vocabulary is namespaced by an opaque digest of each world identity and checked for collisions.
- Model selection has access to training and validation, **not** test labels.
- Tests rewire one shared intermediary while leaving all visible predicate names and facts-per-relation consistent. The hidden oracle outcomes flip. This is an intervention **inside programmed graph rules**, not causal evidence about the physical world.

**Protocol correction:** early v1 generated predicate names by independently sampling a finite shared pool of 2,000 words. That did *not* guarantee distinct vocabulary across worlds. We corrected the benchmark to explicit namespaced opaque predicates and recorded the changed protocol as **v2**. The model still uses the same relational grammar. The v2 benchmark is development-locked, **not an independently preregistered scientific study**.

## The learner

Input:

\`[(observed_before_graph, proposed_actor_target_binding, separately_supplied_observed_after_graph), ...]\`

Representations:

- Single-edge conditions: unary actor/target facts and direct actor-target edges.
- Directed two-edge motifs with shared existential witness \`x\` (forward and backward).
- Conjunctions of at most **two** candidate motifs (up to four graph edges total).

Selection uses supervised outcomes **derived from** synthetic before/after changes, then chooses among candidate conditions using validation balanced accuracy, training balanced accuracy and structural complexity. It exposes its candidate-search cap and abstains unless validation balanced accuracy reaches **0.90** or better. Sparse class evidence causes explicit abstention.

It does not see hidden flags, the oracle's internal functions, test labels or real-world truth.

**This is a symbolic feature/rule learner.** It is not an LLM, GNN, transformer, Bayesian program learner, causal discovery engine, or new trainable weight architecture. Relation IDs remain manually supplied by the generator, not inferred from raw perception.

## Matched-information baselines

Every method gets the **same training and validation episodes**, with identical holdout worlds.

1. **Majority:** predict the training majority outcome on every test instance. Reports balanced accuracy.
2. **Single-edge relational rule:** choose the best *unary/direct-edge* feature based on training and validation, no shared-intermediate join and no conjunction. Reports held-out balanced accuracy.
3. **Classical two-bit depth-2 decision-tree baseline:** searches the **same full feature grammar** as the MOTIF rule learner, including joins, and learns Boolean leaf predictions from the same training data. This is a deliberately **stronger baseline** capable of representing XOR. Sparse evidence triggers an explicit constant-prediction fallback.

Do not compare a covered-only score from the abstaining learner with the baseline's all-world average as if they have the same denominator. Report coverage, failures, and per-family results in addition to conditional accuracy.

## Reproduce

Python 3.10+, **no dependencies**, no paid API:

\`\`\`sh
cd experiments/008
python -m unittest -v test_unknown.py
python benchmark.py
\`\`\`

GitHub Actions repeats all seven earlier MOTIF experiment suites, runs the eighth suite, and prints a complete seed-level JSON result receipt with markers in its CI logs. A copy of that result is archived in [experiment-results.json](experiment-results.json).

**The tests do not certify neural intelligence**; they verify synthetic protocols, isolation, deterministic generation, feature matching, intervention semantics, abstention and result transparency.

## What a positive result would mean

If the relational learner reliably predicts changes in **unseen synthetic graphs with unseen entity IDs and opaque predicate names**, while withholding its predictions on outcomes outside its grammar, that is evidence for *invariant symbolic pattern recognition* under these generator conditions.

The strongest result is not automatically the most scientifically interesting. If an ordinary two-level decision tree with access to the same graph features matches the learner, MOTIF has **not** demonstrated an advantage over a well-specified classical baseline.

A fully unfamiliar environment would require object types, relations, physics, time, embodiment, sensing gaps and governing goals that were not hand-designed to match the candidate grammar.

## The next falsifiers

- **Genuine cross-world transfer:** train reusable structural priors on some domains, freeze them, and test faster learning on held-out domain *families*, not merely their names.
- **Structural distribution shift:** vary graph degree, arity, missing edges, nonlocal prerequisites, hidden noise and nonlinear rules the learner has not seen.
- **Independent causal interventions:** test actual alternatives that break confounding instead of assuming predictive motifs are causal.
- **Active experimental design:** permit the model to request a bounded next *synthetic observation*, measure information gain and compare with random and uncertainty sampling.
- **Calibration:** measure prediction probability and abstention quality; current confidence threshold is a validation accuracy gate, not calibrated probability.
- **Full planning:** convert inferred transition hypotheses into verified-bounded, multi-step policy comparisons with matched classical planners.
- **Neural alternative:** compare a small learned relational/GNN world model under equal evidence and compute rather than asserting architectural novelty.
- **Real authority:** any real interoperability with reLATTE, JAR;VIS or GHoT requires human-stewarded, explicitly authorized crossings. The synthetic before/after record is neither human consent nor real-world observation.

## The research boundary

\`CORRELATION != CAUSE\`

\`OPAQUE NAMES != UNKNOWN PHYSICS\`

\`IN-WORLD FEW-SHOT != CROSS-WORLD ZERO-SHOT\`

\`HELD-OUT SYNTHETIC GRAPH != REAL-WORLD GENERALIZATION\`

\`CONDITIONAL ACCURACY != OVERALL ACCURACY\`

The success criterion is **improving predictions or useful decisions under stronger, genuinely unseen conditions and matched baselines**. If MOTIF cannot do that, the model should not be described as a new form of intelligence.
