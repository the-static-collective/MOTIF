# MOTIF GEOM-008 — The Geometry That Questions Itself / The Free Graph Frontier

**Status:** executable, isolated, local Python-stdlib synthetic research branch. Based on open GEOM-007 PR #121, which itself inherits GEOM-006 and GEOM-005. Not merged into `main`. No real-world source authentication, autonomous network calls, production JAR;VIS connection, or PEN promotion.

## The two requests this attempts to answer

1. **Can the reasoner recognize when its existing relation vocabulary is inadequate, propose a composed new operator, and test it against untouched examples?**
2. **Can it make its own graphs without a Flower-of-Life/13-circle/4096-world ceiling, allowing arbitrarily typed and n-ary relationships to grow as the process unfolds?**

The implemented answer is a scoped **yes within explicit symbolic grammars**, not unrestricted autonomous understanding. The system has no fixed total **node**, **relation**, **depth**, **hyperedge arity** or **operator composition length** limit, but *every invocation has finite work*, hardware is finite, and neither a pretty map nor a program-synthesis hit authenticates a claim.

## 1. Living Graph: grow the structure instead of drawing a fixed template

`living_graph.py` stores a typed, attributed, **PENCIL-only hypergraph** in a local SQLite database. There is no 13-node global limit and no assumption that a thought must be a binary relation. A relation has any number of role-labeled participants: parent/child, evidence/claim/challenge, witness/case/context, etc. This is a graph data representation, not a claim that the relationships are true.

- `LivingGraph.add_node` and `add_relation`: preserve arbitrary declared kinds and N-ary roles; source-root **labels** are not cryptographic provenance.
- `RewriteRule`: caller-declared finite sequences of tokens can transform into other sequences. An empty find pattern enables insertion. Mutually reversing rules generate cycles; rules with `# → 0 #` and `# → 1 #` generate an indefinitely extensible binary tree with typed fork relations.
- `grow(work_budget=N, seconds=S)`: each call expands at most N pending nodes (and optionally checks a time slice **between nodes**). New nodes enter a persistent FIFO SQLite frontier. It never treats this invocation budget as a global graph bound. The exact grammar is fingerprinted and cannot silently change mid-run; fork a new graph to reinterpret its derivation history. A very high-branching single expansion can still be expensive; per-derivation yielding remains future work.
- Reopening the same SQLite file resumes the same unexpanded frontier without duplicating nodes or edges. A repeated seed is idempotent.
- Each node/edge has stable content-derived IDs. Hypothetical rewrite edge provenance includes rule name and application position. Duplicate outputs are deduplicated, original statuses cannot change from `PENCIL` via this module.
- Scope is declared observer/cut/decoder identity; a mismatched scope refuses to open an existing graph. This is a label-based local fence, **not** live authentication.
- `node_page`, `relation_page` use indexed keyset pages; `neighborhood` returns a deliberately **partial** proximity view with caller-set node/relation/hop budgets, not a promise to load the entire graph into memory.
- `display.render_dot` exports this *small view* as ordinary Graphviz DOT with n-ary relations as hubs. No geometry is imposed on the underlying data, and spatial positions have no authority. A different renderer could choose hex, radial, spring or NONE without changing data.

**Why this matters:** The Flower of Life may be a useful optional visual alphabet. It is not a prison or a mandatory ontology. The graph can exceed the visible geometry, develop cycles, new relation kinds, many-to-many associations, disagreement and derived paths; the viewing window stays small while the graph persists.

### Explicit physical limits

Not “infinite”: SQLite space, disk, RAM, the runtime of individual rewrite applications, file system and CPU limits all exist. The system **does not** offer a limitless background agent. It does not infer an arbitrary new string-rewrite rule from natural language. Rules are supplied; the *structure* they generate emerges from rule closure. At huge scale, partitioning, concurrency, per-derivation checkpoints, collision audits, and graph-store profiling remain necessary before production use.

## 2. Compositional operator invention: repair a missing reasoning vocabulary

`repair.py` searches a recursively extensible typed **path-expression** grammar. Atomic vocabulary consists of the distinct edge kinds present in *training* worlds, optionally including inverse relations. A candidate consists of one or more typed directed atoms composed in order:

```
carry ○ serve
```

The expression asks whether a path runs from `start` by a `carry` edge and then a `serve` edge to `goal`. That compound relation can distinguish a world even when no single edge type can. The operator is not in the input atomic list: the algorithm **synthesizes its composition by enumeration**.

