# MOTIF LEGIT-020 — APERTURE × DOGRAM × MATHALIZING

**Status: research HOLD.** Executable experiment. No production promotion, automatic factual interpretation, new public Dogram operator, general natural language model, or historically new mathematical theorem.

## The proposed bridge

The user's idea is that MOTIF may benefit from keeping multiple perspectives visible *before* translating language into mathematics. The existing Static Collective APERTURE architecture specifies:

    RAW → SIGNAL / CONTEXT / GAP → SENSE FIELD
      → FACT / IDEA / RELATION → SUBSTANCE / LINEAGE / AUTHORITY

The three independent triads create a sparse 27-cell address space, not an obligation to manufacture 27 objects. Different plausible readings belong to different possible mathematical questions. Context can narrow that set but cannot rewrite an old receipt or establish a person's intention.

This experiment uses **mathalizing** as the working name of a deterministic, bounded bridge:

    original utterance
      → multiple candidate readings
      → declared perspective and type
      → finite mathematical question
      → Dogram calculation or Z3 proof/counterexample
      → language gloss, lineage and unresolved gap

It is a *research implementation of a proposed workflow*, not an assertion that mathalizing is an externally established technical discipline.

## Actual project sources, not only metaphor

Four real Dogram mathematical modules are pinned as exact, byte-identical research copies and checked against the original Git blob SHA-1 digests:

- path_tree_test_language.py — path/walk counts, branching star homomorphisms, independent finite enumeration, exact all-length recurrence certificates.
- probe_partition_refinement.py — declared probe partition refinement and finite factorization.
- anti_collapse_reachability.py — information lost by a lawful finite projection collapse.
- operation_reachability_quotient.py — operation-enabled distinctions no longer addressable when perspectives are merged.

Original Dogram repository: the-static-collective/Dogram, commit 551b5f9df18f17ec69b452ddcdff01718e0ff771. The original project remains canonical; no upstream change or public operator promotion is implied.

The language grammar follows the project-owned 2026-09-17 Daily Slice formation witness, APERTURE — HOLD THE MEANINGS OPEN, in the-static-collective/the-daily-slice. The actual LEGIT-019 mathematical conjecture/proof engine is reused for Z3 bitvector equalities.

## Test 1 — identical according to WHICH viewpoint?

Dogram's documented seven-vertex graph specimens:

- G: a six-node cycle and one isolated vertex.
- H: a subdivided three-armed claw.

The utterance “Are these two graphs the same?” produces three candidate mathematical questions: (1) equal total path/walk-homomorphism counts, (2) equal branching star-homomorphism counts, and (3) isomorphism of full graph structure.

**Under linear paths:** identical. All finite path-length counts agree by an exact recurrence certificate; the first nine totals are 7, 12, 24, 48, 96, 192, 384, 768, 1536. This is not merely extrapolation from the displayed prefix.

**Under branching:** different. The star with one leaf and two leaves still collides (12 and 24), but the first three-leaf claw distinguishes G (48) from H (54). The original Dogram homomorphism counter independently enumerates all 7^4=2401 possible mappings of the claw's four vertices and reproduces that delta of six.

**Under full graph isomorphism:** also different; the degree multisets differ.

The canonical Dogram probe-poset confirms that the branching perspective strictly refines the path perspective for these carriers. Identical under an entire weaker test language need not imply identical under a richer test language. This was known graph mathematics already present in Dogram, not a new mathematical theorem.

## Test 2 — math needs a declared type

The phrase “Shift x right by one bit” admits at least two bitvector readings.

- Unsigned logical right shift.
- Signed arithmetic right shift.

A real external Z3 call produces a concrete counterexample to their equivalence:

    x                      0x8000000000000000
    unsigned logical       0x4000000000000000
    signed arithmetic      0xc000000000000000

Low-magnitude inputs can conceal the difference. The missing signedness is a genuine mathematical gap, not merely an imprecise translation. Context such as “Treat x as an unsigned 64-bit word” selects one compatible reading in a *new child receipt*; the original ambiguity remains accessible, and the context does not confer authority to assert human intent.

