# FIELD-008 — BLANCHING FRONTIER: PRE-SCORE PROTOCOL
2026-11-10. Commit this protocol before executing the scored benchmark. No change to the declared primary endpoint after outcomes are inspected.

## Hypothesis
A version-space investigator may **temporarily blanch** several evidence-consistent graph hypotheses, trace 2–5 conditional reasoning hops to candidate verifiable probes, and select one deeper observation that resolves multiple open questions. A branched hypothesis is never promoted into a fact; descendants retain assumption lineage and are withdrawn if contradicted. The experiment tests whether this policy yields an **independent gain over strong classical question selection**, not merely over a depth-1 baseline.

## Independent preexisting source
Use NetworkX **3.6.1** implementation of Read & Wilson's *Atlas of Graphs* (1998), containing 1,253 graphs up to 7 vertices. Pin a canonical normalized corpus SHA-256; never invent Atlas records. 6-node full cohort = all 156 Atlas graphs. Additional 7-node challenge = deterministic **96** graph IDs chosen by SHA256 hash of `FIELD008/7-node/audit/ID` (not performance). The candidate model inventory contains ALL Atlas graphs of the same vertex size and same **initial source-verified edge count**; actual selected graph ID is hidden from chooser but corpus available as an enumerated candidate catalogue. This is not blind research: the catalogue and feature grammar were authored/prepared by us.

## Query and conditional grammar
Starting INK facts: number of vertices and edge count, from a *single* corpus-backed owner; count it as **one provenance origin**, not independent corroboration. Graph hypotheses matching these facts remain PENCIL. Allowed read-only **one source observation per query**: named `edge(i,j)` depth 1; `degree(i)` depth 2; `common_neighbors(i,j)` depth 3; `triangle_count` depth 3; `four_cycle_count` depth 4; `is_connected` depth 4; `bridge_count` depth 5; `articulation_count` depth 5. Derivations are authored typed operations; all conclusions computed *as if* a possible graph were the world and are conditional. No graph change, outside action, assumption-to-fact shortcut, or source authentication from hashes.

## Budget and comparisons
Exactly up to **4 additional source queries** (HOLD if no discriminating questions). Deterministic tie breaks.
- NEAR: classical depth-1 edge-only maximum pair-discrimination.
- ENTROPY: strong classical one-step Shannon information gain across the **entire same depth-1..5 probe catalog**.
- GINI: strong classical one-step pair-discrimination across the **entire same catalog**.
- BLANCH: breadth of downstream property uncertainty resolved (connected, triangles, 4-cycles, bridges, articulations) across all evidence-consistent conditional worlds, then pair discrimination. Blanched branch beam may suggest questions, but elimination and scoring must retain **all** consistent hypotheses, never discard a competing explanation merely because it is lower-ranked.
All methods receive exactly the same initial evidence, candidate models, probe catalog, and number of source questions. Report extra computation cost (candidate evaluations and conditional evidence edges). No paid LLMs.

## Primary / secondary / falsifier
Primary: number of **uniquely identified source graphs** after four questions in 6-node cohort, compared to the **better of ENTROPY and GINI**. A strict reproducible win is necessary to claim a gain over the stated classical competitors. 7-node 96-graph cohort is additional explicit transfer check; report separately, no combined p-values. Secondary: exact structural property resolution of the five target attributes across all surviving worlds, query depth/number, and source query spend. Property resolution is not verifying a new mathematical law; it is reduction in uncertainty about a known source record.

If BLANCH ties/loses strong classical, record the negative result. All outcomes use historical source graph truth computed after question proposal. Receipt verification must reject changed owner state, forged/rehashed report, invalid question, stale revision and self-referential supporting evidence. Bound and label all proposed worlds; no mass deletion of independently supported alternatives. Do not claim future physical fact or real-world probability of hypotheses from the finite version space. A full-catalog GINI tie is normal if the objective collapses to pair discrimination.

## Development limitations
This is pre-score against a known historical graph collection, NOT a prospective or source-owner-blinded field study. Query costs are modeled as equal **source calls**, while computational costs and algebraic depth differ; report this distinction. Preserving source-level identity does not establish witness independence. Code cannot merge/deploy itself; PR must remain a research draft.
