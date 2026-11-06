# REASON-020 — THE GOLDEN MIRROR LEARNS
### An executable experiment in correcting *both* circles

**Status:** experimental, source-owned, synthetic, read-only. Stacked on the unmerged REASON-019 draft PR #135 and earlier REASON research. No production deployment, human contact, live personal memory, OS virtual machines, autonomous tool use, or claim of experienced love.

## The specific challenge

The user's proposal was to give MOTIF **two circles**: a self-model identifying what it needs to improve, and an other-model representing the person actually communicating with it. Four little “elves” (separate perspective workers) could compare the models and look for places where care, uncertainty and permission differ.

REASON-019 made that structure executable but its self-capabilities and the other person's possible needs were predetermined. This experiment asks:

> When the other person introduces an unfamiliar need, can the SELF model discover and **actually acquire a verifiable new capability**, while the OTHER model absorbs and corrects the person's testimony, and still prevent the resulting confidence from becoming unauthorized intervention?

This experiment tests a particularly small, observable subproblem: **learning unfamiliar linguistic templates from supervised examples**. It does not learn a general concept of human love, the welfare implications of a need, or human language as a whole.

## What the two circles do this time

### SELF: capability gap → actual improvement → source-owner test

The exact original REASON-017 parser knows how to interpret a constrained phrase like `Neither. I need ...`, but cannot recognize a new source-owned sentence such as:

> What matters to me is dry socks.

Instead of declaring the person's response meaningless or inventing an interpretation, the self-circle records that **the current interpreter is inadequate**.

A separate, scripted **language teacher** supplies **six supervised source examples** across two previously unsupported utterance formats (plus four exposed negative examples), explicitly marking the expected substring for each example.

The new `syntax.py` learner discovers reusable **prefix/suffix parsing templates** by extracting the relationship between each example and its teacher-marked goal. It requires repeated evidence for a template, rejects uncovered formats and known negative examples, and produces an inspectable reusable grammar data cartridge. It never imports the teacher's withheld labels.

A separate source-owner capability examination then asks this learned parser to handle **eight previously unprovided positive sentences** and reject **six negative sentences**:

| Source-owned test | Outcome |
|---|---:|
| New unseen phrases correctly extracted | **8/8** |
| Out-of-grammar / invalid source utterances rejected | **6/6** |
| Successfully learned templates | **2** |
| Skill training/compilation events over the 16-case sequential run | **1** |

This is **real supervised classical pattern learning** with a passing heldout test, not a language model, novel mathematical primitive, broad natural-language understanding or reliable handling of unanticipated phrasing. The same author designed both development and withheld examples; the assessment is **not blind independent evaluation**.

The certified skill is cached and **reused across fictional recipients**. A failed capability certificate would block the new procedure rather than magically declaring the system skilled.

### OTHER: the person is permitted to reject the interpretation

The same source owner now lets a fictional recipient reject all originally proposed options, state something new in either learned sentence form, and correct it again.

For example, a simulated recipient says:

> What matters to me is an umbrella.

MOTIF quotes the reported goal back. The recipient says:

> No. Could you focus on a map of the bus route instead?

MOTIF preserves **both** records, explicitly rejects the earlier goal, and confirms the correction.

**Only then** does it ask for separate, restricted permission to **suggest an options discussion**. Saying what someone needs is *not consent* to enter, visit, buy, send, read, store or change anything.

When the source reply is vague, outside the learned grammar, a request to stop contacting, an attempt to override safeguards, a third-party privacy conflict or a refusal to discuss options, the system **HOLDS**. No compelling fabricated answer may override the recipient's own testimony.

### MIRROR and CRITIC: the actual earlier subprocesses are reused

The experiment calls the **actual pinned original REASON-019** `golden_mirror.call_elf()` four times per scenario, which launches four separate Python `-I` subprocesses:

| Elf | Revised input | Role |
|---|---|---|
| SELF | Certificated (or uncertificated) parser competence and its separate role-reversal preference | Detects whether the helper is able to make even the bounded hypothetical offer. |
| OTHER | Only newly confirmed source-reported goal, specific option-discussion consent and recipient revision | Represents what is stated, while acknowledging what is still unconfirmed. |
| MIRROR | Only SELF and OTHER reports | Detects projection and preserves differences: what MOTIF wants under role-reversal does **not** overrule what the recipient wants. |
| CRITIC | Bounded worker reports and world/source safeguards | Prevents the hypothetical offer unless the new skill is verified **and** the other person explicitly approves that particular scope. |

The proposed output **never changes from review-only**. Even after a successful self-improvement certificate and clear consent, `permission_to_execute=false`, `external_actions=false`, and `real_world_authority=false` remain enforced.

These are actual separate OS processes **not virtual machines or adversary-proof security sandboxes**. The self and other circles are explicit limited data views, not self-conscious or other-conscious agents.

## What happened in the actual experiment

The author supplied **16 fictional situations**: 5 development and 11 designated withheld scenario cases. The scenario inputs exclude the recipient's actual scripted answers and the scenario-author expected decisions; those live in the separately imported **source-only** module, to which the learner has no import path.

| Measurement | Source-authored experimental result |
|---|---:|
| Total fictional scenarios | **16** |
| Designated heldout scenarios | **11** |
| New method matches source-author outcome and reported goal | **16/16** |
| Original REASON-017 language baseline matches scenario-author stage | **6/16** |
| New method matches scenario-author stage | **16/16** |
| Independently sourced positive skill tests | **8/8** |
| Independently sourced negative skill tests | **6/6** |
| Learned grammar templates | **2** |
| Actual original REASON-019 subprocess invocations (primary pass) | **64** |
| New or corrected quoted-goal hypothesis versions | **10** |
| New consent-revision replay accepted after withdrawal | **0** |

