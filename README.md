# MOTIF — Model Of Transformations In Fields

**Experimental, graph-native research for JAR;VIS.** The native unit is a change to a typed relational field—not a text token. MOTIF explores what happens when a system learns reusable transformation schemas and composes them into hypothetical futures.

This is a research sandbox, **not** a pretrained LLM, a real-world causal model, an autonomous agent, or evidence of permission. All demonstrations are deliberately invented. No external calls or actions occur.

## Working experiments

- **[001 — Named transformation induction](experiments/001/VISION.md):** Learn role-relative graph rewrites from labeled synthetic `before/action/after` episodes. Discover a synthetic repair → teach → repair chain.
- **[002 — Birth of an unnamed verb](experiments/002/DESIGN.md):** Infer anonymous graph-rewrite operators from unlabeled `before/after` graphs and compose them in unfamiliar synthetic worlds.
- **[003 — The affordance frontier](experiments/003/affordance.py):** Compare the immediate utility of hypothetical transitions with the new actions they enable; see [the outermost circle](docs/THE-OUTERMOST-CIRCLE.md).
- **[004 — The first scar](experiments/004/DESIGN.md):** Record an attempted edit that did not occur, compare predicted and observed graphs, learn one provisional missing-context discriminator from contrasts, and explicitly abstain when evidence conflicts.
- **[005 — The birth of a concept](experiments/005/DESIGN.md):** Propose an anonymous two-edge derived relation from successful and failed synthetic attempts; distinguish a shared intervening part from disconnected parts, and filter hypothetical actions without altering observed history.
- **[006 — The composite verb](experiments/006/DESIGN.md):** Induce anonymous reusable operator programs from repeated synthetic traces, nest macros within macros, pin every dependency's source semantics, and recheck every primitive guard during hypothetical replay.
- **[007 — Inheritance without empire](experiments/007/DESIGN.md):** Export only source-pinned abstract operator closures, hold them for independent local preview and explicit planning-only review, then inherit and improve a composite method across two separate synthetic worlds without sharing either observed graph.
- **[008 — The unknown world](experiments/008/DESIGN.md):** Infer relational rules from unfamiliar opaque-predicate synthetic worlds, compare with matched classical baselines, preserve validation-based abstention, and measure held-out structural interventions. **The strong depth-2 tree baseline essentially matches MOTIF's covered performance.**
- **[009 — The Experimenter](experiments/009/DESIGN.md):** Turn two-question decision trees into portable, source-checksummed, local-reviewable **prediction cartridges**. An [actual XOR tree cartridge](experiments/009/example-tree-cartridge.json) is checked in. A committee proposes which synthetic observation to reveal next; compare fixed-budget inquiry with seeded random sampling. v1 showed no benefit at the accuracy ceiling; a separate, post-hoc low-data stress test shows a temporary early advantage.
- **[010 — The Scientist](experiments/010/DESIGN.md):** Convert competing MOTIF-009 tree cartridges into an information-gain experiment selector. A separate simulator executes two controlled graph interventions **on demand**; see the [actual two-step scientist transcript and final tree cartridge](experiments/010/example-scientist-interventions.json). In 60 tiny synthetic worlds the selector identifies the correct two-port truth table in 60/60 worlds, compared with 12/60 random, **and ties a strong fixed classical diagnostic control**.
- **[011 — The Skeptical Scientist](experiments/011/DESIGN.md):** Preserve contradictions that disprove the current two-input grammar; refuse to guess about hidden causes or noise; propose a new **role-relative relation routing to two real MOTIF-009 tree cartridges** only with independent validation and local prediction-only review. [The actual composite router and six-case transcript](experiments/011/example-skeptic.json) are committed. In 30 controlled worlds, MOTIF predicts only half the holdouts but makes no wrong covered predictions; a forced baseline predicts all and gets 160/480 wrong.
- **[012 — The Causal Cartographer](experiments/012/DESIGN.md):** Start with MOTIF-011's perfectly confounded candidate concepts, package four competing **real MOTIF-009 decision-tree cartridges**, choose synthetic interventions to break their correlation, and record independent local falsification and explicit prediction-only review. The [concrete causal-map and refusal cartridge](experiments/012/example-causal-map.json) is stored. Across 36 synthetic worlds, 24/36 model candidates pass separate local review and an explicit synthetic admission fixture, 12/36 are held for hidden-context/noisy counterexamples; this **ties an ordinary fixed diagnostic strategy**, not evidence of new causal mathematics.
- **[013 — The Probabilistic Witness](experiments/013/DESIGN.md):** Replace exact outcomes with **sampled Bernoulli success/failure, unreliable and anti-reliable witnesses, forwarded hearsay, missing reports, and real synthetic actuator noncompliance**. Learn Beta-calibrated source/actuator uncertainty, weight four real 009 decision-tree cartridges plus unresolved OTHER mass, and issue probabilities or abstentions. In 3,600 held-out synthetic outcomes, **a flexible classical Bayesian four-cell baseline beats MOTIF on Brier score (0.224069 vs 0.228364)**. See the [verified probabilistic witness cartridge and admitted/missed failures](experiments/013/example-probabilistic-witness.json).
- **[014W — The Witness of Witnesses](experiments/014w/DESIGN.md):** Treat the **auditor itself as another unreliable witness**, instead of assuming its adjudications are gold truth. Jointly enumerate source truthfulness, fallible audit reports, intervention compliance and causal-tree hypotheses in an exact **960-state finite Bayesian grid**, while integrating missing action receipts rather than treating requested actions as completed. The [actual probabilistic 009-tree ensemble, meta-witness credibility intervals and both caught/missed source drifts](experiments/014w/example-joint-credibility.json) are committed. Across **2,688 stochastic holdouts**, a broader **classical 16-Boolean-model joint Bayes wins** (Brier 0.197640 versus MOTIF 0.202442). This parallel research organ is isolated from the concurrent **014 Organ Gardener** branch.

