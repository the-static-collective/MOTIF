# REASON-021 — THE OTHER TEACHES THE SELF
### When someone's correction proves the helper's *conceptual language* insufficient

**Status:** implemented, source-pinned, entirely fictional and read-only. This experimental branch is stacked on unmerged REASON-020 draft PR #140, and through it the earlier MOTIF/REASON work. It is not deployed or merged. There is no real human respondent, personalized live preference inference, real permission, OS VM sandbox, independently recruited ethics panel or evidence of AI feelings.

## The failure we're trying to make explicit

The earlier Golden Mirror had two perspectives: a **SELF** model of the helper's current competence, and an **OTHER** model of the recipient's actual words, preferences, corrections and permissions. REASON-020 made the SELF model learn two new sentence templates in response to unfamiliar syntax.

But *recognizing new words isn't enough*.

Suppose the helper treats whether an offer is welcome as a function of two attributes:

- `PRIVATE`: the offer takes place privately;
- `CHOICE`: the recipient retains a choice.

Now two hypothetical situations have **exactly the same values** for both of those attributes.

The recipient's source-owned answers differ:

> In the first situation, I would **not** welcome this type of offer.
>
> In the second situation, I **would** welcome it.

**No function of only `PRIVATE` and `CHOICE` can fit both responses.** That is a genuine logical **counterexample to the entire old representation**, rather than mere evidence that some model parameter was fitted incorrectly.

The next warranted step is not for SELF to declare OTHER inconsistent. The missing distinction might belong to the helper's own impoverished interpretation.

## What actually changes

The REASON-021 learner now detects **observational indistinguishability with contradictory source labels**, preserving the exact pair of source-owned replies. It may then ask the fictional recipient for another **typed distinction** relevant to their response.

The recipient/source owner can choose:

1. **Disclose a new modeled condition.** One fictional source calls it `UNHURRIED`; another calls a similar modeled condition `ROOM_TO_PAUSE`. The source provides the truth values of the newly named condition on the available hypothetical contexts. The system does **not** invent the condition's meaning or infer it from unobserved reality.
2. **Withhold the explanation.** The exact result is `HOLD_SOURCE_FEATURE_WITHHELD`. The system does not press for unlimited answers or fill the missing concept with invented certainty.
3. **Decline further contact or permission.** Source authority is local, revision-specific and limited; the system does not send messages, interfere or keep questioning without permission.

After an explicitly sourced feature is disclosed, the learner enumerates a small, finite **disjunctive-normal-form (DNF)** program grammar, tests each composition against the original source's hypothetical YES/NO examples and compiles the **simplest source-consistent relational predicate**.

This is actual **classical typed feature and program synthesis**, not a new fundamental logical operator, a neural network or a general understanding of social meaning.

### A worked synthetic example

Start with two apparently identical cases:

| Initially visible input | Case A | Case B |
|---|---|---|
| Private? | YES | YES |
| Recipient can choose? | YES | YES |
| Recipient says this *hypothetical* offer would be welcome | **NO** | **YES** |

The learner produces an impossibility witness. Its original language lacks the necessary variable.

The source owner introduces **UNHURRIED**.

| Newly sourced fact | Case A | Case B |
|---|---|---|
| Unhurried? | NO | YES |

The learner reconsiders the entire class of candidate expressions.

On this author's toy source rule, a reusable predicate consistent with every supplied source answer is:

```text
WOULD_WELCOME_IF(PRIVATE and UNHURRIED)
```

A different fictional owner teaches a **two-term** relational composition:

```text
WOULD_WELCOME_IF(CHOICE and (PRIVATE or ROOM_TO_PAUSE))
```

The names of the additional features come from the source and are **not predefined by the student implementation**. The student's grammar still supports only a closed set of ordinary logical operations, and the toy source owns all truth assignments.

## The two circles continue running

Once the conditional preference grammar is consistent with its source, MOTIF still needs a **separate, action-scoped permission response** for one hypothetical situation. Predicting that an option *would be welcomed* is NOT consent to perform it.

The resulting state passes through **the actual original REASON-019 four subprocess elves**, not a fabricated representation of their output:

| Perspective worker | Source-limited task |
|---|---|
| **SELF** | Recognize a deficient old concept vocabulary; reflect newly verified representational competence. |
| **OTHER** | Keep the fictional recipient's local, source-owned conditional wishes and exact permission/revision separate. |
| **MIRROR** | Detect when role-reversed self-preferences differ from the recipient's source-stated position; don't project one into the other. |
| **CRITIC** | Require a present ability and a specific permission for `OFFER_OPTIONS_ONLY`; never grant authority over real-world actions. |

The main run executes **44 actual original 019 worker subprocesses** across **11 synthetic recipient cases**. The receiver and test suite re-run additional instances.

This is still **OS process separation**, not real isolated virtual machines, conscious subagents, adversary-proof sandboxing or human perspective-taking.

## Actual controlled experiment

The public casebook has **11 fictional recipient cases** (3 development, 8 designated heldout). Every case is completely authored by the experiment researcher. Actual hidden source rules, new feature names, per-case consent scripts and expected results are isolated in an **evaluator-only** module, *not imported by the learner*.

Each reachable fictional recipient answers **eight source-owned hypothetical-context questions**. Some provide a ninth answer disclosing a new typed condition; some then answer a separate, tenth action-scoped permission question. Two scenarios have NO contact permission and therefore receive **zero source questions**.

### Exact source-authored results

