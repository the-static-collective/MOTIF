# MOTIF LANGUAGE-GROWTH-001 — When a mathematical language is too small

**Status:** synthetic, executable, finite-meta-grammar investigation. Draft stacked after FEATURE-FRONTIER-001. No deployed agent, independent scientific verification, arbitrary-code invention, or automatic source modification.

## Question MOTIF asked

> When a bounded mathematical repertoire fails to explain observations, can MOTIF distinguish a lack of evidence from a language mismatch, propose an additional operator, exercise it on an independently measured problem, build a child, and keep a scoped receipt?

## The deliberately unfamiliar task

Existing `FEATURE-FRONTIER-001` synthesized graph features with `COUNT DISTINCT x`, existential `y`, and closure. Here the observed output is **the change in the number of 4-cycles** when a new edge `(a,b)` is added to a simple graph. The outcome instrument enumerates four-vertex cycles from `nunumathal.Graph` transitions (`contractdiscovery.apply`); the learner receives only the selected probe's measured integer outcome. It does **not** see a named `square`, `four_cycle`, or `three_path` operator or gold-labeled expressions.

An old-grammar diagnostic enumerates the genuine **237 existing expressions**. On two synthetic training interventions, none of those expressions can reproduce all observed results. This is a **finite-grammar contradiction**, *not* proof that no mathematical expression whatsoever is possible. If diagnostic observations are insufficient (e.g. all zero outcomes), the controller **holds without proposing an edit**.

## Executable expansion

A developer-supplied **meta-grammar** permits three possible generic extensions to the counting semantics:

- `COUNT_OTHER_BINDING`: count distinct existential `y` rather than `x`;
- `PRESENCE_OF_TWO_BINDINGS`: count only whether any satisfying `(x,y)` assignment exists;
- `COUNT_BINDING_PAIRS`: count distinct satisfying `(x,y)` assignments.

For each licensed edit, an enumerator generates candidate expressions from up to three elementary edge atoms chosen from `a,b,x,y`. **No correct atom arrangement or patch is handed to the selector.** It evaluates **90** new candidate programs, using observations from the original diagnostic plus an actively chosen third synthetic edge-addition experiment. The winning finite model is:

```
1 * COUNT_XY(E(a,x), E(b,y), E(x,y)) + 0
```

This counts the length-three walks between previously unconnected edge endpoints, which in a loopless simple graph are precisely the additional 4-cycles produced by that edge. The process has **not invented the concept of counting pairs from nothing**: the meta-grammar and evaluator for `COUNT_XY` were explicitly authored. It *selected a grammar edit and synthesized its use*.

It verifies the frozen model against separate validation graphs and then reports untouched test and larger OOD data. The strong baseline uses an independent neighbor-intersection path enumerator. This should tie a correct synthesizer; there is no claim of novel mathematics or better performance than classical methods.

## Reproduce

In the full stacked GitHub checkout:

```sh
cd experiments/languagegrowth001
python -m unittest -v test_languagegrowth.py
python languagegrowth.py
python benchmark.py
```

Python 3.11+, standard library only. The experiment imports real `nunumathal.Graph`, real prior feature-program enumerations, and real prior graph transition logic.

## Locally observed frozen results

| Measure | Result |
|---|---:|
| Existing grammar candidates | 237 |
| Observations before old grammar contradicted | 2 |
| Candidate programs from permitted grammar edits | 90 |
| Training interventions before a validated edit | **3** |
| Held-out graph experiments | **30/30 correct** |
| Larger OOD graphs | **30/30 correct** |
| Strong handwritten classical comparator | **60/60 correct** |
| Constant-zero comparator | **8/60 correct** |
| Without `COUNT_BINDING_PAIRS` edit | `HOLD_NO_SUPPORTED_OPERATOR` |
| Three-intervention random selection, 10 seeds | **10/10 validation success** |
| Eight-intervention random selection, 10 seeds | **10/10 validation success** |

**Negative result:** The active selection mechanism did not outperform random selection on the tested pool and budget. The value of this experiment is controlled, testable **language repair**, not a demonstrated advantage from active learning or general intelligence.

The generated read-only child verifies pinned exact source hashes, reconstructs the discovered formula from a serialized AST, replays the finite learning/validation fixture, and tests an untouched example in a separate Python process. Hashes detect changes but cannot prove source authorship, and subprocess separation is **not** a secure execution sandbox for malicious code.

## Restrictions and challenges

- Only undirected, loopless finite graphs and insertion of a previously absent edge are modeled. A shared source/simulator bug can corrupt both diagnosis and learning.
- Training, validation, test, and OOD fixtures are generated by one author and one known mathematical mechanism; larger graphs do not establish transfer to a genuinely different world.
- The meta-grammar already contains the necessary pair-counting extension. If the needed primitive is not offered, the system must refuse. This is **not** unrestricted invention of new operators.
- The diagnostic must observe an actual contradiction before expanding. A merely uncertain model is not classified as a grammar failure.
- A surviving law is at most `I` (proposal) in FIR; only exact computations on specified finite fixtures are `F_LOCAL`.
- A child never edits the repository, deploys itself, fetches arbitrary internet data, spends money, or acts on physical objects.

## Next legitimate frontier

Can MOTIF generate **operator implementations** from candidate semantics and executable counterexamples rather than selecting from a supplied meta-grammar? Compare against strong classical program synthesis and external unanticipated task families; require negative controls where the new operator introduces overfitting or unacceptable computational cost.