## Test 3 — different representations, genuinely equal mathematics

The phrase “Double x modulo 2^64” has distinct mathematical implementations: add x+x and shift x left by one.

Here, a real Z3 64-bit proof returns UNSAT for their inequality: both representations compute exactly the same mathematical function in the stated type. The trial verifies that LEGIT-019's prior generated proof packet already included this relationship. It never labels the theorem historically new.

This distinguishes two very different situations: different descriptions of the same typed operation, and underspecified words that conceal different mathematical operations.

## Test 4 — Dogram measures the actual cost of collapsing readings

The real upstream anti-collapse and operation-reachability kernels measure loss of possible future questions when a sense field is forcibly reduced to an unqualified single answer.

| Initial source | Alternative readings | Lost reading pairs |
| --- | ---: | ---: |
| Graph equivalence | 3 | 3 |
| Signed/unsigned shift | 2 | 1 |
| “The bank moved.” | 2 | 1 |

The bank example preserves riverbank relocation versus relocation of a financial institution. No statement about an actual riverbank or institution is established; these are readings, not factual claims.

Unknown input returns an explicit unresolved GAP without making up an equation or interpretation.

## Finite language comparison — and the honest strong baseline

Nine explicit source/context cases test all three graph meanings, both shift types, both bank readings, and both descriptions of doubling.

- APERTURE after declared context: 9 of 9 compatible readings.
- Strong conventional context-aware deterministic parser: ALSO 9 of 9.
- Weak, forced-first-reading ablation: 4 of 9 happen to agree.

This **does not prove APERTURE outperforms good existing language parsers**. The weak single-reading baseline illustrates precisely what is lost through premature collapse; it is not a fair optimized baseline. The cases and parser mapping are researcher-authored, not independent language challenge data.

No cognitive interpretation or real-world mathematical authority follows from passing these tests.

## Reproduction

From the MOTIF repository root, Python 3.11 and genuine z3-solver 4.16.0.0:

    python -m unittest discover -s experiments/legit020 -p 'test_*.py' -v
    python experiments/legit020/benchmark.py --emit

Dedicated GitHub Actions installs external Z3 and runs all source-hash, immutable-receipt, perspective, graph-isomorphism, homomorphism, signedness, known-equation and anti-collapse falsifiers. It archives the complete mathematical witness.

Repository files:

- aperture.py — immutable raw/context lineage, sparse 27-cell addresses, multiple interpretations, typed candidate translation, math-to-language gloss and explicit no-authority boundary.
- perspectives.py — real Dogram math + quotient/operation tests, independent graph witness, external Z3 signedness counterexample and reuse of actual previous LEGIT-019 proof.
- vendor_dogram/ — four pinned original Dogram modules plus their original source identities.
- benchmark.py — nine context tests and mathematical witnesses with strong parser comparison.
- test_aperture_mathalizing.py — adversarial verification and archived-result replay.
- generated/aperture_mathalizing_witness.json — saved, actual CI-executed mathematical and language witness.
- .github/workflows/legit020.yml — dedicated tests and receipt archive.

## Limits and follow-on experiment

**The demonstrated result:** a narrow deterministic, provenance-preserving language ⇄ mathematics bridge that can expose alternate formal readings, use Dogram to quantify lost distinctions, and bring mathematical counterexamples to bear on unresolved interpretations.

**Not demonstrated:** general natural-language comprehension; superiority over strong multi-parse semantic parsers; an original mathematical discovery; an improved external SyGuS competition score; or empirically compounded self-improvement.

The rigorous next experiment should have an optional small language model propose, but never *authorize*, different formal readings from independently authored unfamiliar sentences. Let Dogram select discriminating probes and Z3 check proposed mathematical constraints. Compare errors, abstentions, proof costs and downstream operation recovery against a strong conventional multi-parse language-to-logic baseline.

**An aperture is valuable when it makes a previously invisible distinction testable, not when it declares one perspective universally correct.**
