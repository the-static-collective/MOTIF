# MOTIF-012 — THE CAUSAL CARTOGRAPHER

## Predictive companions are not necessarily causal parents

**Question:** Can MOTIF separate two equally predictive, perfectly correlated graph relations by choosing interventions that change them independently—and refuse causal attribution when an unobserved factor or contradictory measurements defeat the current hypotheses?

**Status:** Executable, standard-library Python, **synthetic** graph research only. No real-world causal discovery, physical interventions, sensor access, validated human consent, authenticated evidence or novel statistical method.

### The challenge inherited from MOTIF-011

MOTIF-011 correctly refused to decide between two new, perfectly confounded predictive relations. Both could explain its graph observations, but neither had been shown to be consequential.

The new experiment begins with precisely that uncertainty: in every natural observation, **two opaque candidate predicates C and P are equal**. Their relationship to an outcome is indistinguishable. There are four synthetically programmed causal explanations whose predictions agree when C=P:

- C alone matters.
- P alone matters.
- C AND P matters.
- C OR P matters.

A fifth world makes the observed effect depend on an **unseen context** that naturally follows C=P, but does not follow either candidate after independent intervention. A sixth world introduces 25%-frequency *deterministic hash-based outcome flips* **only during intervention/evaluation**, so it is a deliberate synthetic distribution shift, **not a calibrated stochastic sensor model**.

The research method is not supplied the family name. The evaluator knows the family, but [cartographer.py](cartographer.py) never imports [oracle.py](oracle.py), hidden rules, held-out labels or the independently reviewed outcomes.

There is an important *declared prior*: the original two visible input ports already have a known XOR baseline. The learner attributes only the **residual** unexplained by that baseline to candidate C/P relationships. The learner is not discovering that baseline autonomously, and the four possible residual programs are **hand-designed**.

### The executable causal inquiry

