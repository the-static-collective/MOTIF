# MOTIF — Model Of Transformations In Fields

**Experimental, graph-native research for JAR;VIS.** The native unit is a change to a typed relational field—not a text token. MOTIF explores what happens when a system learns reusable transformation schemas and composes them into hypothetical futures.

This is a research sandbox, **not** a pretrained LLM, a real-world causal model, an autonomous agent, or evidence of permission. All demonstrations are deliberately invented. No external calls or actions occur.

## Working experiments

- **[001 — Named transformation induction](experiments/001/VISION.md):** Learn role-relative graph rewrites from labeled synthetic `before/action/after` episodes. Discover a synthetic repair → teach → repair chain.
- **[002 — Birth of an unnamed verb](experiments/002/DESIGN.md):** Infer anonymous graph-rewrite operators from unlabeled `before/after` graphs and compose them in unfamiliar synthetic worlds.
- **[003 — The affordance frontier](experiments/003/affordance.py):** Compare the immediate utility of hypothetical transitions with the new actions they enable; see [the outermost circle](docs/THE-OUTERMOST-CIRCLE.md).
- **[004 — The first scar](experiments/004/DESIGN.md):** Record an attempted edit that did not occur, compare predicted and observed graphs, learn one provisional missing-context discriminator from contrasts, and explicitly abstain when evidence conflicts.
- **[005 — The birth of a concept](experiments/005/DESIGN.md):** Propose an anonymous two-edge derived relation from successful and failed synthetic attempts; distinguish a shared intervening part from disconnected parts, and filter hypothetical actions without altering observed history.

- **[006 — The first question × Dogram](experiments/006/DESIGN.md):** Under synthetic uncertainty, select one permitted, affordable discriminator of target predictions; export finite probe vectors for optional calculation-only Dogram analysis. No general intelligence claim.

- **[007 — The smallest key × Dogram](experiments/007/DESIGN.md):** Find a minimum-cost sequence of synthetic interventions to open a target opportunity without deleting other actors' options; compare knowledge vs capability and Dogram's mixed difference / lost distinctions.

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
python question.py
python -m unittest -v test_question.py
python -m unittest -v test_baselines.py

cd ../007
python smallest_key.py
python -m unittest -v test_smallest_key.py
```

The suites also run on GitHub Actions with no paid services or API credentials.

## Research laws

- **Hypothesis ≠ observation.** Simulated futures cannot amend observed history.
- **Structure ≠ causality.** Correlated transitions do not establish why events occur.
- **Graph permission fact ≠ real-world consent.** The hard gate is a synthetic demonstration only.
- **Learned rule ≠ capability to act.** Neither experiment can affect external systems.
- **New verb ≠ novel model architecture.** Program induction, graph rewriting, and planning have substantial prior art; originality remains to be proven through controlled benchmarks.

## Next frontier

Test whether the proposed composite concepts survive true structural holdouts, graph rewirings, and interventions that break confounders. Compare with simple relational and neural baselines under identical budgets. Then train on varied, noisy, partially observed transitions with unlabeled agent roles, ambiguous preconditions, multiple confounders and held-out relation types; compare against a deterministic rule learner and a graph-network baseline under identical budgets. The goal is falsifiable prediction of changes in *reachable future capabilities*, not flattering descriptions of emergence.

This repository is a standalone science lab. A future JAR;VIS integration must use explicit, reviewed contracts rather than treating generated scenarios as reality.