# MOTIF-GEOM-003 — Geometric Laws as Inventable Cartridges

**Stage:** isolated, standard-library-only, synthetic research. **Scientific interpretation:** typed program synthesis of **known Euclidean geometry**, not a discovery of a new mathematical theorem, geometric consciousness, privileged sacred-geometry claim, or permission to take actions.

## The question

Can MOTIF construct **a reusable method it was not handed as a program**, by combining primitive geometric operations, and then use the first two learned methods to make a third method available? Could an independently executable witness distinguish a geometric conjecture from a correct construction without treating a few matching demonstrations as universal proof?

- GEOM-001: execute a known Flower-of-Life lattice construction.
- GEOM-002: infer a finite lattice under an explicit near-equal-length prior from noisy unknown-position/rotation points.
- **GEOM-003:** synthesize typed geometric construction programs from examples, reuse them compositionally, check rational invariants, and preserve a HOLD-only cartridge. The demos also bridge **observed inlier points** from GEOM-002, never inferred/missing holes.

## Primitive operator grammar

The synthesizer is given only Euclidean point/line operations, as a fixed, bounded **architectural prior**:

| Operator | Input | Output |
|---|---|---|
| `line` | 2 points | a line |
| `midpoint` | 2 points | a point |
| `perpendicular` | line + point | a line |
| `intersection` | 2 lines | a point or undefined |

There are three input roles A, B, C. The grammar enumerates **all three base segment lines**, **their three pairwise midpoints**, **18 perpendicular lines through those roles**, and **210 line-line intersections**. Each candidate is replayed on all eight teacher triangles. The teacher supplies **coordinates of target points only** using a *separate direct algebraic formula*, never the desired recipe. A matching candidate is then selected by expression size and lexical tie break. No neural training, LLM, geometric label search, or free-form code invention is performed.

**First synthesis:** two selected constructions:

- **Circumcenter** — intersection of independently reconstructed perpendicular bisectors.
- **Orthocenter** — intersection of independently constructed altitudes.

**Second synthesis:** expose those two *whole programs* as reusable point-constructors, and enumerate all ten possible pair-midpoint compositions over {A, B, C, circumcenter, orthocenter}. One matches the teacher's **nine-point-circle center**: the midpoint of the first two learned programs. No dedicated nine-point-center recipe is in the synthesis grammar. This is an actual composed program, albeit a classical and well-known geometric construction.

These are three named synthetic goals. GEOM-003 does **not** autonomously discover the value of an arbitrary new goal, invent a novel theorem, invent the primitive grammar, derive its own unknown physical metric, or demonstrate open-ended search.

## Why this is more than a drawing

The raw triangle A,B,C is unchanged. Synthesized methods produce *proposed derived points*, with expression trees, exact-instance geometric checks, and a JSON evidence checksum. Methods remain `HOLD` and never become admitted capabilities automatically. A candidate program can be applied repeatedly to different triangles without exposing the examples it learned from.

### Strong mathematical control

The primary baseline computes O,H,N directly from a two-by-two linear solve and the standard Euler vector relation, on the **same 40 test triangles**, with exact rational arithmetic. Both the synthesized programs and direct classical solver have **zero errors** in the deterministic development fixtures. The direct solver has a more direct expression and no training/search overhead; this experiment is about method composition and provenance, **not state-of-the-art numerical accuracy or complexity**.

### What is proven, and what is not

The symbolic module `proof.py` establishes the following *conditional*, universal vector identities under exact rational coefficients:

1. If O is the circumcenter, then `H = A+B+C-2O` lies at the intersection of the altitudes (by the circumcenter equidistance identity).
2. For `N=(O+H)/2=(A+B+C-O)/2` and midpoint `M_AB=(A+B)/2`, `N-M_AB=(C-O)/2`, with symmetric equivalents for BC and CA.
3. Therefore the three side midpoints are equidistant from N, at radius `R/2`, **provided** `|A-O|=|B-O|=|C-O|=R`.

The executable symbolic certificate explicitly checks vector coefficient equalities. `certificates()` separately checks 4 families of geometric facts on each exact, rational test instance. The symbolic identities are not a general proof that *every possible program output* is a circumcenter. In particular, finite test cases do not establish unrestricted generalization.

## Executed development test (not preregistered/blind)

From this directory:

```sh
python -m unittest -v test_synthesis.py
python benchmark.py
python demo.py
```

- **8 synthetic teacher triangles**; **40 disjoint synthetic holdout triangles**; generator seed fixed in `benchmark.py`.
- **210** initial candidates; **10** next-stage compositions.
- All three derived positions are exact on **40/40** heldout triangles. The direct classical formula is also exact on **40/40**.
- No invariant failures. The method search returns **HOLD** if `midpoint` or `perpendicular` is removed in this restricted grammar, for duplicate or insufficient teachers, for collinear or duplicated triangle vertices, or for unsupported metrics.
- A separate GEOM-002 synthetic crossing chooses only three *observed inlier* points (never proposed holes), converts their coordinate snapshots to finite rationals, and independently applies the geometric programs. Both source and derived predictions retain **HOLD**.
- Tests include corrupt JSON and altered program-code detection. SHA-256 integrity is **not** identity, source authenticity, or general proof.

These fixtures were developed alongside the algorithm. Real-world performance, noisy geometric model identification, out-of-distribution transfer, and unknown-goal invention remain unverified.

## Falsifiers / next experiment

- A selected method fails on independently generated unseen triangles, nontrivial rational slopes, right or obtuse triangles, or has undefined operations.
- A claimed proof does not follow from recorded premises, or a result is admitted to observed state.
- A better generic enumerative solver finds equally good or shorter methods (expected: substantial classical prior art exists).
- Under alternate metrics, dimensionalities, malformed coordinates, missing/noisy GEOM-002 witnesses, the crossing should **HOLD** until separately verified.

**GEOM-004 proposal:** permit candidate constructors to *invent a new intermediate subroutine* when no bounded grammar program solves a withheld geometric task, use counterexample-guided inductive synthesis (CEGIS), and compare against classical enumerative synthesizers and SMT-based geometry methods under identical budgets, with frozen out-of-family controls and honest abstention.

## Artifacts

- `synthesis.py`: exact rational geometric DSL + finite typed enumeration and inference.
- `proof.py`: compact, self-contained symbolic conditional identities.
- `cartridge.py`: portable, reproducible, checksum-bound **HOLD** program records.
- `benchmark.py`: fixed development generator, direct formula control and ablations.
- `test_synthesis.py`: eleven unit tests including GEOM-002 read-only crossing.
- `demo.py`: outputs the exact example points, accepted *candidate methods*, and an SVG of the triangle and nine-point circle.
