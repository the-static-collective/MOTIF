# MOTIF-011 — THE SKEPTICAL SCIENTIST
## When no available explanation deserves to be believed

**Research question:** Can a graph-native symbolic learner detect that its decision-tree grammar is inadequate, preserve contradictory before/after observations, propose *testable* new relational structure when it is actually visible, and **abstain** when an explanation is hidden, noisy, observationally ambiguous, unsafe to investigate or too costly?

**Result:** Executable Python-standard-library research using entirely **synthetic** relational graphs. This is **not** a trained neural intelligence, physical causal discovery, general epistemic calibration, verified third-party provenance, consent, human safety evaluation or autonomous real-world agency.

## What MOTIF-010 could not do

MOTIF-010 succeeded because the simulator's hidden rule always belonged to its pre-specified **16 two-input decision trees**. The moment a third unmodeled condition changes an outcome, a deterministic two-input model may be unable to fit repeated observations.

In 011, the model must decide whether it has the right to predict **before choosing which hypothesis to use**.

A change of confidence is not sufficient: if two observations share the **same known inputs** and report *opposite outcomes*, the entire deterministic two-input grammar fails for that evidence, not merely one candidate tree.

\`\`\`text
        INDEPENDENT SYNTHETIC OBSERVATIONS
                   |
          group by known controls
                   |
       same controls, different result?
             /                   \
           no                     yes
           |                       |
   check all four settings    PRESERVE CONTRADICTION
   & independent validation         |
           |                   inspect other visible
      local two-input rule     role-relative predicates
                                   |
                      +------------+------------+
                      |            |            |
                   unique        several        none
                      |            |            |
                  PROPOSE        ABSTAIN       ABSTAIN
                a concept       ambiguous   inadequate
                      |
              build a third-relation
              two-cartridge router
                      |
                   HOLD
                      |
           independent local review
                      |
          ADMIT_PREDICT_ONLY / REFUSE
                      |
               separate heldout test
\`\`\`

## The six synthetic worlds

[oracle.py](oracle.py) creates six procedural families with five seeds each. Every world has its own opaque predicate vocabulary and independently constructed graph examples. The *learning module* [skeptic.py](skeptic.py) never imports the oracle, its family labels or hidden outcome rules.

Each synthetic world has **four separate 16-example partitions**:

1. Training — evaluate the original model and search for candidate missing predicates.
2. Validation — reject candidate missing predicates that fail independent synthetic predictions.
3. Local review — a *separate* 16-example evidence batch for explicit prediction-only admission.
4. Held-out test — not consulted by the learner or reviewer; used solely for final scoring.

| Family | What the evaluator secretly implements | Appropriate model response |
|---|---|---|
| \`clean_two\` | The outcome depends on the two known inputs | Keep the ordinary two-input model. |
| \`visible_third\` | A third **visible, unmodeled** unary relation changes the result | Propose a **third-predicate router** if uniquely supported by training and validation, then HOLD pending local review. |
| \`hidden_third\` | A third factor changes outcomes but does **not appear** in the before graph | **ABSTAIN**; don't invent it. |
| \`noisy_flip\` | Deliberately alternating synthetic observation-label flips | **ABSTAIN**; cannot distinguish its evidence from a hidden cause. |
| \`ambiguous_proxy\` | Two visible third relations are perfectly confounded | **ABSTAIN**; both observational explanations fit, and neither is known causal. |
| \`restricted_clean\` | The ordinary two-input mechanism, but potentially informative interventions are **locally prohibited** | Retain known predictions while refusing prohibited new experiments. |

The \`hidden_third\` and \`noisy_flip\` evidence streams were deliberately constructed to be observationally indistinguishable with respect to the known variables. The correct outcome is **not** to label one "noise" and the other "latent cause"; neither inference is justified.

The "noise" here is an artificial patterned label flip. It is not a proper stochastic sensor-noise model, and the experiment never claims to distinguish real noise from confounding.

## What a new concept actually is

In the \`visible_third\` world, training contains repeated pairs of observations with the **same two known inputs** but incompatible outcomes. MOTIF enumerates unknown unary relations attached to the actor or target; it does **not** receive the name or meaning of the useful third relation.

For each candidate, it builds an eight-cell truth table over:

\`known_input_A × known_input_B × candidate_relation_present\`

The candidate must cover **all eight configurations** with no contradictory labels and predict all separately supplied validation examples exactly. More than one candidate passing creates **ABSTAIN_AMBIGUOUS**. No candidate creates **ABSTAIN_INADEQUATE**.

A uniquely predictive relation becomes an anonymous *proposed composite router*:

\`\`\`text
                           HAS RELATION C?
                              /       \
                            NO         YES
                            |           |
                     009 TREE 1     009 TREE 2
                      tests A,B      tests A,B
                            \          /
                              PREDICT
\`\`\`

These are **real, serializable MOTIF-009 decision-tree Cartridge objects**. The routing node is a new, role-relative relational predicate discovered from the graph, not a named human-defined outcome mechanism. [example-derived-router.json](example-derived-router.json) is a complete actual composite packet generated in CI. It includes both nested 009 trees and a strict schema/content fingerprint.

**The new predicate is supported as a *predictive distinction*. The experiment does not establish that the visible condition causes the outcome.** A perfect proxy is not a cause; the perfectly confounded-proxy world is deliberately refused.

### Predict-only local crossing

A proposed router is initially **HOLD**. It may be exported/imported as a JSON artifact; its content checksum detects changes but **cannot establish the author's identity**. The receiver checks the nested tree definitions and vocabulary. A separate batch of eight-or-more synthetic **local** observations must cover all eight input combinations and validate the candidate before an explicit local reviewer decision admits **read-only prediction**.

No prediction admission authorizes external action, real sensor access, changes to the original graph, or a new permission. A local refusal or revocation blocks use.

## Measured controlled results

The [complete seed-level CI receipt](experiment-results.json) contains 30 synthetic worlds × 16 held-out examples = **480 held-out synthetic examples**. All worlds also have their own 16-example training, validation and local-review partitions.

| Outcome | Result |
|---|---:|
| Ordinary two-input model retained | **10/30 worlds** |
| Unprovided third relational predicate proposed and independently reviewed | **5/30 worlds** |
| Abstention for unexplainable/hidden/noisy evidence | **10/30 worlds** |
| Abstention for equally explanatory proxies | **5/30 worlds** |
| Skeptical learner prediction coverage | **50% of 480 held-out cases** |
| Incorrect predictions **where it chose to predict** | **0** |
| Forced two-input majority baseline prediction coverage | 100% |
| Forced majority baseline incorrect predictions | **160 / 480 (33.33%)** |
| Synthetic unsafe informative proposals | **HELD** |
| Synthetic over-budget proposals | **HELD** |
| Physical/external operations | **0** |

This is a **coverage/accuracy tradeoff**, not a demonstration of universal superiority. MOTIF abstains on half of the benchmark. The baseline intentionally always predicts and is *naive*; no strong Bayesian, noise-aware or causal competitor has yet been tested. The data and candidate vocabulary are designed to make a unique third predicate explain one family, so the measured success is narrow and programmatically constructed.

The 30 "worlds" differ largely in opaque names and seeds inside the same six programmed mechanisms. They are **not** 30 independent real-world domains.

### A safety/cost counterexample

The skeptical experimenter also receives a separate declared synthetic *local intervention policy* with an allowed control-setting set, positive integer costs and a remaining budget.

It computes expected information gain over the competing MOTIF-010 tree cartridges, but **filters prohibited or unaffordable experiments *before* optimization**. An unsafe experiment is not rescued by being informative. Its outputs distinguish:

- \`HOLD_UNSAFE\`: all informative experiments are prohibited.
- \`HOLD_BUDGET\`: an admissible informative experiment costs more than the remaining budget.
- \`HOLD_NO_INFORMATION\`: no remaining experiment distinguishes the candidate models.
- \`PROPOSE_SYNTHETIC_ONLY\`: an allowed, affordable *proposal*, which still cannot execute anything.

The [concrete six-case demo](example-skeptic.json) includes these refusals and an accepted synthetic proposal. No real cost accounting, ethical approval, or live actuator exists in this experiment.

## Reproduce

Python 3.10+, standard library only, no paid API:

\`\`\`sh
cd experiments/011
python benchmark.py
python demo.py
python -m unittest -v test_skeptic.py
\`\`\`

The GitHub Actions workflow runs all previous MOTIF experiments, reproduces the full 30-world JSON result, and verifies the checked-in demo artifacts against new synthetic runs. See [test_skeptic.py](test_skeptic.py) for targeted falsifiers: unseen vocabulary, malformed packets, label contradictions, sparse evidence, ambiguous proxies, independent local review and intervention refusal.

## The next genuinely difficult boundary

MOTIF-011 demonstrates that **a theory can fail while the system preserves the right to remain uncertain**. But it still assumes deterministic, exact observations in its successful concept family, a single discoverable unary relation, Boolean input controls and a complete observed eight-cell table.

To progress beyond this controlled proof:

1. **Allow partial and noisy observations** with proper probabilistic models; distinguish measurement uncertainty from model inadequacy without pretending to know which is which.
2. **Test new concepts on randomized interventions** that break correlations. If a candidate is only a proxy, it should fail a targeted causal falsifier.
3. **Model unobserved causes explicitly as unresolved possibilities**, not invented confirmed predicates.
4. **Expand the graph grammar without losing interpretability:** arity, temporal delays, quantities, shared-witness motifs, contradictions, incomplete source custody and true distribution shifts.
5. **Use real planning costs and procedural safety constraints** only in properly authorized, independently reviewed integrations; compare with Bayesian and classical optimal experimental design under matched budgets.
6. **Assess independent inheritance:** transfer a proposed concept between unrelated ontologies with explicit local review, while preventing source history, private state, or authority from moving with it.

**The tested principle:** Recognizing that a model cannot explain the observations is itself a measurable behavior. Repair requires independently supported evidence, and the option to refuse must remain real.
