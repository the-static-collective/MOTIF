# MOTIF LEGIT-021 — THE APERTURE INVENTOR

**Status: research HOLD. The actual experiment is executable and its mathematical receipts are inspectable. Nothing automatically merges, deploys or claims historically novel mathematics.**

## The user-origin hypothesis

Could MOTIF notice that its existing mathematical perspectives cannot distinguish competing possible worlds, then **invent a better question** instead of guessing an answer?

This experiment connects the actual LEGIT-020 language APERTURE and pinned Dogram graph mathematics to a bounded mathematical question generator. It synthesizes smaller SOURCE graphs whose homomorphism counts become new questions about larger target graphs. A second channel uses genuine external Z3 to produce minimal distinguishing inputs for bitvector ambiguity, or formally prove that no such numeric input exists.

All challenge families and mathematical grammars remain researcher-authored. The experimental outcome is valid within those declared boundaries, not proof of open-ended original mathematics or general language understanding.

## Experiment 1 — source graph observation invention

The generic generator enumerates all connected, unlabeled, simple source graphs with at most four vertices. It removes isomorphic duplicates, producing **10** admissible graph patterns. It asks the actual pinned Dogram homomorphism counter how often each source graph maps into each candidate target graph, stopping at the first discriminator. It does NOT contain a manually written order of triangle, claw, and square candidate labels.

A separately implemented exhaustive classical homomorphism enumerator checks each chosen result and independently establishes minimality **among the ten source patterns**.

**Calibration A:** C6 versus C3+C3. Both are six-vertex, degree-two regular graphs, so all finite path-homomorphism counts agree by an exact recurrence. The first three generated source probes cannot distinguish them; the fourth automatically generated pattern is a triangle:

    hom(triangle, C6)        = 0
    hom(triangle, C3+C3)     = 12

**Calibration B:** Dogram's actual C6+isolated-node versus subdivided-three-arm-claw mathematical example. Again every finite path test collides. The first discriminator is the fifth generated source: a three-leaf star, with homomorphism counts **48 versus 54**. This is original Dogram mathematical work reused in a novel executable questioning workflow, not a new theorem.

## Experiment 2 — measured transfer to other graph questions

Two previously synthesized source graphs (triangle and claw) were made available as inherited experimental questions on three different researcher-authored graph pairs. The same entire graph-source grammar and independent exhaustive correctness oracle were available to both variants.

| New graph pair | From-scratch proposed questions | With inherited questions | Exact minimum source |
| --- | ---: | ---: | --- |
| C7 vs C3+C4 | 4 | **1** | Triangle |
| C8 vs C3+C5 | 4 | **1** | Triangle |
| C8 vs C4+C4 | 8 | 8 | Four-cycle |

The third pair is important: neither old probe helps, and the engine must invent a four-cycle observation. Every emitted separator matches an independently computed classical exact minimum. Caching known useful mathematical questions is useful, but it is also standard classical practice; these results do not establish independently verified compounding discovery productivity.

## Experiment 3 — an adaptive math-question decision tree

Consider three eight-vertex possible worlds: C8, C3+C5, and C4+C4. All are degree-two regular graphs and therefore indistinguishable by **every finite path count**.

The inventor synthesizes source-graph questions and builds a small active decision tree from the numerical responses:

    How many triangle homomorphisms?
      6  -> the world is C3+C5
      0  -> how many four-cycle homomorphisms?
              48 -> C8
              64 -> C4+C4

It uses **1, 2, and 2 questions**, respectively. Under the explicitly assumed uniform distribution over these three known worlds, that is **5/3 questions on average**, instead of running both source tests unconditionally (2 per world).

An independently implemented conventional exhaustive decision-tree dynamic program evaluates the same family and determines that **5/3 is the exact optimum**. MOTIF's bounded greedy question selector TIES that strong classical optimum; no superiority is claimed.

The actual pinned Dogram probe-partition-refinement kernel verifies that the generated tests distinguish the declared graph-state partitions.

## Experiment 4 — an entirely invisible distinction becomes visible by enlarging the aperture

The hardest case starts with two genuinely different graph carriers:

- One ten-vertex cycle, C10 — **one connected component**.
- Two disjoint five-vertex cycles, C5+C5 — **two connected components**.

