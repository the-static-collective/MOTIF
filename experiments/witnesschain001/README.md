# MOTIF WITNESS-CHAIN-001 — Can the witness's witness be questioned?

**Status:** executable, synthetic mathematical experiment; proposed in a draft PR stacked on `PROVENANCE-PROBE-001` → `DECODER-INTEGRITY-001` → `CONTEXT-GATE-001` → `SELF-MIRROR-001` → `MATHAL-001` → `FIR-001`.

This is **not a real-world identity verification system, proof of sensor correctness, new mathematics, or autonomous agent**. No tool, human, or external device is queried by this code. A fixture's truth is a **declared assumption**, not a validated credential.

## Research question and result

The previous `PROVENANCE-PROBE-001` showed that two fallible witnesses can remain observationally indistinguishable under joint polarity inversion, and that a synthetic trusted truth anchor can disambiguate them. But who verifies the anchor?

Here the previous trusted `Observation.anchor` is *reinterpreted as a third fallible witness*, not as actual truth. The fixed toy family comprises **eight polarity hypotheses for three noisy channels**. Each channel has a known, assumed conditional accuracy (`primary=.85`, `audit=.90`, `anchor=.92`); latent truths are independent and balanced. This makes a mathematical impossibility explicit:

For every three-reading observation `x` and hypothesis `h`, `P(x | h) = P(x | complement(h))` when the latent truth is equally likely amber or blue. The global inversion simply exchanges the two summands in the marginalized likelihood. Consequently **any number of ungrounded three-witness reports cannot identify absolute polarity**. This symmetry is tested exhaustively for all eight hypotheses × all observation patterns, including missing-channel cases.

**Query-relative stopping:** With sufficient triplets, a *relative* question, such as whether primary and audit tend to have the same polarity, can receive an `I_RELATIVE_MODEL_ONLY` estimate while *absolute* polarity remains `HOLD_GLOBAL_FLIP_SYMMETRY`. A query needn't wait for an ultimate reference when the answer it seeks is invariant to that reference.

**Recursive challenges:** An external-to-the-posterior synthetic `TruthReceipt` can conditionally resolve absolute polarity. However, its provenance remains an assumption. `challenge_reference` removes the attestation from inference, preserves before-and-after states with a reasoned receipt, and restores the hold if no reference remains. It does **not** erase the original report. A tampered reference can make the posterior confidently wrong.

## Executable controls

- `Witness` and `Event` represent an explicit provenance DAG with parent links and asserted roots. Cycles, missing parents, conflicting forwarded copies, overlapping roots across channels, multiple channel roots, duplicate event IDs, and reused roots across events are held or rejected. Distinct declared roots **are not proof of independence**; hidden correlation with forged disjoint roots is a negative control. An asserted root is the origin of a *datum*, not a physical sensor identity.
- `State` is an immutable Bayesian evidence ledger. Replays cannot amplify evidence. It computes posterior probabilities over eight explicit candidate mechanisms and preserves reference assumptions separately from observed readings.
- `from_probe_observation` integrates existing `PROVENANCE-PROBE-001` data while **downgrading** its old trusted fixture anchor to a regular fallible instrument. It deliberately does not infer a `TruthReceipt` from the prior `fixture_anchor_attested` flag.
- `expected_gain` compares classical information gain of a new ungrounded triplet versus **checking the truth of an already observed synthetic event**; `propose` enforces inquiry permissions and budget. `investigate` stops when the stated *question*, not every conceivable future question, is sufficiently answered. All inquiries remain ideas, with zero real-world authority.
- `fir_receipt` makes only a precisely scoped finite ledger count `F_LOCAL`, through the existing `FIR-001` and `MATHAL-001` code. The leading explanatory model stays `I`, even at posterior probability 1 under floating-point rounding.

## Reproducible benchmark

The fixed benchmark covers **8 model regimes × 25 deterministic seeds = 200 synthetic worlds**. In each world, the model sees 100 initial triplets, then compares the same declared additional cost (**16 units**):

| Protocol | Additional observations | Extra cost | Top-1 mechanism identification |
| --- | --- | ---: | ---: |
| Ungrounded | 16 more triplets (cost 1 each) | 16 | **100/200 (50%) forced top-1**, all held for absolute claims |
| Assumed reference | Ground truth of 4 previously observed events (cost 4 each) | 16 | **200/200 (100%)** under the correct fixture assumption |
| Tampered reference | 4 deliberately inverted synthetic truth receipts | 16 | **0/200 (0%)**, confidently wrong |

The deliberately simple problem, fixed known noise parameters, large preliminary sample, and exact correctly specified hypothesis family make the reference result especially favorable. This is **not** evidence that 4 real-world corroborations suffice, and none of these synthetic reference receipts has independently verified authenticity. These scores are calculated from the source benchmark, not a real sensor. All 200 worlds answer the *relative* primary/audit alignment question on this fixture without reference, conditional on the model family.

Important limits: stationarity, truth balance, event independence, unverified origin strings, hidden common causes, prior/model misspecification, and unauthenticated fixture receipts. A spoofed root can evade the declared-ancestry check, and independently named channels can still share hidden errors. Posterior concentration is not a guarantee of correctness. A real deployment would require an authorization boundary and externally verified provenance, neither of which exists here.

## Reproduce

Python 3.10+, standard library only:

```sh
cd experiments/witnesschain001
python -m unittest -v test_witnesschain.py
python witnesschain.py
python benchmark.py
```

All sibling stacked experiments are left unchanged. The new workflow runs the entire mathematical regression suite before this experiment.

## Source ancestry

Owner-authored *nunuMATH: First Course in FIR Systems* (F/I/R distinctions, reopening, query-relative receipts, hostile controls), *nuMATHELOLOGY 2nd ed.* (typed worlds and lenses), MOTIF's `014W` witness-of-witnesses model, `010` classical information-gain scientist, and prior `PROVENANCE-PROBE-001` synthetic anchor limitation. This is a falsifiable classical construction, not a claim to invent a new general reasoning algorithm.
