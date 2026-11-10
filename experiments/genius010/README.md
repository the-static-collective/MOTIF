# MOTIF-GENIUS-010 — THREE THREADS, ONE BRIDGE

**RESEARCH HOLD — unmerged, source-protected experimental branch based on GENIUS-009.** This is the first concrete attempt to test whether MOTIF can *discover and justify a convergence* between three apparently unrelated threads, rather than merely notice a shared word or invent an elegant ending. All agents, reports, interventions, source IDs, outcomes, mechanism definitions and evaluator truth are engineered synthetic artifacts. No human participant, physical sensor, account or MCP tool is contacted.

## Two kinds of convergence must not be conflated

**Povenmire-style storytelling:** three plots can maintain independent local logic before sharing a payoff. Acaster-style callbacks can alter the audience's understanding of earlier beats. GENIUS-009 demonstrated that those interpretations can change without editing the earlier witnesses.

**Empirical research:** three independent investigations can seem to point toward a common explanation. The fact that they use the same phrase, have correlated observations, or share a copied source is *not* enough to establish an explanatory bridge. We must compare proposed explanations with distinct, independently generated evidence—and keep the inference conditional on the design assumptions.

This study combines them: only **after** the three investigations support the same predeclared hypothesis under an engineered intervention test may a later source-bound interpretation link their prior records. The bridge interpretation is explicitly later testimony, not a retroactive revision to their original claims.

## Public research question and case structure

Three fictional investigative strands with different surface stories:

1. `glasshouse` — an unexplained greenhouse timing anomaly.
2. `broadcast` — an unexplained radio schedule anomaly.
3. `parcel` — an unexplained courier handoff anomaly.

Three candidate bridges are supplied *before* the trial (the program does **not** invent new mechanism names):

- `blue_ribbon` — the frequent **lexical motif** shared by the reports. It is a deliberately enticing decoy.
- `hinge_timing` — a proposed underlying coordination switch. In some simulator regimes, switching it influences success in all three strands.
- `sunset_mark` — a possible partial bridge, sometimes relevant to only two strands.

A purely lexical approach always selects `blue_ribbon` because it has the largest source-word overlap score. The stronger analysis evaluates **distinct observations and intervention contrasts**, never equating a recurring name with a real shared cause.

## Classical statistical shoulders of giants

Judea Pearl (1995), *A Causal Calculus for Statistical Research*, Proceedings of Machine Learning Research, https://proceedings.mlr.press/r0/pearl95a.html , sharply distinguishes **observational conditioning** from **intervention**. Co-occurrence can arise from an unmeasured common cause.

Classical **Fisher two-sided exact contingency tests** use fixed arm sizes and a conditional hypergeometric distribution. **Bonferroni** correction controls the overall chance of one or more false rejections among a predeclared family of tests at or below 5% *under the individual valid null assumptions*. It does not authenticate the experiment or establish the explanation is true.

The current study preregisters exactly **3 candidate bridges × 3 threads = 9** two-sided statistical comparisons, each thresholded at `0.05/9`, together with a predeclared minimum positive observed risk difference of **0.25**. A bridge is *conditionally supported* only if all three threads pass, their source-origin roots are unique, their evidence is public, and the synthetic randomized-design attestation is present. A single marginal false alarm is possible; a negative or inconclusive strand blocks the full bridge.

**Causal limitation:** this is not a statistical causal-identification theorem about an arbitrary real mechanism. The generator actually flips synthetic assignments and produces binary outcomes; the test observes the resulting aggregate contrast, not the internal causal logic. If assignment, source integrity or outcome measurement were compromised, a small p-value would not settle causation. The `randomization_attested` boolean is merely a supplied fixture flag, **not** independently verified randomization.

## Seven falsification regimes

