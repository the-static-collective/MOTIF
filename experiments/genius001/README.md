# MOTIF-GENIUS-001 — ARCHITECTURE OF DISCOVERY

**Status: executable exploratory prototype / RESEARCH HOLD.** Experimental branch stacked on LEGIT-029, not merged into `main`. No historical cognition has been reverse-engineered, no novel mathematical result has been established, and no learning or recursive self-improvement is claimed.

## Starting trio: Einstein · Ramanujan · Leonardo da Vinci

These three are not "genius personalities" to simulate. They motivate **different candidate operations** that can be defined, falsified, measured and transferred.

| Historical research record | Candidate operation | Executable miniature | Critical distinction |
| --- | --- | --- | --- |
| Einstein's 1905 operational definition of distant clock synchronization | **OPERATIONAL_REDEFINITION:** expose missing measurement assumptions | Given round-trip timestamps, estimate a clock offset *conditional on equal outbound/return times*, otherwise HOLD | This is a reconstructed exercise, **not** evidence of the actual chronology of Einstein's private discovery |
| Ramanujan's partition-number congruences | **CONJECTURE_THEN_FALSIFY:** recognize numerical regularity, then separate observed evidence from proof | Calculate partition numbers; mine congruence candidates on one index interval; test on an untouched later interval | Finite verification of known congruences is **not** an infinite proof or new mathematics |
| Leonardo's notebooks of observation, diagrams and cross-domain inquiry | **STRUCTURAL_ANALOGY:** externalize a relational model and validate transfer | Transfer a small directed-network minimum-cut witness between two differently named networks only if a capacity-preserving bijection is verified | Minimum-cut theory is **a modern illustrative algorithm**, **not** something attributed to Leonardo |

The three prompts are intentionally plural. New historical case studies and domain strategies can be added without redefining this as a fixed "three kinds of genius" taxonomy.

### Sources / provenance (not psychological reconstructions)

- Einstein, **On the Electrodynamics of Moving Bodies** (1905), §1, on distant clock definitions: https://www.physics.umd.edu/courses/Phys371/AnlageFall20/Einstein_1905_relativity.pdf
- Stanford Encyclopedia of Philosophy, **Conventionality of Simultaneity**: https://plato.stanford.edu/entries/spacetime-convensimul/
- John D. Norton, **Discovering the Relativity of Simultaneity**: https://d-scholarship.pitt.edu/2674/1/Simultaneity_Einstein.pdf — cautions against treating Einstein's final presentation as a verified step-by-step discovery diary.
- MacTutor / University of St Andrews, **Srinivasa Ramanujan**: https://mathshistory.st-andrews.ac.uk/Biographies/Ramanujan/ — records partition discoveries and distinguishes true and false claims.
- V&A, **Leonardo da Vinci's notebooks**: https://www.vam.ac.uk/articles/leonardo-da-vincis-notebooks
- Metropolitan Museum of Art, **Leonardo da Vinci, Master Draftsman**: https://www.metmuseum.org/exhibitions/listings/2003/leonardo-da-vinci

## Execute the bounded trial

From the repository root:

```sh
python -m unittest discover -s experiments/genius001 -p 'test_genius.py' -v
```

Pure Python standard library; no credentials, GPU, or network calls. Four tests cover assumption refusal, held-out congruence checks, structural transfer with an independent finite oracle, and unknown-problem refusal.

### Proof-carrying / caveat-carrying return

Each operator returns a typed status, a result, the assumption or mapping on which the result depends, and a *next useful research question*. In particular:

- **CONDITIONAL:** arithmetic is correct if the signal symmetry assumption is independently established.
- **FINITE_TEST_PASS_NOT_PROOF:** the conjecture survived held-out finite checks, but an infinite theorem was not proven.
- **EXACT_FINITE:** an exhaustive small-graph calculation and a separately recomputed mapped target agree.
- **HOLD:** available observations/typing do not justify an answer.

No "genius score" or attribution of a historical researcher's reasoning is generated.

## First small controls

- Clock example: naive `observed_b - send_a` confounds clock offset with signal transit; midpoint conditional estimate removes this confound *under explicit path symmetry*. If symmetry is unestablished, abstain.
- Partition numbers: train on indices 0..109, hold out indices 110..220; p(5k+4) divisible by 5, p(7k+5) divisible by 7, and p(11k+6) divisible by 11 survive this finite test. The false p(5k+1) pattern is not accepted.
- Relabeled capacity network: "pick smallest individual edge" guesses 2, but the exact minimum directed cut costs 5. Transfer to a second network is admitted only after every vertex, edge and capacity is verified. Mutating one capacity correctly blocks the analogy.

These are **engineer-authored educational fixtures**, not independently authored blind challenges. No performance improvement can be inferred from passing a deliberately constructed example.

## Real research frontier (NOT YET DONE)

1. **Historical discovery casebook:** cite dated primary notebooks/papers, reconstruct what was demonstrably available *before* each result, and mark disputed chronology. Compare unsuccessful contemporary attempts; avoid hindsight narratives.
2. **Operator grammar:** allow typed compositions such as `OBSERVE → REFRAME → CONJECTURE → FALSIFY → TRANSFER`, not fixed personality presets. Require source, proof, counterexample, and failure-mode receipts.
3. **Cross-domain frozen evaluation:** learn/select candidate operator sequences using training cases only; freeze code, candidate set and policies before independently authored problems; compare identical compute and evidence budgets with strong classical portfolios and unmodified MOTIF.
4. **Failure audit:** record seductive but invalid analogies, selection effects, false discoveries, conditional models mistaken for measurements, and experimenter leakage.
5. **True improvement criterion:** hold-out accuracy and verification cost across previously unseen domains, plus independent audits. A successful historical analogy alone does not demonstrate learned meta-reasoning.

**Frontier question:** can source-grounded discovery operations, rather than historical hero narratives, increase MOTIF's rate of *independently verified* insights outside their training domains?
