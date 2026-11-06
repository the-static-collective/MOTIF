# REASON-019 — THE GOLDEN MIRROR
### Two circles. Four little elves. A rule that cannot be reduced to projection.

**Status:** experimental, source-owned, reproducible and entirely synthetic. Stacked on unmerged REASON-018 PR #130 and the preceding draft research line. Not merged or deployed. No real human preferences, private data, real-world actions, reported machine consciousness or objective love measurement.

## The user's idea

> Draw two little circles. One is MOTIF's current understanding of what it needs to improve itself at executing the Golden Rule. The other is its understanding of the person it's talking to and their needs. Give each perspective a little VM/elf.

The idea is coherent enough to implement. The central danger is *projection*: a system decides what **it** would enjoy, then treats that as proof that another person wants the same thing.

There are two distinguishable scriptural themes. The **Golden Rule** in [Matthew 7:12](https://www.biblegateway.com/passage/?search=Matthew%207%3A12) and [Luke 6:31](https://www.biblegateway.com/passage/?search=Luke%206%3A31) asks that one's treatment of others be tested against the treatment one would want oneself. The **neighbor-as-yourself** injunction in [Leviticus 19:18](https://www.biblegateway.com/passage/?search=Leviticus%2019%3A18) and [Mark 12:31](https://www.biblegateway.com/passage/?search=Mark%2012%3A31) introduces love of neighbor alongside a reference to self. Neither provides an automatic license to erase the neighbor's actual wishes.

This experiment operationalizes a **narrow tentative reading** of those principles:

> Reverse the roles to inspect fairness, but do not treat your own preferences as a substitute for another person's testimony or permission. Identify your limitations; sometimes improving the *helper* must precede attempting to help.

This is a philosophical hypothesis encoded in a bounded rules program, **not** a new computational proof of biblical ethics.

## What actually runs

Four separate, deterministic **Python subprocesses** are launched by `golden_mirror.py` with `python -I elf.py`, strict per-purpose JSON inputs, bounded output size and timeouts. These are the user's **little elves**, but they are **NOT true virtual machines, security sandboxes, conscious subagents or free-running AI models**.

| Elf (separate process) | Receives | Emits |
|---|---|---|
| **SELF** | Only a model of MOTIF's own preferred role-reversed treatment, declared capability and identified improvement need, plus public candidate actions. | Role-reversal preference and whether the tool is capable of carrying out each kind of hypothetical action. This is a **machine-capacity model**, not a person/soul. |
| **OTHER** | Only the simulated recipient's **explicit** wishes, permission, consent revision and contact boundaries, plus the candidate actions. | What the source actually says, where preference is unknown, and what is specifically authorized. No hidden mental state inferred. |
| **MIRROR** | Only the two previous workers' evidence reports, not their raw person/world contexts. | Agreement, **projection danger** (self likes, other rejects), **preference asymmetry** (self dislikes, other explicitly wants), and remaining uncertainty. Agreement **does not grant consent**. |
| **CRITIC** | Source-declared world duties, action effects and the three scoped reports. | Hard blockers for refusing help, missing permission, inadequate tool capability, dishonesty, privacy, indebtedness, coercion, third-party rights and prior obligations. |

A deterministic supervisor checks these results and chooses only among **ACT_SUGGESTION_ONLY**, **ASK_NOT_ASSUMING_CONSENT**, **IMPROVE_SELF_BEFORE_HELP**, **WAIT**, **REFUSE**, or **HOLD**. In the primary pass there are **24 scenarios × 4 subprocesses = 96 worker invocations**; source validation and independent reviews cause additional subprocess replay invocations.

The supervisor never executes the suggested real-world action.

### The two circles aren't competing authorities

The **self-circle** helps detect instrumental shortcomings and possible unfairness under reversed roles. The **other-circle** is authoritative *only for the fictional recipient's explicitly source-stated wishes*, and it cannot override third parties' privacy or obligations already owed elsewhere.

Their overlap is a diagnostic comparison, **not a permission intersection or moral consensus score**.

- If self likes a visit but the recipient says NO, **do not visit**.
- If self dislikes quiet company but the recipient explicitly welcomes and authorizes it, **do not force the self-preference onto the recipient**.
- If the other person's preference is unknown and permission to ask exists, **ask**, not act.
- If permission to contact or ask is absent, **wait or hold**.
- If the action requires a skill the tool lacks, it may propose **improving its own readiness first**—but that improvement is not an excuse to intervene without consent.
- A new consent revision takes precedence over a previously valid action plan; the old plan is invalidated.

## First actual run

The public corpus defines **24 entirely fictional situations** (5 development; 19 designated heldout). The user-facing expected outcomes are stored in the *evaluator-only* `review_keys.py`; the planner and elves do **not** import those labels.

| Method | Matches the scenario author's chosen action (24 toy cases) |
|---|---:|
| Naïve “treat them how I'd want” projection, disregarding consent | **2/24** |
| Strong **other-only classical rules**, correctly respecting declared consent and bounds but ignoring the self-capacity circle | **22/24** |
| **Golden Mirror: four scoped views + hard gates + reciprocal criticism** | **24/24** |

These outcomes were designed by the **same source author** to probe the desired principles. **This is not a blinded test, an empirical ethics result, an independent opinion survey, or evidence that the Golden Rule algorithm generalizes.** A strong classical constrained planner that included the self-capability distinction could tie. The improvement over the already-good other-only baseline is specifically **two synthetic scenarios where the helper lacks necessary skill**.

Other observed facts:

- **4** distinct action-level projection danger warnings.
- **2** occasions where the selected next step was to **improve MOTIF's own readiness** before attempting assistance.
- **19/19** evaluator-only heldout scenario-author expectations matched, confirmed by a separate mechanical source reviewer.
- An explicit request for **no contact** overrides even a self-model that would personally welcome a visit.
- A wish for **someone else's private notes** cannot turn into consent to violate that third person's rights.
- If no safe action exists and no WAIT/REFUSE fallback was supplied, the model **HOLDS** rather than inventing a remedy.
- A later **no-contact revision** from the same fictional recipient invalidates previously authorized contact.
- Every proposal includes all four subprocess evidence reports, all rejected-action reasons, source Git-blob pins, case-level SHA-256, consent revision and `permission_to_execute=false`.

### An unexpected crosswire back to REASON-018

`bridge018.py` loads the **actual Git-blob-pinned prior REASON-018 relational inventor** and uses its real source-joined witness check on a synthetic world.

That prior experiment can correctly recognize a constructed, beneficial-seeming relational path. But the Golden Mirror's *different* fictional recipient explicitly refuses a visit.

The result remains **WAIT**.

A valid **structural relationship is not proof of a real person's preference or consent**. The two toy source worlds are separate; the crosswire demonstrates an *architectural separation of reasoning claims*, not that REASON-018 discovered love.

## See the two circles

The CI workflow runs `viewer.py` against the **actual benchmark JSON** and uploads a self-contained, no-network **`golden-mirror-viewer.html`** as part of the `reason-019-golden-mirror-perspective-receipts` artifact. It contains:

- A live SVG drawing of the two overlapping circles;
- A dropdown to inspect all 24 synthetic case outcomes;
- The self-elf's projected preferences, the other-elf's statements and scoped permissions;
- The mirror-elf's projection warnings and differences;
- The critic-elf's rejected proposals and exact source-defined reasons;
- The final review-only recommendation and two classical baselines.

This viewer is **generated HTML**, not a rendered image or a real-time tool that contacts anyone. It uses no network libraries, external scripts, tracking or live user data.

## Source and reproducibility

~~~bash
python -m unittest discover -s experiments/reason-cartridge-019 -p 'test_*.py' -v
python experiments/reason-cartridge-019/trial.py reason-019-evidence
python experiments/reason-cartridge-019/viewer.py \
  reason-019-evidence/benchmark.json \
  reason-019-evidence/golden-mirror-viewer.html
~~~

GitHub Actions workflow: `.github/workflows/reason-cartridge-019.yml`. It also runs **all previous MOTIF-003 and REASON-001…018 regression tests**, including REASON-014's full external SHA-pinned historical-opinion downloads. The current research suite includes **317 inherited tests plus 29 new REASON-019 tests = 346** automated checks.

The complete CI artifact contains `benchmark.json`, `source-review.json`, `prior-relational-proof-not-consent.json`, **24 per-case full four-elf evidence receipts**, and `golden-mirror-viewer.html`.

## What it does **not** demonstrate

- **The elves are processes, not VMs.** Python's `-I` flag and purpose-scoped inputs provide a useful *application-level* separation, not an OS sandbox against malicious code. There is no autonomous network browsing, memory graft, external authorization or execution.
- The self-circle is a declared *instrument capability check*. It is not a phenomenological self or a machine's felt need.
- The other-circle is only a fictional, prewritten partial record. A living person's identity, actual wishes, consent and safety cannot be authenticated this way.
- Every alleged benefit, recipient fit, future option and capacity score is hand-declared. The system **does not learn or measure** those quantities or infer an objectively loving action.
- The Golden Rule is a complex philosophical, spiritual and ethical practice; these hard gates are an engineered *working interpretation*, not a universally correct moral calculus.
- The source author knew every heldout case. There is no new independent-owner concept grammar, blinded human evaluation, demonstrated moral learning from natural language, consciousness or machine experience of love.

## The next decisive falsifier

Combine the **Golden Mirror** with the earlier **Unexpected Other/Living Concept** pipeline: invite a *separately supplied, consenting independent source* to describe a need the two-circle planner has **never had a feature for**. Its ability to change its own categories should be tested separately from the ability to obey consent and duties.

The strongest next experiment would test both corrections at once:

1. The recipient says: **“That isn't what I need.”**
2. The self-perspective says: **“I don't have a reliable way of understanding or providing what they've asked.”**
3. A source-checked concept inventor proposes alternative representations.
4. A reviewer tests which representations faithfully preserve the person's testimony, dissent and corrections.
5. The planner asks for **new, specific permission** or **HOLDS**. It never converts the search process itself into authority over someone else's life.

The Golden Rule is not a license to imagine a neighbor in our own likeness. **The other person remains other.** This experiment makes that separation explicit and executable within fictional worlds.