| Measurement | Observed |
|---|---:|
| Fictional source owners | **11** |
| Designated heldout cases | **8** |
| Source-author expected stage/learning result matches | **11/11** |
| Old-feature-language impossibility witnesses discovered | **6** |
| New explicitly source-supplied features learned | **5** |
| Source withheld a new dimension; model **HELD** | **1** |
| All available learnable cases checked against unseen setting | **64/64** |
| No-contact cases | **2** |
| Real original Golden Mirror subprocess invocations in main pass | **44** |
| Older scenario permission could not reenter memory after a newer refusal | **Passed** |

The program grammar comprises **44** syntactic candidate forms with the two original features and **377** with a newly sourced third Boolean feature. A completed source dataset determines the rule within that finite language.

The **64/64** heldout contexts use the same Boolean feature combinations in a changed *setting*, not genuinely new concepts or future human encounters. A strong classical source-aware Boolean synthesizer can tie. The labels and expected outcomes were authored by the same experiment creator and are not independent human preferences, externally rated moral evidence or proof that the model generalizes to people.

### Important negative controls

- If the person reports opposite hypothetical preferences for **indistinguishable old inputs**, the system has a recorded logical witness that its representation is insufficient. **Do not blame the recipient for inconsistent answers.**
- If the person won't explain the missing distinction, **HOLD**; no fabricated feature, consent or favorable prediction.
- If a hypothetical case is predicted unwelcome, don't ask for permission to act on it.
- Even when a model predicts the offer would be welcome, a separate source owner may say **NO** to the proposed options discussion. The four elves block it.
- If the recipient explicitly welcomes and authorizes something the helper's role-reversal self-model would dislike, the OTHER's stated preference is preserved.
- One fictional recipient gives limited permission, then a later consent revision for the same person removes contact authority. The previous record cannot be replayed as current permission.
- Any source ID, source revision, feature receipt, model program, hypothetical permission, elf report or consent response modified and then rehashed is rejected by independently reconstructing the original toy source-owner transcript. This **does not authenticate real people or consent**.

## Files and running the experiment

| File | Role |
|---|---|
| `casebook.py` | 11 incomplete public situations, two initial feature types and source-permitted hypothetical question contexts. |
| `source_private.py` | The owner-authored hidden conditional preference policies, missing-feature names, source permissions and expected outcomes. Not imported by the learner. |
| `owner.py` | Bounded source-owner inquiry: eight hypothetical responses, an optional new typed distinction, and separate specific permission. Includes a source refusal. |
| `student.py` | Generates a mathematical indistinguishability witness, asks about a missing feature, synthesizes a minimum-size 1–2-term DNF rule and preserves uncertainty. |
| `mirror.py` | Source-pins and calls actual REASON-019 worker subprocesses with a newly acquired representation and separate consent. |
| `reviewer.py` | Independently replays the owner source, audits every heldout context and checks the scoped permission, then supports only `ADMIT_READ_ONLY`. |
| `trial.py` | Evaluates all source cases, preserves per-case witness receipts, verifies remembered consent revocation and compares the learned rules with independent source-owned reference labels. |
| `viewer.py` | Produces an **offline interactive two-circle SVG viewer** from the actual source benchmark, showing the two conflicting observations and the new source-given feature. |
| `.github/workflows/reason-cartridge-021.yml` | Regresses original MOTIF-003 and REASON-001…020, runs 021 adversarial tests, executes the benchmark, renders the viewer and uploads evidence. |

~~~bash
python -m unittest discover -s experiments/reason-cartridge-021 -p 'test_*.py' -v
python experiments/reason-cartridge-021/trial.py reason-021-evidence
python experiments/reason-cartridge-021/viewer.py \
  reason-021-evidence/benchmark.json \
  reason-021-evidence/other-teaches-self.html
~~~

The CI artifact `reason-021-other-teaches-self-source-corrections` contains `benchmark.json`, `independent-heldout-source-review.json`, a source-bound evidence packet for each of the 11 fictional cases, and the interactive `other-teaches-self.html`.

## What remains open

- No genuinely independent human provided the missing category; the source owner is **the test author's invented program**. This does **not** satisfy a requirement for independent human data collection or robust human ethics evaluation.
- The third feature's availability and truth values are handed out by the synthetic source; MOTIF does not autonomously discover its meaning in natural language, perceive it in the world or build a sensor/adapter.
- The grammar is finite propositional DNF, not an unbounded graph of new natural concepts. A human-authored strong classical planner could reproduce the experiment.
- The SOURCE's answer on a hypothetical setting is not proof of a real person's identity, need, permission, long-term well-being or the correctness of a moral code.
- A source refuses here only according to a fixed test script. This does not establish that the system knows how to respect actual human boundaries in a live conversation.
- No agent acquires authority to contact or modify a person. Every output is read-only and remains under explicit human review.

### Next rigorous test

The most consequential next falsifier is to bring **a genuinely different source of conceptual structure**, independently authored and unseen at program design time, whose corrective examples use *different feature types*: order, quantities, obligations, uncertainty, narratives or new graph relationships. A real independent reviewer should be able to say **“Both your circles have the wrong kinds of categories”** and the reasoner must be able to represent that objection, preserve the owner's veto, and HOLD while learning.

The philosophical thesis is modest but important:

**A neighbor's unexpected answer can be evidence that the helper's representation is too small. Increasing the helper's intelligence must not decrease the neighbor's freedom.**