| Regime | Hidden engineered world | What a defensible result should do |
| --- | --- | --- |
| CONVERGENCE | One positive hypothesis influences all three streams | Identify a *conditional* bridge, not a demonstrated real-world cause. |
| HIDDEN_MOTIF | Same genuine synthetic bridge, despite irrelevant lexical overlap | Reject the tempting shared-word explanation and find the source-supported candidate. |
| NULL | No hypothesized switch influences all three | HOLD rather than manufacture a common cause. |
| CONFOUNDED | A common latent Z makes survey variables correlate, with no matching effect under randomized assignment | Distinguish 'seeing together' from 'doing'. |
| PARTIAL | At most two streams support a hypothesis | Preserve the dissenting third strand; do not force convergence. |
| REVERSED | A candidate helps two strands but harms the third | Reject a uniformly positive three-stream story, without denying heterogeneous effects. |
| ECHO_SOURCE | All three apparent sources reuse source-root identifiers | HOLD copied evidence rather than treating it as three independent witnesses. |

Each candidate/thread has **64 observational** and **48 randomized simulated observations** (24 per assignment) before prespecified, outcome-independent withholding. The source ledger only receives shareable items, strips private notes, rejects replayed event IDs, and rejects repeated origin-root identifiers in an asserted independent intervention set. Distinct identifiers are *not* enough to establish genuine human/institutional independence; they are merely a required structural constraint.

## How it connects to the actual previous MOTIF code

`convergence.py` directly imports `genius009.two_clocks` from the adjacent existing experiment. The code creates three immutable source-owned records containing the original unrelated anomaly descriptions. When a bridge passes its experimental gate, a **new later analytical witness** can create three retrospective interpretation edges. Those edges never overwrite the prior observations and are labeled `INTERPRETATION_NOT_TESTIMONY`.

For unsuccessful regimes the two-clock corpus retains three independent strands **without fabricating callbacks**. This is a mechanical structural test. It does not imply the connection is artistically funny or historically significant.

## Strong controls / honest science

- **Weak lexical baseline:** choose the shared word with the highest motif score. It is a useful deliberately bad comparator, but not a serious causal method.
- **Observational association control:** confounded survey correlations can be large even without an intervention effect.
- **Source-aware classical exact baseline:** uses exactly the same intervention contrast, Fisher test, multiplicity correction, and source integrity rules. Its statistical classifications are **identical** to the new MOTIF module by construction. It is not an independent competing implementation of those statistics, nor proof of new algorithms.
- **Two-clock result:** a separate *interpretation/provenance graph*, not superior hypothesis testing.
- **No external sources:** all data/ground truth are from this engineer-authored synthetic generator. Validation and future seeds are different but not independently authored, externally blind tasks.

An unusually attractive or coherent relationship is **not** sufficient proof. Even if 3/3 simulated intervention contrasts pass, the receipt explicitly records `causal_mechanism_claim_allowed=False` and asks for independently run, authenticated replication before any real-world causal assertion.

## Reproduce

```sh
python -m unittest discover -s experiments/genius010 -p 'test_*.py' -v
python experiments/genius010/benchmark.py > /tmp/motif-genius010.json
python -m json.tool /tmp/motif-genius010.json >/dev/null
```

GitHub Actions archives the public-only synthetic evidence for one heldout case per regime, plus full aggregate scores. The design contract is SHA-256 frozen before sampling the six heldout seeds; thresholds and candidate sets are not optimized on those seed outcomes.

## Next meaningful trial

1. Invite **independent authors** to supply three genuinely unrelated evidence packets. Keep authors, collecting institutions and source roots independent and verifiable.
2. Allow MOTIF to **generate** candidate bridge mechanisms from typed existing hypotheses, while protecting against combinatorial multiple-testing inflation and post-selection bias. This experiment only **selects** among three preset candidates.
3. Establish pre-registered interventions only when ethically safe, legal, feasible and authorized; use observational identification/sensitivity bounds where intervention is impossible.
4. Compare against separate established causal-discovery and experimental-design implementations with identical data, candidate grammar, source audit and compute budgets.
5. Ask independent reviewers to score whether late reinterpretive connections are *meaningful, surprising and correctly evidenced* in real nonlinear narrative, scientific, and civic situations—without forcing one domain's standard on another.

**Invariance to defend:** separate investigations may acquire an explanatory relation, but the relation cannot rewrite their original records. Their independence, disagreements and limitations remain part of the result.