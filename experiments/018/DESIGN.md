# MOTIF-018 — THE UNKNOWN UNKNOWN
## A diagnostic that can propose a representation its original vocabulary could not express

**Status:** runnable, deterministic, standard-library-only **synthetic research**. No LLM, consciousness detector, live source retrieval, self-modifying code, external actuation, tool authorization, or autonomous deployment. The proposed method is **held for human review**.

### Falsifiable question

Can a system (1) detect a contradiction that cannot be resolved in its current observation language, (2) *propose* expanding that language from lower-level relational primitives, (3) reject an attractive spurious alternative on independent evidence, (4) distinguish useful prediction from real permission, and (5) preserve failure on transfer to an unfamiliar mechanism?

The experiment compares a **surface-only diagnostic** against a **finite graph-concept compiler**. The latter is conventional program synthesis and feature selection, not a discovery of new laws of intelligence.

### What actually runs

The initial observer recognizes only a binary variable **x**. Four synthetic training graph episodes share the same x values but sometimes have opposing labels. A surface-only truth table cannot resolve this.

The underlying raw graph carries relations. The proposer is **not** provided a named list of candidate concepts. Instead it enumerates (a) a direct actor-to-goal edge and (b) two-edge actor→intermediate→goal paths using relation labels found in the *unlabeled* training graphs.

Two candidate programs result:

- **direct(marked):** a badge edge, perfectly correlated with the hidden explanatory path in training.
- **path2(carries,reaches):** a two-edge graph relation, also perfectly predictive in training.

The **frozen validation** episodes reverse the badge correlation while preserving the two-edge relation. The badge candidate fails; the path candidate passes. Its small prediction table is learned from training, serialized with train/validation episode IDs, and checksummed. The checksum is a change detector, **not** proof that observations, authors, or sources are authentic.

The old diagnostic identifies irreducible surface collisions and produces HOLD. The new diagnostic proposes changing the *representation-search method*. It does not install that method in a live system; the successful cartridge remains **HOLD_FOR_HUMAN_REVIEW**.

### No sneaking knowledge in

- The program generator sees graph topology and relation names, **not the labels**.
- Truth-table fitting sees only the designated training examples.
- Candidate admission sees training and validation, **not holdout**.
- The holdout and intervention simulator are opened only for scoring the already chosen candidate.
- The evaluator, fixture author, and Python code do know the toy ground truth; this is a constructed demonstration, **not** an unknown real world.
- The fixed two-step grammar, variable x, XOR-generated outcomes, perfect evidence and small concept space are all developer choices. The program cannot invent an arbitrary mathematical primitive.

### Benchmark and classical control

Run `python benchmark.py` to obtain a deterministic JSON receipt; values are recomputed, not hardcoded in the report. The intended outcomes, checked in unit tests, are:

| Held-out outcome | Surface-only observer | Expanded graph program | Exhaustive classical feature selector |
|---|---:|---:|---:|
| Predictive accuracy in the path world | 0.50 | 1.00 | 1.00 |

**The classical exhaustive selector ties.** It is given the same grammar, training cases, validation cases and truth-table learner. This is not evidence that MOTIF beats established feature engineering or adaptive experimental design. The useful result is a *visible representation expansion* compared with a deliberately constrained original observer.

The experiment records independently simulated actor→intermediate→goal toggles while x and the badge stay fixed. It scores whether the frozen candidate predicts the changed outcomes. These are synthetic simulator interventions, not real-world causal discovery.

The held-out scoring records correct *permitted* positive plans, incorrect permitted positive proposals, and positive predictions blocked by the toy permission fence. No plan executes. The toy authorization bit is supplied by the fixture and cannot be inferred into a real-world grant of authority.

### Required negative results

1. **Confounded training:** Both candidate features fit training perfectly. Reusing training as validation gives **HOLD_RIVAL_MODELS**.
2. **Bad new evidence:** Flip one independent validation label; neither candidate has perfect validation accuracy, giving **HOLD_UNEXPLAINED_SURPRISE**.
3. **Out-of-grammar hidden cause:** An unrepresented independent bit changes outcomes even when the visible graph is identical. No generated concept explains it. The result is **HOLD_UNEXPLAINED_SURPRISE**, not a fictional invented dimension.
4. **Negative transfer:** The accepted path model gets only **0.50 accuracy** on an independently generated world where the badge rather than the path determines the outcome. The learned cartridge cannot be promoted across world boundaries without new evaluation.
5. **Permission:** Neither a valid path prediction nor a code checksum authorizes real-world action.

### Run

Requires Python 3.10+; no packages, API keys, internet or paid compute.

```sh
cd experiments/018
python -m unittest -v test_unknown_unknown.py
python benchmark.py
```

CI runs these same scripts on pushes and pull requests.

### What MOTIF-019 should try to falsify

1. **An unanticipated grammar, not a supplied search menu:** Let a learner propose new composition rules rather than only recombine typed one- and two-edge patterns.
2. **A self-diagnostic capable of losing:** Freeze unfamiliar, noisy and shifted worlds where the representational expansion makes calibration *worse*. Compare cost-aware Bayesian experimental design, feature construction, program synthesis and strong supervised controls on identical data/compute.
3. **An actual information-acquisition decision:** Hide some raw relational observations behind scoped, costly probes. Allow concurrent questions and adaptive stopping, borrowing from the separate MOTIF-015/016 experimental branches only through reviewed interfaces.
4. **Independent evidence and method-review gates:** Distinguish witness unreliability, wrong representation, wrong objective and wrong diagnostic. Preserve non-identifiability when interventions are not possible.
5. **Reachable future capability:** Define a non-gameable, independently adjudicated task-success metric that counts *newly feasible, valuable and permitted* actions, not just more graph edges or optimistic planning branches.
6. **Recursive methodology revision:** Compare original and proposed diagnostic criteria from identical pre-revision states, with sealed meta-holdouts and an unchanged external adjudicator. Neither diagnostic can unilaterally declare itself superior.

**Observed contradiction ≠ discovered hidden cause. New graph feature ≠ new general intelligence. Improved toy prediction ≠ consciousness. A method proposal ≠ admission or permission.**
