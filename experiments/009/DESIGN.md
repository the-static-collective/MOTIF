# MOTIF-009 — THE EXPERIMENTER
## Let decision trees become cartridges that ask for evidence

**Hypothesis:** After reading some before/after graph observations, MOTIF can assemble an inspectable decision-tree *cartridge*, use disagreement and under-sampled decision branches to choose what to investigate next, then improve its predictive understanding with a fixed observation budget.

**Implementation status:** executable, tested, Python-standard-library **synthetic research**. No real-world intervention, network action, human consent verification, signature authentication, autonomous tool invocation, causal identification, neural learning or verified external evidence.

### The vertical

MOTIF-008 found that an ordinary two-bit classical decision tree matched the graph learner's predictive accuracy in controlled unfamiliar worlds. MOTIF-009 does **not** ignore that result.

**It adopts the tree as a portable cognitive cartridge.** A tree is not a competitor to be defeated here; it is a useful bounded method that MOTIF can inspect, store, exchange, test and deploy *inside the simulation*.

\`\`\`text
observations (before/after)
        |
        v
   learn tree cartridge
       /         \
  question A?    question B?
       \         /
        \       /
         [one of four leaves]
             |
    learned example counts
             |
    uncertain / sparse branch?
             |
  candidate unlabeled graph pool
             |
  committee disagreement + sparse leaf
             |
  choose ONE observation ticket
             |
    INDEPENDENT EVALUATOR
    reveals only that answer
             |
   revise next tree cartridge
             |
  test on untouched hidden outcomes
\`\`\`

A **cartridge** is a typed JSON structure with a schema, two transparent graph-motif questions, four Boolean leaves, observed leaf class counts, an in-sample performance statistic, an opaque source evidence digest, and a content checksum. Every graph motif is role-relative rather than tied to a particular participant or object name.

The questions can be single edges or composed two-edge existential joins. The leaf logic permits conjunction, disjunction and XOR within the two-bit decision space; this is a classical tree, not a new model architecture.

The in-sample leaf probabilities are simple Laplace-smoothed *heuristics*, **not calibrated probabilities**.

### A literal cartridge you can inspect

The checked-in [example-tree-cartridge.json](example-tree-cartridge.json) is an actual CI-generated portable cartridge learned on the **synthetic XOR world**, not a hand-drawn design.

It holds two role-relative unary questions over opaque graph predicates, with four Boolean leaves:

```text
                         TREE CARTRIDGE
                      /                  \
          property present for target?    property present for actor?
                       \                /
                        \              /
                 [false, true, true, false]
