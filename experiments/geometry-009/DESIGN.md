# MOTIF GEOM-009 — The Geometry that Questions Itself / Free Graph Grammar Frontier

**Status: synthetic, executable research branch.** Built on the still-open GEOM-008 branch, not merged into `main`. All entities are PENCIL, scope-bound and source-declared; no external evidence authentication, authority, production integration or autonomous actions.

## The user's experiment

1. Let the structure of MOTIF's thought graph be **free-form**, neither constraining it to 13 nodes, a fixed lattice, a max hyperedge arity, nor a predetermined depth.
2. Give it an explicit **representational gap**: labeled before→after transitions its current rewrite grammar does not already explain.
3. Search for a new reusable rule, test against labeled examples, compare independently generated candidate graph futures, and archive only a **PENCIL** grammar revision.
4. Temporarily set graph growth work budget to **1,000,000,000,000,000 (10^15)** to see what happens; retain an explicit monotonic time slice and the unavoidable physical disk/RAM limits. Never execute a truly unbounded loop.

## Actual functions

- `candidate_patterns`: exact single-span insertion, deletion or replacement enumeration from one demonstration. The generator does not impose an arbitrary node count, rule-arity or token-count ceiling; time/memory costs grow with input length. This is classical symbolic program synthesis/anti-unification, not learned natural language or consciousness.
- `propose_revision`: requires at least two separately *declared* positive roots by default, a diagnosis that at least one positive is not already explainable by the parent grammar, a finite per-call candidate budget, and a deterministic source/dataset-bound continuation cursor. It chooses using training **only**, then evaluates frozen heldout once. Incomplete search returns `CONTINUE_SEARCH`, not an invented proof of absence or optimality. Exactly reproducing a proposed input is not evidence of real-world truth.
- `compare_fork`: compares parent versus the proposed new grammar in **different isolated in-memory SQLite hypergraphs** with the same seeds and expansion allowance. A missed target in an unfinished frontier is explicitly `unknown`, not `false`.
- `preserve_proposal`: recomputes the claimed scores, verifies parent scope, then adds a candidate node and N-ary lineage relation to the persistent graph as PENCIL. It does **not** rebind the parent grammar, import into THOUGHT-006 PEN, merge branches, authenticate witness roots, or perform external actions.
- GEOM-008's unchanged `LivingGraph` is included here for standalone replay; graph shape remains freely emergent from user-declared syntax and rule effects. Its purpose is to preserve a graph rather than force geometric positions to assert meaning.

## Results

See `experiment-results.json`, `benchmark-results.json` and `high-budget-results.json` (all produced locally). The main fixed demo sees parent grammar saturate without ever reaching two requested `branch` targets. From three separately labeled positive demonstrations it proposes `bud -> branch`. A fork with this one additional rule reaches both targets. It archives the hypothetical candidate separately, with lineage and without changing the existing graph's grammar. This is **supervised induction from a supplied goal**, not unconstrained invention of semantic truth.

The heldout benchmark deliberately contains unmodeled context-specific negative cases. Failures on those controls are important: the induced context-free rule cannot distinguish the exceptions. This is a route toward more expressive grammar and explicit representation of contextual predicates, not evidence that arbitrary semantics are already solved.

### The intentionally huge growth experiment

`stress_frontier.py` requests **10^15 expansions per invocation** rather than GEOM-008's prior 16,000-work benchmark, but uses a separate finite `seconds` argument (monotonic-clock deadline). With a controlled 2-branch grammar the growth frontier stays safe to resume and SQLite stores it incrementally. A large earlier stress invocation was interrupted by the external tool runtime; the persistent SQLite file survived and passed `PRAGMA integrity_check` and `foreign_key_check`. It was resumed and reached the totals recorded in `high-budget-results.json`. No larger record is claimed from the interrupted attempt.

Synthetic binary-tree invariants are `nodes=2×expanded+1`, `relations=3×expanded`, `unexpanded=expanded+1`, checked against SQL counts. **The graph is large but still a very simple binary rewrite tree.** Size alone is not cognitive improvement or an emergent theorem. RAM/disk and worst-case per-node work are still resource constraints; time slices do not interrupt a single pathological node transaction.

## Controls and falsifiers

- Unit tests: grammar induction, redundant-rule abstention, origin gate, provenance, tampered proposed score, immutability, scope mismatch, partial-fork uncertainty, wrong budget/type refusal, malicious command refusal, deterministic continuation, heldout non-leakage, and 120 seeded small exhaustive enumeration cross-checks for possible single-span rewrites.
- Test against a **memorization-only** baseline and the existing parent grammar; heldout cases have different contexts/prefixes from the training sample.
- Include adversarial context-specific forbidden examples where an unconstrained `bud -> branch` is wrong. Count false positives explicitly.
- Future work should discover more expressive conditional/multi-step/type-aware operators, where source authentication, counterevidence, causal provenance, relation permissions and guarded rule execution are independently owned by ALEX, Free Graph, 3rdi, THOUGHT-006 and LOADOUT.

## Reproduce

```sh
cd experiments/geometry-009
python3 -m unittest -v test_grammar_invention.py
python3 demo.py
python3 benchmark.py
python3 interface.py example-input.json
python3 stress_frontier.py --seconds 1 1
# Optional experimental near-unbounded expansion: local process, finite time
python3 stress_frontier.py --seconds 5 5 5 --work-budget 1000000000000000
```

GitHub CI runs only small deterministic checks, **not** the large stress, to avoid unbounded public CI usage.

### Important distinction

> A free graph is not free compute. A proposed grammar is not evidence. A structure that fills available space has not necessarily learned anything. MOTIF's strongest future proof must be improvement on frozen, independent tasks with a correct abstention and honest runtime cost.
