# LLM-005 — ODYSSEY-240: Long-chain Reason Hypermap pressure

**Status: DRAFT, executable, not deployed, not merged.** Stacked on LLM-004 PR #318, which itself is stacked on unmerged LLM-003/LLM-002/LLM-001. No JAR;VIS, MEMENTO, Understory, Supabase, Free Graph writes, real people, photos or physical-world actions were involved.

## A genuinely long causal chain

This is not 96 disconnected trivia questions. There is one *serial, required dependency chain*:

- **12 sequential sectors**, each with a distinct hidden authored Boolean rule. A sector starts with exactly one independently witnessed calibration. The rule changes in the next sector (concept drift), so facts must be scoped to the correct sector.
- **8 ordered checkpoints per sector = 96 source-verified decisions**. Every checkpoint must first be surveyed (reveals only 3-bit input, not target) and then committed to a binary decision. The synthetic owner independently returns acceptance/refusal.
- A **wrong provisional commitment is actually refused**. It cannot advance the chain; it requires its own repair action plus a correct retry using the original owner report. The mistake remains in the immutable hash-chained event history. No fabricated second source root or retroactive rewriting.
- **12 halfway audits**, requiring four independently sourced accepted checkpoints; **12 terminal audits**, requiring eight; and **3 bridge relays** at every fourth sector. A successor is inaccessible until the previous sector's terminal audit (and required relay) is passed.
- Minimum without errors or optional evidence probes: **96 surveys + 96 accepted commits + 24 audits + 3 relays = 219 mandatory serial actions**. This is a *critical causal chain*, not just aggregate operation count.
- Hard limits: **350 total actions and 400 synthetic cost units**. Incorrect submissions incur penalty and extra recovery cost. A repeated, potentially false rumor travels with every survey using the same stage root and never becomes an independent evidence source.

## Actual source-owned code

`odyssey.py` uses the existing LLM-003 `Owner` / eight-rule hypothesis family and the actual LLM-004 `ReasonHypermap`. It does **not** invent a new unrelated collection of arbitrary labels. Each sector has its own map. The map preserves PENCIL proposed predictions, typed tests, independent root receipts, contradictions, revised posterior states, source historical hyperedges, and an immutable stage ledger. Owner truth remains available ONLY to the simulator/verifier.

A small budget-aware **HYPERMAP_VOI** policy probes before commitment when estimated cost of an incorrect commitment exceeds the cost of obtaining an independent source result. It uses the same hypothesis posterior as strong classical Bayes; its difference is when and whether to pay for evidence rather than accepting the risk of guessing. The probe's source is counted only once.

Competing policies:
- STATIC: ignores newly learned cross-checkpoint posterior information, though every current checkpoint is still owner-verified.
- CLASSICAL_BAYES: reuses all independently verified within-sector evidence, without paid speculative probes.
- HYPERMAP_VOI: same Bayesian memory, adds cost-aware independent precommit verification on uncertain gates.
- CONTRARIAN: intentionally flips uncertain PENCIL candidate answers. Source verification and repair still required; deliberately wrong guesses receive no intrinsic reward.

These policies and score definitions were **preregistered before implementation** at commit `56bf6658832bc2401b19a641d234e72c9e9647f9`.

## Observed 64-world authored-fixture results, 2026-11-12

Separate held-out author's simulator seeds, identical source-owner task distribution and cost/action limits. GitHub Actions [run](https://github.com/the-static-collective/MOTIF/actions/runs/43257784463).

| Policy | Completed full 219+-action path | Mean actions attempted | Mean synthetic cost | Mean wrong commits | Mean paid precommit probes |
| --- | ---: | ---: | ---: | ---: | ---: |
| STATIC | 61 / 64 | 278.64 | 371.43 | 29.97 | 0 |
| CLASSICAL_BAYES | 64 / 64 | 242.28 | 243.48 | 11.64 | 0 |
| HYPERMAP_VOI | **64 / 64** | 242.78 | **216.83** | **2.42** | 18.94 |
| CONTRARIAN | 64 / 64 | 248.38 | 264.81 | 14.69 | 0 |

**Within these invented rules**, cost-aware verification reduced average synthetic cost relative to classical Bayes by **26.66 units** (approximately 10.95%), and avoided about **9.22 wrong commitments per long chain** at approximately **18.94 additional optional probes**. It took **0.5 more attempted actions on average**. More computation was not universally better; the best result depended on the stipulated relative costs of probes, mistakes and repairs.

