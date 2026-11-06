# REASON-023 — THE MANY-TRUTH MIRROR
### Source-supported alternatives, honest contradiction, and the right not to answer

**Status: an experimental, read-only, stacked draft.** Based on the unmerged REASON-022 branch (draft PR #149), which itself builds on earlier MOTIF/REASON drafts. Neither this package nor its four-process Golden Mirror bridge contacts or profiles real people, executes tasks for them, or measures love.

## The failure we are correcting

REASON-022 evaluated three developer-supplied classical typed solvers on independently authored Facebook bAbI story questions. On the prospectively reserved questions 251–500, **749/750** matched the dataset's answer key. One wrong scorer match was especially instructive: the story contained source lines supporting *both* the official answer and a different answer chosen by our solver. The single-answer parser silently selected a recent event, asserting more certainty than the evidence warranted.

The new research question is **not** "How do we force the last remaining score to 100%?" It is:

> Can MOTIF preserve every independently source-supported interpretation, distinguish nonunique answers from genuine source contradiction, actively propose the most useful possible clarification, and refuse to ask when the source has not permitted questions?

This is a tractable, experimentally falsifiable target. Our earlier REASON-011 four-valued system already preserves explicitly positive/negative factual evidence. Our earlier REASON-019 Golden Mirror runs four separate bounded perspective subprocesses. Both source codebases are reused and Git-blob-pinned, not imitated.

## Four deliberately separate components

### A. Source-evidence hypergraph, not one best guess

`source_graph.py` imports the **actual exact Git-blob-pinned REASON-022** transfer predicate and original single-answer engine. It reads the numbered source sentences and query—but **never the bAbI gold label or official support-index annotations**.

It builds source-linked event edges:

~~~text
Bill ──GAVE──> [apple] ──TO──> Mary   (source line 2)
Bill ──GAVE──> [football] ──TO──> Mary (source line 11)
~~~

Every distinct answer is now a candidate with its own source-edge IDs, full exact quotes, premise lines and explicit structural assumption: *this utterance literally matches the question*. Repeated support for the **same** answer is retained without inventing a separate contradictory answer.

If exactly one source-supported answer exists, the result is `ANSWER`.

If multiple **different** answers are source-supported, the result is:

`HOLD: NON_UNIQUE_SOURCE_SUPPORTED_ANSWERS`

The model still records what an **EARLIEST_EVENT** or **LATEST_EVENT** assumption *would* select, but neither assumption is presented as a source-established fact. These alternatives are disjunctive **interpretations**, not automatically claims that one answer has an explicit NO witness.

An independently coded, strong **all-source-events classical baseline** checks every candidate. **The new graph method is itself classical finite graph enumeration and should tie that strong baseline**, not surpass it.

### B. Paraconsistent truth is different from ambiguous alternatives

`polarity.py` imports the actual, source-blob-pinned original **REASON-011 `verdict()`** to validate an independent source-scoped four-value checker over *fictional* explicit YES/NO statements.

| Source evidence for one proposition, same person and same revision | Result |
|---|---|
| YES only | `SUPPORTED` |
| NO only | `REFUTED` |
| Explicit YES and NO | `BOTH` |
| Neither | `UNDETERMINED` |

Two people disagreeing or a person changing their mind in a later revision does **not** automatically create a same-scope `BOTH`. Neither does the presence of two different source-backed answers in bAbI. No contradictions are inferred from silence, and an unrelated allegation has no authority over this source.

This dual classification avoids two symmetric mistakes:

1. **Premature convergence:** one possible answer is silently chosen because it is the most recent.
2. **Premature collapse:** every disagreement or difference is labeled a contradiction that would license arbitrary inference.

### C. Source-conscious active learning, but no unsolicited questions

`inquiry.py` proposes *bounded binary questions* that partition the set of competing, source-backed answers. Under an explicitly declared **artificial uniform prior**, the planner chooses a balanced partition maximizing binary entropy reduction.

For four competing alternatives, a 2–2 question yields exactly **1 bit** of possible reduction. This is classical active learning, not knowledge of what an actual person believes or wants.

An **entirely fictional source clarifier** may agree to answer, decline, prohibit questions, withhold contact or exhaust a bounded question budget.

- If the source provides a valid correction, the resulting interpretation remains **read-only and tied to that fictional source's reply**.
- If the source says no, `HOLD_SOURCE_REFUSED`.
- If no source has authorized contact or there is no identifiable owner, `HOLD_NO_QUESTION_PERMISSION` or `HOLD_AMBIGUITY_NEEDS_SOURCE_PERMISSION`.
- If no further source questions remain, `HOLD_QUESTION_BUDGET`.

**This simulated clarifier is not the author of the actual bAbI dataset.** Its intervention is NOT applied retroactively to the external source answer key, and it grants no moral, personal, legal or operational authority.

### D. The actual Golden Mirror checks permission

`mirror_bridge.py` calls the **real Git-blob-pinned REASON-019** subprocess implementation four times per fictional situation:

- SELF: the helper's provisional preference for clarification;
- OTHER: source-stated limits on questions and contact;
- MIRROR: projection vs the other person's independent wishes;
- CRITIC: whether even the proposed *question* is authorized.

Four synthetic settings exercise permission, no permission, no contact and a SELF preference different from the source. The primary pass launches **16 actual subprocess perspective workers**; independent reviewer/test replays launch additional processes.

The outcome is only **ASK_PREFERENCE** or **WAIT**, without a live message being sent. Original `permission_to_execute=false` continues to hold.

## First independent source experiment: new untouched question slice

The previous REASON-022 development process inspected source test questions 1–250 per task, then evaluated and inspected 251–500 per task. **This branch reserves the as-yet-uninspected bAbI Task-5 transfer questions 501–750**, exactly 250 fresh externally authored questions, before reading their gold labels.

The dataset is the public Facebook bAbI v1.1 copy published by [iamtrask/Grokking-Deep-Learning](https://github.com/iamtrask/Grokking-Deep-Learning/tree/e665168b4aefe3256360951504103cf98827ca51/tasksv11/en), pinned to exact commit `e665168b4aefe3256360951504103cf98827ca51` and original Git blob SHA for each of six source files. Credit: Weston et al. 2015, *Towards AI-Complete Question Answering*, arXiv:1502.05698; original dataset CC BY 3.0.

**Scoring categories preserve a three-way distinction:**

1. **Unique source answer:** correct vs confidently wrong against the official gold label.
2. **Nonunique source answer:** explicit HOLD, with a separate indicator whether the official gold label is among the supported candidates.
3. **No source-grounded answer:** explicit HOLD.

The trial reports *all three* of those categories, the original single-answer algorithm's performance, and an independent all-source-events classical baseline. A HOLD isn't counted as a correct gold answer; it reduces forced certainty at a cost of coverage. Even when the official gold is included in a multi-answer set, we do **not** call that an exact single-answer success.

### Actual result — including the cost of being cautious

The first and now-inspected external reserved 501–750 run is complete.

| Independent test metric | Exact result |
|---|---:|
| Independent bAbI transfer questions | **250** |
| Original REASON-022 single-answer parser | **250/250 exact; 0 HOLD** |
| New source graph: unique supported answer, matching gold | **183/250** |
| New source graph: confident mistakes | **0** |
| New source graph: multiple different answers explicitly supported | **67/250 HOLD** |
| Of those 67, official gold included among the supported options | **67/67** |
| No grounded candidate | **0** |
| Strong independent exhaustive-source classical baseline agrees with candidate set | **250/250** |

**This is not an accuracy win.** The old system answers all 250 gold questions correctly; the conservative new answer policy abstains on **26.8%** of them. It does expose **67 sets of multiple literal-source answers**, but the original bAbI scorer expects a single response, and implicit recency, discourse focus or annotated supporting lines may legitimately resolve those questions. The model's **single-answer coverage fell from 100% to 73.2%** without preventing a single actual original-model mistake on this new slice.

The result therefore tests a genuine tradeoff: **source literal evidence preservation vs. answer coverage on an artificial dataset**. Do not claim 250/250 official correctness for the new policy, and do not claim the 67 abstentions rescued 67 errors; they did **not**. This is a **negative result for task-answer efficiency** and a positive implementation result for inspectable multi-source provenance and non-forced selection.

The previously identified one wrong original-model answer was on the *earlier* 251–500 slice. We did not reuse that inspected slice as fresh external performance. This next slice (501–750) is **now also inspected**; any posthoc correction requires a further unseen test set.

The official dataset author did not necessarily intend a multi-answer question. Literal support is an alternative interpretation, not proof of equivalence with the official annotation. Every confident mistake and abstention is retained in the CI artifact.

These 250 examples are **prospective only up until the first completed run**. Once results are inspected, any later repair must use an additional uninspected source slice or dataset. Do not call the same observations independently blind twice.

## Tests, artifacts, and reproducibility

| Source | Function |
|---|---|
| `source_graph.py` | Full source event graph, competing candidates, provenance checks, original REASON-022 single-answer comparison. |
| `polarity_cases.py` + `polarity.py` | Fictional signed-source scenarios, separate person/epoch, and actual original REASON-011 cross-check. |
| `inquiry.py` | Entropy-based balanced partition questions, simulated source veto, permission and question-budget limits. |
| `mirror_bridge.py` | Real original REASON-019 four-subprocess Golden Mirror (SELF/OTHER/MIRROR/CRITIC), restricted ASK vs WAIT. |
| `trial.py` | Evaluates untouched external bAbI questions 501–750, reports all false confidence/HOLD, tests a classical baseline, and writes source-provenance artifacts. |
| `viewer.py` | Standalone offline interactive HTML with the two circles, source candidate graphs, explicit source hypotheses, four-valued signed proof, simulated question policy and source-scoped criticism. |
| `test_many_truth.py`, `test_viewer.py` | Adversarial checks of fabricated source evidence, repeated witnesses, no-source cases, incorrect scopes, self preference vs permission, and source questionnaire refusal. |
| `.github/workflows/reason-cartridge-023.yml` | Regresses MOTIF-003 and REASON-001…022, acquires the externally pinned bAbI source and full historical opinions used by earlier tests, runs source/evidence benchmarks and uploads a 30-day read-only artifact. |

~~~bash
python experiments/reason-cartridge-022/acquire.py reason-023-sources
python -m unittest discover -s experiments/reason-cartridge-023 -p 'test_*.py' -v
python experiments/reason-cartridge-023/trial.py reason-023-sources reason-023-evidence
python experiments/reason-cartridge-023/viewer.py \
  reason-023-evidence/benchmark.json \
  reason-023-evidence/many-truth-mirror.html
~~~

The artifact `reason-023-many-truth-source-graph-and-active-inquiry` includes: `benchmark.json`, all ambiguous answers and full source witness graphs, all confident wrong or unsupported examples, four-value source test receipts, the bounded inquiry and real subprocess traces, original external source provenance, and the offline `many-truth-mirror.html`.

## What this cannot claim

- **No AI subjective experience, empathy, love, or genuine spiritual/moral discovery.** The user's Golden Rule remains a philosophical objective, not a benchmark-measured achievement.
- **No open-ended independent algorithm invention.** The graph expansion, supervised query selection, four-value logic and subprocess programs are classical, human-written programs; the experiment composes them and verifies concrete evidence.
- **External QA != a person's needs.** The bAbI dataset's independent authorship establishes a better technical source test, not an independently owned ethical scenario, a real person's consent or a source-owner-authorized inquiry.
- **Source literal matching can overproduce alternatives.** Historical event order, conversational reference, and the dataset author's intended support annotations may disambiguate an apparently multi-answer case. Such cases remain conservatively unresolved and MUST be reviewed, not silently counted as solved.
- **No secure virtual machines or external permissions.** `python -I` isolates imports but is not an OS security boundary; no external actions are authorized or taken.
- **A strong classical graph solver can tie.** The value here is transparency, scope, abstention and evidence, not outperforming classical algorithms.

## A harder next falsifier

Combine multi-interpretation source graphs with **causal and temporal discriminators** rather than just asking which literal answer is intended. Allow multiple *competing causal explanations* with different consequences, source-versioned observations and counterfactual intervention plans. Require the system to choose observations by the **expected reduction in downstream harmful actions**, not only entropy. Test against independently constructed source narratives and strong classical causal-model baselines.

The underlying philosophical design goal remains:

> Another person's reality may not fit the helper's favorite interpretation. Intellectual care includes preserving that difference, recognizing uncertainty, and accepting the other person's right not to answer.
