# MOTIF-010 — THE SCIENTIST
## Decision-tree cartridges propose interventions that distinguish rival explanations

**Question:** When passive observations cannot distinguish multiple explanations, can MOTIF select a bounded simulator experiment whose possible outcomes separate them?

**Status:** Executable standard-library Python, *completely synthetic*. No physical interventions, real-world permission or external actions, causal discovery from uncontrolled data, or learned neural architecture.

## The architecture

MOTIF-009 selects which *preexisting unlabeled observation* to reveal. MOTIF-010 asks for a **new intervention**, executed only after the question is chosen. The simulator and learner are separate:

- [oracle.py](oracle.py) contains the evaluator-only hidden rule, graph world creation, natural observation regime and \`intervene(spec, portA, portB, serial)\` operation. The learner cannot import the oracle.
- [scientist.py](scientist.py) sees previous before/after graph evidence and a public schema describing two controllable Boolean input ports. It constructs a version space of **real MOTIF-009 \`Cartridge\` objects** representing possible two-question trees, selects an informative control setting, and revises its surviving explanations after the evaluator provides the independent synthetic result.
- [benchmark.py](benchmark.py) executes the chosen synthetic intervention, tracks its costs and outcomes, and tests the surviving explanation on independently generated held-out settings.

### The confounded world

The synthetic natural regime always presents \`A=B\`: either both controls are false or both are true. Four hypotheses can fit those observations equally well: the outcome depends on A, on B, on A AND B, or on A OR B. Other hidden mechanisms (XOR and equality) exhibit their own observational equivalence class.

The learner is **not told these mechanism names**. It enumerates all 16 Boolean truth tables over two variables (a deliberately handcrafted, complete small grammar), filters trees contradicted by observed before/after graph changes, and assigns real MOTIF-009 cartridge definitions to the survivors.

A controlled \`do(A=0,B=1)\` experiment breaks the natural correlation. Rival cartridges predict opposite results. After one such intervention, the version space contracts from four to two; a second intervention \`do(A=1,B=0)\` distinguishes the remaining two.

The simulator computes a fresh event **only after** a candidate intervention is selected. It does not reveal a cached labeled observation from a fixed pool, unlike MOTIF-009.

### Information-gain selection

If \`p\` of the surviving trees predict success under a proposed setting, and each tree has equal prior weight with deterministic noiseless outcomes, the expected information gain in bits is

\`IG = -p log2(p) - (1-p) log2(1-p)\`.

The scientist chooses the available setting with maximum gain and refuses to invent a useful query when all remaining trees agree. This is **classical version-space information gain**, not a novel algorithm.

A cartridge is a bounded and inspectable two-question tree: structural role-relative predicates, four possible leaves, observation counts, and an unverified content digest. It can be exported as the portable MOTIF-009 JSON format. A tree is a hypothesis, not an independently observed fact or an executable external tool.

## An actual scientist cartridge and inquiry transcript

[Open the generated two-step intervention transcript](example-scientist-interventions.json). This artifact was produced by the GitHub Actions simulator, not assembled by hand, and the test suite checks its exact reproducibility.

In the synthetic XOR world, the learner starts with **four** indistinguishable tree-cartridge hypotheses. It proposes:

1. \`do(A=false,B=true)\` — expected gain **1 bit**; the independently computed simulator outcome is **success**; two hypothetical trees survive.
2. \`do(A=true,B=false)\` — expected gain **1 bit**; the simulator again reports **success**; one tree survives.

Its final exported decision-tree cartridge has four leaves \`[false,true,true,false]\`, so it predicts success exactly when one of the two synthetically controlled inputs is present.

The transcript stores the input settings, rival tree IDs and votes **before** each result, observed graph outcome, remaining hypothesis count, final cartridge and an explicit \`real_world_authority=false\` declaration. None of the simulated world states or observations are modified by recording it.

## Controlled comparisons: actual measured results

[The reproducible CI receipt](experiment-results.json) includes all 60 synthetic worlds and every individual question. The protocol covers six hidden rule families × ten seeds. All four methods receive the same two initial natural observations and **exactly two further observations**.

| Outcome after two further observations | Scientist | Random | Fixed diagnostic | Passive natural |
|---|---:|---:|---:|---:|
| Worlds with one exact model identified | **60/60** | **12/60** | **60/60** | **0/60** |
| Mean held-out prediction coverage | **1.0000** | **0.7667** | **1.0000** | **0.5000** |
| Errors among predictions where surviving trees agree | 0 | 0 | 0 | 0 |
| Extra observation budget | 2 | 2 | 2 | 2 |

**Controls:** Random chooses two distinct port combinations with a frozen seed; Fixed diagnostic always tries \`(0,1)\` and \`(1,0)\`; Passive obtains two new but still naturally correlated observations. All methods are scored on the same independently generated four-setting synthetic truth table after observing their allotted evidence.

**Interpretation:** Experiment selection greatly outperforms passive correlation and randomly chosen settings in this noiseless, simple two-control simulator. **It does not outperform an obvious classical diagnostic policy**, which obtains the same perfect result. The 60 worlds are related procedural examples with different names/seeds, not 60 independent physical or social domains. The hypothesis grammar already contains the true model in every case. No calibrated posterior probabilities or unknown hidden variables are tested.

### The portable decision-tree boundary

MOTIF-010 reuses MOTIF-009's \`CartridgeBay\`: a new tree defaults to **HOLD**. Local review requires a separate compatible observation set (at least eight synthetic examples), and explicit \`ADMIT_PREDICT_ONLY\` grants only read-only predictions. Revocation blocks them. The prototype cannot verify any real reviewer identity.

We repaired a closed-world Boolean bug in MOTIF-009: a *false* input port is naturally represented by an **absent** predicate, and should not be mistaken for an unreviewed vocabulary. Unknown actual predicates remain held. We also explicitly allow \`SYNTHETIC_NATURAL\` and \`SYNTHETIC_INTERVENTION\` provenance in the earlier synthetic observation reader without accepting any claimed real evidence.

**Critical distinctions:** intervention proposal is not permission; programmed synthetic causation is not physical causal inference; a content checksum is not origin authentication; admission for prediction is not authority to act; information gain in a four-leaf truth table is not general experimental science.

## Reproduction

Python 3.10+, standard library, no paid API:

\`\`\`sh
cd experiments/010
python benchmark.py
python -m unittest -v test_scientist.py
python demo.py     # concrete two-step inquiry and exported tree cartridge
\`\`\`

GitHub Actions runs all previous MOTIF experiments and logs the full independently generated benchmark. The 010 test suite checks that the archived JSON matches the regenerated JSON **exactly**.

## The next serious falsifiers

1. **Missing hypotheses:** hide a third control or a latent common cause. A scientifically honest learner should abstain when no available tree can explain observations.
2. **Noise and partial visibility:** include imperfect measurements and unreliable effects, then require calibrated uncertainty.
3. **Cost and safety:** assign different intervention costs, disallowed experiments and simulated harms. Optimize safe information per cost rather than free information alone.
4. **Different causal domains:** freeze truly unfamiliar graph rules, time delays, cardinalities and intervention semantics before the experiment.
5. **Matched rival methods:** compare with stronger classical active learning, Bayesian intervention planning, information-theoretic baselines, and learned relational/neural models.
6. **Independent transfer:** evaluate whether tree cartridges reduce the observation budget in another world while leaving its evidence and governance local.

**What MOTIF-010 really demonstrates:** with explicit controls and a complete small hypothesis grammar, learned decision-tree cartridges can represent competing explanations, choose a useful synthetic intervention, and update after the simulator supplies a separate observation. It makes no claim to authority or understanding beyond that laboratory.
