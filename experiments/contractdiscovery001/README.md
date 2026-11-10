# CONTRACT-DISCOVERY-001 — The missing mathematical crossing

**Status:** executable research experiment using existing MOTIF graph cartridges. Finite exact linear discovery, not proof of a novel mathematics, unrestricted semantic interpretation, arbitrary code generation, or independent scientific adjudication.

## Question MOTIF investigated

> Can I run controlled experiments on a cartridge's unfamiliar numerical outputs, discover a useful relationship **without being given its equation**, and build a typed adapter that reconstructs an otherwise unavailable output?

This experiment uses **actual** `NUNUMATHAL-001` `Graph`, `perform`, and `statistics` implementations. The readouts are anonymized as `u0...u4`; the learner is never supplied their field meanings, a target-label table, or the relationship among them. The experimental harness intentionally provides **five integer channels** and a **homogeneous linear** search grammar. Those are substantial prior assumptions.

## What happened

1. MOTIF enumerated locally permitted interventions on synthetic undirected graphs. Three additions/subdivisions dispatch through the existing `NUNUMATHAL` implementation; a fourth operation adds an edge to close a cycle or join components.
2. It executed eight sequential train probes, selecting unseen operation types before repeats. No prospective probe's outcome is inspected until it is executed. Four probes increased exact rational matrix rank, until the five-channel system had a **one-dimensional nullspace**.
3. Exact Gaussian elimination discovered the primitive relation **`u1 + u2 - u3 - u4 = 0`**. This is an encoded form of the familiar graph identity `Δcycle_rank = Δedges − Δvertices + Δcomponents`; the relationship exists in the upstream module already, and the experiment rediscovers it from observations. **It is not historically novel mathematics.**
4. Fifteen separate validation trials checked the frozen relation, followed by **35 test** and **48 OOD** trials. OOD includes **removing graph edges and isolated vertices**, neither of which is allowed in the train intervention set.
5. The learned equation was used to create a **new executable missing-port adapter**. Four of five channels can be reconstructed from the other four, exactly **140/140** held-out test attempts and **192/192** OOD attempts. The fifth channel has zero coefficient, so MOTIF correctly refuses to manufacture it.
6. A generated child replays the discovered training/validation contract, pins actual repository source bytes, launches in another Python interpreter, fills a held-out missing port, and compares against an independently implemented spanning-forest-based graph measurement. SHA pins detect changes, not upstream authenticity; a subprocess is **not a security sandbox**.

## Important negative controls

- Restricting probes to only the original three NUNUMATHAL operations leaves a larger nullspace. MOTIF returns **`HOLD_UNIDENTIFIABLE_CONTRACT`**, not a guessed relationship.
- Classical exhaustive enumeration of integer coefficient vectors in `{-1,0,1}^5` finds the **same relation**. There is no claimed advantage over ordinary classical linear algebra.
- Changing a single type-correct channel value triggers a detectable violation on **140/175** attacks. The other **35/175** change a channel not constrained by the inferred law, so they go unnoticed.
- A **coordinated corruption of two measured channels** can preserve the equation even though both values are wrong. Without independent measurement, the contract cannot establish absolute correctness.
- Different rewrite mechanisms (attach leaf versus subdivide edge) have matching numerical deltas: the relation does not identify their mechanisms.
- An adversarial validation contradiction refuses promotion. Parent build and child execution revalidate coefficients instead of trusting an injected contract object.
- A `FIR-001` local finite observation may receive `F_LOCAL`; the general, unlimited claim remains **I**.

This is a **meaningful first demonstration of discovered executable numerical contracts and a new port adapter** inside a very narrow, known graph domain. It does not show MOTIF discovering arbitrary non-linear semantics, external source integrity, or general real-world skill acquisition.

## Reproduce

Run from a full checkout of the stacked experimental branch (Python 3.10+, standard library):

```sh
cd experiments/contractdiscovery001
python -m unittest -v test_contractdiscovery.py
python contractdiscovery.py
python benchmark.py
```

The executable test suite has **43 tests** covering real prior-cartridge calls, exact arithmetic, insufficiency holds, duplicate split refusal, falsified validation, independent held-out calculations, OOD operations, type-correct semantic attacks, a coordinated-undetectable attack, FIR admission, generated child, pins, and hostile tampering.

## What the machine ought to ask next

**Can the contract learner escape fixed linear equations and five declared integer channels, discover higher-order or conditional relationships, and distinguish shared source bugs from independently verified behavioral evidence?**

Stacked parent: `experiment/semantic-adapter-001-20261109` / draft PR #213. This branch should remain draft pending review of experimental dependencies and source integrity; no merges or deployments are performed by this experiment.