- **[IMMUNE-001 — Epistemic Virology](experiments/immune001/DESIGN.md):** An isolated synthetic graph-integrity experiment with ancestry tracing, declared-origin de-duplication, local finite mathematical checks, targeted dependency review and anti-autoimmunity controls. In 480 engineer-authored held-out scenarios (same families, different seeds), it matched all expected statuses, had zero unsupported promotions and retained 80 checked true novelties. **The strong classical finite-check baseline tied 480/480 on binary promotion; no broad AI immunity claim.**

- **[IMMUNE-002 — Shoulders of Giants](experiments/immune002/DESIGN.md):** Reuse Doyle/de Kleer-inspired truth maintenance, alternative minimal support environments, exact polynomial checks, and a simulated source-to-sink reference monitor. On 480 synthetic reasoning fixtures, the algorithm matched an independent exhaustive environment baseline in **480/480**, preserving 40 alternative supports after revocation. On 320 simulated actions, an exact-parameter classical ACL **tied 320/320**, permitting all 120 benign cases and denying all 200 attack cases. No practical superiority over the strong controls is claimed. A separate opt-in Qwen3B action-proposal probe exists; it executes no real actions. **Stacked draft, not merged.**\n\n### Run (Python 3.10+, standard library only)

```sh
cd experiments/001
python motif.py
python -m unittest -v test_motif.py

cd ../002
python motif002.py
python -m unittest -v test_motif002.py

cd ../003
python affordance.py
python -m unittest -v test_affordance.py

cd ../004
python scar.py
python -m unittest -v test_scar.py

cd ../005
python concept.py
python -m unittest -v test_concept.py

cd ../006
python composition.py
python -m unittest -v test_composition.py

cd ../007
python inheritance.py
python -m unittest -v test_inheritance.py

cd ../008
python -m unittest -v test_unknown.py
python benchmark.py

cd ../009
python -m unittest -v test_experimenter.py
python benchmark.py   # v1 ceiling benchmark
python stress.py      # v2 low-data stress, post hoc
python cartridge_demo.py # print portable XOR tree, HOLD/review and next question

cd ../010
python benchmark.py
python -m unittest -v test_scientist.py
python demo.py  # reproduce the two-step scientist cartridge

cd ../011
python benchmark.py
python demo.py    # inspect proposed missing relation and safe refusals
python -m unittest -v test_skeptic.py

cd ../012
python benchmark.py
python demo.py    # show candidate causal maps, interventions, and refusals
python -m unittest -v test_cartographer.py

cd ../013
python benchmark.py  # 30 worlds, noisy reporters and classical Bayesian control
python demo.py       # uncertainty, anti-witness, and missed shift examples
python -m unittest -v test_witness.py

cd ../014w
python benchmark.py  # exact finite-grid joint Bayes, stronger full-Boolean competitor
python demo.py       # meta-auditor, model uncertainty, and missed reliability shifts
python -m unittest -v test_joint.py
```