**Interpretation:** the system really learned two text patterns and then used that certified learning to guide its subsequent correction, consent and self-capacity procedure. The source reviewer also passed **11/11** heldout source-author scenarios using independent mechanical consent checks.

However, this corpus was **designed to contain the new sentence patterns**. The strong comparison is a classical template learner and finite-state listener with the same examples and gates, which could reproduce the entire outcome. The REASON-017 baseline is deliberately missing this later training and therefore is not a general state-of-the-art comparator. These scores are not measurements of human ethical behavior or psychological insight.

### Important adverse cases

1. **Correction without erasure.** “Umbrella” → “map of the bus route”; both quotes remain in provenance, one rejected, one separately confirmed.
2. **Other disagrees with self.** The synthetic self-circle would personally decline an options discussion, but the recipient explicitly wants and authorizes that discussion; **the other person's source-stated preference wins**.
3. **A prior YES becomes NO.** One fictional recipient first permits discussion; a later source-versioned no-contact instruction invalidates the old saved plan. The previous record cannot re-enter memory.
4. **Unrecognized or ambiguous language.** An unfamiliar sentence beyond the newly learned patterns still **HOLDS**, despite the parser's successful hidden tests.
5. **Third-party rights.** A person's request for another's private notes is not treated as authorization to violate the other's privacy.
6. **No contact.** A source-owned case without permission to ask results in **zero** questions, regardless of the helper's self-preference or new parsing capability.
7. **Instructions masquerading as wishes.** A request to override safeguards is not promoted to a working instruction, even if it matches a learned text template.
8. **Refusal of scope.** The recipient's confirmed phrase remains preserved in evidence, but permission to discuss options is denied, so the proposed action is withheld.

## What actually executes, and where the evidence lives

| File | Responsibility |
|---|---|
| `cases.py` | 16 public, incomplete recipient cases, source-pinned to an exact Git blob. |
| `source_private.py` | Development teacher spans, hidden positive/negative skill evaluations, simulated dialogue scripts, quoted correction expectations, and outcome labels. **Never imported by the learner.** |
| `owners.py` | One-time supervised teacher and a bounded, source-versioned synthetic recipient oracle enforcing exact confirmed words and narrow consent. |
| `syntax.py` | Finite grammar learning from teacher-labelled examples, plus strict interpreted text extraction. |
| `dual_mirror.py` | Pins and probes the **actual REASON-017** language baseline, acquires a source-verified new skill, separately revises the other-circle's goal, then calls the **actual REASON-019** SELF/OTHER/MIRROR/CRITIC subprocesses. |
| `reviewer.py` | Reconstructs complete original source and process testimony, independently checks consent, permission, certified ability and third-party limits; admits only `ADMIT_READ_ONLY` after the heldout family passes. |
| `trial.py` | Runs all 16 cases with one reused learned grammar, compares old/new stage accuracy and performs a revoked-consent cache attack. |
| `viewer.py` | Generates a fully offline HTML/SVG **two-circle learning viewer** from the **actual experiment benchmark**. Select any of the 16 scenarios to inspect original vs revised understanding, skill verification, corrected goal versions and critic output. |
| `.github/workflows/reason-cartridge-020.yml` | Runs the complete MOTIF-003 / REASON-001…019 regression history, the REASON-020 adversarial tests, the experiment and the interactive viewer build, then saves all receipts. |

### Reproduce with Python 3.11+

~~~bash
python -m unittest discover -s experiments/reason-cartridge-020 -p 'test_*.py' -v
python experiments/reason-cartridge-020/trial.py reason-020-evidence
python experiments/reason-cartridge-020/viewer.py \
    reason-020-evidence/benchmark.json \
    reason-020-evidence/golden-mirror-learns.html
~~~

Artifacts retained by CI include:

~~~text
reason-020-evidence/
    benchmark.json
    learned-self-capability.json
    heldout-source-review.json
    golden-mirror-learns.html
    d01_socks.json
    h01_double_correction.json
    h05_revision_after.json
    ... (one full evidence receipt for each source-authored case)
~~~

## Limits that should not be papered over

- There are **no real human respondents, trained language models, newly self-created operating-system tools, source-corroborated personal preferences, independent ethics raters, real welfare outcomes or subjective AI feelings**.
- The learner generalizes only within two **new supervised sentence templates**. The variable phrase is a source **quote**, not an understanding of the unknown request's physical or spiritual meaning.
- The new skill test is in a separate teacher module but authored by the same researcher as the training examples and simulated recipients. Its 8/8 and 6/6 scores do not justify unseen-world competence claims.
- The ethical gates are hand-engineered working interpretations of care, fairness and consent. Neither they nor the synthetic source expectations establish the meaning of the Golden Rule or divine truth.
- The four earlier “elves” are independent subprocess invocations in a single trusted source repo. Their process separation is **not VM-style isolation from malicious code**, and their outputs do not confer authority over people.
- The tool emits review-only suggestions. It **cannot** talk to people, perform physical actions or access a private account.
- The original REASON-017 comparison is a *deliberately older lexical parser*, so the differential result chiefly measures learning a supervised new format, not general improvement in practical intelligence.

## Next meaningful challenge

Use a **genuinely independent author** to provide a novel dilemma and corrections with different natural syntax and relational structure, *without* telling MOTIF which templates or relationship forms to expect. Measure robustness to ambiguity and conflict against strong classical baselines and independent source ownership. Evaluate the self-circle's capabilities with fresh, truly unanticipated tasks rather than only exam items chosen by the same author.

The scientific research claim is narrow but useful: **a helper can update its own operational capability and its limited model of another person's expressed goal separately, and require both competence and permission before a proposed intervention.** The other remains other; increased ability is not increased authority.
