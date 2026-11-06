# MOTIF-010 — THE SELF-CORRECTING WORLD MODEL

This source-native experiment builds directly on [MOTIF-009 #91](https://github.com/the-static-collective/MOTIF/pull/91). It updates beliefs about **four genuinely rendered PNG world hypotheses** when new **synthetic** evidence arrives, without replacing the original images, prior probabilities, or earlier contradictory reports.

**Question:** Do successive (simulated) observations improve forecast accuracy and decision quality compared with freezing MOTIF's initial assumptions?

## Sequence and source ownership

1. Original MOTIF-007 turns constrained ambiguous text into two valid distinct source-bounded PNG scene hypotheses: crate left vs right of a blue wall.
2. Original MOTIF-008's exposed assumption adds a second axis: partial-height vs full-height wall.
3. Original GRAFT-030 generated JavaScript is source-pinned and independently checked by CANNON-095; original MOTIF-006 reassembles and tests it, providing the reachability of each modeled PNG world. **This checks the executable code, not whether any picture represents reality.**
4. Original MOTIF-009 builds the four-world question policy with prior weights **1:1:4:4**, declaring its hypothetically useful questions. **No question has actually been sent or answered.**
5. **New MOTIF-010 `world_model.py`** verifies byte hashes for every original binary PNG and source-owned image gap, validates the original consent and uncertainty boundaries, and runs an **offline stream of typed simulated sensor reports**. Each report carries a sequence number, content digest, explicit assumed reliability, synthetic provenance and no-action authority. Exact rational Bayesian update revises world weights.
6. After *each* update, MOTIF re-evaluates its best terminal decision and **recomputes its next unsent question** using the original exact classical MOTIF-009 cost-sensitive decision tree.
7. Every event and previous/posterior is preserved in an append-only SHA-linked evidence record. Opposing observations do not overwrite one another; a contradictory synthetic report may reduce confidence in a previous update.
8. A fourth **held-out sensor report** is forecast before assimilating it. Its actual fixture value is disclosed to the **scorer**, never used to update the posterior that is being evaluated.

## Genuine numerical result — within authored synthetic fixtures

Four balanced, preselected **perfectly consistent** hypothetical worlds were evaluated separately. Each received a three-event training sequence (wall extent, side, wall extent; assumed 90%-accurate independent sensor) and one held-out side measurement.

| Metric | Frozen initial prior | After Bayesian revision |
| --- | ---: | ---: |
| Mean held-out **Brier score** (lower better) | 0.2500 | **0.0324** |
| Mean *simulated realized decision loss* | 2.5 | **0.0** |
| Original images preserved | Yes | Yes |
| Independently equivalent conventional Bayesian updater | **Matches** | **Matches** |

This shows that the online system **assimilated evidence and changed a decision coherently** on these designed examples, versus a *frozen prior* control. **It does not demonstrate generalization, calibrate its sensor, identify a real world, or outperform a matched-information classical Bayesian algorithm.**

The hypothetical priors, 90% sensor accuracy, conditional-independence assumption, outcomes and penalties were all authored for this experiment. Real observations can be wrong, correlated, misleading, missing, or outside the four-world grammar. The synthetic test was constructed with correct sensor readings; the measured gains are not a real-world empirical forecast of accuracy. Negative tests demonstrate that contradictory evidence is retained and mathematically weakens or reverses earlier belief, but this does not establish robustness to unmodeled sensor failures.

## Provenance and refusals

The source-native code rejects unknown evidence types, invalid likelihoods (including exact 1.0 certainty), duplicate and out-of-order event identities, false claims that a human answered, fake external source authority even if the attacker recomputes the packet hash, tampered source PNGs, changed initial priors, malformed event signatures/fields, and silent overwrites.

Records:
- `evidence/belief-revision/<WORLD_ID>/belief-01.json`, `belief-02.json`, `belief-03.json`: chained pre/post belief updates with the exact simulated event and next unsent question.
- `evidence/belief-revision/<WORLD_ID>/replay.json`: cumulative posterior, held-out forecast, simulated decision regret, complete custody and assumptions.
- `evidence/belief-revision/benchmark.json`: four-world Brier, log-loss and decision-loss frozen-vs-updated comparison.
- Prior MOTIF-009 four actual PNGs, original GRAFT code, CANNON review, original visual future frames, and source evidence are included in the CI artifact.

A deterministic independent *product of all likelihoods* checks every incremental Bayesian result. The original standard MOTIF-009 decision tree is recomputed at each revision. The review is read-only and does **not** contact anyone, change repositories, deploy, admit new code, learn from photographs, run T5, or collect real data.

### Run

The complete [hosted workflow](../../.github/workflows/door-foundry-010.yml) checks out the original independent source owners, regenerates original MOTIF-009 evidence in read-only CI, then runs:

```sh
python experiments/door-foundry-010/world_model.py \
  --question-dir evidence/original-active-question \
  --out evidence/belief-revision

python -m unittest discover \
  -s experiments/door-foundry-010 -p 'test_world_model.py' -v
```

`MOTIF009_QUESTION_DIR` must be set to the original regenerated evidence path for the test suite.

### Further frontier

Move beyond a handpicked finite true-world fixture by adding a user-authorized input interface and independent source attestations for *actual* observations, measured likelihood calibration, spatial observations beyond the model's support, adversarial/correlated evidence, and a forward-chaining falsification ledger with evidence partitions that are genuinely reserved for evaluation. Compare all improvements against same-data classical Bayesian and sequential-test baselines. A T5 language interpreter should remain a proposal producer, never evidence of its own proposals.

**Source text ≠ imagined PNG ≠ simulated sensor evidence ≠ physical observation. Revision ≠ deletion; improved fixture score ≠ general intelligence.**