- Programs are enumerated by increasing length. There is no fixed *global* composition length; caller supplies a finite per-call candidate evaluation budget and may provide a length ceiling.
- State uses indexed `(depth, offset, domain fingerprint)` cursors so the caller can resume a search from a later invocation without trying every earlier candidate again.
- The first training-perfect program is selected **without looking at heldout labels**. Heldout performance is reported afterward and may be worse; the algorithm does not rewrite results to claim success.
- A separately chosen **best atomic relation** serves as a matched, weaker classical baseline. This is classical enumerative program synthesis, not a new scientific principle or an all-possible-reasoning-language inventor.
- `inspect_composition_on_graph` can apply a typed path composition to the persistent hypergraph **read-only** using a finite transition budget. When that budget expires it reports **INCOMPLETE_RESOURCE_SLICE**, not a false negative.
- `preserve_as_pencil` independently recomputes the candidate's declared train/heldout scores, appends a `reason_cartridge_candidate` node and an arbitrary-arity witnessed-evaluation hyperrelation. No evidence is promoted, no tool is executed, and no outside authority is granted.

### The adversarial demonstration

Two classes of synthetic graph have the same count of `carry` and `serve` edges. In class A the *order and endpoints* produce `origin →carry→ middle →serve→ destination`; class B has `serve → carry` and no equivalent target route. A one-hop relation check cannot discriminate them. `carry ○ serve` can.

In the fixed-seed benchmark:

- 20 developer-generated training worlds; the chosen two-atom program classifies 20/20.
- 100 separately instantiated but **same-generator** heldout worlds; the program classifies 100/100. The best single-atom baseline classifies 50/100.
- This demonstrates a representational *gain over the deliberately restricted atomic baseline*, **not** superiority to a general classical reachability algorithm. A competent classical two-hop query matches it. There is no proof of open-world generalization.
- A negative control with relabeled heldout answers explicitly reports failure; it does not use those labels to retune the selected program.

## 3. Verification evidence

`test_geometry008.py`: **26/26 unit tests** passed locally. Includes an **independent 70-case exhaustive path-witness oracle** over randomized small worlds, composition cursor/heldout tests, a deliberate hostile JSON field, cycle saturation, scope and grammar mismatch refusal, arbitrary 31-participant hyperedge, large growth beyond GEOM-007's former graph bounds, replay across a SQLite reopen, paging, DOT escaping, explicit PENCIL statuses, and partial-budget negative controls.

`stress-results.json` (local environment, Python 3.13, Linux SQLite; timings not portable):

- Two `grow(work_budget=8,000)` calls, same persistent graph; **16,000 expanded nodes**.
- **32,001 graph nodes**, **48,000 relations**, **16,001 still-unexpanded nodes**.
- ~79.5 MB SQLite allocated in the local test; ~14.7 seconds for both growth slices in this environment.
- SQLite foreign-key and integrity checks succeeded.

A default short benchmark with 1,200 expansions runs in the dedicated CI workflow. The longer stress benchmark is not automatically run on every PR.

## 4. Reproduction

```sh
cd experiments/geometry-008
python3 -m unittest -v test_geometry008.py
python3 demo.py
python3 benchmark.py
python3 interface.py example-input.json --db /tmp/motif-free-graph.sqlite --dot /tmp/motif-local-view.dot
# Run that same interface command again; it resumes from the existing SQLite file.
# Optional larger stress test:
python3 benchmark.py --expansions 16000
```

`interface.py` uses exactly the supplied local JSON and SQLite paths. It does not execute source code, access a network, run a language model, or obtain new permission. The DOT file is only the requested local **view**, not the full graph.

## 5. Ownership boundaries / follow-on work

- **GEOM-005:** optional geometric scratchpad; its coordinates remain a non-evidentiary display.
- **GEOM-006:** temporal ancestry and observer knowledge cuts. GEOM-008 does not turn a synthetic grammar's derived relations into historically admitted edges.
- **GEOM-007:** finite local-to-global contextual solver. Its 9-context/13-variable/4096-combination refusal is unchanged; GEOM-008 removes graph-growth ceilings **in a separate experimental subsystem**, not by pretending the older CSP is magically scalable.
- **THOUGHT-006:** pencil/pen ledger. Proposed macro stays pencil; an isolated SQLite graph is not a pen event, signed evidence or outside action authorization.
- **ALEX / Free Graph / 3rdi / LOADOUT:** no live mutation or integration, and source-root labels are never authenticated. Scope strings are not a substitute for true observer/capability receipts.
- **MEMENTO/Novelist:** future consumers of alternative attributed graph narratives; nothing here becomes story canon.

**Most important next falsifier:** test heldout worlds with shifted graph motifs, adversarial distractions, causal confounds, and grammar-missing primitives. A real representation-improving system must notice that neither atom enumeration nor path composition suffices, propose *new safe primitives* through validated type rules, and withhold unsupported answers. Compare equal-compute classical planning and query-synthesis baselines, not only atomic features. If there is no measurable improvement, report parity or failure.

**Principle:** Free graph form, bounded local computation, permanent source distinctions, no geometry-induced truth, and no promotion of hypothetical relationships.