Classical Bayes was itself highly effective and is the necessary baseline: reusing verified facts reduced wrong commitments dramatically relative to STATIC. Intentionally wrong suggestions did not improve cost over classical Bayes.

Those results are **not evidence that a pretrained LLM solved 96 tasks**, not evidence of real-world safety, and not a general model intelligence benchmark. HYPERMAP_VOI is a simple cost-aware Bayesian verification strategy acting on a tiny authored hypothesis set. A precise classical planner with access to the same probe actions could reproduce it. The study does not establish a new algorithm, independent external generalization, or a statistically established real-world advantage.

LLM-004's independent-grader definition of an informative wrong provisional hypothesis remains in force: it is useful only if testing produces *independently verified subsequent decision improvement net of cost*. The graph records both useful counterexamples and counterexamples that taught nothing. Some independent right guesses also yield valuable information. A final false answer is never rewarded.

### One fully inspectable long chain (curated illustration)

All four policies finished fictional scenario `8001`. The actual source ledger contains:
- STATIC: **279 actions**, 30 wrong commitments, 372 cost units.
- CLASSICAL_BAYES: **243 actions**, 12 wrong commitments, 246 cost units.
- HYPERMAP_VOI: **237 actions**, 2 wrong commitments, 14 optional probes, 204 cost units.
- CONTRARIAN: **243 actions**, 12 wrong commitments, 246 cost units.

The display seed was **deliberately selected** from the registered seed list to ensure every policy completes and the Hypermap arm displays both a wrong commitment and paid verification. Its values must not be treated as representative averages.

## Offline interactive replay

`viewer_long.py` builds `odyssey240.html`: a **self-contained, offline, clickable, real execution trace** with policy switcher, step scrubber, replay, next-error jump, 12-sector × 8-gate dependency lattice, staged audit and relay status, source-root receipt details, exact JSON event history, per-sector reified Reason Hypermap inputs and outcomes, and the actual 64-world results. The 200+ event records are source-generated, not hand-drawn to suggest success. JavaScript is syntax-checked separately in CI and the web viewer was loaded without runtime errors in headless Chromium.

Data packages: `benchmark.json` (64-world summary), `odyssey240-dossier.json` (four complete synthetic trajectory traces with per-sector maps), `odyssey240-display-summary.json`, and `odyssey240.html`. All are published as a GitHub Actions artifact by the dedicated LLM-005 workflow. No remote network calls or arbitrary user input are needed to view the HTML.

## Reproduce

Python 3.11+ standard library only:

```sh
PYTHONPATH=experiments/llm003:experiments/llm004:experiments/llm005 \
  python -m unittest discover -s experiments/llm005 -p 'test_*.py' -v

PYTHONPATH=experiments/llm003:experiments/llm004:experiments/llm005 \
  python experiments/llm005/odyssey.py

PYTHONPATH=experiments/llm003:experiments/llm004:experiments/llm005 \
  python experiments/llm005/build_viewer.py --out /tmp/odyssey240 \
  --study-file /tmp/odyssey240/benchmark.json
```

The latest completed GitHub Actions execution passed **53 LLM-005 tests + 41 inherited LLM-004 tests**, independently ran the 64-world experiment, built all artifacts, and syntax-checked the actual generated browser script.

## Post-hoc length escalation: ODYSSEY MARATHON (879+ REQUIRED steps)

Following the initial successful 219-action result, we froze a **separate** [MARATHON-PREREGISTRATION](MARATHON-PREREGISTRATION.md) before implementing a more severe challenge: four complete ODYSSEY-240 chains connected by three **mandatory source-bound handoff actions**. A later chain cannot start before the preceding one has passed all 96 gates and returned its terminal state digest.

The minimum serial critical path is **4 × 219 + 3 = 879 mandatory actions**, involving **384 source-verified decisions, 48 changing rule contexts, 96 audits, 12 relays and 3 inter-world handoffs**. Each global event commits to the original child's event hash and the preceding global event hash. All previous mistakes, corrections and separate source roots are preserved. The marathon has hard 1,350-action and 1,800-cost global ceilings. No invented cryptographic identity or owner authorization is assigned to those consistency digests.

