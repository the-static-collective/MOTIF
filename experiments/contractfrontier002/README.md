# MOTIF CONTRACT-FRONTIER-002 — Discover conditional, topology-dependent contracts

**Status:** executable finite synthetic graph experiment, proposal-only general claims, no real-world actions or autonomous repository modifications. Built on unmerged `CONTRACT-DISCOVERY-001`, NUNUMATHAL graph data, and FIR admission.

## MOTIF's next question

> Having found a linear relation among five anonymous channels, can I discover a useful law involving graph topology and conditional behavior, then build an executable bridge to an unfamiliar input port?

This experiment deliberately **does not tell the learner which law to find**. It supplies a finite, authored grammar of **313 candidate programs** over 12 graph features, including degree, edge counts, two-edge path counts, and reachability indicators. The learner chooses its own synthetic `add_edge(a,b)` intervention from a fixed, train-only pool by expected version-space disagreement. Only after choosing does it obtain the two graph-output changes from the real `contractdiscovery001.apply()` and `nunumathal.Graph` implementation.

It uses classical hypothesis elimination, *not* a trained language model or unrestricted algorithm invention. Its expression language is linear in the supplied features; the resulting laws are nonlinear/conditional **in the raw graph adjacency relation**. Both the common-neighbor counter and the connectivity predicate were manually implemented and included among candidate features. The system **does not invent these graph features**.

### Observed results

From the frozen deterministic sample, active inquiry identified unique surviving expressions after **three** readout-bearing interventions:

```text
Δ(number of triangles) = common_neighbors(a, b)
Δ(number of connected components) = connected(a, b) - 1
```

For adding an absent edge `(a,b)` in a *simple undirected graph*, the first formula counts newly closed triangles and the second determines whether two components merge. The rules were mathematically known long before this experiment. The result is a bounded *recovery* of known relationships from permitted observations, not novel mathematics.

- 100/100 independent held-out graph interventions: both port outputs correct; 100/100 independently recomputed outcomes.
- 100/100 out-of-distribution larger/different graph interventions: both outputs correct; 100/100 independently recomputed outcomes.
- A true coarse-statistics counterexample: two 6-vertex graphs with the same `(V,E,C,I,β)`, same endpoint degrees and connectivity have `Δtriangle` **1 versus 0**. No function of those coarse inputs alone can answer both cases.
- A deliberately type-correct `+1` corruption of the triangle readout is caught by the independently recomputed contract, but the model cannot authenticate an external source or detect a perfectly co-corrupted measuring instrument.

### Fair controls

The same 313-program version space and identical graph training pool were given to 30 classical random-probe searches:

| Method | Unique exact laws located within budget |
|---|---:|
| Active, 3 readout-bearing interventions | **1/1** run |
| Random, 3 interventions | **1/30** seeds |
| Random, 8 interventions | **25/30** seeds |

Random at an 8-intervention budget uses a mean of **5.8** readout-bearing probes across 30 runs, including unsuccessful runs. A **strong handwritten topology formula** matched all **200/200** test and OOD cases, tying the learned law; a weak constant-zero baseline got 32/200. This is evidence of sample-efficiency on this predeclared candidate pool, not a novel active-learning strategy.

### No answer-label leakage

Probe selection receives only **source graph + possible action**; it is not allowed to call the post-intervention outcome instrument before choosing. A test patches the outcome function to raise during selection to enforce the interface. Training observations filter the hypothesis space; validation is reserved until a candidate is uniquely identified, and test/OOD are opened only after freezing it. Each output stores digests and question/action receipts.

### Child construction

The `build_child` method replays the pinned source training and validation evidence, emits a fixed Python interpreter containing the inferred expressions, pins **four actual source files**, and executes the child in a separate Python process. The child reads an independently chosen holdout graph and reconstructs two typed output ports. An unvalidated or forged law, corrupted source, mutated child, or invalid index is held.

A second process is **not a security sandbox** for untrusted Python; the experiment assumes a trusted repository checkout. Source hashes detect modification, not authorship. The child cannot modify live MOTIF components, write GitHub branches, or dispatch external actions.

### FIR/nunuMATH status

A finite held-out computation may receive `F_LOCAL` under the declared test scope. A universal generalization claim remains **I**. The source universe is finite *simple, undirected graphs* with only the enumerated edge-addition action. It has no proof-term checker and does not discover unseen feature vocabularies, causality, biological or human semantics, or independently authenticated data.

## Reproduce

Full stacked MOTIF checkout, standard-library Python 3.10+:

```bash
cd experiments/contractfrontier002
python -m unittest -v test_contractfrontier.py
python contractfrontier.py
python benchmark.py
```

## Next question generated by the controller

> Which higher-order graph relations survive changes to the **feature grammar itself** and tests on genuinely independent world families?

The promising next hostile experiment is removing authored feature predicates, synthesizing graph-pattern counters instead, and comparing with classical inductive logic programming / relational program-synthesis baselines. None of that is claimed in this version.