```

This leaf table represents **exclusive OR**: success is predicted when exactly one tested property holds. The abstract predicate names are produced by the synthetic world, so the cartridge has not interpreted their meanings.

The artifact includes source-claim evidence counts, a semantic ID and checksum. It is inspectable, transferable as JSON, and defaults to **HOLD** at a receiving bay. The separate [cartridge_demo.py](cartridge_demo.py) reproduces it, performs a local read-only review, and proposes the next *unlabeled* observation ticket.

**One important distinction:** the cartridge itself predicts; the *experimenter* chooses what to observe next based on cartridges' disagreements and sparsely supported branches. It does not turn graph predicates into real-world executable operations.

### Portable but not authoritative

[cartridge.py](cartridge.py) contains the source-defined **CartridgeBay**.

\`OFFER\` → \`HOLD\` → \`LOCAL DATA REVIEW\` → \`ADMIT_PREDICT_ONLY / REFUSE\`

A locally offered cartridge cannot be used as an admitted predictor until a receiving environment explicitly records its review, and a separate local observation set supports a minimum accuracy. Revocation blocks additional admitted use.

Even after admission, the only ability is **read-only inference** from a presented graph. No graph mutation, real-world action, personal-data access, authority grant, network dispatch or human permission follows.

The JSON checksum detects changes but **does not authenticate who authored the cartridge**. An attacker can rewrite and rehash it. Source digest is not a signature. A cartridge with unknown or incompatible predicate vocabulary requires explicit local adaptation and evaluation, rather than being treated as proof that cross-domain transfer works.

**Cartridges may transfer methods, not operational rights.**

### The active inquiry experiment

[experimenter.py](experimenter.py) accepts only:

- Previously revealed synthetic before/after observations.
- Candidate questions consisting of a ticket, an unlabeled graph and the graph's explicit actor/target role bindings.
- A committee of three separately fitted tree cartridges.

It cannot import the oracle module or access the hidden family, rule implementation or unrevealed outcomes.

The question selector scores each candidate by **committee disagreement**, sparsity of the primary cartridge's destination leaf, a heuristic leaf uncertainty and structural novelty. These are **heuristics**, not proved information gain.

The hidden-world evaluator has the observation records. It resolves the chosen ticket and releases **one** independently generated synthetic before/after record. The selector revises its cartridge and asks again.

This is **pool-based active observation selection**, **not a physical intervention**. The graph pool is visible without labels; a real agent would need consent and authority to collect or change any external data.

### Matched-budget experiment

The evaluation is conducted on MOTIF-008's six opaque-predicate rule families and five fixed seeds, giving **30 independently seeded synthetic worlds**.

Two strategies receive the same initial observations and exact same total budget:

| Strategy | Query selection | Model used |
|---|---|---|
| Active tree cartridges | Three-tree disagreement, sparse leaves, novelty | Two-question tree cartridge |
| Random control | Seeded random selection from the same unlabeled pool | The exact same two-question tree learner |

Both strategies are tested on the same **80 held-out observations per world**, whose labels are never used for selection.

Two distinct protocols are preserved:

1. **v1 initial protocol:** 16 initially revealed observations; 12 additional questions from 96 unlabeled candidates. This reached a predictive ceiling immediately: see [v1 results](experiment-results-v1.json).
2. **v2 post-hoc stress protocol:** 6 initially revealed observations; the same 12 additional question slots. This was introduced **after** inspecting the v1 ceiling effect, and is explicitly *not* independently preregistered. Run \`python stress.py\`; see [v2 stress results](experiment-results-stress.json) when checked in.

Results always include both strategies, initial and final accuracy, per-family outcomes, world-level wins/ties/losses, individual question tickets, their predicted outcomes before revealing the label, and the actual label after reveal. **Negative and null findings are never dropped.**

### v1 observed results: a necessary ceiling result

The original CI reproduction showed:

| Metric | Active cartridges | Seeded random |
|---|---:|---:|
| Mean held-out balanced accuracy at 16 known labels | 0.9822 | 0.9822 |
| At 22 known labels | 1.0000 | 1.0000 |
| At 28 known labels | **1.0000** | **1.0000** |
| Worlds where active outperformed random | **0** | — |
| Worlds tied at final budget | **30 / 30** | — |

The original generator is too easy for a competent two-question tree: **active selection demonstrated no improvement over random acquisition**. A ceiling result is a useful falsification of the belief that more sophisticated selection necessarily helps.

Do not describe these results as a discovery of autonomous curiosity or improved sample efficiency.

### v2 post-observation stress results: a detectable early effect

After seeing the v1 ceiling, the development stress protocol reduced the initial revealed observations from **16 to 6** while preserving the same 12-question budget and all six generator families, 5 seeds and 80 held-out test episodes per world.

| Labeled examples per world | Active mean balanced accuracy | Random mean balanced accuracy |
|---|---:|---:|
| 6 (before further questions) | 0.6169 | 0.6169 |
| 12 (6 new observations) | **0.9876** | **0.9025** |
| 18 (12 new observations) | **1.0000** | **0.9943** |

Final results across 30 worlds: **active won 1, tied 29, lost 0**. The early (6-additional-observation) advantage was **0.0851 mean balanced-accuracy points**. By the final budget, most of that difference vanished.

This is **a small, post-hoc synthetic stress result**, not independently preregistered evidence of a generally superior active-learning method. The toy generator remains easy for a shallow tree, and the early gap could reflect the particular frozen seeds, query-selection heuristic and finite observation pool. A stronger benchmark must repeat the result on genuinely different, harder worlds with more seeds, an information-gain baseline, and a locked design.

The full per-seed and per-question outputs for both protocols are retained; neither the original null result nor the stress result replaces the other.

### A strong falsifier is better than a flattering story

The real research frontier is to evaluate whether tree-guided inquiry becomes useful **when evidence is actually scarce, observation is costly and plausible hypotheses disagree**.

The next laboratory should:

1. Generate genuinely competing world models with partially hidden states and several causally different explanations.
2. Select **which intervention to perform** in a safely isolated synthetic world, not only which pre-generated observation to reveal.
3. Measure answer quality *per observation requested*, on frozen independently generated test worlds.
4. Compare tree committees to random, uncertainty sampling, greedy information gain, random forests and Bayesian active-learning baselines.
5. Allow explicit predicate remapping only through a local review and separate holdout. No blind reliance on opaque names.
6. Preserve error histories, refused import attempts, disagreements and all permission boundaries.
7. Transfer cartridges across new domains while keeping their raw personal/source observations local, and measure both beneficial transfer and harmful negative transfer.

### Reproduce

\`\`\`sh
cd experiments/009
python -m unittest -v test_experimenter.py
python benchmark.py   # original v1 protocol
python stress.py      # separately identified post-hoc stress protocol
\`\`\`

No paid API, model download or additional Python package is required. The GitHub Actions workflow executes and logs every experiment, and saves complete seed-level synthetic receipts in the branch.

**A working decision tree is a usable cartridge. A cartridge is not proof of intelligence. A good question is one that demonstrably buys better evidence, not simply one that sounds insightful.**
