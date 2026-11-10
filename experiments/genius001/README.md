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


## R/R extension — Rasputin × Mister Rogers: social intelligence is not identical to moral intelligence

Two **historical prompts**, not reconstructed personalities and not proven moral opposites:

- **Grigori Rasputin**: access to authority through an intensely trusted personal connection, coupled with enduring public reputation, rumor, fear, and disputed narratives. Historical records support proximity to Alexandra and spiritual consolation, but **do not establish that every rumor or manipulation allegation was true**. The analysis question is how vulnerability, exclusive access, perceived care, authority, and outsiders' impressions interact. Background: Smithsonian Magazine, *What Really Happened During the Murder of Rasputin?* https://www.smithsonianmag.com/history/what-really-happened-during-murder-rasputin-russia-mad-monk-180961572/ ; historical reassessment: Orlando Figes, *A Very Close Friend of the Family* https://www.nybooks.com/articles/2016/12/08/rasputin-close-friend-family/
- **Fred Rogers**: outwardly simple, exceptionally deliberate attention to children's feelings, self-regulation, autonomy and trust, with an observable instance of persuasive communication in his 1969 Senate testimony. The evidence is primary recording/transcript, not an inference that his motives can be read mechanically. Primary transcript: https://current.org/1969/05/i-give-an-expression-of-care-every-day-to-each-child/ ; archives: https://www.fredrogersinstitute.org/archive ; institutional values: https://www.fredrogersinstitute.org/about-the-fred-rogers-institute

### Hypothesis / distinguishing variable

**Social effectiveness** = can an actor attune to another person's needs and change a relationship or outcome?

That question is distinct from **longitudinal agency** = can the other person still disagree, check claims, draw on relationships beyond the actor, or leave without inappropriate penalty? Both relief and a narrowing of agency can occur in the same relationship. Neither the person's charisma nor a favorable immediate reaction establishes benefit.

The paired aperture is a **test for observable dependence and autonomy, not a classifier of good versus evil, diagnostic tool, persuasion playbook or predictive social-science model.** Historical evidence can support observations; it cannot justify invented mental states. The simulation below is explicitly modern and fictional, not a claim that Rasputin or Rogers performed the listed actions.

### Executable slice

`social.py` defines `SocialObservation` with optional and source-bound observations; no evidence is treated as UNKNOWN rather than defaulting to a virtue or vice. The assessment returns:

- Reported immediate comfort, as a **separate channel**.
- Positive indicators of agency: acknowledged need, permission to disagree and refuse, independent verification, other support permitted.
- Possible concentration/dependency indicators: exclusivity demands, inability to refuse without penalty, discouraging external checks.
- An explicit provisional status and next useful question, plus evidence still missing.
- A chronological inspection in which later problematic episodes cannot be masked by earlier kindness.

The **adversarial synthetic pair** has *the same immediate comfort* in both scenarios. A relief-only predictor labels both SAFE; the evidence lens marks autonomy-supporting cues in one and dependency/control risk worth investigating in the other. Another case with only comfort returns HOLD. A trajectory test reports a late risk rather than averaging it away.

The dependency-risk flag is a request to investigate **observable behavior**, not an assertion of harmful intention or a verdict about real people. No behavioral measurement scales have been validated. The benchmark is engineer-authored and deliberately minimal.

Run both the original and R/R tests:

```sh
python -m unittest discover -s experiments/genius001 -p 'test_*.py' -v
```

### Next frontier

Model **relational transformation graphs** over time, with explicit **needs → response → perceived safety → options → trust/dependence** edges, separating witnesses and hearsay. Compare against strong social-science baselines such as autonomy-supportive communication, attachment research, coercive control frameworks, epistemic trust and social network dynamics; do not treat any one figure as a verified model of a psychological construct.

A falsifiable research question: **Can MOTIF identify when influence expands the other party's independent options versus when influence concentrates choices, on externally authored, ethically reviewed scenarios, without learning to reward manipulation or inventing motives?**
