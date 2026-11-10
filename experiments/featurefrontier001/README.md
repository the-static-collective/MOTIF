# FEATURE-FRONTIER-001 — Compose the missing mathematical vocabulary

**Status:** frozen, executable, synthetic experiment. This does **not** invent a completely new mathematical operator, prove general theorems, establish source authenticity, or modify a deployed agent.

## Question

Can MOTIF construct a useful structural graph feature from a primitive edge relation, *without the investigator handing it the precomputed `common_neighbors` or `connected` features*, then infer two observable graph transition laws, test counterexamples, and build an executable child?

## Executable design

- **Carrier and actual upstream modules:** `nunumathal.Graph` is the source of immutable undirected graphs, and `contractfrontier002.observed_outcome` supplies two *separately computed* outcome labels after a proposed edge addition: change in triangles and change in connected components. No generic physical-world simulator is claimed.
- **Predeclared primitives:** `E(u,v)` (edge membership), variables `a,b` (the proposed edge endpoints), bound variable `x`, optional existential variable `y`, finite conjunctions of up to three edge atoms, `COUNT DISTINCT x`, and the *generic* transitive-closure operator `E*` (plus path-length-limited variants). The system does **not** receive `common_neighbors` or `connected` as individual candidate features. However, the ability to form relational queries and compute closure is explicitly supplied, not invented.
- **Search:** enumerate **237** typed integer program candidates, including constants and simple affine transformations of the generated feature expressions. `discover` performs version-space filtering against the exact outcomes of *selected* training interventions. Selection uses only pre-intervention graphs and surviving candidate predictions; it cannot see an intervention's true outcome until after choosing the probe.
- **Validation:** freeze the simplest consistent program only after the remaining programs become observationally equivalent on unqueried training inputs. Validate on a separate split without replacing a failed law. Check held-out and larger OOD graphs only after freezing.
- **Generated child:** a fixed-template Python interpreter serializes the two learned feature ASTs; it reruns learning against pinned trusted code, exercises an unseen synthetic graph, and produces a receipt. A subprocess is **not** a secure sandbox for untrusted Python. Source hashes indicate changes, not author authenticity.
- **FIR admission:** exact finite replay may be `F_LOCAL`; universal mathematical or real-world correctness remains an `I` (proposal).

## Observed results (local, before GitHub CI)

| Measure | Result |
| --- | ---: |
| Candidate programs | 237 |
| Actively chosen training interventions | 5 |
| Held-out synthetic graph cases | 108/108 correct |
| Larger / varied OOD graph cases | 110/110 correct |
| Random selection, same five-probe budget | 8/20 seeds identified a validation-passing program |
| Random selection, twelve probes | 19/20 seeds identified one |
| Strong pre-existing handwritten baseline | 218/218 correct |
| Constant-zero baseline | 39/218 correct |
| Retrain with multi-atom joins forbidden | `HOLD_NO_RELATIONAL_EXPLANATION` |
| Retrain with unrestricted closure forbidden | `HOLD_VALIDATION_COUNTEREXAMPLE` |

The inferred programs are:

```text
triangle_delta = COUNT(x : E(a,x) & E(b,x))
component_delta = EXISTS((E)*;a,b) - 1
```

The first is the previously known **common-neighbor** result, obtained here as a synthesized two-atom conjunctive query. The second uses generic transitive closure to determine pre-existing endpoint reachability. Neither mathematical theorem is new; the finite language contains the operators needed to express them. Some more complex observationally equivalent programs remain in the surviving version space; the implementation makes a canonical **simplicity** selection rather than pretending to have proved syntactic uniqueness.

The train, validation, test, and OOD families are author-generated, overlapping in mathematical mechanism. The reported cases do **not** measure independent scientific generalization, outside-domain performance, or novel universal vocabulary invention. A handwritten strong baseline ties the generated solution exactly. A search over only five randomly chosen interventions often fails because the relevant relational programs remain indistinguishable.

## Independent falsification and controls

38 targeted tests cover real imports, finite algebra, path length > finite-horizon candidate (23-edge chain), disconnected bridges, two-common-neighbor counts, vertex relabeling, source and child tampering, train/test isolation, graph-class ablations, malformed queries, duplicate split IDs, insufficient intervention budget, FIR epistemic scope, actual generated-child execution, and exact comparison with the previously handwritten `contractfrontier002.features` oracle.

**Adversarial caveat:** If an upstream graph representation and all observations were corrupted in mutually consistent ways, this calculation could also be fooled. The finite replay tests exercise typed-outcome tampering, not an independent source of ground truth.

## Reproduce

From the stacked MOTIF checkout (Python >=3.10, standard library):

```sh
cd experiments/featurefrontier001
python -m unittest -v test_featurefrontier.py
python featurefrontier.py
python benchmark.py
```

The dedicated CI also runs the relevant FIR, mathal, contract discovery, and contract frontier regression suites.

## Next question

Can MOTIF *extend its own representation language* when no composition of its available operators can explain what it observes? Test candidate **grammar expansions** against held-out problem families and the cost of expanding search, rather than falsely asserting that every unexplained observation must indicate a missing operator.

**Stack:** This draft experiment depends on unmerged `experiment/contract-frontier-002-20261109` and all of its preceding research branches. This is not deployed to JAR;VIS or wired to real-world actions.