The marathon uses **four separately preregistered groups of four distinct synthetic scenario seeds** (8001–8016), compares the same four policies, and preserves any incomplete chain as an incomplete result rather than treating early termination as efficient completion. This is an additional length/integrity challenge, not a new pretrained-model test.

Executable files:

- `marathon.py`: executes the genuine preceding source-owned LongChain four times in sequence; requires each segment's source-hash handoff; provides one global monotonically hashed immutable event ledger.
- `test_marathon.py`: 20 direct falsifiers for mandatory causal order, replay, 48 distinct synthetic owner source coordinates, full 384-correct-decision acceptance, and budget stops.
- `build_marathon.py` and `viewer_marathon.py`: create `marathon-dossier.json`, `marathon-display-summary.json`, and an **offline interactive `marathon.html` replay covering all 48 sectors and more than 879 sequential events**, with policy switcher, replay and step scrubber, jumps to the next wrong guess or handoff, a 384-gate dependency lattice, exact source-rooted event history and four-group results.
- `test_viewer_marathon.py`: explicit tests for actual long event payloads and safe offline read-only rendering.

### Observed post-hoc marathon trial: 4 registered fictional groups

The **actual** serialized length and source-verified outcomes are from the dedicated GitHub Actions [long-chain plus marathon run](https://github.com/the-static-collective/MOTIF/actions/runs/43260021908), using identical prepared source-owner rules and resource constraints within each group.

| Policy | All 384 decisions completed | Mean actual serial steps | Mean fictional cost | Mean wrong commitments | Mean optional probes |
| --- | ---: | ---: | ---: | ---: | ---: |
| STATIC, no learned memory | 3 / 4 | 1,117 | 1,487.31 | 119.75 | 0 |
| CLASSICAL_BAYES | **4 / 4** | 967 | 959.00 | 44.00 | 0 |
| HYPERMAP_VOI | **4 / 4** | 974 | **870.25** | **9.75** | 75.50 |
| CONTRARIAN | **4 / 4** | 1,001 | 1,078.00 | 61.00 | 0 |

This is descriptive data from just **four independently registered authored groups**; it neither proves statistical superiority nor tests a real pretrained language model. In this fixed-cost synthetic workload, cost-aware verification saved an average of **88.75 fictional cost units** compared with classical Bayes while taking **seven more serial steps**. It also committed approximately **34.25 fewer wrong provisional answers per marathon**, paid for with more independent verification. A perfect classical source-aware strategy could reproduce its decision logic.

In the first preregistered group (8001→8002→8003→8004), **HYPERMAP_VOI actually completed 969 serialized actions** with 384 accepted synthetic decisions, 96 audited gates, 12 relays, 3 source handoffs, **6 wrong commitments**, **78 paid independent probes**, and total synthetic cost **849**. Classical Bayes also took 969 actions, but incurred 45 wrong commitments and cost 966. The complete 969-step trace, all original child receipt hashes, and all four policy replays appear in `marathon.html`. The viewer was independently loaded and interacted with in headless Chromium without JavaScript runtime errors.

The LLM-005 job passed **79 direct long-chain/marathon/viewer tests plus 41 inherited Reason Hypermap tests**. The required causal chain was independently checked as at least 879 steps, rather than merely printing an action count.

The fully generated marathon JSON and HTML are included in the same LLM-005 workflow artifact as the original 219-step viewer; actual results must be read from the successful workflow attached to the current commit, not assumed from the earlier short-chain success.

**Meaning:** This is a real 879+-step *simulated causal dependency and evidence-retention chain*, not 879 tokens of model thinking, 879 natural-language reasoning conclusions, or proof that an LLM can perform a long task in the real world.

## Falsification next

The above is a long **classical synthetic reason chain**, not a pretrained LLM test. Its unresolved research task is to connect LLM-003's actual pinned pretrained model to select these provisional candidate decisions *without passing in the hidden rule or direct labels*, then test whether source-scoped Hypermap memory improves later independently graded decisions against classical Bayesian planning, a similarly equipped model without memory, and cost-aware optimal inquiry. Also test adversarial false independent owner reports, changing hidden worlds mid-sector, more options than Boolean rules, long attention context loss and real measured GPU/CPU inference costs.

Nothing has been merged into production. Source roots are historical consistency coordinates, not external authentication or project authority.