\`\`\`text
                NATURAL GRAPH OBSERVATIONS
                    C = P, always
                           |
                  011: ABSTAIN_AMBIGUOUS
                           |
               discover TWO unnamed relations
                           |
              build FOUR real 009 tree cartridges
                   FIRST / SECOND / AND / OR
                           |
                  choose an intervention
              to split their predictions evenly
                           |
                  do(C=false,P=true)
                           |
               INDEPENDENT SIMULATOR ANSWER
                           |
                  ELIMINATE CONTRADICTIONS
                           |
                   do(C=true,P=false)
                           |
                 ONE PROVISIONAL MODEL?
                       /       \
                      no        yes
                      |          |
                     HOLD    SEPARATE REVIEW
                               |
                   16 NEW FACTORIAL PROBES
                               |
                    mismatch? / \ agrees?
                             /   \
                            HOLD  ELIGIBLE
                                  |
                         EXPLICIT LOCAL DECISION
                           /                \
                         REFUSE       ADMIT_PREDICT_ONLY
                                            |
                               16 separate held-out tests
\`\`\`

The four candidates are **actual reusable MOTIF-009 \`Cartridge\` objects**, with role-relative graph motifs, Boolean leaves, an explicit evidence count, an unverified source digest, and content hashes. Their off-diagonal answers are labeled *hypotheses*, not observations. Each can be exported and validated with the existing 009 package format.

The query selector calculates exact, classical version-space information gain over the surviving candidate trees, divides by declared positive cost, and **filters prohibited or unaffordable proposals before optimization**. The first two informative questions can each split the remaining hypothesis space in half, giving **1 bit** expected information gain per question in the noiseless four-candidate world.

The evaluator constructs a genuinely **new synthetic intervention event after the proposal**, rather than retrieving an existing unlabeled example. Original natural observations are never modified.

### Independent falsification before admission

Two off-diagonal observations are enough to select one model **in the handcrafted noiseless grammar**. They are not enough to justify trusting it. A hidden contextual factor can fool the first two probes.

A separate 16-observation \`local_review\` split independently varies C, P and an unobserved context. It exists only on the evaluator side. The reviewer receives the provisional candidate and records every graph disagreement as an **independent falsification scar**.

A model may be:
- \`ELIGIBLE_PREDICT_ONLY_PENDING_LOCAL_DECISION\` if all 16 separate synthetic checks agree.
- \`HOLD_INDEPENDENT_FALSIFIER\` when some independent interventions disagree.
- \`HOLD_AMBIGUOUS_OR_FALSIFIED\` if no uniquely surviving model exists.
- \`HOLD_INSUFFICIENT_LOCAL_REVIEW\` if the reviewer lacks adequate independent synthetic coverage.

**Eligibility is NOT admission.** \`LocalCausalBay\` holds every offered cartridge until a distinct explicit **synthetic reviewer fixture** records \`ADMIT_PREDICT_ONLY\` or \`REFUSE\`. That fixture name is not a verified human identity. Even after admission, the only authorized operation is **read-only inference in a compatible synthetic world**. An explicit revocation blocks subsequent predictions.

An additional 16-observation \`test\` split is held out until the evaluator scores the result. Its labels never influence the scientist's question selection or the local admission decision. Do not reinterpret test results as evidence the model had available in advance.

### Measured results

The benchmark contains **six mechanism families × six seeds = 36 synthetic worlds**, evaluated against each of three two-query methods. Every method starts with the same 16 natural training and 16 natural validation snapshots, gets **exactly two** new inquiry opportunities, and is subject to the **same** independent 16-case local review and 16-case final held-out test.

| Measure | Cartographer | Fixed classical diagnostic | Random control |
|---|---:|---:|---:|
| Worlds evaluated | 36 | 36 | 36 |
| Provisionally unique explanations after two questions | **36** | **36** | **6** |
| Independently reviewed and explicitly fixture-admitted | **24/36** | **24/36** | **4/36** |
| Mean held-out prediction coverage after review | **66.67%** | **66.67%** | **11.11%** |
| Wrong predictions **among covered** held-out examples | 0 | 0 | 0 |

Across Cartographer's six-seed families, the four deterministic visible-cause programs each passed independent review in **6/6** worlds. The latent-context and noisy-intervention worlds were **held in all 12/12** instances. Independent review found **76 contradictions** across all 36 Cartographer worlds; they were retained in the checked-in seed-level audit.

**The fixed diagnostic baseline tied the Cartographer perfectly.** It simply selects the two off-diagonal interventions. Information-gain selection is useful here because the premise is synthetic and known, not because we discovered a superior intervention-planning algorithm.

Likewise, zero wrong covered predictions comes with **33.33% abstention** for the Cartographer and 88.89% abstention for random control. A deliberately naive, always-predicting observational-only baseline is also reported, but is not a credible strong Bayesian comparator.

All 36 mechanisms are six programmatic families with opaque names/seeds, **not** independent causal domains. The one-bit scores derive from a uniform, deterministic **finite** version space, not a calibrated posterior. The noisy family is a deterministic hash fixture and is not evidence that MOTIF understands stochastic noise. Importantly, the natural observations are explicitly clean, even in the family whose later intervention measurements are flipped.

The [complete seed-level CI result](experiment-results.json) exposes all interventions, candidate transitions, local-review contradictions, refusals and held-out outcomes without selectively dropping negative cases.

### Real, inspectable cartridges

[example-causal-map.json](example-causal-map.json) is an actual CI-produced record of four 009 tree cartridges, the two interventions proposed in a synthetic candidate-driver world, a resulting provisional tree, the local review, and explicit prediction-only fixture decision. It also includes one latent-cause case and one noisy-intervention case **refused** after independent review.

The artifact contains no real identity, user-world record or authorized actuation. Content checksums **do not authenticate origins** and do not guarantee confidentiality for future, richer vocabularies.

### Research integrity and governance

\`\`\`text
NATURAL CORRELATION != CAUSAL PARENT
INTERVENTION IN SIMULATION != REAL-WORLD AUTHORITY
TWO GOOD EXPERIMENTS != RELIABLE CAUSAL IDENTIFICATION
CANDIDATE TREE != OBSERVED WORLD
INDEPENDENT REVIEW != AUTOMATIC ADMISSION
HASHED CONTENT != VERIFIED AUTHOR
NO WRONG COVERED PREDICTIONS != CORRECT ON ABSTENT CASES
FOUR HANDCRAFTED PROGRAMS != UNCONSTRAINED WORLD MODEL
\`\`\`

A separate synthetic policy proof rejects informative but prohibited experiments with \`HOLD_UNSAFE\`, rejects unaffordable ones with \`HOLD_BUDGET\`, and emits only a **proposal** when the control settings and cost are admitted. It does not call the simulator, let alone a real actuator.

### Reproduce

Python 3.10+, standard library only:

\`\`\`sh
cd experiments/012
python benchmark.py
python demo.py
python -m unittest -v test_cartographer.py
\`\`\`

The GitHub Actions workflow reproduces all eleven prior experiments, prints complete versioned 012 experiment receipts, and checks that archived results and example cartridges match fresh deterministic runs.

### Next falsifiers

1. Replace artificially clean natural observations and deterministic intervention label flips with **real probabilistic sensing models**, outcome likelihoods and calibrated uncertainty. An appropriate probabilistic model should sometimes maintain several hypotheses rather than treat any disagreement as impossible.
2. Randomize third-party **confounders** while deliberately hiding their existence. Determine how often an innocent predictor is falsely assigned causal status, including on withheld domain families.
3. Add interventions that are **not guaranteed to work as intended**, with witness receipts recording intervention compliance and failed manipulation.
4. Include **three or more controlled causes**, temporal delays, structural relational interactions, dependent witnesses and interventions with unequal costs/risks.
5. Compare with strong classical causal-design baselines, Bayesian posterior inference, randomized controlled trials in simulation and small trainable relational models, all using identical observation and computation budgets.
6. Measure **negative transfer** of a local prediction cartridge into a new ontology and insist on independent local review, explicit governance and refusal before any proposed real-world integration.

**What is actually established:** Under a small programmed causal simulator, changes to correlated candidate predicates can distinguish observationally equivalent explanations. A source-independent learner can formulate those interventions, package candidate programs as inspectable trees, preserve independent contradictions and decline to make unsupported predictions. No general causal intelligence is established.