Both are degree-two regular, so every finite path count is identical. More strongly, **all ten admissible graph-source probes of at most four vertices yield the same result** on both graphs.

The proper outcome under that source language is HOLD: the worlds are not distinguishable **by these observations**. It does not imply that the graphs are identical.

The program performs one explicitly allowed, bounded expressivity step, raising the maximum source graph to five vertices. The grammar now has **31** connected unlabeled types (21 new patterns). It generically enumerates the new structures rather than inserting a handwritten five-cycle source. The first successful source question is a **five-cycle**:

    hom(C5, C10)        = 0
    hom(C5, C5+C5)      = 20

The independent exhaustive classical oracle confirms the count and the minimality of this separating source **within the 31-pattern grammar**. The previous question language was blind; the larger language can observe a genuine difference.

This is the experiment's central executable result:

    "No question I know separates them"
          does NOT entail
    "They are the same."

The limit of five vertices was supplied by the research design; this is a bounded source-grammar expansion, not the unconstrained invention of a new universal mathematical operator.

## Experiment 5 — mathematical typed-language probing and formal impossibility

The original LEGIT-020 APERTURE preserves two possible readings of the utterance "Shift x right by one bit": signed arithmetic versus unsigned logical shift.

External Z3 verifies the smallest unsigned 64-bit word differentiating the operations and separately proves there is no smaller unsigned witness:

    x                            0x8000000000000000
    unsigned logical shift       0x4000000000000000
    signed arithmetic shift      0xc000000000000000

For "Double x modulo 2^64", it instead verifies the known LEGIT-019 equality of adding x+x and shifting x left by one. The inequivalence solver returns UNSAT over **all 64-bit words**: no numeric input can distinguish those two equivalent mathematical operations.

A numeric witness never establishes which interpretation a human actually meant. No matching result grants semantic or evidentiary authority.

## Source provenance, controls and reproduction

The experiment reuses the source-exact real Dogram modules introduced in LEGIT-020 and the original 2026-09-17 Static Collective APERTURE formation witness. Dogram remains canonical. The source graph homomorphism counter, probe-refinement module and LEGIT-019 Z3 interface are actually executed.

The new implementation files:

- graph_inventor.py — connected source-graph enumeration, graph isomorphism canonicalization, Dogram observation construction, independent exact classical homomorphism and minimality checking, adaptive decision-tree search and bounded 4→5 source-language expansion.
- math_apertures.py — genuine LEGIT-020 APERTURE, Dogram mathematical partitions, minimal external Z3 signedness witness and formal no-separation proof for equivalent 64-bit doubling.
- benchmark.py — two calibration problems, three new comparison problems, a three-world adaptive decision tree, a bounded new-language exploration and complete mathematical receipts.
- test_inventor.py — adversarial tests for source generation, mathematical proof, classical optimality, exact source fingerprints, unresolved worlds, expansion and source/intent boundaries.
- generated/aperture_inventor_report.json — the actual CI-executed proof and experimental result.
- GitHub Actions legit021.yml — installs real external Z3, executes everything, runs tests and archives the mathematical receipts.

Run from MOTIF repository root with Python 3.11:

    python -m pip install z3-solver==4.16.0.0
    python -m unittest discover -s experiments/legit021 -p 'test_*.py' -v
    python experiments/legit021/benchmark.py --emit

The second command saves a complete JSON report to /tmp/motif-legit021-aperture-inventor.json.

**Boundaries:** These are finite, assistant-authored graph and bitvector tasks. Minimum means only minimum within the declared source-graph grammar. The adaptive tree is exactly tied with an established classical optimum. Reuse of earlier successful probes is not proof of recursive self-improvement. No historical mathematical originality, external scientific adoption, unrestricted new capability synthesis, or general speech understanding is established.

Research verdict:

    HOLD_RESEARCH_ONLY_BOUNDED_APERTURE_DISCOVERY_NOT_NEW_MATH

The next serious test should come from independent challenge authors with an unknown observation-language gap, a precommitted budget and a strong classical model-refinement baseline. Make new mathematical measurements compete to enable previously impossible downstream problem solving.

**The aperture invents a better question, not a new truth about the underlying world.**
