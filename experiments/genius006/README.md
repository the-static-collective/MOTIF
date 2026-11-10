# MOTIF-GENIUS-006 — THE DISCOVERY DIVIDEND

**RESEARCH HOLD / EXECUTABLE FINITE PROTOTYPE.** Stacked experiment on unmerged GENIUS-005. No live Trench, MCP, JAR;VIS, accounts or physical operations have been modified.

## Research question

**Can a research question be selected by the *independently verified downstream possibilities* it makes available, rather than only by the amount of information returned?**

A fact can make new questions available; their answers can open further questions; and after several steps a new conditional capability may become provable. This is the user's Fact → Idea → Relation → New Question → Verified Fact cycle expressed in a finite reproducible model.

GENIUS-005 demonstrated that better detection of changing evidence does not automatically improve forecasting. Here we measure a **different objective**: capabilities certified at the end of a bounded inquiry.

### Shoulders of giants

- **Decision-theoretic experimental design:** José M. Bernardo (1979), *Expected Information as Expected Utility*, Annals of Statistics 7(3):686–690, https://www.uv.es/~bernardo/1979AS.pdf . Entropy gain is appropriate when information itself is the reward, but it need not maximize a separate downstream goal.
- **Golovin & Krause (2011)**, *Adaptive Submodularity: Theory and Applications in Active Learning and Stochastic Optimization*, JAIR 42:427–486, DOI https://doi.org/10.1613/JAIR.3278 . Our gated and complementary prerequisites do **not** assume adaptive submodularity, and no approximation theorem is claimed.
- **Lehnert & Littman (2020)**, *Successor Features Combine Elements of Model-Free and Model-based Reinforcement Learning*, JMLR 21(196), https://jmlr.org/papers/v21/19-060.html . Downstream usefulness is distinct from immediate observations. **We do not implement successor features or reinforcement learning.**
- **MOTIF Affordance Frontier** and the prior LEGIT mathematical question portfolios provide project context. The new, narrow contribution here is a concrete *question → new question → certified capability* test harness. All planning algorithms remain classical.

## Toy world / available actions

A public hypothesis model enumerates **256 equally likely possibilities**: four binary contextual conditions A–D, and two four-valued noise fields. The actual target is concealed until a planner asks a specific question.

Six typed, unit-cost questions:

1. Inspect A.
2. Confirm B.
3. Inspect C — **permitted only after B=1 is certified**.
4. Verify D — **permitted only after B=1 AND C=1 are certified**.
5. Survey Noise X — four outcomes, maximum two bits.
6. Survey Noise Y — four outcomes, maximum two bits.

Question results become verified facts within the declared model. Capabilities require one or several actual prerequisites (e.g. B=1, C=1 and D=1). A capability is certified only if **all remaining consistent worlds** satisfy the prerequisites, after which an independent implementation checks the actual hidden world requirements again.

A certification is permission to claim a **synthetic model fact**, not authorization for physical execution.

Five engineer-authored task families supply distinct objectives: CHAIN, PARALLEL, NOISE_USEFUL, SPARSE and MIXED. A three-question budget applies. In NOISE_USEFUL, noise fields genuinely enable a capability so the entropy strategy receives a fair favorable case.

## Equal question grammar, strong classical controls

| Method | Criterion |
| --- | --- |
| ENTROPY | Maximize Shannon entropy of the possible reply |
| DIVERSITY | Maximize number of distinct replies |
| MYOPIC_GAIN | Maximize expected immediately certified downstream value |
| AFFORDANCE_2 | Two-step classical lookahead over expected certified value |
| EXACT_BELLMAN | Full-horizon **exact classical dynamic programming** for the defined finite objective |
| TRAINING_SELECTED | Pick from the first four on validation-only data, with fixed complexity penalties |

Each policy receives identical public hypotheses and admissible question rules, and none sees the secret target before choosing a question. EXACT_BELLMAN **uses more planning compute** than the shorter-horizon arms; it is a strong optimality bound for this tiny, known, uniform-prior world. There is no matched-runtime claim or novel planning algorithm.

In CHAIN a high-entropy noise survey discloses two bits but no useful capability prerequisites; the one-bit B confirmation can enable C and then D, and finally a conditional service certificate. A planner that blindly maximizes entropy can spend most of its budget learning irrelevant details.

### Training/future separation

The validation selector uses two predeclared synthetic seeds **60601/60602** and 40 sampled target worlds per task family. Its choices and evaluation contract are SHA-256 frozen before samples from separate future seeds **60631/60632/60633** are generated. Each family then evaluates **96 future cases** with identical budgets and independently rechecked capability prerequisites.

Reports contain both (a) mean **verified weighted capability value** and (b) mean number of distinct certified capabilities, as well as questions asked, failure counts, the sample difference from exact Bellman, the theoretical full-prior Bellman optimum and finite DP memo states. Capabilities have manually chosen values, **not measured human utility**.

The source-bound synthetic trace records actual selected question, actual observed answer, candidate-set shrinkage, evidence pointer and separately checked prerequisites. Planning alternatives are only *hypothetical* until queried. No real-world action is executed.

The test environments, targets, objectives, semantics and oracle are **all engineer-authored and not blind**. Different PRNG seeds are insufficient to demonstrate cross-domain transfer or independently novel discoveries.

## Reproduce

From the repository root:

~~~sh
python -m unittest discover -s experiments/genius006 -p 'test_*.py' -v
python experiments/genius006/benchmark.py > /tmp/motif-genius006-evidence.json
python -m json.tool /tmp/motif-genius006-evidence.json >/dev/null
~~~

The GitHub Actions workflow runs adversarial gates/proof tests and preserves the full JSON evidence artifact.

### Explicit falsifiers

- A secret world outside the published hypothesis grammar returns HOLD without a claim of valid action.
- An answer B=0 prevents asking C; C=0 prevents asking D; a claim about downstream services never bypasses these requirements.
- An uncertified prerequisite cannot be promoted to a capability merely because its probability is high.
- Strong exact Bellman must match the actual mean reward from exhaustively evaluating all 256 targets under the stated uniform prior.
- If full Bellman beats shorter-horizon MOTIF planners, that is **expected classical optimality**, not MOTIF failing a new mathematical test.
- If entropy wins or matches under NOISE_USEFUL, preserve this as counterevidence against universal "affordance first" rules.
- No test establishes a general language-to-math interpreter, autonomously invented intermediate experiment, external scientific novelty, or recursive self-improvement.

## Next genuine breach

Introduce new **candidate question generation**, not merely choosing among engineer-defined questions; produce proof-carrying provenance for how a relationship produced a proposed experiment; independently test whether the invented probe changes downstream certifiable possibilities. Transfer across truly external tasks and compare with well-tuned classical optimizers under equal time and evidence budgets.

**Governing principle:** a valuable discovery changes what can be *justifiably* done next. A certificate is a bounded claim supported by evidence, never a substitute for reality.