The suites also run on GitHub Actions with no paid services or API credentials.

## Research laws

- **An adjudicator's report ≠ ground truth.** MOTIF-014W models fallible calibration judges and actuator attestations as latent-variable Bayesian evidence, not privileged observations.
- **A posterior interval ≠ proof of independent identification.** Inferring who is right from agreement relies on orientation priors and observed-source assumptions; those can be wrong.
- **A report ≠ an observed outcome.** Sources can misreport, disagree, be absent or be malicious; witness identity metadata and checksum are not verified real-world truth.
- **A forwarded witness ≠ another independent witness.** Repeated claims sharing one upstream origin are counted once, not multiplied into false certainty.
- **An intended intervention ≠ an applied intervention.** Without a separate synthetic receipt of applied controls, MOTIF-013 holds causal attribution from that training attempt.
- **A high posterior ≠ calibration or immunity to distribution shift.** The 013 ensemble loses to a flexible Bayesian baseline overall and misses some out-of-family and drift worlds.
- **A broken hypothesis family ≠ a discovered cause.** Repeated same-input contradictions require abstention until an independently validated explanation exists.
- **A new feature ≠ a causal relation.** A predictive relation can be a proxy; competing indistinguishable proxies are explicitly held.
- **A simulated causal intervention ≠ identification in the physical world.** A predictive causal map must survive independent controls and validation; even then, it is only supported in its programmed sandbox.
- **Passed review ≠ admitted authority.** A separately recorded local fixture decision is required before a hypothesis can be used for read-only synthetic predictions.
- **Information gain ≠ permission.** A prohibited or unaffordable synthetic experiment stays held even when informative.
- **Hypothesis ≠ observation.** Simulated futures cannot amend observed history.
- **Structure ≠ causality.** Correlated transitions do not establish why events occur.
- **Graph permission fact ≠ real-world consent.** The hard gate is a synthetic demonstration only.
- **Learned rule ≠ capability to act.** None of these experiments can affect external systems.
- **Portable method ≠ shared sovereignty.** Source checksums do not authenticate authors, and admitted simulations never authorize real actions.
- **Compressed macro ≠ new external ability.** Reusing a sequence as one planning primitive does not bypass or reduce its underlying steps.
- **Decision tree cartridge ≠ autonomous action.** Cartridges offer auditable inferences, and their local admission only permits read-only predictions in this prototype.
- **Synthetic interventions ≠ real-world intervention authority.** MOTIF-009 chooses pre-generated unlabeled observations; MOTIF-010 chooses changes executed only inside a separate synthetic graph simulator.
- **Opaque predicates ≠ open-world understanding.** MOTIF-008 learns within each controlled synthetic world; zero-shot cross-world transfer remains unproven.
- **Matching a classical baseline ≠ architectural superiority.** A simple tree with the same graph features approaches the full synthetic benchmark ceiling.
- **New verb ≠ novel model architecture.** Program induction, graph rewriting, and planning have substantial prior art; originality remains to be proven through controlled benchmarks.

## Next frontier

Break the **identifiability assumptions** of the finite-grid witness-of-witnesses model: introduce correlated reports, false origin metadata, doubly fallible adjudicators, and time-changing evidence quality. Measure online calibration, safe abstention and conditional source dependence under independently frozen uncertainty regimes. Freeze out-of-family/noisy-regime holdouts, measure online calibration and abstention, and compare against strong classical Bayesian baselines on matched evidence and compute. Compare active causal maps to strong Bayesian and classical experimental-design algorithms in independently frozen held-out graph domains, and measure *harm from negative cross-world cartridge transfer*. Compare with stronger statistical, program-induction, graph network and classical planning baselines under identical evidence and compute budgets. The goal is falsifiable prediction of changes in *reachable future capabilities*, not flattering descriptions of emergence.

This repository is a standalone science lab. A future JAR;VIS integration must use explicit, reviewed contracts rather than treating generated scenarios as reality.