# QC-006 — SYMBOLIC MEANING REMIX / REPRESENTATION INVENTOR

**Status:** classical synthetic research, local review only; stacked on QC-005 and its preceding open drafts. Nothing is installed or merged into MOTIF production.

## Why start with symbolic meaning?

The user's proposal was to begin representation invention by **remixing symbolic meaning**, rather than only adding new hard-coded mathematical operators. We can make that testable without treating a graphic mark as a physical particle or equating speculative historical correspondences with mathematical evidence.

In [National Treasure's Quantum Code glyph-circuit](https://github.com/the-static-collective/national-treasure/blob/main/cases/quantum-code-glyph-circuit/README.md), the boundary condition and interpretation are distinct. [Daily Slice: The Field Is Not the Message](https://github.com/the-static-collective/the-daily-slice/blob/main/slices/2026/08/2026-08-26/the-field-is-not-the-message.md) explicitly separates field, glyph, path, meaning and authority. [Grow a World That Knows How to Read the Seed](https://github.com/the-static-collective/the-daily-slice/blob/main/slices/2026/08/2026-08-26/grow-a-world-that-knows-how-to-read-the-seed.md) suggests that the same small carrier may be understood differently by a receiving decoder.

These lead to the engineering proposal:

> A symbolic mark is a *carrier*. Its computational meaning is a typed, independently checked **binding between mark + decoder context + operation + evidence**. New meanings are candidate programs, not declarations of universal spiritual or physical authority.

The mark **◈** is arbitrary and deliberately *not* identified with any historical Hebrew glyph, language, theological claim, subatomic entity, or real-world person.

## The representational failure we begin from

QC-005 [PR #191](https://github.com/the-static-collective/MOTIF/pull/191) made an endpoint-only binary-relation DSL HOLD when the only difference between two worlds was an **isolated vertex elsewhere in the graph**. No operator formed solely from endpoint relations E/CUT/ID/TC/JOIN/UNION/INTER/DIFF could tell that such a disconnected vertex existed. An exhaustive cost≤5 search found **555** observationally indistinguishable ASTs. The certified result was a useful refusal, not a fabricated prediction.

QC-006 tests a **separately researcher-supplied representational expansion**: typed **vertex sets** and **Boolean quantification** about the whole graph. We do not claim it autonomously invented that new type system. We ask whether, after the allowed DSL is expanded, the learner can construct a *specific meaning* using evidence rather than being given a named `HAS_ISOLATED` oracle.

## Frozen typed search vocabulary

The generator constructs expression trees with at most 5 nodes. Each constructor has an explicit type:

| Constructor | Type | Meaning |
|---|---|---|
| ALL | VertexSet | Every current graph vertex |
| ANCHORS | VertexSet | The two old endpoints of the candidate graph edit |
| ADJ(Set) | VertexSet → VertexSet | Union of neighbors of those vertices |
| MINUS(Set, Set) | VertexSet×VertexSet → VertexSet | Set subtraction |
| UNION / INTER | VertexSet×VertexSet → VertexSet | Set union / intersection |
| ANY(Set) | VertexSet → Boolean | Whether a set is nonempty |
| EVEN(Set) | VertexSet → Boolean | Whether its cardinality is even |
| NOT(Boolean) | Boolean → Boolean | Negation |

Cost is standard AST node count; Boolean-typed expressions are candidate meanings. Enumeration is generic and cost ordered, with basic duplicate suppression. An ill-typed AST, unrecognized operator or AST over budget **cannot execute**, and no generated Python is ever evaluated.

### The source-owned synthetic learning task

The researcher-authored evaluator supplies a *hidden* Boolean law: if a graph has any isolated vertex, use one anonymous two-fresh-node edit; otherwise use another anonymous local edit. As with QC-003/004, training records consist only of synthetic BEFORE/AFTER graphs (no law name, symbolic interpretation or explicit anchor), and the affected edge and effect are inferred from structural difference.

- **12 TRAIN** examples: connected path cores of varying parity, with 0 / 1 / 2 / 3 isolated vertices, positive and negative examples both of even/odd total graph size.
- **12 independent VALIDATE** examples: different, longer source graphs and source IDs.
- **16 TEST** examples: larger source graphs with independent labels, never used for selecting or reviewing candidate expressions.
- **48 additional foreign-graph interventions**: the 12 NetworkX 3.6.1 host graph families from QC-005, each with 0 / 1 / 2 / 3 *isolated* vertices added, scored against the independent `nx.number_of_isolates()` semantics. These host graphs are different from the path training distribution, but researcher-selected and publicly inspectable, **not sealed blind test data**.

The first TRAIN-consistent candidate is frozen, then must pass both positive and negative VALIDATE evidence to be admitted into a local-only lexicon. A deliberately contradictory validation outcome at the *same edge* causes HOLD. Source IDs, evidence hashes and decoder types must be reconstructible.

### Expected chosen meaning

The search has to synthesize the global expression:

    ANY(MINUS(ALL,ADJ(ALL)))

Read: **"Does the set of all vertices contain at least one vertex that is not adjacent to any vertex?"** This is true exactly when at least one vertex has degree zero for simple undirected loopless graphs.

This is a new representable observation relative to QC-005's restricted endpoint graph-relation language, **not a novel theorem or invented mathematical primitive**. The author explicitly supplied the typed ALL, ADJ, MINUS and ANY constructors, their meanings and the search ceiling.

## The symbolic remix

The same arbitrary carrier **◈** is independently bound to two different evidence-checked meanings:

| Carrier | Decoder context | Resulting meaning |
|---|---|---|
| ◈ | WHOLE_GRAPH | `ANY(MINUS(ALL,ADJ(ALL)))` |
| ◈ | EDGE_LOCAL | QC-004's previously validated `JOIN(CUT,CUT)` (triangle membership) |

The **context is explicit**. Given the same graph and same candidate edge, it is possible for one decoder to answer *false* and the other *true*. If the caller supplies only ◈ without a decoder, the system returns **HOLD_AMBIGUOUS_DECODER**, not one preferred answer. Unknown symbols and unknown decoder contexts also HOLD. A status-only or pin-forged meaning cannot be admitted.

This represents *local, context-conditioned mathematical polysemy*. It does not demonstrate that human words have been grounded, that symbolic glyphs carry intrinsic physical meaning, or that semantics can be inferred without before/after feedback and a predeclared decoder coordinate.

## Independent classical controls

The learned global expression is evaluated against a separate NetworkX oracle for isolated vertices. Additionally, `classical_meanings.py` implements a **separate NetworkX-based interpreter for the same typed grammar** and searches the **same candidate AST enumeration** with **identical TRAIN and VALIDATE rows**, then evaluates on the same TEST examples.

Expected: the classical learner finds the **same** cost-5 expression, examines the **same 43** candidate ASTs, and ties all TEST outcomes. This is an intentionally strong *matched data and hypothesis/candidate enumeration* comparator. CPU time or wall clock budgets are not matched; neither system is claimed to be faster or smarter.

## Predeclared falsifiers and authority limits

- If an expression from the old binary endpoint grammar already distinguishes the paired isolated-vertex worlds under the stated semantics, the alleged representation gap is false.
- If `EVEN(ALL)` (a trivial size-parity shortcut) separates the examples, the training cases are insufficient. The paired examples deliberately include *both parities for both labels*.
- Any TRAIN/VALIDATE evidence overlap, fake source ID, contradictory validation, false provenance, nonreconstructible meaning pin, duplicate symbol-decoder binding, or status escalation must refuse.
- A new graph with a triangle but no isolates must yield **different answers** when ◈ is interpreted by its EDGE_LOCAL and WHOLE_GRAPH decoders. If the meanings collapse or the context is silently guessed, the symbolic remix model fails.
- Directed graphs, multigraphs, edge weights, self-loops and non-graph observations lie outside the current semantics; they must not silently be treated as ordinary graphs.
- The local cryptographic digests are content receipts, *not signed proof of external events*.
- No production changes, unrestricted code generation, tool dispatch, new physical law, quantum computation, human-language comprehension or spiritual insight are demonstrated.

## Reproduce

From a checkout of this stacked branch:

    python -m pip install networkx==3.6.1
    cd experiments/quantumcode006
    python -m unittest -v test_remix.py
    python remix.py

The dedicated GitHub Actions workflow `.github/workflows/quantum-code-006.yml` verifies both code and report. Review its actual job results, logs, and upstream branch changes before proposing a merge. All demonstrations are synthetic and review-only.

## The next meaningful challenge

**QC-007 should not simply add every conceivable new operator to this toy grammar.** Instead test a blinded program of representation proposals from different domains (graph connectivity, ordinal time, acoustic intervals, symbolic language), with independent externally written validation cases and competing semantic bindings. Allow multiple interpretations to coexist and ask a *discriminating experimental question* when ambiguity cannot yet be resolved. Introduce counterexamples that break the learned meaning and require **source-pinned revision rather than silent overwriting**.

Only externally validated improvement under genuinely matched classical compute/sample budgets can support stronger claims of adaptive, compounding mathematical reasoning.
