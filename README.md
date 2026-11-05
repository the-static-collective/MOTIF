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

### Run (Python 3.10+, standard library only)

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
```

The suites also run on GitHub Actions with no paid services or API credentials.

## Research laws

- **Hypothesis ≠ observation.** Simulated futures cannot amend observed history.
- **Structure ≠ causality.** Correlated transitions do not establish why events occur.
- **Graph permission fact ≠ real-world consent.** The hard gate is a synthetic demonstration only.
- **Learned rule ≠ capability to act.** None of these experiments can affect external systems.
- **Portable method ≠ shared sovereignty.** Source checksums do not authenticate authors, and admitted simulations never authorize real actions.
- **Compressed macro ≠ new external ability.** Reusing a sequence as one planning primitive does not bypass or reduce its underlying steps.
- **Opaque predicates ≠ open-world understanding.** MOTIF-008 learns within each controlled synthetic world; zero-shot cross-world transfer remains unproven.
- **Matching a classical baseline ≠ architectural superiority.** A simple tree with the same graph features approaches the full synthetic benchmark ceiling.
- **New verb ≠ novel model architecture.** Program induction, graph rewriting, and planning have substantial prior art; originality remains to be proven through controlled benchmarks.

## Next frontier

Measure whether structural knowledge learned in **one world** reduces sample cost in a genuinely different, held-out world family; include incomplete observations, concept drift, more than two roles, nonlocal dependencies and active inquiry. Compare with stronger statistical, program-induction, graph network and classical planning baselines under identical evidence and compute budgets. The goal is falsifiable prediction of changes in *reachable future capabilities*, not flattering descriptions of emergence.

This repository is a standalone science lab. A future JAR;VIS integration must use explicit, reviewed contracts rather than treating generated scenarios as reality.