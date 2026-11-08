# QC-005 — THE FOREIGN WORLD TEST
**Research status:** frozen local-only symbolic learner, tested against externally implemented graph hosts; no merge or production installation.

## Research lineage and literal claims

The user's Quantum Code thread in National Treasure and Daily Slice describes a recursive architecture of **local constraints → transformed history → changed observation/decoder → further constraints**. QC-001 through QC-004 progressively implemented this analogy on synthetic classical graph-rewrite problems. None is a quantum physics experiment.

- [QC-001 PR #182](https://github.com/the-static-collective/MOTIF/pull/182): context-conditioned finite grammar.
- [QC-002 PR #185](https://github.com/the-static-collective/MOTIF/pull/185): infer anonymous edge-local graph deltas and compose them.
- [QC-003 PR #188](https://github.com/the-static-collective/MOTIF/pull/188): derive affected anchors from before/after graphs and introduce a researcher-permitted fixed-point observation when local questions fail.
- [QC-004 PR #189](https://github.com/the-static-collective/MOTIF/pull/189): enumerate typed relational algebra ASTs, independently locally review source-bound question cartridges, and test a favorable example of reusing one learned expression to build another.

QC-005 asks whether **frozen** QC-004 expressions transfer to structurally different host graphs produced by **NetworkX 3.6.1**, a separately maintained open-source graph library, without tuning their grammar against those graphs. It also tests a case the current language **provably cannot distinguish for the chosen local endpoint question** and compares against a separately written NetworkX-based AST search.

"Foreign" means foreign **graph topology source and size**: this is NOT an externally administered sealed blind benchmark. Our team still chose the target concepts and the 12 host families, and this repository contains the public test code. The learned expressions are classical and semantic-task-specific.

## Frozen pre-test contract

### Learning conditions

The QC-004 learner receives only the original **6 TRAIN / 4 VALIDATE unlabeled before/after synthetic graph pairs per structural question**, with no explicit anchor or action label. It proposes an AST from an 8-constructor bounded typed DSL, validates independently, and then **freezes** its program and source pin.

The three research questions are alternate-path membership, triangle membership and four-cycle membership for a candidate undirected edge. They correspond to these already selected expressions:

| Question | Frozen program |
| --- | --- |
| Alternate path | `TC(CUT)` |
| Triangle | `JOIN(CUT,CUT)` |
| Four-cycle | `JOIN(CUT,JOIN(CUT,CUT))` |

Test outcomes may **not** be used to select another AST, adjust the vocabulary, or repair an admitted model. If the model fails on foreign graphs, record the failure intact.

### Independent foreign source

The CI workflow installs **NetworkX==3.6.1** and constructs 12 topology-only sources using that library, including its real-data-backed Karate Club, Florentine families and Davis Southern Women affiliation graphs; plus external library grid, barbell, random regular, Watts–Strogatz, Erdős–Rényi, wheel, lollipop, path and cycle generators.

**Precise meaning:** graph classes and the algorithms to generate them are independently maintained; the chosen graph parameters, RNG seed 20261107, edge-level questions and overall experiment are still author-selected. The graphs are **not** training inputs. A deterministic fixture manifest logs graph names, sizes, edge counts and SHA-256 hashes for reproducibility.

All foreign node labels (including actual name strings and tuple nodes) are replaced by neutral IDs. All metadata is discarded because the experiment is **explicitly topology-only**. Directed graphs, parallel edges and loops must be rejected as unsupported. We DO NOT claim valid predictions about individual edge weights, chemistry, directionality, human identities or societal structure.

### Classical truth and competitor

The independent output oracle is implemented with **NetworkX graph connectivity after deleting an edge**, **common-neighbor intersection for triangles**, and **simple length-three paths for four-cycles**, each written separately from the MOTIF AST interpreter. The comparator constructs actual before/after graph edits independently and compares outputs modulo fresh-vertex renaming.

A **separately implemented classical grammar learner** gets the *same QC-004 TRAIN and VALIDATE rows*, the *same finite candidate AST grammar and order*, and uses **NetworkX graph/closure operations** instead of MOTIF's set-valued interpreter. It is assessed on the same foreign graphs. This comparison matches **training examples, validation examples, hypothesis class and candidate-enumeration allowance**, not CPU cycles, runtime, implementation optimizations, source authorship or external task priors. A tie is expected and must be reported.

The NetworkX truth oracle knows the task concept by name; this is an **evaluator** and correctness comparator, not a learner discovering natural-language task semantics. The independently implemented classical search learner is a closer match but still shares the predeclared grammar.

## Declared hypotheses and falsifiers

1. **H1 — transfer without tuning:** correctly classify the condition and predict the synthetic edited output for every source edge in all 12 external graphs, for each of the three already-frozen questions. Because these questions have exact mathematical definitions in the fixed representation, any error would be a bug or a representation mismatch, not a new physical discovery.
2. **H2 — matched classical search:** an independent NetworkX-based relational synthesizer with the same examples/grammar can select the same shortest consistent ASTs and achieve the same predictions. Any systematic disagreement is a falsifier warranting diagnosis.
3. **H3 — source integrity:** a changed validation digest makes an old prediction fail replay; directed/multigraph/self-loop data cannot be silently recast as the simple-graph topology the question assumes.
4. **H4 — unexpressible challenge:** add one completely isolated vertex to one of two otherwise identical source graphs, leaving the marked edge and all existing relations unchanged. Assign contradictory effects to the two worlds. No binary-relation program formed solely from E/CUT/ID, TC, JOIN, UNION, INTER and DIFF can distinguish **an endpoint pair on the original component** by the mere existence of a disconnected isolated vertex. This follows from structural induction on the relational operators: no constituent operation can connect the isolated vertex to an old vertex, so every expression's relation restricted to the old component is unchanged. An exhaustive search of all ASTs with cost at most 5 provides a bounded executable check; the correct response is **HOLD**, not arbitrary feature invention or fabricated certainty.
5. **H5 — provenance and input safety:** duplicate evidence IDs, a forged source status, contradictory validation on the same target edge, an unsupported concept or an ill-typed AST must refuse or hold.

## Verified experimental results

See the dedicated Actions workflow output for per-source breakdown and candidate AST search counts.

- **12 separate NetworkX-produced graph hosts, 754 source edges each tested three ways.**
- **754/754** alternate-path classifications and generated output graphs match the independent oracle.
- **754/754** triangle classifications and outputs match.
- **754/754** four-cycle classifications and outputs match.
- **2,262/2,262** total edge-level predictions; no unsupported graph question was silently answered.
- **555/555** exhaustively enumerated bounded ASTs fail to distinguish the deliberate isolated-component pair. No rule is admitted; status **HOLD_UNEXPRESSIBLE_IN_DECLARED_DSL**.
- **Independent NetworkX classical learner:** searched exactly **4 / 16 / 310** ASTs for alternate path / triangle / square using the same samples and grammar, chose the **same three expressions**, and predicted **754/754 per task** on the foreign test graphs. This is a **tie**, not a performance improvement. Hypotheses/examples and candidate counts match, but CPU budgets do not.
- Run verified unit tests and check all job steps, not simply the Actions badge.

## Crucial limits

These results show *transfer of exact graph-theoretic predicates to larger and more varied graphs*, not autonomous concept discovery from an unknown domain. The target concepts, node/edge representation, validation labels and the DSL were all provided by the experiment design. The named real-world graph sources do not imply conclusions about the people represented by those datasets.

No uncontrolled Python generation or execution; no memory-trained neural network; no ability to infer a hidden action selected by another agent; no quantum execution; no autonomous production merge; no demonstrated mathematical novelty. The natural question is whether the system can choose among **genuinely new representations** from different domains using externally authored tests and matched resource budgets.

## Reproduction

Python 3.11 with a pinned optional graph dependency:

    python -m pip install networkx==3.6.1
    cd experiments/quantumcode005
    python -m unittest -v test_trial.py
    python trial.py

The workflow is `.github/workflows/quantum-code-005.yml`. It records foreign graph checksums, frozen model pins and every task's edge-level results in GitHub Actions stdout.

## Next real falsifier

Reproduce with a *truly independently authored*, sealed input/target task set whose distribution and language-to-math relation were withheld from the system designer. Equalize not only sample count and grammar size but also actual query/runtime/compute budgets; include noisy evidence, unseen algebraic operations and domain representations that cannot be losslessly mapped to simple undirected graphs. Compare against standard ILP/SyGuS graph learners. If the model cannot solve an unfamiliar task, preserve HOLD and the counterexample. Extend the grammar **only by a separately reviewed proposal** after that result is frozen.
